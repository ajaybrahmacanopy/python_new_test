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


@patch("api.retriever.retrieve_with_reranking")
@patch("api.generator.generate_structured_answer")
def test_chat_answer_endpoint_success(mock_generate, mock_retrieve):
    """Test /chat/answer endpoint with successful response"""
    from src.models import AnswerResponse, AnswerContent, Media

    # Mock retrieval
    mock_retrieve.return_value = (
        "Sample context",
        ["/media/page_1.png"],
        ["Diagram 1.1"],
    )

    # Mock generation - return actual AnswerResponse object
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
    )
    mock_generate.return_value = mock_response

    # Test endpoint
    response = client.post(
        "/chat/answer", json={"question": "What are fire safety requirements?"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "answer"
    assert "answer" in data


@patch("api.retriever.retrieve_with_reranking")
def test_chat_answer_endpoint_no_context(mock_retrieve):
    """Test /chat/answer when no relevant context found"""
    # Mock retrieval returning None
    mock_retrieve.return_value = (None, None, None)

    response = client.post("/chat/answer", json={"question": "Irrelevant question"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"]["title"] == "No Information Found"


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
