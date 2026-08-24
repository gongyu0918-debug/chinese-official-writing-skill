# v1.6.15 本地候选基线

日期：2026-08-24

状态：`PREPARING_LOCAL_CANDIDATE`。正式发布门与平台 dry-run 完成前，本文件不表示 GitHub、SkillHub.cn 或 ClawHub 已存在 v1.6.15。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.14^{commit}=b0e5d5c43849b082dd023ba72101689b3eacd0b3`。
- 本轮内容基线：`main@e3ed9bb374fd13234ea0eff9ea61c9e0f3cc7e69`。
- 本地发行分支：`codex/release-v1.6.15`。
- 目标版本：`1.6.15`。
- 合入公开候选：国产 CLI Hook adapter 合并提交 `2ea4a58b`；description 两字原子合并提交 `bb6b46aa`。
- 当前 main 已验证但未发布的 `HK-008b`、`WR-019c/019d`、`WR-014-R4` 一并进入本次补丁候选。
- `WR-020b1` 已拒绝，不进入产品；付费提纲及其 coordinator、胶水、测试和详细规格不反向进入公开 main。
- ClawHub 继续使用普通 OpenClaw 包，不含 Hook、交付门禁或 `agents/openai.yaml`。

## 待完成发布门

- 版本、镜像、Hook adapter、全量 unittest、固定基线消融、Promptfoo stub smoke、quick validation、包体清洁与 dry-run。
- 正式外部写入前复核 HEAD、工作树、远端 main/tag、slug、展示名、分类、话题、文件数和 fingerprint。
