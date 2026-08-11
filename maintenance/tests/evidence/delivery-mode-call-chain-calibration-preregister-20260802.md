# 终稿 delivery-mode 调用链校准预注册（2026-08-02）

## 基线与问题

- 独立 worktree 基线：`main@b2be5d8bb9958ab754907a1b6929085302e2056d`。
- `prose_lint.py` 的有效 CLI 参数是 `--delivery-mode draft-body`，Python API 参数是 `delivery_mode="draft-body"`；默认值 `generic` 不加载终稿交付残留规则。
- 当前 Promptfoo 公文成稿评分和真实样文成稿评估都扫描最终正文，却未传 `delivery_mode`，因此材料读取旁白、约束自证、交付说明和英文思考残片不会进入这两条评测结果。
- 当前有效维护说明误写为不存在的 `--mode draft-body`；终稿复核工具示例也没有选择 `draft-body`。

## 单变量范围

只校准终稿检查的既有参数调用：

1. `evals/official-writing/graders/official_writing_rubric.py` 的 Promptfoo 成稿扫描明确传入 `delivery_mode="draft-body"`。
2. `tools/run_real_article_eval.py` 的真实样文成稿扫描明确传入 `delivery_mode="draft-body"`。
3. 当前有效维护说明改用真实 CLI 参数；`final-review-layers.md` 的终稿工具示例补入同一参数，并通过既有同步工具更新发行镜像。
4. 增加定向回归，证明两条终稿调用确实选择 `draft-body`。

以下调用保持原状：

- `tools/run_real_prompt_ablation.py` 按用例中的 `lint_delivery_mode` 选择模式；未声明模式的历史用例继续使用 `generic`。
- `tools/build_agent_eval_packet.py` 扫描包含多篇样稿和评审标题的合并式 A/B 产物，不按单篇终稿处理，继续使用 `generic`。
- `evals/ai-dedupe/local_scan.py` 接受形态开放的 AI 味/相似度语料，目标不是终稿交付协议检查，继续使用 `generic`。

## 明确不做

- 不扩充词表、正则或场景规则，不修改命中严重度。
- 不修改写作 Prompt、任务路由、reference 加载条件、复核顺序、输出模式、修订次数或回退方式。
- 不把 lint 变为强制门禁或自动改稿器。
- 不修改任何历史发布、候选或评测证据原文中的旧命令记录。
- 不合并 `main`，不发布，不移动版本号或 tag。

## 验收

- 定向测试覆盖 Promptfoo 终稿评分和真实样文终稿评估的模式参数。
- `python -m unittest discover -s tests` 全量通过。
- `npm run eval:official-writing:smoke` 通过。
- canonical 与发行镜像同步，quick validate 通过。
- `git diff --check` 通过；最终人工核对非终稿调用仍为 `generic`，历史证据无 diff。
