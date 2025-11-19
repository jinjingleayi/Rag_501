#!/bin/bash
set -euo pipefail

echo "Starting container..."

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "ERROR: OPENAI_API_KEY is not set. Please configure the secret in App Runner."
  exit 1
fi

if [ ! -d "faiss_index" ]; then
  echo "FAISS index not found. Running ingest.py..."
  python ingest.py
else
  echo "FAISS index already exists. Skipping ingest."
fi

exec python app.py

