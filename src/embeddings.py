"""Embedding and FAISS operations - copied exactly from RAG.py"""

import os
import pickle
import logging
from typing import List, Dict, Any
import numpy as np
import faiss
from openai import OpenAI

from .config import EMBED_MODEL, INDEX_PATH, META_PATH, PDF_PATH
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

os.makedirs("data", exist_ok=True)


class EmbeddingManager:
    """Embedding and FAISS operations class"""

    def __init__(self):
        try:
            self.client = OpenAI()
            self.pdf_processor = PDFProcessor()
            logger.info("EmbeddingManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingManager: {e}")
            raise

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of texts using OpenAI text-embedding-3-small.
        Returns a numpy array of shape (n, d) dtype float32.

        Raises:
            ValueError: If texts list is empty
            Exception: If OpenAI API call fails
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")

        embeddings: List[List[float]] = []
        batch_size = 64

        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                try:
                    resp = self.client.embeddings.create(
                        model=EMBED_MODEL,
                        input=batch,
                    )
                    for item in resp.data:
                        embeddings.append(item.embedding)
                except Exception as e:
                    logger.error(f"Failed to embed batch {i // batch_size + 1}: {e}")
                    raise

            arr = np.array(embeddings, dtype="float32")
            logger.info(f"Successfully embedded {len(texts)} texts")
            return arr
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise

    def build_and_save_index(self) -> None:
        """
        Build FAISS index from PDF and save to disk.

        Raises:
            FileNotFoundError: If PDF file not found
            Exception: If index building fails
        """
        try:
            if not os.path.exists(PDF_PATH):
                raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

            print("Building chunks from PDF...")
            logger.info(f"Processing PDF: {PDF_PATH}")
            chunks = self.pdf_processor.build_chunks_from_pdf(PDF_PATH)
            print(f"Total chunks: {len(chunks)}")
            logger.info(f"Generated {len(chunks)} chunks")

            if not chunks:
                raise ValueError("No chunks generated from PDF")

            texts = [c["text"] for c in chunks]

            print("Embedding chunks...")
            emb_matrix = self.embed_texts(texts)  # (N, D)
            n_chunks, dim = emb_matrix.shape
            print(f"Embeddings shape: {emb_matrix.shape}")
            logger.info(f"Created embeddings: {emb_matrix.shape}")

            print("Creating FAISS index...")
            index = faiss.IndexFlatL2(dim)
            index.add(emb_matrix)
            logger.info("FAISS index created")

            print(f"Saving index to {INDEX_PATH} ...")
            faiss.write_index(index, INDEX_PATH)
            logger.info(f"Index saved to {INDEX_PATH}")

            print(f"Saving metadata to {META_PATH} ...")
            with open(META_PATH, "wb") as f:
                pickle.dump(chunks, f)
            logger.info(f"Metadata saved to {META_PATH}")

            print("Done building FAISS index + metadata.")

        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise

    def load_index_and_metadata(self):
        """
        Load FAISS index and metadata from disk.

        Raises:
            FileNotFoundError: If index or metadata files not found
        """
        try:
            if not os.path.exists(INDEX_PATH):
                raise FileNotFoundError(
                    f"{INDEX_PATH} not found. Run build_and_save_index() once first."
                )
            if not os.path.exists(META_PATH):
                raise FileNotFoundError(
                    f"{META_PATH} not found. Run build_and_save_index() once first."
                )

            logger.info(f"Loading index from {INDEX_PATH}")
            index = faiss.read_index(INDEX_PATH)

            logger.info(f"Loading metadata from {META_PATH}")
            with open(META_PATH, "rb") as f:
                chunks = pickle.load(f)

            logger.info(f"Loaded {index.ntotal} vectors and {len(chunks)} chunks")
            return index, chunks

        except Exception as e:
            logger.error(f"Failed to load index/metadata: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Embed the query, search FAISS, and return top_k chunk metadata entries.

        Raises:
            ValueError: If query is empty or top_k is invalid
            Exception: If search fails
        """
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            if top_k <= 0:
                raise ValueError("top_k must be positive")

            index, chunks = self.load_index_and_metadata()

            # embed query
            q_emb = self.embed_texts([query])

            # search
            distances, indices = index.search(q_emb, top_k)
            indices = indices[0]
            distances = distances[0]

            results = []
            for rank, (idx, dist) in enumerate(zip(indices, distances), start=1):
                chunk = chunks[int(idx)]
                results.append(
                    {
                        "rank": rank,
                        "distance": float(dist),
                        "page": chunk["page"],
                        "text": chunk["text"],
                        "media": chunk["media"],
                        "diagram_ids": chunk["diagram_ids"],
                        "is_table": chunk["is_table"],
                    }
                )

            logger.info(f"Search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
