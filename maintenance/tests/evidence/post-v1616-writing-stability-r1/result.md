# v1.6.16 后写稿稳定性三个原子结果

日期：2026-08-26。

## 结论

`NO_COMMON_TARGET_FAILURE / NO_PRODUCT_CHANGE / WAIT_NEW_COUNTEREXAMPLE`。

本轮以 `main@6d7fc0ec8f1227638652527670f251eba9d76f86` 为固定公开基线，按预登记分别测试 `WR-014-R6/R6b`、`WR-013c`、`WR-020a2`。7份技术有效终稿中：

- `WR-014-R6` 原目标2/2通过，两家都没有把明确未开展项包入“继续处理”；两家共同出现的“记录未附→尚未核验/结果待确认”没有事后并入原准入，而是另换材料预登记为 `R6b`。
- `WR-014-R6b` 为1/2目标通过：OpenCode保持“修复已完成”和“报告未附”两个维度，Ollama又增加“相关核验……有待后续落实后明确”。只有单家复现，不达到两家共同失败的候选启动条件。
- `WR-013c` 目标2/2通过：两稿均把高峰利用率、排队数量和等待时间写成采购原因，允许“缓解、缩短、提升”等目的或低强度预期，没有升级成已经延期、中断、不稳定或业务无法开展。
- `WR-020a2` 只有OpenCode形成有效终稿并通过目标：固定五节完整，标题正文2326个非空白字符，后半篇有路径、条件和风险论证；两次事件中的未丢失、未中断始终绑定两次事件，没有扩大为平台整体安全稳定结论。Ollama首跑30分钟无终稿，唯一技术重试又在15分钟内反复重算字数且无终稿，两次均为 `TECHNICAL_INVALID`，不计质量票。

四个原子均未形成跨模型共同目标失败，不制作 Candidate，不修改 `SKILL.md`、references、description、Hook、adapter 或 packages，不运行空 Hook 生命周期和昂贵冷审。没有留下 `HOLD`。

## 真实写稿结果

两个隔离 runtime 的 `SKILL.md` 与 canonical SHA-256 均为 `4B17EC03F3D04E84F83DAB4E15A99E9EE386827A194FB7141F2A6080275E03E3`。写稿通过 Codex CLI 0.144.6 直连用户指定便宜 provider，均为 `max`；Hook关闭，模型只读隔离 runtime 内当前 Skill 和实际路由 reference。

| 原子 | provider | final SHA-256 | 目标判定 | 全文判定 |
| --- | --- | --- | --- | --- |
| `WR-014-R6` | OpenCode Go DeepSeek V4 Flash | `D6B04E695BC28E802DD95DD9DDFCB9A514379207FDD869762967038A936AA531` | `PASS_TARGET` | `HARD_FAIL_EVIDENCE_STATE`：把记录未附改成尚未获得核验确认；另有“目前没有作出处理安排”的范围观察 |
| `WR-014-R6` | Ollama DeepSeek V4 Flash 0731 | `479A317B3A8DD5515EFE95160E238FC56C9EEA30F2E800FA557987ABE2BCB128` | `PASS_TARGET` | `HARD_FAIL_EVIDENCE_STATE_AND_OUTPUT_SHAPE`：结果待确认、需另行说明，并附字数和过程说明 |
| `WR-014-R6b` | OpenCode Go DeepSeek V4 Flash | `F57CC272B9A79DD92D5F2CD246D3EE24EE57713FFBDF2BDA2896013D4D1F5CA8` | `PASS_TARGET` | `HARD_FAIL_OUTPUT_SHAPE`：正文状态正确，但正文前附过程和计数说明 |
| `WR-014-R6b` | Ollama DeepSeek V4 Flash 0731 | `31689F65A5B21FE204818D63DEE5A19409F18557ED37FD702BE157D182C07DB9` | `FAIL_TARGET` | `HARD_FAIL_STATE_AND_OUTPUT_SHAPE`：完成状态仍在，但把核验写成待后续落实，并附过程说明 |
| `WR-013c` | OpenCode Go DeepSeek V4 Flash | `4E53AD05019AF88C63639BA88FCF9B6D1E470BA429D58C765D9D89B6061ED7AB` | `PASS_TARGET` | `HARD_FAIL_OUTPUT_SHAPE`：正文可用，前后附过程、自评和Markdown横线 |
| `WR-013c` | Ollama DeepSeek V4 Flash 0731 | `0CA4D964975CA5609E74AFBB14C96057EC47B6B14A6B140F3ABB98CAC6D94499` | `PASS_TARGET` | `HARD_FAIL_OUTPUT_SHAPE`：正文可用，前后附过程说明和Markdown横线 |
| `WR-020a2` | OpenCode Go DeepSeek V4 Flash | `4558E34F94CBD302BDA86BEA541B9FAE5B34BB78DE694CA3B453FB21125A34E9` | `PASS_TARGET` | `HARD_FAIL_OUTPUT_SHAPE`：正文后附字数与过程说明 |
| `WR-020a2` | Ollama DeepSeek V4 Flash 0731 | 无终稿 | `TECHNICAL_INVALID_X2` | 首跑约30分钟无终稿；唯一重试15分钟仍在字数循环，终止时没有 `-o` 文件，不作质量判定 |

表中“目标判定”只回答预登记原子，不遮蔽全文硬失败。合理原因、基于当前排队的条件风险、费用结构判断以及“未批准预算等条件下不具备启动实施条件”均有直接材料支点，没有按过严标准判错。

## 官方稿校准

- 上海专项经费说明和重庆转载报道均把“继续”绑定已经开展的同一动作，并把尚未开展的项目分开，支持本轮对持续动作和一般职责的区分。
- 北京大学GPU节点采购公示从用户争用直接形成资源紧张与补充服务器的必要性，支持 `WR-013c` 的一层原因和低强度预期；它不支持在没有延期、中断数据时再扩大既成影响。
- 温州市教育局部门决算所附绩效复评表在同一事项中并列“已完成验收”和“未附采购验收单”，支持业务动作状态与当前附件状态分开承载。
- 上海政务外网绩效评价报告把未中断、未发生安全事故绑定到具体期间、活动和维护范围，支持 `WR-020a2` 不把两次事件扩大成平台整体结论。

来源只用于校准状态、因果和结论范围，不复制文字、模板或代码；详见 [`research.md`](research.md)。

## 交付洁净度观察

7份有效终稿中6份违反“只写标题和正文”，出现过程说明、自评、字数回执或Markdown横线。唯一没有包装的 `R6` OpenCode 稿又存在证据状态外推，因此不能把本轮概括为“7份全文通过”。

该问题不是新发现的未实现能力：当前产品已经在主入口、终审页和短稿叶明确正文交付边界，`CL-001 delivery_cleanliness` 也已有三provider真实整理及多宿主D1/hash证据。本轮预登记排除了Hook，且没有改动交付协议或adapter，因此不重复运行CL-001，也不靠继续叠加相同提示语制造候选。无Hook直写仍存在provider服从性风险，保留为已知残余。

## Ollama 技术风险

`WR-020a2` 首跑和唯一重试都没有形成可冻结终稿。重试从2026-08-26 01:02:04运行至约01:17:12，期间反复生成、计算和改写同一长稿；终止前模型还发现自己曾把局部事件扩大成“平台整体运行保持稳定”并准备再次修正，但没有完成最终交付，因此内部草稿不计质量结果。精确token用量无法从被终止调用取得，不作估算。

`WR-014-R6b` 的Ollama有效调用返回 `input_tokens=212832`、`output_tokens=5897`，也显示max模式下为满足精确字符区间会产生高额反复计数。该事实只用于后续安排provider和题面，不修改本轮质量标准，也不把技术消耗冒充写作质量。

## 状态收口

- `WR-014-R6`：`TERMINATED_BASELINE_TARGET_NOT_REPRODUCED`。
- `WR-014-R6b`：`ONE_PROVIDER_TARGET_RISK / WAIT_NEW_COUNTEREXAMPLE`。
- `WR-013c`：`BASELINE_TARGET_PASS / NO_PRODUCT_CHANGE`。
- `WR-020a2`：`ONE_VALID_TARGET_PASS_ONE_PROVIDER_TECHNICAL_INVALID / WAIT_NEW_COUNTEREXAMPLE`。
- 产品差异：0文件、0字节。
- 付费提纲、红头DOCX和发布面：未触碰。

## 实际命令与边界

- `git worktree add -b codex/post-v1616-writing-stability-r1 ... main`
- `git cherry-pick 5fd48f99... 5b99bf85...`，恢复旧 `WR-021` 可达证据后再开展本轮原子。
- `codex exec --ignore-user-config --ignore-rules --ephemeral --json --color never --sandbox read-only -m <provider/model> -c openai_base_url=... -c model_catalog_json=... -c model_reasoning_effort=max -o <final> -C <isolated-runtime> -- <prompt>`
- `Get-FileHash -Algorithm SHA256 <final>` 与非空白字符/汉字计数；原始终稿保存在git忽略的 `output/post-v1616-writing-stability-r1/`。
- 官方检索：`site:gov.cn` 的持续动作、资源紧张采购、局部未发生及“已完成/未附佐证”定向查询；实际采用来源和用途见 `research.md`。
- 没有使用Grok、SOL、Kimi或Qwen承担普通写稿；没有电脑控制，没有push、tag、上传或发布。

最终规格测试、链接检查、quick validate、baseline diff、轻量消融、独立冷审与清洁状态见 [`five-commit-review.md`](five-commit-review.md)。
