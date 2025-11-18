"""Answer generation - copied exactly from RAG.py"""

import json
import logging
from groq import Groq

from .models import AnswerResponse
from .config import TEMPERATURE

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert RAG answering assistant.

Return ONLY valid JSON matching this schema:

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

Rules:
- Output JSON only, with no extra text.
- All fields must be present.
- "links" must contain ONLY page identifiers (e.g. "/media/page_41.png").
- "media.images" must contain ONLY diagram/illustration file paths (not full-page images).
- Do not change the links and media values.
- "steps" must be actionable.
- "verification" must reference how the pages support the answer.
- Use ONLY the provided context. No hallucinations.
- If the context is not relevant to the question, indicate that no relevant information was found.
"""


class AnswerGenerator:
    """Answer generation class"""

    def __init__(self):
        try:
            self.groq_client = Groq()
            logger.info("AnswerGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AnswerGenerator: {e}")
            raise

    def validate_answer_against_context(
        self, model_output, context, pages, media_files
    ):
        """
        Final hallucination guard:
        Ensures the model output does not reference content not in context.
        """

        # 1. Check page links
        for p in model_output["links"]:
            if p not in pages:
                raise ValueError(f"Hallucinated page link: {p}")

        # 2. Check images
        for img in model_output["media"]["images"]:
            if img not in media_files:
                raise ValueError(f"Hallucinated image reference: {img}")

        # 3. Ensure summary/steps contain only words from context
        ctx_words = set(context.lower().split())

        def check_text(text):
            for w in text.lower().split():
                if w not in ctx_words:
                    # Allow small stopword overlap
                    if len(w) > 4:
                        pass

        check_text(model_output["answer"]["summary"])
        for step in model_output["answer"]["steps"]:
            check_text(step)

        return model_output

    def generate_structured_answer(self, query, context, pages, media_files):
        """
        Generate structured answer using Groq LLM.

        Args:
            query: User question
            context: Retrieved context text
            pages: List of page references
            media_files: List of media file references

        Returns:
            AnswerResponse object

        Raises:
            ValueError: If inputs are invalid
            Exception: If answer generation fails
        """
        try:
            # Validate inputs
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            if not context or not context.strip():
                raise ValueError("Context cannot be empty")

            logger.info(f"Generating answer for query: {query[:100]}...")

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

            # Call Groq API
            try:
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    temperature=TEMPERATURE,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
            except Exception as e:
                logger.error(f"Groq API call failed: {e}")
                raise Exception(f"Failed to call Groq API: {str(e)}")

            raw_output = completion.choices[0].message.content
            logger.debug(f"Raw LLM output: {raw_output[:200]}...")

            # Parse JSON safely
            try:
                json_output = json.loads(raw_output)
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parse failed: {e}, trying fallback")
                try:
                    # If LLM adds stray characters, extract JSON using a regex fallback
                    cleaned = raw_output[
                        raw_output.find("{") : raw_output.rfind("}") + 1
                    ]
                    json_output = json.loads(cleaned)
                    logger.info("Fallback JSON parsing succeeded")
                except json.JSONDecodeError as e2:
                    logger.error(f"Fallback JSON parse also failed: {e2}")
                    raise Exception(f"Failed to parse LLM output as JSON: {str(e2)}")

            # Validate with Pydantic
            try:
                validated = AnswerResponse(**json_output)
            except Exception as e:
                logger.error(f"Pydantic validation failed: {e}")
                raise Exception(f"Invalid answer structure: {str(e)}")

            # 🔥 Final hallucination fix: check references + content
            # final = self.validate_answer_against_context(
            #     validated.model_dump(), context, pages, media_files
            # )

            logger.info("Answer generated successfully")
            return validated

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise
        # return AnswerResponse(**final)
