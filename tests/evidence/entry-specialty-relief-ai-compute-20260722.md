# AI 算力专项规则迁移验证（2026-07-22）

## 变量与基线

- 固定基线：提交 `0fdd6f1`，即第一批入口减负已经通过真实 A/B 后的状态。
- 单一变量：从 `SKILL.md` 的通用质量建议中移除 AI 算力、采购和服务器租赁的详细论证句；专项能力继续由入口路由表和 `references/ai-compute-docs.md` 承接。
- 未修改：事实边界、信息选择、文种路由、输出模式、段内写法、复核顺序、脚本、FSM、Word 路径和其他专项规则。

按统一换行口径统计，入口由 10,366 字符降至 10,280 字符，减少 86 字符，约 0.83%。

## 真实 A/B

writer 与 judge 使用独立 subagent。Baseline 与 Candidate 使用逐字一致的自然语言任务和 high reasoning，各取首个技术有效输出；协作接口没有返回可核验的模型名称，模型标识记为 `unavailable`。

### T01 AI 推理服务年度租赁方案说明

材料包含业务需求、Token、峰值并发、GPU 资源、预算、服务期、SLA、境内处理、日志留存、验收和付款要求。Candidate 实际读取：

- `SKILL.md`
- `information-selection.md`
- `genre-playbooks.md`
- `ai-compute-docs.md`
- `handling-elements.md`
- `argument-chains.md`
- `final-review-layers.md`
- `proofreading-checklist.md`

匿名映射为 A=Baseline、B=Candidate。独立盲审结论为 B 胜：两稿均无硬回退和保护性外扩，Candidate 的“业务需求—租赁方案—安全验收与付款—提请审议”链条更紧，重复解释和直接修改成本更低。

- Candidate SHA-256：`1539F4EF75A33788C98B9040C691A8E2922A3C2189B0754499D2E980EF847121`
- Baseline SHA-256：`6082BEC346F0169B56A1C1E6AF003BFD677C222E6FB2E6D1EC6701C2F8946E07`

### T02 机关办公区雨水管网清淤完成情况报告

该题与 AI 算力无关，用于检查删除入口专项句后是否影响日常报告。两侧均只读取 `SKILL.md`、`information-selection.md` 和 `task-route-cards.md`。

匿名映射为 A=Candidate、B=Baseline。独立盲审结论为 A 胜：两稿均保留全部事实、数字、状态和输出模式，Candidate 重复更少、衔接更自然；两稿均低于“约 600 字”，作为共同不足记录，不据此改变胜负。

- Candidate SHA-256：`C4BF8C8EC3B693C627311A42C18ECFDACE6945E16C2082F8564517DCDBDF28F5`
- Baseline SHA-256：`46CD7389818F02B2A7FAD46CBEDEAE581D2393FA1569B3B6AF70FF8590C6824C`

## 工程验证

- 固定 `0fdd6f1` 与 current 的确定性消融：两侧均为 108/108。
- 专项边界单测：通过，确认详细论证要素仍在 `ai-compute-docs.md`，入口只保留路由。
- `python -m unittest discover -s tests`：354/354 通过。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，0 failed，0 errors。
- `quick_validate.py chinese-official-writing`：通过。
- `tools/sync_adapters.py`：canonical 已同步到各发行镜像。
- `git diff --check`：通过，仅有既有 LF/CRLF 转换提示。

## 结论

本条迁移可保留。它没有削弱 AI 算力专项成稿能力，也没有给普通报告带来事实、文种或输出模式回退。当前证据只支持迁移这一条专项论证句，不外推到字段式材料、网页复制稿、文种结尾或段内公式。
