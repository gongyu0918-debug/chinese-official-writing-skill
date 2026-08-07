# 入口清晰化五原子归并验证记录（v1539）

## 归并内容

在固定 1.5.38 主线（968daac）上依次无冲突合入五个已通过单项验证的候选：

1. `candidate-entry-scope-natural-v1539-r1`（输出范围自然化）
2. `candidate-format-entry-pointer-v1539-r1`（Word 细则迁移至 format-gbt9704 指针）
3. `candidate-search-boundary-compact-v1539-r1`（单位名称搜索句去冗余）
4. `candidate-lint-mode-routing-v1539-r1`（终稿 lint draft-body 自然触发指针）
5. `candidate-entry-route-clarity-v1539-r2`（模式词与加载顺序清晰化，保留 1.5.38 轻量卡措辞）

## 归并后工程门（2026-08-07 实跑）

| 验证 | 结果 |
| --- | --- |
| 镜像同步幂等（sync_adapters.py） | 0 漂移 |
| `python -m unittest discover -s tests` | 442/442，通过 |
| 固定 1.5.38 确定性消融 | v1.5.38 111/111；current 111/111 |
| Promptfoo stub smoke | 20/20；0 failed、0 errors |
| quick_validate | `Skill is valid!` |
| py_compile（prose_lint/review_gate/sync_adapters） | 通过 |
| `git diff --check` | 通过 |

## 宏观真实写稿盲审（对固定 1.5.38）

三题组合任务覆盖多原子交互，writer 为独立子代理（qwen3.8-max），独立 verifier 盲审：

| 任务 | 覆盖交互 | 基线 | 集成 | 结论 |
| --- | --- | --- | --- | --- |
| M1 稀疏说明+只给成稿+不补章节 | A+E | PASS | PASS | 功能等价 |
| M2 Word 版式+文后仅联系人 | A+B | PASS | PASS | 版式要素全对，集成臂读取链更完整，4≥3 |
| M3 只审不改+合法否定句+不联网 | C+D+E | PASS | PASS | 均未联网、未误报合法否定、未越权改稿 |

verifier 总结论：三组配对均未发现输出范围失控、版式要素错误、越权改稿、误删/误报合法内容、擅自联网或编造事实；集成稿不存在任何功能性回退。

## 结论

五个原子单项验证与归并验证均通过，满足"不劣于已发布基线"口径，可合并回主线（不改版本号、不发布市场）。
