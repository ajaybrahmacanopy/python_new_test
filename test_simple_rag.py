#!/usr/bin/env python
"""
Example script demonstrating the SimpleRAG class
"""

import json
import logging
from src.simple_rag import SimpleRAG

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    # Initialize SimpleRAG with default settings
    rag = SimpleRAG(top_k=5, candidate_k=25)

    # Ask a question
    query = "What are the escape requirements for flats over 4.5m?"

    print(f"Query: {query}\n")
    print("Generating answer...\n")

    # Get structured answer
    result = rag.answer(query)

    # Display results
    print(json.dumps(result.model_dump(), indent=2))
