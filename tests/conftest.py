"""Shared test fixtures and configuration"""

import pytest
import os


@pytest.fixture
def sample_context():
    """Sample context text for testing"""
    return """
    Fire safety requirements include proper exits, signage, and alarm systems.
    All buildings must comply with Approved Document B regulations.
    """


@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return "What are the fire safety requirements?"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("GROQ_API_KEY", "test-key-456")
