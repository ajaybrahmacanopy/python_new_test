"""LLM-based passage reranking"""

import json
from groq import Groq

from .logger import logger
from .models import RerankResult
from .prompts import RERANKING_SYSTEM_PROMPT, get_reranking_user_prompt


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

        user_prompt = get_reranking_user_prompt(query, passages_block)

        # Call Llama 3.1 8B Instant
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": RERANKING_SYSTEM_PROMPT},
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
