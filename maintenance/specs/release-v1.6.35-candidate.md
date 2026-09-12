# v1.6.35 纯维护候选

- 候选分支：`codex/release-v1.6.35-maintenance-20260913`。
- 发布基线：`dae0a1ff7ffc3b518ecf167c4c8ef361b18ead06`（v1.6.34 发布证据分支终点）。
- 用户范围：2026年9月13日只发布一个版本；不创建心跳，不预排次日版本。
- 本版范围：统一 README、七个公开 Hook adapter manifest、DeepSeek Harness package 和 OpenClaw 包的 `1.6.35` 版本元数据；补回 v1.6.31—v1.6.33 发布证据及索引。
- 产品边界：`SKILL.md`、`references/`、`scripts/` 和 Hook 运行时代码保持 v1.6.34 内容；ClawHub 继续使用无 Hook 包，GitHub 与 SkillHub 保留 1.x MIT Hook 目录。
- 明确排除：讲话人物排序、文种族群分叶、旁白检测以及任何 2.0 或 Pro 内容。前述写作候选在本轮真实写稿中出现候选独有硬回退，均留在未发布分支。
- 发布门：精确树差异、全量 unittest、五套普通 Skill quick validation、镜像幂等、SkillHub/ClawHub clean package dry-run、远端 ancestry 与 tag 冲突检查。
- 平台边界：GitHub、SkillHub 和 ClawHub 各执行一次正式发布；SkillHub 或 ClawHub 成功回执后不做传播轮询或重复提交。
