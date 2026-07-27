from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_module(
    "ab_provenance_under_test",
    ROOT / "tools" / "check_ab_provenance.py",
)


def make_receipt(side: str) -> dict:
    root = f"F:/worktrees/{side}"
    return {
        "actual_model": "gpt-test",
        "actual_reasoning_effort": "high",
        "source_commit": f"{side}-commit",
        "host_context_sha256": "host-context",
        f"{side}_root": root,
        "generation_policy": {
            "first_technically_valid_output_only": True,
            "resampling_count": 0,
            "post_generation_revision_count": 0,
        },
        "outputs": [
            {
                "task_id": "T01",
                "task_sha256": "same-task",
                "first_technical_validity": True,
                "generation_attempt": 1,
                "route_files_used": [
                    f"{root}/chinese-official-writing/SKILL.md",
                    f"{root}/chinese-official-writing/references/genre-playbooks.md",
                ],
            }
        ],
    }


class ProvenanceComparabilityTests(unittest.TestCase):
    def test_complete_symmetric_receipts_are_strict_comparable(self) -> None:
        result = checker.assess_pair(
            make_receipt("candidate"),
            make_receipt("baseline"),
        )

        self.assertEqual(result["status"], "strict-comparable")
        self.assertTrue(result["strict_comparable"])
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["task_count"], 1)

    def test_unavailable_runtime_identity_is_exploratory(self) -> None:
        candidate = make_receipt("candidate")
        baseline = make_receipt("baseline")
        candidate["actual_model"] = "unavailable"
        baseline["actual_reasoning_effort"] = "unavailable"

        result = checker.assess_pair(candidate, baseline)
        codes = {item["code"] for item in result["issues"]}

        self.assertEqual(result["status"], "exploratory")
        self.assertIn("actual_model_unavailable", codes)
        self.assertIn("actual_reasoning_effort_unavailable", codes)

    def test_asymmetric_conditions_are_exploratory(self) -> None:
        candidate = make_receipt("candidate")
        baseline = make_receipt("baseline")
        baseline["host_context_sha256"] = "different-host-context"
        baseline["outputs"][0]["task_sha256"] = "different-task"
        candidate["outputs"][0]["route_files_used"] = [
            "F:/worktrees/baseline/chinese-official-writing/SKILL.md"
        ]

        result = checker.assess_pair(candidate, baseline)
        codes = {item["code"] for item in result["issues"]}

        self.assertEqual(result["status"], "exploratory")
        self.assertIn("host_context_sha256_mismatch", codes)
        self.assertIn("task_sha256_mismatch", codes)
        self.assertIn("reference_outside_root", codes)

    def test_different_product_references_remain_strict_comparable(self) -> None:
        candidate = make_receipt("candidate")
        baseline = make_receipt("baseline")
        candidate["outputs"][0]["route_files_used"][1] = (
            "F:/worktrees/candidate/chinese-official-writing/"
            "references/genre-playbook-correspondence.md"
        )

        result = checker.assess_pair(candidate, baseline)

        self.assertEqual(result["status"], "strict-comparable")

    def test_parent_traversal_outside_root_is_exploratory(self) -> None:
        candidate = make_receipt("candidate")
        candidate["outputs"][0]["route_files_used"] = [
            "F:/worktrees/candidate/../baseline/chinese-official-writing/SKILL.md"
        ]

        result = checker.assess_pair(candidate, make_receipt("baseline"))
        codes = {item["code"] for item in result["issues"]}

        self.assertEqual(result["status"], "exploratory")
        self.assertIn("reference_outside_root", codes)

    def test_reused_root_is_exploratory(self) -> None:
        candidate = make_receipt("candidate")
        baseline = make_receipt("baseline")
        baseline["baseline_root"] = candidate["candidate_root"]
        baseline["outputs"][0]["route_files_used"] = [
            "F:/worktrees/candidate/chinese-official-writing/SKILL.md"
        ]

        result = checker.assess_pair(candidate, baseline)
        codes = {item["code"] for item in result["issues"]}

        self.assertEqual(result["status"], "exploratory")
        self.assertIn("root_reused", codes)

    def test_duplicate_task_id_is_exploratory(self) -> None:
        candidate = make_receipt("candidate")
        candidate["outputs"].append(dict(candidate["outputs"][0]))

        result = checker.assess_pair(candidate, make_receipt("baseline"))
        codes = {item["code"] for item in result["issues"]}

        self.assertEqual(result["status"], "exploratory")
        self.assertIn("duplicate_task_id", codes)


if __name__ == "__main__":
    unittest.main()
