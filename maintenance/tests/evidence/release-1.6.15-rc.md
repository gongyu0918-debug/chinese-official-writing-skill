# v1.6.15 本地候选基线

日期：2026-08-24

状态：`READY_LOCAL_CANDIDATE`。本文件绑定本地发行候选；正式发布回执完成前，不表示 GitHub、SkillHub.cn 或 ClawHub 已存在 v1.6.15。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.14^{commit}=b0e5d5c43849b082dd023ba72101689b3eacd0b3`。
- 本轮内容基线：`main@e3ed9bb374fd13234ea0eff9ea61c9e0f3cc7e69`。
- 本地发行分支：`codex/release-v1.6.15`。
- 版本准备提交：`90e80e5b0ab0397993622ce1e321871b31e394f1`；发布证据脱敏提交：`9896d36bfbcd5b824d8b6f711d0ff2bc89561219`。
- 目标版本：`1.6.15`。
- 合入公开候选：国产 CLI Hook adapter 合并提交 `2ea4a58b`；description 两字原子合并提交 `bb6b46aa`。
- 当前 main 已验证但未发布的 `HK-008b`、`WR-019c/019d`、`WR-014-R4` 一并进入本次补丁候选。
- `WR-020b1` 已拒绝，不进入产品；付费提纲及其 coordinator、胶水、测试和详细规格不反向进入公开 main。
- ClawHub 继续使用普通 OpenClaw 包，不含 Hook、交付门禁或 `agents/openai.yaml`。

## 真实写稿与生命周期依据

- 国产 CLI Hook adapter 候选先完成真实 CLI 生命周期：Qwen Code 原生扩展覆盖多次 Stop，Kimi Code 原生插件覆盖单次 Stop，ZCode 通过社区 wrapper runtime 覆盖 D0/hash 生命周期；三者的宿主限制分别写入 adapter README 和 manifest，不把静态适配冒充所有宿主均已在线闭环。
- `MT-005b6b` 只把 description 中“实施细则”合并为“细则”，204字降至202字；两轮五 provider 共50次真实正式发文意图路由均为5/5触发、0/5误触发，既有写稿事实、状态和文种功能未出现候选独有硬回退。
- 本轮不把付费提纲、`WR-020b1` 或未通过的 description 组合并入公开产品。

## 发布门

- 合并后定向测试96/96通过；版本、镜像、adapter 与边界定向测试99/99通过。
- 全量 unittest 684/684通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过。
- 固定 v1.6.14/current 的确定性消融分别110/111、111/111；基线唯一失败为旧 tag 不含本轮新增 adapter assembly contract，当前候选0失败。
- Promptfoo 本地 stub smoke 20/20通过，Skill 10胜、baseline 0胜、judge consistency 1.0。
- `sync_adapters.py` 二次执行前后 diff hash 均为空树 hash；128个 tracked Python 文件内存编译、137个 tracked JSON 文件解析与 `git diff --check`通过。
- 脱敏后61个国产 CLI runtime JSON 重新解析，三份修改后的 runner 编译，adapter/contract 定向测试16/16通过；新增和修改文件中本机用户目录、仓库绝对路径命中为0。

## 候选包与平台坐标

- SkillHub.cn 清洁包71文件，本地规范化文件树指纹 `ef7635f955422aadfeaf28bef06cf770e6a82df207b87c1e1c2e07ab5452899b`；slug `chinese-official-writing`，展示名“中文公文写作”，现有条目 `@user_f3d82da7/chinese-official-writing`。dry-run 返回 `dryRun=true`、version `1.6.15`。该包按既有公开边界包含默认关闭的可选 Hook。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 包，本地规范化文件树指纹 `b2fc77dcba8421337bbde7f13104cc864ba61bef5556dac17b84e4daba2dd87c`；Hook 文件命中为0。dry-run 返回 `would-publish`、latestVersion `1.6.14`、fileCount `33`、平台 fingerprint `f20de481091a81905190c84c992e694bd5f875033b6fde2a643df0e62a0f4f1f`。
- ClawHub 坐标保持 owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`。
- SkillHub.cn 当前公开版本和 ClawHub `latestVersion` 均为 `1.6.14`；本地及 GitHub 远端均不存在 `v1.6.15`。

## 当前发布边界

- 用户已明确授权发布 GitHub、SkillHub.cn 和 ClawHub `1.6.15`；ClawHub 必须继续使用33文件无 Hook 包。
- 小红书 Red SkillHub 不在本次范围内，不查询、不上传。
- 本文件写入时尚未推送 main、创建 tag 或 GitHub Release，也未正式上传 SkillHub.cn 或 ClawHub。
- 正式外部写入前仍须复核最终 HEAD、工作树、远端 main/tag、版本表面和两个包体指纹；正式 ClawHub 命令绑定最终产品 tag 提交。
