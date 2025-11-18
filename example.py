#!/usr/bin/env python
"""
Example usage of the RAG system - CLI test
"""

import os
import json
from src import INDEX_PATH, META_PATH, VectorStoreManager, SimpleRAG


def main():
    # Initialize classes
    vector_store = VectorStoreManager()

    # 1st run: build the index if needed
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        print("Building index first...")
        vector_store.build_and_save_index()

    # Example query
    q = "How do I handle wayfinding signage for blocks of flats?"
    print(f"\nQuery: {q}\n")

    # Test 1: Hybrid Search Results
    print("=" * 80)
    print("TEST 1: Hybrid FAISS + BM25 Search Results")
    print("=" * 80)
    hits = vector_store.hybrid_search(q, top_k=5, candidate_k=20, use_reranker=True)
    print(f"\nTop {len(hits)} chunks:\n")
    for i, r in enumerate(hits, 1):
        print(f"- Rank {i} (page {r['page']})")
        print(r["text"][:400], "...\n")
        print("media:", r["media"])
        print("diagrams:", r["diagram_ids"])
        print("is_table:", r["is_table"])
        print("-" * 80)

    # Test 2: Simple RAG end-to-end
    print("\n" + "=" * 80)
    print("TEST 2: SimpleRAG End-to-End")
    print("=" * 80)
    
    rag = SimpleRAG(top_k=5, candidate_k=25)
    result = rag.answer(q)

    print("\n📋 Generated Answer:")
    print(f"\nTitle: {result.answer.title}")
    print(f"\nSummary:\n{result.answer.summary}")
    print("\nSteps:")
    for i, step in enumerate(result.answer.steps, 1):
        print(f"  {i}. {step}")
    print("\nVerification:")
    for v in result.answer.verification:
        print(f"  - {v}")
    print(f"\nLinks: {result.links}")
    print(f"Media: {result.media.images}")

    # Test 3: JSON output
    print("\n" + "=" * 80)
    print("TEST 3: JSON Output")
    print("=" * 80)
    print(json.dumps(result.model_dump(), indent=2))

    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
