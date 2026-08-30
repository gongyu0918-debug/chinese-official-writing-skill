# WR-023 申请原因、依据与材料缺口结果

## 结论

选择 R2（实验产品提交 `f2705273eada326531181376bc0d66f7f1d597d2`），通过工程门后以 squash 方式进入本地 `main`，尚未发布。申请正文应有能够成立的原因、依据或必要性：已给事实与常识能够直接闭合时，写成一层低强度原因、一般依据或直接用途；确实无法闭合时，不在正文中虚构具体事由，只有输出模式允许时才在正文后短提示用户补充。采购申请与请假申请分别约束，不把采购用途、请假制度依据和个人私事原因混成一套固定句式。

R3 因提示过度导致年休假材料遗漏、计划状态升级和事假泛称原因回流，终态为 `TERMINATED_PROMPT_OVERHANDLING`。本项没有活动 `HOLD`。

## 官方表达校准

- 大连理工大学采购论证通知把“采购必要性分析”列为论证内容，要求说明现有设备功能、精度、使用负荷及拟购设备的支撑作用。它支持“采购申请不能只列采购对象”，但不授权在材料没有时编造设备故障、业务损失或审批程序：<https://zcglc.dlut.edu.cn/info/1061/1297.htm>。
- 广东工业大学考勤管理办法所附请假申请表把“请假类别”“请假时间”“请假事由”分列，支持把事由或依据视为请假申请的文种要素：<https://hr.gdut.edu.cn/info/1026/1785.htm>。
- 《企业职工带薪年休假实施办法》给出年休假的制度性资格和安排基础，支持年休假使用不特指条款的“一般休假规定”作为低强度依据；它不支持自动断言个人已经满足某单位的具体资格、剩余天数或已经获批：<https://rlsbj.cq.gov.cn/zwgk_182/fdzdgknr/lzyj/rsbgz/202103/t20210305_8969159.html>。

## 真实写稿

全部任务在隔离 Skill 路径运行，思考强度均为 `max`，每题每模型一次，零质量重试。五条低成本路线为：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `alibaba-token-plan/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

共得到 65/65 份技术有效输出：Baseline、R1、R2 各三题五路共 45 份，R3 两题五路 10 份，固定 R2 的全新 holdout 两题五路 10 份。长度字段只作观察，不把“短于提示词”单独判失败；只把候选改动可归因的事实、状态、文种、交付形态或目标功能回退判为失败。基于已给事实和常识的一层一般原因、直接用途、低强度作用及条件性结论按有效写作接受。

| 阶段 | 目标结果 | 终态 |
| --- | --- | --- |
| Baseline | 采购压力前置 5/5；年休假一般依据仅 3/5；缺事由事假 2 份出现泛称原因或空白占位 | 目标缺口成立 |
| R1 | 采购 5/5；年休假 4/5；缺事由事假 5/5 不补泛称原因或事由占位，但正文外提示和其他包装偏重 | 继续收窄 |
| R2 | 采购 5/5；缺事由事假 5/5；年休假 4/5，另 1 份出现“个人事项” | 固定候选做新题复核 |
| R3 | 10/10 技术有效，但出现年休假材料遗漏、计划状态升级和事假泛称原因回流 | `TERMINATED_PROMPT_OVERHANDLING` |
| R2 fresh holdout | 新年休假 5/5 不造个人原因且保留未来交接状态；稀疏打印机采购 5/5 形成办公打印直接用途，0/5 编造设备损坏、数量不足、具体业务损失、采购程序或完成承诺 | `R2_SELECTED` |

全新年休假中一份 Ollama 稿写“符合休假条件”，按不特指单位制度细节的低强度制度推断接受；一份打印机采购写“批准后另行确定安排”，按条件性未来状态接受。MiniMax 一份年休假带代码围栏，属于既有 provider 输出形态差异，不是本次申请原因规则引入的目标回退，继续作为残余风险记录。

## 产品边界

1. 原因、依据或必要性是申请的文种功能，不等于每稿都要写“效果”和“结论”。
2. 能由材料事实、事项性质和普通常识直接支持的用途或一般制度依据，直接写入正文，不先制造缺口再提示。
3. 无法闭合时，正文不使用“个人事务”“身体原因”、空白横线、“事由待补”等代填；允许正文外提示时，只提示申请原因或用途，不顺带扩成全套材料清单。
4. 不新增 Hook、description、统一字数下限、审批流程、政策条款或其他文种规则。

## 输出与哈希

- `output/wr021-application-reason-r1/summary.json`：45 条，SHA-256 `3ba69d47a87fbefaffb2377487b1aaf17dc0e814781d26573aa96b3d806c13cb`
- `output/wr021-application-reason-r3/summary.json`：10 条，SHA-256 `ec8b73680d8637f0d5699e57529a1d4480d1b37519cbaae35b7d973421f0aef9`
- `output/wr021-application-reason-holdout/summary.json`：10 条，SHA-256 `cc3662cf2aa3b2d92d094f6e490965c52448ea0886b7572d2d16ff94890546d9`

原始生成稿和 trace 留在未提交的 `output/`，仓库只提交预注册、固定用例、运行器和本结果摘要。

## 工程门

- `maintenance.tests.test_skill_boundary`：80/80 通过；申请原因、事实与常识闭合、正文外提示和缺事由请假的反控均有直接断言。
- 全量 `unittest discover`：746/746 通过。首次运行唯一失败是旧测试逐字冻结了本次有意修改的采购申请整句；改为镜像 hash 加关键升级/禁入条件断言后，单项和全量均通过。
- canonical、Agent Skills、Qwen Code、QwenWork、Hermes 的通用 `quick_validate.py` 均通过。OpenClaw 包因平台自有 `category` frontmatter 字段不被通用校验器接受，属于既有平台格式差异；仓库的 OpenClaw 包体、无 Hook 和镜像一致性测试均通过。
- `git diff --check` 通过；canonical 与五套普通兼容镜像的申请叶字节一致。

一次诊断中调用 `sync_adapters.py --help` 时，该脚本没有只显示帮助而是执行了同步；当时的 R3 镜像未提交，随后立即恢复固定 R2 canonical 并重新同步。最终 diff、镜像 hash 和全量回归均基于 R2。

## 实际命令

```powershell
python maintenance/tests/evidence/wr021-application-reason-r1/run_eval.py --arm baseline --skill-root <frozen-baseline-skill> --output-root output/wr021-application-reason-r1
python maintenance/tests/evidence/wr021-application-reason-r1/run_eval.py --arm candidate_r1 --skill-root <r1-skill> --output-root output/wr021-application-reason-r1
python maintenance/tests/evidence/wr021-application-reason-r1/run_eval.py --arm candidate_r2 --skill-root <r2-skill> --output-root output/wr021-application-reason-r1
python maintenance/tests/evidence/wr021-application-reason-r1/run_eval_r3.py --skill-root <r3-skill> --output-root output/wr021-application-reason-r3
python maintenance/tests/evidence/wr021-application-reason-r1/run_holdout.py --skill-root <fixed-r2-skill> --output-root output/wr021-application-reason-holdout
python -B maintenance/tools/sync_adapters.py
python -B -m unittest maintenance.tests.test_skill_boundary -v
python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
python -B -m unittest discover -s maintenance/tests -p "test_*.py" -v
git diff --check
```
