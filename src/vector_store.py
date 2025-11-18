"""Vector store with hybrid retrieval"""

import os
import pickle

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document

from .config import EMBED_MODEL, INDEX_PATH, META_PATH, PDF_PATH
from .pdf_processor import PDFProcessor
from .reranker import LlamaReranker


class VectorStoreManager:
    """Handles embeddings, FAISS, and hybrid retrieval."""

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.embeddings = OpenAIEmbeddings(model=EMBED_MODEL)

    def build_and_save_index(self):
        print("Building chunks from PDF...")
        chunks = self.pdf_processor.build_chunks_from_pdf(PDF_PATH)
        print(f"Total chunks: {len(chunks)}")

        docs = [
            Document(
                page_content=c["text"],
                metadata={
                    "page": c["page"],
                    "media": c["media"],
                    "diagram_ids": c["diagram_ids"],
                    "is_table": c["is_table"],
                },
            )
            for c in chunks
        ]

        # Build FAISS
        print("Embedding and storing into FAISS...")
        faiss_store = FAISS.from_documents(docs, self.embeddings)

        # Save FAISS index
        faiss_store.save_local(INDEX_PATH)

        # Save metadata (original chunk dicts)
        with open(META_PATH, "wb") as f:
            pickle.dump(chunks, f)

        print("FAISS + metadata saved successfully.")

    def load_index_and_metadata(self):
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")

        if not os.path.exists(META_PATH):
            raise FileNotFoundError(f"Metadata not found at {META_PATH}")

        # Load FAISS
        faiss_store = FAISS.load_local(
            INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True
        )

        # Load metadata
        with open(META_PATH, "rb") as f:
            chunks = pickle.load(f)

        return faiss_store, chunks

    def hybrid_search(self, query: str, top_k=5, candidate_k=20, use_reranker=True):
        """
        Hybrid FAISS + BM25 retrieval using LangChain's EnsembleRetriever
        + LLM reranker.
        """

        faiss_store, chunks = self.load_index_and_metadata()

        # Build retrievers
        faiss_retriever = faiss_store.as_retriever(
            search_type="similarity", search_kwargs={"k": candidate_k}
        )

        bm25_retriever = BM25Retriever.from_documents(
            [Document(page_content=c["text"], metadata=c) for c in chunks]
        )
        bm25_retriever.k = candidate_k

        retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever], weights=[0.4, 0.6]
        )

        docs = retriever.get_relevant_documents(query)

        # Convert docs → candidate results
        results = []
        for doc in docs[:candidate_k]:
            md = doc.metadata
            results.append(
                {
                    "page": md["page"],
                    "text": doc.page_content,
                    "media": md["media"],
                    "diagram_ids": md["diagram_ids"],
                    "is_table": md["is_table"],
                }
            )

        # Apply LLM reranking if enabled
        if use_reranker:
            reranker = LlamaReranker()
            ranking = reranker.score_passages(
                query, [{"id": i, "text": r["text"]} for i, r in enumerate(results)]
            )

            # Sort by reranker score
            ranked_ids = sorted(ranking.results, key=lambda x: x.score, reverse=True)

            # Select top_k after reranking
            final = [results[item.id] for item in ranked_ids[:top_k]]

            return final

        # Return top-k ensemble results without reranking
        return results[:top_k]
