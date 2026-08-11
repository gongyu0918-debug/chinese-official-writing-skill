# 解释性句尾成簇检测结果（2026-08-02）

## 结论

PASS，保留在隔离研究分支，具备交由主线程决定是否合并的条件；本轮未合并 `main`、未改版本号、未发布。

本候选只增加 `--structure` 下的 `low / explanatory-tail-cluster` 线索：最近5个实质段中至少3段以“为……提供……基础/依据/支撑/保障/条件”收尾时提示一次。它不进入写作 Prompt，不自动改稿，不把单词设为黑名单，也不改变 `--strict --fail-on medium` 的通过结果。

## 提交

- 固定基线：`b2be5d8bb9958ab754907a1b6929085302e2056d`
- 预注册：`9023ac86101ca2a8a9fafe917c192a9d523bdae6`
- 产品提交：`3ab56fad95cedd0f0fe83eabfc5db8e27e2e6270`
- 分支：`codex/explanatory-tail-cluster-v1533-r1`
- worktree：`output/research-worktrees/explanatory-tail-cluster-v1533-r1`

## 真实历史稿重放

| 样本 | 固定基线 | 候选 | 结论 |
| --- | --- | --- | --- |
| `output/atomic-expanded-20260730/ET01/arm-info.txt` | 无对应结构提示 | 1个 low；定位第9、13、15行的3处同构句尾 | 命中预注册机制 |
| `output/manual-annotation-1.5.6/raw/agent-4/07-合同档案归集试点方案.txt` | 无对应结构提示 | 1个 low；定位第19、21、27行的3处同构句尾 | 命中预注册机制 |

候选对筛选出的2,738个既有稿件文件做只读重放，共命中3个路径、3个 finding。其中 `atomic-expanded-20260730/blind-packets/ET01/A.txt` 与第一份样本正文相同，因此实际对应2份唯一正文；未发现偏离预注册句尾结构的额外命中。

clean corpus 结果：现有12条脱敏 clean fixture 与7篇归档完整稿均未出现 `explanatory-tail-cluster`，即新标签误报为0/19。该统计只说明现有样本范围，不能替代所有文种的长期误报率。

## 实际验证

- `python -m unittest tests.test_explanatory_tail_cluster tests.test_review_regressions -v`：74/74 通过。
- `python -m unittest discover -s tests`：430/430 通过。
- `npm run eval:official-writing:smoke`：20/20 通过；Promptfoo 提示本机版本 `0.121.11` 低于 `0.121.20`，未影响本轮结果。
- `python tools/run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\release-worktrees\release-1.5.23-main --baseline-label main-b2be5d8b --current-root . --out output\explanatory-tail-cluster-ablation-20260802`：固定基线111/111、候选111/111。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过。
- `python -m py_compile chinese-official-writing\scripts\prose_lint.py`：通过。
- `python tools\sync_adapters.py` 后，canonical 与5份运行镜像脚本 SHA-256 均为 `34353C2D1C6000C56D858837ABDEF8D31309E22EEDD8B95D41E1C0666F51B5AA`。
- `git diff --check b2be5d8bb9958ab754907a1b6929085302e2056d..HEAD`：通过。

首次专项运行有2项测试失败，原因是共用测试夹具的三个段落短于预注册的45字符实质段阈值；两份真实历史稿当时已经命中。修正只补足测试段落，未降低阈值、未扩大正则，复跑后全部通过。

## 剩余边界

- 本候选只覆盖已经达到三处门槛的“为……提供……”解释性句尾，不宣称覆盖“推动……”“确保……”等其他口号式收尾。
- 有材料支撑的同构句尾也可能得到 low 提示，因此提示语明确允许保留具有独立事实作用的句尾；它不能作为自动删除依据。
- 检测必须显式启用 `--structure`。裸 `--strict` 仍按脚本既有默认值处理 low finding；CI/发布检查继续使用文档规定的 `--strict --fail-on medium`。
- 本轮是脚本只读检测更新，未新生成真实稿；真实证据全部复用既有归档，不能据此声称写作生成质量发生变化。
