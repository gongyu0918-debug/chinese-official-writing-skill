# 材料旁白版本追溯、拆分因果与独立净稿 A/B

日期：2026-07-10

## 结论

本轮没有形成可发布的 `1.5.6` 候选。真实写稿中出现一次材料读取状态、起草过程说明、代理自证或无关外语残片即视为发布阻断，不等待三次共性。

- `v1.5.2` 已能复现材料旁白，因此该问题不是 `v1.5.3` 以后才出现。
- `v1.5.2` 至 `v1.5.5` 没有发生 canonical Markdown 缩短；总量持续增加。`v1.5.5` 对 `workflow.md` 的改动是把一段拆成短 bullet，不是删除规则。
- 受控拆分消融的方向不一致，不能证明 `workflow.md` 拆段导致旁白增加。
- 父级 agent 明确编排第二个 cleaner agent 时，6 篇样稿均可把旁白命中降为 0，且两名 verifier 均确认事实和结构保真。
- 把“按需调用独立 cleaner”写进 canonical skill 后，真实 writer 没有实际调用子代理；候选的旁白密度反而高于本轮起点，并出现一处 `拟先` 变为 `考虑先` 的状态语气漂移。两名独立 verifier 均判定基线和候选为发布阻断。
- 该产品候选已完整回滚，只保留本报告和 `AGENTS.md` 接手记录。当前版本仍为 `1.5.5`，未创建 tag，未推送或发布。

## 固定基线

| 基线 | commit | 本地只读 worktree |
| --- | --- | --- |
| `v1.5.2` | `70efc9ce74fe956497b5044ee14f60e2b94c5e55` | `output/release-baselines/github-1.5.2` |
| `v1.5.3` | `b4535b9f` | `output/release-baselines/github-1.5.3` |
| `v1.5.4` | `20776d4a` | `output/release-baselines/github-1.5.4` |
| `v1.5.5` | `dd4c6d66` | `output/release-baselines/github-1.5.5` |
| 本轮起点 | `476d1c55c5e4f1177a37e01effb3ab7a672e97f4` | `output/release-baselines/local-pre-cleaner-476d1c5` |

## Markdown 结构追溯

| 版本 | Markdown 文件数 | Markdown 字符数 | `SKILL.md` 行/字符 | `workflow.md` 行/字符 |
| --- | ---: | ---: | ---: | ---: |
| `1.5.2` | 15 | 56,326 | 162 / 9,667 | 153 / 6,814 |
| `1.5.3` | 15 | 61,390 | 169 / 11,402 | 159 / 8,241 |
| `1.5.4` | 16 | 62,491 | 170 / 11,556 | 159 / 8,241 |
| `1.5.5` | 16 | 62,671 | 170 / 11,556 | 178 / 8,315 |
| 本轮起点 | 16 | 63,306 | 173 / 11,727 | 178 / 8,431 |

`v1.5.3` 增加了较多事实边界和材料视角表达，确定性短语命中由 15 增至 30；这只能说明潜在提示暴露增加，不能单独证明它导致模型输出旁白。`v1.5.4` 新增 `task-route-cards.md`。`v1.5.5` 的 `8b645a2` 将 `workflow.md` 一段拆成 18 个 bullet，语义大体保留；`42e7b08` 增加 800 字以上和复杂任务的路由升级条件。

## 五版本真实写稿 A/B

统一使用 `gpt-5.6-luna`、medium，覆盖：600 至 800 字稀疏材料报告、900 至 1100 字调研报告、3000 至 3500 字多附件可研，以及含逐字引语和 `拟` 状态的正式化改写。下表是对正式正文的自动预扫描，最终阻断判断由独立 verifier 作出。

| 版本 | 旁白短语命中 | 样稿字符数 | 每千字命中 |
| --- | ---: | ---: | ---: |
| `v1.5.2` | 25 | 6,934 | 3.61 |
| `v1.5.3` | 25 | 5,818 | 4.30 |
| `v1.5.4` | 39 | 7,976 | 4.89 |
| `v1.5.5` | 44 | 7,393 | 5.95 |
| 本轮起点 | 12 | 5,598 | 2.14 |

这些样稿分别生成，能说明各版本都可复现，不能把密度差直接解释为版本因果。`v1.5.2` 已出现“现有材料”“由于材料”“本报告仅依据”等旁白；本轮起点相对 `v1.5.5` 有改善，但按一次即阻断口径仍不合格。

writer subagent：

- `v1.5.2`：`019f4a4e-b6a7-75c0-8f9f-27459909fead`
- `v1.5.3`：`019f4a4e-cae3-7de3-81bd-6c3437d78cb8`
- `v1.5.4`：`019f4a4e-dfa6-7692-992f-3d88628bb5de`
- `v1.5.5`：`019f4a51-aae6-7280-8afa-48bb78812025`
- 本轮起点：`019f4a51-bf3a-7572-a797-cdb0951af0e0`

首轮盲审 verifier：`019f4a54-73f1-7541-ab93-03a7caadad2f`、`019f4a54-884b-7811-9230-22fc842404d3`。两名 verifier 都认为本轮起点在五组中相对较好，但没有一组达到一次即阻断标准。

## `workflow.md` 拆分因果消融

临时候选只交换 `workflow.md`，不改其他文件：

- `v1.5.4-plus-split`：`v1.5.4` 包加上 `v1.5.5` 的拆分版 workflow。
- `v1.5.5-unsplit`：`v1.5.5` 包换回 `v1.5.4` 的未拆分 workflow。

| 对照 | 每千字旁白命中 |
| --- | ---: |
| `v1.5.4` 原版 | 4.89 |
| `v1.5.4` 加拆分 | 3.84 |
| `v1.5.5` 原版 | 5.95 |
| `v1.5.5` 换回未拆分 | 5.34 |

两个方向都略降，但样稿同时发生篇幅、事实和数学表达变化，独立 verifier 不认为这构成拆分因果证据。加拆分组减少部分旁白但出现轻微事实范围问题；换回未拆分组仍补造会议内容，并把“2 人兼顾其他系统”写成“运维力量不足”。因此不回滚 `v1.5.5` 的 workflow 拆段。

拆分消融 writer：`019f4a55-28ec-7030-b55a-bc3d91952b2f`、`019f4a55-3df5-7733-90b6-c5dcc59ca773`。

## 最小方案实验

### 1. 中性化材料视角措辞

临时候选只改 15 行 prompt/reference，把“材料未”“从已给材料看”等改成业务对象状态表达，不新增禁令。确定性短语命中由 30 降至 10。holdout 中，本轮起点为 17 次、每千字 3.15，候选为 9 次、每千字 1.81；但候选三篇正式稿仍出现“不能据此”“现阶段只能”等旁白。按一次即阻断口径失败，未合并。

### 2. 父级显式编排双 agent 清稿

父级把“原 prompt + 完整首稿”交给第二个 cleaner agent，只要求输出净稿，不传首个 writer 的内部推理或自评。两轮共 6 篇：

- 第一轮 3 篇：清稿前 12 次，清稿后 0 次。
- 第二轮 3 篇：清稿前 17 次，清稿后 0 次。
- 两名独立 verifier 均判定数字、事实、引语、结构和篇幅保真，6 篇通过。

这证明“真实第二 agent 清稿”在父级明确编排时有效，但不证明 canonical skill 能自行保证子代理调用。

### 3. canonical 内按需 cleaner 路由

临时候选增加 `references/final-draft-cleaner.md`，并在 `SKILL.md` 约定 800 字以上、多材料合稿或发现一次旁白时调用独立子代理。直接 post-fix A/B 使用同一组 S1 至 S4：3000 至 3400 字应急平台可研、500 至 700 字档案试点报告、含引语和 `拟` 的正式化改写、只审不改。

| 组别 | S1+S2 字符数 | 旁白命中 | 每千字命中 | 实际调用 cleaner 子代理 |
| --- | ---: | ---: | ---: | --- |
| 本轮起点 `476d1c5` | 3,916 | 7 | 1.79 | 不适用 |
| canonical cleaner 候选 | 3,709 | 8 | 2.16 | 否 |

候选 writer 在事后可观察执行信息中明确回答“未调用”。候选 S1/S2 仍有“不能据此判定”“现阶段只能确认”“不延伸为”“不据此形成”“不作对应”等旁白，并把 S3 的“项目组拟先”改为“项目组考虑先”。

两名 blind verifier 对哪一组相对更好意见不同：一名认为起点保留 `拟` 更好，另一名认为候选篇幅和 S2 事实更完整；但二者都判定两组 `release_blocker=true`，候选不可采用。这一一致结论足以触发回滚。

post-fix writer：`019f4a4e-b6a7-75c0-8f9f-27459909fead`、`019f4a4e-cae3-7de3-81bd-6c3437d78cb8`。post-fix verifier：`019f4a54-73f1-7541-ab93-03a7caadad2f`、`019f4a54-884b-7811-9230-22fc842404d3`。

## 回滚范围

以下临时产品改动均已删除，并重新运行 `tools/sync_adapters.py` 同步镜像：

- canonical 与全部镜像中的 `references/final-draft-cleaner.md`。
- `SKILL.md` 的 cleaner 路由和参考表入口。
- OpenClaw 精简入口的 cleaner 路由。
- `tests/test_skill_boundary.py` 的临时候选断言。
- `tools/run_real_prompt_ablation.py` 的临时 P102。

未改 `prose_lint.py`，未引入硬清洗、模型、API、默认联网或发布阻断脚本。

## 回滚后验证

| 命令 | 结果 |
| --- | --- |
| `python -B tools/sync_adapters.py` | 通过，canonical 与各镜像同步 |
| `python -B -m unittest tests.test_skill_boundary tests.test_review_regressions tests.test_real_prompt_ablation -v` | `86/86` 通过 |
| `python -B -m unittest discover -s tests -v` | `121/121` 通过 |
| `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/local-pre-cleaner-476d1c5 ...` | baseline `101/101`，current `101/101` |
| `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.5 ...` | baseline `95/101`，current `101/101`；baseline 只在后续新增确定性用例失败 |
| `npm run eval:official-writing:smoke` | 沙箱内首次因 Node 不能启动已存在的 bundled Python 而出现 20 个环境错误；沙箱外用同一命令重跑 `20/20` 通过，0 error，judge consistency `1.0` |

确定性测试和 Promptfoo smoke 不调用本轮真实 Luna 写稿链路，不能代替真实样稿阻断结论。

## 剩余风险与后续方向

1. 用户此前实际使用未见旁白，与本轮结论不矛盾。该问题是随机性和长文/稀疏事实场景相关风险，并非每稿必现；`v1.5.2` 也能复现。
2. `v1.5.3` 的材料视角短语增加可能构成提示诱导，但中性化实验仍失败，目前没有足够因果证据支持大范围改写这些 reference。
3. generic skill 不能保证宿主允许或实际执行子代理。有效的双 agent 方案应由父级 orchestrator 明确调用并核验，不应仅靠 canonical Markdown 声明。
4. 若继续产品化双 agent 清稿，应先做平台能力探测和显式调用回执，再与 `v1.5.5`、本轮起点做多随机种子 A/B；任何一次旁白、外语残片、引语变化、`拟/将` 状态漂移或事实变化都应回滚。
5. 在找到可移植、可验证的调用机制前，保持 `1.5.5` 不发布新版本，不继续向 `SKILL.md` 或事实边界 reference 叠加同义禁令。
