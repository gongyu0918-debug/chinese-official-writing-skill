from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "chinese-official-writing"


class HookLayerContractTests(unittest.TestCase):
    def test_gate_spec_is_hook_only_and_not_an_ordinary_skill_route(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        glue = (SKILL_ROOT / "hooks" / "AGENT_GLUE.md").read_text(encoding="utf-8")
        gate_spec = (
            SKILL_ROOT / "references" / "delivery-review-gate.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("delivery-review-gate.md", skill)
        self.assertIn("Three layers", glue)
        self.assertIn("not an ordinary Skill reference route", glue)
        self.assertIn("普通 `SKILL.md` 不加载本页", gate_spec)
        self.assertIn("Hook 默认禁用", gate_spec)

    def test_optional_lint_ends_before_d0_and_is_not_hook_input(self) -> None:
        glue = (SKILL_ROOT / "hooks" / "AGENT_GLUE.md").read_text(encoding="utf-8")
        bridge = (SKILL_ROOT / "hooks" / "gate_stop_hook.py").read_text(encoding="utf-8")
        claude_adapter = (
            SKILL_ROOT / "hooks" / "claude-code" / "scripts" / "gate_stop_hook.py"
        ).read_text(encoding="utf-8")
        repository_manifest = (ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8")
        claude_manifest = (
            SKILL_ROOT / "hooks" / "claude-code" / "hooks" / "hooks.json"
        ).read_text(encoding="utf-8")
        host_adapter = (SKILL_ROOT / "hooks" / "host_gate_adapter.py").read_text(
            encoding="utf-8"
        )
        host_manifest = (SKILL_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8")
        workbuddy_manifest = (
            SKILL_ROOT / "hooks" / "workbuddy" / "hooks.json"
        ).read_text(encoding="utf-8")

        self.assertIn("optional and never edits the draft automatically", glue)
        self.assertIn("It does not run `prose_lint.py`", glue)
        self.assertIn("immutable D0 is the fallback", glue)
        hook_surfaces = {
            "shared bridge": bridge,
            "Claude adapter": claude_adapter,
            "repository manifest": repository_manifest,
            "Claude manifest": claude_manifest,
            "Codex and WorkBuddy adapter": host_adapter,
            "Codex and WorkBuddy manifest": host_manifest,
            "WorkBuddy manifest": workbuddy_manifest,
        }
        for name, hook_surface in hook_surfaces.items():
            with self.subTest(surface=name):
                self.assertNotIn("prose_lint", hook_surface)

    def test_capability_claims_match_repository_and_package_surfaces(self) -> None:
        capabilities = json.loads(
            (SKILL_ROOT / "hooks" / "host-capabilities.json").read_text(encoding="utf-8")
        )
        self.assertEqual(4, capabilities["schema_version"])
        self.assertFalse(capabilities["activation"]["ordinary_skill_install_enables_hooks"])
        self.assertEqual("semantic_skill_only", capabilities["activation"]["current_skillhub_publish_package"])
        self.assertEqual("HOLD", capabilities["activation"]["real_writing_gate"])

        codex = capabilities["hosts"]["codex"]
        self.assertEqual("package_registration_verified", codex["status"])
        self.assertEqual("present", codex["package_presence"]["repository_companion"])
        self.assertEqual(
            "excluded_after_real_ab_hold", codex["package_presence"]["skillhub_ordinary_package"]
        )
        self.assertEqual("unavailable_in_current_publish_package", codex["skillhub_activation"])
        self.assertFalse(codex["live_lifecycle_verified"])

        claude = capabilities["hosts"]["claude_code"]
        self.assertEqual("repository_companion_only", claude["package_presence"])
        self.assertEqual("excluded_after_real_ab_hold", claude["publication_status"])
        self.assertEqual("frozen", capabilities["hosts"]["openclaw"]["status"])
        workbuddy = capabilities["hosts"]["workbuddy"]
        self.assertEqual("package_manifest_verified", workbuddy["status"])
        self.assertEqual("WorkBuddy 5.3.8 / CodeBuddy Code 2.115.0", workbuddy["locally_inspected_host_version"])
        self.assertEqual("repository_companion_only", workbuddy["package_presence"])
        self.assertEqual("excluded_after_real_ab_hold", workbuddy["publication_status"])
        self.assertFalse(workbuddy["live_lifecycle_verified"])


if __name__ == "__main__":
    unittest.main()
