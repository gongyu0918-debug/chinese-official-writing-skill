# `UL-006-INCIDENT-ONLY-R1` 真实写稿与隔离结果

日期：2026-08-30。

终态：`VALIDATED_NEXT_RELEASE_CANDIDATE / NOT_MAIN_YET / NOT_V1.6.21`。

## 候选与判定边界

候选 `a4c7aa4c24b66cf7ff011f639b73bc72e1b6397c` 只从隐式篇幅入口移除情况说明和办理通知，保留事故通报、显式字数能力、动态材料关系、修订指令、机械门和 verifier。上一轮事故通报已有 Alibaba Token Plan 1 与 OpenCode Go 两份真实 D1 被选择并按终稿 hash 交付，本轮按预登记迁移这两份功能收益，并用全新事故稿观察副作用。

合理续报、事实与常识直接支持的一层归纳不按材料外扩判失败；只把候选差异直接造成的事实、状态、文种、用户上限或交付回退计为失败。`3人/3名`、`无人受伤/未造成人员受伤`、`城管/城市管理`、`通行未中断/通行未受影响`按同一事实关系人工复核，不以逐字检查器的假阴性代替稿件判断。

## 五家真实结果

使用以下五条 Codex CLI 低成本路线，思考强度均为 `max`：

- `alibaba-token-plan/deepseek-v4-flash-0731`
- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

每家运行一份全新事故通报、一份情况说明禁用控制、一份办理通知禁用控制和一份80字显式上限控制，共20份有效终稿。

| 项目 | 结果 | 判断 |
| --- | --- | --- |
| 全新事故通报 | Alibaba1 建立动态事务，103→143字的 D1 因语义拒绝安全交付 D0；其余四家初稿114—135字，已离开近材料区间而不启动 | 五份终稿均完整保留日期时间、地点、3人、无伤、城管与消防、警戒、排查、通行、原因待查和排查进行状态；没有候选机制相关硬回退 |
| 情况说明禁用控制 | 五家均为 `disabled_genre_no_start`，无技术失败 | 移除入口生效；部分普通初稿仍省略“本次材料未附”，这是停用该入口的既有理由，不冒充候选回退 |
| 办理通知禁用控制 | 五家均为 `disabled_genre_no_start`，无技术失败 | 移除入口生效；本题未新增落款、日期或把渠道反推为发文主体 |
| 80字显式上限 | 五家均为 `explicit_bypass`，无技术失败 | 用户上限继续优先于隐式篇幅信号 |

Alibaba2 的事故初稿加入“第一时间”，属于未启动 Hook 时的普通模型措辞残余；本次产品 diff 没有改变事故生成或审核逻辑，因此不归因给入口收窄，也不把它作为通过证据。正常“后续情况将及时通报”按阶段性通报交付边界保留。

## 技术异常与有效样本选择

最初合并运行在目标题完成后，因新增控制 sentinel 缺失而中止；随后并行组装又在 Alibaba1、OpenCode 控制题发生插件缓存竞争。上述失败记录不计入结果，也没有覆盖或删除。最终有效控制固定为：

- `output/ul006-incident-only-r1-controls`：Alibaba2、Ollama、MiniMax；
- `output/ul006-incident-only-r1-controls-r2`：Alibaba1、OpenCode；
- `output/ul006-incident-only-r1-live`：五家事故题。

逐字检查器对上述等义表达产生假阴性，已由人工按主体、动作、对象、数量和状态关系复核；未改写评判标准来追求通过。

## 工程门与决定

- 定向篇幅能力测试：`python -m unittest maintenance.tests.test_under_length_capability`，33/33 通过。
- 直接相关回归：`python -m unittest maintenance.tests.test_under_length_capability maintenance.tests.test_gate_stop_hook maintenance.tests.test_skill_boundary maintenance.tests.test_promptfoo_eval`，239/239 通过。
- `python -B maintenance/tools/sync_adapters.py` 连续运行：五个普通兼容包同步完成，产品镜像无新增差异。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python -m py_compile` 覆盖篇幅 runtime、中央 coordinator 和定向测试；`git diff --check` 通过。

本候选可以作为 v1.6.21 之后的小版本候选，但不进入已经固定的 v1.6.21 RC。情况说明和办理通知的当前隐式机制终止，不保留 `HOLD`；只有出现新机制或新的跨 provider 反例才重开。事故入口后续若改变修订提示、机械门或 verifier，须重新取得 D1 生命周期，不得继续迁移本轮证据。

## 实际命令

- `python maintenance/tests/evidence/ul006-incident-only-r1/run_live.py --prepare`
- `python maintenance/tests/evidence/ul006-incident-only-r1/run_live.py --provider <alibaba1|alibaba2|ollama|opencode|minimax>`
- `python maintenance/tests/evidence/ul006-incident-only-r1/run_controls.py --prepare`
- `python maintenance/tests/evidence/ul006-incident-only-r1/run_controls.py --provider <provider>`
- `python -m unittest maintenance.tests.test_under_length_capability`
- `python -m unittest maintenance.tests.test_under_length_capability maintenance.tests.test_gate_stop_hook maintenance.tests.test_skill_boundary maintenance.tests.test_promptfoo_eval`
- `python -B maintenance/tools/sync_adapters.py`
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`
- `python -m py_compile chinese-official-writing/hooks/capabilities/under_length/runtime.py chinese-official-writing/hooks/core/gate_stop_hook.py maintenance/tests/test_under_length_capability.py`
- `git diff --check`
