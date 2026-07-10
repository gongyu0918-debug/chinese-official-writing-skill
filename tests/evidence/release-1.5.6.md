# 1.5.6 发布记录

日期：2026-07-10

## 固定状态

- 上一发行版：`v1.5.5` / `dd4c6d66ce31d91e65c6e1d11de3e4e80885b4ba`。
- pre-finalizer 候选：`a444c51b70c168a0f3c8e6e360d403316630e2d3`。
- 发布分支：`codex/release-1.5.6`；发布准备开始时 `origin/main=a777e3a75a964bdc3ee4daccbb1a6e708736623f`，当前分支为其线性后继。
- finalizer 实验全部位于忽略的 `output/`，没有进入 canonical skill、reference、正式测试、适配器或三平台发行包。

## 发布范围

1.5.6 只发布 pre-finalizer 已验证的正向修复和发布基础设施：

- 普通叙述可正式化，只有引号内、明确原文/引语或逐字保留内容按字面锁定。
- 用户要求只输出正文时，除非同时允许某类提示，不附待确认、风险、核验或自证说明；缺项不补造，也不写入正文解释。
- 轻量任务由任务路由卡终止 reference 加载；复杂文种、长文、多材料、专项论证或正式格式请求再升级，playbook 和反 AI 资料保持叶子结构且 reference 图无环。
- `prose_lint` 文档命令补全解释器和稿件路径，脚本仍只提示风险，不自动清洗正文。
- Promptfoo provider 按任务加载完整 reference，不静默截断或跳过缺文件；上下文超预算显式失败，缓存键覆盖命令、批大小、超时、重试和实际 reference，执行超时默认值与缓存一致。
- ClawHub 文档改用 `clawhub skill publish` 和 Windows 安全的等号参数；根目录继续只保留 `AGENTS.md` 一个接手入口。
- 发布前 cold review 发现 OpenClaw 压缩入口未同步“只输出正文优先”；已只修复 `sync_adapters.py` 的 OpenClaw 摘要模板，使缺项提示服从用户交付命令，并补 unit/P103 守卫。canonical prompt 未改。

未新增 finalizer、validator、强制二次 agent、正则删句、固定事实替换、默认联网、外部模型依赖或正文硬清洗。

## Finalizer 拒绝结论

隔离实验测试了三种“确定性检测 + 独立修订 + 不变量比较”实现。主 Luna A/B/C 的 C 组可把显式旁白降为 0，并达到 10/10 确定性场景通过；但两轮 GPT-5.5 复测和独立 cold review 发现修订稿新增培训、身份、采购、审批或因果事实，违反“不新增事实”和不变量 100% 门槛。因此三种实现全部拒绝并回滚，只保留 `a444c51` pre-finalizer 候选。

## 自然语言二次修改测试

使用 5 个独立 `gpt-5.6-luna` writer，在真实 pre-finalizer 上一稿后追加同一类普通用户式提醒：清理材料读取状态、自我解释和写作过程说明，只输出正文，不新增事实，不改变数字、主体、责任、引语、未决状态、标题和章节顺序，并保持原篇幅要求。

writer：

- S1 600—800 字阶段报告：`019f4bb5-313c-7dc0-aedb-5ad34bfa276a`；明确篇幅复测 `019f4bb7-8bc3-7a30-b020-dbc007c5c246`。
- S2 900—1100 字调研报告：`019f4bb5-4597-7b22-b40a-6d9d77752e65`。
- S3 3000—3300 字多附件可研：`019f4bb5-59b4-79f2-980e-ba7b69a01be1`；明确篇幅复测 `019f4bb7-a046-75e0-9740-04717adcda81`。
- S5 300—450 字培训简报：`019f4bb5-6f9b-7d33-a5b0-11d967823777`。
- S7 引语和拟办状态：`019f4bb5-85a1-7250-ba02-5916d5c1bc2e`。

独立 verifier：GPT-5.5 `019f4bb9-da3e-7cd3-a9df-96334e482329`，GPT-5.6 Sol `019f4bb9-ee94-7501-a5c7-f7bbfe6097a7`。

共同结论：自然语言二次提醒能明显减少可见旁白，但不能视为稳定解决。

- S1：两版非空白字符分别为 412、538，均低于 600；明确篇幅版末尾出现异常残片“屾讯”，FAIL。
- S2：904 字，事实、样本边界和数字保持；两名 verifier 分别判 PASS、WARN，分歧来自口径重复和轻微关系外推。
- S3：普通版 2663 字，低于 3000，FAIL；明确篇幅版 3190 字，数字和未决状态保持，但存在程序性泛化和语义空转，WARN。
- S5：300 字达到下限，但把“2 场、37 人、6 个问题”近义重复多轮，属于凑篇幅，FAIL。
- S7：引语逐字保持，`拟先`、`尚未决定` 未升级，无新增事实，PASS。

结论：二次自然语言提醒只作为可选修订方式，不作为默认工作流、发布兜底或“旁白已解决”能力承诺。本轮不再追加 prompt。

## 发布前验证

- `python -B .\tools\sync_adapters.py`：首次在沙箱内因 `.agents` 写权限失败；经批准在沙箱外重跑后全部适配器同步成功。
- `python -B -m unittest tests.test_skill_boundary tests.test_review_regressions tests.test_real_prompt_ablation tests.test_promptfoo_eval -v`：110/110 通过。
- `python -B -m unittest discover -s tests -v`：123/123 通过。
- `python -B .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.5.5 --baseline-label baseline-1.5.5 --current-root . --out .\output\real-prompt-vs-1.5.5-release-1.5.6-final`：baseline 95/102，current 102/102；基线只在 1.5.6 新增守卫失败。
- `python -B .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\pre-finalizer-a444 --baseline-label pre-finalizer-a444 --current-root . --out .\output\real-prompt-vs-a444-release-1.5.6-final`：pre-finalizer 101/102，current 102/102；唯一新增通过项为 OpenClaw 发行入口同步守卫 P103。
- `npm run eval:official-writing:smoke`：沙箱内因 Node 无法访问 Python provider 出现 20 errors；经批准在沙箱外重跑后 20/20 通过，skill 10 胜、judge consistency 1.0。
- `python -B .\tools\run_real_article_eval.py --out .\output\real-article-release-1.5.6`：skill 10 个样本平均差异率 0、关键词命中率 100%；9 个 stub 样本仍有匿名占位标签风险，只作人工复核线索。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过，仅有 Windows 换行提示。

## Cold review

- 独立 reviewer：`019f4bbd-a09f-7cf0-add1-01e405de5c92`。
- 首轮 finding：OpenClaw 发行入口规则 5、13 无条件要求文后提示，与 canonical 的“只输出正文优先”冲突，`publish_blocking=true`。
- 复现：`v1.5.5` 和 pre-finalizer `a444c51` 的 OpenClaw `SKILL.md` 均缺少该例外。
- 最小修复：只改 OpenClaw 摘要生成模板、同步发行文件并补 unit/P103；不改 canonical skill、reference 或默认工作流。
- 修复后 reviewer 复核：`resolved=true`，`publish_blocking=false`。

## 剩余风险

- 600—800 字稀疏材料和 3000 字以上长稿仍可能出现材料读取旁白、自我解释或篇幅不足。
- 自然语言二次净稿可去掉可见旁白，但可能造成压缩过度、异常残片、重复填充、程序性泛化或事实外扩，不能视为稳定自动修复。
- 确定性 lint 和字面不变量不能识别全部语义性新增事实，重要正式稿仍需人工或独立语义复核。
- 真实文章评测使用 stub 写稿，只能证明评测入口和要素覆盖；其中匿名占位标签风险不等同真实模型输出。
- 本地不可读目录 `pytest-cache-files-8y_vrpl7/` 仍会让 `git status` 输出非阻断权限警告。

## 发布状态

发布 commit、tag、GitHub release、ClawHub 和 SkillHub 实况将在发布完成后回写。
