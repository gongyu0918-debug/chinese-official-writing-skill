# HK-004 DeepSeek Harness adapter R1 结果

## 结论

状态为 `CANDIDATE_VERIFIED_HEADLESS / NOT_MERGED / NOT_PUSHED / NOT_RELEASED`。DeepSeek Harness `0.1.1-rc.2` 已形成原生 Profile Bundle 候选，当前只声明 headless + `delivery_review` 在线闭环。Qoder 依用户最新范围终止本轮工作，没有 adapter 候选。

首轮原型曾出现3条 `allow` 回执，但随后发现源码探针误把“组装后 core 路径”用于 canonical 源码树，Python core 实际未启动；这3条全部作废，不能作为 Hook 证据。路径修正后，才出现真实 `block → block → allow`、core 终态记录和原始文本脱敏。最终候选安装测试使用组装包，不再依赖该源码探针。

## 真实安装与写稿

最终源码组装结果：54文件，fingerprint `06c0359227d7d6e5a5a1409235e74a9dc3466af17e3f3c3c581966c4fc65d400`，`installed=false/enabled=false/network_used=false`。在全新隔离 `DSH_HOME` 中运行 `dsh plugin --profile headless add <absolute-companion>` 后，profile manifest 自动增加 `chinese-official-writing-gate-dsh`，`--dump-config` 出现同名 bundle 行；会话继续使用默认 `session.jsonl.zstd`，adapter 不读该文件。

### W1 稀疏采购申请

- 模型：OpenCodex `alibaba-token-plan-2/deepseek-v4-flash-0731`；导出模型无 `reasoningEfforts`，实际 request header 只含 provider/model。
- session：`session-82537533-351d-41bc-a77f-a42330e31783`。
- Stop：位置0 `block`，D0 hash `0d6b1c2e3c63eb8c9e2ef86d08a9144e58290a8f60b014c92d2769e9faa1cf1c`；位置1中间核验响应 `block`；位置2同一 D0 hash `allow`。最终 stdout 与 D0 一致。
- 质量：正文直接可用；保留2台、18项、拟采购4台、96万元上限、2026年专项预算、技术参数初步测算、供应商/采购方式/交付日期未定和待审批。原因前置为缓解排队/延迟，影响使用“预计”“可”，未写成既成采购或既成成效。无过程说明、字数、自评或横线包装。

### W2 未决情况说明

- 模型：OpenCodex `opencode-go/deepseek-v4-flash`，实际 request header 显式 `reasoningEffort=max`。
- session：`session-7f962703-974c-4c1f-b268-b7ab77bd70b4`。
- Stop：位置0 `block`，D0 hash `1aa43a0e6ee7ab6eace63d0983e6926b6a27a8812034fb4396f92c935eb55696`；位置1同 hash `allow`。最终 stdout 与 D0 一致。
- 质量：保留完整日期、两轮联调、860项字段映射、37项待补、协调会未决定上线和安全测试“可安排/尚未安排”。“尚未正式上线、上线时间尚难确定”属于由当前试点阶段和未决事项作的一层低强度结论，没有写成已上线；“待相关事项落实后再行确定”是非承诺性收束。该稿目标通过，但这类由“未作决定”推到整体状态的表达仍应在以后新材料中观察，不能据一稿扩成禁词或全局规则。

### W3 最终源码复跑

- 在异常路径 fail-open 和 dispose 清理补强后，重新组装到新目录、安装到第二个全新隔离 profile，再跑 W1 同题；不是复用旧组装包。
- 模型：OpenCodex `opencode-go/deepseek-v4-flash`，实际 request header 为 `reasoningEffort=max`；session `session-c993cafc-1269-4995-b257-22ab1f1f3d41`，实际调用当前 Skill。
- Stop：位置0 `block`，D0 hash `2039e704c39bca5e518320b8797fc0517aff2bf3330fc391d7d13d1680d7c560`；位置1中间核验响应 `block`；位置2同一 D0 hash `allow`。core 终态 `delivery_verified=true`、`raw_artifact_delete_failures=0`。
- 质量：保留全部事实和未决状态；“为保障稳定运行”“缓解排队、降低响应延迟”是由排队/延迟作的一层原因与预期影响，“预计可满足”仍为预期而非既成成效。只交申请正文，无过程包装。该轮确认最终 adapter 正常路径相对前一组装包无回退。

两个终态 core record 均为 `data_retention_state=raw_turn_data_redacted`、`delivery_verified=true`、`raw_artifact_delete_failures=0`，只留 hash/阶段/Stop 数；确定性 smoke 另覆盖同名外部 Skill 不启动、换回合精确 HostAbort 和多 Stop 终态。

## 实际命令与结果

```text
dsh --version
opencodex --version
opencodex help export
opencodex export --client dsh --out <isolated-DSH_HOME>/settings.yaml
py -3 maintenance/tools/assemble_hook_companion.py --host deepseek-harness --output <new-output> --capability delivery_review
node --check <assembled>/index.mjs
dsh plugin --profile headless add <absolute-assembled-directory>
dsh --profile headless --dump-config
dsh --profile headless <W1 prompt>
dsh --profile headless <W2 prompt>
py -3 -m unittest maintenance.tests.test_deepseek_harness_gate_adapter -v
py -3 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
py -3 -m unittest discover -s maintenance\tests -p "test_*.py"
```

上述命令均实际运行；DSH 专门测试2/2、adapter/层契约8/8、可达性与状态一致性13/13、全量 unittest 723/723通过，Skill Creator quick validate 返回 `Skill is valid!`。另有一条 `py -3 maintenance/tools/quick_validate.py` 因仓库不存在该路径而退出1；它不计验证，随后改用上列系统 Skill Creator 脚本成功运行。

## 剩余边界

- 当前只在线验证 Windows headless；TUI/Web、POSIX 和后续 DSH 版本需各自重跑，不从共用事件名外推。
- 只有 `delivery_review` 取得真稿 Stop 闭环；其他 capability 可静态组装，但尚无 DSH 在线 D1。
- shell 工具映射已实现并进入确定性结构测试，真实 W1/W2 只观察到 Skill/read；`bash|pwsh` 的真实 PostToolUse 尚未单独取样。
- DSH 原始 profile 与宿主日志不属于 companion 终态清理范围。硬退出仍可能留下当前未完成事务，按 README 精确人工清理。

最终范围与固定基线消融见 [`review.md`](review.md)。
