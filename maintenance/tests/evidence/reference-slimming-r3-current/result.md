# v1.6.22 后 references / Hook 冷审与定向审稿减载结果

日期：2026-08-31。固定起点：`main@6c15efca83916cd29b1036ed265f83fc1b70280f`。研究分支：`codex/post-v1622-reference-hook-audit-r1`。

## 结论

- `MT-004b-REVIEW-DIRECT-LEAF-R1/R2` 已通过当前路由基线、两轮五路真实审稿、直接工程门和756项全量，并以 fast-forward 合入本地 `main@c639b282`，状态为 `ENGINEERING_VERIFIED / MERGED_MAIN_NEXT_VERSION_CANDIDATE / EXCLUDED_FROM_FROZEN_V1.6.22`。它只处理用户已点名范围且只审不改的任务；格式、语气、AI 味、多层或综合审稿继续使用 `review-checklist.md`，可研点名完整性审稿继续只读既有可研细查叶。
- `ANTI-AI-SINGLE-SURFACE-ROUTE` 在三题15次基线中只有1次读取 `anti-ai-patterns.md`，状态为 `TERMINATED_BASELINE_LOAD_NOT_REPRODUCED`。不因14 KB静态文件大小拆英文、过程旁白或句群子叶。
- 旧 `REVIEW-LAYER-SPLIT-R1` 仍为 `REJECTED`。本轮新机制是点名范围的轻量执行页，不恢复段落/小节/全文四层物理拆分。
- 当前 Hook 冷审没有发现需要另开产品候选的 P1/P2；当前分支相对起点没有 Hook 产品差异。剩余证据缺口仅是尚未在真实宿主进程内故意制造 emit/子进程超时并核对墙钟不超过30秒，不构成本候选阻断。
- 冻结发布源 `codex/release-v1.6.22@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe`、82文件 SkillHub 包和33文件无 Hook ClawHub 包均未修改、未重建、未移动。

## 当前基线与真实任务

基线先运行7题×5家低成本 provider，共35条记录、33条精确路由有效：

| 题型 | 有效路由 | 基线读取 `review-checklist.md` | 裁决 |
| --- | ---: | ---: | --- |
| 请示/申请点名审稿 | 5 | 3 | 进入轻叶候选 |
| 情况报告点名审稿 | 5 | 4 | 进入轻叶候选 |
| 通知点名审稿 | 5 | 5 | 进入轻叶候选 |
| 可研摘要点名审稿 | 4 | 0 | 既有直达对照成立 |
| 三类去 AI 味改写 | 14 | 1 | 不建立拆分候选 |

五条路线均由 Codex CLI / OpenCodex catalog 以 `reasoning=max`、read-only、ephemeral、Hook关闭、零质量重抽执行：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `alibaba-token-plan/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

基线 usage 回执累计 input 5,521,277、cached input 4,273,583、output 190,437、reasoning output 92,126 token；用量只证明实际模型执行，不作为质量票。

## R1 / R2 结果

R1 新增2,208字节的点名审稿轻页并调整入口和报告叶路由。20组中19组技术有效：请示4/5、报告2/5、通知4/5读取新叶，三个正向题均不再读取16,510字节综合审稿页；可研有效4组均未读取新叶或综合页。19组有效对的实际读取总量相对固定基线少264,688字节，单对最大少48,395字节；该数只说明实际读取，不替代稿件裁决。

R2 只在轻页增加三项最小修正：普通文本输出形状、已有工作量/等待/成本足以支撑基本必要性时不强索次级证明、主体不一致时不得虚构委托或授权关系。轻页最终为2,841字节（Git对象字节；Windows工作树为2,864字节），相对综合页按当前Windows工作树计单次理论少13,646字节。20组中18组技术有效：请示3/4、报告4/5、通知3/5读取新叶，正向有效稿仍为0次读取综合页。可研有1/4被模型额外读取轻页，但未读取综合页、未改变点名范围或未决状态；确定性路由测试已锁定可研只读可研细查叶。

逐稿人工复核采用事实、状态、文种、只审不改输出形状和直接可用性五层判断：

- R2 的20份输出均保留核心数字、日期、主体和未决状态，没有交付改后全文。
- “另行通报”“处罚”等自动命中位于“未补/不得补”的审稿说明内，不是新增承诺，不按硬失败计算。
- 事实与常识直接支持的一层原因、必要性、即时作用、透明算术、条件性结论和合理建议均不按外扩处理。
- 一家未读取轻页的 MiniMax 通知仍建议“经研究，由业务协调处具体组织”；一家技术无效的 Alibaba2 请示仍索要设备年限等次级材料。这两项没有形成跨 provider、可归因于轻页的共同回退，保留为模型侧观察。
- Markdown 包装和过程说明没有完全消失；同类问题在基线也存在。R2 不继续堆第四轮提示，输出形状由现有正文交付规则和确定性测试保护。

## Hook 冷审

独立只读复审检查当前 `main` 的25秒 Stop共享预算、每次调用后的 ContextVar复位、D1/D0可信恢复、终态脱敏和单JSON stdout协议，未发现新的 P1/P2。当前分支没有修改 `chinese-official-writing/hooks/`；102项 Hook 生命周期、适配、under-length和层契约测试全部通过。

当前只保留一个低优先级证据缺口：真实宿主中人为拖慢 emit/子进程到墙钟上限的在线样本尚未执行。现有模拟单调时钟、真实 `handle_stop`、stdin/stdout 主入口和九宿主组装契约已覆盖代码路径；没有实际失败前不为该缺口增加新 Hook、线程或超时门。

## 进一步拆分空间

候选前 canonical 有31个 reference、182,925字节；本候选新增轻页后为32个、185,943字节，活动相对链接无失效。静态冷审仍能看到下列大页内部的场景簇，但没有新的实际读取证据，均只记 `OBSERVE_TRACE_FIRST`，不进入活动 `HOLD`：

| 观察项 | 理论空间 | 当前不立项原因 |
| --- | --- | --- |
| 调研/研究/可研从 `genre-playbooks.md` 独立 | 约4.2—4.5 KB/次 | 先要两家全新长调研或研究报告复现组合页过读；不能遗漏论证和估算状态 |
| 请示场景从 `argument-chains.md` 独立 | 约3.2—3.5 KB/次 | 与申请/请示叶已有骨架重叠，须先证明整页实际伴读 |
| 一般 Word 与红头段从 `format-gbt9704.md` 分层 | 约1.8—3.0 KB/次 | 红头 DOCX 属付费候选边界且必须渲染验证，不以 Markdown 静态拆分代替 |
| 讲话在中央用语页与组合 playbook 间消歧 | 理论约4 KB/次 | 旧讲话任务卡已拒绝；先看当前真实路由，不能堆旧提示词 |
| `handling-elements.md` 按场景减载 | 理论约4—5.5 KB/次 | 缺少两家共同整页过读，且最容易破坏统一缺项处理 |

中央 `formulaic-language.md` 不复制成多份词库；`review-checklist.md` 与 `final-review-layers.md` 职责相邻但不合并；报告、方案叶中的少量自包含重复不为节省包体而删除。下一次若继续 reference 减载，优先只做 `RESEARCH-PLAYBOOK-LEAF-R1` 的当前基线 trace；基线未读组合页即终止，不先建产品叶。

## 提交、原始证据与验证

- `492dde18`：新增点名审稿轻页和最小路由原型。
- `66d5dd6d`：只收紧输出形状、次级材料和主体授权三项边界。
- `ff61404e`：同步五套公开宿主镜像并建立确定性直达/综合/可研反控。
- 原始终稿、trace、stderr、usage与实际读取位于忽略目录 `output/reference-slimming-r3-current/`。
- 基线 summary SHA-256：`A37BD79848AB96751A025288C2607E35D8BA405657EB932884E420F9F2134183`。
- R1 summary SHA-256：`D83D0F7FFD6E0F456BF925DDF09F15C3FBA5B32DF813FD6540ED879CB6B415A6`。
- R2 summary SHA-256：`843767A4F2CFB0F6E9BBBAE5354332801C3AF5D66F2618240072863092603FC5`。

已执行：

```text
py -3 -m unittest maintenance.tests.test_promptfoo_eval maintenance.tests.test_skillhub_package_builder maintenance.tests.test_status_ledger_consistency maintenance.tests.test_oc003_feasibility_state_layering
Ran 103 tests；OK

py -3 -B -m unittest maintenance.tests.test_gate_stop_hook maintenance.tests.test_host_gate_adapter maintenance.tests.test_under_length_capability maintenance.tests.test_hook_layer_contract
Ran 102 tests in 49.752s；OK

py -3 -B -m unittest discover -s maintenance/tests -p "test_*.py"
Ran 756 tests in 115.722s；OK

py -3 maintenance/tools/sync_adapters.py
五套公开宿主镜像同步完成

git diff --check
PASS
```

本结果不改版本号、不创建或移动 tag、不推送、不发布。候选已 fast-forward 合入本地 `main@c639b282`；冻结 `codex/release-v1.6.22@62ba9e82` 及其82/33文件包仍逐字不变。
