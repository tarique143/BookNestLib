#!/bin/bash

echo "📦 Installing dependencies from requirements.txt"
pip install -r library_backend/requirements.txt

echo "📁 Moving to backend folder"
cd library_backend

echo "🗃️ Running alembic..."
alembic stamp head
