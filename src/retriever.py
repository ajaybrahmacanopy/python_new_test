"""Retrieval and reranking - copied exactly from RAG.py"""

from groq import Groq
import numpy as np

from .embeddings import search
from .utils import context_is_relevant

groq_client = Groq()


def rerank(query, faiss_results, top_k=5):
    """
    Re-rank FAISS results using Llama 3.1 8B Instant.
    Returns top_k highest-scoring chunks.
    """
    scored = []

    for r in faiss_results:
        prompt = f"""
You are a reranker in a Retrieval-Augmented Generation system.

QUESTION:
{query}

CONTEXT CANDIDATE:
{r["text"]}

Evaluate how relevant this context chunk is to the question.
Return ONLY a score between 0 and 1.
A score of 1 means "directly answers the question".
A score of 0 means "irrelevant".
"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        try:
            score = float(response.choices[0].message.content.strip())
        except:
            score = 0.0

        scored.append((score, r))

    # Sort high → low
    scored.sort(key=lambda x: x[0], reverse=True)

    return [item[1] for item in scored[:top_k]]


def retrieve_with_reranking(query, top_k=5, candidate_k=20):
    # 1. FAISS retrieves top 20 candidates (fast)
    faiss_results = search(query, top_k=candidate_k)

    # 2. Rerank
    reranked = rerank(query, faiss_results, top_k=top_k)
    # print(reranked)

    # 3. Build context for final answer
    context_text = "\n\n---\n\n".join(
        f"[Page {r['page']}]\n{r['text']}" for r in reranked
    )

    # media_files = sorted({m for r in reranked for m in r["media"]})
    media_files = sorted({m for r in reranked for m in r["diagram_ids"]})
    pages = sorted({m for r in reranked for m in r["media"]})

    # Hallucination prevention: context must match query
    if not context_is_relevant(query, context_text):
        return None, None, None  # signal irrelevance

    return context_text, pages, media_files
