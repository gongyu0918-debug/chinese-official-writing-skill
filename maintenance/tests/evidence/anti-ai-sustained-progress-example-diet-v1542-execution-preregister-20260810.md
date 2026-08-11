# ANTI-AI “持续推进”重复例子微减载真实 A/B 执行预注册

日期：2026-08-10

固定 Baseline：`9968038b0bc68c942eac78cffe7b4968d674f801`

固定 Candidate：`75eb98fa5147a2fff2bc806b12e6955daf42154c`

分支：`codex/anti-ai-sustained-progress-example-diet-v1542`

## 冻结与唯一变量

- detached baseline：`output/research-baselines/anti-ai-sustained-progress-example-diet-v1542-base`；
- detached candidate：`output/research-baselines/anti-ai-sustained-progress-example-diet-v1542-candidate`；
- 两臂逐字读取同一组完整冻结 Skill context：`SKILL.md`、信息选择、通用文种、工作总结、建设方案、ANTI-AI、总审和校对资料；
- 执行器必须确认两个 detached HEAD、两个工作树清洁、且只有 `references/anti-ai-patterns.md` 哈希不同；该文件差异必须恰为删除一行 ``- `持续推进` ``；
- Candidate 不删除 `有力支撑`，不修改本节标题、资格、处理句、其余例子、脚本、路由、版本或加载顺序。

执行器：`tests/evidence/anti-ai-sustained-progress-example-diet-v1542/harness.py`。默认只允许 `--preflight`；真实调用必须显式传入 `--run`。预检不得创建 output、final、匿名包或 mapping。

## 任务与控制

每次调用只输出五项互不相关的正式正文，沿用 D1 的题包和事实判据：

1. `R1`：审改无对象、责任、时限的空泛短语，检验既有通用机制仍能处理无支撑的 `持续推进`、`有力支撑`；
2. `R2`：16 项仍待主管部门确认的事实受限工作总结，防止状态过度收束或新增责任；
3. `R3`：窗口终端、信息屏、预约取号的建设方案，防止功能范围或投运状态扩展；
4. `C1`：材料给出主体、事项、日期、反馈和汇总机制的 `持续推进`，保留持续性语义与具体机制；
5. `C2`：固定 `重点任务包括`、`保障措施包括` 标题、三阶段和三方职责。

每份 manifest 记录 `prose_lint_executed_by_harness=false`。本轮不调用 lint，不得将脚本存在表述为终稿已复核。

## 运行矩阵与匿名

- Alibaba Token Plan `deepseek-v4-flash-0731` `max`：4 个配对；
- Ollama Cloud `deepseek-v4-flash:0731` `max`：4 个配对；
- 每个 provider 固定 ABBA：Baseline→Candidate、Candidate→Baseline、Candidate→Baseline、Baseline→Candidate；
- 共 8 对、16 次调用；每臂只收首个 final，零重试、无补稿；
- 调用完成后才随机匿名，mapping 在裁判结论前不得读取。

每条记录保存 provider、模型、顺序、返回码、时长、prompt/final SHA、标题完整性、final 长度和 harness 脚本执行状态。任一调用失败、空稿或标题不完整记无效；任一 provider 少于 3 个有效配对时不生成匿名包、不进入质量比较。

## 盲审、DIFF 与停止

匿名裁判先检查事实、数字、日期、主体、状态、用户模板和输出范围，再评价空泛表达、直接修改成本和可用性；不得猜测 A/B 身份。`R1` 看既有规则能否删去或落到材料已有事实；`R2/R3` 看是否补造；`C1/C2` 看具体机制、固定词和模板是否被误删、弱化或改序。

单个 Candidate 独有硬事件只能登记，不能归因或作为撤回依据。若出现，才以相同 provider、相同任务、同一冻结 context 做 4 对 ABBA 定向复放：同一机制 Candidate 至少 2 次而 Baseline 为 0，或 Candidate 比 Baseline 多至少 2 次，才判为 DIFF 回退并停止。两臂共有、单次或裁判分歧均记为噪声/未决。

两家各至少 3 个有效配对，且 `R1`、`R2/R3`、`C1/C2` 无经复放确认的 Candidate 独有硬回退，才可记 `REAL NON-INFERIOR MICRO-RELIEF`。该结论只证明删除重复例子在本矩阵不劣；实际 prompt 字符减少是成本收益，不宣称写作质量提升。本提交不运行真实模型、不合入 `main`、不推送、不打 tag 或发布。
