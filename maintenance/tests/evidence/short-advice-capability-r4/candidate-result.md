# WR-026-R4 短意见正文能力候选结果

日期：2026-09-02。

固定候选：`codex/wr026-short-advice-r4@011d3e4c`。候选只在 `references/genre-playbook-advisory-feedback.md` 的“结构与版式”增加一条短意见正文组合规则；真实写稿时未改 `SKILL.md`、通用短稿页、description、Hook、版本或其他文种叶。

## 技术状态

| provider | Codex task | 状态 | 有效稿 |
| --- | --- | --- | --- |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 | `01a06149-f7be-7d33-843f-de3d862f6310` | 完成 | 5 |
| Alibaba Token Plan / DeepSeek V4 Flash 0731 | `01a06149-fbcd-7661-8d0d-33f2d0068ea5` | 完成 | 5 |
| Ollama Cloud / DeepSeek V4 Flash 0731 | `01a06149-ff6b-7352-923c-6d05501c318d` | 502 | 0（技术无效） |
| Ollama Cloud / GLM 5.3 Flash（同 provider 回退） | `01a0614d-4661-74c2-ad78-823e16eddc0e` | 同一 502；按用户要求本轮停止重试 | 0（技术无效） |
| OpenCode Go / DeepSeek V4 Flash | `01a0614a-038d-7261-bd75-8cfc70c49379` | 完成 | 5 |
| MiniMax / MiniMax M3 | `01a0614a-07c8-78a2-88e0-773e0d3bc3b4` | 完成 | 5 |

当前共 20 份有效候选稿。Ollama 两个模型均返回 `Provider unreachable: ollama-native orphan tool result <missing-id>`，目标地址为 `http://127.0.0.1:10100/v1/responses`；该 provider 本轮不再重试，不计质量。

在用户指出 OpenCodex 2.39.0 `ollama-native` 的同 `call_id` 前置消息要求后，另请求 Baseline 与 Candidate 两个全新干净任务，分别只返回 `client-new-thread:1b8ed8ca-0cbf-4a8b-bcec-1248a82eddcf` 与 `client-new-thread:85c81029-8c13-42d9-9a69-d85664446563`，随后未形成可列出的 Codex task或正文。有限重试至此停止；因未跑通，不把该诊断写成通用测试规则。

## 正向题

四家有效 provider 的平台建议栏、反馈邮件和独立成文短意见共 12 份，均可直接用于指定载体：

- 均保留给定事实或第一方经历，写出由材料直接支持的影响或判断，并把审核口径与平台字段、功能分别交给审核部门和平台运营方；
- 均保持“研究”“尚未决定”等未决强度，没有把建议写成被建议方已经作出的决定；
- 平台栏和邮件正文未机械重复完整题名、建议方和日期；独立成文稿保留题名、建议方与给定日期；
- `便于核对`、`减少重复上传`、`影响核对效率`等属于材料直接支持的一层作用或判断，按预登记不记为外扩。

MiniMax 基线的平台栏和邮件稿采用编号式问题段，候选改为紧凑连续正文并保留实质关系，显示新增组合规则可被真实读取。Alibaba 两路与 OpenCode 的基线本已可用，候选保持其能力；本轮不把“基线必须失败”或“候选逐项文采胜出”作为新增功能的必要条件。

## 控制题

- 四家正式长意见均保留题名、建议方、日期、两类处置权限和全部给定事实。部分候选比同 provider 基线少设层级，但没有压成短意见，仍是可直接使用的完整长意见，不以标题数量差异判失败。
- 四家短通知均保持已决定状态、执行对象和责任关系，没有把建议语气串入通知。
- MiniMax 的长意见补入集团授权、付款证明、服务关系、断点续传和外链附件等材料外具体例子，通知补入未给出的“本群”。其基线已有同类具体化倾向，其他 provider 未复现，且本轮改动只作用于意见建议专叶；因此记为 provider 残余风险，不记候选共性回退，也不据此增写泛化禁令。

## 结论

`R4_REAL_WRITING_PASSED / ENGINEERING_VERIFIED / NEXT_VERSION_CANDIDATE / MERGE_NOT_AUTHORIZED`

四家有效 provider 共 20 份候选稿，正向题 12/12 可直接使用；至少两家实际读取目标叶并稳定呈现“依据或实际情形—直接影响或判断—有权对象的具体建议”的新增组合。控制题没有跨 provider 的候选相关事实、状态、权限、文种或交付形态硬回退。候选因此进入直接工程门，但不等于已合入 `main`、已进入冻结 v1.6.25 或已发布。

本结论不掩盖两项剩余风险：Ollama provider 本轮没有有效样本；MiniMax 对材料外具体措施和例子的既有倾向仍需在后续出现新反例时单独处理。

## 直接工程门

- `python -m unittest maintenance.tests.test_advisory_feedback_leaf maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability`：108项通过。
- Skill Creator `quick_validate.py`：canonical、Agent Skills、Qwen Code、QwenWork、Hermes 五处通过；OpenClaw 镜像因宿主合法扩展字段 `category` 被通用校验器拒绝，不能记为通用校验通过。OpenClaw 的 frontmatter、无Hook包边界和镜像字节一致性由仓库 `test_skill_boundary` 与 `test_advisory_feedback_leaf` 专项断言通过。
- `python maintenance/tools/sync_adapters.py`：五套持久镜像同步；再次运行未产生新的产品差异。
- `git diff --check`：通过。

工程门只锁定已由真实稿验证的专叶文本、载体关系、镜像与状态索引，不反向改变写稿准入结论。
