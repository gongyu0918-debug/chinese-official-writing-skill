# `WR-018-NOTICE-ISSUER-DATE-R1—R3` 真实写稿结果

日期：2026-08-30。

终态：`VALIDATED_NEXT_RELEASE_CANDIDATE / NOT_MAIN_YET / NOT_V1.6.21`。

## 目标

稀疏内部办理通知给出“发送至信息中心公共邮箱”，但没有给发送单位、落款或成文日期。写稿应保留对象、时限、渠道、表内字段和免报条件，不把报送渠道中的单位名反推为发文主体，也不补当前日期、占位日期、邮箱地址或联系人信息。标题、主送、自然目的句和“特此通知”允许；不设固定100字门槛，只要求成稿完成通知功能且不比材料退化为残缺转写。

## 真实写稿

固定 `main@c60e3ffaa12af012bf2a3910081ae70244a87a21` 为首轮基线，五家低成本 provider 使用同一自然用户题。R1 完成五家 baseline/candidate 共10稿；R2复用基线完成五家 candidate 及 MiniMax 同题复跑共6稿；R3固定 R2 产品，只完成目标 provider MiniMax 与稳定控制 Alibaba2 两稿。总计18稿，全部技术有效；R2、R3候选均记录目标 `task-route-cards.md` 的实际读取。

| 轮次 | 结果 | 结论 |
| --- | --- | --- |
| R1 “不反推 + 只交正文” | Alibaba2基线的推定“信息中心”落款被移除；MiniMax仍补“信息中心 + 当前日期”；Alibaba1、OpenCode候选明显缩短 | “只交已经成立的通知正文”可能造成篇幅副作用，删除该尾句 |
| R2 仅保留“不反推” | 五家均保留办理事实；Alibaba2移除推定落款，MiniMax首次移除落款、日期和占位联系方式 | MiniMax新增正文前规则说明；同题复跑又补“信息中心 + 空白日期”并正文后解释，R2不稳定 |
| R3 增加“渠道/接收单位名称不等于发文主体” | MiniMax 147字符，全部事实保留，无落款、日期、占位或过程说明；Alibaba2 90字符，全部事实保留且无原目标回退 | 2/2目标复测通过，规则进入工程门 |

Alibaba2 的90字符稿不是失败：它有标题、主送、完整报送动作、时限、渠道、字段和免报条件，并明显形成通知功能；本原子不以整数下限替代真实可用性。MiniMax R3 也没有因“信息中心”在材料中真实出现就把它当作发文授权，说明关系提示解决了目标错误。

## 产品范围与风险

- 产品原子只有短通知卡的一条关系限定：材料没有发送单位、落款或成文日期时，不从邮箱、接收方或当前日期反推；渠道或接收单位名称不等于发文主体。
- canonical 与五套公开静态镜像已同步；新增确定性测试只锁定该关系文本和既有镜像字节一致性。
- 本候选不加入已冻结的 v1.6.21，也不改 description、普通写稿篇幅规则、Hook、包体版本或其他文种。
- 仅验证一份内部办理通知和两家 R3 provider；材料明确给发送单位、用户要求完整落款、正式红头版式或多主送关系不外推。MiniMax 与其他模型仍可能产生独立的正文包装，后续由直接交付原子处理。
- 原始 trace、终稿、fixture 和 provider JSON 位于忽略目录 `output/wr018-notice-issuer-date-*`，未提交模型正文或运行时凭据。

## 实际命令

- `python maintenance/tests/evidence/wr018-notice-issuer-date-r1/run_eval.py --prepare|--provider <id>`
- `python maintenance/tests/evidence/wr018-notice-issuer-date-r1/run_eval_r2.py --prepare|--provider <id>`
- `python maintenance/tests/evidence/wr018-notice-issuer-date-r1/run_eval_r2_repeat.py --prepare|--provider minimax`
- `python maintenance/tests/evidence/wr018-notice-issuer-date-r1/run_eval_r3.py --prepare|--provider <alibaba2|minimax>`
- `python maintenance/tools/sync_adapters.py`
- `python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_promptfoo_eval -v`
- `python C:\\Users\\admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py chinese-official-writing`
- `git diff --check`
