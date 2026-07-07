# chinese-official-writing 1.5.2 release evidence

## Scope

1.5.2 is a small prompt/reference release candidate based on GitHub `origin/main` plus the validated local proofreading and long-form test commits:

- `01cb9ee` adds the AI writing quality proofreading layer.
- `1faf56e` records proofreading regression tests and the fixed quote verification sentence behavior.
- `cc8e579` records 3000+ character long-form regression tests.

This release does not add scripts, hard cleaning, a new model, API usage, default internet search, or a new workflow gate.

## GitHub Main Baseline

- `git fetch origin`: succeeded.
- `origin/main`: `ee1127e708324fe197641d6ddded7cd15650bdee`.
- `HEAD` before version bump: `0` behind and `3` ahead of `origin/main`.
- Baseline worktree: `output/release-baselines/github-main-1.5.1`, detached at `ee1127e`.

`ee1127e` is a post-release documentation commit for 1.5.1 and does not change the skill behavior.

## Architecture Review

Architecture reviewer: `019f3a2c-db13-73e2-a42a-dc09dd4c4b63`.

Result: `WARN`, not blocking.

Findings:

- Progressive disclosure is still present. `SKILL.md`, `genre-playbooks.md`, and `final-review-layers.md` continue to say references should be loaded by task and not all at once.
- The entrypoint is long, but the current structure is still "long entry with route table", not "all references merged into the entry".
- Repeated rules around pending items, field-style materials, long writing, search boundaries, AI-style checks, and proofreading are mostly layered repetition, not conflicts.
- One small inconsistency was accepted: the quote verification sentence in `SKILL.md` was more absolute than `proofreading-checklist.md`, which already says the fixed sentence applies when a retained user quote has not been externally verified and the user has not supplied another wording.

Accepted minimal fix:

- In `chinese-official-writing/SKILL.md`, change the entrypoint wording from "最终稿保留用户给定引用时..." to "需要提示未核验引用时...".
- Keep the fixed sentence unchanged: `引用表述、出处和发布日期建议由用户按原始材料核实。`
- Leave detailed quote-handling rules in `references/proofreading-checklist.md`.

Rejected changes:

- No large reference reorganization.
- No script hard-cleaning.
- No new model/API/default internet workflow.
- No broader prompt rewrite based on single-sample observations.

## Real Subagent Writing Tests

Writer subagents:

- W1 writer: `019f3a2c-ef71-7ce2-96fc-701ffb4ff157`.
- W2 writer: `019f3a2c-f06f-7f33-9186-ca260d090641`.
- W3 writer: `019f3a2c-f177-7a32-874c-fbecebb54ebe`.
- Independent verifier: `019f3a30-bfb5-7aa1-8d96-a537ac7d582a`.

Coverage:

- 请示起草：缺主送机关、预算、施工日期、联系人、成文日期，不得编造。
- 通知起草：缺联系人、反馈邮箱，不得写泛占位。
- 平行函：商请公交集团临时加密班次，缺具体日期、客流数据、联系人。
- 字段式材料改写：只改“用途说明”，不得散文化。
- 只审不改：AI 味和空话套话定位，不得重写或打分。
- 引用保真：保留领导讲话/名言类引用，固定短句提示。
- 成语处理：明显不合语境时替换，合适成语保留。
- 数据冲突：320、315、330 不一致时不得自行取数。
- 新旧稿防回流：旧数字和旧建议不得回流。
- 回滚本次修改：恢复 7 月 12 日和联系人待补充，不保留 7 月 15 日或通报要求。
- 会议纪要：不得补“会议强调”。
- 讲话稿：不得编造成效、就业率或荣誉。
- 普通采购公告：不得误入 AI 算力。
- AI 算力可研摘要：Token 测算、SLA、安全、验收边界，不编造单价、供应商、预算和模型。
- 网页复制印发稿：只改附件办法条文，不改通知壳，不保留网页元信息。

Verifier result: `WARN`, not blocking.

- PASS: 11 samples.
- WARN: 4 samples.
- FAIL: 0 samples.
- No fact fabrication, genre mismatch, hard-boundary failure, field-style material breakage, review-only rewrite, or webpage attachment boundary failure was found.

Non-blocking observations:

- Formal element pending hints were incomplete in 2 samples: W1-C2 and W1-C3.
- A "校内指定地点" phrase in W3-C3 remained slightly placeholder-like.
- One sample had template-like wording quality risk in W2-C2.

Common issue threshold:

- No 3+ occurrence common issue was found.
- Therefore, no prompt fix was made for these writing samples.

## Targeted Quote Prompt Retest

Writer subagent: `019f3a33-395a-7c52-967b-415f91d7c196`.

Cases:

- `QFIX-1`: Retain user-provided quotes and, if a warning is needed, use the fixed sentence.
- `QFIX-2`: Retain the same quotes but obey the user's explicit instruction: "只输出正文，不附任何提示、说明或核实句".

Result:

- `QFIX-1` used `引用表述、出处和发布日期建议由用户按原始材料核实。`
- `QFIX-2` did not append any verification sentence.

This confirms the 1.5.2 wording does not force a quote warning when the user explicitly asks for body-only output.

## 3000+ Long-Form Subagent Tests

Long-form writer subagent: `019f3a33-395a-7c52-967b-415f91d7c196`.

Independent verifier subagent: `019f3a30-bfb5-7aa1-8d96-a537ac7d582a`.

Coverage:

- 3000+ 调研报告：`县域公共数据资源开发利用现状调研报告`，材料给调研主体、调研渠道和问题，但缺少目录总量、调用次数、开放数据集数量、应用收益等统计口径。
- 3000+ 可研报告：`基层政务服务大厅智能化改造项目可行性研究报告`，材料给建设内容，但资金金额、建设周期、运维责任和供应商均未确定。
- 3000+ 多附件合稿：通知壳、附件 1 工作方案、附件 2 任务分工表、附件 3 反馈表说明合并润色，要求保留通知壳和附件边界，不把附件内容揉进通知正文，不补造联系人和日期。

Writer output summary:

- 调研报告结构为调研背景和方式、当前工作基础、主要问题、原因分析、对策建议、待确认事项；未写具体数量、比例、排名或成效金额。
- 可研报告结构为项目概况、建设必要性、建设内容、可行性分析、实施与运维边界、风险控制、结论与建议、待确认事项；未编造投资金额、供应商、建设日期和运维单位。
- 多附件合稿结构为通知正文、附件清单、附件 1、附件 2、附件 3、待确认事项；附件 2 保持 `任务事项/主要内容/责任单位/配合单位/完成要求/备注` 字段行，未散文化。

Verifier result: `PASS`, not blocking.

- 调研报告：PASS。结构完整，缺少统计口径时未编造数据，使用 `从已给材料看` 等克制表述，并把统计口径放入待确认事项。
- 可研报告：PASS。未编造金额、供应商、日期和运维单位，资金、周期、接口、验收指标等列为正文外待补。
- 多附件合稿：PASS。通知壳、附件 1、附件 2、附件 3 边界清楚，字段式内容未散文化，未补联系人、电话、邮箱、反馈期限和成文日期。

Common issue threshold:

- No 3+ occurrence common issue was found.
- No prompt fix was made for these long-form samples.

Known limitation:

- The first writer report returned summaries and sampled passages instead of full 9000+ character outputs. A follow-up writer pass generated or retained the full samples in memory and returned exact counts without writing repository files.

Follow-up exact count pass:

- Count method: PowerShell in-memory variables; total characters by `.NET String.Length`; Chinese characters by CJK Han regex; the `3000+` threshold was judged by Chinese-character count.
- 调研报告：`3961` total characters, `3579` Chinese characters; Markdown marks `0`; placeholder tokens `0`; invented amount/supplier/date/phone/email `0`.
- 可研报告：`3970` total characters, `3554` Chinese characters; Markdown marks `0`; placeholder tokens `0`; invented amount/supplier/date/phone/email `0`.
- 多附件合稿：`4266` total characters, `3713` Chinese characters; Markdown marks `0`; placeholder tokens `0`; invented amount/supplier/date/phone/email `0`.

Verifier follow-up result: `PASS`, not blocking.

- The verifier judged that the exact count report removes the earlier estimate-only observation.
- Remaining limitation: the verifier did not receive the full text or original command output, so this is not an independent full-text recount by the verifier.

## Deterministic Verification

- `python .\tools\sync_adapters.py`
  - First sandbox run failed on `.agents` permission.
  - Escalated rerun succeeded.
- `python -B -m unittest tests.test_skill_boundary tests.test_review_regressions tests.test_real_prompt_ablation -v`
  - Result: PASS, `78` tests.
- `python -B -m unittest discover -s tests -v`
  - Result: PASS, `105` tests.
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-main-1.5.1 --baseline-label baseline-github-main-1.5.1 --current-root . --out .\output\real-prompt-vs-github-main-1.5.1-release-1.5.2-final`
  - Result: PASS.
  - Baseline `baseline-github-main-1.5.1`: `85` cases, `84` pass, `1` fail.
  - Current: `85` cases, `85` pass, `0` fail.
  - Baseline failure is the new P085 proofreading boundary check.
- `python .\tools\run_real_article_eval.py --out .\output\real-article-release-1.5.2-final`
  - Result: PASS for release regression use.
  - Skill mode: `0.00%` average missing-key-element rate, `100.00%` keyword coverage, `0` format risk, `0` repeat items, `0` anti-AI risk.
  - Existing placeholder-risk samples remain a manual/LLM judge signal.
- `npm run eval:official-writing:smoke`
  - Run with `PROMPTFOO_PYTHON=C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe` and elevated permissions.
  - Result: `20/20` passed, `0` failed, `0` errors.
  - Skill wins `10`, baseline wins `0`, invalid `0`, manual review `0`, judge consistency `1.0`.
- `git diff --check`
  - Result: PASS; only CRLF normalization warnings were printed.

## Remaining Risks

- Real subagent testing covered 15 short/medium samples plus 3 long-form 3000+ samples, but not every possible public-sector document variant.
- The 3000+ samples were generated and counted in a subagent context, but not saved as full text in this repository. Future release tests should store full long-form samples under `output/` for independent recount and lint scanning.
- Formal element hinting for notices and letters should continue to be observed; current evidence shows only 2 WARN samples, below the 3+ fix threshold.
- Real article eval remains deterministic and does not replace human review or live drafting judgement.
- This release does not add external fact checking; quote and data authenticity remain user/public-source verification responsibilities.
