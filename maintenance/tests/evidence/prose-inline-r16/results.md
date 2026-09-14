# F03 行内代码残留检查原型

结果：原问题已复现，原型通过针对性检查及选定的现有回归。只构建 `output/prose-inline-r16/candidate/scripts/prose_lint.py`，产品差异为 +17/-3 行；未修改 canonical、完整冻结候选或其他产品脚本。

工作树：`codex/reference-rewrite-20260912`，本次读取 HEAD 为 `35ea2ef441755d0708ea41d771c11f367a24f118`。本子任务的维护代码与证据交父侧组合后统一提交，不单独在共享工作树 commit。

## 绑定与修改

- 原脚本 SHA-256：`e843ddb35ec19653fe702e09ffc9e2e962113dcd015ae51c7547f3026ed3c4b8`。
- 原型 SHA-256：`513934d60e145087d992b2383dc92a522ecd9497446194ce1885e937800486fc`。
- 完整冻结候选 map 仍为 `1f113afba08a2d6e5bb0a2c0c9ed1caf3a1440de3cf2cdc521cb3edd779971c6`，73 文件未变。
- 复用现有行内代码范围计算，将原先“范围定位并判断”拆为范围函数与原有判断函数。正文模式另用现有 `delivery_absolute` 加 `DELIVERY_BODY_ONLY_LABELS` 检查行内内容；没有新增词表、正则或文种路由。
- 单独检查代码片段内容，使已有行首锚定的英文推理、正文前言和制作说明规则同样可命中。命中保持原标签、严重性及原稿行号。
- 检查仅进入 `draft-body`、`gap-note-allowed` 的正文部分。generic、review-only、文后提示示例及其他普通代码规则沿用既有行为；业务版本标识未升级为高风险。

## 实际命令与结果

以下命令均在本工作树根目录运行，顺序为原脚本复现、构建、候选回归。

```text
python -B maintenance/tests/evidence/prose-inline-r16/test_inline_residue.py --phase baseline
python -B maintenance/tests/evidence/prose-inline-r16/build.py
python -B maintenance/tests/evidence/prose-inline-r16/test_inline_residue.py --phase candidate
```

- 原脚本：8 类残留 × 2 种正文模式，16/16 组复现“原文有命中、反引号包装后无命中”；两次原 CLI 也返回空数组及退出码 0。
- 候选：25/25 个测试方法通过，失败 0、错误 0。其中 6 个针对性方法覆盖 32 组包装残留、普通技术代码、业务版本状态、generic/review-only 引文、文后提示示例及两次真实 CLI；19 个方法复用现有 `test_review_regressions.py`，方法正文未改。
- 两次候选 CLI 均在第 3 行报告 `thought-leak/high`，严格模式退出码为 1；stderr 为空。
- 现有回归用 AST 原样抽取选定类方法，仅把 `prose_lint` 绑定到本原型，避免导入无关写稿模型 harness。选择清单和测试文件 SHA 均已保存。
- 构建器、测试文件及原型脚本 AST 解析通过，无行尾空白。`git -c core.autocrlf=false diff --no-index --check -- <原脚本> <原型>` 无空白错误输出；退出码 1 表示两输入存在差异。

机器输出均在 `output/prose-inline-r16/`：

- `baseline-001.json`：原脚本 16 组对照、两次 CLI 的真实输入与原始输出。
- `candidate-001.json`：32 组阳性扫描结果、两次 CLI 和 25 个测试方法的完整 unittest 记录。
- `build.json`、`candidate.diff`：原脚本与原型绑定及完整差异。
- `validation.json`：冻结 map、代码 SHA、AST/空白检查、现有测试源 SHA 和改动量。

## 未完成与风险

本任务的原型与最小脚本回归已完成。未运行写稿模型、Word 渲染或完整候选全量验证；尚未与父侧 F01/F02 组合，也未进入 canonical、安装、发布或推送。

扫描仍只提供既有规则的风险线索，不自动删除正文；材料要求保留的引文和真实业务内容仍需结合上下文判断。这个原型修复已知残留被单反引号隐藏的问题，不宣称能够识别全部代码形态或所有语义残留。
