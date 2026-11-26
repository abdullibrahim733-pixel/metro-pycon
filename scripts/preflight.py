"""Facilitator pre-flight: verify the whole METRO demo works offline.

Run from anywhere with the project environment active:
    python scripts/preflight.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_QUESTIONS = {
    "Give me a summary of this sample.": "summary",
    "Show the failed payments.": "failed",
    "Find repeated transaction IDs.": "duplicates",
    "Which amounts should be reviewed?": "large",
    "Give me the full transaction review.": "all",
}


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(label: str, ok: bool, detail: str = "") -> None:
        results.append((label, bool(ok), detail))

    check("Python 3.10 or newer", sys.version_info >= (3, 10), sys.version.split()[0])

    for package in ("langgraph", "openai", "dotenv"):
        try:
            __import__(package)
            check(f"Package: {package}", True)
        except ImportError as exc:
            check(f"Package: {package}", False, str(exc))

    if any(not ok for _, ok, _ in results):
        print("\nInstall dependencies first: python -m pip install -r requirements.txt")
        _report(results)
        return 1

    sys.path.insert(0, str(ROOT))
    try:
        import metro
    except Exception as exc:  # pragma: no cover - setup failure path
        check("Import metro.py", False, str(exc))
        _report(results)
        return 1
    check("Import metro.py", True)

    check("transactions.csv present", metro.DATA_FILE.exists(), str(metro.DATA_FILE))
    if metro.DATA_FILE.exists():
        rows = metro.read_transactions()
        unique, repeated = metro.unique_rows_and_duplicates(rows)
        successful = [r for r in unique if r.get("status") == "SUCCESS"]
        check("7 raw rows", len(rows) == 7, f"got {len(rows)}")
        check("6 unique IDs", len(unique) == 6, f"got {len(unique)}")
        check("TX003 repeated", repeated == ["TX003"], f"got {repeated}")
        check("4 successful", len(successful) == 4, f"got {len(successful)}")
        check(
            "TZS 580,000 successful total",
            sum(metro.amount(r) for r in successful) == 580_000,
            f"got {sum(metro.amount(r) for r in successful)}",
        )

    check(".env present", (ROOT / ".env").exists(), "copy .env.example if missing")

    metro.client = None  # force deterministic local path
    app = metro.build_graph()
    check("LangGraph compiles", app is not None)
    for question, intent in SAMPLE_QUESTIONS.items():
        try:
            result = app.invoke({"question": question})
            ok = result.get("intent") == intent and bool(result.get("answer"))
            check(f"Route: {intent}", ok, f"question: {question!r}")
        except Exception as exc:
            check(f"Route: {intent}", False, str(exc))

    return 1 if _report(results) else 0


def _report(results: list[tuple[str, bool, str]]) -> int:
    print("METRO pre-flight check")
    print("-" * 60)
    failed = 0
    for label, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  ({detail})" if detail else ""))
        failed += 0 if ok else 1
    print("-" * 60)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
