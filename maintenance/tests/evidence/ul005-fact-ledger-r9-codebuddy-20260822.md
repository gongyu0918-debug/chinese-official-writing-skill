# UL-005 单稿事实台账 R9：CodeBuddy 正反生命周期

## 结论

`UL-005` 的本轮来源绑定原子完成：同一安全 D0 在当前 WorkBuddy 5.3.13 内置 CodeBuddy CLI 2.115.0、`deepseek-v4-flash`、`max` 下形成 61→114 字的可用 D1，完整事实台账通过后实际选择 D1；同一候选又用一份含强保障、材料外用途和多余请批语的 111 字风险 D1 验证逐字回退 D0。两次最终交付 hash 均由 Hook 回显闭合。

本轮只使用 CodeBuddy CLI 和仓库 companion，没有桌面控制，没有第三方写稿 harness。候选不再因模型把“允许推断”的通用说明填成核心 source 而误拒安全 D1；同一来源 span 的机械约束本身没有放宽。

## 真实失败驱动的最小修正

R8 先运行一条自然长稿：原生 Skill 已被宿主识别，但稿件含标题共 1001 字，已落在用户 1000—1200 字区间，因此没有触发 under-length，只记 `INVALID_NO_TRIGGER`。该稿还出现培训内容、全流程办理、材料缺失和业务影响等材料外判断，不能当作质量通过。

随后固定一份事实安全 D0，加入真实但无关的“办公室收到三份纸质档案”，允许一层低强度原因、目的或预期。R8 生成的 D1 为 114 字，未使用无关事实，模型返回 `verdict=PASS` 和完整 `fact_ledger`，但把计划句、问题句和通用授权句分开填作核心 source，机械同 span 复核以 `semantic_rejected` 选择 D0。该结果定位到 verifier 填表指引不足，不是 D1 内容失败。

候选 `651b36b1` 只补充一条填表指引：合理推断的核心 source 必须从同一条直接事实或通常功能锚中拆取，不得把允许推断或强度说明本身当作核心 source。严格同 span 校验、无关 span、局部相关但新增谓语和既成成效拒绝逻辑均未修改。

## R9 正反样本

| 样本 | D0 / D1 | 实际选择 | 关键结果 |
| --- | --- | --- | --- |
| 风险候选 | 61→111 字 | D0 | D1 新增“保障系统正常运行”“日常业务办理”“现申请予以批准”；`reason=semantic_rejected`，D0 与交付 SHA-256 同为 `2436bbbd989decff7caea52db1299be808c727f0f86f20003352e9f1854dee3d` |
| 受控正向候选 | 61→114 字 | D1 | D1 只写“为缓解……拟申请”“有助于提升……提供支撑”，保留“尚未批准”，未使用无关 3 份档案；`reason=semantic_pass`，候选与交付 SHA-256 同为 `ae0ff3d4cbc3425150015f404154093dec0221a7f043238e6da15127958bb110` |

正向样本的 D1 为：

```text
关于办公系统资源扩容的申请

现有办公系统高峰时段响应缓慢，技术排查认为资源承载压力较大。为缓解高峰时段响应缓慢问题、应对资源承载压力，拟申请扩容系统资源。扩容有助于提升系统资源承载能力，为办公系统平稳运行提供支撑。该事项尚未批准。
```

## 宿主与原始证据

- R9 CodeBuddy companion：54 文件，fingerprint `b1ccea4a5e743cd9948f82659d8af95d73c32e2ec637783a1c55d4a643b27656`；`plugin validate` 通过。
- R9 session JSONL：`cb-ul005-r9-guided-ledger-20260822.jsonl`，353922 bytes，SHA-256 `F7E5EB99221E646BC8E41D4D038C047D7155AC6BB8409D487BDA12C1D8895821`。
- 风险样本 Hook record：`workbuddy-2-0b70f77bfda28467.json`，3560 bytes，SHA-256 `FE85ECC370032F22B398613A181758172FCA540EF8F78D8AE51FF2FBC9B98F92`。
- 正向样本 Hook record：`workbuddy-3-8a510d77a334ab0b.json`，3577 bytes，SHA-256 `DACAFC6CCE1E51208086AB88E733F76C41EA453591480A6A092FEAB619E8BA90`。
- R8 自然无触发 session：564724 bytes，SHA-256 `CE5F6F15D446CC7447C6A134A19EC76B6CFD392712A3189C0C0620067FCFD44E`。
- R8 完整台账但机械拒绝 session：327190 bytes，SHA-256 `773F6515C64AEE2B43CBC4B06828ED2925934A0F7B1012A1D4063675173946EE`。

## 实际验证

```text
python -B -m unittest maintenance.tests.test_under_length_capability -q
Ran 25 tests — OK

python -B -m unittest maintenance.tests.test_under_length_capability maintenance.tests.test_shared_hard_anchors maintenance.tests.test_host_gate_adapter maintenance.tests.test_hook_layer_contract -q
Ran 62 tests — OK

python -B maintenance/tools/assemble_hook_companion.py --host codebuddy --capability under_length --output output/current-verification/20260822-ul005-r8-codebuddy-r9/companion
54 files; fingerprint b1ccea4a5e743cd9948f82659d8af95d73c32e2ec637783a1c55d4a643b27656

node <WorkBuddy CodeBuddy CLI> plugin validate <R9 companion>
Validation passed
```

本结果关闭的是 `UL-005` 来源台账与安全推断的当前原子，不把一次受控 D1 冒充所有文种和所有模型均能自然扩写。自然修订仍可能生成风险 D1，但当前负向样本已经证明该风险会回退，而不是放行。
