# 旧 CLI 与显式两跳路由责任迁移结果（R18）

指定三处已迁移，两个 CLI 方法已实际执行通过，平台卡方法恢复通过。另一个 helper 调用方法仍有范围外旧整句断言；完整模块仍为失败状态，未包装成全绿。

## 改动范围

- 基线 HEAD：`8f9d08898cd1f52b6f16f32691739af5a7e4067d`。仅修改 [test_skill_boundary.py](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/test_skill_boundary.py>) 中以下三个定义；63 行增加、42 行删除。
- [read_routing_surfaces](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/test_skill_boundary.py:51>)：首页显式链接索引，索引显式链接兼容分流页，读取固定目标；不在任意页面搜索补链。
- [test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/test_skill_boundary.py:435>)：文档 owner 迁到 writing-rules/compression-details，保留有依据、篇幅上限和下限未达标边界，真实执行 nonspace/cjk。
- [test_review_command_includes_interpreter_and_draft_path](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/test_skill_boundary.py:1267>)：共性复核桥及当前 prose-lint-usage 命令；验证带引号的脚本/草稿路径，真实执行三个 delivery mode 并解析 JSON。
- 文档契约放入独立 subTest；如失配仍记录失败/错误，随后继续运行独立 CLI 子测试。未加 skip、未吞掉错误、未恢复撤页。
- 用原定义重建出的全文件 hash 与改前一致，证明其余字节完全不变，CRLF 保留。原 SHA-256 `f8095b65819f9d14383ce30670e49229e097fb3d60ebd6513d5a4eb2b207df9f`；新 SHA-256 `b5d10c7d910ac6397abced3081f66f42f130681ed154d36ebe197f47938c629d`。产品输入 hash 保持，未改其他方法、常量、产品或镜像，未 commit。

## 限定验证与实际子进程

```text
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B maintenance/tests/evidence/legacy-cli-migration-r18/run_focused.py
```

4 个已有方法实际执行，3 个通过、1 个受影响，6 个 failure 子事件、0 error；命令退出码 1。通过的是两项 CLI 方法和 `test_openclaw_skill_card_uses_absolute_links_and_key_genres`。`test_lightened_indices_resolve_from_each_skill_root_and_keep_quality_bridges` 在各 root 的 helper 两跳成功后，仍因首页旧整句“文种或行文关系冲突时再读取 references/genre-routing.md”失配；后续该方法还有已撤页断言，均不在本次修改授权内。

5 个 helper 小验证通过：有效两跳、首页缺入口、索引缺第二跳、索引文件缺失、兼容页文件缺失。索引第二跳缺失时，即便首页直链兼容页或无关页面含目标链接，仍失败；未用任意文件内容兜底。

实际子进程记录器包装原 subprocess.run，并调用原函数取得真实结果，没有替换命令结果或模拟输出。共记录 5 次真实命令，均用显式 Python 3.13，返回码全部为 0：

| CLI | 输入/参数责任 | 实际结果 |
| --- | --- | --- |
| draft_length nonspace | stdin、--json、min=max=8，正文后附独立提示 | count=8，within，draft-before-postscript |
| draft_length cjk | 同一 stdin、--json、min=max=2 | count=2，within，draft-before-postscript |
| prose_lint draft-body | stdin 正文+文后提示，--structure --format --json | 检出 unexpected-external-note |
| prose_lint gap-note-allowed | 同一 stdin 和格式/结构参数 | 不将独立提示报为 unexpected-external-note |
| prose_lint review-only | stdin 审核意见与相同协议参数 | JSON list，未报上述正文提示残留 |

完整 [focused.log](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/focused.log>)、[focused-result.json](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/focused-result.json>) 及 [cli-calls/](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/cli-calls>) 保存命令、stdin、stdout/stderr 文本、保存文本 SHA-256 和退出码。没有使用 PATH 的 Hermes Python，也未安装依赖。

## 完整模块只运行一次

```text
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B -m unittest maintenance.tests.test_skill_boundary
```

| 统计口径 | R17 记录 | 本次 R18 |
| --- | ---: | ---: |
| 方法总数 | 81 | 81 |
| 有失败/错误的方法 | 53 | 50 |
| 无失败记录的方法 | 28 | 31 |
| failure 事件 | 78 | 76 |
| error 事件 | 35 | 34 |

本次完整模块退出码 1。[R18 完整日志](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/module-python313.log>) 另存，SHA-256 `c9e615e12543296f5e788ccada1201cfc4465ded2734127c2ba92d484bad6406`；[module-result.json](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/module-result.json>) 保留 50 个受影响方法名。R17 原日志未覆盖，前后 SHA-256 同为 `7833d5d508919da66dba978374db4dba25da58c6d8aba6892dea5c12cef624c8`。

相比 R17 不再失败的恰是两项 CLI 方法与平台卡方法，没有新增失败方法。failure/error 仍含 subTest，不能把 76+34 当成 110 个独立方法或写作能力失败；基线已有其他 R17 后提交，统计对照也不是模型写作质量对照。

## 尚未完成与风险

- 该模块还有 50 个方法需要按原责任继续迁移/核查；本次没有修改范围外旧整句、撤页读取或版本常量。
- helper 的图可达和 CLI 执行通过不代表 native Agent 已遵循路由、实际处理风险或生成质量改善。主任务并行实稿不在本次验证内。
- R18 共性页候选仅在 output；本次测试使用当前 canonical。未跑模型、未安装依赖、未 commit。
- 长度方法中的三条正文正则绑定当前 canonical 的有据事实、篇幅上限及不足说明。若后续采用 R18 共性压缩，应按最终语义重新核对这些断言；本次不为尚未采用的原型调整测试。
- [字节范围绑定](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/edit-binding.json>)、[改前定义](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/before-sections.json>)、[简洁摘要](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/maintenance/tests/evidence/legacy-cli-migration-r18/summary.json>) 可供主任务复核。`git diff --check -- maintenance/tests/test_skill_boundary.py` 无空白错误；Git 的换行提示未改变原 CRLF 或授权范围外字节。
