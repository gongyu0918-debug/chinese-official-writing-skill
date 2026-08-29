# `SHORT-NATURAL-REFERENCE-R1` R1 真实写稿结果

## 固定候选与样本

- 产品候选：`bda7b77b1c6a413e51a37920dbe63ab75c274f1f`。
- 相同十题、五家低成本 provider、`max`，共 50 次候选输出；两个显式压缩控制未确认固定 Skill trace，其余 40 次普通起草均技术有效。
- R1 把“不短于事实材料”与采购、通知、新闻、说明、纪要、事故六类功能示例同时写入必读信息选择页，并在轻量卡修改说明/通知/事故。

## 目标结果

| 题组 | 基线 | R1 | 人工结论 |
| --- | --- | --- | --- |
| 未决情况说明 | 102—274 字，3/5 低于140初值 | 103—125 字的四份正常正文及一份119字正文；按120校准后仍3/5偏短 | 没有跨 provider 稳定增益；Ollama 仅102→103，却候选独有漏掉“本次材料未附” |
| 突发事故通报 | 四份有效正文98—105字 | 五份102—122字 | 5/5形成可用正文；Alibaba 1/2 的“后续有关情况将及时通报”按阶段性事故通报的正常发布收束重判为可接受，不再构成阻断 |
| 办理通知 | 74、90、113、171、461字 | 99—107字 | 包装和虚构细节显著减少，但仍有两份99字；Alibaba 2 候选独有新增“对本部门数据目录进行梳理”前置动作，阻断 |
| 未决会议纪要 | 118—216字，1/5低于120 | 118—213字，1/5低于120 | 没有稳定目标改善；MiniMax 候选独有新增“听取汇报”和“留待后续研究后再行议定” |

## 控制和旁路

- 显式不超过80字的五份候选正文均为39—48字，保留时间、渠道和值班表字段；未被普通起草规则反向扩写。
- 100—120字压缩控制的三份技术有效稿为111—113字；两份没有确认固定 Skill trace，只记技术失效，不用来证明回退。
- 采购/维修基线本来15/15超过100字。R1没有必要收益，却在多家候选中新增“另行报批/报告”、调研论证、故障部件、专业维修单位和采购流程；MiniMax 维修稿还扩到700个非空白字符。合理的办公效率、培训影响或算力紧张归因没有被判失败，阻断项均是新具体动作、程序、部件或承诺。
- 活动新闻基线最低150字，R1不解决既有短稿；候选出现完整年份遗漏，以及“系统管理员、常见问题答疑、真实业务案例、具备独立操作能力、确保全员达标、下一步回访”等新具体过程、范围或承诺。该组证明通用功能枚举会串扰已经足够的文种。

## 决定与 R2 消融

R1 为 `REJECTED_CANDIDATE_SPECIFIC_HARD_REGRESSION`，不进入 Hook 或工程门。拒绝原因不是合理推断或稿件变长，而是候选独有的新程序、动作、承诺和事件内容。

R2 只做三项缩减：

1. 必读信息选择页删除六文种功能枚举，只保留“不换词缩写、不短于可分离事实材料、只使用现有文种叶功能”；已有事实关系和文种功能完整时停止扩写。
2. 当时曾把事故通报的未来披露收束列为禁项；现经用户纠正和官方样本复核，该限制撤销，阶段性通报可写无具体时间、渠道或新处置内容的后续通报/公布收束。
3. 通知的一层目的只能承接已给报送动作，不新增梳理、核对、摸排等前置动作。

R2 不改采购、新闻或纪要叶，不新增统一结构、效果句或条件性结论要求。

## 实际命令

```powershell
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate --prepare
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate --provider alibaba2
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate --provider alibaba1
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate --provider ollama
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate --provider opencode
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate --provider minimax
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --summarize
git diff --word-diff=plain c60e3ffaa12af012bf2a3910081ae70244a87a21..95ffb71d -- chinese-official-writing
git diff --word-diff=plain bda7b77b1c6a413e51a37920dbe63ab75c274f1f..95ffb71d -- chinese-official-writing
```

自动关键词仅用于定位，最终结论来自逐份读取 `output/short-natural-reference-r1/raw/*/*-candidate.final.txt` 后的事实、状态、文种与候选归因复核。
