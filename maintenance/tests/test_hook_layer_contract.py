from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
PLUGIN_ROOTS = {
    "codex": SKILL_ROOT / "plugins" / "codex",
    "codebuddy": SKILL_ROOT / "plugins" / "codebuddy",
    "claude-code": SKILL_ROOT / "plugins" / "claude-code",
}


class HookLayerContractTests(unittest.TestCase):
    def test_plugins_readme_explains_required_nested_skill_copy(self) -> None:
        readme = (SKILL_ROOT / "plugins" / "README.md").read_text(encoding="utf-8")
        self.assertIn("宿主发现规范要求的入口", readme)
        self.assertIn("不是第二套产品规则", readme)
        self.assertIn("不要直接编辑副本", readme)

    def test_gate_spec_is_hook_only_and_semantically_routed(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        guide = (SKILL_ROOT / "hooks" / "README.md").read_text(encoding="utf-8")
        gate_spec = (
            SKILL_ROOT / "references" / "delivery-review-gate.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("delivery-review-gate.md", skill)
        self.assertIn("明确要求安装、启用、适配或排查交付门禁 Hook", skill)
        self.assertIn("普通起草、改稿、压缩和复核不加载该页", skill)
        self.assertIn("三层边界", guide)
        self.assertIn("逐字回退 D0", guide)
        self.assertIn("当前没有自动补足字数", guide)
        self.assertIn("普通 `SKILL.md` 不加载本页", gate_spec)
        self.assertIn("Hook 默认禁用", gate_spec)

        for packaged_skill in [
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md",
        ]:
            with self.subTest(packaged_skill=packaged_skill):
                self.assertNotIn(
                    "读取 `hooks/README.md`",
                    packaged_skill.read_text(encoding="utf-8"),
                )

    def test_optional_lint_stays_out_of_every_hook_surface(self) -> None:
        guide = (SKILL_ROOT / "hooks" / "README.md").read_text(encoding="utf-8")
        surfaces = {
            "shared bridge": SKILL_ROOT / "hooks" / "gate_stop_hook.py",
            "shared adapter source": SKILL_ROOT / "hooks" / "host_gate_adapter.py",
            "Codex manifest": PLUGIN_ROOTS["codex"] / "hooks" / "hooks.json",
            "CodeBuddy manifest": PLUGIN_ROOTS["codebuddy"] / "hooks" / "hooks.json",
            "Claude manifest": PLUGIN_ROOTS["claude-code"] / "hooks" / "hooks.json",
            "Claude adapter": PLUGIN_ROOTS["claude-code"] / "scripts" / "gate_stop_hook.py",
        }

        self.assertIn("不向 Hook 传递报告", guide)
        self.assertIn("只回退 D0", guide)
        for name, path in surfaces.items():
            with self.subTest(surface=name):
                self.assertNotIn("prose_lint", path.read_text(encoding="utf-8"))

    def test_capabilities_match_three_self_contained_plugins(self) -> None:
        capabilities = json.loads(
            (SKILL_ROOT / "hooks" / "host-capabilities.json").read_text(encoding="utf-8")
        )
        self.assertEqual(4, capabilities["schema_version"])
        self.assertFalse(capabilities["activation"]["ordinary_skill_install_enables_hooks"])
        self.assertEqual("not_shipped", capabilities["length_gate"]["status"])

        for host in ("codex", "codebuddy", "claude-code"):
            with self.subTest(host=host):
                plugin_root = PLUGIN_ROOTS[host]
                manifests = sorted(
                    path.relative_to(plugin_root).as_posix()
                    for path in plugin_root.rglob("plugin.json")
                )
                expected_manifest = {
                    "codex": [".codex-plugin/plugin.json"],
                    "codebuddy": [".codebuddy-plugin/plugin.json"],
                    "claude-code": [".claude-plugin/plugin.json"],
                }[host]
                self.assertEqual(expected_manifest, manifests)
                packaged_skill = plugin_root / "skills" / "chinese-official-writing"
                self.assertTrue((packaged_skill / "SKILL.md").is_file())
                self.assertTrue((packaged_skill / "scripts" / "review_gate.py").is_file())
                self.assertTrue((packaged_skill / "hooks" / "gate_stop_hook.py").is_file())
                self.assertFalse((packaged_skill / "plugins").exists())
                self.assertEqual(
                    host == "codex",
                    (packaged_skill / "agents" / "openai.yaml").is_file(),
                )
                for file in plugin_root.rglob("*"):
                    if file.is_file():
                        self.assertNotIn("../", file.read_text(encoding="utf-8", errors="ignore"))

        self.assertEqual("package_registration_verified", capabilities["hosts"]["codex"]["status"])
        self.assertFalse(capabilities["hosts"]["codex"]["live_lifecycle_verified"])
        self.assertEqual("package_manifest_verified", capabilities["hosts"]["codebuddy"]["status"])
        self.assertFalse(capabilities["hosts"]["codebuddy"]["live_lifecycle_verified"])
        self.assertEqual("lifecycle_verified", capabilities["hosts"]["claude_code"]["status"])
        self.assertEqual("skill_only", capabilities["hosts"]["openclaw"]["status"])


if __name__ == "__main__":
    unittest.main()
