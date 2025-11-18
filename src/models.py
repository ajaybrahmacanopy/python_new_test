"""Pydantic models - copied exactly from RAG.py"""

from pydantic import BaseModel
from typing import List


class AnswerContent(BaseModel):
    title: str
    summary: str
    steps: List[str]
    verification: List[str]


class Media(BaseModel):
    images: List[str]


class AnswerResponse(BaseModel):
    mode: str = "answer"
    answer: AnswerContent
    links: List[str]
    media: Media
    latency_ms: int = 0
