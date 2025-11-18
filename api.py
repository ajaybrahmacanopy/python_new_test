"""
FastAPI application for RAG system
"""

import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.logger import logger
from src import (
    SimpleRAG,
    GuardrailViolation,
    validate_input,
    validate_output,
)
from src.models import AnswerResponse
from src.config import MEDIA_DIR

app = FastAPI(title="RAG System API", version="1.0.0")

# Mount static files to serve media
try:
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    logger.info(f"Media directory mounted: {MEDIA_DIR}")
except Exception as e:
    logger.warning(f"Failed to mount media directory: {e}")

# Initialize SimpleRAG
try:
    rag = SimpleRAG(top_k=5, candidate_k=25)
    logger.info("SimpleRAG initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SimpleRAG: {e}")
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
        # GUARDRAIL 1: Input validation
        try:
            sanitized_query = validate_input(request.question)
            logger.info(f"Processing query: {sanitized_query[:100]}...")
        except GuardrailViolation as e:
            logger.warning(f"Input guardrail violation: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        # Use SimpleRAG for end-to-end processing
        try:
            result = rag.answer(sanitized_query)
        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to generate answer: {str(e)}"
            )

        # GUARDRAIL 2: Output validation (lenient mode - allows diagram references)
        try:
            # Extract pages and media from result for validation
            pages = result.links
            media_files = result.media.images
            validate_output(result.model_dump(), pages, media_files, strict=False)
        except GuardrailViolation as e:
            logger.error(f"Output guardrail violation: {e}")
            raise HTTPException(
                status_code=500, detail=f"Generated answer failed validation: {str(e)}"
            )

        # Calculate total latency
        total_latency = int((time.time() - start_time) * 1000)

        # Log timing
        logger.info(f"Request completed - Total: {total_latency}ms")

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
