"""Tests for guardrails module"""

import pytest
from src.guardrails import (
    GuardrailViolation,
    validate_input,
    validate_output,
    validate_context,
    sanitize_input,
)


class TestInputGuardrails:
    """Test input validation guardrails"""

    def test_valid_query(self):
        """Test valid query passes"""
        query = "What are the requirements for residential buildings?"
        result = validate_input(query)
        assert "requirements" in result

    def test_query_too_short(self):
        """Test query that's too short is rejected"""
        with pytest.raises(GuardrailViolation, match="too short"):
            validate_input("Hi")

    def test_query_too_long(self):
        """Test query that's too long is rejected"""
        long_query = "A" * 600
        with pytest.raises(GuardrailViolation, match="too long"):
            validate_input(long_query)

    def test_sanitize_whitespace(self):
        """Test excessive whitespace is normalized"""
        query = "What   are    the    requirements?"
        result = sanitize_input(query)
        assert "   " not in result
        assert result == "What are the requirements?"

    def test_sanitize_html_tags(self):
        """Test HTML tags are removed"""
        query = "What are <b>requirements</b>?"
        result = sanitize_input(query)
        assert "<b>" not in result
        assert "</b>" not in result

    def test_empty_query_rejected(self):
        """Test empty query is rejected"""
        with pytest.raises(GuardrailViolation, match="non-empty string"):
            validate_input("")

    def test_none_query_rejected(self):
        """Test None query is rejected"""
        with pytest.raises(GuardrailViolation, match="non-empty string"):
            validate_input(None)


class TestOutputGuardrails:
    """Test output validation guardrails"""

    def test_valid_answer(self):
        """Test valid answer structure passes"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Fire Door Requirements",
                "summary": "Fire doors must meet specific standards.",
                "steps": ["Install compliant doors", "Ensure proper sealing"],
                "verification": ["See Section 5.3"],
            },
            "links": ["/media/page_42.png"],
            "media": {"images": ["/media/page_42_img_0.png"]},
        }
        pages = ["/media/page_42.png"]
        media = ["/media/page_42_img_0.png"]

        # Should not raise
        validate_output(answer, pages, media)

    def test_missing_required_field(self):
        """Test missing required field is detected"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Test",
                "summary": "Summary",
                "steps": [],
                # missing verification
            },
            "links": [],
            "media": {"images": []},
        }

        with pytest.raises(GuardrailViolation, match="Missing required"):
            validate_output(answer, [], [])

    def test_hallucinated_page_link_strict(self):
        """Test hallucinated page reference is detected in strict mode"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Test Answer",
                "summary": "This is a summary text",
                "steps": ["Step 1"],
                "verification": ["Ver"],
            },
            "links": ["/media/page_999.png"],  # Not in allowed pages
            "media": {"images": []},
        }
        allowed_pages = ["/media/page_42.png"]

        with pytest.raises(GuardrailViolation, match="Invalid page reference"):
            validate_output(answer, allowed_pages, [], strict=True)

    def test_hallucinated_media_strict_mode(self):
        """Test hallucinated media reference is detected in strict mode"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Test Answer",
                "summary": "This is a summary text",
                "steps": ["Step 1"],
                "verification": ["Ver"],
            },
            "links": [],
            "media": {"images": ["/media/fake_img.png"]},
        }
        allowed_media = ["/media/page_42_img_0.png"]

        # Strict mode should detect this
        with pytest.raises(GuardrailViolation, match="Invalid media reference"):
            validate_output(answer, [], allowed_media, strict=True)

    def test_diagram_reference_allowed(self):
        """Test diagram references are allowed in lenient mode"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Test Answer",
                "summary": "This is a summary text",
                "steps": ["Step 1"],
                "verification": ["Ver"],
            },
            "links": [],
            "media": {"images": ["Diagram D6", "/media/Diagram D6.png"]},
        }

        # Should not raise in lenient mode
        validate_output(answer, [], [], strict=False)

    def test_answer_too_long(self):
        """Test excessively long answer is rejected"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Test Answer Title",
                "summary": "A" * 3000,  # Too long (over 2000 chars)
                "steps": [],
                "verification": [],
            },
            "links": [],
            "media": {"images": []},
        }

        with pytest.raises(GuardrailViolation, match="too long"):
            validate_output(answer, [], [])

    def test_too_many_steps(self):
        """Test too many steps is rejected"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Test Answer Title",
                "summary": "This is a valid summary text",
                "steps": ["Step"] * 15,  # Too many (over 10 steps)
                "verification": [],
            },
            "links": [],
            "media": {"images": []},
        }

        with pytest.raises(GuardrailViolation, match="Too many steps"):
            validate_output(answer, [], [])

    def test_empty_title_rejected(self):
        """Test empty title is rejected"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "",  # Empty
                "summary": "Summary text here",
                "steps": [],
                "verification": [],
            },
            "links": [],
            "media": {"images": []},
        }

        with pytest.raises(GuardrailViolation, match="Title too short"):
            validate_output(answer, [], [])


class TestContextGuardrails:
    """Test context validation guardrails"""

    def test_valid_context(self):
        """Test valid context passes"""
        context = "Regulations require proper exits and signage." * 10
        result = validate_context(context)
        assert result == context  # Should return sanitized context

    def test_empty_context_rejected(self):
        """Test empty context is rejected"""
        with pytest.raises(GuardrailViolation, match="Context is empty"):
            validate_context("")

    def test_context_too_long(self):
        """Test excessively long context is rejected"""
        context = "A" * 60000
        with pytest.raises(GuardrailViolation, match="Context too long"):
            validate_context(context)


class TestMainFunctions:
    """Test main validation functions"""

    def test_validate_input_function(self):
        """Test validate_input main function"""
        query = "What are the requirements?"
        result = validate_input(query)
        assert "requirements" in result.lower()

    def test_validate_input_raises(self):
        """Test validate_input raises on violation"""
        with pytest.raises(GuardrailViolation):
            validate_input("AB")  # Too short

    def test_validate_output_function(self):
        """Test validate_output main function"""
        answer = {
            "mode": "answer",
            "answer": {
                "title": "Test Title",
                "summary": "Test summary text",
                "steps": [],
                "verification": [],
            },
            "links": [],
            "media": {"images": []},
        }
        validate_output(answer, [], [])

    def test_validate_context_function(self):
        """Test validate_context main function"""
        context = "Context text here" * 10
        result = validate_context(context)
        assert result  # Should return sanitized context
        assert isinstance(result, str)
