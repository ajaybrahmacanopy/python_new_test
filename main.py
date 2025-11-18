#!/usr/bin/env python
"""
Build FAISS index from PDF
"""

import os
import sys
import fitz
from src.logger import logger
from src import INDEX_PATH, META_PATH, VectorStoreManager
from src.pdf_processor import PDFProcessor
from src.config import PDF_PATH, MEDIA_DIR


def ensure_images_generated():
    """Check and generate any missing page images"""
    try:
        processor = PDFProcessor()
        doc = fitz.open(PDF_PATH)
        total_pages = len(doc)
        doc.close()

        # Count missing images
        missing = []
        for page_num in range(1, total_pages + 1):
            filename = f"page_{page_num}.png"
            out_path = os.path.join(MEDIA_DIR, filename)
            if not os.path.exists(out_path):
                missing.append(page_num)

        if missing:
            print(f"📸 Generating {len(missing)} missing images...")
            logger.info(f"Generating {len(missing)} missing page images")

            for i, page_num in enumerate(missing, 1):
                processor.get_page_image_path(page_num)
                if i % 10 == 0 or i == len(missing):
                    print(f"   Progress: {i}/{len(missing)}")

            print(f"✅ Generated {len(missing)} images")
            logger.info(f"Generated {len(missing)} images successfully")
        else:
            logger.info("All page images already exist")

    except Exception as e:
        logger.warning(f"Failed to generate images: {e}")
        print(f"⚠️  Warning: Could not generate some images: {e}")


if __name__ == "__main__":
    try:
        logger.info("Initializing VectorStoreManager...")
        vector_store = VectorStoreManager()

        # Build the index if it doesn't exist
        if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
            print("Building FAISS index...")
            logger.info("Starting index build...")

            try:
                vector_store.build_and_save_index()
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

        # Ensure all page images are generated
        print()
        ensure_images_generated()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
