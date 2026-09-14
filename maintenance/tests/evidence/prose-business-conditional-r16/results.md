# 办理条件误报的有界修复原型

原型已完成：删除否定词与判断谓词之间任意跨越 70 字的匹配，保留直接判断及“据此/由此”“直接/充分/准确”等紧邻修饰。产品差异 +3/-3 行；没有加入参会、综合岗等业务词黑名单，没有新增框架、标签、严重性或执行门槛。

原型仅位于 `output/prose-business-conditional-r16/candidate/scripts/prose_lint.py`。canonical、final 冻结包及其他产品文件未改，未 commit，未调用写稿模型。

## 绑定

- 基线：`output/reference-integration-r16-final/candidate/scripts/prose_lint.py`，已含 F03。
- 基线 SHA-256：`513934d60e145087d992b2383dc92a522ecd9497446194ce1885e937800486fc`。
- 原型 SHA-256：`d69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc`。
- 测试前后基线脚本 SHA 未变；原型目录只有该单脚本。构建器、测试与差异均可复用。

## 收益与覆盖损失

原句“不能参会的会前向综合岗说明”中的“不能”限定参会行为；原规则跨过办理条件后命中“说明”，误当成“不能说明”的证据判断。候选使判断谓词与否定结构紧邻，阻止这类跨越。

| 对照范围 | 组数，含两种正文模式 | 原脚本命中 | 候选命中 |
| --- | ---: | ---: | ---: |
| 真实句子及 9 条相近正常办理条件 | 20 | 20 | 0 |
| 14 条直接推断、证据和依据判断 | 28 | 28 | 28 |
| 3 条含长距离介词或条件插入的推断 | 6 | 6 | 0 |

直接的“不能据此认定”“不足以证明”“不宜作为依据”“不能形成采购结论”等仍为原来的 `protective-negative-inference/medium`，另外两类未决结论与否定边界标签也保留。两次候选真实 CLI 对办理条件返回空数组、退出码 0；对直接判断仍返回原标签、退出码 1（测试使用既有严格模式）。

收窄后不再自动识别以下长距离表达，这项损失已进入测试与机器记录，不能把它们算作普通业务负例：

- “不能仅凭本次抽查结果认定问题已经彻底消除。”
- “不足以在缺少连续监测记录时证明系统始终正常。”
- “无法对不同统计周期的数据直接比较。”

仍有语义重合风险。例如“不能说明原因的，暂缓受理。”中否定词直接连接“说明”，候选仍会给出提示。本原型降低任意跨越导致的误报，不宣称消灭所有误报或保持所有长距离表达的召回；有据正文是否保留仍需语义复核。

## 实际验证

按以下顺序运行，先复现基线，再构建、验证候选：

```text
python -B maintenance/tests/evidence/prose-business-conditional-r16/test_business_conditional.py --phase baseline
python -B maintenance/tests/evidence/prose-business-conditional-r16/build.py
python -B maintenance/tests/evidence/prose-business-conditional-r16/test_business_conditional.py --phase candidate
```

两次完整测试结果均为 **22 个方法：21 个通过，0 个断言失败，1 个错误，退出码 1**。不能报为全套通过。

- 新增 6 个方法覆盖正常办理条件、直接阳性、长距离损失、同稿后续独立判断、模式/提示区及真实 CLI，全部按各自基线或候选预期通过。
- `test_protective_negative_tail_lint.py` 的全部 10 个方法均尝试执行；只把脚本 import 和 CLI 路径绑定到被测脚本，原断言与方法保持不变。9 个脚本、语料、CLI 方法通过。
- 剩余的 `test_review_and_lint_routes_preserve_evidence_bounded_semantic_choices` 在修改前后均因 `chinese-official-writing/references/final-review-layers.md` 不存在而发生 `FileNotFoundError`。这是旧文本路由测试与现目录的失配，不是候选新增错误。未修改测试、伪造旧页或把该项改记为通过。
- F03 的 6 个针对性方法全部通过，含 32 组包装残留检查及两次 CLI；普通技术代码、审稿引用、业务版本标识和文后提示示例未出现这组测试可见的回归。
- AST 解析及行尾空白检查通过。基线和候选复用的测试源码 SHA 相同，没有新增失败或错误。

机器记录在 `output/prose-business-conditional-r16/`：`baseline-001.json`、`candidate-001.json` 保存真实扫描和 CLI 输出及完整 unittest 日志；`build.json`、`candidate.diff` 保存绑定与产品差异；`comparison.json` 保存收益、损失、同一旧错误、剩余歧义及代码 SHA。

## 尚未完成的验证与解释边界

本任务没有执行写稿模型、组合包全量验证或发布。旧路由文本测试仍需在其所属维护范围另行处理，本原型没有更改其他文件。此次误报只是一条已复现的继承问题线索，不能据此认定它是本轮真实写稿超时的唯一原因。
