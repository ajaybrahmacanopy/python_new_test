"""Answer generation with LLM"""

import json
import time
from groq import Groq

from .models import AnswerResponse
from .config import TEMPERATURE, API_TIMEOUT_MS, API_MAX_RETRIES


SYSTEM_PROMPT = """
    You are an expert RAG answering assistant.

    Return ONLY valid JSON matching this exact schema:

    {
    "mode": "answer",
    "answer": {
        "title": "string",
        "summary": "string",
        "steps": ["string", ...],
        "verification": ["string", ...]
    },
    "links": ["string", ...],
    "media": {
        "images": ["string", ...]
    }
    }

    CRITICAL RULES:
    - Output JSON only, with no extra text.
    - All fields must be present.
    - "links" must contain ONLY pages from the provided PAGES list.
    - "media.images" must contain ONLY diagrams from the provided MEDIA list.
    - Do NOT invent or hallucinate page numbers or media files.
    - Use ONLY the exact page and media references provided in the PAGES and MEDIA sections.
    - "steps" must be actionable.
    - "verification" must reference how the pages support the answer.
    - Use ONLY the provided context. No hallucinations.
    - If the context is not relevant to the question, indicate that no relevant
      information was found.
"""


class AnswerGenerator:
    """Simple, clean answer generator for RAG."""

    def __init__(self):
        self.client = Groq(timeout=API_TIMEOUT_MS / 1000)

    def _validate_references(self, output, pages, media_files):
        """
        Filter out references that aren't in the retrieved context.
        Returns cleaned output instead of raising errors.
        """
        # Filter links to only include retrieved pages
        valid_links = [p for p in output["links"] if p in pages]

        # Filter media to only include retrieved diagrams
        valid_media = [img for img in output["media"]["images"] if img in media_files]

        # Update output with filtered references
        output["links"] = valid_links
        output["media"]["images"] = valid_media

        return output

    def generate(self, query, context, pages, media_files):
        """Generate structured, validated answer."""

        if not query.strip():
            raise ValueError("Query cannot be empty")

        if not context.strip():
            raise ValueError("Context cannot be empty")

        user_prompt = f"""
QUESTION:
{query}

CONTEXT:
{context}

PAGES:
{pages}

MEDIA:
{media_files}
"""

        # Retry loop (simple & robust)
        response_text = None
        for attempt in range(API_MAX_RETRIES + 1):
            try:
                resp = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    temperature=TEMPERATURE,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                response_text = resp.choices[0].message.content
                break

            except Exception as e:
                if attempt == API_MAX_RETRIES:
                    raise RuntimeError(f"Groq API failed after retries: {e}")
                time.sleep(2**attempt)

        # JSON parsing with fallback
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            cleaned = response_text[
                response_text.find("{") : response_text.rfind("}") + 1
            ]
            result = json.loads(cleaned)

        # Filter out hallucinated references
        cleaned_result = self._validate_references(result, pages, media_files)

        # Pydantic validation with cleaned references
        validated = AnswerResponse(**cleaned_result)

        return validated
