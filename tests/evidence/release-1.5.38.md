# 1.5.38 本地候选验证记录

## 当前状态

1.5.38 已合并到本地 `main` 等价分支并完成版本面同步，尚未推送、打 tag 或发布到 GitHub、ClawHub、skillhub.cn。候选分支为 opencode 工作区独立 worktree `release-1.5.38`（基于 GitHub `origin/main`），固定发布基线为 `v1.5.37=5d166a8d671fcb0bd96e66aec8e944ccbdf3c0d4`。

## 本轮改动

- 删除入口中的五个关键名词示例（“反馈渠道”“联系人”“原因分析”“问题清单”“每周反馈”），保留“用户给出的关键名词和结构标签一般保留原词，不能只用泛化近义词带过”承重规则；示例在 `references/workflow.md` 与复核清单中仍有承载。
- 将“命中 `references/task-route-cards.md` 且卡片能够覆盖任务时，在轻量卡早停”改为“由卡片完成，不再读取长 reference”，路由条件不变。
- canonical、Codex、Claude Code、Qwen、Hermes、OpenClaw 镜像及展示元数据统一到 1.5.38。
- 不改变文种路由、reference 加载条件、篇幅规则、输出模式、复核顺序、脚本、Hook 或回退方式。

## 基线与提交

- 固定 1.5.37 产品基线：`5d166a8d671fcb0bd96e66aec8e944ccbdf3c0d4`（GitHub annotated tag `v1.5.37` 解引用提交）。
- 已合并入口清晰化两项原子：`370a2bfd`（关键名词示例压缩）、`84292368`（轻量卡加载边界显式化）；整合证据：`317fdff0`。
- 版本面同步：`a2e8ac050035dc6be5315b7ad5ca6ce65ae5ea6c`。

## 合并后验证（2026-08-07，opencode 工作区实跑）

| 验证 | 实际结果 |
| --- | --- |
| `python -m unittest discover -s tests` | 442/442，通过 |
| `npm run eval:official-writing:smoke`（OFFICIAL_WRITING_EVAL_STUB=1） | 20/20，通过；0 failed、0 errors |
| 固定 1.5.37 确定性消融（`tools/run_real_prompt_ablation.py`，基线 worktree 为 `v1.5.37` detached） | v1.5.37 111/111；current 111/111 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py` 通过 |
| `python tools/sync_adapters.py` | 重复执行后无语义差异，镜像同步幂等 |
| `git diff --check` | 通过 |

## 真实写稿 + 独立盲审（对固定 1.5.37）

口径（用户 2026-08-07 定义）：不劣于已发布基线即可发布；“不劣于”= 不存在由本轮 diff 改动造成的质量回退，写作本身波动不算。

三题覆盖本轮 diff 直接交互边界与旧能力回归：T1 稀疏材料轻量卡情况说明（200 字内、禁补固定章节）；T2 关键名词保留改稿（五个指定名词原词保留 + 第三部分后加自然段、不加小标题）；T3 请示起草回归（缺主送/单位/金额/日期不得编造）。writer 为独立子代理，分别加载固定 1.5.37 基线与 1.5.38 候选；独立 verifier 只看“原 prompt + 匿名稿”，不知版本映射。

| 任务 | 基线 1.5.37 | 候选 1.5.38 | 盲审结论 |
| --- | --- | --- | --- |
| T1 轻量卡 | WARN（缺标题） | PASS | 候选略优；两臂均只读轻量卡与信息选择规则，未加载长 reference |
| T2 关键名词 | PASS（尾轮有“特此通知”） | WARN（缺结尾语） | 五个关键名词两臂两轮均 2/2 原词保留；结尾语有无在两轮间双向抖动，判波动 |
| T3 请示回归 | PASS | WARN（首轮补写“设备老化、性能下降”等未给背景） | 同题两次定向复现候选均未再编造（0/2 复现），基线 3/3 干净；该任务不命中本轮任一改动子句，判写作波动 |

结论：未见由本轮 diff 造成的质量回退，满足“不劣于”发布口径。writer/verifier 均由 opencode 子代理执行（模型 qwen3.8-max），本轮未使用其他模型档位。

## 发布边界

本记录只证明本地 1.5.38 候选可供后续发布决策使用。当前没有 GitHub 推送或 Release、ClawHub 上传、skillhub.cn 上传及公开传播回执。小红书 Red SkillHub 按 2026-07-13 决定继续排除。
