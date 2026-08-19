# 中文数量透明归纳结果

## 目标与边界

既有真实篇幅不足样本中，材料明确“两方面工作”，两份真实 D1 分别使用“两项、前一项、后一项”和“两项工作相互衔接”。旧机械门在语义核验前直接以 `under_length_quantity_added_dropped_or_changed` 回退，无法区分结构概括与新增业务数量。

本原子只处理显式同数转换：材料或 D0 已明确“几方面”，D1 才可把同一组事项概括为“几项”并进入语义核验；“前一项、后一项”等回指不计作新业务数量。它不是直接放行，事项、范围、归属、状态和其他增量仍由既有 verifier 核验。两个小区改成三个小区、两场改成三场等独立数量变化继续机械回退。

## 真实同稿

- D0：106 字，SHA-256 `f1472c5c1fb88b83a40b61fc690e2c3b8b0c1ec686a1e5b127ca41cbe43bdc6c`。
- 历史真实 D1：206 字，SHA-256 `213c9cdc1a670b514dda3eb0cce636fa63bfb4e786c0777f3b04f75bd1f7e472`；含“两方面→两项”和“前一项/后一项”。
- 当前机械层生成 `quantity_summary` 关系复核项，不再以新增数量直接拒绝。
- `ollama-cloud/deepseek-v4-flash:0731`、max 对冻结增量返回 PASS；verdict 文件 SHA-256 `debbe4964e15b1dfb3dbb76a0b56268ad6ccf0ea425fb760cd63d02446e93fd2`。
- 同一事务复放选择 D1，逐字回显后 `delivery_verified=true`，终稿 SHA-256 与 D1 一致。

## WorkBuddy / CodeBuddy 在线反控

当前 branch 组装 CodeBuddy `under_length` companion：54 文件，fingerprint `67982f4e5925fdf67daba931eff09c322e9436d80484a23a3f684ded239b5d33`。WorkBuddy 5.3.13 / CodeBuddy CLI 2.115.0 使用 `deepseek-v4-flash`、max 完成 UserPromptSubmit、Skill Read/PostToolUse、Stop、修订、核验和回显。

在线 D1 为190字，SHA-256 `1eab0c17387f1830f9523ef49cadd366a482165eaf3aad0d3ce6fa6ebe58ad5e`。它新增“培训对象为窗口工作人员”，并把两处咨询内容另归纳为“上述两项内容”；机械层允许其进入语义层，verifier 以 `semantic_rejected` 选择 D0。最终交付 SHA-256 仍为 `f1472c5c…`，`delivery_verified=true`。runner receipt 绑定的源记录文本 SHA-256 为 `11935de272c2b0aa7656e53e82c9a3738d3507909b3b9c84f0d3562cc5e6755e`。

该结果同时证明窄放宽可以接纳安全透明归纳，也不会把含新增对象或错归属的同类数量表达直接放行。

## 最小验证

- `python -B -m unittest maintenance.tests.test_shared_hard_anchors -q`：16/16 PASS。
- `python -B -m py_compile chinese-official-writing/hooks/shared/hard_anchors.py chinese-official-writing/hooks/capabilities/under_length/runtime.py`：PASS。
- WorkBuddy / CodeBuddy 在线 runner：exit 0，`under_length_complete`，D0 精确交付。
