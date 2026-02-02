#!/usr/bin/env bash
set -e
source .venv/bin/activate
export FLASK_ENV=development
python main.py
