#!/usr/bin/env python
"""
Example usage of the RAG system - CLI test
"""

import os
from src import (
    INDEX_PATH,
    META_PATH,
    EmbeddingManager,
    Retriever,
    AnswerGenerator,
)


def main():
    # Initialize classes
    embedding_manager = EmbeddingManager()
    retriever = Retriever()
    generator = AnswerGenerator()

    # 1st run: build the index if needed
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        print("Building index first...")
        embedding_manager.build_and_save_index()

    # Example query
    q = "How do I handle wayfinding signage for blocks of flats?"
    print(f"\nQuery: {q}\n")

    # Test 1: Search
    print("=" * 80)
    print("TEST 1: FAISS Search Results")
    print("=" * 80)
    hits = embedding_manager.search(q, top_k=5)
    print("\nTop chunks:\n")
    for r in hits:
        print(f"- Rank {r['rank']} (page {r['page']}, dist {r['distance']:.4f})")
        print(r["text"][:400], "...\n")
        print("media:", r["media"])
        print("diagrams:", r["diagram_ids"])
        print("is_table:", r["is_table"])
        print("-" * 80)

    # Test 2: Retrieve with reranking
    print("\n" + "=" * 80)
    print("TEST 2: Retrieve with Reranking")
    print("=" * 80)
    context, pages, media_files = retriever.retrieve_with_reranking(q)

    if context is None:
        print("❌ No relevant context found")
        return

    print(f"\nContext length: {len(context)} chars")
    print(f"Pages: {pages}")
    print(f"Media files: {media_files}")

    # Test 3: Generate answer
    print("\n" + "=" * 80)
    print("TEST 3: Generate Structured Answer")
    print("=" * 80)
    result = generator.generate_structured_answer(q, context, pages, media_files)

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

    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
