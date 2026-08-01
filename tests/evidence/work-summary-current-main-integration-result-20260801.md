# 工作总结逐字拆叶与当前 main 组合验证结果

日期：2026-08-01

## 结论

**PASS，可进入后续 main 组合合并；本 worktree 未自行合并、未发布。**

固定 Baseline 为 `6bd6c6762a6ccf6b42c378a3990c093db43804ab`，预注册提交为 `65dc9045`，产品提交为 `755177b6`。产品只把工作总结、工作要点、周报、月报的既有规则逐字迁到直达叶，并同步 provider、确定性测试和五份发行镜像；没有修改叶内写作语义、事实边界、复核链、输出模式或版本号。

当前 main 已把核心路由收成“参考资料表”单一来源，因此组合时没有恢复旧候选的超长路由段，只在表中增加工作类直达叶。该处理保留当前 main 的入口减负，不改变旧候选已经验证的实际加载集合。

## 证据继承核验

- 当前新叶与旧候选 `e7c0fd21` 的 Git blob 均为 `d952abb4dcf38b9b03295077d3a488c41dc2dcea`，正文逐字一致。
- 当前与旧候选的纯工作类加载集合均为 `SKILL.md + references/genre-playbook-work-summary.md`。
- 当前与旧候选的“工作总结 + 通知”混合加载集合均为 `SKILL.md + references/genre-playbook-work-summary.md + references/genre-playbooks.md`。
- canonical 与五份镜像的新叶 SHA-256 均为 `3D903A19619A23EA55E6D69DAF06AEE04693205C5AC74C205DA163B281E0AEBC`；通用 playbook SHA-256 均为 `9EB6F5B7E90194688F6823483FB9D21523CA1CD3F5DEFFB4E5A689018BB58B05`。各平台 `SKILL.md` frontmatter 按宿主适配不同，去除 frontmatter 后正文 SHA-256 均为 `eb59e92fcca5a1766b5d78e1359e6b398cce4845e6552b3a425e6f7c290b4b16`。

以上条件满足预注册的真实证据继承门槛。本轮没有重新生成稿件，复用 WSV01、WSN02、WSN03 三对首稿及 `b524511d` 的独立因果复核：旧 1 胜 2 负没有 Candidate 独有硬回退，宽口径外围补写在两臂均为 3/3，单题措辞胜负无法归因于逐字迁移和专叶路由。该证据只能证明没有可归因质量回退，不能宣称物理拆分稳定提升写作语言。

## 减载

按 UTF-8/LF 文本和实际纯工作类加载集合计量：

| 指标 | 固定 main | Candidate | 减少 | 比例 |
| --- | ---: | ---: | ---: | ---: |
| 字符 | 14145 | 10959 | 3186 | 22.52% |
| 字节 | 33642 | 25700 | 7942 | 23.61% |

## 实际验证

| 验证 | 结果 |
| --- | --- |
| 工作类直达、混合文种双叶、逐字迁移等 4 项聚焦单测 | 4/4 PASS |
| `python -m unittest discover -s tests` | 407/407 PASS |
| `npm run eval:official-writing:smoke` | 20/20 PASS |
| 固定 main / current 确定性消融 | Baseline 109/110；current 110/110。Baseline 仅在新增 P075 新叶路径用例失败，属于旧版本不存在新文件的预期新增断言 |
| `quick_validate.py chinese-official-writing` | PASS，`Skill is valid!` |
| canonical / 五镜像正文与 reference 哈希 | PASS |
| `git diff --check` | PASS，仅有 Windows LF/CRLF 提示，无空白错误 |

第一次全量 unittest 曾出现 1 项失败：移植测试指针时误把 P074 复函用例改到工作总结叶，而 P075 周报仍指向通用 playbook。该问题只存在于尚未提交的测试改动，不是产品行为；按原始用例语义将 P074 恢复通用叶、P075 指向工作总结叶后，当前侧 110 项及全量 407 项全部通过。没有补抽、改写任务或变更产品规则。

## 剩余风险

1. 该候选提供的是确定性上下文减载，不直接修复工作总结偶发的外围补写、保护性自证或篇幅不足；这些旧稿风险在 Baseline 与 Candidate 两臂均出现，继续作为共享写作风险记录。
2. 旧真实 A/B 的比较差异较小，且存在单次采样噪声；本结果不把“1 胜 2 负”改写成质量领先，只排除了它与本物理拆分之间的可验证因果关系。
3. 若后续组合又修改工作总结叶正文、工作类加载集合或复核链，本轮真实证据继承失效，必须重新做与变量相称的写作验证。
