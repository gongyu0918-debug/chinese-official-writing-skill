# v1.6.7 Hook 重构后真实生命周期 smoke 结果

结论：**PASS（真实 D0 生命周期）**。

## 执行结果

- Claude Code：`2.1.195`
- 模型：`alibaba-token-plan-2/deepseek-v4-flash-0731`
- 思考档位：`max`
- 调用：1 次，外层重试 0，耗时 404.407 秒，未超时
- 静态 companion：51 个源文件；组装时 fingerprint 为 `4e4ad8aff34307d71b45d4f4c9616d52bd75adf01e775f49dce06fc54241e0e1`
- 正式 manifest SHA-256：`d56e5e47a3033f69f14604c9a8720110933b090b2c0b311a9bda0438850bd56d`

实际读取了组装包内 `SKILL.md`、`information-selection.md` 和 `task-route-cards.md`，没有范围外读取。`UserPromptSubmit`、3 次 `PostToolUse:Read` 和 2 次 `Stop` 均有 started/response 记录，companion 已注册，本地 adapter turn 和门禁 transaction 均已落盘。

事务检测 1 次，finding 为 0，状态为 `TERMINAL_D0`，reason 为 `no_review_candidate`。最终稿、D0 snapshot 与 selection claim 的 SHA-256 均为 `ed875f3c83c33d550f96704fd3ea3845c1c891d5fc98ab63af1f311381433ac6`，证明第一次 Stop 阻断后的精确 D0 回显闭合。

正文共 191 个非空白字符，落在 180—260 字区间；预注册的日期、时间、时长、核查范围、记录数量和未决状态全部保留。该稿没有进入 repair/verdict，因此本结果只证明行为保持型重构后的真实普通交付链可用，不证明 D1 修订质量。

## 运行期缓存说明

宿主执行时在 companion 内产生了 1 个 ignored `__pycache__/gate_stop_hook.cpython-313.pyc`。正式 manifest 的旧字段把该运行期缓存计入全树 fingerprint，得到 `63c3e3375da3145ef93a25d6fb2758b5630ed272001ce77b33a27104819515ae`；去除缓存后的51个源文件 fingerprint 与组装回执一致。该字段不参与通过条件，模型没有重跑。后续 harness 已改为记录 `companion_source_fingerprint` 并排除 `__pycache__`/`.pyc`。

## 能力边界

- 短稿自然度已由独立真实写稿验证并进入当前下一版候选；明确字数下限不足仍交给 under-length 能力处理。
- 常用语机械化 R1—R6 继续 HOLD，不修改 canonical 总表，不以固定开头、固定尾语或逐项结构补齐换取表面整齐。
- 本次只验证 Claude Code 的已支持真实生命周期；Codex、CodeBuddy 的宿主在线生命周期状态不由此推断。
