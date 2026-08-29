# `UL-005-R10` 扩写指令 R4 最终结果

## 结论

`CANDIDATE_PASSED_NOT_MERGED`。R4 五路候选15份全部技术有效：扫描仪采购申请5/5进入220—280字，活动新闻4/5进入范围且 MiniMax 对材料边界选择逐字 D0，稀疏打印机控制5/5逐字回 D0。正文外包装为0，完整日期、数字、未完成/补测/正在汇总及采购未决状态均保留；R1—R3 出现的具体设备规格、状态改写、后续程序和强行补用途均未复现。

候选只修改 `under_length` 的修订指令，不修改普通 Skill/reference、description、机械硬锚、单稿事实台账、语义 verifier、adapter、包体或版本。它已通过真实写稿门，但仍位于独立分支，未合并 main、未推送、未发布。

## 四轮收敛

| 轮次 | 有效候选 | 目标收益 | 硬回退与处理 |
| --- | ---: | --- | --- |
| R1 | 15/15 | 新闻4/5可达到范围；允许一层原因/作用的方向成立 | MiniMax/ OpenCode 稀疏题补用途和程序，状态与后续安排外扩；拒绝并拆分状态/精确回退 |
| R2 | 15/15 | 稀疏逐字回退提升到4/5，状态改写消失 | MiniMax仍补用途和程序；Alibaba 1仍附字数说明；拒绝并前移正文首尾及稀疏判定 |
| R3 | 15/15 | 稀疏5/5逐字回退，包装0/15；两道充足题各4/5进入范围 | Alibaba 1把未定型号展开为自动进纸、连续扫描；拒绝并限制通常功能的抽象层级 |
| R4 | 15/15 | 扫描仪5/5达标；新闻4/5达标、1份安全D0；稀疏5/5精确D0 | 无候选独有的事实、状态、程序、交付或本原子相关硬回退 |

## R4 逐题结果

| 题目 | 长度结果 | 功能与事实边界 |
| --- | --- | --- |
| 扫描仪采购申请 | 231、235、245、236、237字，5/5进入范围 | 五份均保留260份、1台、15至25分钟、错峰尝试、2台及预算/型号/供应商/采购方式未决；均写出缓解排队、提高处理能力等一层作用；没有组件、参数、性能对比或新增用途 |
| 培训活动新闻 | 224、238、221、230字进入范围；MiniMax逐字D0 | 五份均保留2026年8月28日、36/34/2范围、账号未开通、9月2日补测和意见正在汇总；帮助熟悉、检验操作等为活动直接支持的一层作用，不写成36人全体既成成效 |
| 稀疏打印机控制 | 5/5均为38字正文、逐字D0；五份 SHA-256 相同 | 不借“打印机通常用于打印”补原因、用途、程序或效果；没有判断说明、字数、自评、横线或引导语 |

## 五提交 checkpoint

分支前5次提交后暂停扩展并完成 review：

- 相对 `main@6e4e8914` 的产品差异只有 `chinese-official-writing/hooks/capabilities/under_length/runtime.py::_revision_instruction`；机械门、事实台账、verifier、core 和 adapter 零差异。
- 107项 under-length、共享硬锚、宿主 adapter、Hook 层契约、复杂度与 Stop 回归通过。
- review 发现“不得接待确定后将”中文歧义并在 `12b2dfd9` 改成带引号短语后才固定 R3。
- 仓库不存在 `maintenance/tools/quick_validate.py`，该旧命令实际返回文件不存在，未记为通过；本轮使用直接相关回归和后续确定性检查。

R4 固化测试后，同一组相关回归增至108项并全部通过。Codex 与 Qwen Code 的 `under_length` companion 离线组装分别为56/55文件，fingerprint 为 `f0200ab657e4b736af7eff697776ee3db6efff29af10726d7e9e7d52729da366`、`1608f9833782dc964a658a55e6bdb4dd10161e2504807ffcd3996c8fc916d227`；两者均 `enabled=false`、`installed=false`、`network_used=false`，不冒充当前在线生命周期重跑。

## 实际命令

```powershell
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --prepare --candidate-commit c692d0f4b250aa5cc158f3d87b9eb1bb015205ed --output-root output/short-inference-r1/underlength-r10-r4
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba2 --candidate-only --output-root output/short-inference-r1/underlength-r10-r4
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba1 --candidate-only --output-root output/short-inference-r1/underlength-r10-r4
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider ollama --candidate-only --output-root output/short-inference-r1/underlength-r10-r4
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider opencode --candidate-only --output-root output/short-inference-r1/underlength-r10-r4
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider minimax --candidate-only --output-root output/short-inference-r1/underlength-r10-r4
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --summarize --output-root output/short-inference-r1/underlength-r10-r4
python -B -m unittest maintenance.tests.test_under_length_capability maintenance.tests.test_shared_hard_anchors maintenance.tests.test_host_gate_adapter maintenance.tests.test_hook_layer_contract maintenance.tests.test_complexity_contract maintenance.tests.test_gate_stop_hook -q
python maintenance/tools/assemble_hook_companion.py --host codex --capability under_length --output output/short-inference-r1/assembled-r4/codex
python maintenance/tools/assemble_hook_companion.py --host qwen-code --capability under_length --output output/short-inference-r1/assembled-r4/qwen-code
```

原始末条消息、JSONL轨迹和 token/耗时记录保存在忽略目录 `output/short-inference-r1/underlength-r10-r4/`。
