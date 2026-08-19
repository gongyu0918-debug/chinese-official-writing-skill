# v1.6.10 本地发行候选

日期：2026-08-19

状态：`VALIDATION_PENDING`。本文件当前只绑定本地候选；发布完成前不代表 GitHub、SkillHub.cn 或 ClawHub 已存在1.6.10。

## 固定对象与范围

- 上一正式 tag：`v1.6.9^{commit}=5047c224456183d97dd46cb5be09506bfdcfd0b8`。
- 公开候选起点：`main@438a33e8c7733e7c24123b8383854731ce404c81`。
- 候选分支：`codex/release-v1.6.10`。
- 目标版本：`1.6.10`。
- 公开包不包含本地付费提纲能力 `outline_assist`。
- SkillHub 使用 canonical 清洁包并保留可选 Hook；ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 无 Hook 包。

## 主要变化

- 完善标题与正文边界：主标题去除句末句号并与正文留空行，编号正文仍保留必要句号。
- 收束未决状态引出的材料外程序，减少重复规则和解释性负担。
- 篇幅不足、超长收束 Hook 共享引用、数字、字段和归属关系保护。
- 精简会议纪要、函件和通用文种叶中重复的使用说明。

## 已有真实证据

- 标题生成16/16、同稿修复12/12及两路自然路由通过。
- WR-007 与 AH-001 组合真实写稿24/24技术有效；SOL、Grok、Qwen 三方冷审未发现候选独有硬失败。
- reference 减负后的会议纪要与工作联系函真实稿通过；报告、方案和 AI 算力未通过的减负候选均已撤回，未进入本版本。

## 待完成发行门

- 直接相关测试、全量测试、quick validation、同步幂等和 diff check。
- SkillHub 与 ClawHub 清洁包文件边界、哈希和 dry-run。
- GitHub tag/Release、SkillHub.cn 与 ClawHub 正式回执及发布后只读核验。
