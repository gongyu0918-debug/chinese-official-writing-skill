# 保护性否定收束提示：完整真实稿 A/B 预注册

日期：2026-08-03。本文在真实改稿输出生成前登记，只补上一轮短链路未覆盖的完整自然稿验证，不修改产品规则。

## 固定版本与条件

- Candidate：`2b71e3e125ded103c24888504904f8dc7e792a58`
- Baseline：Candidate 的直接父提交 `4cbe7c0da3c78ce0e69f26859bda9345b459492a`；两者行为差异只来自 `prose_lint.py` 三类提示和 `final-review-layers.md` 的一次语义接应。
- 两臂均使用 `gpt-5.6-terra / high`，逐字读取相同原任务和相同既有初稿，各取首个技术有效结果，不补抽、不换题。
- 测试是“终稿审校”自然修改任务。写作指令只要求按原任务把初稿审校成可直接使用正文，不在指令中点名 P0、目标句、预期删除或检测标签。
- Candidate 在完整初稿上执行一次 `prose_lint.py --delivery-mode draft-body --json`，逐项作保留、进行态改写或删除的语义判断，最多修改一次并复扫一次；Baseline 按直接父提交的既有终稿复核正常处理，不注入 Candidate 标签或额外轮次。

## 三个既有样本

1. R01 完整阶段报告：原任务取自 `tests/evidence/candidate-b-three-way-blind-20260715/packets/luna-t01-j1.md` 的“原始任务”块；初稿为 `tests/evidence/candidate-b-writing-20260715/luna-t01.md`。该稿经用户人工标注存在外围结论限定、无锚定否定和未决事项重复披露。
2. R02 完整异常报告：原任务取自 `tests/evidence/candidate-b-three-way-blind-20260715/packets/luna-t03-j1.md` 的“原始任务”块；初稿为 `tests/evidence/candidate-b-writing-20260715/luna-t03.md`。该稿含异常原因、影响总量和会议结果的保护性收束，并残留正文符号。
3. C01 clean 通告：原任务取自 `output/manual-annotation-round2-20260711/source-tasks.md` 的第 07 题；初稿为 `output/manual-annotation-round2-20260711/raw/agent-4/07-市图书馆临时闭馆通告.txt`。该稿已由用户确认自然、完整、无保护性外扩，用于检查误伤和无必要改写。

## 验收

- 三题均不得新增事实、数字、日期、主体、责任、期限、承诺、决定状态、文种、格式或输出范围回退。
- R01、R02 中，Candidate 对无业务锚的保护性补句应删除；本单位正在办理的核心事项应改成与材料相符的进行态；材料明确的会议决定状态、法律边界或业务事实应保留。不能按词表一刀切。
- Candidate 至少在一个风险题上降低保护性收束数量或直接修改成本，且两个风险题均不比 Baseline 更差。
- C01 不得出现 Candidate 独有的删事实、改状态、扩写、套话或格式回退；没有新标签时允许终稿与初稿一致。
- 独立盲审只看原任务、初稿和匿名终稿，先核验硬事实，再评价 P0、自然度和直接使用成本。单纯字数变化不决定胜负。
- 技术失败原样记录；不换提示词、不补抽、不为单句追加产品规则。
