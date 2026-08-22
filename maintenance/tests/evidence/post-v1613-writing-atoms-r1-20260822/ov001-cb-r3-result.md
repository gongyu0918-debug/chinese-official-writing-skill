# OV-001-CB-R3 CodeBuddy 单样本结果

## 固定候选

- branch: `codex/ov001-cb-r3`
- commit: `1972d4bb`
- 变更：observer 的 `segment_id` 与 `preserved_segment_id` 均限定为 `kind=sentence`，保留段不得为 `tail`。
- companion fingerprint: `3393bdea36189f3a52702424c25cb5dfda07aa4806eace2e6c38845a4c0039a7`
- host: WorkBuddy 内置 CodeBuddy CLI 2.115.0
- model: DeepSeek V4 flash, max
- session: `cb-ov-r3-20260822-a`

未使用电脑控制或外部 writer harness。

## 同稿生命周期

- request SHA-256: `e45267a1c59f501c214e03e0bdfe1270040ebe0588f29861052ba2a34d409385`
- D0 SHA-256: `dfb90ead77cd7d30296748e31a1158350d48876e35227fa959720ae057dab466`
- Hook 计数：496；历史终端显示的506与当前核心计数口径并存，正文和 D0 hash 一致，因此按同稿处理，不用字符数标签冒充内容一致性。
- repetition selection: `E1`
- over-length selection: `D1`
- compression attempts: `1`
- final count: `229`
- maximum: `420`
- reason: `semantic_pass`
- delivery verified: `true`
- final SHA-256: `16d29ffd5414ae31e45a8d4c90dea80b1f52f62497c491c633bb920def906812`

## 最终正文

```text
根据专项检查安排，本次检查共登记8项问题。各责任单位按照原检查表确定的责任分工推进整改，复核人员依照原检查表开展复核。现将有关整改进展情况报告如下。

截至7月10日，8项问题中已有5项完成整改并通过现场复核，其中制度记录、设备标识问题各2项，值班交接问题1项，当前状态均为整改完成、复核通过。

其余3项问题仍处于整改阶段，尚未提交复核，分别计划于7月18日、7月20日、7月22日提交复核。

最终验收安排在7月25日统一开展。责任单位和复核人员均已按原检查表确定。
```

## 判定

`PASS_TARGET`。这次不是 D0 安全回退：CodeBuddy 真实走完 observer → compression → semantic verification，同稿安全压到420字以内，保留8/5/2/2/1/3的数量关系、截至日期、三项计划日期、统一验收日期、未提交复核状态及责任主体。
