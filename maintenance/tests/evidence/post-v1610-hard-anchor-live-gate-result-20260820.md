# v1.6.10 后共享硬锚生命周期结果

## 范围

- 候选提交：`c86c4e712fabe3ffa877fc2e954d1b081f3ceb1a`。
- 只验证两条同一 D0 边界：修辞性“一方面/另一方面”压缩；“会后三天”被改成“会后两天”的回退。
- 不改篇幅语义 verifier，不扩大全量写稿矩阵。

## 真实在线样本

Claude Code 2.1.195 以临时 `over_length` companion 加载当前候选，调用 `alibaba-token-plan-2/deepseek-v4-flash-0731`、`max`、0 retry。修辞样本完成 UserPromptSubmit、Skill Read/PostToolUse、Stop、重复观察、压缩、语义核验和精确回显：D0 `cd124bd...e6dd1d`，D1与终稿均为 `db1c9f...55e0f7`，`selection=D1`、`reason=semantic_pass`、`delivery_verified=true`。companion 54 文件，fingerprint `80091630f2ad62a677c05701b0b57e446144a7495c66143c4c65ebada64632af`。

同批相对期限在线样本完成相同三事件并安全选择 D0，但模型实际保留了“三天”，因删去责任承载内容以 `over_length_responsibility_subject_dropped` 回退；该臂只证明在线失败回退，不计入相对期限目标命中。

## 同稿产品生命周期复放

在当前产品 core/runtime 上复放同一 D0：129字原稿中的“会后三天”被95字候选改为“会后两天”，其他责任主体保持。观察、修订、机械门和精确回显完整执行；候选以 `over_length_quantity_added_dropped_or_changed` 选择 D0，最终交付哈希逐字等于原稿 `43efbeb7...7f326a`，`delivery_verified=true`。

这条复放验证共享硬锚本身；宿主 adapter、hooks.json 和 coordinator 相对已通过的当前 Claude/WorkBuddy/Codex 在线样本没有变化，不把复放冒充新的宿主在线注册证据。

## 无效尝试

- R1 首臂把预设候选直接当作首稿，未建立目标篇幅事务；第二臂停止。
- R2 首臂未读取 Skill，缺少 PostToolUse/skill-seen，未建立事务；第二臂停止。
- 两批均不计效果，不作为补样或通过证据。

## 绑定

- R3 manifest SHA-256：`9bd347bc76f09dda84cd89d81d087c63d42cd663d70868269b3edcb6d6160585`。
- 修辞在线 receipt SHA-256：`e7e2c5d15b1528e372e33d53cee08c1d7972dce330daeef2c7a0a016894fdf94`。
- 相对期限在线 receipt SHA-256：`884a4e6cb7cfa178a66bc79f35476a5e4198530049d9b4a9d7988a1239fff398`。
- 相对期限复放 SHA-256：`80019aa8e9ba11aca384aef9782d207bfe1614be6e4cc3c2568adeec0365493f`。
- 当前 `hard_anchors.py` SHA-256：`b4f90475ea0aa000586e6222e16689ddd0790e5517f5b5adc2afb28960a20698`。
- 原始流、stderr、companion 和运行态保存在 ignored 的 `output/post-v1610-hard-anchor-live-gate/`。

## 结论

目标边界通过：修辞性“方面”不再被误当业务数量而阻止压缩；相对期限中的真实中文数量变化仍在机械层选择 D0。该窄修复可以合并；`UL-005`、付费组合和提纲修正继续 HOLD。
