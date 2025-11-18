"""Shared test fixtures and configuration"""

import pytest
import os

# Set environment variables BEFORE any other imports
os.environ["OPENAI_API_KEY"] = "test-openai-key-12345"
os.environ["GROQ_API_KEY"] = "test-groq-key-12345"


def pytest_configure(config):
    """Configure pytest - runs before test collection"""
    # Ensure environment variables are set
    os.environ["OPENAI_API_KEY"] = "test-openai-key-12345"
    os.environ["GROQ_API_KEY"] = "test-groq-key-12345"


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
