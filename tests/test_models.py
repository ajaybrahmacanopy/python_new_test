"""Test Pydantic models"""

import pytest
from src.models import AnswerContent, Media, AnswerResponse


def test_answer_content_valid():
    """Test valid AnswerContent creation"""
    content = AnswerContent(
        title="Test Title",
        summary="Test summary",
        steps=["Step 1", "Step 2"],
        verification=["Verified"],
    )
    assert content.title == "Test Title"
    assert len(content.steps) == 2


def test_media_valid():
    """Test valid Media creation"""
    media = Media(images=["image1.png", "image2.png"])
    assert len(media.images) == 2


def test_answer_response_valid():
    """Test valid AnswerResponse creation"""
    response = AnswerResponse(
        mode="answer",
        answer=AnswerContent(
            title="Test", summary="Summary", steps=["Step 1"], verification=["Verified"]
        ),
        links=["/media/page_1.png"],
        media=Media(images=["diagram.png"]),
    )
    assert response.mode == "answer"
    assert len(response.links) == 1


def test_answer_response_invalid_missing_fields():
    """Test AnswerResponse with missing required fields"""
    with pytest.raises(Exception):
        AnswerResponse(
            mode="answer",
            answer=None,  # Missing required field
            links=[],
            media=Media(images=[]),
        )
