#!/bin/bash
set -e

echo "=== Starting RAG Application ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo ""
echo "=== Checking OPENAI_API_KEY ==="
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "WARNING: OPENAI_API_KEY is not set as environment variable."
  echo "The application will attempt to retrieve it from AWS Secrets Manager."
  echo "If this fails, the application will not work correctly."
else
  echo "OPENAI_API_KEY is set as environment variable (length: ${#OPENAI_API_KEY})"
fi

echo ""
echo "=== Checking FAISS index ==="
if [ ! -d "faiss_index" ]; then
  echo "FAISS index not found. Running ingest.py..."
  python ingest.py || {
    echo "ERROR: ingest.py failed!"
    exit 1
  }
  echo "Ingest completed successfully."
else
  echo "FAISS index already exists. Skipping ingest."
fi

echo ""
echo "=== Starting Flask application ==="
exec python app.py

