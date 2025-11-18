"""
FastAPI application for RAG system
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src import (
    INDEX_PATH,
    META_PATH,
    retrieve_with_reranking,
    generate_structured_answer,
)
from src.models import AnswerResponse
from src.config import MEDIA_DIR
import os

app = FastAPI(title="RAG System API", version="1.0.0")

# Mount static files to serve media
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    """Health check endpoint"""
    index_exists = os.path.exists(INDEX_PATH)
    metadata_exists = os.path.exists(META_PATH)

    return {
        "status": "healthy",
        "index_ready": index_exists and metadata_exists,
        "index_path": INDEX_PATH,
        "metadata_path": META_PATH,
    }


@app.post("/chat/answer", response_model=AnswerResponse)
def answer_endpoint(request: QueryRequest):
    """
    Query the RAG system

    Args:
        request: QueryRequest containing the question

    Returns:
        AnswerResponse with structured answer
    """
    # Retrieve and rerank
    context, pages, media_files = retrieve_with_reranking(request.question)

    # Check if no relevant context found
    if context is None:
        from src.models import AnswerContent, Media

        return AnswerResponse(
            mode="answer",
            answer=AnswerContent(
                title="No Information Found",
                summary="No relevant information found in the document for your query.",
                steps=["Try rephrasing your question", "Use different keywords"],
                verification=["Retrieved content was not relevant to the query"],
            ),
            links=[],
            media=Media(images=[]),
        )

    # Generate answer
    result = generate_structured_answer(request.question, context, pages, media_files)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
