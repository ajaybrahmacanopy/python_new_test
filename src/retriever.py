"""Retrieval and reranking - copied exactly from RAG.py"""

import logging
import time
from groq import Groq

from .embeddings import EmbeddingManager
from .utils import context_is_relevant
from .pdf_processor import PDFProcessor
from .config import TOP_K, CANDIDATE_K, TEMPERATURE, API_TIMEOUT_MS, API_MAX_RETRIES

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieval and reranking class"""

    def __init__(self):
        try:
            self.groq_client = Groq(
                timeout=API_TIMEOUT_MS / 1000
            )  # Convert ms to seconds
            self.embedding_manager = EmbeddingManager()
            logger.info("Retriever initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Retriever: {e}")
            raise

    def rerank(self, query, faiss_results, top_k=5):
        """
        Re-rank FAISS results using Llama 3.1 8B Instant.
        Returns top_k highest-scoring chunks.

        Raises:
            ValueError: If inputs are invalid
            Exception: If reranking fails
        """
        try:
            if not query:
                raise ValueError("Query cannot be empty")

            if not faiss_results:
                raise ValueError("FAISS results cannot be empty")

            if top_k <= 0:
                raise ValueError("top_k must be positive")

            scored = []
            logger.info(f"Reranking {len(faiss_results)} candidates")

            for i, r in enumerate(faiss_results):
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

                # Retry logic for API calls
                score = 0.0
                for attempt in range(API_MAX_RETRIES + 1):
                    try:
                        response = self.groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=TEMPERATURE,
                        )

                        try:
                            score = float(response.choices[0].message.content.strip())
                        except (ValueError, AttributeError) as e:
                            logger.warning(f"Failed to parse score for chunk {i}: {e}")
                            score = 0.0

                        break  # Success, exit retry loop

                    except Exception as e:
                        if attempt < API_MAX_RETRIES:
                            wait_time = 2**attempt  # Exponential backoff: 1s, 2s
                            logger.warning(
                                f"Groq API call failed for chunk {i} "
                                f"(attempt {attempt + 1}/{API_MAX_RETRIES + 1}): {e}. "
                                f"Retrying in {wait_time}s..."
                            )
                            time.sleep(wait_time)
                        else:
                            logger.error(
                                f"Groq API call failed for chunk {i} after "
                                f"{API_MAX_RETRIES + 1} attempts: {e}"
                            )
                            score = 0.0

                scored.append((score, r))

            # Sort high → low
            scored.sort(key=lambda x: x[0], reverse=True)

            result = [item[1] for item in scored[:top_k]]
            logger.info(f"Reranking complete, returning top {len(result)} results")
            return result

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            raise

    def retrieve_with_reranking(self, query, top_k=TOP_K, candidate_k=CANDIDATE_K):
        """
        Retrieve and rerank results for a query.

        Args:
            query: Search query
            top_k: Number of final results
            candidate_k: Number of initial candidates

        Returns:
            Tuple of (context_text, pages, media_files) or (None, None, None)

        Raises:
            Exception: If retrieval or reranking fails
        """
        try:
            logger.info(f"Retrieving with query: {query[:100]}...")

            # 1. FAISS retrieves top candidates (fast)
            try:
                faiss_results = self.embedding_manager.search(query, top_k=candidate_k)
            except Exception as e:
                logger.error(f"FAISS search failed: {e}")
                raise

            if not faiss_results:
                logger.warning("No FAISS results found")
                return None, None, None

            # 2. Rerank
            try:
                reranked = self.rerank(query, faiss_results, top_k=top_k)
            except Exception as e:
                logger.error(f"Reranking failed: {e}")
                raise

            if not reranked:
                logger.warning("No reranked results")
                return None, None, None

            # 3. Build context for final answer
            context_text = "\n\n---\n\n".join(
                f"[Page {r['page']}]\n{r['text']}" for r in reranked
            )

            media_files = sorted({m for r in reranked for m in r["diagram_ids"]})
            pages = sorted({m for r in reranked for m in r["media"]})

            # Hallucination prevention: context must match query
            if not context_is_relevant(query, context_text):
                logger.info("Context not relevant to query")
                return None, None, None  # signal irrelevance

            # Ensure all referenced images exist (generate on-demand if missing)
            try:
                PDFProcessor.ensure_images_exist(pages)
            except Exception as e:
                logger.warning(f"Failed to ensure images exist: {e}")

            logger.info(
                f"Retrieved {len(pages)} pages and {len(media_files)} media files"
            )
            return context_text, pages, media_files

        except Exception as e:
            logger.error(f"Retrieval with reranking failed: {e}")
            raise
