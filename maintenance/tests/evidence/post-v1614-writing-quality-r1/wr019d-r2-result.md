# WR-019d-R2 翻译腔原子结果

## 结论

`PASS_CANDIDATE_ELIGIBLE`。产品候选只增加“翻译式框架成簇”的软审及一条主体边界：优先把连续介词框架和名词化动作改成直接动词；只有材料已经明确或上下文能够无歧义继承主体时才显化主体，主体不明时不得新增责任主体、实施主体或归属关系。canonical 与四套普通镜像同步；不改 lint、Hook、description 或其他反 AI 词表。

## 从失败到最小修正

R1 使用 Luna 同模型独立基线/候选五题。019a“口径”、019b行业词、019c必要英文的当前基线已经通过，候选只有等价变化或局部措辞差异，不据此改产品。019d 候选把只在“正在复核数据”处明确出现的“窗口服务中心”扩成了前期分析、调整和试行主体，匿名 SOL 判为候选硬失败。R1 候选不接入。

R2 只修正这一项：主体不明时保留无主表达或只调动词；不再同时处理口径、行业词或英文。固定同一主体不明反例，新增明确主体正向题和合法对比/并列控制。

## 两模型真实写稿

| 模型/臂 | X1 主体不明 | X2 明确主体 | X3 合法句式 | 硬回退 |
| --- | --- | --- | --- | --- |
| Luna baseline | 保留无主表达，但仍有“围绕…以…为目标”叠加 | 重复“市数据中心”，仍有“以…为目标，围绕…” | 保留法律属性和并列要求 | 无 |
| Luna candidate | 保留无主表达，改成直接动词 | 主体前置，去掉成簇介词框架 | 与 baseline 逐字同义 | 无 |
| Terra baseline | 保留事实，但出现“设置…后，已试行”新连接 | 主体重复，句式较长 | 改成“应当…同时坚持” | 无 |
| Terra candidate | 保留无主表达，日期、312、83=51+20+12和复核状态完整 | 主体、126、两轮、19/11与上线未决完整，句式更直接 | 保留“既要…也要…” | 无 |

Luna 匿名包中，候选在 X1、X2 分别以 A、B 位置出现；SOL 在不知道映射时均选择候选，X3 判 TIE。Terra 匿名审阅第一次因未读取题面而无效；补读题面后仍把原题逐字给出的“并据此调整材料清单”误判为候选新增因果，与冻结输入直接矛盾，因此该项 verifier 结论作废，不用错误裁判覆盖原稿。主线程逐字核对三题，未发现候选新增主体、责任、数量、因果、状态或结论强度。

Ollama Desktop 路线两次均在写稿前返回 `unreadable_encrypted_agent_task`，属于第三方 provider 无法读取加密 V2 worker task 的转发层技术失败；没有形成稿件，不计模型质量，也不冒充多 provider 覆盖。

## 产品改动

- `references/anti-ai-patterns.md` 的句群节奏部分增加一个风险项和一个修订边界。
- 不新增英文/行业黑话禁词表，不把 `基于、面向、围绕、通过、对于` 单次出现判错。
- 不改 `scripts/prose_lint.py`；现有 strict 误报另按独立原子验证。

## 验证

- `python -m unittest maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_v148_anti_ai_borrowing_stays_soft_and_official maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_packaged_resource_mirrors_match_canonical_bytes`：2项通过。
- `python -m unittest maintenance.tests.test_repository_reachability`：7项通过。
- canonical 与四套普通镜像 `anti-ai-patterns.md` SHA-256 一致。
- `git diff --check`：通过。

## 剩余风险

本结果证明两个固定改稿题中的句法减载和主体保护，不证明所有翻译腔都可自动识别。主体继承仍由模型语义判断；不得把本项工程化为介词禁词表或自动替换器。英文术语、讲话任务卡、长报告用途和 description 减载分别保留独立结果，不由本项代替。
