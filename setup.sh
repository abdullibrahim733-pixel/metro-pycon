#!/usr/bin/env bash
# Linux / macOS: create the virtual environment and install core packages.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python not found. Install Python 3.10+ and try again."
  exit 1
fi

"$PYTHON" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example - add your own OpenRouter key to enable AI responses."
fi

echo "Setup complete. Run: .venv/bin/python scripts/preflight.py"
