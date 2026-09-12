# 全稿共性规则减负 R10

2026-09-13。用户最新要求替代先前短稿出口设计：所有稿件使用精简的共性层，不增加长短稿入口、分流或复读管控。数万字、多篇材料等特殊任务再按实际需要处理。R9 系列尚未运行写稿，保留草案和冷审，不计质量结果。

## 对照与变化

双臂在 `output/common-layer-experiment-r10/{baseline,candidate}`。基线是冻结 R8，额外加入用户明确的普通完整短稿至少 80 字；候选同样保留该要求。prompt 长度不是门槛。局部替换、字段处理及用户明确的更短要求按任务范围处理。

候选将 information-selection、final-review-layers、delivery 合为 writing-rules，精炼 anti-ai-patterns 和 prose-lint-usage，首页只引入一次共同流程。语义归属参照 `output/common-layer-ownership-r10.md`；原文件保存在基线。其余文种页主要同步共性路径与原回跳标题。目录清单、文件 SHA-256 和差异在 build.json、changes.diff 记录。

共同规则体量按统一换行 Unicode 字符计算：R8 五页合计 5944，候选三页合计 3001（含启动前冷审修正）。数字不含首页和其他按需叶，也不是调用 token 或费用。当前候选尚未采纳；canonical、镜像、main、安装和发布未更新。

## 必须保留

- 主文种与用户模板、材料事实、业务状态、合理原因及影响分析；允许有据推断和授权拟方案，具体事实需对应依据。
- 当前日期可作未给定的草稿落款，明示留空或待确认时保持要求；业务日期单独判断。
- 普通完整短稿至少 80 字，实际调用独立字数脚本；正文与文后提示分别计。
- 抗 AI 味仍必查；prose_lint 扫描实际文本，按结果处理合理用语及错误，不靠清空提示替代正文判断。
- 默认文后提示、上一轮缺项和未处理错误、正文隔离；审稿意见和审核后完整改稿分别符合用户任务。
- 复杂金额、责任、表格与附件实际相关时仍充分核对；不按几个词或长度过早截断。

## 原生写稿计划

复用 `maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py`，每臂自主读取 Skill，使用隔离 Codex CLI profile、每调用独立目录、同题同配置。

两通道：alibaba-token-plan/qwen3.8-flash（medium，沿用 max/high 不收束后的可执行配置）、command-code/deepseek-deepseek-v4.1-flash（provider 默认）；单次上限 240 秒。

六题：explanation、material_based_analysis、minutes_local、complex_application、guards_grammar_quote、review_rewrite。共 12 对、24 次调用。分别覆盖说明与缺项、申请理由、局部范围、附件金额、引语语法、审后完整改稿。

比较正文质量、完整交付、字数、实际读页、工具调用及用量。技术失败不当作文种质量失败；日期、合理推断及正常风格变化按用户已校准的口径判断。样本差异不直接证明规则因果，较弱项另看位置与两侧情况。

本组是 R8 与共性精炼包的归因比较；不是旧 1.x 对最终 2.0 的验收。通过后仍需补其他场景、五通道及旧金线组合验证。
