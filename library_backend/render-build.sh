#!/usr/bin/env bash

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run alembic before the app starts
alembic stamp head
