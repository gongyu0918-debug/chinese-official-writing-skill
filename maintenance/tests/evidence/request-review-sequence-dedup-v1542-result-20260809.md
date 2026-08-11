# 请示细查顺序重复去除结果（2026-08-09）

## 结论

`BEHAVIOR-EQUIVALENT / ELIGIBLE FOR COMBINATION`。Candidate 删除请示小节第二次完整复述的参考顺序，保留一文一事、请批事项、依据/现状/必要性/经费/安排和请批语的近场规则。两家 provider、两道真实只审不改任务均保持核心召回和输出模式；SOL 四组均判 `direct_regression=NO`，结论为“可作为等义维护候选”。

本结果只支持同文件重复去除，不宣称审稿质量提升。

## 产品与工程

- 固定基线：`a66228cebf4282d4acb6b153816a06ddf3b964bb`。
- 预注册：`8a0d02f8`。
- 产品原子：`9edf7aea`。
- canonical 与五个镜像各删除同一句；新增 focused guard，确保其余请示要素仍在。
- focused 与镜像测试 3/3 PASS，`git diff --check` PASS。

## 真实任务

### Q1 完整请示

| Provider | Baseline | Candidate |
| --- | --- | --- |
| Alibaba DeepSeek V4 Flash 0731 high | `019fe231-ebad-7873-a19c-d5d9bb57bd5f` | `019fe231-ebdb-73b0-8158-aaeba76baae2` |
| Ollama DeepSeek V4 Flash 0731 high | `019fe231-eb97-7581-b716-bf5373d4fe63` | `019fe232-054b-78f1-8b88-76d9f76e6665` |

四稿都识别请示文种、一文一事、请批事项、事实依据、经费来源、实施期限和请批语，保持只审不改。不同稿件对“请批事项是否还需再明确”“检测依据是否充分”的严格程度不同，但没有核心召回缺失。

### Q2 缺项请示

| Provider | Baseline | Candidate |
| --- | --- | --- |
| Alibaba DeepSeek | `019fe231-ebb8-7dd0-aa12-540cb1f873e8` | `019fe232-081d-7993-98c1-2f53e6415a27` |
| Ollama DeepSeek | `019fe231-ebca-7393-9962-a14e304e5aea` | `019fe232-075d-77f2-9061-8128aa3d530a` |

四稿都命中缺主送、请批事项不够明确、“请审阅”不属于请批语、依据/必要性、经费来源和实施安排缺口，没有重写全文。

## SOL 匿名裁决

- 任务：`019fe235-a037-7fe3-9f08-172bc97dc2c5`，`gpt-5.6-sol` max，projectless。
- 四组均保持只审不改和核心要素召回。
- Q1-DSA、Q1-DSO、Q2-DSA、Q2-DSO 的 `direct_regression` 全为 `NO`。
- 裁判观察到部分单稿把已有请批事项、检测依据判得过严，或对“请审阅”给出模板例外，但这些差异没有稳定随 Candidate 出现，也不是删除重复顺序的直接语义后果。
- 最终裁决：`可作为等义维护候选`。

## 边界

该原子进入当前 `main` 前仍需在精简 AGENTS 的组合基线上重跑 full、smoke、固定消融、quick validate 和镜像检查。任何组合期确定性召回下降都撤回；语言偏好不作为本原子的质量收益。

未推送、未发布。
