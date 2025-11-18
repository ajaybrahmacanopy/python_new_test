#!/usr/bin/env python
"""
Main entry point - matches the CLI test from RAG.py
"""

import os
from src import (
    INDEX_PATH,
    META_PATH,
    build_and_save_index,
    search,
    retrieve_with_reranking,
    generate_structured_answer,
)

if __name__ == "__main__":
    # 1st run: build the index
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        build_and_save_index()

    # quick smoke test
    q = "How do I handle wayfinding signage for blocks of flats?"
    hits = search(q, top_k=5)
    print("\nTop chunks:\n")
    for r in hits:
        print(f"- Rank {r['rank']} (page {r['page']}, dist {r['distance']:.4f})")
        print(r["text"][:400], "...\n")
        print("media:", r["media"])
        print("diagrams:", r["diagram_ids"])
        print("is_table:", r["is_table"])
        print("-" * 80)

    # 1. retrieve & rerank
    q = "How do I handle wayfinding signage for blocks of flats?"
    context, pages, media_files = retrieve_with_reranking(q)

    # 2. generate validated answer
    result = generate_structured_answer(q, context, pages, media_files)

    print(result.model_dump())

    print(pages)
    print(media_files)
