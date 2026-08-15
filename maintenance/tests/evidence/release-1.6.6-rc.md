# v1.6.6 本地发行候选

日期：2026-08-16

状态：`READY_LOCAL_CANDIDATE`。本地 GitHub 与 SkillHub 候选已准备完成，但不代表已经发布。

## 固定对象与范围

- 上一正式 tag：`v1.6.5^{commit}=81061bd78c0dbf5604fb2927ba275169fc93f5ed`。
- 候选起点：`main@03e8ec98242a441a9400674cbf9a883528bfca94`。
- 本地组包产品提交：`2160c8be6bf123fb4eca82b877fe8f7a7595389e`。
- 候选分支：`codex/v166-release-candidate`。
- 候选版本：`1.6.6`；上一正式版本仍为 `1.6.5`。
- 本版只包含 WR-003 跨文种责任承载与合理推断、WR-004 约20类事务文体功能/结构/常用语路由，以及相对时间锚和编者按标识修复。WR-005 继续 HOLD，Hook 行为相对 v1.6.5 不变。

## 主要变化

- 新增约20类事务文体的中央直接叶，按文种选择功能、结构、开端、承启、综合和结尾语，不为每类文体复制大词库。
- 合理推断须由材料主体、写作主体或近邻语篇主体承载；责任主体成立不替代事实、状态和权限核验。
- 材料只给月份、月日或时间段时不补年份；编者按明确使用功能标识。

## 真实写稿依据

- 三条指定 DeepSeek V4 Flash 路线完成20份真实写稿；原型文种功能19/20，唯一缺口为编者按标识。
- 候选直连复测覆盖编者按、演讲词和责任书；最终样本只读取 SKILL、信息选择和中央事务文体叶，保留`3月至6月`且不补年份。
- 独立 SOL max 对最终样本的事实、状态、时间锚、责任主体、文种、篇幅和直接使用全部判 PASS。
- WR-005 的11/20篇幅失败、3稿 Markdown 残留和重复/拖沓风险继续单列，不以本版发布掩盖。

## 本地候选门

- [x] 版本、README、镜像、OpenClaw 与 SkillHub builder 聚焦测试：8/8 PASS；README 可达性4/4 PASS。
- [x] canonical、Agent Skills、Qwen Code、Hermes quick validation 全部 PASS；`sync_adapters.py` 重跑零 diff；`git diff --check` PASS。
- [x] 全量维护测试：`python -B -m unittest discover -s maintenance/tests -p "test_*.py" -q`，603/603 PASS。
- [x] GitHub 源码归档与 SkillHub 清洁包已核对版本、许可证、文件集合和禁入项。
- [x] SkillHub 本地 dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.6`；没有正式提交。

## 本地候选包

唯一候选目录：`output/release-candidates/v1.6.6-local-rc/`。

### GitHub 源码归档

- 文件：`github-source-v1.6.6.zip`。
- 绑定产品提交：`2160c8be6bf123fb4eca82b877fe8f7a7595389e`。
- 大小：3,234,673 bytes。
- SHA-256：`db887478b220e207ef1182c546f2dc42b6a349e3a1a19e394a7a08d49551b281`。

### SkillHub 清洁包

- 目录：`skillhub-package/`，共57文件。
- `_meta.json` 与专用 `SKILL.md` 均为 `chinese-official-writing@1.6.6`。
- 逐文件 `SHA-256 + 相对路径` 清单文本 SHA-256：`c827e0bc0d1049d679f99b818146e06856d64b47a686d3db75d0d230068ba3bc`。
- 排除 `agents/openai.yaml` 和无扩展名 `LICENSE`，以 `LICENSE.md` 携带根 MIT；禁入项0。

待正式发布时可使用的 SkillHub 更新说明：

> 完善20类事务文体的功能、结构与常用语路由，增强跨文种责任主体和合理推断约束，补充编者按标识与相对时间锚保护。

## 未授权动作

本候选未推送、未打 tag、未创建 GitHub Release、未上传 SkillHub，也未对 ClawHub、Red SkillHub 或其他平台执行上传、同步、删除、撤回或版本覆盖操作。

只读核验时，GitHub 远端不存在 `v1.6.6` tag，SkillHub 公开 `tags.latest` 仍为 `1.6.5`。这些状态仅用于确认没有版本冲突，不构成发布动作。
