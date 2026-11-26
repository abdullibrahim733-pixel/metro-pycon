"""Deterministic tests for METRO - no API key or internet required.

Run from the project folder:
    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import metro  # noqa: E402


class MetroTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.object(metro, "client", None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_dataset_matches_teaching_expectations(self) -> None:
        rows = metro.read_transactions()
        unique, repeated = metro.unique_rows_and_duplicates(rows)
        self.assertEqual(len(rows), 7)
        self.assertEqual(len(unique), 6)
        self.assertEqual(repeated, ["TX003"])

        successful = [r for r in unique if r.get("status") == "SUCCESS"]
        failed = [r for r in unique if r.get("status") == "FAILED"]
        self.assertEqual(len(successful), 4)
        self.assertEqual(len(failed), 2)
        self.assertEqual(sum(metro.amount(r) for r in successful), 580_000)

    def test_analysis_modes_return_only_the_requested_sections(self) -> None:
        expected = {
            "summary": {"summary"},
            "failed": {"summary", "failed_transactions"},
            "duplicates": {"summary", "possible_duplicate_ids"},
            "large": {"summary", "large_amounts_for_review"},
            "all": {
                "summary",
                "failed_transactions",
                "possible_duplicate_ids",
                "large_amounts_for_review",
            },
        }
        for mode, keys in expected.items():
            with self.subTest(mode=mode):
                self.assertEqual(set(metro.analyse(mode)), keys)

    def test_failed_duplicate_and_large_items_are_correct(self) -> None:
        all_findings = metro.analyse("all")
        self.assertEqual(
            [item["transaction_id"] for item in all_findings["failed_transactions"]],
            ["TX004", "TX006"],
        )
        self.assertEqual(all_findings["possible_duplicate_ids"], ["TX003"])
        self.assertEqual(
            [item["transaction_id"] for item in all_findings["large_amounts_for_review"]],
            ["TX005"],
        )

    def test_simple_intent_fallback(self) -> None:
        cases = {
            "Find repeated transaction IDs.": "duplicates",
            "Show the failed payments.": "failed",
            "Which amounts should be reviewed?": "large",
            "Give me a summary of this sample.": "summary",
            "Give me the full transaction review.": "all",
            "Something unexpected": "all",
        }
        for question, intent in cases.items():
            with self.subTest(question=question):
                self.assertEqual(metro.simple_intent(question), intent)

    def test_graph_routes_all_five_sample_questions(self) -> None:
        cases = {
            "Give me a summary of this sample.": "summary",
            "Show the failed payments.": "failed",
            "Find repeated transaction IDs.": "duplicates",
            "Which amounts should be reviewed?": "large",
            "Give me the full transaction review.": "all",
        }
        app = metro.build_graph()
        for question, intent in cases.items():
            with self.subTest(question=question):
                result = app.invoke({"question": question})
                self.assertEqual(result["intent"], intent)
                self.assertTrue(result["answer"])

    def test_offline_explanation_contains_key_facts(self) -> None:
        answer = metro.offline_explanation(metro.analyse("all"))
        for fact in ("TZS 580,000", "TX003", "TX005", "review signal"):
            with self.subTest(fact=fact):
                self.assertIn(fact, answer)

    def test_threshold_change_is_applied(self) -> None:
        with mock.patch.object(metro, "HIGH_VALUE_THRESHOLD_TZS", 600_000):
            findings = metro.analyse("large")
        self.assertEqual(findings["summary"]["threshold_tzs"], 600_000)
        self.assertEqual(findings["large_amounts_for_review"], [])

    def test_model_label_is_used_when_valid(self) -> None:
        response = mock.Mock()
        response.choices = [mock.Mock(message=mock.Mock(content="`failed`"))]
        with mock.patch.object(metro, "client") as fake_client:
            fake_client.chat.completions.create.return_value = response
            intent = metro.understand({"question": "anything"})
        self.assertEqual(intent["intent"], "failed")

    def test_unknown_model_label_falls_back_to_simple_intent(self) -> None:
        response = mock.Mock()
        response.choices = [mock.Mock(message=mock.Mock(content="fraud"))]
        with mock.patch.object(metro, "client") as fake_client:
            fake_client.chat.completions.create.return_value = response
            intent = metro.understand({"question": "Show the failed payments."})
        self.assertEqual(intent["intent"], "failed")


if __name__ == "__main__":
    unittest.main()
