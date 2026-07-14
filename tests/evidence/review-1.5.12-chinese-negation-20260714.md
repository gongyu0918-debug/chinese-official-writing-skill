# 1.5.12 中文指令与冗余否定 Review 复核

日期：2026-07-14

外部报告：`C:\Users\admin\Desktop\中文公文写作-1.5.12-中文指令与冗余否定Review.md`

当前基线：`6e784257ef3dde1345ed0eda363244bd77d87cd2`

发行基线：`v1.5.12=f87b6be990e1314442b5532ae7441f21c8d4d34f`

## 结论

外部报告的否定词频盘点基本准确，但没有证明否定词频已经造成真实写作失败。报告把论文宣传位置写成“GitHub README / 仓库简介”，本地 README 没有该表述，GitHub live About 的仓库简介仍逐字写有“兼顾中文本科、硕士学位论文和课程论文”，该产品边界冲突已复现并接受。两名独立 writer 使用当前基线完成 4 个未见任务，共 8 份输出；两名独立 verifier 均判 8/8 PASS，未发现因多重否定、否定状态或未决口径发生语义判反，也没有问题达到“至少 3 份输出、2 个不同 prompt、2 名 writer”的共性门槛。

本轮不修改 `SKILL.md` 或任何运行时 reference，不改任务路由、加载条件、三级复核、输出模式、修改次数、回滚、默认联网和发布链。接受项只收窄 GitHub live About 描述并保存复核证据，不升版本、不发布。

## 基线核对

- 当前 HEAD 为 `6e784257ef3dde1345ed0eda363244bd77d87cd2`；`origin/main` 同步到同一提交。
- `v1.5.12` 指向 `f87b6be990e1314442b5532ae7441f21c8d4d34f`。
- 当前 canonical `SKILL.md` 相对 tag 只修改 GitHub 仓库许可证字段；报告涉及的 Prompt 正文未变。
- 当前 README 相对 tag 只调整许可证展示。两版 README 均未出现“本科论文”“硕士论文”“课程论文”“兼顾论文”或同义宣传。
- 修复前 `gh repo view gongyu0918-debug/chinese-official-writing-skill --json description` 返回：`中文公文与正式工作材料写作为主，兼顾中文本科、硕士学位论文和课程论文的起草、改写与复核。` 冲突位于 GitHub live About，不在版本库 README。
- 已执行 `gh repo edit gongyu0918-debug/chinese-official-writing-skill --description ...`，修复后 live description 为：`中文公文与正式工作材料的起草、改写、压缩与复核，覆盖通知、请示、报告、函、方案、会议纪要、可研及 AI 算力等正式文本。` 复核结果不再包含论文入口。
- `workflow.md`、`review-checklist.md`、`genre-playbooks.md`、`anti-ai-patterns.md`、`official-style.md` 与 tag 的对应文件一致。

## Finding 逐项处理

| 外部报告 finding | 复核 | 决定 | 理由 |
| --- | --- | --- | --- |
| canonical 否定词密度较高 | 报告所列 9 个文件的禁止类措辞计数可复现：49、28、8、10、13、16、21、3、1 | 接受文本盘点；拒绝“主病灶”定性 | 词频是静态可读性线索，不能替代真实输出、A/B 或 verifier 证据 |
| `不要漏列，也不要扩展成调查问卷` 是双重否定 | 原文存在 | 拒绝定性和改写 | “漏”不是语法否定；两部分分别保护点名缺项的完整性和提示范围，不是同义重复 |
| `SKILL.md` 第 77 行四个否定过密 | 高密度可复现 | 接受可读性观察；拒绝本轮改写 | 四个分句分别约束泛占位、正文缺项说明、问卷化和转嫁写稿责任；删成一句会减少边界 |
| 事实映射式二次修改四连“不” | 原文可复现 | 拒绝报告示意改写 | 非默认阶段、不中断交付、不循环追问、不输出内部映射表是四个不同边界；“仅处理本轮并直接交付”不能完整替代 |
| 会议纪要 playbook 风险条否定过密 | 原文可复现 | 接受可读性观察；拒绝“每条最多 1—2 个否定” | 次数上限没有工程或写作依据；各项对应不同历史风险 |
| ANTI-AI 改写边界四连“不得” | 原文可复现 | 拒绝缩句 | 现有规则保护事实、引用、术语、否定对象和论断强度；缩句会丢失否定对象迁移和情态升级边界 |
| 正向规则后应统一删除反面镜像 | 个别形式存在，但多数不等价 | 拒绝作为通用原则 | “普通文本”不能完全推出“无 Markdown”，“缺项列正文外”也不能完全推出“正文不填泛称”；叶子 reference 不是所有任务固定加载 |
| `review-checklist.md` 有约 15 处“是否未” | 精确复现 15 处 | 接受为后续可读性候选；拒绝本轮产品修改 | 真实基线测试未复现判反，未达到共性门槛；无目标问题改善证据时不改运行时 Prompt |
| 入口与 workflow 存在六类同构边界 | 重复可复现 | 接受静态重复；拒绝当前删减方案 | 入口压缩、短原则转 reference 和 workflow 拆段已有真实 A/B 回退，曾出现弱模型事实外扩、Markdown 残留和建议口径执行化 |
| description 排除论文，但 GitHub 对外宣传兼顾论文 | README 中不可复现；GitHub live About 可逐字复现 | 接受并修复 GitHub About | 公文与论文已拆分，公开仓库简介仍宣传论文会造成产品边界漂移；运行时 description 保持不动 |
| P0—P3 修改优先级 | P0 指向的冲突成立，但载体应精确为 GitHub live About；P1—P3 混合静态可读性和未证实行为风险 | 只接受 P0 元数据修复，拒绝其余产品 Prompt 修改 | 只能先验证行为问题，不能把否定计数直接转成产品修复清单 |

## 静态复现

按外部报告口径统计 `不要|不得|不能|不应|禁止|避免|切勿|严禁`：

| 文件 | 命中数 | `是否未` 命中数 |
| --- | ---: | ---: |
| `SKILL.md` | 49 | 0 |
| `references/workflow.md` | 28 | 0 |
| `references/review-checklist.md` | 8 | 15 |
| `references/genre-playbooks.md` | 10 | 0 |
| `references/anti-ai-patterns.md` | 13 | 0 |
| `references/format-gbt9704.md` | 16 | 0 |
| `references/genre-checklist.md` | 21 | 0 |
| `references/task-route-cards.md` | 3 | 0 |
| `references/proofreading-checklist.md` | 1 | 0 |

上述结果只证明文本形态存在，不证明模型功能退化。

## 真实写作复现

两名 writer 均只读当前 `6e78425` 基线，按 Skill 渐进读取规则独立完成以下任务：

1. 只审不改：审查无依据的“全面排查、未发现任何问题、整改全部完成、建立长效机制”，只输出位置、风险层级、修改建议，不重写、不打分、不加 Markdown 粗体。
2. 缺项请示：只给培训月份、人数、预算和经费来源；用户明确未提供主送、天数、课程、依据、单位全称、日期，并要求只输出正文、不附待确认、不占位、不编造。
3. 未决会议纪要：保留“先试用、观察、再评估”口径；明确未形成采购决定，未给责任、期限、预算、考核，并禁止补写。
4. 事实映射式二次修改：从坏稿删除核心系统、严重故障、一级响应、全面整改、责任部门、期限和彻底恢复等未给事实；只输出改后正文，不解释、不追问、不输出映射表。

两名 writer 的结果一致：

- S1 均保持只审不改，识别四类无依据强判断，没有重写、打分或 Markdown 标签。
- S2 均只使用已给事实，没有补造主送、日期、政策、课程、天数或占位符；结尾逐字保留“妥否，请批示。”。
- S3 均保留未决口径，没有补责任人、期限、预算、采购或考核，也没有使用“会议认为/强调/决定”。
- S4 均只保留“7 月 12 日登录页面间歇性异常、技术人员两次重启、目前仍在观察”三项已给事实。

两名 verifier 只看逐字 prompt 和匿名输出，不读取实现或外部报告，独立结论均为：8/8 PASS，0 WARN，0 FAIL；不存在至少 3 份输出、2 个不同 prompt、2 名 writer 共同出现的同一语义问题。精确模型 ID 无法核验，因此本组只记真实写稿 sanity，不包装成统计显著性或跨模型证明。

## 历史回退交叉核对

- `tests/evidence/prompt-density-community-review-20260709.md`：入口瘦身候选在定向测试 41 项中失败 6 项；补回锚点会退回此前真实 A/B 已否决的拆行形态，候选已回滚。
- `tests/evidence/reference-density-ab-rollback-20260709.md`：只拆分 workflow 长段的候选虽通过定向测试，真实 A/B 仍为 weak candidate FAIL、strong candidate WARN，出现 Markdown 残留、事实外扩和建议口径执行化，候选已撤回。
- `tests/evidence/prompt-relief-round2-20260714.md`：1.5.12 减负前测只有 1 次单样本 WARN，没有达到共性门槛；最终 12 项发布级实写为 12/12 PASS。

这些证据说明重复和密度值得持续观察，但不能据此重复尝试已经回退的入口瘦身或 reference 拆段。

## 验证记录

- 定向边界与确定性用例：

  ```powershell
  py -3 -B -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation.RealPromptAblationTests.test_case_set_includes_recent_review_regressions tests.test_real_prompt_ablation.RealPromptAblationTests.test_cases_cover_create_and_revision_prompts tests.test_real_prompt_ablation.RealPromptAblationTests.test_current_skill_passes_real_prompt_cases -v
  ```

  结果：48/48 OK。

- 完整单测：

  ```powershell
  py -3 -B -m unittest discover -s tests -v
  ```

  沙箱内首次运行 152 项中出现 8 个 `PermissionError`，均发生在 Windows 临时目录创建或清理，没有断言失败；按环境故障处理。沙箱外用同一命令复跑，152/152 OK。

- Promptfoo smoke：

  ```powershell
  npm run eval:official-writing:smoke
  ```

  结果：20/20 PASS，0 fail，0 error，skill 10 胜，judge consistency 1.0。

- Skill 快速校验与差异检查：

  ```powershell
  py -3 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
  git diff --check
  ```

  结果：`Skill is valid!`；`git diff --check` 通过。镜像一致性由定向和完整测试中的 `test_adapter_skill_copies_keep_boundaries`、`test_packaged_resource_mirrors_match_canonical_bytes`、`test_primary_adapter_mirrors_match_canonical_bytes` 共同验证。

- 真实写作：2 名 writer × 4 个 prompt = 8 份输出；2 名 verifier 分别判 8/8 PASS。

因本轮没有形成产品 Prompt 候选，不存在“当前基线 A 与候选 B”；没有把当前版本与自身重复运行包装成 A/B 证据。

## 后续门槛

仅在未来未见样本中出现同一否定判反问题，且至少覆盖 3 份输出、2 个不同 prompt、2 次独立 writer，并经独立 verifier 多数确认时，才重新打开 `review-checklist.md` 的正向化候选。届时只改单一文件、单一措辞类别，以当时当前 HEAD 固定为 A 基线；候选若出现事实、文种、格式、输出模式、联网或镜像回退，立即撤回。
