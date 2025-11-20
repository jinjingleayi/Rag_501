#!/bin/bash
# Don't use set -e, we want to handle errors gracefully

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
  echo "FAISS index not found. Attempting to run ingest.py..."
  
  # Only run ingest if we have the API key (either from env or can retrieve from Secrets Manager)
  if [ -n "${OPENAI_API_KEY:-}" ]; then
    echo "OPENAI_API_KEY is available, running ingest.py..."
    if python ingest.py; then
      echo "Ingest completed successfully."
    else
      echo "WARNING: ingest.py failed, but continuing. The app will try to retrieve the key from Secrets Manager."
      echo "If the FAISS index is required, the app may not work correctly."
    fi
  else
    echo "OPENAI_API_KEY not available yet. Skipping ingest for now."
    echo "The app will retrieve the key from Secrets Manager and can create the index if needed."
    echo "Note: For production, ensure the FAISS index is included in the Docker image."
  fi
else
  echo "FAISS index already exists. Skipping ingest."
fi

echo ""
echo "=== Starting Flask application ==="
# Use exec to replace shell with Python process
exec python app.py

