#!/bin/bash
 
set -e

echo "Installing dependencies..."
pip install -r library_backend/requirements.txt

cd library_backend
echo "Running alembic stamp..."
alembic stamp head
