from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AgentsControlPlaneTests(unittest.TestCase):
    def test_root_agents_is_small_engineering_only_control_plane(self) -> None:
        path = ROOT / "AGENTS.md"
        text = path.read_text(encoding="utf-8")
        self.assertLess(len(path.read_bytes()), 12 * 1024)
        for required in [
            "本文件是活动规则入口",
            "产品规则只放 `chinese-official-writing/SKILL.md` 及 `references/`",
            "历史归档不作为新要求",
            "main 不含付费提纲 Hook、胶水、测试和详细规格",
        ]:
            self.assertIn(required, text)
        active_link = re.search(r"\[开发细则\]\(([^)]+)\)", text)
        self.assertIsNotNone(active_link)
        development_path = ROOT / active_link.group(1)
        self.assertTrue(development_path.is_file())
        development = development_path.read_text(encoding="utf-8")
        for required in [
            "立即跑真实写稿或生命周期",
            "全量门原则上只在合并或发布前跑一次",
            "每累计 5 次 commit",
            "未获当次明确授权，不合并 main",
            "`codex/paid-outline-review` 保持“当前 main + 付费提纲增量”",
            "Skill 安装、companion 组装、插件安装、启用、信任和真实执行分别举证",
            "报告摘要、branch、commit、实际命令与结果",
            "外部写入、发布和删除只在明确授权范围内执行",
        ]:
            self.assertIn(required, development)
        license_link = re.search(r"仓库及仓内包使用根 \[LICENSE\]\(([^)]+)\)（MIT）", development)
        self.assertIsNotNone(license_link)
        self.assertEqual(
            (development_path.parent / license_link.group(1)).resolve(),
            (ROOT / "LICENSE").resolve(),
        )
        for product_rule in ["妥否，请批示", "报告不用请批语", "先……再……", "持续推进"]:
            self.assertNotIn(product_rule, text)

    def test_pre_rewrite_snapshot_and_index_are_preserved(self) -> None:
        snapshot = ROOT / "maintenance" / "docs" / "evidence" / "AGENTS-control-plane-v1.6.0-pre-v1601.md"
        normalized = snapshot.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
        self.assertEqual(
            sha256(normalized).hexdigest().upper(),
            "2F76DAC314A91FBE9D20E28F321135893DC5C8E3C964B4B49EC15CD4B5B5710A",
        )
        index = (ROOT / "maintenance" / "docs" / "evidence" / "README.md").read_text(encoding="utf-8")
        self.assertIn("AGENTS-control-plane-v1.6.0-pre-v1601.md", index)
        self.assertTrue((ROOT / "maintenance" / "docs" / "evidence" / "AGENTS-history-through-v1.5.39.md").is_file())


if __name__ == "__main__":
    unittest.main()
