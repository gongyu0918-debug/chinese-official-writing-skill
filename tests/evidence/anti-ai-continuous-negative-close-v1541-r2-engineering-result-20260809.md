# anti-AI 连续否定式收口 R2 工程结果

日期：2026-08-09

研究分支：`codex/anti-ai-protective-state-v1541`

固定底座：`main=fb52e16dc94566d55eb679d3efdf2cbe19113513`。

预注册补充：`2c85ad38`

R2 产品提交：`b0e12c4c`

评测锚点提交：`597ed136`

## 结论

`ENGINEERING PASS / PROCEED TO ISOLATED REAL A/B`。

R2 把用户点名的十种同构否定尾句压成一个“连续否定式收口”反例簇。即使材料确有未决状态，也保留含义并直接写事项和当前办理状态；无办理作用时删除。未增加词级禁令、自动替换、脚本或新规则段落，B 两步骨架未修改。

canonical 相对失效 R1 规范化净增 32 字符，相对当前 `main` 净增 116 字符。canonical 与五份运行镜像 SHA-256 唯一值为 `CCC3FE7303AA007D4E2F0025BB8D500800907693E0C5D03974EDC1DFA94ED73E`。

## 首次工程失败及修正

第一次完整复跑中，旧测试和 P109 硬编码“无前文依据的否定”，导致 `test_skill_boundary` 66/67、全量 456/458；该失败属于标签重命名后的评测锚点漂移，不是产品行为回退。`597ed136` 只把两个确定性锚点及 P109 用户式 prompt 改为“连续否定式收口”，未修改运行时产品。

修正后实际结果：

| 检查 | 结果 |
| --- | --- |
| R2 聚焦测试 | 1/1 通过 |
| `python -m unittest tests.test_skill_boundary` | 67/67 通过 |
| `python -m unittest discover -s tests -p 'test_*.py'` | 458/458 通过 |
| `OFFICIAL_WRITING_EVAL_STUB=1; npm.cmd run eval:official-writing:smoke` | 20/20 通过，0 error |
| 固定 `main=fb52e16d` 确定性工程门 | Baseline 110/111；Candidate 111/111；唯一差项为 Baseline 缺少 R2 新锚点 P109 |
| Skill Creator `quick_validate.py` | `Skill is valid!` |
| `tools/sync_adapters.py` 后复查 | 六份 reference 字节一致 |
| `git diff --check` | 通过 |

Promptfoo 使用本地 stub，111 项工程门不调用 LLM；真实收益仍以 A1—A4 的 Alibaba/Ollama 首稿和独立 Sol 盲审为准。

## 旧真实调用状态

R1 真实写稿没有形成有效正文。Codex app 编排调用无可核验 task ID；CLI 探针 `019fe4ce-12fc-7c03-a505-d47a65b57799` 只输出 `OK`；首轮并发调用因共享隔离 `CODEX_HOME` 出现 SQLite `disk I/O error`。这些均标为 `INVALID / ENVIRONMENT FAILURE` 并保留原始外部日志，不进入 R2 匿名包。
