# HK-008 Hook 终态数据减载结果

日期：2026-08-22。

## 结论

`PASS_CANDIDATE_ELIGIBLE`。当前候选在终态 Stop 后删除本轮原请求、D0、候选稿、删除 span、观察包、已选正文和 capability 事务文件，只保留 hash、阶段、选择、交付状态、Stop 计数和删除失败数。CodeBuddy 2.115.0 的一份真实采购申请完成完整生命周期，用户可见终稿逐字未变，终态记录没有正文或提示词，`raw_artifact_delete_failures=0`。

该结论只准入“本地终态数据减载”原子，不改变 Hook 默认关闭、单 capability、有限 Stop 或写稿语义，不证明当前 Hook 的等待和 Token 成本已经适合默认开启。

## 触发与外部边界

- 2026-08-22 实时 SkillHub API 中，`chinese-official-writing@1.6.13` 的 Keen 为 `benign`，Sanbu 为 `suspicious`。Sanbu 指向两项行为：可选 Hook 参与终稿门禁，以及 Hook 在插件数据目录保存请求/稿件快照而没有清理。
- 第一项已有明确的预览、组装、加载/启用和关闭边界，普通 Skill 与 ClawHub 33 文件无 Hook 包不进入该路径；第二项经源码确认属实，因此启动本原子。
- OpenAI Codex、Claude Code 和 CodeBuddy 官方 Hook 文档用于核对生命周期、插件根和数据根。当前公开文档检索没有找到替第三方 Hook 规定其自有快照保留期限的宿主契约，因此由候选承担本地最小化责任。
- 社区实现只用于确认“Hook 输入可能含原始、未脱敏内容，不应无清理地长期记录”的风险形态；未复制第三方文字、模板或代码。

来源：

- SkillHub 当前记录：<https://api.skillhub.cn/api/v1/skills/chinese-official-writing>
- ClawHub 当前无 Hook 包：<https://clawhub.ai/gongyu0918-debug/chinese-official-writing>
- CodeBuddy Hooks：<https://www.codebuddy.ai/docs/cli/hooks>
- CodeBuddy 插件：<https://www.codebuddy.ai/docs/cli/plugins-reference>
- Codex Hooks：<https://learn.chatgpt.com/docs/hooks>
- Claude Code Hooks：<https://code.claude.com/docs/en/hooks>
- 社区风险形态：<https://github.com/morganlinton/Albatross>

## 实现边界

1. 只在终态 allow，或 Stop 判定本轮不启动门禁时执行清理；修订、验收和 emit 中间态仍保留完成当前有界事务所需的数据。
2. 普通交付、保护性扩写、篇幅不足、超长收束、交付洁净度和重复清理共用同一终态清理入口。
3. 删除目标必须 resolve 到本 companion 的 `PLUGIN_DATA/candidate-ai-gate-hook` 之下；数据根本身和外部路径永不删除。
4. 重复 Stop 识别 `raw_turn_data_redacted` 后立即放行，不重建事务。
5. 宿主或进程在终态 Stop 前中断时，未完成快照仍可能留存。README 明示精确数据子目录的人工清理边界；本原子没有用后台 TTL 或全目录递归清扫扩大工程面。

## 确定性验证

运行：

```text
python -B -m unittest maintenance.tests.test_gate_stop_hook maintenance.tests.test_under_length_capability maintenance.tests.test_over_length_capability maintenance.tests.test_delivery_cleanliness_capability maintenance.tests.test_repetition_cleanup_capability maintenance.tests.test_hook_layer_contract
python -B -m py_compile chinese-official-writing/hooks/core/gate_stop_hook.py chinese-official-writing/hooks/adapters/host_gate_adapter.py
python -c "import json; json.load(open(r'chinese-official-writing/hooks/host-capabilities.json', encoding='utf-8')); print('host-capabilities JSON OK')"
python -B -m unittest maintenance.tests.test_repository_reachability maintenance.tests.test_skill_boundary
python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
git diff --check
```

结果：84项 Hook focused 测试、84项可达性/Skill 边界测试通过；Python 编译、JSON 解析、Skill Creator quick validate 和 diff whitespace 检查通过。覆盖普通终态、无事务 Stop、明确旁路、重复 Stop、外部路径保护、终态回执写入失败时删除本轮精确原始 record，以及五项 optional capability 的终态脱敏。曾按旧记忆尝试仓内 `maintenance/tools/quick_validate.py`，因该路径不存在退出1；随后改用当前 Skill Creator 的真实脚本并通过，不把前一次记为通过。

## CodeBuddy CLI 真实生命周期

### 组装与校验

```text
python -B maintenance/tools/assemble_hook_companion.py --host codebuddy --output output/current-verification/20260822-hk008-retention/companion
node "E:\Program Files\WorkBuddy\resources\app.asar.unpacked\cli\bin\codebuddy" plugin validate output/current-verification/20260822-hk008-retention/companion
```

组装结果：`host=codebuddy`、`capability=delivery_review`、54文件、未安装、未启用、未联网；CodeBuddy manifest 校验通过。CLI 版本为2.115.0。

### 无效首跑

第一次用单次 `--print --plugin-dir` 启动。真实采购申请可用，Skill、三次 Read 和 Stop 均实际发生；但 inline 插件在该进程的 `UserPromptSubmit` 之后才完成加载，本地 Hook 没有接到最初的 UserPromptSubmit，Stop 只返回 allow，没有建立门禁事务。该稿只记为写稿有效，HK-008 生命周期记为 `TECHNICAL_INVALID`，不计通过。

### 有效持久会话

第二次用 `--input-format stream-json --output-format stream-json` 先启动同一 CLI 进程，再提交同题，session 为 `hk008-codebuddy-20260822-r3`。模型为 `deepseek-v4-flash`、effort `max`；只要求 Skill/Read，未使用电脑控制、远程控制、Shell 或文件写入。

真实题要求起草设备采购申请：保留4台、其中2台于2020年购置、2026年8月18日至20日连续三天高峰平均等待约38分钟、拟采购2台、单价不超过28000元、年度信息化设备预算列支、品牌/供应商未定、采购方式待审核；允许一层合理原因和预期影响，禁止把预期写成成效。

观察结果：

- CodeBuddy 实际执行 `UserPromptSubmit → Skill → Read × 3 → Stop → 语义 KEEP → Stop → emit → Stop allow → FinalStop`。
- 第一个 Stop 定位“品牌、供应商尚未确定，采购方式待审核”一句；模型选择 `KEEP`。可见终稿与 D0 逐字一致，既保留未决状态，也写出“为缓解任务排队”和“预计可……提升处理效率”的低强度目的/影响，没有升级为既成成效。
- 3个 Stop 事件中2次为有界阻断，终态记录 `stop_attempts=2`、`hook_phase=complete`、`emit_seen=true`、`delivery_verified=true`。
- 完整生命周期耗时53.625秒；CodeBuddy 结果统计输入61600、输出5693、cache creation 16032、cache read 45568。该成本继续支持“默认关闭、窄能力 opt-in”，不能因安全清理通过而淡化体验风险。

终态 core 记录：

```json
{"bootstrapped_by_stop":true,"bypass":null,"data_retention_state":"raw_turn_data_redacted","delivery_verified":true,"emit_seen":true,"emitted_sha256":"4069e330414f46b46e8295e1b992c0521421d674f8060816a8fad6b03adbbbca","hook_phase":"complete","last_action":"emit","raw_artifact_delete_failures":0,"run_id":"717e0b86-21d3-49b1-8d83-122e76835279","schema_version":1,"skill_seen":true,"stop_attempts":2}
```

适配层只保留：

```json
{"counter":1,"schema_version":1,"turn_id":"workbuddy-1-25b86e5631347632"}
```

会话对应的 ordinary transaction 文件和 `-inputs` 目录均已删除；只剩空的会话级 transactions 目录。对终态 record 与 adapter record 搜索“图形工作站”“28000”均无命中。

## 状态与剩余风险

- 候选可以接入公开研究候选，但尚未合入 `main`、未推送、未发布，SkillHub 当前扫描状态不会因此自动改变。
- CodeBuddy 自身 debug、trace、会话转录和通用日志属于宿主留存面，本原子不越权删除；本结论只覆盖该 companion 自己写入的插件数据。
- 终态前异常退出仍可能留下原始快照；当前采用透明说明和精确人工清理，不先造后台 TTL。
- 单个原始事务文件删除失败时以 `raw_artifact_delete_failures` 记录；若脱敏回执本身无法原子写回，候选只删除该轮精确 raw record，宁可丢失回执也不保留正文。未做跨进程崩溃注入，record 删除也被文件系统拒绝时仍是剩余风险。
- 有效会话使用 CodeBuddy 固定的 `chinese-official-writing-inline` 插件数据根和唯一 session 子目录，而不是独立改写宿主数据根；核验只读取该 session 的精确路径，没有删除既有其他任务数据。
