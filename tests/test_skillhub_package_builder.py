from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "build_skillhub_package.py"
SPEC = importlib.util.spec_from_file_location("build_skillhub_package", MODULE_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class SkillHubPackageBuilderTests(unittest.TestCase):
    def test_builds_minimal_tracked_package_without_repository_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "publish-package"
            result = BUILDER.build_package(output, version="1.6.2")

            self.assertEqual(result["files"], 39)
            self.assertFalse((output / "LICENSE").exists())
            self.assertFalse((output / "agents" / "openai.yaml").exists())
            self.assertEqual(
                (output / "_meta.json").read_text(encoding="utf-8"),
                '{\n  "slug": "chinese-official-writing",\n  "version": "1.6.2"\n}\n',
            )

            packaged = (output / "SKILL.md").read_text(encoding="utf-8")
            canonical = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = yaml.safe_load(packaged.split("---", 2)[1])
            self.assertEqual(
                set(frontmatter),
                {"slug", "version", "displayName", "summary", "tags", "name", "description"},
            )
            self.assertEqual(frontmatter["version"], "1.6.2")
            self.assertEqual(
                frontmatter["tags"],
                ["chinese", "official-document", "writing", "gongwen", "ai-compute"],
            )
            for forbidden in ["homepage", "license", "metadata", "compatible_agents", "qwen_code", "openclaw", "hermes"]:
                self.assertNotIn(forbidden, frontmatter)
            self.assertNotIn("github.com", packaged.lower())
            self.assertEqual(packaged.split("---", 2)[2].strip(), canonical.split("---", 2)[2].strip())

    def test_refuses_to_overwrite_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "publish-package"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                BUILDER.build_package(output, version="1.6.2")

    def test_rejects_invalid_release_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                BUILDER.build_package(root / "bad-version", version="v1.6.2")
            with self.assertRaises(ValueError):
                BUILDER.build_package(root / "bad-slug", version="1.6.2", slug="Bad_Slug")


if __name__ == "__main__":
    unittest.main()
