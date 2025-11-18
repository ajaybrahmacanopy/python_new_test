"""Test utility functions"""

import pytest
from src.utils import count_tokens, find_diagram_ids, context_is_relevant


def test_count_tokens():
    """Test token counting"""
    text = "This is a test sentence."
    token_count = count_tokens(text)
    assert token_count > 0
    assert isinstance(token_count, int)


def test_count_tokens_empty():
    """Test token counting with empty string"""
    assert count_tokens("") == 0


def test_find_diagram_ids():
    """Test diagram ID extraction"""
    text = "See Diagram 3.1 and Diagram 4.2 for details"
    diagrams = find_diagram_ids(text)
    assert len(diagrams) == 2
    assert "Diagram 3.1" in diagrams
    assert "Diagram 4.2" in diagrams


def test_find_diagram_ids_no_diagrams():
    """Test with no diagrams"""
    text = "This text has no diagrams"
    diagrams = find_diagram_ids(text)
    assert len(diagrams) == 0


def test_find_diagram_ids_case_insensitive():
    """Test case insensitive diagram detection"""
    text = "See DIAGRAM 1.1 and diagram 2.2"
    diagrams = find_diagram_ids(text)
    assert len(diagrams) == 2


def test_context_is_relevant_true():
    """Test context relevance check - relevant"""
    query = "fire safety requirements"
    context = "The fire safety requirements include proper exits"
    assert context_is_relevant(query, context) is True


def test_context_is_relevant_false():
    """Test context relevance check - not relevant"""
    query = "fire safety requirements"
    context = "The weather today is sunny"
    assert context_is_relevant(query, context) is False


def test_context_is_relevant_partial_overlap():
    """Test context relevance with partial word overlap"""
    query = "building regulations"
    context = "The building must comply"
    assert context_is_relevant(query, context) is True


def test_context_is_relevant_empty():
    """Test context relevance with empty strings"""
    assert context_is_relevant("", "") is False
    assert context_is_relevant("test", "") is False
    assert context_is_relevant("", "test") is False
