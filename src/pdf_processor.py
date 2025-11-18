"""PDF processing functions - copied exactly from RAG.py"""

import os
import uuid
import fitz  # PyMuPDF
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import PDF_PATH, MEDIA_DIR
from .utils import count_tokens, find_diagram_ids

os.makedirs(MEDIA_DIR, exist_ok=True)

# Recommended chunk settings
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  # Adjust based on your Llama context needs
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def get_page_image_path(page_num: int) -> str:
    filename = f"page_{page_num}.png"
    out_path = os.path.join(MEDIA_DIR, filename)

    if not os.path.exists(out_path):
        with fitz.open(PDF_PATH) as doc:
            page = doc[page_num - 1]
            pix = page.get_pixmap(dpi=10)
            pix.save(out_path)

    return f"/media/{filename}"


def extract_embedded_images(doc, page, page_num: int):
    """
    Extract diagrams & inline images from a page.
    """
    image_list = page.get_images(full=True)
    saved_paths = []

    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        ext = base_image["ext"]

        filename = f"page_{page_num}_img_{img_index}.{ext}"
        out_path = os.path.join(MEDIA_DIR, filename)

        with open(out_path, "wb") as f:
            f.write(image_bytes)

        saved_paths.append(f"/media/{filename}")

    return saved_paths


def extract_paragraphs(page):
    """
    Splits on double newlines.
    """
    raw_text = page.get_text("text")
    paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
    return paragraphs


def extract_tables_from_page(pdf_path, page_num):
    """
    Extracts tables using pdfplumber.
    Returns list of tables as list-of-lists.
    """
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]
        extracted = page.extract_tables()
        for t in extracted:
            if t:
                tables.append(t)
    return tables


def table_to_markdown(table):
    """
    Convert a table (list-of-lists) into Markdown safely.
    Handles None, empty strings, uneven rows, etc.
    """
    md = ""

    # Skip empty/invalid tables
    if not table or not isinstance(table, list):
        return ""

    # Sanitize header
    header = table[0]
    header = [(str(col).strip() if col is not None else "") for col in header]

    # Build header row
    md += "| " + " | ".join(header) + " |\n"
    md += "| " + " | ".join(["---"] * len(header)) + " |\n"

    # Process all remaining rows
    for row in table[1:]:
        clean_row = [str(cell).strip() if cell is not None else "" for cell in row]

        # Pad row if it's shorter than header
        if len(clean_row) < len(header):
            clean_row += [""] * (len(header) - len(clean_row))

        md += "| " + " | ".join(clean_row) + " |\n"

    return md


def build_chunk_record(text, page_num, page_img, embedded_imgs, is_table=False):
    diagram_ids = find_diagram_ids(text)

    media_paths = [page_img] + embedded_imgs

    return {
        "id": str(uuid.uuid4()),
        "page": page_num,
        "text": text,
        "token_count": count_tokens(text),
        "contains_diagram": len(diagram_ids) > 0,
        "diagram_ids": diagram_ids,
        "media": media_paths,
        "is_table": is_table,
    }


def build_chunks_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_chunks = []

    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page = doc[page_idx]

        print(f"Processing page {page_num}...")

        # Extract page-level assets
        page_img = get_page_image_path(page_num)
        embedded_imgs = extract_embedded_images(doc, page, page_num)
        tables = extract_tables_from_page(pdf_path, page_num)

        # 1️⃣ Convert tables to markdown chunks
        for t in tables:
            md_table = table_to_markdown(t)

            all_chunks.append(
                build_chunk_record(
                    text=md_table,
                    page_num=page_num,
                    page_img=page_img,
                    embedded_imgs=embedded_imgs,
                    is_table=True,
                )
            )

        # 2️⃣ Extract text from page
        raw_text = page.get_text("text") or ""

        # 3️⃣ Generate chunks using LangChain splitter
        text_chunks = splitter.split_text(raw_text)

        # 4️⃣ Add each text chunk with metadata
        for ch in text_chunks:
            all_chunks.append(
                build_chunk_record(
                    text=ch.strip(),
                    page_num=page_num,
                    page_img=page_img,
                    embedded_imgs=embedded_imgs,
                    is_table=False,
                )
            )

    return all_chunks
