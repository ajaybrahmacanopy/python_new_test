"""Utility functions - copied exactly from RAG.py"""

import re
import tiktoken
from .config import OVERLAP_TOKENS

# OpenAI tokenizer (for text-embedding-3-small)
enc = tiktoken.get_encoding("cl100k_base")

diagram_pattern = re.compile(r"Diagram\s+\d+\.\d+", re.IGNORECASE)


def count_tokens(text: str) -> int:
    return len(enc.encode(text))


def find_diagram_ids(text: str):
    return sorted(set(diagram_pattern.findall(text)))


def apply_overlap(prev_text: str):
    tokens = enc.encode(prev_text)
    if len(tokens) <= OVERLAP_TOKENS:
        return [], 0

    overlap_tokens = tokens[-OVERLAP_TOKENS:]
    overlap_text = enc.decode(overlap_tokens)

    return [overlap_text], len(overlap_tokens)


def context_is_relevant(query: str, context: str) -> bool:
    """
    Very strong hallucination prevention:
    If context does not contain concepts from the query,
    we should not answer at all.
    """

    q_words = set(query.lower().split())
    c_words = set(context.lower().split())

    overlap = q_words.intersection(c_words)
    return len(overlap) > 0
