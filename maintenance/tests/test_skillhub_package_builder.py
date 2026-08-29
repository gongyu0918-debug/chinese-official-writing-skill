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
RC_VERSION = "1.6.20"


class SkillHubPackageBuilderTests(unittest.TestCase):
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
            self.assertTrue((output / "hooks" / "README.md").is_file())
            self.assertTrue((output / "hooks" / "host-capabilities.json").is_file())
            self.assertTrue((output / "hooks" / "core" / "gate_stop_hook.py").is_file())
            self.assertTrue(
                (
                    output
                    / "hooks"
                    / "capabilities"
                    / "protective_expansion"
                    / "runtime.py"
                ).is_file()
            )
            self.assertTrue((output / "hooks" / "adapters" / "host_gate_adapter.py").is_file())
            self.assertFalse((output / ".codex-plugin").exists())
            self.assertFalse((output / ".codebuddy-plugin").exists())
            self.assertFalse((output / "skills").exists())
            self.assertFalse((output / "plugins").exists())
            for host in (
                "codex",
                "codebuddy",
                "claude-code",
                "zcode",
                "qwen-code",
                "kimi-code",
                "opencode",
                "hermes-agent",
                "deepseek-harness",
            ):
                adapter = output / "hooks" / "adapters" / host
                self.assertTrue((adapter / "README.md").is_file())
                self.assertEqual(
                    host not in {"opencode", "hermes-agent", "deepseek-harness"},
                    (adapter / "manifest.json").is_file(),
                )
                self.assertEqual(
                    host == "hermes-agent", (adapter / "plugin.yaml").is_file()
                )
                self.assertEqual(
                    host not in {"kimi-code", "opencode", "hermes-agent", "deepseek-harness"},
                    (adapter / "hooks.json").is_file(),
                )
                self.assertEqual(
                    host == "opencode", (adapter / "opencode_gate_plugin.js").is_file()
                )
                self.assertEqual(
                    host == "hermes-agent", (adapter / "__init__.py").is_file()
                )
                self.assertEqual(
                    host == "deepseek-harness", (adapter / "package.json").is_file()
                )
                self.assertFalse((adapter / "skills").exists())
            self.assertFalse((output / "hooks" / "build_companion.py").exists())
            self.assertFalse((output / "maintenance").exists())
            capabilities = json.loads(
                (output / "hooks" / "host-capabilities.json").read_text(encoding="utf-8")
            )
            self.assertEqual("hooks/adapters/codex", capabilities["hosts"]["codex"]["adapter_source"])
            self.assertEqual("hooks/adapters/codebuddy", capabilities["hosts"]["codebuddy"]["adapter_source"])
            self.assertEqual("hooks/adapters/zcode", capabilities["hosts"]["zcode"]["adapter_source"])
            self.assertEqual("hooks/adapters/qwen-code", capabilities["hosts"]["qwen_code"]["adapter_source"])
            self.assertEqual("hooks/adapters/kimi-code", capabilities["hosts"]["kimi_code_cli"]["adapter_source"])
            self.assertEqual("hooks/adapters/opencode", capabilities["hosts"]["opencode"]["adapter_source"])
            self.assertEqual("hooks/adapters/hermes-agent", capabilities["hosts"]["hermes_agent"]["adapter_source"])
            self.assertEqual("hooks/adapters/deepseek-harness", capabilities["hosts"]["deepseek_harness"]["adapter_source"])
            self.assertEqual(
                "lifecycle_verified_fresh_query_single_pass",
                capabilities["hosts"]["hermes_agent"]["status"],
            )
            self.assertEqual(
                "lifecycle_verified_headless",
                capabilities["hosts"]["deepseek_harness"]["status"],
            )
            self.assertEqual("available_opt_in", capabilities["length_gate"]["status"])
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
