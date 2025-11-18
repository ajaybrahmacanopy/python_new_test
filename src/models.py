"""Pydantic models - copied exactly from RAG.py"""

from pydantic import BaseModel, Field
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


class PassageScore(BaseModel):
    id: int = Field(..., description="Index of the passage")
    score: float = Field(..., description="Relevance score 0–1")


class RerankResult(BaseModel):
    results: List[PassageScore]
