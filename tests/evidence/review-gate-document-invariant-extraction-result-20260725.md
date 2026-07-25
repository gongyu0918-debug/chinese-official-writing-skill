# Review gate 文档不变量职责提取结果

## 结论

PASS。候选只做同文件纯函数提取，公共行为与固定基线等价，具备合并资格。

## 固定对象与改动

- 基线：`cb2b51e53412a5aa212e084edacde77a32d6427b`
- 预注册：`ca9c8f0`
- 产品提交：`8e8deec`
- 从 `evaluate_candidate` 提取 `_candidate_document_invariant_reason`，只负责标题、章节正文、正文保留比例、候选扩张和用户篇幅遵循五项不变量。
- `evaluate_candidate` 的签名、硬锚检查、D0/D1 选择、reason、CLI、JSON、状态、哈希和回退方式不变。

## 实际验证

- 定向事务与回退回归：245/245 通过。
- 全量 unittest：369/369 通过。
- Promptfoo smoke：20/20 通过。
- 固定基线确定性消融：基线 108/108，Candidate 108/108。
- quick validate：通过。
- `git diff --check`：通过。
- canonical、`skills/`、`.agents/`、`.qwen/`、Hermes 五份脚本一致；OpenClaw 未新增 `review_gate.py`。
- 独立只读 review：GO。五项检查顺序、`repair_mode` 例外、长度计算、D0 回退和 D1 reason 均保持原语义。

该修改不改变写稿 Prompt 或成稿文本，只重排检测器内部职责。真实验证采用既有真实事务路径的单元与回归覆盖，不新增写作稿件。

## 剩余风险

- `evaluate_candidate` 仍承担协议校验、修复授权、操作应用、硬锚保护和最终选择，函数仍较长；本轮只拆出风险最低且边界完整的一块。
- `detect_transaction` 也较长，但属于事务安全入口，未与本轮组合。
- Windows `git status` 会把若干未发生内容变化的 `SKILL.md` 标成修改；提交对象不含这些换行/stat 噪声。
