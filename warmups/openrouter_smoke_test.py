"""Test the OpenRouter connection with one small chat completion.

Run from the project folder with the virtual environment active:
    python warmups/openrouter_smoke_test.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key or "PASTE-YOUR" in api_key:
    print("Set your own OPENROUTER_API_KEY in .env first (see .env.example).")
    raise SystemExit(1)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
try:
    reply = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        messages=[{"role": "user", "content": "Reply: METRO is connected."}],
        max_tokens=40,
    )
    print(reply.choices[0].message.content)
except Exception as exc:
    print(f"Connection failed: {exc}")
    print("Check the key, model access and rate limits, or use METRO's local fallback.")
    sys.exit(1)
