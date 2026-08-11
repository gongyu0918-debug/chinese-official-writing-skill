from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "maintenance" / "tools" / "build_skillhub_package.py"
SPEC = importlib.util.spec_from_file_location("build_skillhub_package", MODULE_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
RC_VERSION = "1.6.1"


class SkillHubPackageBuilderTests(unittest.TestCase):
    def test_builds_minimal_tracked_package_without_repository_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "publish-package"
            result = BUILDER.build_package(output, version=RC_VERSION)

            self.assertEqual(result["files"], 46)
            self.assertEqual(result["license"], "LICENSE.md")
            self.assertFalse((output / "LICENSE").exists())
            self.assertEqual((output / "LICENSE.md").read_bytes(), (ROOT / "LICENSE").read_bytes())
            self.assertTrue((output / "LICENSE.md").read_text(encoding="utf-8").startswith("MIT License\n"))
            self.assertFalse((output / "agents" / "openai.yaml").exists())
            self.assertTrue((output / "hooks" / "AGENT_GLUE.md").is_file())
            self.assertTrue((output / "hooks" / "host-capabilities.json").is_file())
            self.assertTrue((output / "hooks" / "claude-code" / "hooks" / "hooks.json").is_file())
            self.assertTrue((output / ".codex-plugin" / "plugin.json").is_file())
            self.assertTrue((output / ".codebuddy-plugin" / "plugin.json").is_file())
            self.assertTrue((output / "hooks" / "hooks.json").is_file())
            self.assertTrue((output / "hooks" / "workbuddy" / "hooks.json").is_file())
            self.assertTrue((output / "hooks" / "host_gate_adapter.py").is_file())
            self.assertTrue((output / "skills" / "chinese-official-writing" / "SKILL.md").is_file())
            capabilities = json.loads(
                (output / "hooks" / "host-capabilities.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                "companion_present_inactive",
                capabilities["hosts"]["codex"]["package_presence"]["skillhub_ordinary_package"],
            )
            self.assertEqual(
                "package_present",
                capabilities["hosts"]["claude_code"]["package_presence"],
            )
            self.assertEqual(
                "companion_present_inactive",
                capabilities["hosts"]["workbuddy"]["package_presence"],
            )
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
