# 入口减载、可研只审不改与文后提示边界组合回归结果

日期：2026-08-02

固定基线：`5ed38350c2ac10ac83ea81b5f6d3ec7c04462012`

研究分支：`codex/entry-feasibility-postbody-integration-v1532`

## 组合范围

本轮只组合三项已在独立 worktree 验证的改动：

1. 将入口中的审稿输出细则下沉到既有 `review-checklist.md` 和 `anti-ai-patterns.md`，入口净减 121 个字符；
2. 可研“只审不改”命中专用叶，并把审查边界收束为项目主张本身及相互之间的一致性；
3. `prose_lint.py --mode draft-body` 识别带中文、阿拉伯数字、括号及章节目次前缀的文后提示标题，仍只报告、不自动改稿。

未修改默认起草事实边界、正文与文后提示的触发条件、用户输出模式、篇幅规则、门禁流程、修改次数或回退方式。

## 单变量真实证据复用

组合回归不新增写稿，复用三个独立候选已经完成的首个技术有效输出和独立盲审：

- 入口减载：IR01、IR02 均为 TIE，四稿硬边界 PASS；
- 可研只审不改：S4 为改后胜，S5 与控制题为 TIE；六份输出均保持只审不改；
- 文后提示：OS01—OS04 均符合输出模式；当前主线未复现“文后提示误入正文”，新增脚本测试覆盖四种编号标题及三类正文反例。

精确模型和 thinking 在既有写稿记录中为 `unavailable`，因此上述稿件只作为单变量行为证据，不包装成严格同条件总体质量胜率。

## 组合工程验证

实际运行：

- `python -m unittest discover -s tests`：417/417 通过；
- `npm run eval:official-writing:smoke`：20/20 通过，0 failed，0 errors；
- `python tools/run_real_prompt_ablation.py --baseline-root <固定基线> --baseline-label 1.5.32-main-5ed38350 --current-root . --out output/entry-feasibility-postbody-integration-ablation-20260802`：基线 111/111，组合候选 111/111；
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：PASS；
- `python tools/sync_adapters.py`：canonical 与发行镜像内容一致；
- `git diff --check 5ed38350..HEAD`：PASS。

Promptfoo 提示本机 `0.121.11` 低于可用新版本 `0.121.20`，不影响本次 20 项结果；本轮未升级依赖。

## 结论

PASS。三项改动组合后没有出现事实、文种、输出模式、只审不改、文后提示或镜像一致性回退，可合并到本地 `main`。

## 剩余风险

1. 文后提示是否应出现仍由 Agent 按语义和输出模式判断；`prose_lint.py` 是辅助定位器，不是所有宿主都强制执行的交付门禁。
2. 用户确实要求把“待确认事项”作为正文业务章节时，脚本可能提示人工复核，但不会自动删除或改写。
3. `review-checklist.md` 中仍保留“审一下”作为兼容触发词；它来自评测构造，尚无真实用户语料证明必须常驻，后续应作为独立原子继续验证。
