# OV-001 calibrated over-length CodeBuddy live result

## Result

`PASS_TARGET`.

The candidate over-length runtime completed a real WorkBuddy/CodeBuddy lifecycle on the procurement request:

- original: 328 non-whitespace characters, SHA-256 `ff0727c09fc9e69828c33126b3180ca3146de8e0fd0babb7dfd53bf5f749e041`
- candidate/final: 236, SHA-256 `0ef4bdab65c0ca65881e889d9b7e50552e0a638264a6e95aecc12785018faefc`
- maximum: 260; internal target: 249
- repetition observation: `E0/CLEAR`
- compression attempts: 1
- selection: `D1`
- reason: `semantic_pass`
- delivery verified: true
- final assistant text: byte-for-byte equal to the selected candidate

The draft kept the request title, addressee, four substantive sections, reason-before-action relation, resource-sharing fact, resource pressure/task waiting, two devices, `18.6万元` each and `37.2万元` total, both test uses, special-fund coverage, not-approved/not-purchased state, low-strength expected effect and approval close. It did not become a bare outline or label list and did not upgrade the expected effect to an achieved result.

One non-blocking style observation remains: the first section says `两类测试同时开展` before the second section spells out the two test names. The reference is recoverable from the following section and all hard facts remain, so it is a readability WARN rather than a fact, relation or genre failure. It is not used to add another gate sentence from one sample.

## Host evidence

- branch commit under test: `85507cd7`
- companion: 54 files, fingerprint `70f2a6f9b77b61de1729f8199300fcf05b0d7a515f8ac6a548b5b99714738939`
- CodeBuddy CLI: `2.115.0`
- model: `deepseek-v4-flash`, effort `max`
- valid session: `cb-ov001-judgment-live-r2-20260822`
- duration: API 1m58.0s; wall 3m57.4s
- CLI usage report: about 15.7k output tokens and 248.3k cache-read tokens
- external harness/computer control: not used

The preceding session `cb-ov001-judgment-live-r1b-20260822` used `不超过260个非空白字符`, which the current length parser did not recognize as a registered specification. Over-length never armed; the default gate safely returned D0. That run is `ACTIVATION_INVALID`, not evidence against the candidate. R2 changed only the prompt phrase to `不超过260字` and reused the same D0/system/companion.

## Final draft

```text
关于采购数据脱敏测试设备的请示

市数据管理局：

一、采购原因

现有测试环境与生产环境共用部分计算资源，两类测试同时开展时资源紧张、任务排队等待，需配置独立测试设备。

二、采购内容与用途

拟采购数据脱敏测试设备2台，单台18.6万元、总37.2万元，用于脱敏规则验证和接口压力测试，预期可缓解资源紧张、减少测试任务等待。

三、资金和项目状态

已有专项资金可覆盖37.2万元。项目尚未批准，尚未采购。

四、请示事项

现申请同意使用已有专项资金37.2万元采购2台数据脱敏测试设备。

妥否，请批示。
```

## Disposition

The candidate judgment calibration has five-provider writer evidence, 15/15 three-case verifier directions and one valid CodeBuddy D1 lifecycle. The final integration additionally ran focused and full regression, Skill validation and a four-reviewer blind audit.
