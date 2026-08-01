# 入口固定余量删除原子真实 A/B 结果

日期：2026-08-01

## 结论

`PASS / MERGEABLE / WAIT FOR FINAL COMBINATION`。

候选只从入口篇幅句删除“并留出 5%-10% 余量”，保留“输出前做字数自检，尽量压到限制内”；`workflow.md`、`review-checklist.md`、文种路由、事实边界、篇幅预算、复核顺序和脚本均未修改。三题首稿中，Candidate 全部满足用户篇幅，固定 main 有一题明显低于下限。匿名盲审解盲后 Candidate 3 胜 0 负，六稿均未发现 P0 保护性外扩或材料外程序承诺。

该结果确认入口固定比例是当前短稿的一个可控贡献因素；它不是唯一原因，也不支持继续加入“达到下限”“扩写”等显著公式。Candidate 可进入当前 main 的最终组合回归，暂不单独合并、推送或发布。

## 固定对象

- 固定 Baseline：`6bd6c6762a6ccf6b42c378a3990c093db43804ab`。
- 预注册：`c5c139db`。
- 产品提交：`2d006905`。
- 工程结果：`a3484c9a`。
- 冻结任务：沿用 `dbfc4ac1` 的 LH01—LH03 原始任务及输入哈希。
- 产品减载：每个运行包减少 13 个字符、23 个 UTF-8 字节。

## 运行条件与证据边界

- Candidate 与 Baseline writer 分别由编排层显式派发为 `gpt-5.6-terra/high`，使用逐字相同任务、固定同序 reference、各自首个技术有效输出；generation=1、revision=0、resample=0。
- writer 回执记录了输入/输出 SHA-256、实际读取顺序和字符数，但未独立回显模型与 thinking；精确模型档位以编排层派发记录为准，不扩大为跨模型结论。
- Candidate 与 Baseline 使用物理隔离 worktree；writer 不读取另一臂、旧稿、候选证据或盲审。
- 独立包装器复算六稿哈希和字符数，匿名目录未出现 Candidate/Baseline 身份词。
- 硬核验只看原任务与匿名稿；匿名 judge 不读取 mapping、receipt、hard verifier、git 或候选说明。

原始产物位于忽略目录：

- `output/length-headroom-delete-only-real-ab-20260801/candidate/`
- `output/length-headroom-delete-only-real-ab-20260801/baseline/`
- `output/length-headroom-delete-only-real-ab-20260801/anonymous/`
- `output/length-headroom-delete-only-real-ab-20260801/hard-verifier.md`
- `output/length-headroom-delete-only-real-ab-20260801/mapping.md`

## 真实 A/B

| 任务 | Candidate / Baseline 去空白字符 | 硬核验 | 匿名映射与结果 | 解盲 |
| --- | ---: | --- | --- | --- |
| LH01 培训通知，≤420 | 322 / 340 | 两稿 PASS，无 P0 | A=Candidate，B=Baseline；A 小胜 | Candidate 小胜 |
| LH02 机房报告，800—900 | 804 / 531 | Candidate WARN（重复）且篇幅合规；Baseline 因篇幅 FAIL；两稿无 P0 | A=Baseline，B=Candidate；B 胜 | Candidate 胜 |
| LH03 总结改稿，1000—1100 | 1038 / 1059 | 两稿均保留事实、结构与状态；hard verifier 均记重复 WARN，无 P0 | A=Candidate，B=Baseline；A 小胜 | Candidate 小胜 |

### LH01

两稿都保留通知全部硬要素。Candidate 起句更直接，Baseline 同句重复“网络安全专题培训”，差距小但与篇幅无关。

### LH02

Baseline 首稿只有 531 字，属于产品输出的篇幅失败，不是宿主、权限或启动噪声，按预注册保留且未补抽。Candidate 为 804 字，事实、数字、未决状态和下半年安排均与材料一致；存在首段和末段解释性复述，需轻量压缩，但没有新增事实、责任、程序或承诺。匿名 judge 判 Candidate 为本题唯一可交付臂。

### LH03

两稿均满足 1000—1100 字、标题与三部分结构要求，并保留全部数字、日期、进展和三项下半年安排。Candidate 的状态复述较少，匿名 judge 判 Candidate 小胜。hard verifier 对两稿都记录了软重复，不构成 Candidate 独有硬回退。

## 因果判断

1. 旧的显式“达到下限”候选同时改变了固定余量和下限显著性，无法分离二者；本轮只删除 13 字符固定比例，三题 Candidate 均合规，且相对当前 main 没有事实或 P0 代价，完成了单变量分离。
2. 入口固定 `5%-10%` 余量可确认为短稿的一个贡献因素。它的删除没有强制扩写，也没有改变硬上限控制：LH01 两臂都安全低于 420。
3. `workflow.md` 中同类余量句仍是实际被 LH02、LH03 读取的弱疑点；本轮两臂保持它不变，因此不能把现有收益归因给 workflow，也不在通过候选上顺手修改。
4. `review-checklist.md` 和 `anti-ai-patterns.md` 未在本轮三题读取，不是这些短稿的直接原因；`information-selection.md` 的正向展开句三题均读取，不列为压短源。
5. 成稿后篇幅门禁此前 0/3 接纳 D1，说明“按短计划段补写”尚不能安全选中遗漏关系；该门禁不解释首稿偏短，本轮不合入。

## 剩余风险

- Candidate LH02 和两臂 LH03 都有不同程度重复，说明篇幅合规仍不等于稳定高质量；本轮没有三场景 Candidate 独有同机制回退，不追加一例一修。
- 当前结论只证明相对固定 main 的单变量净收益，不包含 true No-Skill 或跨模型胜率。
- `workflow.md` 的固定余量与“尽量压到限制内”仍可作为后续独立原子研究；只有新证据显示持续下偏时再启动，不与本候选混合。
