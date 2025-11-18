"""Simple guardrails for RAG system safety"""

import re
from typing import List
from .logger import logger


class GuardrailViolation(Exception):
    """Raised when a guardrail check fails"""

    pass


# Constants
MIN_QUERY_LENGTH = 3
MAX_QUERY_LENGTH = 500
MAX_ANSWER_LENGTH = 2000
MAX_STEPS = 10
MAX_LINKS = 10
MAX_MEDIA = 5
MIN_CONTEXT_LENGTH = 50
MAX_CONTEXT_LENGTH = 50000

# Suspicious patterns for prompt injection
INJECTION_PATTERNS = [
    r"ignore\s+.*(previous|above|all).*instructions?",
    r"you\s+are\s+now",
    r"new\s+instructions?",
    r"system\s*:\s*you",
    r"<\s*script\s*>",
    r"javascript:",
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__",
    r"forget\s+(everything|all)",
    r"disregard\s+(previous|above)",
]


def sanitize_input(query: str) -> str:
    """
    Sanitize and normalize input query.

    Removes:
    - Excessive whitespace
    - Control characters
    - HTML tags
    - Special characters
    """
    # Remove excessive whitespace
    query = " ".join(query.split())

    # Remove control characters
    query = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", query)

    # Remove HTML tags
    query = re.sub(r"<[^>]+>", "", query)

    # Remove special characters that could be injection attempts
    query = re.sub(r"[{}[\]\\]", "", query)

    return query.strip()


def validate_input(query: str) -> str:
    """
    Validate and sanitize input query.

    Args:
        query: User query to validate

    Returns:
        Sanitized query string

    Raises:
        GuardrailViolation: If query fails validation
    """
    if not query or not isinstance(query, str):
        raise GuardrailViolation("Query must be a non-empty string")

    # Check length
    length = len(query.strip())
    if length < MIN_QUERY_LENGTH:
        raise GuardrailViolation(f"Query too short (min {MIN_QUERY_LENGTH} chars)")
    if length > MAX_QUERY_LENGTH:
        raise GuardrailViolation(f"Query too long (max {MAX_QUERY_LENGTH} chars)")

    # Check for injection patterns
    query_lower = query.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            logger.warning(f"Injection attempt detected: {pattern}")
            raise GuardrailViolation(
                "Query contains suspicious patterns and was blocked for security"
            )

    # Sanitize after security checks
    return sanitize_input(query)


def validate_output(
    answer_dict: dict,
    allowed_pages: List[str],
    allowed_media: List[str],
    strict: bool = False,
) -> None:
    """
    Validate output meets all requirements.

    Args:
        answer_dict: Generated answer dictionary
        allowed_pages: List of allowed page references
        allowed_media: List of allowed media references
        strict: If True, enforce exact matching (default: False)

    Raises:
        GuardrailViolation: If output fails validation
    """
    # Check required top-level keys
    required_keys = ["mode", "answer", "links", "media"]
    for key in required_keys:
        if key not in answer_dict:
            raise GuardrailViolation(f"Missing required field: {key}")

    # Check answer subfields
    answer = answer_dict.get("answer", {})
    required_answer_keys = ["title", "summary", "steps", "verification"]
    for key in required_answer_keys:
        if key not in answer:
            raise GuardrailViolation(f"Missing required answer field: {key}")

    # Check quality
    title = answer.get("title", "").strip()
    if not title or len(title) < 5:
        raise GuardrailViolation("Title too short or empty")

    summary = answer.get("summary", "").strip()
    if not summary or len(summary) < 10:
        raise GuardrailViolation("Summary too short or empty")

    # Check length limits
    if len(summary) > MAX_ANSWER_LENGTH:
        raise GuardrailViolation(f"Answer too long (max {MAX_ANSWER_LENGTH} chars)")

    steps = answer.get("steps", [])
    if len(steps) > MAX_STEPS:
        raise GuardrailViolation(f"Too many steps (max {MAX_STEPS})")

    # Check links
    links = answer_dict.get("links", [])
    if len(links) > MAX_LINKS:
        raise GuardrailViolation(f"Too many links (max {MAX_LINKS})")

    for link in links:
        if not link.startswith("/media/"):
            raise GuardrailViolation(f"Invalid link format: {link}")
        if strict and link not in allowed_pages:
            raise GuardrailViolation(f"Invalid page reference: {link}")

    # Check media
    media_images = answer_dict.get("media", {}).get("images", [])
    if len(media_images) > MAX_MEDIA:
        raise GuardrailViolation(f"Too many media files (max {MAX_MEDIA})")

    for img in media_images:
        # Allow diagram references and /media/ paths
        if not (img.startswith("/media/") or img.startswith("Diagram ")):
            raise GuardrailViolation(f"Invalid media format: {img}")
        if strict and not img.startswith("Diagram ") and img not in allowed_media:
            raise GuardrailViolation(f"Invalid media reference: {img}")


def validate_context(context: str) -> None:
    """
    Validate retrieved context.

    Args:
        context: Retrieved context string

    Raises:
        GuardrailViolation: If context is invalid
    """
    if not context:
        raise GuardrailViolation("Context is empty")

    length = len(context)
    if length < MIN_CONTEXT_LENGTH:
        logger.warning(f"Context very short: {length} chars")
    if length > MAX_CONTEXT_LENGTH:
        raise GuardrailViolation(f"Context too long (max {MAX_CONTEXT_LENGTH} chars)")
