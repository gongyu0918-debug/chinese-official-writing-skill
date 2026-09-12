# v1.6.35 发布记录

## 冻结范围

v1.6.35 是 2026年9月13日的纯维护版本。相较 v1.6.34，写作规则、检查脚本和 Hook 运行时代码不变；本版只统一公开版本元数据、补齐 v1.6.31—v1.6.33 发布证据与索引，并修正相应测试中的当前版本常量。

本轮曾验证讲话人物排序、文种族群分叶和旁白检测候选。讲话排序在 MiniMax 留出中重复破坏具体人物与泛称顺序；四文种与两文种分叶在通知、调研或采购控制中重复出现正文外说明及材料外推断；旁白检测只能证明显式运行脚本时提高发现率，不能证明普通路径稳定降低旁白。上述候选均未进入本版，也不以篇幅、票数或工程门掩盖写稿失败。

## 产品与平台边界

- GitHub 与 SkillHub 的 1.x 包保留 MIT Hook 目录；本版只改 adapter manifest 版本，不改 Hook 行为。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing` 无 Hook 包。
- `outline_assist`、`paid/redhead_docx`、2.0 规则和 Pro 源码均不在公开发布树。
- SkillHub 与 ClawHub 各只允许一次正式提交；取得成功回执后不做传播轮询。

## 发布前验证

- 候选内容提交：`0f0793cf872b52741d8dc039928be2b2ca0e9f70`；后续只补本记录，发布产品与版本元数据不再改变。
- 相对 v1.6.34，`SKILL.md`、`references/`、`scripts/`、`hooks/core/`、`hooks/capabilities/` 和 `hooks/shared/` 的差异路径数均为 0；公开差异限于版本元数据、README、测试常量与维护证据。
- `py -3.13 -B -X utf8 -m unittest discover -s maintenance/tests -p 'test_*.py'`：850/850 通过，耗时 140.913 秒。
- 版本、边界、状态台账与可达性聚焦回归：107/107 通过。
- Skill Creator `quick_validate.py`：canonical、Agent Skills、Qwen Code、QwenWork、Hermes 共 5/5 通过；OpenClaw 保留平台专用 frontmatter，由仓库边界测试覆盖。
- `sync_adapters.py` 复跑前后工作树均为 clean，镜像幂等；`git diff --check` 通过。
- SkillHub clean package：98 文件；`publish --version 1.6.35 --dry-run --json` 返回 `dryRun=true`。
- ClawHub 无 Hook 包：47 文件；dry-run 返回 `status=would-publish`、`latestVersion=1.6.34`、fingerprint `f470da3efa343b734df664566d9efa3e375bb03dad487df9a4bf41601b4b1813`。
- 远端发布前检查：`origin/main=52dfe7aa86ee8c3ced184b0fbf6cddddb4630914` 未漂移；`origin/main` 与 `v1.6.34` 均为候选祖先；远端 `v1.6.35` tag 不存在；工作树 clean；公开树中付费路径数为 0。

## 发布回执

- GitHub：一次 `git push --atomic` 成功，将 `main` 从 `52dfe7aa86ee8c3ced184b0fbf6cddddb4630914` 快进至 tag 解引用提交 `c0abfeeb3d2a21cfd6ec722de7d8ae534ad68f61`，并创建 annotated tag object `0ecfb334e342ee7ac211cac3f0a6f11c772c29a9`；GitHub Release 已公开：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.35>。
- SkillHub：向既有 `skillId=70149` 正式提交一次，返回 `ok=true`、`versionId=308557`、98 个文件、fingerprint `6eba65acdda394a97cb9d797b8b989e960a1d3c3c11ab2b74b28572c6c5037e1`、`tags.latest=1.6.35`；`reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。成功回执后未做传播轮询或重复提交。
- ClawHub：向 `chinese-official-writing` 正式提交一次，返回 `ok=true`、`status=published`、`versionId=k97agmzzb012patmb1a4k933gd8e96fb`、47 个文件、fingerprint `f470da3efa343b734df664566d9efa3e375bb03dad487df9a4bf41601b4b1813`。回执中的 `latestVersion=1.6.34` 只记录提交当时的平台返回值；按项目规范以成功发布回执为完成依据，未做传播轮询或重复提交。
- 本次未创建心跳、定时任务或次日版本安排；明日版本由新的工令另行决定。
