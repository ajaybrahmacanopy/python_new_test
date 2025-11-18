# RAG System - Fire Safety Document Q&A

A Retrieval-Augmented Generation (RAG) system for querying fire safety documents using semantic search, LLM reranking, and structured answer generation.

## Features

- Semantic search with FAISS vector database
- Hybrid retrieval (FAISS + BM25)
- LLM-based reranking using Groq
- Structured JSON responses validated with Pydantic
- Automatic extraction of diagrams and images
- REST API with FastAPI
- Docker support

## Prerequisites

You need API keys for:

- **OpenAI API** - For embeddings: https://platform.openai.com/api-keys
- **Groq API** - For LLM: https://console.groq.com/keys

## Quick Start

### 1. Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
```

### 2. Docker Setup (Recommended)

```bash
# Build and start
docker-compose up --build

# API will be available at http://localhost:8000
```

### 3. Local Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build FAISS index (first time only)
python main.py

# Start API server
python api.py
# or
uvicorn api:app --reload
```

## Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Query API

```bash
curl -X POST "http://localhost:8000/chat/answer" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are fire door requirements?"}'
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Project Structure

```
.
├── src/                      # Source code
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── logger.py            # Loguru logging
│   ├── pdf_processor.py     # PDF parsing
│   ├── vector_store.py      # FAISS + BM25 hybrid search
│   ├── reranker.py          # LLM reranking
│   ├── generator.py         # Answer generation
│   ├── simple_rag.py        # End-to-end RAG pipeline
│   ├── guardrails.py        # Input/output validation
│   └── utils.py             # Utilities
├── tests/                   # Unit tests
├── content/                 # PDF documents
├── data/                    # FAISS index and metadata
├── static/media/            # Extracted images
├── logs/                    # Log files
├── api.py                   # FastAPI application
├── main.py                  # Index builder
├── example.py               # Usage example
├── regenerate_images.py     # Image regeneration utility
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Lint code
flake8 src/ api.py main.py regenerate_images.py tests/

# Format code
black src/ api.py main.py regenerate_images.py tests/
```

## Configuration

Default settings in `src/config.py`:

- Chunk size: 600 characters
- Chunk overlap: 100 characters
- Embedding model: text-embedding-3-small
- Top-k results: 5
- Candidate-k for reranking: 25
- Temperature: 0

## Technologies

- Python 3.12+
- FastAPI - REST API framework
- FAISS - Vector similarity search
- LangChain - RAG components
- OpenAI - Text embeddings
- Groq - LLM (Llama 3.1 8B Instant)
- Loguru - Logging
- Pydantic - Data validation
- Docker - Containerization
- Pytest - Testing

## Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose build --no-cache
```

## Troubleshooting

### FAISS Index Not Found

```bash
python main.py  # Build the index
```

### Missing Images

```bash
python regenerate_images.py  # Regenerate all images
```

### Port Already in Use

```bash
# Change port in docker-compose.yml or run:
uvicorn api:app --port 8001
```

## License

This project is for internal use only.
