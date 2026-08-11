# Candidate Direct Fact State 结果

日期：2026-07-29

## 结论

结果为 **MIXED / NO MERGE**。

产品侧只增加一句纯 Prompt：

> 已选入正文的事项，直接陈述该事项已给的业务事实和当前状态。

两题匿名结果均为 Candidate 小胜，且没有 Candidate 独有的事实、数字、日期、主体、状态、文种、格式、篇幅或输出模式硬回退。C01 中，Candidate 压掉了固定 1.5.28 基线的“材料所述”“不作其他结论”等高风险表达，同时完整保留“正在核查、继续监测、核查完成后通报结果”；S15 中，Candidate 的算术自证和解释性尾句较少。

但运行审计不能确认四臂实际模型和 thinking，Candidate 两臂缺少可独立复验的首个技术有效输出回执，同题两臂实际读取的 reference 集合也不一致。因此，这轮只能证明该原子具有较强正向信号，不能作为严格单变量因果 A/B，也不能直接合并。

## 固定对象

- 固定基线：`v1.5.28=f7570d4df5064582946732d283d30e86063ef142`
- 预注册提交：`da470508dc9bf27703d5f9ccd5825cdf6f82c234`
- 产品提交：`a3134679be2198ea59290cf87292e0cfd0b8140c`
- 产品范围：canonical `information-selection.md` 一句及五个发行镜像
- 两套测试包：各 29 个文件；除 `references/information-selection.md` 外逐文件字节一致

## 工程验证

| 验证 | 结果 |
| --- | --- |
| `python -m unittest discover -s tests` | PASS，390/390 |
| `npm run eval:official-writing:smoke` | 沙箱内 Node 启动 Hermes/system Python 失败；按既有环境噪声口径改用显式系统 Python 复跑 |
| `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2` | PASS，20/20；Skill 10 胜；judge consistency 1.0 |
| `python tools/run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\release-worktrees\release-1.5.28 --baseline-label v1.5.28 --current-root . --out output\candidate-direct-fact-state-v1528-ablation` | PASS，baseline 110/110，current 110/110 |
| `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing` | PASS，`Skill is valid!` |
| canonical 与发行镜像 SHA-256 | PASS，六份 `information-selection.md` 一致 |
| `git diff --check` | PASS |

## 真实写稿与匿名结果

两题均使用自然语言原始任务；Candidate 与基线任务文件 SHA-256 一致；各臂记录为一次生成、无补抽和无二次修订。匿名副本与原稿字节一致。

### S15：1200 字左右季度工作总结

- 匿名映射：A = 固定 1.5.28；B = Candidate。
- 硬核验：A、B 均为 WARN，事实、数字、状态、四段结构和篇幅均通过。
- A 的主要修改点为 4 句：数字自证、材料外程序、跨项关系和安排自证。
- B 的主要修改点为 3 句：统计口径自证、跨项关系和安排自证。
- 独立盲审：B 小胜。B 的算术自证和解释性尾句较少，直接修改成本更低。
- `prose_lint.py`：两稿均无中高风险；Candidate 的“口径”出现 9 次，基线 6 次，记为语言负项。

### C01：500—700 字供餐异常情况通报

- 匿名映射：A = Candidate；B = 固定 1.5.28。
- Candidate 保留全部时间、73 笔、未重复扣款、日志备份、正常运行和三项后续状态。
- 硬核验：A 为 WARN；B 为 FAIL。B 独有“材料所述”来源泄露和“不作其他结论”无锚定保护性否定。
- 独立盲审：A 小胜。A 仍有重复自证和扩大否定，但直接使用成本低于 B。
- 两稿均处于用户要求的 500—700 字范围。

## 运行证据限制

只读运行审计见 `tests/evidence/candidate-direct-fact-state-v1528-run-audit-20260729.md`。

1. 四臂请求条件均记录为 `gpt-5.6-terra/high`，实际模型和 thinking 均为 `unavailable`。
2. Candidate 两臂记录 `single_call=true`，但缺少 `first_output_status` 和原始调用回执；首个技术有效输出不能独立复验。
3. S15 的实际读取数为 Candidate 10、基线 7；C01 为 Candidate 10、基线 3。已记录读取均位于各自物理隔离包，但生成上下文并非逐项对称。
4. 基线两臂记录运行期间五个预存 tracked 修改并发消失；当前工作树 clean，历史并发影响无法完全追溯。

所以，匿名稿的 2/2 正向只能记为探索性质量证据，不写成严格因果通过。

## 剩余风险与下一步

- Candidate 没有消除 P0：S15 仍有统计口径自证和跨项关系，C01 仍有事实重复、自证句及一处扩大否定。
- 单句原子可能增加“口径”等词的复用；本轮已经观察到一次，不作一例一修。
- 下一轮不修改产品 Prompt。先固定两臂完全相同的 reference manifest，并保存实际模型、thinking、首个技术有效输出和完整读取回执，做一轮受控组件 A/B；自然路由能力另行验证，不把两种证据混为一谈。
- 受控 A/B 若继续正向且无硬回退，再扩大到报告、通报、请示等日常任务；否则冻结该原子。
