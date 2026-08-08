# 外部确定性冻结与检查结果

固定基线：`origin/main=cff8a45408b16b11f3e44aed46d7325d5ab78225`。本分支只新增外部证据工具和测试，不修改产品 Prompt、SKILL、reference、路由、provider 或发布包。

## 可交付能力

- `capture`：拒绝空正文，以同目录临时文件、flush、fsync 和无覆盖硬链接原子发布 schema v2 receipt；已存在目标不覆盖。
- `verify`：核对 schema、非空 task id、`capture_ordinal=1`、可选 request SHA-256 和正文 SHA-256。
- `count`：先验证 receipt，再按 Unicode code point 统计非空白字符；篡改正文后不重新出具 PASS 计数。
- `amount-check`：只处理 fact packet 中显式登记的 CNY 金额和 scalar，拒绝重复 id、非有限 Decimal、异构单位错误运算和未在材料中出现的 source quote。

schema v2 只证明指定路径第一次成功冻结的正文，即 `capture_ordinal=1`；它不声称自己能证明“模型第一次 generation attempt”或“第一个 assistant 消息”。首个最终消息的 provenance 仍由 Codex task id 和消息历史提供。

## 独立冷审与修复

首版冷审发现六项 P1：非原子可见文件、把路径首次写入误称 generation attempt、计数前不验哈希、金额与 scalar 不分、JSON object 重复 key 覆盖、空正文可冻结。另发现非有限 Decimal、标识符校验和错误协议等 P2。

上述 P1 已全部修复；相关 P2 中的非有限数、task/request 标识校验和捕获错误也已纳入 schema v2。早期 schema v1 receipt 仅保留为探索性历史证据，不能升级解释为 schema v2 的完整 provenance。

## 实际验证

| 检查 | 结果 |
| --- | --- |
| `python -m unittest tests.test_deterministic_capture` | 11/11，通过 |
| `python -m unittest discover -s tests` | 453/453，通过 |
| `OFFICIAL_WRITING_EVAL_STUB=1 npm run eval:official-writing:smoke` | 20/20，通过 |
| 固定基线确定性消融 | baseline 111/111；candidate 111/111 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `git diff --check origin/main..HEAD` | 通过 |

Promptfoo 使用本地 stub，只证明评测入口和结构未回退。金额检查只验证调用方显式登记的关系，不从自然语言自由抽取金额，也不替代财务判断。

## 剩余边界

- Windows 同卷硬链接提供无覆盖发布；跨文件系统路径不在本工具接口内。
- 工具不能阻止调用方把第二稿伪装成输入，必须结合 task 历史审计。
- 旧 schema v1 receipt 不补写或覆盖；新实验统一使用 schema v2。
