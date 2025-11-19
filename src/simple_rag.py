"""End-to-end RAG pipeline"""

from .logger import logger
from .vector_store import VectorStoreManager
from .reranker import LlamaReranker
from .generator import AnswerGenerator
from .guardrails import validate_context
from .config import TOP_K, CANDIDATE_K


class SimpleRAG:
    """Clean, minimal end-to-end RAG pipeline."""

    def __init__(
        self,
        top_k: int = TOP_K,
        candidate_k: int = CANDIDATE_K,
    ):
        self.top_k = top_k
        self.candidate_k = candidate_k

        self.store = VectorStoreManager()
        self.reranker = LlamaReranker()
        self.generator = AnswerGenerator()

        logger.info("SimpleRAG initialized.")

    def retrieve(self, query: str):
        """Hybrid retrieval + LLM reranking -> top_k contexts."""

        # 1. Get FAISS + BM25 candidates
        faiss_store, chunks = self.store.load_index_and_metadata()

        # Build page-to-diagrams mapping from ALL chunks
        page_diagram_map = {}
        for chunk in chunks:
            page = chunk.get("page")
            diagrams = chunk.get("diagram_ids", [])
            if page not in page_diagram_map:
                page_diagram_map[page] = set()
            page_diagram_map[page].update(diagrams)

        # Convert sets to sorted lists
        page_diagram_map = {
            page: sorted(list(diagrams)) for page, diagrams in page_diagram_map.items()
        }

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

        # Gather unique pages from final results
        unique_pages = list({f["page"] for f in final})

        # Gather media (page images)
        pages = list({m for f in final for m in f["media"]})

        # Get ALL diagrams for the unique pages using page_diagram_map
        all_diagrams = []
        for page in unique_pages:
            if page in page_diagram_map and page_diagram_map[page]:
                all_diagrams.extend(page_diagram_map[page])

        # Remove duplicates and sort
        images = sorted(list(set(all_diagrams)))

        # Safety: Limit to max 25 diagrams to avoid overwhelming the LLM
        if len(images) > 25:
            logger.warning(f"Too many diagrams ({len(images)}), limiting to 25")
            images = images[:25]

        return context, pages, images

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
