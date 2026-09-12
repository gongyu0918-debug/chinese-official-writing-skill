# Pro Hook 接续便条

状态：2.0 测试线仅本地保存 Hook 去向，Pro 任务暂缓激活；2.0 暂不发布。本轮不发送 Pro 通知、不安装、不激活；没有改动其他仓库的 HANDOFF 文件。1.x 稳定线独立维护和发布，保留其既有 Hook 的 MIT 授权。

## 保留位置

- 分支：`codex/pro-hooks-preserved-20260912`
- 精确提交：`3b6f273b6ee4ea583e7c0ade8311ad1f262d7159`
- 保存的产品资产：`chinese-official-writing/hooks/` 下 48 个文件、`scripts/review_gate.py`、`references/delivery-review-gate.md`，合计 50 个文件；同一提交保留对应工具、测试和历史证据。
- 历史参照版本：已核实本地发布 tag `v1.6.34` 存在；此便条不新增版本或发布声明。

## 已做验证

移除前运行：

```powershell
python -m unittest maintenance.tests.test_hook_layer_contract.HookLayerContractTests.test_maintenance_assembler_produces_nine_self_contained_plugins maintenance.tests.test_body_wrapper_route maintenance.tests.test_delivery_cleanliness_capability
```

结果：14 项通过，覆盖 9 个宿主 companion 组装、正文包装与交付洁净协议。这是组装和本地协议验证，本轮没有重新证明各宿主的原生生命周期执行。后续 Pro 修改路由或协议时，按实际受影响宿主补真实执行。

## 许可与接续

普通 Skill 及普通脚本继续采用 MIT。2026-09-13 用户更新分线要求：1.x 稳定线及其既有 Hook 维持 MIT 授权，撤回将 v1.6.34 作为所有后续 1.x Hook 授权截止点的笼统表述。2.0 测试线不包含 Hook；另建的 Pro 专属内容按其许可发布，复用的 MIT 代码及第三方代码保留各自版权与许可声明。

未来接续需分别核对 MIT 普通能力更新与 Pro Hook 保存资产。MIT 候选中的 Hook 删除记录用于收窄公开产品，不能直接覆盖 Pro 的 Hook、适配器、组装器或测试。具体步骤见 [普通 Skill 与 Pro 同步](../specs/public-paid-sync.md)。

篇幅统计可复用旧 Hook 的纯计算代码，作为普通 `draft_length.py` 由写作规则调用；`prose_lint.py` 保留文稿复核兜底。两者独立运行，不依赖 Agent 生命周期。
