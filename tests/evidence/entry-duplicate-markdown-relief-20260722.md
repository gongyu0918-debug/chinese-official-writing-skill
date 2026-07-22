# Markdown 重复反例去重验证（2026-07-22）

## 变量

- 固定基线：`a65c0d9`。
- 单一变量：保留 `SKILL.md` 前文关于正式正文不用 Markdown 加粗、井号标题、代码块和横线的完整硬边界；把“常见错误反例”中重复列举格式符号的长句缩为普通文本提醒。
- 未改变 reference 路由、用户格式优先、文种规则、复核顺序或脚本。

该原子按统一 LF 口径减少 29 字符，约占基线入口 0.28%。叠加此前已通过的减负后，当前入口相对固定 1.5.21 由 10,631 字符降至 10,152 字符，累计减少 479 字符，约 4.51%。

## 真实 A/B

writer 与 judge 使用独立 subagent。两侧使用逐字一致的自然语言任务和 high reasoning，各取首个技术有效输出；协作接口没有返回可核验模型名称，记为 `unavailable`。

### T01 Markdown 实施方案清理

Candidate 与 Baseline 字节和文字完全一致，SHA-256 均为 `A008535CF96BD33C37C2E3E20EB17E3922F6D12E423890966E60A93850B37B90`。两稿均删除代码块、加粗、井号标题和横线，完整保留标题、三级层级、事实和原顺序。

结论：持平，无硬回退。

### T02 更新会议室投影设备请示

该题为全新的日常请示，Candidate 与 Baseline 同时首抽。两稿均完整保留4间会议室、6台设备、8年、2台无法开机、3台闪烁、1台正常、更新5台、7.5万元、预算来源、采购程序、到货验收、资产登记、请批事项和落款；均未新增品牌、供应商、单价、具体采购方式或期限。

匿名映射为 A=Candidate、B=Baseline。独立盲审判难分：Candidate 标题信息更完整、实施复述更少，但两项请批合写；Baseline 两项请批更醒目、篇幅更接近要求，但标题省略发文机关，并有预算和验收关系的机械补句。两稿无事实、状态、文种、格式、输出模式或保护性外扩回退，直接修改成本接近。

- Candidate SHA-256：`FA3BE20736F7B3F71DA198123C57E6EC150359DD499B7946AC0A6CD1EC0D9C29`
- Baseline SHA-256：`7BA608039C1B5A8B12186B0472584A7BB1C5C3D358B7D7D7992CA0FFE0833F8D`

## 工程验证

- `python -m unittest discover -s tests`：354/354 通过。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，0 failed，0 errors。
- 固定 `a65c0d9` 与 current 的确定性消融：两侧均为 108/108。
- `quick_validate.py chinese-official-writing`：通过。
- `tools/sync_adapters.py`：canonical 已同步到发行镜像。
- `git diff --check`：通过，仅有既有 LF/CRLF 转换提示。

## 判定

本原子为 PASS，可以保留。它仅压缩同一入口中的重复格式反例，完整硬边界仍高曝光；专项稿字节级持平，新日常请示盲审难分，没有 Candidate 独有回退。
