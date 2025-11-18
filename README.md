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

### 2. Docker Setup

```bash
# Build and start
docker-compose up --build

# API will be available at http://localhost:8000
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

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Lint code
flake8 src/ api.py main.py tests/

# Format code
black src/ api.py main.py tests/
```

## Configuration

Default settings in `src/config.py`:

- **Chunk size: 1000 characters** - Balances context preservation with retrieval precision. Large enough to capture complete concepts in technical documentation while small enough for focused retrieval.
- **Chunk overlap: 150 characters** - Ensures critical information spanning chunk boundaries isn't lost, maintaining continuity across splits.
- **Top-k: 5** - Provides sufficient context diversity without overwhelming the LLM. After reranking from 30 FAISS candidates, top 5 ensures quality over quantity.
- **Candidate-k: 30** - Initial FAISS retrieval pool for LLM reranking. Large enough to capture diverse relevant passages while keeping reranking latency manageable (~2-3s).
- **Embedding: text-embedding-3-small** - OpenAI's cost-effective model (1536-dim) with strong semantic understanding. Balances performance and affordability for technical document retrieval.
- **Temperature: 0** - Ensures deterministic, factual outputs critical for technical/regulatory documentation. Eliminates hallucination risk in safety-critical domain.

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
