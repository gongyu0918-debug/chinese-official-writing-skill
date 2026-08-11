# 终稿 delivery-mode 调用链校准结果（2026-08-02）

## 结论

本候选按预注册完成，保留。Promptfoo 公文成稿评分和真实样文成稿评估现在明确使用既有 `draft-body` 模式；合并式评审包、开放形态 AI 味语料和逐用例消融未被盲目切换。没有修改 lint 词表、正则、严重度、自动改稿能力、写作规则或核心工作流。

基线为 `b2be5d8bb9958ab754907a1b6929085302e2056d`，独立分支为 `codex/v1533-delivery-mode-calibration`。本结果不合并 `main`，不发布，不修改版本号或 tag。

## 提交

- `8ead8ee63af194325628c5fb715eb1c18ac745d2`：冻结单变量范围、调用点分类和验收口径。
- `2f82bde5ebf93fdcfc60088ab2ab6b18e0803bf1`：校准两条终稿 API 调用、现行工具命令和发行镜像，增加两条参数回归。
- `2891a5ab8827a859012ef7d2e97ac1d3250ae0ff`：将两个仍要求旧命令的现行确定性断言同步到有效 CLI 参数。

## 精确改动

- `evals/official-writing/graders/official_writing_rubric.py`：Promptfoo 输出扫描增加 `delivery_mode="draft-body"`。
- `tools/run_real_article_eval.py`：真实样文草稿扫描增加 `delivery_mode="draft-body"`。
- `chinese-official-writing/references/final-review-layers.md`：终稿示例改为 `python scripts/prose_lint.py --delivery-mode draft-body --format --structure <draft>`；使用 `tools/sync_adapters.py` 同步到 `skills`、`.agents`、`.qwen`、Hermes 和 OpenClaw 五个发行镜像。
- `AGENTS.md`：当前 1.5.33 说明中的不存在参数 `--mode draft-body` 改为真实参数 `--delivery-mode draft-body`。
- `tests/test_promptfoo_eval.py`、`tests/test_review_regressions.py`：分别锁定两条终稿评测调用必须传入 `draft-body`。
- `tests/test_skill_boundary.py`、`tools/run_real_prompt_ablation.py`：只更新当前有效命令的断言，不修改评测机制。
- 未修改任何既有历史证据原文；相对基线，`tests/evidence/` 中只有本轮新增的预注册和结果文件。

## 保持 generic 的调用

- `tools/run_real_prompt_ablation.py` 继续只在用例声明 `lint_delivery_mode` 时传递模式，兼容不支持该参数的旧基线；未声明模式的用例仍为 `generic`。
- `tools/build_agent_eval_packet.py` 扫描包含多篇样稿和评审标题的合并式 A/B 文档，继续为 `generic`。
- `evals/ai-dedupe/local_scan.py` 接受 `output` 或 `text` 等开放形态语料，只做建议性的 AI 味和相似度扫描，继续为 `generic`。

## 实际验证

1. `python -m unittest tests.test_promptfoo_eval.PromptfooGraderTests.test_lint_summary_uses_draft_body_delivery_mode tests.test_review_regressions.RealArticleEvalAuditTests.test_evaluate_uses_draft_body_delivery_mode`
   - `2/2` 通过。
2. `python -m unittest tests.test_promptfoo_eval tests.test_review_regressions`
   - `148/148` 通过。
3. `python chinese-official-writing/scripts/prose_lint.py --delivery-mode draft-body --format --structure tests/fixtures/clean_prose_corpus.json`
   - 退出码 `0`，输出 `No prose risks found.`，证明现行 CLI 示例可执行。
4. `python tools/run_real_article_eval.py --out output/delivery-mode-call-chain-calibration-targeted`
   - 成功生成摘要；对 20 个固化草稿以相同路径标签比较 `generic` 与 `draft-body`，finding 差异为 `0`。
5. 首次 `python -m unittest discover -s tests`
   - 共运行 424 项，2 项失败；失败均为仍断言旧命令字符串的现行确定性守卫，不是产品行为失败。提交 `2891a5ab` 后定向复跑 `2/2` 通过。
6. 最终 `python -m unittest discover -s tests`
   - `424/424` 通过。
7. `npm run eval:official-writing:smoke`
   - `20/20` 通过，0 failed、0 errors；pairwise 为 skill 10、baseline 0、tie 0、invalid 0、needs manual review 0，judge consistency `1.0`。
8. `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`
   - `Skill is valid!`
9. `python tools/sync_adapters.py`
   - canonical 与五个发行镜像同步；同步后无新增 staged diff，工作树清洁。
10. `git diff --check b2be5d8bb9958ab754907a1b6929085302e2056d...HEAD`
    - 通过。

## 兼容性与剩余风险

- `prose_lint.scan()` 的默认值仍是 `generic`，未改 API 签名；未显式选择模式的外部调用不受影响。
- 两条终稿评测现在会对真实存在的材料读取旁白、约束自证、交付说明和英文思考残片计入既有风险权重。包含这些残留的后续真实评测可能比过去得分更低，甚至触发现有发布阈值；这是本候选要修复的漏检，不是正文生成行为变化。
- 终稿命令仍未增加 `--strict` 或 `--fail-on`，只输出复核线索，不会自动阻断或改写稿件。
- 固化真实样文的 20 个草稿没有新增 finding，Promptfoo smoke 也未出现阈值回退；这不能替代以后发布候选上的真实模型写稿和独立 verifier。
