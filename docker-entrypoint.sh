#!/bin/bash
set -e

echo "=== Starting RAG Application ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo ""
echo "=== Checking OPENAI_API_KEY ==="
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "ERROR: OPENAI_API_KEY is not set!"
  echo "Please configure the secret in App Runner."
  exit 1
else
  echo "OPENAI_API_KEY is set (length: ${#OPENAI_API_KEY})"
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

