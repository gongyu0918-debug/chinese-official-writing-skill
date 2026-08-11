# 1.5.37 发布证据

## 当前状态

1.5.37 已完成 GitHub、ClawHub 和 skillhub.cn 各一次正式提交。GitHub `main`、annotated tag `v1.5.37` 和正式 Release 的产品提交均为 `5d166a8d671fcb0bd96e66aec8e944ccbdf3c0d4`；发布回执记录作为后续文档提交推进 `main`，不移动发布 tag。ClawHub 与 skillhub.cn 的公开详情仍处于异步传播阶段，不重复提交。

## 本轮改动

- anti-AI 复核文件不再重复展开只审输出契约，改为指向统一规则源；写作边界、文种路由和复核顺序保持不变。
- `prose_lint.py` 收紧三类已复现误报：合法否定指令、编号式“补充信息”正文和中文相邻 `XX` 占位重复报告；高置信风险召回继续保留。
- canonical、Codex、Claude Code、Qwen、Hermes、OpenClaw 镜像及展示元数据统一到 1.5.37。

## 基线与提交

- 固定 1.5.36 产品基线：`8bd4eb8c8b4f233445e07ebf4d3f54ceb5777aa2`。
- anti-AI 契约去重：`ef68ec49`。
- lint 误报修复：`ddd86de4`。
- 组合结果记录：`d0aed66a`。
- 合并本地 `main`：`6488dc13`。
- 版本面同步：`c65d0af3`。

## 合并后验证

| 验证 | 实际结果 |
| --- | --- |
| `python -m unittest discover -s tests` | 442/442，通过 |
| `npm run eval:official-writing:smoke` | 20/20，通过；0 failed、0 errors |
| 固定 1.5.36 确定性消融 | baseline 111/111；current 111/111 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py` 通过 |
| `python tools/sync_adapters.py` | 重复执行后无语义差异，镜像同步幂等 |
| `git diff --check` | 通过 |

组合分支此前完成两题 `gpt-5.6-terra`、`high` 真实写稿与独立匿名盲审：相对固定 1.5.36 为 2 胜 0 负，全部稿件的事实、数字、主体、状态和输出模式通过硬检查。详细原始结果见 `1.5.37-integration-anti-ai-lint-result-20260805.md`。

发布当日重新运行上述工程门：单元测试仍为 442/442，Promptfoo stub smoke 为 20/20，固定 1.5.36 消融两边仍为 111/111；quick validate、脚本编译和 `git diff --check` 均通过。

## 发行包

### ClawHub

- 发行目录：`openclaw/skills/chinese_official_writing/`；
- 文件数：32；
- dry-run：`status=would-publish`，公开基线 1.5.36，目标版本 1.5.37；
- fingerprint：`456325f574d5e6f71f8cf0decee7cea89f480f0f9a06bf7a0cb8a4e98fdffb19`。

### skillhub.cn

- 清洁包：`output/skillhub-release-1.5.37-20260806/publish-package/`；
- 文件数：31，禁入文件 0，共享内容哈希不一致 0；
- 排除 `agents/openai.yaml`、`delivery-review-gate.md`、`gate_stop_hook.py`、`review_gate.py`，加入平台 `_meta.json` 和 SkillHub 专用 frontmatter；
- 排序清单 SHA-256：`6a50e512f3d4df3db1674990a7e3511b1774f1720dbb49e60d5ad172350bf156`；
- dry-run：精确返回 `chinese-official-writing@1.5.37`。

## 剩余风险

1. 真实组合回归为两题，能够验证本轮两项直接交互，不能据此宣称所有文种的统计性提升。
2. writer 自然调用 lint 时仍可能采用 generic 参数；本轮修复检测精度，没有改变调用模式。
3. lint 继续只提供定位线索，不自动改稿；材料原文、合法否定和保护性外扩的最终取舍仍由 Agent 结合语义完成。

## 实际发布与回执

- GitHub：`origin/main` 已包含产品提交；annotated tag `v1.5.37` 的 tag object 为 `31e336eba6e5dc086ba358e197ef55ab8995ea70`，解引用提交为 `5d166a8d671fcb0bd96e66aec8e944ccbdf3c0d4`。正式 Release 已公开：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.37`。
- ClawHub：正式提交只执行一次，回执为 `status=published`、`versionId=k978my6g22dwz97kmesexjs9a98byrvg`、32 个文件、fingerprint `456325f574d5e6f71f8cf0decee7cea89f480f0f9a06bf7a0cb8a4e98fdffb19`。首次只读查询仍显示公开 `latestVersion=1.5.36`、`tags.latest=1.5.36`，精确查询 1.5.37 返回传播期 `Version not found`；当前 moderation `clean` 对应仍公开的 1.5.36，不推断为 1.5.37 已完成扫描。
- skillhub.cn：正式提交只执行一次，回执为 `ok=true`、`skillId=70149`、`versionId=199757`、31 个文件、fingerprint `c4906d1c8e2fb44138537f764b09777649b67dd03564ee718f277fad437914fa`、`tags.latest=1.5.37`；提交回执中的 review、security scan 和 content audit 均为 `pending`。首次公开查询已显示 `tags.latest=1.5.37`，正文详情仍为 `latestVersion=1.5.36`；公开 benign 报告对应当前已传播版本，不写成 1.5.37 审核结论。
- 小红书 Red SkillHub 未调用。
