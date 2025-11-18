"""Test FastAPI endpoints"""

from fastapi.testclient import TestClient
from unittest.mock import patch
from api import app


client = TestClient(app)


def test_health_endpoint():
    """Test /health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_endpoint_method():
    """Test /health only accepts GET"""
    response = client.post("/health")
    assert response.status_code == 405  # Method not allowed


@patch("api.rag.answer")
def test_chat_answer_endpoint_success(mock_rag_answer):
    """Test /chat/answer endpoint with successful response"""
    from src.models import AnswerResponse, AnswerContent, Media

    # Mock SimpleRAG answer - return actual AnswerResponse object
    mock_response = AnswerResponse(
        mode="answer",
        answer=AnswerContent(
            title="Test Answer",
            summary="Test summary",
            steps=["Step 1"],
            verification=["Verified"],
        ),
        links=["/media/page_1.png"],
        media=Media(images=["Diagram 1.1"]),
        latency_ms=100,
    )
    mock_rag_answer.return_value = mock_response

    # Test endpoint
    response = client.post(
        "/chat/answer", json={"question": "What are fire safety requirements?"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "answer"
    assert "answer" in data
    assert "latency_ms" in data
    assert isinstance(data["latency_ms"], int)


@patch("api.rag.answer")
def test_chat_answer_endpoint_no_context(mock_rag_answer):
    """Test /chat/answer when no relevant context found"""
    from src.models import AnswerResponse, AnswerContent, Media

    # Mock SimpleRAG answer for no context scenario
    mock_response = AnswerResponse(
        mode="answer",
        answer=AnswerContent(
            title="No Information Found",
            summary="No relevant information was found in the documentation.",
            steps=["Try rephrasing your question"],
            verification=["No supporting documents"],
        ),
        links=[],
        media=Media(images=[]),
        latency_ms=50,
    )
    mock_rag_answer.return_value = mock_response

    response = client.post("/chat/answer", json={"question": "Irrelevant question"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"]["title"] == "No Information Found"
    assert "latency_ms" in data
    assert isinstance(data["latency_ms"], int)


def test_chat_answer_missing_question():
    """Test /chat/answer with missing question field"""
    response = client.post("/chat/answer", json={})
    assert response.status_code == 422  # Validation error


def test_chat_answer_invalid_json():
    """Test /chat/answer with invalid JSON"""
    response = client.post(
        "/chat/answer",
        data="invalid json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
