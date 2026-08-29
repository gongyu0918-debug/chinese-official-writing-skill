# 事务稿原因缺口正文外提示结果

## 结论

`WR-009b` 以 `CURRENT_BASELINE_SUFFICIENT / WAIT_NEW_COUNTEREXAMPLE` 收口，不保留产品候选。当前 `information-selection.md` 的通用“实质缺口按输出模式短列”规则已经覆盖本目标：明确允许提示的缺原因申请5/5给出正文外原因提示；没有把答案写进题面的自然 holdout 中，4份技术有效稿4/4主动提示，另1份因读取到用户级 Skill 污染而作废。可由排队、设备数量和错峰尝试直接闭合原因的申请5/5均写出采购必要性，没有因文后提示逻辑删去合理原因。

两轮最小候选均已拒绝并恢复产品字节。R1 一度把“只输出正文”题的目标安全率从3/5提高到4/5，但明确拒绝提示题由基线4/5降为3/5，并在自然 holdout 出现把打印机一般用途当作本次原因、续造另行报批的目标回退。R2 增加“材料前提”后修复该 holdout，但明确拒绝题仍只有3/5安全，且只输出正文题的 Ollama 又写入“待进一步明确后按程序组织实施”。两轮均不是稳定净收益。

分支最终已将 `chinese-official-writing/references/information-selection.md` 恢复到固定基线；相对 `main@6e4e8914` 的产品差异仍只有已独立通过的 `UL-005-R10` 扩写指令候选。

## 样本与判定

- 固定基线、R1、R2 各25份，共75份真实稿；分别有24、25、22份技术有效。技术失败只记环境/trace，不计质量票，也未用贵模型补写。
- 五条低成本路线均为 `max`：Alibaba Token Plan 2 / 1 的 DeepSeek v4 Flash 0731、Ollama Cloud DeepSeek v4 Flash 0731、OpenCode Go DeepSeek v4 Flash、MiniMax M3。
- 原因可推断题接受由日均260份、1台设备、15至25分钟排队和错峰尝试形成的缓解排队、保障归档等一层原因与即时作用；这类表述不是外扩。
- 失败只认具体事实、用途、流程、责任、期限或决定被补造，未决状态升级，正文外提示回流正文，或用户输出范围被破坏。正文短于完整提示词不构成失败。

## 新登记风险

1. `WR-009c` 稀疏事务申请的未决字段续写：基线及候选多次出现“待明确后另行报批”“按程序组织实施”等材料外动作。下一原子只测未决字段后的程序承诺，不同时改原因推断；采购原因有事实前提时仍允许自然写入。
2. `CL-001-NOHK-R2` 普通无 Hook 正文交付：三臂、多 provider 仍反复出现“已读取技能”“正文如下”、横线、自检、commit/测试说明。后续只前移或合并现有“只交正文”规则，使用采购申请、活动新闻、情况说明和长稿控制题，不新增 description。

## 五提交复核

上一个 checkpoint 后又累计5次提交时暂停扩展并复核：

- `06e1a3c5` 与 `902cf698` 两个候选及 `e730e0d8` 恢复提交完整保留，最终 `information-selection.md` 与 `136fd2ae` 逐字一致；R1/R2 不以隐藏改动留在产品中。
- 相对固定 main 的产品差异只有 `hooks/capabilities/under_length/runtime.py`；本轮原因提示试验没有改 description、Hook、adapter、包体、版本或平台元数据。
- 108项 under-length、共享硬锚、宿主 adapter、Hook 层契约、复杂度与 Stop 回归通过；两套 runner 通过 `py_compile`，两套 JSON 通过解析，`git diff --check` 通过。

## 实际命令

```powershell
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint.py --arm baseline --prepare
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint.py --arm baseline --provider <alibaba2|alibaba1|ollama|opencode|minimax>
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py --arm baseline --prepare
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py --arm baseline --provider <alibaba2|alibaba1|ollama|opencode|minimax>
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint.py --arm candidate --prepare
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint.py --arm candidate --provider <alibaba2|alibaba1|ollama|opencode|minimax>
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py --arm candidate --prepare
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py --arm candidate --provider <alibaba2|alibaba1|ollama|opencode|minimax>
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint.py --arm candidate_r2 --prepare
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint.py --arm candidate_r2 --provider <alibaba2|alibaba1|ollama|opencode|minimax>
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py --arm candidate_r2 --prepare
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py --arm candidate_r2 --provider <alibaba2|alibaba1|ollama|opencode|minimax>
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint.py --summarize
python -B maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py --summarize
python -B -m unittest maintenance.tests.test_under_length_capability maintenance.tests.test_shared_hard_anchors maintenance.tests.test_host_gate_adapter maintenance.tests.test_hook_layer_contract maintenance.tests.test_complexity_contract maintenance.tests.test_gate_stop_hook -q
python -m py_compile maintenance/tests/evidence/short-inference-r1/run_cause_hint.py maintenance/tests/evidence/short-inference-r1/run_cause_hint_holdout.py
python -m json.tool maintenance/tests/evidence/short-inference-r1/cause-hint-cases.json
python -m json.tool maintenance/tests/evidence/short-inference-r1/cause-hint-holdout-cases.json
git diff --check
```

原始 final、trace、stderr 和汇总保存在未提交的 `output/short-inference-r1/cause-hint*`，不进入产品包。
