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
            "产品写稿规则不得进入 `AGENTS.md`",
            "每累计 5 次 commit",
            "禁止直接誊抄第三方代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文",
            "真实链路 A/B",
            "解盲前不泄露候选身份",
            "完整插件包可携带可选 Hook 伴随物",
            "专属 `hooks/` 目录",
            "`packages/openclaw/` 排除 Hook 和交付门禁资产",
            "`packages/openclaw/` 随 GitHub 仓库维护，不代表 ClawHub 已发布同版",
            "GitHub、skillhub.cn、ClawHub 和 Red SkillHub 是彼此独立的发行面",
            "包内存在、插件安装、功能启用、信任确认和真实执行是五项独立事实",
            "未经授权不得合并 `main`、推送、移动 tag、创建 Release 或上传平台",
            "写作行为类规则只修复至少三份真实样本共同指向的机制",
            "确定性工程、安全或发行缺陷须有可重复证据",
            "不得择优汇报",
            "来源证明缺失时记 `unavailable`",
            "实际测试命令与结果",
            "本仓库及仓内当前包统一采用根 `LICENSE`（MIT）",
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
