# RAG System API

FastAPI application for the RAG system.

## Installation

```bash
pip install fastapi uvicorn
```

## Running the API

```bash
# Start the server
python api.py

# Or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## Endpoints

### Media Files

**GET** `/media/{filename}`

Serves static media files (page images and diagrams).

**Example:**

```bash
# Access a page image
curl http://localhost:8000/media/page_148.png

# Or view in browser
http://localhost:8000/media/page_148.png
```

### Health Check

**GET** `/health`

Returns the health status of the API and whether the index is ready.

**Example:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy"
}
```

### Chat Answer

**POST** `/chat/answer`

Query the RAG system with a question.

**Request Body:**

```json
{
  "question": "What are fire door requirements?"
}
```

**Example:**

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
    "summary": "...",
    "steps": ["Step 1", "Step 2"],
    "verification": ["Verified from pages..."]
  },
  "links": ["/media/page_41.png"],
  "media": {
    "images": ["Diagram 3.1"]
  },
  "latency_ms": 2450
}
```

**Response Fields:**

- `latency_ms`: Total request processing time in milliseconds (includes retrieval and generation)

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Notes

- The index must be built before querying (run `main.py` first)
- The API will return a "No Information Found" response if no relevant content is retrieved
- Media links in the response (e.g., `/media/page_148.png`) are directly accessible via the API
- You can view page images in your browser: `http://localhost:8000/media/page_148.png`
