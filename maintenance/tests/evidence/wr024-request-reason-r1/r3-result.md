# WR-024 R3 真实写稿结果

## 执行

- 候选：`690fc8e9b4fc39de2cc0990b3d271fc726854af5`
- 任务：同一 4 题 × 5 家登记低成本 provider，`max`，每格一次，零质量重试
- 技术结果：20/20 有效；候选 Skill 指纹 `dbf79a5af7ebf0dee21fc188ba5db4061d3400fb69d77ff4220a3072cc66db96`
- 四臂汇总：`output/wr024-request-reason-r1/summary.json`，80 条记录，SHA-256 `c4f9549bb529abdf3775da6ba3c90aafbbc7919585e9836b80e00766b60f71f0`

## 人工判读

| 题目 | 结果 | 判定 |
| --- | --- | --- |
| Q1 已确认故障维修 | 5/5 以故障事实或恢复会议室正常使用承载缘由，18000元与待批关系保留 | 通过；直接作用是合理推断 |
| Q2 制度依据与人员聘任 | 5/5 交付含管理规定、工作需要和人员事实的请示正文，未把拟聘任写成已聘任 | 通过；“具备相应条件”等低强度判断不作失败 |
| Q3 常识可支持的采购用途 | 5/5 写出日常文件处理需要；4/5 同时保留未批和供应商未定，Alibaba-2 单稿遗漏两项当前状态 | 达到至少 4/5；遗漏为单稿风险，没有第二家同类回退 |
| Q4 真正缺少延期原因 | 5/5 识别并提示原因缺口，0/5 编造天气、场地、人员等具体原因 | 结构原子通过；Ollama 单稿“因故”和两稿“其他安排不变”登记为既有材料边界风险，另项处理 |

自动关键词观察有 7 份命中，主要来自“未补任期/待遇/涉密”等否定式过程说明，未把这些误判为正文事实。稿件长短、自然原因、直接作用、条件判断和正常论证均不作失败。

## 结论

状态：`R3_SELECTED_ENGINEERING_ALLOWED`。

R3 解决的是 reference 中错误的顺序暗示和请示/申请适用对象不一致：请示按“缘由—事项—要求”组织，紧凑短稿可同句承载；事实与常识能闭合时允许一层自然原因或用途，确实缺失时提示原因，不在正文捏造。R1、R2 的宽泛或负面枚举均不进入产品。后续只同步普通兼容镜像、增加直接语义断言并回填规格；“只提示一项”的稳定性与“其他安排不变”另立后续原子，不冒充本次已解决。

## 工程验证

- 五套普通兼容镜像由 `py -3 maintenance/tools/sync_adapters.py` 同步，第二次运行幂等；canonical 与镜像字节一致。
- `py -3 -m unittest maintenance.tests.test_safe_request_entry_integration maintenance.tests.test_status_ledger_consistency maintenance.tests.test_skill_boundary`：96/96 通过。
- `py -3 -m unittest discover -s maintenance/tests`：746/746 通过。
- `py -3 C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check e05de14a..HEAD`：通过。
