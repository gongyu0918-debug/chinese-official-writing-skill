# 轻量校对叶维护前缀去除预注册（2026-07-23）

## 基线与单变量

- 固定基线：`bc1477c49e9b3cf9ec1ababade9bc4d445f778fe`。
- 只修改 `references/proofreading-checklist.md` 第 11 行：删除维护者口径“`不改变 prose_lint.py 为深度语法纠错器；`”，保留运行时能力边界“`脚本仍只提示语言、格式和重复风险。`”。
- 不修改第 10 行的模型/API/联网边界，不修改校对范围、引用保真、稿内一致性、真实性边界、脚本、路由、输出模式或复核顺序。
- 同步 canonical 与五份发行镜像；测试断言如精确固定被删除维护前缀，只删除该精确锚点，不放宽对脚本只提示、不自动改写和校对能力的断言。

## 三组真实 A/B

Baseline 与 Candidate 使用同一模型、同一 thinking 和逐字一致的原始任务，各取首个技术有效输出，不补抽。两臂读取物理隔离的 Skill 路径，writer 与匿名 verifier 分离。

### T01 普通校对

> 请把下面记录校对成《设备巡检情况说明》，380—500字，只输出改后正文，不新增事实。记录：2026年7月18日，明川市政务服务中心逐台检察12台自助终端,其中11台运行正常,1台离线；7月19日完成远程重连，离线终端恢复。7月20日复查12台终端，均可正常使用。后续每周检查1次，持续至8月31日。发文单位为明川市政务服务中心，成文日期为2026年7月23日。

### T02 引用保真

> 请把下面材料顺成一份简短工作报告，420—560字，只输出改后正文。可以调整引号外的口语、标点和句序，引号内原话必须逐字保留，不新增事实。材料：2026年7月21日，项目组检查8个数据接口，7个正常，1个响应较慢。技术人员当日调整连接参数，7月22日复测8个接口均正常。负责人在复盘会上说：“先把这次记录整理清楚，再安排下一轮测试。”下一轮测试时间为7月29日。发文单位为明川市数据管理处，成文日期为2026年7月23日。

### T03 稿内一致性

> 请校对下面这份项目进展材料，450—600字，只输出改后正文。两处金额来自不同版本，按原位置和原口径保留，不自行统一，也不新增解释。材料：项目于2026年7月1日启动，计划采购14台终端。进度部分记载预算控制数为28.6万元；附件汇总部分记载采购测算总额为29.6万元。7月15日完成需求登记，7月20日完成现场测量，现正整理技术需求。下一步于7月28日前完成内部核对。发文单位为明川市信息中心，成文日期为2026年7月23日。

## 验收门

- 硬检查：事实、数字、日期、主体、状态、文种、篇幅、只输出正文不得回退；T01 应清理明显错字和半角标点；T02 引语逐字一致；T03 同时保留 28.6 万元与 29.6 万元，不擅自统一或新增原因。
- 软比较：结构、语句、机械复述、保护性外扩和直接修改成本至少与 Baseline 持平。
- 三题均须 Candidate 不劣；任一题出现 Candidate 独有硬回退或更高直接修改成本即撤回。通过只证明该维护前缀可以移出运行时叶子。

## 工程验证

- 全量 `unittest`；
- 固定基线与 Candidate 的确定性消融；
- Promptfoo smoke；
- `quick_validate`；
- canonical 与五份发行镜像一致性；
- `git diff --check`。

## 实际结果

结论：`FAIL`，候选修改已完整撤回，只保留本证据记录。`proofreading-checklist.md`、五份发行镜像和对应测试断言均恢复至固定基线 `bc1477c` 的原文。该候选不进入后续版本。

### 工程门

- 首次全量 unittest 为 354/355：唯一失败是测试精确固定了被删的维护者前缀。将该断言改为核验仍保留的运行边界“脚本仍只提示语言、格式和重复风险”后，`python -m unittest discover -s tests` 为 355/355。
- `python tools/run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\research-worktrees\baseline-proofreading-bc1477c --baseline-label bc1477c --current-root . --out output/proofreading-maintenance-prefix-20260723/deterministic`：Baseline 108/108，Candidate 108/108。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- Promptfoo 首次在沙箱内运行出现 20 个环境错误：Node 无法启动 Hermes Python；改用系统 Python 后在沙箱内仍因同一子进程权限失败。随后在沙箱外以同一 suite、同一数据运行 `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`，结果为 20/20、0 failed、0 errors、judge consistency 1.0。前两次环境失败不记为产品失败，也不改写成通过。
- 六份 `proofreading-checklist.md` 的 Candidate 阶段 SHA-256 一致，为 `D96B414E1DE490BE7871FDEC25EA92CC83CE3FF2B01556C0B0711E7FF3B25BF4`；`git diff --check` 通过。

### 三题真实 A/B 与盲审

六名独立 writer 均使用 `gpt-5.6-sol`、`thinking=high`，逐字一致原始任务，各自只提交首个技术有效输出，无重试。匿名 judge 未读取映射，先做硬检查再比较直接修改成本。

| 题目 | 匿名映射 | 盲审结果 | Candidate 独有回退 | 结论 |
| --- | --- | --- | --- | --- |
| T01 普通校对 | A=Candidate，B=Baseline | A 胜 | 无 | Candidate 重复较少，胜 |
| T02 引用保真 | A=Baseline，B=Candidate | A 胜 | 有。Candidate 用“按照这一安排”“相关时间安排与负责人在复盘会上的要求一致”把另行给出的 7 月 29 日绑定为负责人要求，材料没有给出这一归因 | Candidate 直接修改成本更高，负 |
| T03 稿内一致性 | A=Candidate，B=Baseline | B 胜 | 无硬回退；Candidate 的“仍按”“继续做好”“按期转入”增加软性确认和过程色彩，且复述更多 | Candidate 直接修改成本更高，负 |

结果为 Candidate 1 胜 2 负，并有一题独有事实关系外扩。根据预注册门，候选失败，不补抽、不换题、不修改提示词挽救。

### 原始稿哈希

| 样本 | SHA-256 |
| --- | --- |
| T01 Baseline | `25F072E915F03987CAECFFA4B13C842413A469B779282E119C83FB63D85C7600` |
| T01 Candidate | `582C07E0C3597B179B4D2BB9B86CF21593B54639E4F3933AB9BB1259CED86755` |
| T02 Baseline | `E4EA73740BE2A27BFF58BB60C464FACB7137E9B00CB90F6FFDEA16ED21F5A55C` |
| T02 Candidate | `C526DBF9B063A0B284272E99792DCA1555635F59B83DF3309D08FA74B9152DDD` |
| T03 Baseline | `56B4E08B1469D0DE46D0FE7E4EA1E23389CB138B4AC1BED5EC639A7576F6151A` |
| T03 Candidate | `D001C95E84DC624FED499FC90DFFFF900808AB5787635915DC3EC6DBBC1C9870` |

原始稿、writer 回执、匿名 packet、映射和盲审保存在被忽略的 `output/proofreading-maintenance-prefix-20260723/real-ab/`。两臂自主选择的 reference 数量不完全相同：这组结果足以判定 Candidate 未达到“不劣”门槛，但不能把每处语言差异机械归因于删除的 30 个字符。

## 对外部高熵标记的处置

外部审计把这段维护前缀列为优先减负点；本轮已按原子变量复现。静态上它确属维护口径，但真实 A/B 没有证明删除后稳定不劣，反而出现 1 胜 2 负和一次 Candidate 独有归因外扩，因此拒绝将该建议直接落入产品。该结论不外推到外部审计的其他点位，其他点位仍须分别复现。
