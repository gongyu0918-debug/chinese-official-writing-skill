# WR-026-R4 当前基线真稿结果

日期：2026-09-02。

固定产品：`main@821364abfd7df2fa0af04f5e3ab7277897110ff0`。五家均在 Codex Desktop 独立任务中运行相同五题，使用各自 `max` 档；任务只读根产品，不读取本轮预登记结论。

## 技术状态

| provider | Codex task | 状态 | 有效稿 |
| --- | --- | --- | --- |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 | `01a06142-5857-7fc2-9ed7-a27fb629ab42` | 完成 | 5 |
| Alibaba Token Plan / DeepSeek V4 Flash 0731 | `01a0613f-3fa7-7c70-82fe-87d3c30f3430` | 完成 | 5 |
| Ollama Cloud / DeepSeek V4 Flash 0731 | `01a06142-5de3-7e71-bcec-36ad9991abbb` | 首次与原任务重试均为同一 502 | 0（技术无效） |
| Ollama Cloud / GLM 5.3 Flash（同 provider 回退） | `01a0614d-428a-7cb3-a167-da01377d1e76` | 同一 502；按用户要求本轮停止重试 | 0（技术无效） |
| OpenCode Go / DeepSeek V4 Flash | `01a06142-627c-74c3-83aa-16f45303d302` | 完成 | 5 |
| MiniMax / MiniMax M3 | `01a06142-67a1-7301-9ae6-e8bff49f0d2c` | 完成 | 5 |

当前共 20 份有效真稿。Ollama 两个模型均返回 `Provider unreachable: ollama-native orphan tool result <missing-id>`，目标地址为 `http://127.0.0.1:10100/v1/responses`；这是同 provider 的传输失败，不计写稿质量，也不以其他 provider 的稿件冒充 Ollama 结果。

用户指出 OpenCodex 2.39.0 的 `ollama-native` 适配器要求 `tool_result` 前存在同 `call_id` 的 assistant tool call 后，本轮又分别为 Baseline 与 Candidate 请求全新干净任务；两次请求只返回 client setup id，未形成可列出的 Codex task，也没有正文输出。按用户要求停止有限重试。由于没有跑通样本，该诊断不提升为仓库通用测试规则，只保留在本证据中等待下次复现。

## 正向题观察

- Alibaba 1、Alibaba 2、OpenCode 的平台栏、邮件和独立成文短意见均已形成事实或亲历、直接影响或判断、有权对象和具体建议的完整关系；平台栏与邮件没有重复标题、落款、日期，独立成文稿保留题名、建议方和日期。
- 三家均把审核口径与平台字段/功能分别交给审核部门和平台运营方，没有把尚未明确、尚未决定升级为现行规则。`便于核对`、`减少重复操作`、`难以确定补充何种材料`等由已给事实直接支持的一层作用或判断记为正常写作，不记外扩。
- MiniMax 平台稿和邮件稿有可用的事实—影响—建议骨架，但把“协会拟另行汇总对照表”、错误位置提示等写成更具体的现状或安排；独立短意见又补了书面/电话过渡措施。具体新增措施不是本轮期望的一层合理推断，记为基线模型风险。

## 控制题观察

- 三家 DeepSeek 的正式长意见保留完整题名、问题与建议层级、建议方和日期，通知保持已决定状态与责任关系。
- MiniMax 正式长意见补写总部/子公司交易关系、已被要求提交证明、税务备案材料、文件压缩后格式变化等材料外具体事实。这是当前基线已有的 provider 风险；后续只有候选相对同 provider 新增或放大同类内容，才记候选回退。

## 基线结论

当前基线已经具备短意见能力，但能力只在专叶中以“可以同节”间接表达，跨 provider 稳定性仍有差异。R4 可以继续作为新增能力的显式、窄规则原型；准入不以“Baseline 必须先失败”为前提，也不按包装计数零和判定。Candidate 必须用相同五题重新写稿，重点看必要说理、权限分配、载体形态以及是否诱发材料外具体措施。
