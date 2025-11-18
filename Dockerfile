# Use Python 3.12 slim image for better pre-built wheel support
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY api.py .
COPY main.py .
COPY startup.sh .
COPY content/ ./content/

# Create directories for data and media
RUN mkdir -p data static/media

# Make startup script executable
RUN chmod +x startup.sh

# Expose port
EXPOSE 8000

# Health check (increased start period for index building)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run startup script (builds index if needed, then starts API)
CMD ["./startup.sh"]

