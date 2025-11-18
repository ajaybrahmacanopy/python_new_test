#!/usr/bin/env python
"""
Regenerate all page images with current DPI settings
"""

import os
from src.logger import logger
from src import PDFProcessor
from src.config import MEDIA_DIR
import fitz


def regenerate_all_images(force=False):
    """
    Regenerate all page images.

    Args:
        force: If True, regenerate even if images exist
    """
    processor = PDFProcessor()

    # Open PDF to get page count
    from src.config import PDF_PATH

    doc = fitz.open(PDF_PATH)
    total_pages = len(doc)
    doc.close()

    logger.info(f"Found {total_pages} pages in PDF")

    if force:
        logger.info("Force mode: Deleting existing images...")
        # Delete existing page images
        for filename in os.listdir(MEDIA_DIR):
            if filename.startswith("page_") and filename.endswith(".png"):
                # Only delete main page images, not embedded images
                if "_img_" not in filename:
                    filepath = os.path.join(MEDIA_DIR, filename)
                    os.remove(filepath)
                    logger.debug(f"Deleted {filename}")

    logger.info("Generating images...")
    generated = 0
    skipped = 0

    for page_num in range(1, total_pages + 1):
        filename = f"page_{page_num}.png"
        out_path = os.path.join(MEDIA_DIR, filename)

        if os.path.exists(out_path) and not force:
            skipped += 1
            if page_num % 20 == 0:
                logger.info(
                    f"Progress: {page_num}/{total_pages} (skipped {skipped}, generated {generated})"
                )
        else:
            # Generate the image
            processor.get_page_image_path(page_num)
            generated += 1
            if generated % 10 == 0:
                logger.info(
                    f"Progress: {page_num}/{total_pages} (generated {generated})"
                )

    logger.info(f"Complete! Generated: {generated}, Skipped: {skipped}")

    # Show file size summary
    total_size = 0
    for filename in os.listdir(MEDIA_DIR):
        if (
            filename.startswith("page_")
            and filename.endswith(".png")
            and "_img_" not in filename
        ):
            filepath = os.path.join(MEDIA_DIR, filename)
            total_size += os.path.getsize(filepath)

    total_mb = total_size / (1024 * 1024)
    avg_kb = (total_size / total_pages) / 1024
    logger.info(f"Total size: {total_mb:.1f}MB, Average per page: {avg_kb:.1f}KB")


if __name__ == "__main__":
    import sys

    force = "--force" in sys.argv

    if force:
        print("Force regeneration mode: Will regenerate ALL images")
        response = input("Are you sure? (y/n): ")
        if response.lower() != "y":
            print("Cancelled")
            sys.exit(0)
    else:
        print("Generating missing images only (use --force to regenerate all)")

    regenerate_all_images(force=force)
