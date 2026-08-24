# MT-005b6b 五提交复核

日期：2026-08-24。

## 范围与消融

- 固定基线：`main@e3ed9bb374fd13234ea0eff9ea61c9e0f3cc7e69`。
- 五提交候选：`3dddaa18b5d620291a5d7f1ac7050b7c1bcadc68`。
- 产品 diff 只在 canonical 与四套普通镜像的 description 把 `实施细则` 替换为 `细则`；把候选该片段机械恢复后，204字 description 与 main 逐字相同。
- 候选 description 为202字；canonical 正文路由与制度叶仍明确保留 `实施细则`，没有删改产品规则、Hook、版本号或发行元数据。
- 研究新增只含预登记、两个固定 cases、两个 Codex CLI runner、R1/R2结果及状态索引；忽略目录中的运行时和原始稿件未进入 Git diff。

## 实际验证

| 命令 | 结果 |
| --- | --- |
| `python -B maintenance/tools/sync_adapters.py` | 四套普通镜像同步；随后工作树无漂移。 |
| `python -B -m unittest maintenance.tests.test_description_news_trigger maintenance.tests.test_skill_boundary maintenance.tests.test_real_prompt_ablation -q` | 89/89 OK。 |
| `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -B -m unittest discover -s maintenance/tests -p 'test_*.py' -q` | 674/674 OK，60.307秒。 |
| `git diff --check` | PASS。 |
| `git status --porcelain=v1` | 空。 |

最初尝试的仓内路径 `maintenance/tools/quick_validate.py` 不存在；该次命令失败后改用已读取的 skill-creator 实际脚本路径并通过，不把失败命令记成验证通过。

## 结论

`CLEAN_MERGE_CANDIDATE`。真实写稿先行、单原子消融和工程回归均闭合；当前只形成隔离分支候选，未合入 main、未推送、未发布。
