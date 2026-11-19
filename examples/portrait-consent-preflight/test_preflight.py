"""Tests for the local portrait-consent preflight."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import preflight  # noqa: E402


def all_true() -> dict[str, bool]:
    return {item["id"]: True for item in preflight.CHECKS}


class EvaluateTests(unittest.TestCase):
    def test_all_acknowledged_is_a_local_record_only(self) -> None:
        result = preflight.evaluate(all_true())
        self.assertTrue(result.ready)
        self.assertEqual(result.blocking, ())

    def test_missing_answers_are_rejected(self) -> None:
        with self.assertRaises(preflight.AnswerError):
            preflight.evaluate({})

    def test_false_answer_blocks_that_check(self) -> None:
        answers = all_true()
        answers["no_minor"] = False
        result = preflight.evaluate(answers)
        self.assertFalse(result.ready)
        self.assertEqual(
            [item.id for item in result.blocking],
            ["no_minor"],
        )

    def test_non_boolean_is_rejected(self) -> None:
        answers: dict[str, object] = all_true()
        answers["adult_operator"] = "yes"
        with self.assertRaises(preflight.AnswerError):
            preflight.evaluate(answers)

    def test_unknown_id_is_rejected(self) -> None:
        answers: dict[str, object] = all_true()
        answers["upload_to_api"] = True
        with self.assertRaises(preflight.AnswerError):
            preflight.evaluate(answers)

    def test_sample_file_is_not_ready(self) -> None:
        answers = preflight.load_answers(ROOT / "unchecked-answers.json")
        result = preflight.evaluate(answers)
        self.assertFalse(result.ready)
        self.assertEqual(len(result.blocking), len(preflight.CHECKS))

    def test_cli_sample_exits_one(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "preflight.py"), str(ROOT / "unchecked-answers.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("Result: not ready", completed.stdout)
        self.assertIn("no_minor", completed.stdout)

    def test_cli_ready_file_exits_zero_without_claiming_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "answers.json"
            path.write_text(json.dumps(all_true()), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROOT / "preflight.py"), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Result: ready as a local record", completed.stdout)
        self.assertIn("not approval", completed.stdout)

    def test_cli_invalid_json_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "answers.json"
            path.write_text("{", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROOT / "preflight.py"), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("not valid JSON", completed.stderr)


if __name__ == "__main__":
    unittest.main()
