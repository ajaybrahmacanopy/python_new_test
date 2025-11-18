# RAG System - Fire Safety Document Q&A

![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-39%25-yellow)
![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)

A production-ready Retrieval-Augmented Generation (RAG) system for querying fire safety documents with semantic search, reranking, and structured answer generation.

## ✨ Features

- 🔍 **Semantic Search** - FAISS vector search with OpenAI embeddings
- 🎯 **Smart Reranking** - LLM-based relevance scoring with Groq
- 📊 **Structured Answers** - Validated JSON responses with Pydantic
- 🖼️ **Media Support** - Automatic extraction and serving of diagrams/images
- 🏗️ **OOP Architecture** - Clean, modular class-based design
- 🐳 **Docker Ready** - Full containerization support
- 🧪 **Tested** - Unit tests with 39% coverage
- 🚀 **CI/CD** - GitHub Actions for testing, linting, and Docker builds
- 📚 **REST API** - FastAPI with automatic documentation

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run
docker-compose up --build

# API available at http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key
export GROQ_API_KEY=your_key

# Build FAISS index (first time only)
python main.py

# Run API server
uvicorn api:app --reload
```

## 📁 Project Structure

```
.
├── src/                      # Main source code
│   ├── config.py            # Configuration and API keys
│   ├── models.py            # Pydantic data models
│   ├── utils.py             # Utility functions
│   ├── pdf_processor.py     # PDF parsing and chunking
│   ├── embeddings.py        # FAISS indexing and search
│   ├── retriever.py         # Reranking and retrieval
│   └── generator.py         # Answer generation
├── tests/                   # Unit tests
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_api.py
├── content/                 # PDF documents
├── data/                    # FAISS index and metadata
├── static/media/            # Extracted images
├── api.py                   # FastAPI application
├── main.py                  # Index builder script
├── example.py               # Usage examples
├── Dockerfile               # Docker image
├── docker-compose.yml       # Docker orchestration
└── requirements.txt         # Python dependencies
```

## 🔧 API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy"
}
```

### Query Endpoint

```bash
curl -X POST "http://localhost:8000/chat/answer" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are fire door requirements?"}'
```

**Response:**

```json
{
  "mode": "answer",
  "answer": {
    "title": "Fire Door Requirements",
    "summary": "Fire doors must meet specific standards...",
    "steps": [
      "Install fire doors with appropriate rating",
      "Ensure proper sealing and hardware"
    ],
    "verification": ["See Section 5.3 of Approved Document B"]
  },
  "links": ["/media/page_42.png"],
  "media": {
    "images": ["Diagram 5.1"]
  }
}
```

### Access Media Files

```bash
curl http://localhost:8000/media/page_42.png --output page.png
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py

# View coverage report
open htmlcov/index.html
```

### Run Linting

```bash
# Check code quality
flake8 src/ api.py main.py example.py

# Check formatting
black --check src/ api.py main.py example.py

# Auto-format
black src/ api.py main.py example.py
```

### Use Makefile

```bash
make test          # Run tests
make test-cov      # Run with coverage
make lint          # Run linter
make format        # Format code
make clean         # Clean cache files
make docker-build  # Build Docker image
```

## 🐳 Docker

### Build and Run

```bash
# Build
docker-compose build

# Run (detached)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
```

Docker Compose will automatically load these variables.

## 🔄 GitHub Actions CI/CD

The project includes automated workflows:

1. **Lint Job** - Runs `flake8` and `black`
2. **Test Job** - Runs `pytest` with coverage
3. **Docker Build** - Builds and tests Docker image

## 🏗️ Architecture

### 1. PDF Processing

- Extract text, tables, and images from PDF
- Chunk text with overlap for better retrieval
- Store chunk metadata (page, media, diagrams)

### 2. Embedding & Indexing

- Generate embeddings with `text-embedding-3-small`
- Build FAISS index for fast similarity search
- Persist index and metadata to disk

### 3. Retrieval

- Semantic search with FAISS
- LLM-based reranking with Groq
- Context relevance filtering

### 4. Answer Generation

- Structured answer generation with Groq
- Pydantic validation for data quality
- JSON parsing with fallback handling

## ⚙️ RAG Configuration

**Optimized Settings:**

- **Chunk Size:** 600 characters (~150 tokens) - Maintains semantic coherence for technical regulations while preventing information dilution
- **Overlap:** 100 characters - Ensures cross-chunk context continuity, preventing answer fragmentation at boundaries
- **Embedding:** `text-embedding-3-small` - Optimal cost-performance ratio; 1536 dimensions sufficient for domain-specific retrieval
- **Top-k:** 5 results - Balances answer comprehensiveness with noise reduction; more degrades precision
- **Candidate-k:** 20 - Provides reranker adequate selection pool (4x final results)
- **Temperature:** 0 - Eliminates stochasticity for deterministic, factual responses critical in regulatory contexts

These parameters optimize retrieval precision and answer quality for structured technical documents while maintaining efficiency.

## 📚 Documentation

- [API Documentation](API_README.md) - FastAPI endpoints
- [Testing Guide](TESTING_README.md) - Testing and CI/CD
- [Source Documentation](src/README.md) - Code structure

## 🛠️ Technologies

- **Python 3.13** - Core language
- **FastAPI** - REST API framework
- **FAISS** - Vector similarity search
- **OpenAI API** - Text embeddings
- **Groq API** - LLM for reranking and generation
- **PyMuPDF** - PDF parsing
- **Pydantic** - Data validation
- **Docker** - Containerization
- **Pytest** - Testing framework
- **GitHub Actions** - CI/CD

## 📊 Coverage Report

Current test coverage: **39%**

| Module           | Coverage |
| ---------------- | -------- |
| config.py        | 100%     |
| models.py        | 100%     |
| utils.py         | 71%      |
| embeddings.py    | 28%      |
| retriever.py     | 32%      |
| generator.py     | 26%      |
| pdf_processor.py | 22%      |

## 🔐 Security

- API keys stored in environment variables
- `.env` file excluded from git
- `.ipynb_checkpoints/` excluded from git
- Git history cleaned of sensitive data

## 🎯 Next Steps

- [ ] Increase test coverage to >80%
- [ ] Add integration tests
- [ ] Set up Codecov badge
- [ ] Add performance benchmarks
- [ ] Implement caching layer
- [ ] Add multi-document support

## 📝 License

This project is for internal use only.

## 🤝 Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass (`make test`)
4. Run linter (`make lint`)
5. Format code (`make format`)
6. Submit PR

## 🆘 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, FAISS, and OpenAI**
