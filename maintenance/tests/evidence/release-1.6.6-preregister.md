# v1.6.6 本地预发布候选预登记

日期：2026-08-16

## 固定对象

- 上一正式版本：`v1.6.5^{commit}=81061bd78c0dbf5604fb2927ba275169fc93f5ed`。
- 候选起点：`main@03e8ec98242a441a9400674cbf9a883528bfca94`。
- 候选分支：`codex/v166-release-candidate`。
- 目标版本：`1.6.6`。

## 范围

- 本版只发布已经合入主线的 WR-003 跨文种责任承载与合理推断、WR-004 约20类事务文体功能/结构/常用语路由，以及对应的时间锚和编者按标识修复。
- WR-005 普通短稿自然度继续 HOLD；不修改篇幅、洁净度、重复清理或其他 Hook 能力。
- 更新 GitHub/SkillHub 所需版本元数据、README 最近五版记录、GitHub OpenClaw 兼容源码版本和四套普通镜像。
- 构建本地 GitHub 源码归档与 SkillHub 清洁包，准备更新说明和核验记录。

## 明确禁止

- 不推送分支，不创建或移动 tag，不创建 GitHub Release。
- 不调用 SkillHub、ClawHub、Red SkillHub 或其他平台的正式上传、同步、删除、撤回或版本覆盖命令。
- 不把 ClawHub 远端状态与 GitHub `packages/openclaw/` 兼容源码混为一谈。

## 验证

- 先完成版本、README、镜像、OpenClaw 与 SkillHub builder 聚焦测试。
- 运行 canonical 与普通镜像 quick validation、同步幂等和 `git diff --check`。
- 本地候选最终化后只运行一次全量维护测试；真实写稿不重复执行，直接复用已冻结的20稿与候选直连 SOL max 结果。
- 构建全新输出目录，核对文件集合、禁入项、版本、许可证与逐文件 SHA-256 清单；可运行 SkillHub 本地 dry-run，但不得正式提交。

任一产品文件超出上述范围、工作树来源不明、版本面不一致、全量测试失败或构建包含禁入文件时停止，不生成 READY 结论。
