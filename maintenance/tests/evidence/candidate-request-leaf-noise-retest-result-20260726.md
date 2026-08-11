# 请示/申请叶子 MIXED 噪声复验结果

## 结论

结果仍为 `MIXED`。不合并稳定 `main`，不修改 Candidate Prompt，不新增系词、空格或格式案例规则，不改版本号、不发布。

- Candidate 产品：`123d0d13a3879075b82457d7e012b314b8623413`
- Candidate 证据 HEAD：`be1aea2562be730b00b507c4ff925762d595acc7`
- 稳定基线：`faba4c1f410b3007d60671b3d2ead6d78a2ea8a4`
- 编排条件：`gpt-5.6-terra/high`
- 实际有效比较：Q01、Q02；Q03 因 reference 读取不对称只作探索性证据

上一轮 F13 中“服务期为 6 个月”和“服务期 6 个月”的轻微差异未在新样本复现。历史同题不同 Writer 也曾分别出现双方都有“为”和双方都没有“为”，因此该负项可校准为高概率采样波动，不能作为叶拆分的因果缺陷。

但新 Q01 中 Candidate 把原稿数字与日期周围的空格一并删除，Baseline 只修改用户点名的日期、人数和地点。该差异不改变事实，却超出“其他内容保持原样”的局部修改范围，独立盲审判 Baseline 小胜。它与 F13 的系词差异不是同一机制，单次出现不足以触发 Prompt 修复；同时也意味着本轮不能宣称 Candidate 全面不弱于稳定 `main`。

## 有效 A/B

Q01、Q02 使用逐字一致输入、同一模型和 thinking、首个技术有效输出、不补抽。Candidate 读取入口、信息选择、原子请示叶、总审和校对；Baseline 读取入口、信息选择、通用文种 playbook、总审和校对。Writer 与匿名 Judge 独立。

| 任务 | 匿名结果 | 揭盲 | 结论 |
| --- | --- | --- | --- |
| Q01 既有培训请示局部修改 | B 胜 | A=Candidate，B=Baseline | Candidate 事实 PASS，但改动了未点名的数字空格格式，记 WARN；Baseline PASS |
| Q02 增配自助借还设备请示 | A 胜 | A=Candidate，B=Baseline | Candidate 明确写出“同意增配 3 台并安排经费”；Baseline 仅用笼统请批语，未完整落实指定请批事项 |

有效结果为 Candidate 1 胜、Baseline 1 胜、0 平。两稿均未出现事实、数字、状态、文种或 P0 硬失败。

## Q03 效力

Q01、Q02 一胜一负后按预注册启用字段式培训费用申请。两侧输出 SHA-256 均为：

`34c25662a863ea8187b6fecad1b97d9a26cfd86db04a86d87e5cbf210824e585`

文本逐字一致，九个字段、字段顺序和禁止新增项均通过。但 Candidate provenance 额外记录读取了根仓库 `.agents/skills/chinese-official-writing/SKILL.md`，Baseline 没有该读取，实际 reference 条件不对称。Q03 因此只能记为技术有效的探索性 tie，不计入优劣分母，也不重跑、不补抽。

## 减载与因果判断

请示路径的文种 playbook 仍从 3928 字符降为 551 字符，减少 3377 字符、85.97%；规则为原样迁移，未加入句法或系词指令。工程验证在产品提交时已通过 370/370 unittest、20/20 Promptfoo smoke、固定基线与 Candidate 108/108 确定性消融、quick validate、镜像同步和 `git diff --check`。

现有证据支持：

1. F13 的“为”字负项不是稳定回退。
2. 原子请示叶在 Q02 对明确请批事项有正向信号。
3. Q01 的空格改动属于新的单样本局部修改范围漂移，尚未达到共性阈值。
4. 由于有效样本仍一胜一负，Candidate 只证明“有价值但未稳定胜出”，不能作为优于 `main` 的可合并更新。

原始稿与 provenance 位于：

`output/candidate-request-leaf-noise-retest-20260726/`

## 停止依据

预注册要求出现 Candidate 独有负项时维持 `MIXED`，且 Q03 后停止扩样。本轮不以单篇空格问题追加规则，也不借无效 Q03 稀释负项。若未来重启，应直接复验“局部修改只改点名字段”这一共性边界；只有在三个正常场景复现后，才研究最小修复。
