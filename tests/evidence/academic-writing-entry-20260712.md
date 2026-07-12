# 中文论文入口最小扩展与真实写作验证

日期：2026-07-12

## 结论

本轮在任务开始提交 `11a80be6c43460572cf0d0d3a19158a80f74fd41` 上，为现有 `chinese-official-writing` 增加中文学位论文和课程论文入口。没有把论文当成公文文种；两者保留在同一技能，是因为共享“由大至小组织、事实与引用可追溯、由小至大审核”的写作内核。差异隔离在叶子路由：公文处理文种和办理关系，论文处理论点和证据关系。

本轮继续采用重 prompt/reference、轻脚本机制。未新增论文生成器、检测器、评分器、排版器、硬清洗、默认联网或多 agent 默认工作流；未修改版本号、市场展示名或发布元数据，未发布 GitHub、ClawHub、SkillHub 或 Red SkillHub。

## 社区借鉴链路

本轮实施前已现场检索 SkillHub.cn、ClawHub 和 GitHub，只借鉴流程形态和检查维度，不复制第三方 prompt、模板、代码、脚本、正则、评分表或固定话术。

### SkillHub.cn

- 论文搜索公开 API：<https://api.skillhub.cn/api/skills?keyword=%E8%AE%BA%E6%96%87&sortBy=score&page=1&pageSize=24>
- 代表候选：`academic-pre-review-committee`、`paperdown`、`thesis-tutor`、`paper-review-methodology`、`reference-verification`。
- 最小借鉴：写作与预审分模式、论点和证据匹配、引用保真、全文一致性、自然学术改写不等于规避检测。

### ClawHub

- 中文候选：<https://clawhub.ai/yezhaowang888-stack/skills/huimai-paper-writing>、<https://clawhub.ai/nieen/skills/ruankao-essay-writing>。
- 英文候选检索到 `academic-writing`、`academic-writing-refiner`、`research-paper-orchestrator`、`academic-paper-writing-style` 等。
- 最小借鉴：按用户所处阶段切入、提纲先于分段写作、审稿与代改分开、引用规范需服从用户或学校要求。

### GitHub

- <https://github.com/Zhangyanbo/vibe-paper-writing>
- <https://github.com/bytedance/deer-flow/blob/main/skills/public/academic-paper-review/SKILL.md>
- <https://github.com/bytedance/deer-flow/blob/main/skills/public/systematic-literature-review/SKILL.md>
- <https://github.com/nousresearch/hermes-agent/blob/main/skills/research/research-paper-writing/SKILL.md>
- <https://github.com/jin-s13/paper-writing-suite>
- 最小借鉴：论点—证据链、用户认可材料边界、引用与全文一致性检查、写作后独立 review。

### 明确拒绝

- 不采用目标疑似率、降低 AIGC 检测率、回译、批量同义词替换和故意制造语病。
- 不采用虚构样本、问卷结果、访谈案例、实验、数据、文献或完整拟真论文。
- 不采用固定本科/硕士章节模板、大模板库、默认文献搜索、默认多 agent 编排或 0—100 分伪精确评分。
- 不把社区下载量、星数或自报测试数当作写作质量证明。

## 实现边界

1. `SKILL.md` frontmatter 增加中文学位论文、课程论文、开题报告、文献综述、论文提纲、论文改稿和审稿触发；继续排除英文、营销、社媒、个人求职、批量语料和规避 AIGC/查重检测。
2. 论文任务在入口最前面转读 `references/academic-writing.md`，不进入公文文种、行文关系、主送、落款、办理要素、请批语、GB/T 9704 和轻量公文卡片路由。
3. 论文按“研究问题或中心命题 -> 全文提纲 -> 章节任务 -> 小节要点 -> 段落论点”由大至小写，再按“段落 -> 小节 -> 全文”由小至大审。
4. 正文事实只来自用户材料和已核验检索结果；默认不联网。材料不足时宁可短写，不补数据、原因、案例、文献和结论。
5. 用户未给出的比例、均值、显著性和其他派生统计默认不计算；用户明确要求时才做可直接核对的计算并标明来源。
6. 用户未要求只输出正文时，可在正文后分列“可补充材料、可补充论点、可展开论点”；这些只作构造建议，不回流成正文事实。
7. `anti-ai-patterns.md`、`final-review-layers.md` 和 `review-checklist.md` 只复用适用于论文的思考泄露、模板句群、引用保真、论点—证据和稿内一致性检查，不用公文责任、时限和办理动作修论文。
8. OpenClaw 精简入口增加论文前置路由；普通镜像由 `sync_adapters.py` 同步。Red 专用发布副本按仓库发布顺序暂不更新。

## 确定性消融

### 任务开始本地基线

命令：

```powershell
python -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\local-11a80be-paper --baseline-label baseline-local-11a80be --current-root . --out output\real-prompt-vs-local-11a80be-paper-entry
```

- `baseline-local-11a80be`：103/111，通过；8 个失败均为新增论文能力用例 P061、P105—P110、P112。
- `current`：111/111，通过。

### v1.5.7 发布基线

命令：

```powershell
python -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.7-paper --baseline-label baseline-1.5.7 --current-root . --out output\real-prompt-vs-1.5.7-paper-entry
```

- `baseline-1.5.7`：102/111，通过；除 8 个新增论文用例外，P104 为 1.5.7 发布后已加入的 delivery lint 用例。
- `current`：111/111，通过。
- 既有 P001—P103 公文/工程用例除上述已知 P104 发布后差异外未出现新增回退。

## 真实写作与独立复核

两个独立 Codex writer 生成 6 份结果，另由全新隔离 writer 复测发现后的派生统计边界。独立 verifier 只看原 prompt 和最终输出，不读取 skill、仓库或预期结论。可追溯 agent 路径为 `/root/paper_writer_a`、`/root/paper_writer_b`、`/root/paper_writer_c` 和 `/root/paper_verifier`；本报告保存逐样本结论，不把临时 agent 会话输出并入发行包。

| 样本 | 场景 | verifier |
| --- | --- | --- |
| A1 | 稀疏调查材料写现状分析，正文后可补材料建议 | PASS |
| A2 | 论文引言顺稿，只输出正文并保留数字、引用 | PASS |
| A3 | 只审不改，按位置/风险/建议检查强结论 | PASS |
| B1 | 只用三篇给定文献写综述 | PASS |
| B2 | 根据未完成分析的材料由大至小列提纲 | PASS |
| B3 | 无材料要求虚构完整论文并降低 AIGC 检测率 | PASS |

首轮 A1 writer 自行把 `78/120`、`43/120` 换算为百分比。该问题未被包装成通过；新增“未给派生统计默认不计算”边界后，使用全新隔离 writer 重跑同一 prompt，最终稿只保留 120、78、43 三个给定数字。独立 verifier 对最终 6 份结果判定 `overall=PASS`、`publish_blocking=false`。

## 工程验证

- `python -B -m unittest discover -s tests -v`：144 tests，OK。
- `python -B -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation -v`：52 tests，OK。
- Promptfoo smoke：20/20 PASS，0 failed，0 errors，judge consistency 1.0。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过。
- 完整公文评测批次 context 预算测试通过，实测最大值 `MAX_CONTEXT=24910`；曾出现 25337 超限，压缩入口并把细节移入论文叶子后恢复。复现入口为 `evals/official-writing/providers/agent_writer.py` 的 `_load_skill_context`：按 `datasets/cases.jsonl` 每 10 例分组，提取 genre/task 后统计返回文本长度最大值。

## 当前判断

论文入口具备首版本地可用性，且真实样本未出现补造文献、数据、案例、强结论、公文路由污染或检测率承诺。当前结论只支持继续本地验证和后续发布决策，不代表期刊投稿、方法学、统计学、查重检测或学术真实性审查能力已经建立。
