"""
FastAPI application for RAG system
"""

import logging
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src import (
    Retriever,
    AnswerGenerator,
)
from src.models import AnswerResponse, AnswerContent, Media
from src.config import MEDIA_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG System API", version="1.0.0")

# Mount static files to serve media
try:
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    logger.info(f"Media directory mounted: {MEDIA_DIR}")
except Exception as e:
    logger.warning(f"Failed to mount media directory: {e}")

# Initialize classes
try:
    retriever = Retriever()
    generator = AnswerGenerator()
    logger.info("Retriever and Generator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    raise


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/chat/answer", response_model=AnswerResponse)
def answer_endpoint(request: QueryRequest):
    """
    Query the RAG system

    Args:
        request: QueryRequest containing the question

    Returns:
        AnswerResponse with structured answer

    Raises:
        HTTPException: If processing fails
    """
    start_time = time.time()

    try:
        # Validate input
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        logger.info(f"Processing query: {request.question[:100]}...")

        # Retrieve and rerank
        retrieval_start = time.time()
        try:
            context, pages, media_files = retriever.retrieve_with_reranking(
                request.question
            )
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve context: {str(e)}"
            )
        retrieval_time = (time.time() - retrieval_start) * 1000  # Convert to ms

        # Check if no relevant context found
        if context is None:
            total_latency = int((time.time() - start_time) * 1000)
            logger.info(
                f"No relevant context found - Retrieval: {retrieval_time:.2f}ms, Total: {total_latency}ms"
            )
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
                latency_ms=total_latency,
            )

        # Generate answer
        generation_start = time.time()
        try:
            result = generator.generate_structured_answer(
                request.question, context, pages, media_files
            )
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to generate answer: {str(e)}"
            )
        generation_time = (time.time() - generation_start) * 1000  # Convert to ms

        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)

        # Log timing breakdown
        logger.info(
            f"Request completed - Retrieval: {retrieval_time:.2f}ms, "
            f"Generation: {generation_time:.2f}ms, Total: {total_latency}ms"
        )

        # Add latency to response
        result.latency_ms = total_latency
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in answer_endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
