.PHONY: help install test lint format clean docker-build docker-run

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code with black"
	@echo "  make clean         - Clean cache and temp files"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo "  make docker-test   - Test Docker image"

install:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ api.py main.py example.py
	black --check src/ api.py main.py example.py

format:
	black src/ api.py main.py example.py tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov .coverage coverage.xml .tox

docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-test:
	docker build -t rag-api:test .
	docker run --rm rag-api:test python -c "import src; print('✅ Import successful')"

all: format lint test

