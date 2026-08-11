# 终稿 lint 模式自然选择候选复验预注册（v1539-r1）

## 基线与来源

- 候选来源：v1537 系列 `codex/lint-mode-routing-v1537-r1`（087cc1b），原预注册 `lint-mode-routing-v1537-r1-preregister-20260806.md`。
- 本轮固定基线：`v1.5.38` 产品提交 `c3fa2128ef9426b4ebb135986a7e19feccf08421`。
- 候选已 rebase 到 1.5.38 之后的 main（968daac）。

## 单变量改动

只在入口"脚本"段开头增加短指针：检查终稿正文时按 `references/final-review-layers.md` 使用 `draft-body` 模式；完整命令继续留在终审页（final-review-layers.md 第 74 行已有 `--delivery-mode draft-body --format --structure` 全命令）。

不增加 `review-only` 或 `gap-note-allowed` 指令，不改脚本、正则、词表、严重度、自动改稿、复核次数和发布链。

## 验证计划

1. 工程门：全量 unittest（新增入口指针守卫）、Promptfoo smoke、固定 1.5.38 消融、quick validate、镜像同步幂等、`git diff --check`。
2. 真实 A/B（对固定 1.5.38，独立盲审）：
   - LM01 普通报告正文终稿：writer 自然调用 lint 时 argv 应含 `--delivery-mode draft-body`；
   - LM02 含合法否定指令或引文的正文终稿：使用 draft-body 且不误删合法内容；
   - LM03 只审不改控制题：审查意见不按 draft-body 清洗正文。
3. 若 writer 不调用 lint，记为效果无证据；人工事后调用不能代替自然触发。

通过要求：自然触发 draft-body 且无事实、数字、主体、状态、输出范围或二次修订回退方可保留；出现合法内容误删即不合并。
