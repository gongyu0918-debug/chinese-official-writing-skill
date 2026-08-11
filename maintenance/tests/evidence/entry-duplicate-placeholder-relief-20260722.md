# 未完成占位重复反例去重验证（2026-07-22）

## 变量

- 固定基线：`3c38576`。
- 单一变量：保留 `SKILL.md` 硬边界中的完整占位清单和日期处理规则；把后文“常见错误反例”中重复的占位长清单缩为一句复核提醒。
- 未改变 reference 路由、信息选择、文种规则、复核顺序、脚本或日期边界。

该原子按统一 LF 口径减少 99 字符，约占基线入口 0.96%。叠加此前已通过的减负后，当前入口相对固定 1.5.21 由 10,631 字符降至 10,181 字符，累计减少 450 字符，约 4.23%。

## 真实 A/B

writer 与 judge 使用独立 subagent。两侧使用逐字一致的自然语言任务和 high reasoning，各取首个技术有效输出；协作接口没有返回可核验模型名称，记为 `unavailable`。

### T01 情况说明占位清理

任务要求删除维护单位、附件和成文日期占位，不使用当前日期补写，同时保留巡检事实。Candidate 与 Baseline 字节和文字完全一致，SHA-256 均为 `0ED36284FECE05C5B3647367D4E47056903491E3DE2D16ED1C3D39714B5B7111`。两稿均删除指定占位、未补日期，完整保留日期、主体、3个库房、12台记录仪及运行状态。

结论：难分，硬边界通过。

### T02 夏季办公楼空调运行时间通知

该题为新建的日常通知，Candidate 与 Baseline 同时首抽，没有复用已知胜出的历史稿。两稿均完整保留执行日期、工作日和公共区域时段、周末申请、26摄氏度、电话、发文单位及成文日期，没有新增节假日、审批层级、处罚或设备参数。

匿名映射为 A=Baseline、B=Candidate。独立盲审判 B 胜：Baseline 为接近篇幅加入三处重复提醒，Candidate 在不丢实质事项的前提下结构更紧、直接修改成本更低。Candidate 把咨询电话归入保障科，属于材料关系内的轻微归纳，不构成硬回退。

- Candidate SHA-256：`AE35AA10F215DC5DA2AC9BE3FDE3D40712C9012786B595F8E1D9CC77165EEC8F`
- Baseline SHA-256：`FA1D753882A6E0E2BA03EB1E4A79A0903F70D778980CC9EB9EF7183CA2B2A350`

## 工程验证

- `python -m unittest discover -s tests`：354/354 通过。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，0 failed，0 errors。
- 固定 `3c38576` 与 current 的确定性消融：两侧均为 108/108。
- `quick_validate.py chinese-official-writing`：通过。
- `tools/sync_adapters.py`：canonical 已同步到发行镜像。
- `git diff --check`：通过，仅有既有 LF/CRLF 转换提示。

## 判定

本原子为 PASS，可以保留。它删除的是同一入口文件内的重复反例，不改变规则来源和渐进式路由；真实专项稿持平，新的日常通知 Candidate 胜，未发现事实、状态、文种、格式、输出模式或保护性外扩回退。
