# WR-005b / WR-026 本地 main 合入记录

日期：2026-09-02

## 合入范围

- 合入前本地 `main`：`69515dbc216e6e057e497fbaa0c1cebb9dac6547`。
- `WR-026` 候选：`codex/wr026-short-advice-r3@a22fa104a20a40b720db8844ebb275c21b9df9a1`；合并提交 `936c63e9`。只合入真实写稿、公开样本校准和终态证据，产品、Hook、description、镜像、版本及包体相对合入前 `main` 均不变。
- `WR-005b` 候选：`codex/wr005b-short-route-semantic-r1@16fe90c8c59a1a64e38647836c1eb9fa11ce2456`；合并提交 `8d9cff6c`。合入语义短稿路由、短稿自然度页、五套普通兼容镜像、定向测试和证据；不改 Hook、description、版本或发布面。
- 终态：`WR-026 = BASELINE_RETAINED / WAIT_NEW_COUNTEREXAMPLE`；`WR-005b = R3_SELECTED_ENGINEERING_VERIFIED / MERGED_MAIN_POST_V1.6.23`。

## 合并后验证

1. `python maintenance/tools/sync_adapters.py`
   - 退出码 `0`；执行后工作树无新增差异，五套镜像幂等。
2. `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py <skill-root>`
   - canonical、Agent Skills、Qwen Code、QwenWork、Hermes 五套通过。
   - OpenClaw 因既有 `category: writing` 扩展字段不在通用校验器白名单而被拒绝；该字段已存在于 `v1.6.23`，不是本候选新增。仓库自身全量门继续覆盖 OpenClaw 包。
3. `python -m unittest maintenance.tests.test_short_draft_naturalness maintenance.tests.test_advisory_feedback_leaf maintenance.tests.test_status_ledger_consistency maintenance.tests.test_skill_boundary maintenance.tests.test_skill_frontmatter_relief_harness`
   - `Ran 102 tests in 9.559s`，`OK`。
4. `python -m py_compile maintenance/tools/sync_adapters.py maintenance/tests/evidence/short-route-semantic-r1/run_eval.py maintenance/tests/evidence/short-advice-routing-r1/run_baseline.py maintenance/tests/evidence/short-advice-routing-r1/run_candidate.py`
   - 退出码 `0`。
5. `python -m json.tool` 校验 `short-route-semantic-r1/cases.json` 与 `config.json`
   - 退出码 `0`。
6. `python -m unittest discover -s maintenance/tests -p "test_*.py"`
   - `Ran 761 tests in 146.065s`，`OK`。
7. `git diff --check`
   - 通过。

## 边界复核

- `69515dbc..main` 的产品差异只包含 canonical `SKILL.md`、`short-draft-naturalness.md` 及其五套普通兼容镜像；其余差异为规格、测试和证据。
- `hooks/`、付费提纲、版本文件和发布元数据相对合入前 `main` 均为零差异。
- `v1.6.23^{commit}` 仍为 `6a6ededa2ec287f68457ec1d5762aabae8e79bac`，且仍是当前 `main` 的祖先。
- 本次只更新本地 `main`；未推送、未移动标签、未创建 Release、未上传任何平台。
