# 1.5.13 长文成品连续改稿稳定性

## 范围与口径

- 产品基线：`v1.5.13` 发布内容；本轮未修改 `SKILL.md` 或写作 references。
- 两名独立 Codex writer 使用同一份多附件材料形成两份成品稿。用户说明长链路可直接从既有成品开始后，第一轮只作为冻结底稿，不把首稿表现并入“连续改稿稳定”结论。
- 第二轮在各自成品上压缩、调整两个一级标题顺序；第三轮继续在同一会话恢复标题顺序，并只把主管部门反馈期限从 7 月 15 日改为 7 月 18 日。
- writer 和 judge 均由 Codex 子上下文执行；精确模型 ID 不可用，本轮只记真实链路 sanity。
- 字数同时记录 Python/.NET 字符总数和 CJK `[一-鿿]` 数量；用户明确写“中文字符”时，以 CJK 数量判定。

## 原始包

原始 prompt、两名 writer 的三轮稿件和本地检查文件保存在 `output/long-revision-stability-20260714/`。关键 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `prompt-long.md` | `0673091EDD2AFC2A38F3ABFD651CFC987D655FC50DEFE164C10E0FA08C524808` |
| `prompt-round2.md` | `57960118485D915099581E646F0E825FC2226E1E2F327054E53E3042A61D4F77` |
| `prompt-round3.md` | `23F6E350C0D8DC01A79556DDDAFBB7E06A8A18288996B60A62682D01D16716C8` |
| `writer-a-round1.md` | `64230B4D9D0546D92E91E2F04224180EA93D54346B50E05E52CB224474C61DE4` |
| `writer-a-round2.md` | `19970278E325F38940575AD55ED486998949A062AC82A7E57699CDA11432EB8E` |
| `writer-a-round3.md` | `5E49AB4816B7C83F3317E65E6BA9F64D7C177F3CB4D24AC4B61A12A6451F88F5` |
| `writer-b-round1.md` | `43ECA72116C0C948ACD9E3496B65266FE99CDC969A8F8042E536302B23F3A474` |
| `writer-b-round2.md` | `F72596213F9DC64590022B1E398CEF583B45FD78D83D0A495558DD2EECCE4AB0` |
| `writer-b-round3.md` | `6B3D40C6DD87C5F83C813C381D1D574BF3E1115E2126EDA828A522C143CC2C61` |

## 独立 judge

| 稿件 | 事实和状态 | 标题与顺序 | CJK 篇幅 |
| --- | --- | --- | --- |
| A1 | PASS | PASS | PASS，3286；目标 3000—3600 |
| A2 | PASS | PASS | FAIL，2268；目标 2400—2800 |
| A3 | PASS | PASS | FAIL，2268；目标 2400—2800 |
| B1 | PASS | PASS | FAIL，2646；目标 3000—3600 |
| B2 | PASS | PASS | FAIL，2011；目标 2400—2800 |
| B3 | PASS | PASS | FAIL，2011；目标 2400—2800 |

两条链路均保留132个事项、486份表单、74个问题及五类分项、58项已复核和16项待确认、三批数量、24项抽检的22/2结果、7个待上级或跨层级核验问题、办理总量和73.4%、38项14.2分钟至11.6分钟、128条反馈的分类和办理状态、7月20日、7月25日、8月5日节点以及统一字段库待专题会议审议状态。数字中的千位分隔符被删除，但数值未改变。

第三轮逐行对比显示，两名 writer 都只移动“存在问题”“下一步安排”两个完整区块，并把7月15日改为7月18日；没有其他事实、数字或状态漂移。正文没有 Markdown 标记。`prose_lint.py --format --structure --delivery-mode draft-body` 只提示低级 `口径` 高频（A 为12次、B为9次），没有 medium/high 命中。

## 研判

- 长文连续改稿的事实保真、状态保真、一级结构调整和第三轮局部修改稳定，未发现功能性回退。
- 精确 CJK 下限执行不稳定：两名 writer 在第二轮和第三轮均低于2400，B 的第一轮也低于3000。这是两名 writer 的共同现象，但只覆盖一个原始任务，未达到“至少2个 prompt”的产品修复门槛。
- 独立 judge 建议增加交付前 CJK 计数提示；本轮不采纳到产品 Prompt。原因是证据仍限于一个任务，且用户已明确任务完成度、事实边界和渐进式路由优先，不能为单一计数问题继续增加入口负担。
- 下一步可直接选用另一份既有长文成品，设置不同压缩比例和文种，补第二个 prompt。只有同类下限失败再次由两名 writer 复现，才评估一句级、非脚本的篇幅自检提示。

## 工程回归

- `python -B -m unittest discover -s tests -v`：152/152 PASS。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.12-for-1.5.13 --baseline-label baseline-1.5.12 --current-root . --out output/post-release-1.5.13-context-gate-retirement`：baseline 104/108，current 108/108。
- `npm run eval:official-writing:smoke`：沙箱内首次因 Promptfoo 无法启动已经失效的 Hermes Python 路径产生20个 provider error，未记为通过；改用本机 Python 3.13 在允许子进程执行的环境中运行同一 `run_eval.py --suite smoke --judge-batch-size 2` 后，20/20 PASS、0 error、skill 10胜、judge consistency 1.0。
- `python -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing`：PASS。
- `git diff --check`：PASS。

本轮只删除测试中的 `<25000` 自设断言，并在维护文档中更正口径；provider 的 `MAX_SKILL_CONTEXT_CHARS=50000` 完整性保护继续保留。`SKILL.md`、写稿 references、路由、输出模式和复核顺序均未修改。
