"""METRO: Mobile-money Evaluation & Transaction Review Operator.

Learning demo only. Uses synthetic CSV data and a hosted OpenRouter model.
No payments are sent, changed, approved, or reversed.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import END, START, StateGraph

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DATA_FILE = BASE_DIR / "transactions.csv"
HIGH_VALUE_THRESHOLD_TZS = int(os.getenv("METRO_HIGH_VALUE_TZS", "250000"))
MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
API_KEY = os.getenv("OPENROUTER_API_KEY")
client = (
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )
    if API_KEY
    else None
)

INTENTS = ("summary", "failed", "duplicates", "large", "all")


class MetroState(TypedDict, total=False):
    question: str
    intent: str
    findings: dict
    answer: str


def read_transactions() -> list[dict[str, str]]:
    """Read the teaching dataset beside this Python file."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cannot find {DATA_FILE.name}. Keep it in the same folder as metro.py."
        )
    with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def unique_rows_and_duplicates(rows: list[dict[str, str]]):
    """Keep the first occurrence for demo totals; separately flag repeated IDs."""
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    repeated_ids: list[str] = []
    for row in rows:
        tx_id = row.get("transaction_id", "").strip()
        if tx_id in seen:
            repeated_ids.append(tx_id)
        else:
            seen.add(tx_id)
            unique.append(row)
    return unique, repeated_ids


def amount(row: dict[str, str]) -> int:
    try:
        return int(float(row.get("amount_tzs", "0")))
    except (TypeError, ValueError):
        return 0


def analyse(mode: str) -> dict:
    rows = read_transactions()
    unique, repeated_ids = unique_rows_and_duplicates(rows)
    successful = [r for r in unique if r.get("status", "").upper() == "SUCCESS"]
    failed = [r for r in unique if r.get("status", "").upper() == "FAILED"]
    large = [r for r in unique if amount(r) >= HIGH_VALUE_THRESHOLD_TZS]

    summary = {
        "raw_rows": len(rows),
        "unique_transaction_ids": len(unique),
        "repeated_record_count": len(repeated_ids),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "successful_total_tzs": sum(amount(r) for r in successful),
        "threshold_tzs": HIGH_VALUE_THRESHOLD_TZS,
    }
    failed_items = [
        {
            "transaction_id": r["transaction_id"],
            "amount_tzs": amount(r),
            "channel": r.get("channel", ""),
        }
        for r in failed
    ]
    large_items = [
        {
            "transaction_id": r["transaction_id"],
            "amount_tzs": amount(r),
            "channel": r.get("channel", ""),
        }
        for r in large
    ]
    duplicate_items = sorted(set(repeated_ids))

    if mode == "summary":
        return {"summary": summary}
    if mode == "failed":
        return {"summary": summary, "failed_transactions": failed_items}
    if mode == "duplicates":
        return {"summary": summary, "possible_duplicate_ids": duplicate_items}
    if mode == "large":
        return {"summary": summary, "large_amounts_for_review": large_items}
    return {
        "summary": summary,
        "failed_transactions": failed_items,
        "possible_duplicate_ids": duplicate_items,
        "large_amounts_for_review": large_items,
    }


def simple_intent(question: str) -> str:
    """Offline fallback if the model/API is unavailable."""
    q = question.lower()
    if any(word in q for word in ("duplicate", "repeated", "same id")):
        return "duplicates"
    if any(word in q for word in ("failed", "unsuccessful", "declined")):
        return "failed"
    if any(
        word in q
        for word in (
            "large",
            "high value",
            "high-value",
            "big transaction",
            "which amounts",
            "amounts should be reviewed",
            "review amount",
            "for review",
        )
    ):
        return "large"
    if any(word in q for word in ("summary", "total", "overview", "reconcile")):
        return "summary"
    return "all"


def _model_text(messages: list[dict[str, str]], max_tokens: int, temperature: float) -> str:
    """Return visible model text; reasoning models may need a larger budget.

    Some free OpenRouter models think before answering and can spend the whole
    token budget without emitting text, so retry once with double the budget.
    """
    assert client is not None
    kwargs = {"model": MODEL, "temperature": temperature, "messages": messages}
    text = ""
    for budget in (max_tokens, max_tokens * 2):
        response = client.chat.completions.create(**kwargs, max_tokens=budget)
        raw = response.choices[0].message.content or ""
        text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        text = text.strip()
        if text:
            break
    return text


def understand(state: MetroState) -> dict:
    """Ask the model to select one safe analysis path; fall back locally."""
    question = state.get("question", "")
    if client is None:
        return {"intent": simple_intent(question)}
    try:
        text = _model_text(
            [
                {
                    "role": "system",
                    "content": (
                        "Classify the user's request into exactly one label: "
                        "summary, failed, duplicates, large, all. "
                        "Return only the label. Use all if uncertain."
                    ),
                },
                {"role": "user", "content": question},
            ],
            max_tokens=400,
            temperature=0,
        )
        cleaned = text.lower().replace("`", "").replace(".", "")
        labels = [intent for intent in INTENTS if intent in cleaned]
        return {"intent": labels[0] if len(labels) == 1 else simple_intent(question)}
    except Exception:
        return {"intent": simple_intent(question)}


def make_analysis_node(mode: str):
    def node(_: MetroState) -> dict:
        return {"findings": analyse(mode)}
    return node


def offline_explanation(findings: dict) -> str:
    s = findings["summary"]
    lines = [
        "METRO sample report",
        f"Rows read: {s['raw_rows']} | Unique transaction IDs: {s['unique_transaction_ids']}",
        f"Successful: {s['successful_count']} | Failed: {s['failed_count']}",
        f"Successful total (unique IDs): TZS {s['successful_total_tzs']:,}",
        f"Repeated records to review: {s['repeated_record_count']}",
        f"Large-amount review threshold: TZS {s['threshold_tzs']:,}",
        "A repeated ID or large amount is a review signal, not proof of fraud.",
    ]
    if findings.get("failed_transactions"):
        lines.append(f"Failed records: {findings['failed_transactions']}")
    if findings.get("possible_duplicate_ids"):
        lines.append(f"Possible duplicate IDs: {findings['possible_duplicate_ids']}")
    if findings.get("large_amounts_for_review"):
        lines.append(f"Large amounts: {findings['large_amounts_for_review']}")
    return "\n".join(lines)


def explain(state: MetroState) -> dict:
    findings = state["findings"]
    if client is None:
        return {"answer": offline_explanation(findings)}
    try:
        answer = _model_text(
            [
                {
                    "role": "system",
                    "content": (
                        "You are METRO, a learning-only fintech operations assistant. "
                        "Explain only the supplied computed data. Do not invent facts, "
                        "claim fraud, or recommend moving money. Describe flags as "
                        "items for human review. Keep the answer concise."
                    ),
                },
                {
                    "role": "user",
                    "content": "Question: " + state.get("question", "")
                    + "\nComputed data: " + json.dumps(findings),
                },
            ],
            max_tokens=900,
            temperature=0.2,
        )
        if answer:
            return {"answer": answer}
        return {
            "answer": offline_explanation(findings)
            + "\n\n(Model returned no text; used local explanation.)"
        }
    except Exception:
        return {
            "answer": offline_explanation(findings)
            + "\n\n(API unavailable; used local explanation.)"
        }


def build_graph():
    graph = StateGraph(MetroState)
    graph.add_node("understand", understand)
    for intent in INTENTS:
        graph.add_node(intent, make_analysis_node(intent))
    graph.add_node("explain", explain)

    graph.add_edge(START, "understand")
    graph.add_conditional_edges(
        "understand",
        lambda state: state.get("intent", "all"),
        {intent: intent for intent in INTENTS},
    )
    for intent in INTENTS:
        graph.add_edge(intent, "explain")
    graph.add_edge("explain", END)
    return graph.compile()


def _print_answer(app, question: str) -> None:
    try:
        result = app.invoke({"question": question})
        print("\n" + result.get("answer", "No answer returned.") + "\n")
    except Exception as exc:
        print(f"Could not run the demo: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="METRO - Mobile-money Evaluation & Transaction Review Operator"
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="Ask one question and exit (otherwise start the interactive prompt)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force the deterministic local report even if an API key is configured",
    )
    args = parser.parse_args()

    global client
    if args.offline:
        client = None

    print("METRO - Mobile-money Evaluation & Transaction Review Operator")
    print("Learning demo: synthetic records only. Type 'quit' to exit.\n")
    app = build_graph()

    if args.question:
        _print_answer(app, " ".join(args.question))
        return

    while True:
        try:
            question = input("Ask METRO > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        _print_answer(app, question)


if __name__ == "__main__":
    main()
