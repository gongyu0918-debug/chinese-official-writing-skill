# OC-003-R3 可研完整性审稿与渐进路由结果

日期：2026-08-25。

## 结论

候选阶段结论为 `VALIDATED_INTEGRATION_CANDIDATE / READY_FOR_LOCAL_MAIN_MERGE / NOT_RELEASED`；已于本地 `main@68eaf5ba` 非快进合并，当前为 `DONE_LOCAL_MAIN_NOT_RELEASED`。

候选解决两个相连问题：只审既有可研摘要、且用户已点名完整性核对项时，不再自动加载整份 AI 算力起草选项库；审稿意见仍可核算数据、说明缺项影响，并按点名维度列出指标、费用和依据类别。限制对象是材料外的厂商数量、比较路径、数值阈值、实际责任主体、合同义务、既定程序和未点名审查域，不限制由给定事实、任务目的和文种功能直接支持的原因、影响、结论与论证。

最终候选在 OpenCode Go、Ollama、Alibaba Token Plan 1、Alibaba Token Plan 2、MiniMax 五个便宜 provider 的真实审稿中均只实际读取入口与可研细查叶，5/5 保留算术、数据性质、未决状态和四项点名缺口，未新增材料外事实、固定数值阈值或既定办理安排。各稿存在不同程度的指标类别、费用构成、抽样依据或候选主体类别展开，但均以待材料明确或条件态表达，属于可研审稿的合理分析，只记范围提示，不按过严标准判失败。

本轮没有修改 description、通用信息选择、Hook、adapter、版本号或付费能力。

## 判定口径

原自然题预登记把“枚举具体指标清单”整体列为失败条件，容易误伤合理审稿论证。根据用户在出稿后的明确校正，保留原预登记并另存 [`adjudication-addendum.md`](adjudication-addendum.md)：

- 允许基于已给数据核算、比较、形成审慎结论，说明点名缺项的直接影响，并列出直接相关的指标、费用或依据类别；
- 只有推断冒充既成事实，或新增材料外数值、具体主体、期限、承诺、固定程序、合同义务和无关审查域，才判硬回退；
- 一般类别建议、条件性影响和由常识支持的一层结论不因“原文没逐字写”而失败。

## 过程与消融

### 固定文件列表控制

早期 R3 把四个允许文件直接写进提示词，MiniMax 连续把“允许读取”理解为“四个都要读取”，因此不能验证渐进路由。相关样本保留为提示词设计反例，不进入最终准入：

- current main MiniMax：SHA-256 `692B59C281952719BE392E2B680FA9EEBDAB1BFFD87D202443F3E61237C06D7D`；
- early candidate MiniMax：SHA-256 `F7895D71FE75E9A45CCE067C8762296C2E9C2C3DA0B8E15993A71462B8BC6D82`；
- Kimi 的两份早期稿仅作历史辅助观察，不计写稿准入；其模型职责已由 [`model-amendment.md`](model-amendment.md) 校正。

### 自然请求同模型 A/B

OpenCode Go DeepSeek V4 Flash 在 current main 与候选上使用同一 `natural-prompt.md`：

| 臂 | session | 实际路由与结果 | SHA-256 |
| --- | --- | --- | --- |
| main | `01a03528-3cae-77a0-b984-147766255908` | 读取通用审稿、可研与 AI 算力长页；扩展到备选路径、7×24、扣款/替换资源、安全与验收程序 | `A92436FC25D6D0017AFDEBCAF33C7E80B27150F0931A8E3B71BD8CCA3937C693` |
| R3D candidate | `01a0351f-f740-79e0-a0e8-af367715af06` | 未读取 AI 算力长页；保留四项分析，没有材料外数值、实际主体或未点名审查域 | `192E875742AC3B8542B2971E04B17DD066E6A0B60B292D26C5BB7BACB390F0D5` |

同模型结果证明，专项选项库不是完成该题所必需，减少加载不会使审稿变薄。

### R3D 暴露的剩余问题

- Ollama 仍写“至少两家”和候选验收角色；
- Alibaba Token Plan 1 经通用去 AI 味页转回 AI 算力长页，扩展比较路径、第三方与安全内容；
- Alibaba Token Plan 2 自造 `2800—4200` 敏感性区间，判 `HARD_FAIL_UNSUPPORTED_NUMBER`；
- MiniMax candidate 首跑反复目录探测，记 `TECH_INVALID_AGENT_LOOP`；技术恢复重跑完成审稿，未新增事实数值，记 `PASS_WITH_SCOPE_NOTE`。

这些结果没有被终止在中间状态：候选随后拆成 R3F 专项只审直达和 R3F2 技术缺项例外收窄，并只复跑暴露相应问题的路线。

## 最终候选五路真实审稿

同一事实包、同一审稿目标、无 Hook、无联网、只读 checkout：

| provider / model | session | 裁定 | final SHA-256 |
| --- | --- | --- | --- |
| OpenCode Go / DeepSeek V4 Flash | `01a03535-409b-7262-b6b1-ffada1ece6d7` | `PASS_WITH_SCOPE_NOTE`；只读入口与可研叶，算术、状态、四项缺口完整；5.7% 为给定数字直接计算，指标类别和验收建议均未写成既定安排 | `C8EF022752BDB017AF7EEDBFB7F7A29B93113392C1D86CB4B84D951CB4B06539` |
| Ollama / DeepSeek V4 Flash 0731 | `01a03532-11dc-77d3-8f91-92c8ad229762` | `PASS_WITH_SCOPE_NOTE`；无厂商数量和阈值；候选主体类别明确要求由材料确定，不是实际责任分工 | `94C9273CFC70AD0BFE8B5C900F488FC7CEC3537C64DB149B71F3AE1BA5B703B7` |
| Alibaba Token Plan / DeepSeek V4 Flash 0731 | `01a03532-1169-7bf2-8d2c-cb80b32bd789` | `PASS_WITH_SCOPE_NOTE`；没有比较路径、固定程序或无关安全域；抽样、资源和费用类别与点名审查直接相关 | `97F659D0F18622703AFAC4F1AF4F1184C8E79B4D5AC5BE3FF1CD4DE03BBB5F03` |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 | `01a03537-cd09-7bb3-9610-54d35707ec57` | `PASS_WITH_SCOPE_NOTE`；R3F2 只读入口与可研叶，旧 `4200` 数值消失；0.88元/千Token为明示金额和用量的直接试算并附口径警告 | `C5B594FCDC7793B04E8F72ACC138E4A18E3A9304BCC63CD115F34B4939FC4D1E` |
| MiniMax / MiniMax M3 | `01a03535-40dc-7a53-b168-d5cca54157b5` | `PASS_WITH_SCOPE_NOTE`；技术恢复提示只用于避免目录循环；正文保留全部状态，费用试算有条件说明，未代填阈值 | `A253A1C6936B380E518A4663FF205CEEF26D54103251DD7E4130723A5DC336E7` |

五稿都具有实质审稿内容，并非为了减载而只复述材料。候选没有要求模型回避原因、影响、效果或结论；它要求这些分析保持证据可追溯、状态正确且不冒充已安排事实。

## 加载与 token 观察

- R3D Ollama 读取通用页后的会话报告输入为 `201370`，R3F 为 `56484`；Alibaba Token Plan 1 从 `114115` 降到 `46486`。这两组说明减少长页可显著降低实际会话输入。
- OpenCode、MiniMax 和 Alibaba Token Plan 2 在部分运行中发生目录探测、插件同步失败或长推理；其会话总输入没有稳定下降。Alibaba2 R3F2 虽只读两份产品文件，仍因代理探测报告 `154490` 输入。因此只能确认“产品参考资料集合减载”，不能把所有 provider 的端到端 token 都宣传为稳定下降。
- 一次 CLI 命令把 `-a` 放在 `exec` 子命令后而立即报参数错误，记技术无效并用 `codex -a never exec ...` 修正；没有冒充模型结果。

## 产品与工程边界

- canonical：`SKILL.md`、`references/ai-compute-docs.md`、`references/genre-checklist-feasibility-review.md`；
- 普通镜像：Agent Skills、Hermes、OpenClaw、Qwen Code 逐字同步；
- 新增确定性测试覆盖专项只审直达、长页不自动加载、允许的类别分析和四镜像一致性；
- 没有新增 Hook、coordinator、adapter、自动测算、厂商数量门、指标阈值门或段长门。

五提交暂停复核、固定 main 差异检查和同模型消融未发现范围外产品变更。镜像同步二次运行保持工作树干净；快速校验为 `Skill is valid!`，状态/链接/专项路由和镜像相关检查均通过，`git diff --check` 只有 Windows 行尾提示。

全量首跑实际为 `Ran 693 tests in 81.457s`、2项失败：两条旧测试仍断言 AI 算力“专项直接读取”，与新路由文案不一致。产品未回退；只更新 `test_skill_boundary.py` 的过时断言后，该文件78/78通过，全量复跑 `Ran 693 tests in 85.737s`、`OK`。

本地 main 集成后重新执行专项、镜像、状态、链接、快速校验和差异检查；结果见合并回执提交。push、tag、Release 和三平台发布是不同授权，本结果不授权推送或发布。
