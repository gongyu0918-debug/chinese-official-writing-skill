# R6 manifest 与确定性夹具适配

本次仅修改 `maintenance/specs/reference-route-manifest.json`、`maintenance/evals/official-writing/providers/agent_writer.py`、`maintenance/tests/test_promptfoo_eval.py`、`maintenance/tests/test_reference_rewrite_contract.py`，另在 output 保存本报告和运行日志。未提交；未修改 canonical 产品、镜像、其他测试、native runner 或真实写稿证据。根任务在本次期间同步了镜像。

- 工作树：`F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912`
- 分支：`codex/reference-rewrite-20260912`
- 开工 HEAD：`d06d51f8c766739a3f0e49dc5205e1672aad53e4`
- 本次 commit：无，按分工留给根任务统一复核和提交。

## 适配范围

manifest 从 65 页更新为 72 页，当前 39 个主叶、41 条路线。新增审查意见、技术需求、责任书、倡议书、公开信、讲解稿、宣传材料七页；采购审查旧页改为采购专项 overlay。情况综合使用 report，建议信使用 advisory，采购方案使用 plan，采购审查意见使用 review-opinion 并附采购核对规则。

所有页的 `allowed_reads` 严格等于首页、自身及 canonical 页内实际直接指针；`forbidden_reads` 为其余当前主叶。没有通过允许全部主叶规避闭合检查。各路线 `review` 对齐当前四个通用终检/交付阶段；已有文种专项复核页仍保留在页面清单和实际指针中。

provider 夹具补充按交付用途区分：审核采购方案保留方案主叶和审稿页，依据评审记录起草独立意见使用审查意见主叶。采购专项规则按采购审查或明确专项核对条件附加；普通服务器、软件及接口需求使用技术需求主叶，明确算力场景加读 AI 页。技术内容出现在建设方案中时仍保留方案主叶。情况说明按解释事实/回应疑问与汇报进展用途区分说明、报告。

测试迁移了被七页新组织替代的页集合及采购旧主叶断言，补充新主叶在起草、审核、改写中的隔离和条件附加检查。既有事实、状态、完整正文、审稿意见、缺项、长度、脚本及交付断言保留，新增七页另核对主体、责任、待定状态和交付承接。未触碰 `test_skill_boundary.py` 的 16 个未决断言。

## 实际验证

命令均从上述工作树执行。

| 命令 | 结果 |
| --- | --- |
| `python -B -m unittest maintenance.tests.test_promptfoo_eval` | PASS，34 项，日志 `output/r6-promptfoo-final.log` |
| `python -B -m unittest maintenance.tests.test_reference_rewrite_contract` | PASS，29 项，日志 `output/r6-reference-contract-final.log` |
| `python -B maintenance/tools/validate_reference_manifest.py` | PASS，`reference manifest valid: 72 pages` |
| `python -B -c "from pathlib import Path; paths=['maintenance/evals/official-writing/providers/agent_writer.py','maintenance/tests/test_promptfoo_eval.py','maintenance/tests/test_reference_rewrite_contract.py']; [compile(Path(p).read_text(encoding='utf-8'),p,'exec') for p in paths]; print('syntax compile valid: 3 Python files')"` | PASS，三个 Python 文件语法编译通过，无 bytecode 落盘 |
| `git diff --check -- maintenance/specs/reference-route-manifest.json maintenance/evals/official-writing/providers/agent_writer.py maintenance/tests/test_promptfoo_eval.py maintenance/tests/test_reference_rewrite_contract.py` | PASS，退出码 0；Git 仅提示后续会转换 LF/CRLF |

最小单元测试合计由 57 项增至 63 项，最终 63/63 通过。

## 失败保留

首次联合测试运行 57 项，有 3 处失败，原日志为 `output/r6-fixtures-before.log`：

1. 新增七页未进入已生成页面集合；在本次 contract 测试中迁移集合断言后消除。
2. manifest 仍为 65 页，漏掉七页；本次补齐页面与实际读取边界后消除。
3. `test_mirror_contains_rewritten_overlay` 检出 `reference-index.md` 与镜像不同；根任务同步镜像后消除，本子任务未改镜像或放松字节一致性断言。

第一次适配后联合运行仍有 2 处失败，原日志为 `output/r6-fixtures-adaptation.log`：新页集合断言尚未更新；自然采购审查夹具仍将采购 overlay 当作主叶。随后迁移对应字面断言，并保留审查意见主叶与采购附加页两者检查。`output/r6-fixtures-check.log` 保存迁移后 63/63 的联合运行。

## 证据边界与未完成

这些是维护元数据和确定性夹具，不是真实模型选路证据。provider 由 Python 根据输入标签及受控任务文本选页；测试断言的是该确定性结果。它们不证明宿主自主读取、自然任务泛化、实际成稿质量或消融效果，不能计入根任务 native 写稿通过数。

未在本子任务运行真实模型、全量测试或 `test_skill_boundary.py`；native 验证和既存 16 个未决断言由根任务分别处理。没有修改 runner 或历史证据来消除失败。剩余风险是关键词夹具不能覆盖任意自然语言组合，实际选路和稿件质量继续以根任务的独立 native 证据为准。
