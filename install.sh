#!/bin/bash

# Ensure terminal stops if an internal item errors out
set -e

echo "🚀 Verifying and installing system environment dependencies..."
pip install requests --quiet

echo "📥 Syncing local workspace deployment script..."
curl -sSL [https://raw.githubusercontent.com/akhilreddy59/ollama-file-editor/main/ollama-file-editor.py](https://raw.githubusercontent.com/akhilreddy59/ollama-file-editor/main/ollama-file-editor.py) -o ollama-editor.py

echo "✅ Engine Ready! Activating execution setup..."
python3 ollama-editor.py