#!/usr/bin/env python
"""
Build FAISS index from PDF
"""

import os
import sys
import logging
from src import INDEX_PATH, META_PATH, EmbeddingManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Initializing EmbeddingManager...")
        embedding_manager = EmbeddingManager()

        # Build the index if it doesn't exist
        if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
            print("Building FAISS index...")
            logger.info("Starting index build...")

            try:
                embedding_manager.build_and_save_index()
                print("✅ Index built successfully!")
                logger.info("Index build completed successfully")
            except FileNotFoundError as e:
                logger.error(f"File not found: {e}")
                print(f"❌ Error: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Failed to build index: {e}")
                print(f"❌ Error building index: {e}")
                sys.exit(1)
        else:
            print("✅ Index already exists")
            print(f"Index: {INDEX_PATH}")
            print(f"Metadata: {META_PATH}")
            logger.info("Index files already exist")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
