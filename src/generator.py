"""Answer generation with LLM"""

import json
import time
from groq import Groq

from .models import AnswerResponse
from .config import TEMPERATURE, API_TIMEOUT_MS, API_MAX_RETRIES
from .prompts import ANSWER_GENERATION_SYSTEM_PROMPT, get_answer_generation_user_prompt


class AnswerGenerator:
    """Simple, clean answer generator for RAG."""

    def __init__(self):
        self.client = Groq(timeout=API_TIMEOUT_MS / 1000)

    def _detect_hallucination(self, output):
        """
        Detect if the model is hallucinating by checking for telltale phrases
        in the verification or summary fields.

        Returns True if hallucination detected, False otherwise.
        """
        hallucination_indicators = [
            "general knowledge",
            "does not directly relate",
            "does not provide any information",
            "based on common knowledge",
            "not mentioned in",
            "context does not contain",
            "outside the provided context",
            "beyond the scope",
            "however, based on",
            "not directly related to",
            "does not discuss",
        ]

        # Check verification field
        verification = output.get("answer", {}).get("verification", [])
        for item in verification:
            item_lower = item.lower()
            for indicator in hallucination_indicators:
                if indicator in item_lower:
                    return True

        # Check summary
        summary = output.get("answer", {}).get("summary", "").lower()
        for indicator in hallucination_indicators:
            if indicator in summary:
                return True

        return False

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

        user_prompt = get_answer_generation_user_prompt(
            query, context, pages, media_files
        )

        # Retry loop (simple & robust)
        response_text = None
        for attempt in range(API_MAX_RETRIES + 1):
            try:
                resp = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    temperature=TEMPERATURE,
                    messages=[
                        {"role": "system", "content": ANSWER_GENERATION_SYSTEM_PROMPT},
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

        # Detect hallucination - if detected, return "No Information Found" response
        if self._detect_hallucination(result):
            result = {
                "mode": "answer",
                "answer": {
                    "title": "No Information Found",
                    "summary": (
                        "No relevant information was found in the documentation."
                    ),
                    "steps": [],
                    "verification": [],
                },
                "links": [],
                "media": {"images": []},
            }

        # Filter out hallucinated references
        cleaned_result = self._validate_references(result, pages, media_files)

        # Pydantic validation with cleaned references
        validated = AnswerResponse(**cleaned_result)

        return validated
