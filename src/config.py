"""Configuration settings"""

import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

# Need to remove this once we have a proper solution for the KMP_DUPLICATE_LIB_OK issue
# Have added due to time constraints
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# PDF Settings
PDF_PATH = "content/fire_safety_doc.pdf"
MEDIA_DIR = "static/media"

# RAG Configuration
# Chunking settings
CHUNK_SIZE = 600  # characters (~150 tokens) - balances context and precision
CHUNK_OVERLAP = 100  # characters (~25 tokens) - ensures continuity

# Retrieval settings
TOP_K = 5  # final results after reranking
CANDIDATE_K = 20  # initial FAISS candidates for reranking

# Embedding settings
EMBED_MODEL = "text-embedding-3-small"  # cost-effective, high-quality
INDEX_PATH = "data/fire_safety.index"
META_PATH = "data/fire_safety_metadata.pkl"

# Generation settings
TEMPERATURE = 0  # deterministic, factual outputs for technical docs

# Legacy settings (deprecated, kept for backward compatibility)
MAX_TOKENS = 350
OVERLAP_TOKENS = 50
