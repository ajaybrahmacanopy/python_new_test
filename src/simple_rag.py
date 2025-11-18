"""Simple end-to-end RAG pipeline - copied exactly from RAG.py"""

from .logger import logger
from .vector_store import VectorStoreManager
from .reranker import LlamaReranker
from .generator import AnswerGenerator
from .guardrails import validate_context


class SimpleRAG:
    """Clean, minimal end-to-end RAG pipeline."""

    def __init__(
        self,
        top_k: int = 5,
        candidate_k: int = 25,
    ):
        self.top_k = top_k
        self.candidate_k = candidate_k

        self.store = VectorStoreManager()
        self.reranker = LlamaReranker()
        self.generator = AnswerGenerator()

        logger.info("SimpleRAG initialized.")

    # -----------------------------------------------------------
    # RETRIEVAL + RERANKING
    # -----------------------------------------------------------
    def retrieve(self, query: str):
        """Hybrid retrieval + LLM reranking -> top_k contexts."""

        # 1. Get FAISS + BM25 candidates
        faiss_store, chunks = self.store.load_index_and_metadata()

        # Get ensemble results
        results = self.store.hybrid_search(
            query=query,
            top_k=self.top_k,
            candidate_k=self.candidate_k,
            use_reranker=False,  # We'll do our own reranking below
        )

        # 2. Apply Llama reranker
        ranking = self.reranker.score_passages(
            query, [{"id": i, "text": r["text"]} for i, r in enumerate(results)]
        )

        # Sort by score descending
        ranked = sorted(ranking.results, key=lambda x: x.score, reverse=True)

        # Select final top_k
        final = [results[item.id] for item in ranked[: self.top_k]]

        # Prepare context text
        context = "\n\n---\n\n".join(f["text"] for f in final)

        # Gather media + pages
        pages = list({m for f in final for m in f["media"]})
        images = list({img for f in final for img in f["diagram_ids"]})

        return context, pages, images

    # -----------------------------------------------------------
    # GENERATE FINAL ANSWER
    # -----------------------------------------------------------
    def answer(self, query: str):
        """Retrieve → Rerank → Generate structured answer."""

        logger.info(f"SimpleRAG answering query: {query}")

        context, pages, media_files = self.retrieve(query)

        # Sanitize context with Ammonia (nh3) to remove HTML/XSS
        sanitized_context = validate_context(context)

        answer = self.generator.generate(
            query=query,
            context=sanitized_context,
            pages=pages,
            media_files=media_files,
        )

        return answer
