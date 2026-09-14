from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
SCRIPT_NAMES = ("draft_length.py", "prose_lint.py")
REMOVED_GATE_PATHS = (
    "hooks",
    "scripts/review_gate.py",
    "references/delivery-review-gate.md",
)


class MitScriptBoundaryTests(unittest.TestCase):
    def test_plain_skill_packages_remain_hook_free_and_keep_scripts(self) -> None:
        surfaces = (
            SKILL_ROOT,
            ROOT / "packages/agent-skills/skills/chinese-official-writing",
            ROOT / "packages/qwen-code/skills/chinese-official-writing",
            ROOT / "packages/qwenwork/skills/chinese-official-writing",
            ROOT / "packages/hermes/skills/chinese-official-writing",
            ROOT / "packages/openclaw/skills/chinese_official_writing",
        )
        for surface in surfaces:
            with self.subTest(surface=surface):
                for relative in REMOVED_GATE_PATHS:
                    self.assertFalse((surface / relative).exists(), relative)
                for script in SCRIPT_NAMES:
                    self.assertTrue((surface / "scripts" / script).is_file(), script)
                self.assertNotIn(
                    "hooks/README.md", (surface / "SKILL.md").read_text(encoding="utf-8")
                )

    def test_drafting_routes_keep_references_without_gate_commands(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        information = (SKILL_ROOT / "references/writing-rules.md").read_text(
            encoding="utf-8"
        )
        for instruction in (
            "hooks/",
            "delivery-review-gate.md",
            "⟦OWG-DROP⟧",
            "scripts/review_gate.py",
        ):
            self.assertNotIn(instruction, skill)
            self.assertNotIn(instruction, information)

    def test_both_standalone_script_routes_are_present(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/writing-rules.md", skill)
        common = (SKILL_ROOT / "references/writing-rules.md").read_text(encoding="utf-8")
        self.assertIn("scripts/draft_length.py", common)
        self.assertIn("prose-lint-usage.md", common)
        usage = (SKILL_ROOT / "references/prose-lint-usage.md").read_text(encoding="utf-8")
        self.assertIn("scripts/prose_lint.py", usage)

    def test_plain_script_clis_run_without_hooks(self) -> None:
        for script in SCRIPT_NAMES:
            with self.subTest(script=script):
                completed = subprocess.run(
                    [sys.executable, "-B", str(SKILL_ROOT / "scripts" / script), "--help"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=30,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                if script == "prose_lint.py":
                    options = ("--json", "--format", "--structure", "--strict")
                    for length_option in ("--min-chars", "--max-chars", "--count-mode"):
                        self.assertNotIn(length_option, completed.stdout)
                else:
                    options = ("--min-chars", "--max-chars", "--count-mode", "--json")
                for option in options:
                    self.assertIn(option, completed.stdout)


if __name__ == "__main__":
    unittest.main()
