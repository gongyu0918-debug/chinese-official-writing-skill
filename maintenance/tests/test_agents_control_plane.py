from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AgentsControlPlaneTests(unittest.TestCase):
    def test_root_agents_is_small_engineering_only_control_plane(self) -> None:
        path = ROOT / "AGENTS.md"
        text = path.read_text(encoding="utf-8")
        self.assertLess(len(path.read_bytes()), 12 * 1024)
        for required in [
            "本文件是仓库唯一活动开发纪律",
            "产品写稿规则只写入 `chinese-official-writing/SKILL.md` 与 `references/`",
            "真实结果优先",
            "全量测试原则上只在准备合并或发布前运行一次",
            "每累计5次 commit",
            "未经当次明确授权，不合并 `main`",
            "`main` 是公开版主线，不包含提纲审核 Hook",
            "`codex/paid-outline-review` 是“当前 `main` + 付费提纲增量”",
            "普通 Skill 安装、Hook companion 组装、插件安装、启用、信任和真实执行是不同事实",
            "当前仓库和仓内包使用根 `LICENSE`（MIT）",
            "交付时报告修改摘要、branch、commit、实际命令与结果",
            "外部写入、发布和删除只在明确授权范围内执行",
        ]:
            self.assertIn(required, text)
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
