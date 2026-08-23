# v1.6.14 本地候选基线

日期：2026-08-23

状态：`PREPARING_LOCAL_CANDIDATE`。本文件先登记目标版本和发布边界；正式外部写入前补齐固定提交、全量门、包体指纹和 dry-run 回执。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.13^{commit}=c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`。
- 上一远端发布回执：`origin/main@4b51fd8242850e5c35fe86406216f6cfd26f49c0`。
- 本轮内容基线：`main@bb7bdc3c0a06937184a3a220740d92aff5b884ea`。
- 本地候选分支：`codex/release-v1.6.14`。
- 目标版本：`1.6.14`。
- 公开候选只包含本地 main 已清洁合入的 `UL-005` 状态收口、`OV-001` 超长判定与 sentence-target、`HK-008` 终态脱敏、`WR-014-R3` 能力/计划状态锚，以及对应测试、规格和证据。
- `MT-005c` description 减载已因真实稿硬回退撤回，候选 description 与 v1.6.13 相同。
- `codex/paid-outline-review` 不反向合入；公开树不含付费提纲 coordinator、胶水、测试或详细实现规格。

## 真实写稿与生命周期依据

- `OV-001`：五路采购请示222—251字且事实、状态和办理功能完整；三题五路语义判定15/15；CodeBuddy 两稿分别328→236、496→229，一次压缩、语义通过并闭合 hash；Kimi K3、Grok 4.6、Qwen 3.8 Max、SOL 对两个匿名案例均4/4选择达标稿。
- `WR-014-R3`：五路有效反例稿5/5保留“可安排”，四路有效正向控制4/4保留“拟”和未决审核；OpenCode provider stream 失败只记技术失败。
- `HK-008`：CodeBuddy 2.115.0 真实 Stop 生命周期保持 D0 逐字交付，并在终态移除原始事务数据；宿主日志和异常中断不冒充已覆盖。
- `WR-018`：五家 provider、三个文种共15稿，13/15硬通过、0/15功能性过薄；单个 MiniMax 状态升级和 Ollama 重复/过程话语保留为模型风险，不新增统一字数门。

## 发布门与候选包

- 待运行最终全量 unittest、focused、quick validation、确定性消融、Promptfoo stub、同步幂等、Markdown 链接与 `git diff --check`。
- SkillHub.cn 清洁包目标为61文件，slug `chinese-official-writing`、展示名“中文公文写作”、现有条目 `@user_f3d82da7/chinese-official-writing`。
- ClawHub 固定使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 包；owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 均不得漂移。

## 当前发布边界

- 用户已明确授权发布 GitHub、SkillHub.cn 和 ClawHub `1.6.14`；ClawHub 必须继续使用33文件无 Hook 包。
- 小红书 Red SkillHub 不在本次范围内，不查询、不上传。
- 本文件当前不表示 GitHub、SkillHub.cn 或 ClawHub 已存在1.6.14；外部写入只在候选冻结且全部发布门通过后执行。
