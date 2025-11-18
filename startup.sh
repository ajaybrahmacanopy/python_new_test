#!/bin/bash
set -e

echo "🚀 Starting RAG API initialization..."

# Check if index exists
if [ ! -f "data/fire_safety.index" ] || [ ! -f "data/fire_safety_metadata.pkl" ]; then
    echo "📦 Index not found. Building FAISS index..."
    python main.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build index"
        exit 1
    fi
    echo "✅ Index built successfully"
else
    echo "✅ Index already exists"
fi

# Check if critical images exist (check first 5 pages as a sample)
MISSING_IMAGES=0
for i in 1 2 3 4 5; do
    if [ ! -f "static/media/page_${i}.png" ]; then
        MISSING_IMAGES=$((MISSING_IMAGES + 1))
    fi
done

if [ $MISSING_IMAGES -gt 0 ]; then
    echo "📸 Some images missing. Running image generation..."
    python main.py
fi

echo "🎉 Initialization complete. Starting API server..."
exec uvicorn api:app --host 0.0.0.0 --port 8000

