# v1.6.14 本地候选基线

日期：2026-08-23

状态：`READY_LOCAL_CANDIDATE`。本文件绑定本地发行候选；正式发布回执完成前，不表示 GitHub、SkillHub.cn 或 ClawHub 已存在 v1.6.14。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.13^{commit}=c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`。
- 上一远端发布回执：`origin/main@4b51fd8242850e5c35fe86406216f6cfd26f49c0`。
- 本轮内容基线：`main@bb7bdc3c0a06937184a3a220740d92aff5b884ea`。
- 本地候选分支：`codex/release-v1.6.14`。
- 版本准备提交：`dbf9cf88295ab01b84c4c1c8a78779578b8f15cf`。
- 目标版本：`1.6.14`。
- 公开候选只包含本地 main 已清洁合入的 `UL-005` 状态收口、`OV-001` 超长判定与 sentence-target、`HK-008` 终态脱敏、`WR-014-R3` 能力/计划状态锚，以及对应测试、规格和证据。
- `MT-005c` description 减载已因真实稿硬回退撤回，候选 description 与 v1.6.13 相同。
- `codex/paid-outline-review` 不反向合入；公开树不含付费提纲 coordinator、胶水、测试或详细实现规格。

## 真实写稿与生命周期依据

- `OV-001`：五路采购请示222—251字且事实、状态和办理功能完整；三题五路语义判定15/15；CodeBuddy 两稿分别328→236、496→229，一次压缩、语义通过并闭合 hash；Kimi K3、Grok 4.6、Qwen 3.8 Max、SOL 对两个匿名案例均4/4选择达标稿。
- `WR-014-R3`：五路有效反例稿5/5保留“可安排”，四路有效正向控制4/4保留“拟”和未决审核；OpenCode provider stream 失败只记技术失败。
- `HK-008`：CodeBuddy 2.115.0 真实 Stop 生命周期保持 D0 逐字交付，并在终态移除原始事务数据；宿主日志和异常中断不冒充已覆盖。
- `WR-018`：五家 provider、三个文种共15稿，13/15硬通过、0/15功能性过薄；单个 MiniMax 状态升级和 Ollama 重复/过程话语保留为模型风险，不新增统一字数门。

## 发布门

- 固定 `v1.6.13^{commit}=c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`；其为当前候选祖先，远端不存在 `v1.6.14` tag。
- 版本边界、SkillHub 包构建、篇幅、终态清理和状态锚定向测试首次127/128；唯一失败是 README 最近证据列表漏掉上一正式发布记录。只替换该列表一项后，同组复跑128/128通过。
- 全量 unittest 660/660通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过。
- 固定 v1.6.13/current 的确定性消融分别111/111、111/111；当前与基线均0失败。
- Promptfoo 本地 stub smoke 20/20通过，Skill 10胜、baseline 0胜、judge consistency 1.0；首次从仓库根运行因无 `package.json` 返回 `ENOENT`，未进入评测且不记通过，改用仓库实际入口 `npm.cmd --prefix maintenance` 后通过。
- `sync_adapters.py` 二次执行前后 diff hash 一致；repository reachability 7/7，Python compileall、四个 JSON 解析与 `git diff --check`通过。

## 候选包与平台坐标

- SkillHub.cn 清洁包61文件，本地规范化文件树指纹 `89f320da84f6f6f72ed9883e4122935a4e2d53dc410b82d801b252ecd820bec2`；slug `chinese-official-writing`，展示名“中文公文写作”，现有条目 `@user_f3d82da7/chinese-official-writing`。dry-run 返回 `dryRun=true`、version `1.6.14`。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 包，本地规范化文件树指纹 `87f0f849bd9c5fd8ab63be84c083e839d83eed31a098d83d861b77b56b4030be`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲路径与文本命中均为0。
- ClawHub 坐标保持 owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`。dry-run 返回 `would-publish`、latestVersion `1.6.13`、fileCount `33`、平台 fingerprint `3256085ef4c746b4f99abd05c24c82098b139375563df4bf4f661b468c0fdaa7`。
- 两包许可证与根 MIT `LICENSE` 的 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`。

## 当前发布边界

- 用户已明确授权发布 GitHub、SkillHub.cn 和 ClawHub `1.6.14`；ClawHub 必须继续使用33文件无 Hook 包。
- 小红书 Red SkillHub 不在本次范围内，不查询、不上传。
- 本文件写入时尚未推送 main、创建 tag 或 GitHub Release，也未正式上传 SkillHub.cn 或 ClawHub。
- 正式外部写入前仍须核对 HEAD、工作树、远端 main/tag 和两个包体指纹；正式 ClawHub 命令绑定最终产品 tag 提交。
