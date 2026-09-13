"""Run the four scoped methods, real CLI capture, and explicit-link helper probes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from maintenance.tests import test_skill_boundary as boundary


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def helper_checks() -> list[dict]:
    checks = []
    cases = [
        ("two-hop", "`references/reference-index.md`", "`compatibility-scene-routing.md`", True, True, None),
        ("missing-home-link", "missing index route", "`compatibility-scene-routing.md`", True, True, AssertionError),
        ("missing-index-link", "`references/reference-index.md`\n`references/compatibility-scene-routing.md`", "no second hop", True, True, AssertionError),
        ("missing-index-file", "`references/reference-index.md`", "unused", False, True, FileNotFoundError),
        ("missing-scene-file", "`references/reference-index.md`", "`compatibility-scene-routing.md`", True, False, FileNotFoundError),
    ]
    for name, home, index, has_index, has_scene, expected_error in cases:
        folder = EVIDENCE / "helper-fixtures" / name
        refs = folder / "references"
        refs.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text(home, encoding="utf-8")
        if has_index:
            (refs / "reference-index.md").write_text(index, encoding="utf-8")
        if has_scene:
            (refs / "compatibility-scene-routing.md").write_text("scene marker", encoding="utf-8")
        # This unrelated page must never rescue a missing direct edge.
        (refs / "unrelated.md").write_text("`references/reference-index.md`\n`compatibility-scene-routing.md`\narbitrary fallback", encoding="utf-8")
        try:
            actual = boundary.read_routing_surfaces(folder / "SKILL.md")
        except Exception as exc:
            assert expected_error is not None and isinstance(exc, expected_error), (name, type(exc).__name__, str(exc))
            checks.append({"case": name, "status": "PASS", "observed": type(exc).__name__, "message": str(exc)})
        else:
            assert expected_error is None, name + ": missing edge/file did not fail"
            assert actual == "\n".join((home, index, "scene marker")), name
            assert "arbitrary fallback" not in actual, name
            checks.append({"case": name, "status": "PASS", "observed": "exact three-surface concatenation"})
    return checks


def main() -> int:
    helper = helper_checks()
    captures = []
    actual_run = boundary.subprocess.run

    def capture_real_run(*args, **kwargs):
        result = actual_run(*args, **kwargs)
        folder = EVIDENCE / "cli-calls" / f"{len(captures) + 1:02d}"
        folder.mkdir(parents=True, exist_ok=True)
        for key, value in (("stdout", result.stdout), ("stderr", result.stderr)):
            (folder / f"{key}.txt").write_text(value or "", encoding="utf-8")
        captures.append({
            "command": args[0], "stdin": kwargs.get("input"), "returncode": result.returncode,
            "stdout": str(folder / "stdout.txt"), "stdout_sha256": digest(folder / "stdout.txt"),
            "stderr": str(folder / "stderr.txt"), "stderr_sha256": digest(folder / "stderr.txt"),
        })
        return result

    names = [
        "test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority",
        "test_review_command_includes_interpreter_and_draft_path",
        "test_openclaw_skill_card_uses_absolute_links_and_key_genres",
        "test_lightened_indices_resolve_from_each_skill_root_and_keep_quality_bridges",
    ]
    suite = unittest.TestSuite(boundary.SkillBoundaryTests(name) for name in names)
    with (EVIDENCE / "focused.log").open("w", encoding="utf-8") as log:
        with mock.patch.object(boundary.subprocess, "run", side_effect=capture_real_run):
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    assert len(captures) == 5, f"expected two counter and three prose-lint real calls, got {len(captures)}"
    assert all(call["returncode"] == 0 for call in captures), "a real CLI call failed"
    payload = {
        "interpreter": sys.executable, "methods": names, "tests_run": result.testsRun,
        "failure_events": len(result.failures), "error_events": len(result.errors),
        "failed_ids": [test.id() for test, _ in result.failures],
        "error_ids": [test.id() for test, _ in result.errors],
        "helper_checks": helper, "actual_cli_calls": captures,
        "module_sha256": digest(ROOT / "maintenance/tests/test_skill_boundary.py"),
        "product_sha256": {name: digest(ROOT / "chinese-official-writing" / name) for name in [
            "SKILL.md", "references/writing-rules.md", "references/compression-details.md",
            "references/prose-lint-usage.md", "scripts/draft_length.py", "scripts/prose_lint.py",
        ]},
    }
    (EVIDENCE / "focused-result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Scoped methods={result.testsRun}; failures={len(result.failures)}; errors={len(result.errors)}; helper probes=5 PASS; real CLI calls=5 completed")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
