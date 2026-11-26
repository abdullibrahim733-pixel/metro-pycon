"""Optional CrewAI warm-up: two roles, sequential review.

Install first (not part of METRO's core dependencies):
    python -m pip install "crewai[openai]"
Then run:
    python warmups/crewai_warmup.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

try:
    from crewai import Agent, Task, Crew, Process, LLM
except ImportError:
    print('CrewAI is optional. Install it with: python -m pip install "crewai[openai]"')
    raise SystemExit(1)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key or "PASTE-YOUR" in api_key:
    print("Set your own OPENROUTER_API_KEY in .env first (see .env.example).")
    raise SystemExit(1)

llm = LLM(
    model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    custom_openai=True,
    temperature=0,
)
analyst = Agent(
    role="Transaction Analyst",
    goal="Summarise provided sample findings accurately.",
    llm=llm,
)
reviewer = Agent(
    role="Controls Reviewer",
    goal="Check flags and request human review where needed.",
    llm=llm,
)
t1 = Task(
    description="Summarise these supplied synthetic figures: 7 rows, 6 unique IDs, "
    "4 successful, 2 failed, TZS 580,000 successful total, TX003 repeated, TX005 large.",
    expected_output="A factual short summary.",
    agent=analyst,
)
t2 = Task(
    description="Review the summary. Never call a flag fraud.",
    expected_output="Review notes for a human.",
    agent=reviewer,
    context=[t1],
)
crew = Crew(agents=[analyst, reviewer], tasks=[t1, t2], process=Process.sequential)
print(crew.kickoff())
