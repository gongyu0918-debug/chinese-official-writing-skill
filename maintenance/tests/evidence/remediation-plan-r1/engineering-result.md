# WR-028 工程接入结果

## 接入范围

- 固定上一发布基线：`5869234bcfee5aeb7f70762035a8ee593569fbc3`
- 真实写稿选定产品：canonical `SKILL.md` 增加整改方案直达路由和表项；新增 `references/genre-playbook-remediation-plan.md`，R2 后为 2,858 bytes、20 行。
- 同步五套普通兼容镜像：Agent Skills、Qwen Code、QwenWork、Hermes、OpenClaw。兼容包继续排除 Hook companion；OpenClaw 保持宿主专用 frontmatter。
- 新增直接断言，覆盖明确意图路由、相邻文种边界、状态先落位、合理归因与未来措施、固定机制克制、只交正文，以及五套专叶镜像逐字一致。
- 未改 description、Hook、版本号、普通方案叶、通用事实边界或其他文种规则；未合入 `main`、未推送、未发布。

## 验证结果

| 门 | 结果 |
| --- | --- |
| WR-028 R1 真稿 | 五家25份候选，21个双臂技术有效对；控制题10/10未读专叶；发现1处候选独有状态遗漏，未直接放行 |
| WR-028 R2 真稿 | 五家10份候选，8份隔离有效；短、中两题各4份有效稿全部保留状态并形成实际措施，R1硬回退消除 |
| 定向单测 | 路由/状态/镜像4项通过；状态一致性、专叶、Markdown本地链接3项复测通过 |
| Skill Creator quick validate | canonical、Agent Skills、Qwen Code、QwenWork、Hermes五处均返回 `Skill is valid!` |
| 全量 unittest | 首次 774 项中 1 项失败，原因为旧断言写死“当前无活动候选”；更新为识别 WR-028 后相关3项通过，全量复跑 `774/774 OK` |
| 仓库语法与数据 | tracked Python `194/194` 编译通过；tracked JSON `197/197` 解析通过 |
| 镜像幂等与差异 | `sync_adapters.py` 复跑后只保留预期镜像差异；`git diff --check` 无空白错误 |

## 透明记录

- `sync_adapters.py` 没有帮助参数；首次执行 `--help` 实际完成了一次五镜像同步。本次动作正处于真实写稿已通过后的工程阶段，结果可用，但不把该命令记成帮助查询。
- 一次把镜像复同步与全仓 Python 读取并行，OpenClaw 目录在删除重建瞬间产生临时 `FileNotFoundError`；同步完成后文件存在，按顺序重跑为 `194/194` 通过。
- JSON 首次用 PowerShell 对象模式解析时遇到合法空键；改用 `ConvertFrom-Json -AsHashtable -ErrorAction Stop` 后 `197/197` 通过。两次编排/解析失败均保留，不冒充产品失败或通过。

## 实际命令

```powershell
python maintenance/tools/sync_adapters.py
python -m unittest maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_remediation_plan_has_a_state_preserving_atomic_leaf maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_adapter_skill_copies_keep_boundaries maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_reference_loading_table_keeps_progressive_disclosure maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_openclaw_github_package_is_current_mit_and_hook_free
python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py <canonical-or-mirror-root>
python -B -m unittest maintenance.tests.test_status_ledger_consistency.StatusLedgerConsistencyTests.test_post_v1624_spec_audit_records_numbering_backlogs_and_paid_sync maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_remediation_plan_has_a_state_preserving_atomic_leaf maintenance.tests.test_repository_reachability.RepositoryReachabilityTests.test_active_markdown_local_links_exist
python -B -m unittest discover -s maintenance/tests
python -B -c "<compile every tracked Python file in memory>"
Get-Content <each tracked JSON> -Raw | ConvertFrom-Json -AsHashtable
git diff --check
```

## 判定

`WR-028-REMEDIATION-PLAN-R2` 状态为 `REAL_WRITING_PASSED / ENGINEERING_VERIFIED / MERGE_READY / NOT_MERGED`。候选可以作为一个干净原子合入公开主线；是否合并仍等待当次明确授权。
