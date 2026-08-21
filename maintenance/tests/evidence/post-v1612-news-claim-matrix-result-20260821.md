# 新闻声明级核验原子结果

日期：2026-08-21。固定基线为本地 `main@a7266a472629adcd8f215ce88f4982b8e40b4fcd`。本候选未合并 main、未推送、未发布，也未运行第三方脚本。

## 真实 A/B

宿主为 WorkBuddy 5.3.13 内置 CodeBuddy CLI（命令路径：`E:\Program Files\WorkBuddy\resources\app.asar.unpacked\cli\bin\codebuddy`），模型 `deepseek-v4-flash`，`max`，`bypassPermissions`，无会话持久化；同一 prompt、同一 cwd、基线与候选各运行一次。题目含三条互相冲突来源，要求输出“主张—来源—来源身份/层级—冲突—结论状态”矩阵和正文。

固定 prompt：`maintenance/tests/evidence/post-v1612-news-claim-matrix-prompt.txt`；prompt SHA-256：`B830C358B21F3D27C60F71E44D8EBF2C26F8AF6B0F9F416A09E6BBDC2A6BBBC0`。

### R1：原候选

| 项目 | 基线 | 候选 |
| --- | --- | --- |
| session | `news-claim-base-20260821` | `news-claim-candidate-20260821` |
| exit code | 0 | 0 |
| num_turns | 11 | 13 |
| input/output tokens | 95,731 / 6,658 | 96,315 / 8,834 |
| combined JSON SHA-256 | `4467557F6353678D358AAD077FE19BD03036A152ED638156ACF12738036B7D11` | `52FAB192EDE44D7B9A68D3CCC20DB9493342E725DC458841FC1CA3C49EB5EFD9` |
| result SHA-256 | `A29D58E7F2164825FA01A2839C5C628BE69262F5C7506EB44EBECA682DE11EB5` | `EF8EFF103C3042E0150981DCD0C1DBBBB137D966CD52EC1260EB833881A30363` |

候选相对基线的可归因改善：基线标题和矩阵将来源甲的980家作为“可采信/唯一可追溯”口径；候选按来源归属分别陈述，并将整体1200家判为“存在冲突，待确认”，更符合三来源冲突时不替用户选边的目标。

R1 候选仍有硬风险：矩阵写出“相差约220家”，但来源乙是“超过1200家”，不能据此得到“约”或确定差额。该风险不是基线同样输出的内容。

### R2：只修开放数量边界的候选复跑

固定同一 prompt，不重抽固定基线；候选窄叶新增“不同截止日、统计范围或接入/覆盖口径不能相减、相加或折算；‘超过’‘至少’等开放数量不自行写成‘约’‘相差’或确定差额”。

候选 session `news-claim-candidate-r3-20260821`，exit code 0，14 turns，input/output tokens `96,809 / 7,229`；combined JSON SHA-256：`599C072BDC9B107B1DC13C1642EC24B162EB725A98A2234CC575F7C00A11C7FD`；result SHA-256：`CD2475A6AD96D90BA564276F6EA3D8A01B87AE51B6B619B6A7E324D2B947DD7A`。

R2 已消除“相差约220家”，但出现候选独有的直接可用性回退：

- 将材料只称“某市大数据中心”升级成“市级事业单位”；材料未给机构性质。
- 将本地日报这一已知来源写成“来源身份待核”；实际待核的是其数据原始出处，日报身份本身已给定。
- 在正式正文前后输出 Markdown 水平线 `---`，并把正文标题写成 `**…**`；同时增加开场旁白，破坏用户要的直接可用正文边界。

因此 R2 不能用 R1 的冲突处置改善覆盖。最终结论：`HOLD`，不合入产品，不保留 `agent_writer.py` 路由胶水；只保留本结果、预注册和固定 prompt 证据。候选原始 JSON、终稿和日志保存在被忽略的 `output/current-verification/news-claim-matrix-20260821-r2`、`...-r3` 目录。

## 确定性验证

- `python -B -m unittest maintenance.tests.test_promptfoo_eval.PromptfooProviderTests maintenance.tests.test_skill_boundary`：152/152，通过（候选尚在工作树时）。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过。

这些工程门只证明窄路由和镜像在候选工作树中可运行，不能推翻真实写稿的 HOLD。候选产品与路由胶水在本分支最终提交前撤回，main 保持不变。
