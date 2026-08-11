# chinese-official-writing 1.5.13 冷审核记录

日期：2026-07-15

## 审核范围与证据口径

- 审核对象：GitHub `gongyu0918-debug/chinese-official-writing-skill`、ClawHub `gongyu0918-debug/skills/chinese-official-writing`、本地 `v1.5.13` 发行面。
- 外部报告 `C:/Users/admin/Desktop/chinese-official-writing-1.5.13-冷审核报告.md` 只作线索清单；每项必须由源码、diff、真实写稿、独立 verifier、测试或 live 状态复现后才采纳。
- 会话 `019f565b-ac83-79d2-8958-ccd3f91ea9fa` 只用于确认修改边界：维护和研究门禁留在 maintainer 层，运行时只保留直接写作边界；未复用该会话的修改路径和结论。
- 本轮没有修改 `chinese-official-writing/`、OpenClaw、`.agents`、`.qwen` 等运行时发行文件，只修复评测 provider 和回归测试。产品核心 reference 加载条件待用户对具体方案明确同意后再改。

## 冷基线

### GitHub

- `v1.5.13^{commit}`：`cd2d46c58a5f56b9009c5da08626a88640f2e5b3`。
- 远端 `origin/main`：`07866cc5f8e2972eef9cc6a55381e30c980b1576`。
- 远端 tag 对象：`2adc07fd59e86262023f0cb15617470da7052331`；解引用后为上述发布提交。
- 当前分支相对 `v1.5.13` 没有运行时发行文件差异。

### ClawHub

- `displayName=中文公文写作`，`latestVersion.version=1.5.13`。
- `latest`、`chinese`、`official-document`、`writing`、`gongwen`、`ai-compute` 均指向 `1.5.13`。
- moderation 为 `clean`；`clawhub skill verify ... --version 1.5.13` 返回 `ok=true`、`decision=pass`。
- ClawHub 19 个 artifact 文件与本地 `openclaw/skills/chinese_official_writing/` 逐文件 SHA-256 一致，`mismatchCount=0`；平台另生成 `skill-card.md`。
- 仍需如实保留的限制：provenance unavailable、signature unsigned、dependencyRegistry 无结果；本轮不能据此表述为具备 GitHub 来源证明或签名。

## 真实写稿复现

本轮使用 A/B 与 C/D 两组 writer 标识：A/B 完成 T1-T12，C/D 完成 T13-T33，共 33 个任务、66 份交付输出，其中 T6 两份为只审不改的审稿结果。各组任务协议均要求固定使用 detached `v1.5.13`，不读历史 evidence、外部报告、当前实现或另一名 writer 输出；A/B 的控制任务保存在原始文件开头，C/D 的控制条件和完成回报另存 `genre-writer-control.md`。这些记录是任务协议与 writer 自报，不是系统访问日志。

- T1-T12 覆盖未决纪要与完整纪要、普通非 AI 服务器租赁、AI 算力租赁、非 AI 车辆租赁可研、只审不改、只输出正文，以及申请、请示、函、通知、公告、公示的文种自判或正式格式；
- T13-T26 补通告、意见、决议、议案、公报、命令、方案、征求意见函、工作要点、总结、调研、讲话、采购公告、审查材料；
- T27-T30 补决定、复函、批复、致辞；
- T31-T33 补报告、说明、通报。

按文种去重后，本轮已新跑当前清单中的 29 个公文与正式材料入口；此外保留审稿模式、正文模式、AI/非 AI 专项和纪要轻重路由。四个 verifier 结果包均由与 writer 分离的 verifier 按原 prompt 与两组输出判定，先锁定内容判分，再查看 `ROUTE`：

- T1-T12：24 PASS、0 WARN、0 FAIL；
- T13-T26：28 PASS、0 WARN、0 FAIL；
- T27-T30：8 PASS、0 WARN、0 FAIL；
- T31-T33：6 PASS、0 WARN、0 FAIL；
- 合计：66 PASS、0 WARN、0 FAIL，未发现跨 writer 或跨文种累计达到 3 次的同类交付问题。

全部交付输出均保持题面事实、数字、期限、责任、文种关系和输出模式；没有事实编造、AI/非 AI 误路由、Markdown 残留、过程说明或错误联网。只审不改、只输出正文、必要缺项正文外提示、决定/命令、函/复函、请示/批复、报告/说明/通报等易混边界均通过。普通办公家具采购和政务云扩容审查没有误读 AI 算力叶，只有明确 GPU 推理服务的 T4 进入 AI 专项。

路由共性问题则进一步扩大：66 条 writer 自报中，`task-route-cards` 命中 65 条，`genre-playbooks` 命中 60 条，`genre-checklist` 命中 64 条。对 T13-T33 这 21 个显式文种任务，两名 writer 的 42 条自报全部命中任务卡和文种 checklist，38 条同时命中 playbook。未决纪要 T1 也稳定自报“轻卡命中后继续选择 playbook”。这说明渐进路由选择普遍没有收敛到最窄叶子，但 66/66 内容通过，尚未观察到写稿质量回退。

66 条 `ROUTE` 均为 writer 自报，不是系统级文件访问审计；它们可以证明稳定的 agent 选择模式，不能证明每个文件实际被使用到什么程度。所有自报均为未联网；仅两名 writer 的 T4 自报 AI 算力叶。

原始证据：

- `tests/evidence/cold-audit-1.5.13-20260715/baseline-writer-a.md`
- `tests/evidence/cold-audit-1.5.13-20260715/baseline-writer-b.md`
- `tests/evidence/cold-audit-1.5.13-20260715/baseline-verifier.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-matrix-writer-c.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-matrix-writer-d.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-matrix-verifier.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-gap-writer-c.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-gap-writer-d.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-gap-verifier.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-final-writer-c.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-final-writer-d.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-final-verifier.md`
- `tests/evidence/cold-audit-1.5.13-20260715/genre-writer-control.md`

## 采纳的工程问题

### 1. Promptfoo provider 不能证明渐进式路由

旧 provider 对普通文种批量预载 `task-route-cards + genre-playbooks + argument-chains + official-style`，同一批次内不同任务还会共享聚合后的 reference。它只能证明“给模型一包上下文后能产出”，不能证明每个案例实际走了哪条渐进路线。

修复后：

- 每个案例先独立计算 `selected_references`；
- 只把 route signature 完全相同的案例放入同一批；
- skill prompt 只接受单一 signature，混合 route 直接报错；
- prompt 使用该 signature 的精确文件列表，不再根据聚合 genres/tasks 重新计算；
- `call_api` 返回实际选择的 `selected_references` 元数据。

### 2. mixed-route 缓存漏 hash

旧缓存键按所有案例聚合路由。一个批次同时包含“只审通知”和“起草通知”时，`review-checklist.md` 不会进入 hash；该文件变化后可能复用旧审稿输出。

修复后缓存键写入 `case_id -> route` 映射，并对所有逐案例 reference 的并集计算 SHA-256；baseline 不计算 Skill reference。

### 3. review-only、review+rewrite 和实际 prompt 冲突

旧 provider 即使选中 `review-checklist.md`，实际 prompt 仍强制“输出 160-260 字初稿、组织论证链条”；“检查后再改写”也可能误判成只审。

修复后：

- 只审任务使用审稿交付指令，不再强制初稿或论证阶段；
- 对明确的重写、改写、修改全文、改一版、代改和输出改后稿动作转回写稿路线；
- 先剥离“不重写、不改写、不修改、只给修改建议”等负向语境，避免破坏真正只审任务。

独立 diff reviewer 追加的 9 个正负同义样本全部通过。

### 4. AI 算力触发误报和漏报

旧 provider 使用裸 `服务器、云端、技术服务、SLA、并发` 容易把普通租赁或普通云服务送入 AI 叶子；初版收紧后又出现否定分句吞掉后续“但/而是/却/仍需 GPU”的漏判。

修复后：

- 使用明确的算力、GPU、模型服务、智算、Token、模型推理/训练标记和三个 canonical 专项文种；
- 保留“云端 + 本地 + 部署比较”组合，不再用泛化的“云端 + SLA + 并发”；
- 否定作用域在“但、而是、却、仍需、同时、另需”等转折处结束；
- 普通备份服务器且明确非 AI、普通政务网站且明确非 AI 均不加载 AI 叶子。

### 5. 其他 provider 缺口

- 补齐 `style -> official-style.md`，避免“去口语化/润色”任务 `KeyError`；
- complex 路线遇到显式“论证、可行性、必要性、方案比较、成本比较”时保留 `argument-chains.md`；
- full dataset 安全预算测试改为使用真实 route batches，而不是旧的连续十条聚合方式。

## 暂不采纳或拒绝的报告项

- **OpenClaw 正文镜像和 MIT/MIT-0 是同步错误**：拒绝。镜像正文和许可分层是 `sync_adapters.py` 与边界测试锁定的发行契约，未复现加载断裂或文件漂移。
- **800 字升级阈值与 260/300/500 字输出档位冲突**：拒绝。前者是 reference 路由复杂度阈值，后者是用户篇幅要求，不属于同一阈值体系。
- **二次修改规则擅自允许联网**：拒绝。原文只要求判断是否需要，全局仍由默认不联网和时效事实条件约束；报告建议还会误删“最新/现行政策”等必要核验触发。
- **15/15 references 被入口引用说明无渐进披露**：拒绝。可发现性不等于实际加载；reference 应由入口直接链接并写明条件。
- **固定 6KB、40 字、120 字、硬规则 12 条、别名 2 个等门禁**：拒绝。没有真实写稿因果证据，报告内部数值也不一致。
- **广泛文种质量失败**：未复现。新跑的 66 份交付输出全部 PASS；不能把旧覆盖缺口直接表述为质量失败。
- **否定句、长复合句或重复规则已经导致真实写稿回退**：证据不足。文本重复和长行可静态复现，但本轮没有出现三次以上相同交付失败，不据此删写作边界。
- **删改 AI 味、限字、description 或拆新 reference**：暂不采纳。均需针对真实输出的 A/B 或触发消融，不能从外部报告直接实施。

## 会议纪要路由冲突

`SKILL.md` 要求轻量卡能够覆盖时终止长 reference 路由；`task-route-cards.md` 又把全部“会议纪要”列入必须转读长 reference，同时同一文件提供“未决事项会议纪要”专用轻卡。两名 writer 都稳定复现 T1 先命中轻卡再继续升级。

本轮 provider 没有提前替产品裁决：未决纪要在评测元数据中继续保留 `task-route-cards.md + genre-playbooks.md` 两段，以如实反映 1.5.13 冲突；“简短但完整、已形成决定/责任/期限”的纪要仍必须包含 playbook。

### 待用户明确同意的最小产品方案

现有流程：材料稀疏先读轻卡；会议纪要又被无条件要求转长 playbook；writer 的路由自报普遍同时命中任务卡和文种栈。

拟改流程：

1. 明确路由仲裁优先级：只审/排版等模式先分流；轻卡覆盖时终止；已知文种按必要叶子进入；复杂、专项、格式条件再升级。
2. 未决纪要只保留轻卡；已经形成议定事项、责任单位、完成期限，或用户要求完整正式纪要时，升级会议纪要 playbook。
3. 不因文种名称已知而默认并读任务卡；任务卡只用于材料稀疏、短通知、明确不新增事实和局部修改。
4. 不改变事实边界、输出模式、三级复核顺序、修改次数、默认联网和发布链。

改变原因：这是唯一由 A/B、C/D 两组 writer 在 29 类文种中稳定复现的问题。66 条路由自报中 65 条命中任务卡；21 个显式文种任务的 42 条自报全部命中任务卡和文种 checklist。当前 66/66 交付质量无回退，适合只改仲裁、不改写作内容。

主要风险：过度减载可能漏掉文种骨架、办理要素或复核要求。获批后应先用 2-4 个直接相关短稿做 `v1.5.13` A/B，再由独立 verifier 判断；出现任何事实、文种、格式或输出模式回退时撤回该方案，换用更窄的条件表达。

## 验证结果

- `python -B -m unittest discover -s tests -v`：172/172 PASS。
- `python -B -m unittest tests.test_promptfoo_eval`：43/43 PASS。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.13-cold-audit --baseline-label baseline-1.5.13 --current-root . --out output/cold-audit-vs-1.5.13-final`：`baseline-1.5.13 108/108`，`current 108/108`。该工具不调用 LLM，只作确定性支撑。
- `npm run eval:official-writing:smoke`：沙箱内因 Node 无法启动工作区外 Python 而出现环境失败；按错误提示在沙箱外用 Python 3.13 复跑，20/20 PASS。该 smoke 使用默认 deterministic stub，不作为真实模型写稿证据。
- A/B、C/D 两组 writer 标识 + 四个 verifier 结果包：66/66 PASS，覆盖当前 29 个文种入口和专项模式；没有累计达到 3 次的同类成稿问题。隔离来源以任务协议和 writer 自报记录，不表述为系统访问审计。
- 66 条路由自报：任务卡 65、playbook 60、文种 checklist 64；所有任务未联网，AI 算力叶只命中两名 writer 的 T4。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：无错误；仅工作区 LF/CRLF 转换提示。
- ClawHub live：1.5.13、moderation clean、verify pass、19/19 artifact SHA-256 一致。

## 结论

本轮接受并修复的是“真实 agent 评测无法观测渐进路由”这一工程共性问题；不把 stub、确定性消融或 route 元数据包装成真实写作质量。产品层唯一达到修改阈值的是任务卡与文种 reference 常见并行自报，尤其未决纪要轻卡命中后仍选择 playbook 的冲突；全 29 文种真实写稿没有出现质量共性回退。因产品问题属于核心 reference 加载条件，已给出具体的现有流程、拟改流程、原因和回退风险，等待用户明确同意后再实施。
