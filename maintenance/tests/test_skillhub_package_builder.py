from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "maintenance" / "tools" / "build_skillhub_package.py"
SPEC = importlib.util.spec_from_file_location("build_skillhub_package", MODULE_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
RC_VERSION = "1.6.27"


class SkillHubPackageBuilderTests(unittest.TestCase):
    def test_tracked_file_filter_excludes_hooks_and_preserves_plain_scripts(self) -> None:
        plain_files = [
            "SKILL.md",
            "scripts/draft_length.py",
            "scripts/prose_lint.py",
            "scripts/another_check.py",
            "scripts/review_gate_notes.py",
            "references/prose-lint-usage.md",
        ]
        removed_files = [
            "hooks/core/gate_stop_hook.py",
            "hooks/adapters/codex/manifest.json",
            "references/delivery-review-gate.md",
            "scripts/review_gate.py",
            "agents/openai.yaml",
            "LICENSE",
        ]
        tracked_output = "\n".join(
            f"chinese-official-writing/{relative}"
            for relative in plain_files + removed_files
        )
        with mock.patch.object(
            BUILDER.subprocess, "run", return_value=mock.Mock(stdout=tracked_output)
        ):
            self.assertEqual(BUILDER.tracked_canonical_files(), sorted(plain_files))

    def test_builds_minimal_tracked_package_without_repository_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "publish-package"
            result = BUILDER.build_package(output, version=RC_VERSION)

            expected_files = len(BUILDER.tracked_canonical_files()) + 2
            self.assertEqual(result["files"], expected_files)
            self.assertEqual(
                result["files"],
                len([path for path in output.rglob("*") if path.is_file()]),
            )
            self.assertEqual(result["license"], "LICENSE.md")
            self.assertFalse((output / "LICENSE").exists())
            self.assertEqual((output / "LICENSE.md").read_bytes(), (ROOT / "LICENSE").read_bytes())
            self.assertTrue((output / "LICENSE.md").read_text(encoding="utf-8").startswith("MIT License\n"))
            self.assertFalse((output / "agents" / "openai.yaml").exists())
            for relative in ("hooks", "scripts/review_gate.py", "references/delivery-review-gate.md"):
                self.assertFalse((output / relative).exists(), relative)
            for script in (ROOT / "chinese-official-writing" / "scripts").glob("*.py"):
                if script.name != "review_gate.py":
                    self.assertEqual((output / "scripts" / script.name).read_bytes(), script.read_bytes())
            self.assertFalse((output / ".codex-plugin").exists())
            self.assertFalse((output / ".codebuddy-plugin").exists())
            self.assertFalse((output / "skills").exists())
            self.assertFalse((output / "plugins").exists())
            self.assertFalse((output / "maintenance").exists())
            self.assertEqual(
                (output / "_meta.json").read_text(encoding="utf-8"),
                f'{{\n  "slug": "chinese-official-writing",\n  "version": "{RC_VERSION}"\n}}\n',
            )

            packaged = (output / "SKILL.md").read_text(encoding="utf-8")
            canonical = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = yaml.safe_load(packaged.split("---", 2)[1])
            self.assertEqual(
                set(frontmatter),
                {"slug", "version", "displayName", "summary", "tags", "name", "description"},
            )
            self.assertEqual(frontmatter["version"], RC_VERSION)
            self.assertEqual(
                frontmatter["tags"],
                [
                    "office-efficiency",
                    "content-creation",
                    "chinese",
                    "official-document",
                    "writing",
                    "gongwen",
                    "ai-compute",
                ],
            )
            self.assertIn("办公效率", frontmatter["summary"])
            self.assertIn("内容创作", frontmatter["summary"])
            self.assertIn("新闻评论", frontmatter["summary"])
            for forbidden in ["homepage", "license", "metadata", "compatible_agents", "qwen_code", "openclaw", "hermes"]:
                self.assertNotIn(forbidden, frontmatter)
            self.assertNotIn("github.com", packaged.lower())
            self.assertEqual(packaged.split("---", 2)[2].strip(), canonical.split("---", 2)[2].strip())

    def test_refuses_to_overwrite_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "publish-package"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                BUILDER.build_package(output, version=RC_VERSION)

    def test_rejects_invalid_release_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                BUILDER.build_package(root / "bad-version", version=f"v{RC_VERSION}")
            with self.assertRaises(ValueError):
                BUILDER.build_package(root / "bad-slug", version=RC_VERSION, slug="Bad_Slug")


if __name__ == "__main__":
    unittest.main()
