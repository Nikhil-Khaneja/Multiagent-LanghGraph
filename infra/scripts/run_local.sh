#!/bin/bash
# Local development startup script
set -e

echo "🚀 Starting Multi-Agent LLM Backend..."

# Ensure data dir exists
mkdir -p data

# Check for .env
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Copying .env.example to .env..."
    cp .env.example .env
fi

# Run uvicorn
echo "📡 Starting FastAPI server..."
python -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
