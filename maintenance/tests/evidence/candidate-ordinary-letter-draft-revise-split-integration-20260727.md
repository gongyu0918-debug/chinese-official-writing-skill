# 普通函起草与实质改稿分流集成记录（2026-07-27）

## 结论

普通函分流通过隔离集成验证，可以合并到最新 `main`。

- 普通函起草、错字/标点/格式及明确局部措辞修改读取减载专用叶；
- 既有普通函涉及事务动作、状态、条件、范围或结构的实质改稿读取完整 `genre-playbooks.md`；
- 复函、征求意见函和其他文种沿用原路由。

R4 的六题历史结果为 5 胜 1 负。唯一负项完整保留；同题复放中两稿均通过并判持平，未达到共性风险门，因此没有加入场地、培训等样例专用规则。R5 针对复杂改稿的机制性问题改为读取完整 playbook，三题结果为 1 胜 2 平；本次又在最新 `main` 上完成工程回归、最小真实写稿和独立复核。

## 基线与提交

- 最新 `main` 基线：`c8be458c4eb7a3154bcb021858323ef4711015d5`
- 固定 v1.5.26 产品：`50afb5ffd9be88327ad1b4dd25d87c1377d39de9`
- R5 产品：`21632e049f017c5c98e2c6c015fbfbae6498b42d`
- 集成产品末提交：`d4f44e5`

R5 的四个产品提交以原提交顺序应用到基于最新 `main` 的隔离 worktree。集成后的产品文件与 R5 产品树逐字一致；研究预注册、旧原稿和失败候选没有混入产品提交。

## 独立 diff review 与最小修复

首次集成 review 确认产品范围正确，同时复现两类常见路由缺口：

1. “仅调整/更正/替换明确局部对象，其余不变”可能误走完整 playbook；
2. “重新组织/梳理/整体优化既有函的段落、逻辑、层次或顺序”可能误走减载叶。

修复只调整评测 provider 的通用路由识别，并补自然措辞测试：

- 局部修改同时要求局部动作、明确局部对象和范围限定；
- 结构性改稿同时要求既有函、结构动作和结构对象共现。

未修改 Skill 正文、普通函写法、P0/信息选择、ANTI-AI、输出模式、复核顺序、Hook、FSM、版本或发布链。完整 C070“运行优化”起草场景仍走减载专用叶，未被“优化”词面误伤。独立复核结论为 PASS，无新上帝函数。

## 工程验证

| 验证 | 结果 |
| --- | --- |
| 独立路由/diff review | PASS；相关 123 项测试通过 |
| 全量 unittest | 381/381 通过 |
| Promptfoo smoke | 20/20 通过；Skill 10 胜、baseline 0 胜、invalid 0，judge consistency 1.0 |
| 确定性消融 | current 110/110；最新 `main` 108/110，基线只在新增 P110/P111 失败 |
| quick_validate | `Skill is valid!` |
| `git diff --check` | 通过 |
| adapter 同步与镜像检查 | 六份普通函叶一致；同步后无内容差异 |

Promptfoo 在 Windows 沙箱内首次运行时，Node 无法启动已存在的 Hermes Python，20 项均报环境错误；相同命令在获批的沙箱外复跑后 20/20 通过。首次结果只记为运行环境噪声，不计产品失败，也没有用新增题补抽。

## 最小真实回归

两题均由独立 writer 读取隔离集成 Skill 后生成首个技术有效输出，无补抽、无二次修订；独立 verifier 只按原任务和成稿复核。

| 任务 | 路由 | 结果 | 关键检查 |
| --- | --- | --- | --- |
| F04 普通函起草 | 减载专用叶 | PASS | “场地使用时间为当日 8:30 至 17:30”事实角色保留，无外围外扩 |
| F06 既有函实质改稿 | 完整 playbook | PASS | “协助调整末班车时间”与“是否具备调整条件”分别保留，无动作弱化 |

任务 SHA-256：

- F04：`4bf4a644bc2f47731a315e2a816406020b8daeba163cfbdf10435e6d78bef85b`
- F06：`192903d053d2ff678f55cb2703454062c76dbb04044eec64b853811d5e65f3a4`

输出 SHA-256：

- F04：`e961c04beeb622442b7e655c25db920ab0251be8bca1a0c0081f4564288187bd`
- F06：`3cdb5ad1b2ce58fc1477e9043283b2056d88b1ea7d10f8fb74e72f5b47a102df`
- provenance：`9c16eace607f3aa7b407fc86a82afb5a4260f862c979470dfca66dace0061d42`

## 剩余风险

- 实际模型和 reasoning 无宿主回执，记录为 `unavailable`；本轮不能声称严格同模型、同 thinking 复现。
- 真实宿主的 reference 选择仍由 Agent 执行，评测 provider 只能提供可观测路由和回归保障。
- 复杂改稿读取完整 playbook，加载量高于普通起草，这是保留事务动作、条件和结构的预期成本。
- F04 的单次事实角色偏移没有稳定复现，继续作为低频观察项；达到普通场景共性门前不增加专用规则。

## 本地原始证据

- `output/ordinary-letter-integration-real-smoke/F04-output.txt`
- `output/ordinary-letter-integration-real-smoke/F06-output.txt`
- `output/ordinary-letter-integration-real-smoke/provenance.json`
- `output/ordinary-letter-integration-ablation-after-route-fix/summary.md`
- `output/promptfoo/official-writing-smoke-results.json`
