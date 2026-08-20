# v1.6.11 本地发行候选

日期：2026-08-20

状态：`PREPARED_VALIDATION_PENDING`。本文件绑定本地发行分支；发布完成前不代表 GitHub、SkillHub.cn 或 ClawHub 已存在1.6.11。

## 固定对象与范围

- 上一正式 tag：`v1.6.10^{commit}=af12b771e376e815c44d53b08d26c635805586b3`。
- 公开候选起点：`main@f07eae5b`。
- 候选分支：`codex/release-v1.6.11`。
- 目标版本：`1.6.11`。
- 公开包不包含本地付费提纲能力 `outline_assist`。
- SkillHub 使用 canonical 清洁包并保留可选 Hook；ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 无 Hook 包。

## 主要变化

- 完善进行态与责任主体边界，避免把未决状态机械改成无主体动作。
- 允许同数中文数量的透明归纳进入语义核验，不直接越过事实和归属检查。
- 修复相对期限、序号和修辞性“一方面/另一方面”的共享硬锚误判。

## 已有真实证据

- 状态、进行态与责任主体5个真实小样本通过独立 SOL 复核。
- WorkBuddy/CodeBuddy 对同一106字 D0 完成中文数量透明归纳在线事务；含新增对象和错归属的候选被语义层选择 D0。
- Claude Code 在线压缩修辞性方面并选择 D1；相对期限变化在当前产品生命周期复放中以中文数量原因选择 D0并逐字交付原稿。

## 待完成发布门

- 全量单元测试、固定确定性消融、quick validation、镜像幂等和差异检查。
- SkillHub 与 ClawHub 清洁包清单、许可证、指纹和 dry-run。
- 远端 main/tag 漂移复核后，才可推送、创建 GitHub Release并上传两个平台。
