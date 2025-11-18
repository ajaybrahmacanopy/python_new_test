"""LLM-based reranker - copied exactly from RAG.py"""

import json
from groq import Groq

from .logger import logger
from .models import RerankResult


class LlamaReranker:
    """
    LLM-based cross-encoder-style reranker using Groq Llama 3.1 8B Instant.
    Produces STRICT JSON validated via Pydantic.
    """

    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.client = Groq()
        self.model = model

    def score_passages(self, query: str, passages: list):
        """
        Return Pydantic-validated list of scored passages.
        """

        # Combine passages for reranking prompt
        blocks = []
        for i, p in enumerate(passages):
            blocks.append(f"## Passage {i}\n{p['text'][:1000]}")
        passages_block = "\n\n".join(blocks)

        system_prompt = """
You are a relevance scoring model for Retrieval-Augmented Generation.

Return ONLY valid JSON.
No explanations. No extra text.

JSON Schema:

{
  "results": [
    {"id": number, "score": number between 0 and 1},
    ...
  ]
}

Rules:
- Score reflects how well the passage answers the query.
- Higher = more relevant.
- Score ONLY based on semantic relevance.
- Do not change passage IDs.
- Do not include text from passages.
"""

        user_prompt = f"""
Query:
{query}

Passages:
{passages_block}

Return JSON only.
"""

        # Call Llama 3.1 8B Instant
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw = resp.choices[0].message.content

        # Parse JSON reliably
        try:
            cleaned = raw[raw.find("{") : raw.rfind("}") + 1]
            data = json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse reranker JSON: {raw}")
            raise e

        # Validate using Pydantic
        return RerankResult(**data)
