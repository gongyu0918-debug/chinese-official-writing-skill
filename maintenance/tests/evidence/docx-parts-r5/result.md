# DOCX 检查部件修复 R5

基线为重构分支 `8adaa1e64104225d3455b657ffb7214406859f88`。独立冷审对冻结组合候选逐行审查脚本并复现两项缺陷，报告见 [cold-review.md](cold-review.md)。

普通 prose_lint 改为枚举 ZIP 内所有 header/footer XML，保留主文档、脚注、尾注、批注扫描；两种 DOCX 范围都要求主文档存在。draft_length 继续只计主文档，未改生命周期或 Hook。五个兼容包同步同一脚本。

验证：`python -B -m unittest maintenance.tests.test_review_regressions maintenance.tests.test_draft_length` 共 107 项通过，包括新增第四页眉/第十二页脚和缺失主文档两个 CLI 回归。镜像与 MIT 边界：`python -B -m unittest maintenance.tests.test_mit_script_boundary` 4 项通过。`git diff --check` 无空白错误。

这些是确定的读取/退出缺陷修复，不代表真实模型已稳定调用脚本，也不能覆盖检查后追加的最终消息旁白。未新增 OPC 关系解析，未验证 Word 渲染或所有异常 ZIP 类型。报告中的规则路由问题在后续独立候选处理。
