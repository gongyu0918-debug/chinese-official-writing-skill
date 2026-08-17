from __future__ import annotations

import json
from pathlib import Path
import re
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
HOOK_ROOT = SKILL_ROOT / "hooks"


class HookLayerContractTests(unittest.TestCase):
    def test_gate_spec_is_hook_only_and_semantically_routed(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        guide = (HOOK_ROOT / "README.md").read_text(encoding="utf-8")
        gate_spec = (SKILL_ROOT / "references/delivery-review-gate.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("delivery-review-gate.md", skill)
        self.assertIn("明确要求处理交付门禁 Hook", skill)
        self.assertIn("普通起草、改稿、压缩和复核不加载该页", skill)
        self.assertIn("完整初稿形成后增加一次有界交付检查", guide)
        self.assertIn("优先交付原始完整稿", guide)
        self.assertIn("普通 `SKILL.md` 不加载本页", gate_spec)
        self.assertIn("Hook 默认禁用", gate_spec)

    def test_product_manual_is_user_facing_and_discloses_consent_boundaries(self) -> None:
        guide = (HOOK_ROOT / "README.md").read_text(encoding="utf-8")
        for required in (
            "下载、安装或调用普通 Skill 不会自动启用 Hook",
            "不自动识别宿主",
            "不安装插件",
            "不修改配置",
            "不主动联网",
            "组装、安装、启用和宿主信任确认分开进行",
            "本次关闭 Hook",
            "完全关闭后",
            "永久移除包内 Hook",
            "通过本页语义说明永久移除",
            "等待用户再次确认",
            "通常比普通 Skill 慢",
        ):
            self.assertIn(required, guide)
        for internal in (
            "maintenance/tools",
            "tests/",
            "evidence",
            "未进入 v1.6.2",
            "本版本不包含",
            "候选未合入",
        ):
            self.assertNotIn(internal, guide)

    def test_static_adapter_sources_are_minimal_and_reachable(self) -> None:
        adapters = HOOK_ROOT / "adapters"
        expected = {
            "codex": {"README.md", "hooks.json", "manifest.json"},
            "codebuddy": {"README.md", "hooks.json", "manifest.json"},
            "claude-code": {
                "README.md",
                "gate_stop_hook.py",
                "hooks.json",
                "manifest.json",
            },
        }
        self.assertEqual(
            expected,
            {
                host: {path.name for path in (adapters / host).iterdir() if path.is_file()}
                for host in expected
            },
        )
        self.assertTrue((adapters / "host_gate_adapter.py").is_file())
        self.assertTrue((HOOK_ROOT / "core/gate_stop_hook.py").is_file())
        guide = (HOOK_ROOT / "README.md").read_text(encoding="utf-8")
        for host in expected:
            self.assertIn(f"adapters/{host}/README.md", guide)

    def test_maintenance_assembler_produces_three_self_contained_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for host in ("codex", "codebuddy", "claude-code"):
                with self.subTest(host=host):
                    output = root / host
                    result = ASSEMBLER.assemble(host, output)
                    self.assertEqual("delivery_review", result["capability"])
                    self.assertFalse(result["installed"])
                    self.assertFalse(result["enabled"])
                    self.assertFalse(result["network_used"])
                    manifests = sorted(
                        path.relative_to(output).as_posix()
                        for path in output.rglob("plugin.json")
                    )
                    expected_manifest = {
                        "codex": [".codex-plugin/plugin.json"],
                        "codebuddy": [".codebuddy-plugin/plugin.json"],
                        "claude-code": [".claude-plugin/plugin.json"],
                    }[host]
                    self.assertEqual(expected_manifest, manifests)
                    packaged = output / "skills/chinese-official-writing"
                    self.assertTrue((packaged / "SKILL.md").is_file())
                    self.assertTrue((packaged / "hooks/gate_stop_hook.py").is_file())
                    self.assertTrue((packaged / "scripts/review_gate.py").is_file())
                    self.assertTrue((packaged / "hooks/capabilities/protective_expansion/runtime.py").is_file())
                    self.assertTrue((packaged / "hooks/capabilities/over_length/runtime.py").is_file())
                    self.assertTrue((packaged / "hooks/capabilities/delivery_cleanliness/runtime.py").is_file())
                    self.assertEqual(
                        "delivery_review",
                        json.loads((output / "hook-capability.json").read_text(encoding="utf-8"))["capability"],
                    )
                    self.assertFalse((packaged / "hooks/adapters").exists())
                    self.assertFalse((packaged / "hooks/core").exists())
                    guide = packaged / "hooks/README.md"
                    self.assertIn("宿主启用说明见插件根 `README.md`", guide.read_text(encoding="utf-8"))
                    for path in output.rglob("*"):
                        if path.is_file():
                            self.assertNotIn(
                                "../", path.read_text(encoding="utf-8", errors="ignore")
                            )
                        if path.is_file() and path.suffix.lower() == ".md":
                            for target in re.findall(
                                r"\[[^\]]+\]\(([^)]+)\)",
                                path.read_text(encoding="utf-8"),
                            ):
                                target = target.split("#", 1)[0].strip()
                                if not target or target.startswith(("https://", "http://", "mailto:")):
                                    continue
                                self.assertTrue((path.parent / target).resolve().exists(), f"{path} -> {target}")

    def test_capabilities_describe_static_opt_in_adapters(self) -> None:
        capabilities = json.loads(
            (HOOK_ROOT / "host-capabilities.json").read_text(encoding="utf-8")
        )
        activation = capabilities["activation"]
        self.assertEqual(10, capabilities["schema_version"])
        self.assertFalse(activation["ordinary_skill_install_enables_hooks"])
        self.assertFalse(activation["runtime_host_detection"])
        self.assertFalse(activation["automatic_file_generation"])
        self.assertFalse(activation["automatic_installation"])
        self.assertFalse(activation["network_access"])
        self.assertTrue(activation["task_opt_out_supported"])
        self.assertEqual("candidate", capabilities["length_gate"]["status"])
        self.assertFalse(capabilities["length_gate"]["automatic_compression"])
        self.assertEqual("candidate", capabilities["over_length_gate"]["status"])
        self.assertTrue(capabilities["over_length_gate"]["automatic_compression"])
        self.assertFalse(capabilities["over_length_gate"]["default_selected"])
        self.assertEqual(2, capabilities["over_length_gate"]["compression_limit"])
        for host in ("codex", "codebuddy", "claude_code"):
            self.assertEqual(
                7, capabilities["hosts"][host]["over_length_continuation_limit"]
            )
        self.assertFalse(capabilities["protective_expansion_gate"]["default_selected"])
        self.assertEqual(
            "available_opt_in",
            capabilities["protective_expansion_gate"]["status"],
        )
        self.assertEqual("candidate", capabilities["delivery_cleanliness_gate"]["status"])
        self.assertFalse(capabilities["delivery_cleanliness_gate"]["default_selected"])
        self.assertEqual("candidate", capabilities["repetition_cleanup_gate"]["status"])
        self.assertFalse(capabilities["repetition_cleanup_gate"]["default_selected"])
        for host in ("codex", "codebuddy", "claude_code"):
            self.assertIn("adapter_source", capabilities["hosts"][host])

    def test_plain_skill_packages_remain_hook_free_and_keep_lint(self) -> None:
        for packaged_skill in (
            ROOT / "packages/agent-skills/skills/chinese-official-writing",
            ROOT / "packages/qwen-code/skills/chinese-official-writing",
            ROOT / "packages/hermes/skills/chinese-official-writing",
            ROOT / "packages/openclaw/skills/chinese_official_writing",
        ):
            with self.subTest(packaged_skill=packaged_skill):
                self.assertFalse((packaged_skill / "hooks").exists())
                self.assertFalse((packaged_skill / "scripts/review_gate.py").exists())
                self.assertFalse(
                    (packaged_skill / "references/delivery-review-gate.md").exists()
                )
                self.assertTrue((packaged_skill / "scripts/prose_lint.py").is_file())
                self.assertNotIn(
                    "读取 `hooks/README.md`",
                    (packaged_skill / "SKILL.md").read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
