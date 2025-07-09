#!/bin/bash

echo "📦 Installing dependencies from requirements.txt"
pip install -r library_backend/requirements.txt

echo "🔧 Running Alembic..."
cd library_backend
alembic stamp head
