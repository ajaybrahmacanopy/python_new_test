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

# Chunking settings
MAX_TOKENS = 350
OVERLAP_TOKENS = 50

# Embedding settings
EMBED_MODEL = "text-embedding-3-small"
INDEX_PATH = "data/fire_safety.index"
META_PATH = "data/fire_safety_metadata.pkl"
