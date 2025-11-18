# Source Code Structure

This folder contains the RAG system code organized into modules. **All functions are copied exactly from RAG.py without modifications.**

## Files

- **config.py** - Configuration settings (PDF paths, API keys, constants)
- **models.py** - Pydantic models (AnswerResponse, AnswerContent, Media)
- **utils.py** - Utility functions (count_tokens, find_diagram_ids, context_is_relevant, apply_overlap)
- **pdf_processor.py** - PDF processing (extract images, tables, text chunking)
- **embeddings.py** - FAISS operations (build_and_save_index, search, embed_texts)
- **retriever.py** - Retrieval and reranking (rerank, retrieve_with_reranking)
- **generator.py** - Answer generation (generate_structured_answer, validate_answer_against_context)
- ****init**.py** - Package exports

## Usage

```python
from src import (
    build_and_save_index,
    search,
    retrieve_with_reranking,
    generate_structured_answer
)

# Build index (first time only)
build_and_save_index()

# Query
q = "Your question here"
context, pages, media_files = retrieve_with_reranking(q)
result = generate_structured_answer(q, context, pages, media_files)
```

## Note

All function implementations are **exact copies** from RAG.py. Only the organization has changed.
