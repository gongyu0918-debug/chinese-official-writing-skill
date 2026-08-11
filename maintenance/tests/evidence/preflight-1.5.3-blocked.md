# 1.5.3 发布前复核记录（阻断）

日期：2026-07-07

结论：不发布 1.5.3。GitHub、ClawHub、SkillHub 均未推送。本地候选仅作为下一轮修复依据。

## 本轮目标

- 核实当前本地基线是否可升级为 1.5.3。
- 将测试口径从“只跑脚本”改为当前能力测试，重点看真实写作中的指令遵循、事实边界、完成度和格式噪点。
- 复核社区最小借鉴链路是否存在；如不存在，列为下一轮计划。

## 最小借鉴链路复核

隔离 explorer 只读仓库证据后确认：仓库已有最小借鉴链路，不是空白状态。可追溯证据包括：

- `AGENTS.md` 中的社区借鉴门禁：只借鉴流程、检查维度和 prompt/markdown 写法，禁止誊抄代码、脚本、正则、模板库、大段 prompt、固定话术和硬门禁。
- `tests/evidence/skillhub-1.4.4-research.md`、`tests/evidence/anti-ai-memory-1.4.8-research.md`、`tests/evidence/architecture-borrowing-plan-1.5.0.md` 记录了社区检索、借鉴边界和拒绝项。
- 当前包内未发现 `format_docx.py`、`document_generator.py`、`install_fonts.py` 等社区重脚本落入 canonical。

仍建议下一轮补一个 `minimal-borrowing-ledger`，把借鉴点、来源类型、采纳/拒绝理由、测试覆盖集中成表，并加轻量测试防止重脚本或社区 slug 进入 canonical。

## 已做的最小修复候选

本轮仅改 prompt/reference 与确定性测试，不新增 lint 硬规则、不新增脚本、不扩大默认联网：

- 版本字段候选同步为 `1.5.3`，并用 `tools/sync_adapters.py` 同步 Codex/Qwen/Hermes/OpenClaw/README/plugin 镜像。
- 在 `SKILL.md`、`references/workflow.md`、`references/genre-playbooks.md` 收紧事实稀疏场景：
  - 用户写明“材料只有”“不新增事实”“不要编造”时，事实少于字数目标宁可短写。
  - 通报、情况说明、报告不为补齐体裁骨架自动补处置、整改、督导、闭环、清单、台账、联系方式等未给事实。
  - 通报材料只给“已完成梳理、发现问题、组织协调会、后续需补充”时，只保守组织已给事实，待补责任人和更新周期放正文外。
- 在 `tools/run_real_prompt_ablation.py` 新增 P091-P093：
  - P091：数据治理通报材料稀疏，禁止补会议纪要、清单、复核节奏、治理闭环等。
  - P092：字段式硬盘采购申请，禁止补采购类别、资产属性、用途、入库流程。
  - P093：成本考察报告，禁止正文 Markdown 加粗、井号标题、横线包装。

## 确定性验证

已运行：

- `C:\Users\2\AppData\Local\Programs\Python\Python312\python.exe -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`
  - 结果：42 tests OK
- `C:\Users\2\AppData\Local\Programs\Python\Python312\python.exe tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-release-1.5.3`
  - 结果：baseline-1.5.2 为 84/93，current 为 93/93

注意：以上只能说明确定性文件项和规则覆盖通过，不能替代真实写稿测试。

## 当前能力真实写作测试

模型：`gpt-5.3-codex-spark`，低思考强度。writer subagent 只加载当前 skill，不修改仓库。

通过或基本通过：

- 结构锁定改稿：在“三、原因分析”后增加独立自然段，没有新增小标题，四个标题数量、名称和顺序保持不变。
- 版慎通成本考察短稿：没有 Markdown 标题残留，整体把“建议尝试、测试、建立路由机制”处理为建议/评估口径，未直接写成已定执行命令。

阻断失败：

- 数据治理专项推进情况通报连续复测失败。即使 prompt 明确要求“材料只有”“事实少时宁可短写”“不要补项目组、任务清单、处置方向、联系方式、台账清单、责任链条、督办闭环、可验收结论、基础底稿、过程可追踪、统一督导流程”等，弱模型仍补写：
  - 基础目录清单、关键口径对照、系统字段、责任边界、更新机制；
  - 工作组、问题清单、统一共识、后续治理抓手；
  - 治理流程、验收节点、更多系统扩展、工作连续衔接；
  - 责任人岗位、联系方式、生效区间等用户未要求的补充项。

隔离 verifier 只看 prompt 和成稿后判定：不可发布。主要原因是多处未给事实被写实化，属于阻断级事实越界。

## 发布决定

不发布 1.5.3，不创建 tag，不推送 GitHub、ClawHub、SkillHub。

下一轮应优先解决“材料稀疏型通报/情况说明/报告在弱模型上仍会自动补处置链条”的问题。建议方向：

- 继续保持软 prompt，不引入硬阻断或脚本清洗。
- 把“短写安全骨架”表达得更接近可直接仿写的形态，但避免模板化和一例一修。
- 增加真实弱模型对比测试：通报、情况说明、报告、会议纪要、成本考察各 1 例，由独立 verifier 复核。
- 在补修前不要对外宣称 1.5.3 已通过当前能力测试。
