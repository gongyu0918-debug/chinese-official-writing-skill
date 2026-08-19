# v1.6.10 本地发行候选

日期：2026-08-19

状态：`READY_LOCAL_CANDIDATE`。本文件只绑定本地候选；发布完成前不代表 GitHub、SkillHub.cn 或 ClawHub 已存在1.6.10。

## 固定对象与范围

- 上一正式 tag：`v1.6.9^{commit}=5047c224456183d97dd46cb5be09506bfdcfd0b8`。
- 公开候选起点：`main@438a33e8c7733e7c24123b8383854731ce404c81`。
- 候选分支：`codex/release-v1.6.10`。
- 版本准备提交：`7ba12504db171bc992e3adbdb6c5c9ff4a1cf728`。
- 校验契约修正提交：`b1f11ba57510116d5720be0e698976f43fb44d07`。
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

## 实际验证

- 直接相关测试：183/183通过。首次运行有2项旧字符串断言失败，均指向已经验证并压缩的 reference/AGENTS 长句；更新测试契约后，同组复跑通过。
- 全量测试首次为630/632，失败原因同为上述旧断言；修正后先复跑3/3，再取得最终632/632通过回执。
- canonical、Agent Skills、Qwen Code、Hermes 均通过通用 quick validation。OpenClaw 因平台专用 `category` 字段被通用 validator 拒绝，按专用包边界和 dry-run 验证，不将该结果写成通过。
- `sync_adapters.py`、`git diff --check`、版本面和工作树终态检查通过。

## 候选包

- SkillHub 清洁包61文件；路径与 LF 规范化内容哈希为 `762f4d6aee3381d99a02f70add845b1868a40f11ef61f5cf62877919a9df4224`。
- ClawHub 无 Hook 包33文件；同口径哈希为 `c7daa752bcd0fc43d0f91c15097ae1a86cd68ffefbec38bc8c4510b8a56981f4`，Hook、交付门禁和 `agents/openai.yaml` 命中数为0。
- 两包许可证 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`，与根 MIT `LICENSE` 一致。
- SkillHub dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.10`。
- ClawHub dry-run 返回 `status=would-publish`、latestVersion `1.6.9`、fileCount `33`、平台 fingerprint `cc519248b1279a8f49681522a089f2ff19269abb8cdef542f7ed83971ddedd77`。展示名为“中文公文写作”，分类使用当前有效的 `productivity,knowledge`，话题使用 `chinese-writing,official-writing,office-productivity,content-creation`。

## 未执行与剩余边界

- 尚未推送、创建 tag 或 GitHub Release，尚未正式上传 SkillHub.cn 与 ClawHub。
- 本版本没有重新跑 Codex、CodeBuddy/WorkBuddy 在线 Hook 生命周期；共享硬锚的真实修订与静态组装证据已经在本候选中闭环，宿主协议没有变化。
- 付费提纲能力仍只在 `codex/paid-outline-review`，不进入三个公开发行面。
