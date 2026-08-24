你是 Grok 4.6 独立冷审员。只读审查，不修改、不提交、不联网、不运行测试或写稿。你最多执行12次只读命令；不要读取仓库内任何历史模型 verdict、冷审结果或无关长文件。命令受策略拒绝时换一个更窄命令一次，不循环重试。完成必要检查后立即给终判。

固定对象：

- 公开基线 `main@8aab5e61e65c0411b4bd6580173c2a107986fdcb`
- 状态回填 `b9950f8a22ac2d02248df01ce6d311e00c9d7c87`
- 最近产品差异 `v1.6.14..v1.6.15`

必须读取：根 `AGENTS.md`、`maintenance/tests/evidence/post-v1615-status-cold-review-r1/preregister.md`、`maintenance/tests/evidence/post-v1615-status-main-backfill-r1/result.md`，以及 `git diff main...b9950f8a -- maintenance/specs maintenance/docs/待办.md maintenance/docs/evidence/README.md maintenance/tests/test_status_ledger_consistency.py`。只在发现具体矛盾时读取对应直接 evidence。

必须核对：

1. `git diff --name-status main...b9950f8a` 是否夹带 canonical 产品、Hook、adapter、普通镜像或付费源码；
2. v1.6.15 tag/发布、HK/MT/WR 终态是否与最近产品差异一致；
3. `OC-003` 是否允许建议态但禁止已启动/完成/决定、既定程序、主体、期限和预算结论，且候选规则没有进入产品树；
4. `WR-020b1/b2` 和旧 HOLD 终态是否自洽；
5. 公开 main 是否没有 `outline_assist`、`paid/redhead_docx` 或付费路由，付费候选只被记录而未夹带；
6. 新增链接或 ledger 断言是否有一眼可复现的虚假或失效。

不要建议泛化扩测。不要因合法条件性建议要求完全禁止研究判断。严格输出：

`VERDICT: PASS|NEEDS_FIX`

`P0`

`P1`

`P2`

`NON_BLOCKING`

`SOURCE_BOUNDARY: CLEAN|CONTAMINATED`
