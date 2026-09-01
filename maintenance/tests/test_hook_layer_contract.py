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
        self.assertLess(guide.index("## 宿主适配说明"), guide.index("## 永久移除包内 Hook"))
        self.assertLess(guide.index("## Agent 组装清单"), guide.index("## 永久移除包内 Hook"))

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
            "zcode": {"README.md", "hooks.json", "manifest.json"},
            "qwen-code": {
                "README.md",
                "gate_stop_hook.py",
                "hooks.json",
                "manifest.json",
            },
            "kimi-code": {"README.md", "gate_stop_hook.py", "manifest.json"},
            "opencode": {"README.md", "opencode_gate_plugin.js"},
            "hermes-agent": {"README.md", "__init__.py", "plugin.yaml"},
            "deepseek-harness": {
                "README.md",
                "cordis.patch.yml",
                "index.mjs",
                "package.json",
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
            adapter_guide = (adapters / host / "README.md").read_text(
                encoding="utf-8"
            )
            if host == "hermes-agent":
                self.assertIn("`delivery_review`", adapter_guide)
            else:
                self.assertIn("`over_length`", adapter_guide)

    def test_maintenance_assembler_produces_nine_self_contained_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
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
                with self.subTest(host=host):
                    output = root / host
                    result = ASSEMBLER.assemble(host, output)
                    self.assertEqual("delivery_review", result["capability"])
                    self.assertFalse(result["installed"])
                    self.assertFalse(result["enabled"])
                    self.assertFalse(result["network_used"])
                    manifest_names = {
                        "plugin.json",
                        "qwen-extension.json",
                        "kimi.plugin.json",
                        "plugin.yaml",
                        "package.json",
                    }
                    manifests = sorted(
                        path.relative_to(output).as_posix()
                        for path in output.rglob("*")
                        if path.is_file() and path.name in manifest_names
                    )
                    expected_manifest = {
                        "codex": [".codex-plugin/plugin.json"],
                        "codebuddy": [".codebuddy-plugin/plugin.json"],
                        "claude-code": [".claude-plugin/plugin.json"],
                        "zcode": [".zcode-plugin/plugin.json"],
                        "qwen-code": ["qwen-extension.json"],
                        "kimi-code": ["kimi.plugin.json"],
                        "opencode": [],
                        "hermes-agent": ["plugin.yaml"],
                        "deepseek-harness": ["package.json"],
                    }[host]
                    self.assertEqual(expected_manifest, manifests)
                    packaged = output / (
                        ".opencode/skills/chinese-official-writing"
                        if host == "opencode"
                        else "skills/chinese-official-writing"
                    )
                    self.assertTrue((packaged / "SKILL.md").is_file())
                    self.assertTrue((packaged / "hooks/gate_stop_hook.py").is_file())
                    self.assertTrue((packaged / "scripts/review_gate.py").is_file())
                    self.assertTrue((packaged / "hooks/capabilities/protective_expansion/runtime.py").is_file())
                    self.assertTrue((packaged / "hooks/capabilities/over_length/runtime.py").is_file())
                    self.assertTrue((packaged / "hooks/capabilities/delivery_cleanliness/runtime.py").is_file())
                    self.assertTrue((packaged / "hooks/shared/hard_anchors.py").is_file())
                    self.assertTrue((packaged / "hooks/shared/source_bound_dates.py").is_file())
                    self.assertEqual(
                        "delivery_review",
                        json.loads(
                            (
                                output
                                / (
                                    ".opencode/hook-capability.json"
                                    if host == "opencode"
                                    else "hook-capability.json"
                                )
                            ).read_text(encoding="utf-8")
                        )["capability"],
                    )
                    self.assertFalse((packaged / "hooks/adapters").exists())
                    self.assertFalse((packaged / "hooks/core").exists())
                    guide = packaged / "hooks/README.md"
                    guide_text = guide.read_text(encoding="utf-8")
                    self.assertIn("宿主启用说明见插件根 `README.md`", guide_text)
                    self.assertLess(
                        guide_text.index("## Agent 组装清单"),
                        guide_text.index("## 永久移除包内 Hook"),
                    )
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
        self.assertEqual(17, capabilities["schema_version"])
        self.assertFalse(activation["ordinary_skill_install_enables_hooks"])
        self.assertFalse(activation["runtime_host_detection"])
        self.assertFalse(activation["automatic_file_generation"])
        self.assertFalse(activation["automatic_installation"])
        self.assertFalse(activation["network_access"])
        self.assertTrue(activation["task_opt_out_supported"])
        retention = capabilities["data_retention"]
        self.assertEqual(
            "redact_raw_text_and_delete_turn_transaction_files",
            retention["terminal_action"],
        )
        self.assertEqual(
            "hash_count_phase_selection_and_delivery_status_only",
            retention["retained_receipt"],
        )
        self.assertEqual(
            "PLUGIN_DATA/candidate-ai-gate-hook", retention["data_root"]
        )
        self.assertFalse(retention["network_exfiltration"])
        self.assertEqual("available_opt_in", capabilities["length_gate"]["status"])
        self.assertNotIn("known_hold", capabilities["length_gate"])
        self.assertFalse(capabilities["length_gate"]["automatic_compression"])
        self.assertEqual("available_opt_in", capabilities["over_length_gate"]["status"])
        self.assertTrue(capabilities["over_length_gate"]["automatic_compression"])
        self.assertFalse(capabilities["over_length_gate"]["default_selected"])
        self.assertEqual(2, capabilities["over_length_gate"]["compression_limit"])
        for host in (
            "codex",
            "codebuddy",
            "claude_code",
            "zcode",
            "qwen_code",
            "opencode",
            "deepseek_harness",
        ):
            self.assertEqual(
                7, capabilities["hosts"][host]["over_length_continuation_limit"]
            )
        self.assertEqual(
            1,
            capabilities["hosts"]["kimi_code_cli"]["over_length_continuation_limit"],
        )
        self.assertFalse(capabilities["protective_expansion_gate"]["default_selected"])
        self.assertEqual(
            "available_opt_in",
            capabilities["protective_expansion_gate"]["status"],
        )
        self.assertEqual("available_opt_in", capabilities["delivery_cleanliness_gate"]["status"])
        self.assertFalse(capabilities["delivery_cleanliness_gate"]["default_selected"])
        self.assertEqual("available_opt_in", capabilities["repetition_cleanup_gate"]["status"])
        self.assertFalse(capabilities["repetition_cleanup_gate"]["default_selected"])
        for host in (
            "codex",
            "codebuddy",
            "claude_code",
            "zcode",
            "qwen_code",
            "kimi_code_cli",
            "opencode",
            "hermes_agent",
            "deepseek_harness",
        ):
            self.assertIn("adapter_source", capabilities["hosts"][host])
        self.assertEqual(
            "lifecycle_verified", capabilities["hosts"]["qwen_code"]["status"]
        )
        self.assertTrue(capabilities["hosts"]["qwen_code"]["live_lifecycle_verified"])
        self.assertEqual(
            "lifecycle_verified_single_stop",
            capabilities["hosts"]["kimi_code_cli"]["status"],
        )
        self.assertEqual(
            "lifecycle_verified_interactive_only",
            capabilities["hosts"]["opencode"]["status"],
        )
        self.assertTrue(capabilities["hosts"]["opencode"]["live_lifecycle_verified"])
        self.assertFalse(capabilities["hosts"]["opencode"]["headless_run_supported"])
        self.assertEqual(
            "lifecycle_verified_fresh_query_single_pass",
            capabilities["hosts"]["hermes_agent"]["status"],
        )
        self.assertTrue(
            capabilities["hosts"]["hermes_agent"]["live_writing_adapter_verified"]
        )
        self.assertEqual(
            ["delivery_review"],
            capabilities["hosts"]["hermes_agent"]["supported_capabilities"],
        )
        self.assertFalse(
            capabilities["hosts"]["hermes_agent"]["interactive_cli_supported"]
        )
        self.assertFalse(
            capabilities["hosts"]["hermes_agent"]["resumable_session_supported"]
        )
        self.assertFalse(
            capabilities["hosts"]["hermes_agent"]["oneshot_supported"]
        )
        self.assertIn(
            "persists D0 before transform",
            capabilities["hosts"]["hermes_agent"]["host_limit"],
        )
        self.assertTrue(
            capabilities["hosts"]["kimi_code_cli"]["live_lifecycle_verified"]
        )
        self.assertTrue(
            capabilities["hosts"]["deepseek_harness"]["live_lifecycle_verified"]
        )
        self.assertEqual(
            "lifecycle_verified_headless",
            capabilities["hosts"]["deepseek_harness"]["status"],
        )
        self.assertEqual(
            ["delivery_review"],
            capabilities["hosts"]["deepseek_harness"]["online_verified_capabilities"],
        )
        self.assertIn(
            "without a second Stop",
            capabilities["hosts"]["kimi_code_cli"]["host_limit"],
        )

    def test_opencode_host_ceiling_declaration_matches_runtime(self) -> None:
        capabilities = json.loads(
            (HOOK_ROOT / "host-capabilities.json").read_text(encoding="utf-8")
        )
        opencode = capabilities["hosts"]["opencode"]
        capability_budget = opencode["over_length_continuation_limit"]
        host_ceiling = opencode["host_continuation_ceiling"]
        runtime = (
            HOOK_ROOT / "adapters/opencode/opencode_gate_plugin.js"
        ).read_text(encoding="utf-8")
        match = re.search(r"const MAX_HOST_CONTINUATIONS = (\d+)", runtime)

        self.assertEqual(7, capability_budget)
        self.assertEqual(8, host_ceiling)
        self.assertGreater(host_ceiling, capability_budget)
        self.assertIsNotNone(match)
        self.assertEqual(host_ceiling, int(match.group(1)))

    def test_plain_skill_packages_remain_hook_free_and_keep_lint(self) -> None:
        for packaged_skill in (
            ROOT / "packages/agent-skills/skills/chinese-official-writing",
            ROOT / "packages/qwen-code/skills/chinese-official-writing",
            ROOT / "packages/qwenwork/skills/chinese-official-writing",
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
