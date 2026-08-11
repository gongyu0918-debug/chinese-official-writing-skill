# v1.6.1 GitHub 发布记录

## 发布范围

- 本次只发布 GitHub `main`、annotated tag `v1.6.1` 和 GitHub Release。
- SkillHub 本次暂缓更新，没有执行正式上传。
- ClawHub/OpenClaw 继续固定在已发布 v1.6.0；`openclaw/` 相对 `v1.6.0^{commit}=0f6ec603993d5595e784fa7079837e299d1b0da3` 零差异。
- 小红书 Red SkillHub 未触碰。
- 偏短篇幅 Hook v2 研究分支及其产品提交未进入 v1.6.1。

## 主要变化

- 精简运行入口 frontmatter，只保留发现所需字段和标签；新闻稿件能力在 description 中前置呈现。
- 将运行规则中的“顺稿”“收束”等维护用语替换为普通表达，并把“先……再……”仅作为全文通读的软线索，不按词表或次数自动判错。
- SkillHub/Codex 完整包提供默认关闭的 Codex、Claude Code、WorkBuddy/CodeBuddy Hook 伴随物；启用、信任和真实执行分别确认。Hook 的真实矩阵没有形成 D1，不宣称质量提升或全面兜底，并保留额外 Stop 延迟风险。
- 仓库及非 ClawHub 内容统一采用 MIT；只有冻结的 ClawHub/OpenClaw 发行面采用 MIT-0。
- README 同题示例更新为 `gpt-5.6-sol` `ultra` 使用已发布 v1.6.0 Skill 的首个有效输出；两名完整题面匿名裁判均判 Skill 稿胜出。
- README 展示 SkillHub `37k+` 累计下载量下限；因动态 Shields 曾返回 `inaccessible`，使用稳定静态下限而不写成实时精确值。

## 发布前验证

- 全量 unittest：522/522 PASS。
- Promptfoo stub smoke：20/20 PASS，run `eval-2nh-2026-08-11T19:57:20`。
- 固定 v1.6.0 确定性消融：v1.6.0 为 109/111，v1.6.1 为 111/111。
- canonical quick validate、Codex plugin validator、Claude plugin validator、WorkBuddy/CodeBuddy validator：PASS。
- Claude 无模型 preflight：PASS。
- SkillHub 清洁包本地构建：46 文件，version `1.6.1`，MIT `LICENSE.md`；仅作本地包边界验证，没有上传。
- 镜像同步两次内容幂等；Windows 行尾造成的 index 伪脏经 Git 过滤后 blob 与 HEAD 相同，刷新索引后工作树恢复干净。
- OpenClaw tree 与 v1.6.0 相同；tracked 高置信凭据扫描、`git diff --check`：PASS。

## 外部回执

- GitHub 产品发布提交：`239eb72edc9cee513a4f76c13b9ed38f223fe32b`。
- annotated tag object：`1366d46e0e99d43a2b78a27cca97879fd04f6e99`。
- `v1.6.1^{commit}`：`239eb72edc9cee513a4f76c13b9ed38f223fe32b`，与产品发布提交一致。
- GitHub `main` 在发布时已推进到产品发布提交并完成远端回读。
- GitHub Release：[`v1.6.1`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.1)。
- Release 状态：`draft=false`、`prerelease=false`，发布时间 `2026-08-11T20:04:48Z`。
- GitHub 返回的 `targetCommitish` 为 `main`；产品事实以 annotated tag 解引用提交为准。
- 本次没有执行 SkillHub、ClawHub 或 Red SkillHub 正式上传。公开 SkillHub 与 ClawHub 版本继续保持 v1.6.0。

本节作为发布后证据提交推进 `main`，不移动 `v1.6.1` tag。
