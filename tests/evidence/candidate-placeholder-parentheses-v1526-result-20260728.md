# 括号占位符误报修复结果

## 结论

PASS。候选只收紧圆括号占位符检测，没有修改写作 Prompt、任务路由、reference、复核顺序或发布链。三个正常办理要求不再误报，八个预注册的真实占位示例仍全部命中，可以合并到本地 `main`。

## 提交

- 固定基线：`8f4564e03893fdfecd6d3d88bf0280e9d4c36f3d`
- 预注册：`ae2db36`
- 产品与回归测试：`d70a8ee`
- 产品范围：canonical 与五份发行镜像的 `scripts/prose_lint.py`，以及 `tests/test_review_regressions.py`

## 复现结果

以下正常办理要求不再产生 `unfinished-placeholder`：

- `（请于7月30日前确认反馈）`
- `（请确认后反馈）`
- `（请补充盖章）`

以下真实占位仍全部命中：

- `（签发日期）`
- `（会议时间）`
- `（成文日期）`
- `（待确认）`
- `（项目金额待补充）`
- `（联系人待填写）`
- `（待签发）`
- `（成文日期待确认）`

## 实际验证

- `python -m unittest discover -s tests`：390/390 通过。
- `npm run eval:official-writing:smoke`：20/20 通过，0 error。
- `python tools/run_real_prompt_ablation.py ...`：固定基线 110/110，候选 110/110。
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：通过。
- 针对性回归与 clean corpus：6/6 通过。
- 六份 `prose_lint.py` 的 SHA-256 均为 `2D41EF6B1AAFBCDF37F3652AF478A05AA543A6E39D70D9B92684F260CBE95960`。
- `git diff --check`：通过，仅有 Windows 换行提示。

首次在沙箱内运行全量测试时，用户临时目录权限导致 149 个环境错误；首次 Promptfoo 运行还遇到 Node 调用失效 Hermes Python 和 Windows 沙箱进程启动限制。改用已核验的系统 Python 并在批准权限下按原命令复跑后，得到上述完整通过结果。这些失败未计为产品失败或通过证据。

## 边界

本轮没有降低短段重复检测阈值，没有扩大 X/XX 占位符词表，也没有修改正文扫描截止规则。上述项目仍需各自建立独立候选后验证。
