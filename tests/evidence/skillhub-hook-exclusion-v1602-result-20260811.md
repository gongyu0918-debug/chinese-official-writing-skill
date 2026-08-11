# SkillHub Hook 发布排除结果

日期：2026-08-11

结论：`HOOK RESEARCH RETAINED / SKILLHUB RELEASE EXCLUDED / CLAWHUB FROZEN`

## 原因

固定行为根 `9c2ba632` 的 Hook enabled/disabled 真实写稿 A/B 共 9 对、18 次，全部技术有效。SOL 主裁判为 Enabled 1 胜、Disabled 7 胜、1 难分；Kimi 与 Grok 均为 Enabled 2 胜、Disabled 5 胜、2 难分。两个独立长稿出现 Enabled 独有的未给计划与状态外扩，按预注册结论为 `HOLD`。完整简洁结果见 `tests/evidence/hook-postfix-real-ab-v1602-postfix-result-20260811.md`。

所有 Enabled 写稿最终均原样发射 D0，D1 为 0。不能证明外扩由 Hook 改写造成，但也没有达到用户要求的真实写稿非劣门槛，因此不把研究伴随物放入当前 SkillHub 发布包。

## 发布边界

- canonical 与 `skills/` 继续保留 Codex、Claude Code、WorkBuddy/CodeBuddy 伴随物和共享门禁源码，供隔离研究与回归使用。
- `tools/build_skillhub_package.py` 明确排除两个宿主 manifest、全部 `hooks/` 伴随文件、`references/delivery-review-gate.md`、`scripts/review_gate.py` 和插件发现 shim。
- SkillHub 清洁包保留语义 Skill、references、可选只读 `prose_lint.py`、平台 frontmatter、`_meta.json` 和 MIT `LICENSE.md`。
- ClawHub/OpenClaw 继续逐字冻结在 v1.6.0，不参与本轮构建或同步。

## 实际验证

- focused builder、allowlist 与三层能力测试：7/7 通过。
- 清洁包：32 文件；Hook/门禁禁入扫描通过。
- SkillHub CLI 2026.8.5：`dryRun=true`、slug `chinese-official-writing`、测试坐标 `1.6.2`；未上传。
- `git diff --check` 通过。

本文件只记录本地候选边界；未合并 `main`、未推送、未打 tag、未发布。
