"""Embedding and FAISS operations - copied exactly from RAG.py"""

import os
import pickle
from typing import List, Dict, Any
import numpy as np
import faiss
from openai import OpenAI

from .config import EMBED_MODEL, INDEX_PATH, META_PATH, PDF_PATH
from .pdf_processor import build_chunks_from_pdf

os.makedirs("data", exist_ok=True)

client = OpenAI()


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed a list of texts using OpenAI text-embedding-3-small.
    Returns a numpy array of shape (n, d) dtype float32.
    """
    embeddings: List[List[float]] = []
    batch_size = 64

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch,
        )
        for item in resp.data:
            embeddings.append(item.embedding)

    arr = np.array(embeddings, dtype="float32")
    return arr


def build_and_save_index() -> None:
    print("Building chunks from PDF...")
    chunks = build_chunks_from_pdf(PDF_PATH)
    print(f"Total chunks: {len(chunks)}")

    texts = [c["text"] for c in chunks]

    print("Embedding chunks...")
    emb_matrix = embed_texts(texts)  # (N, D)
    n_chunks, dim = emb_matrix.shape
    print(f"Embeddings shape: {emb_matrix.shape}")

    print("Creating FAISS index...")
    index = faiss.IndexFlatL2(dim)
    index.add(emb_matrix)

    print(f"Saving index to {INDEX_PATH} ...")
    faiss.write_index(index, INDEX_PATH)

    print(f"Saving metadata to {META_PATH} ...")
    with open(META_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("Done building FAISS index + metadata.")


def load_index_and_metadata():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(
            f"{INDEX_PATH} not found. Run build_and_save_index() once first."
        )
    if not os.path.exists(META_PATH):
        raise FileNotFoundError(
            f"{META_PATH} not found. Run build_and_save_index() once first."
        )

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embed the query, search FAISS, and return top_k chunk metadata entries.
    """
    index, chunks = load_index_and_metadata()

    # embed query
    q_emb = embed_texts([query])

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

    return results
