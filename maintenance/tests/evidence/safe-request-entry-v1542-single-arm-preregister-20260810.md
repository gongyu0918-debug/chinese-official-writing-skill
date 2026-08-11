# 短事务采购入口候选单臂真实质量验证预注册

## 固定对象与边界

- 候选分支：`codex/safe-request-entry-integration-v1542`。
- 固定提交：`a8a5c4e70bda422833bdee08fb9a068cbfba7583`；运行前后均核验 `HEAD`，变化即停止。
- 产品根：候选 worktree 的 `.agents/skills/chinese-official-writing`；不读取或修改 `description`，不合并、不推送、不发布。
- 本轮只验证候选自身的真实自动路由、事实边界与成稿可用性；不做基线 A/B，不作匿名票数比较，不以模型偏好得出相对优劣结论。

## 运行协议

- 两条独立写作链：Alibaba Token Plan 与 Ollama `DeepSeek V4 Flash 0731`，均设 `reasoning=max`。
- 每个 provider 的每题仅发起一次；只保留首个 final，零重试、零补抽。超时、空输出、模型/effort/实际 Skill 根不可核验，原样记录为技术失败，不用替代模型或第二次调用补齐。
- 在仓库外的独立运行时由 `agent_writer` 生成真实 `skill` prompt；使用 `_reference_paths_for_genres` 的实际返回值，不向 writer 显式指定 reference 路径。
- 每稿冻结原任务、完整首 final、运行时间、provider/model/effort、候选 SHA、Skill 根 SHA、实际 selected paths 与输出 SHA-256。不得将测试控制语、审计结论或 reference 名称混入给 writer 的任务。

## 冻结矩阵

| ID | genre | 原始任务 | 预期路由 |
| --- | --- | --- | --- |
| R1 | 请示 | 请起草一份采购请示。拟购置 1 台图形工作站用于三维建模，型号为 WX-900，单价 18,600 元。现有三家报价：甲公司 18,600 元、乙公司 19,200 元、丙公司 18,950 元；供应商尚未确定。拟从 2026 年设备更新经费列支，到货后按合同约定组织验收。只输出正文。 | `SKILL.md`、`information-selection.md`、`genre-playbook-request.md`、`workflow.md`、`handling-elements.md`、`argument-chains.md` |
| R2 | 申请 | 请起草一份软件订阅申请。拟续订“协同文档专业版”12 个月，金额 9,600 元，用于项目材料协作，拟从部门办公经费列支。材料未给询价、验收或供应商信息，本次只申请续订事项。只输出正文。 | `SKILL.md`、`information-selection.md`、`genre-playbook-request.md` |
| R3 | 请示 | 请起草一份采购请示。拟按同一规格购置 20 台条码扫描器，型号 BS-20，单价 680 元，合计 13,600 元。已完成询价：甲公司单价 680 元、乙公司单价 705 元、丙公司单价 690 元；拟从信息化专项经费列支，尚未验收。只输出正文。 | `SKILL.md`、`information-selection.md`、`genre-playbook-request.md`、`workflow.md`、`handling-elements.md`、`argument-chains.md` |
| R4 | 请示 | 请起草一份采购请示。拟采购会议室显示器 2 台，单价 4,800 元；无线投屏器 2 套，单价 1,200 元；安装服务 1 项，价格 2,000 元，合计 14,000 元。三家总报价分别为甲公司 14,000 元、乙公司 14,600 元、丙公司 14,250 元，供应商尚未确定。拟从办公设备经费列支，到货后组织验收。只输出正文。 | `SKILL.md`、`information-selection.md`、`genre-playbook-request.md`、`workflow.md`、`handling-elements.md`、`argument-chains.md` |
| R5 | 申请 | 请按以下固定字段起草申请，保留字段名、字段顺序和独立行：申请事项：采购档案盒；数量：50 个；单价：12 元；金额：600 元；经费来源：办公经费；用途：年度档案整理；备注：材料未给询价、验收和供应商信息。只输出字段式正文。 | `SKILL.md`、`information-selection.md`、`genre-playbook-request.md` |
| R6 | 请示 | 请起草一份约 800 字的单项采购请示，完整材料如下：信息中心拟采购 1 套网络安全日志审计设备，型号 LA-500，含 3 年原厂维保，单价 86,000 元；已完成三家询价，甲公司报价 86,000 元，乙公司报价 89,500 元，丙公司报价 87,200 元；拟从 2026 年网络安全专项经费列支；供应商尚未确定；设备到货后由信息中心会同资产管理部门按合同约定组织验收。采购用途为汇聚现有业务系统日志，满足安全审计需要。请完整呈现请示文种骨架，仅输出正文。 | `SKILL.md`、`information-selection.md`、`genre-playbook-request.md`、`workflow.md`、`handling-elements.md`、`argument-chains.md` |

所有路径均不得出现 `references/task-route-cards.md` 或 `references/genre-playbooks.md`。R2、R5 必须是轻路由；R1、R3、R4、R6 必须是复杂路由。

## 审计与判定

每份首 final 独立核对：

1. 所有金额、数量、型号、期限、合计与三家报价逐项保真；R3 的 `20 × 680 = 13,600`、R4 的 `9,600 + 2,400 + 2,000 = 14,000` 必须一致。
2. 供应商“尚未确定”、已询价/未询价、已验收/未验收、到货后验收等状态不得升级、倒置或补造；R2、R5 不得因为材料未给而虚构询价、验收或供应商。
3. R5 字段名、顺序和独立字段行必须保留；其余题只输出请求的正文，不附解释、风险提示、路径、审计语或额外清单。
4. R2、R5 应紧凑；R1、R3、R4、R6 应根据材料展开为可办理的请示正文。R6 接近 800 字，优先保证已给要素与完整骨架。
5. 任一硬要素或真实路由失败均如实标记 `FAIL`；技术失败标记 `TECHNICAL_FAILURE`，不重跑。本轮只记录候选质量事实，不据此修改产品。

## 交付

运行记录和首 final 写入仓库外运行目录；结果报告仅汇总 SHA、路径、逐项核验、技术状态、数量化结果与剩余风险。证据提交前运行 `git diff --check` 与结果文件的最小完整性检查。
