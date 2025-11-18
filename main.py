#!/usr/bin/env python
"""
Build FAISS index from PDF
"""

import os
from src import INDEX_PATH, META_PATH, EmbeddingManager

if __name__ == "__main__":
    embedding_manager = EmbeddingManager()

    # Build the index if it doesn't exist
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        print("Building FAISS index...")
        embedding_manager.build_and_save_index()
        print("✅ Index built successfully!")
    else:
        print("✅ Index already exists")
        print(f"Index: {INDEX_PATH}")
        print(f"Metadata: {META_PATH}")
