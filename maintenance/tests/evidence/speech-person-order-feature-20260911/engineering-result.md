# 人物排序功能工程检查

2026-09-11。冻结产品为 `72a1d400`，canonical 五文件语义未改；本记录只覆盖工程适配，不重新评估真实写稿结论。

## 变更

- `maintenance/tests/test_skill_boundary.py` 的索引冻结断言随新增 `speech-person-order.md` 从 36 行更新为 37 行，并绑定当前排序后的 SHA-256：`8b61978940a13e42fef8e6a507b462f836b9e028665128ec6d5bf87145811d62`。
- 使用 `maintenance/tools/sync_adapters.py` 同步 agent-skills、qwen-code、qwenwork、hermes 和 openclaw 五个普通镜像。未修改 red-skillhub 冻结包、版本字段、Hook 或写稿 harness。

## 实际检查

解释器：`C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`。

- `-m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_repository_reachability maintenance.tests.test_information_selection_classification`：94/94 通过。
- `C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py` 分别检查 canonical 与四个普通 Skill 根：5/5 通过（均为 `Skill is valid!`）。
- `-m unittest discover -s maintenance/tests -p 'test_*.py'`：850/850 通过，151.830 秒。
- `git diff --cached --check`：通过。

测试输出仅保留在本次工具回执中，未另写入原始日志文件；本记录不替代回执。

未重跑真实 Hook，未重新冻结或修改 canonical 产品，未执行合并、推送或发布。
