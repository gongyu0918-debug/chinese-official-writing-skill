# 1.6.34 组合减载复核（2026-09-12）

本候选从不含“开场称谓排序”功能的当前主线父提交 `dafc35f9aad594ac6cebf76bd4caf2e1b80a1ba8` 冻结。组合只考察三个此前分别通过的引用拆分：压缩细则、字段编辑细则、prose-lint 使用细则。对照基线 `99b355737361b72600244cd9fae901bd2b39986b` 只恢复这三处内联内容并删除对应叶子；结构编辑等其他规则两臂保持一致。产品差异严格为五个 canonical 文件：`SKILL.md`、`references/compression-details.md`、`references/field-editing.md`、`references/prose-lint-usage.md`、`references/workflow.md`。

## 真实写稿与通道绑定

本轮外层使用原生 Codex CLI harness 固定冻结目录、提示字节和回执；每臂新上下文，不联网、不启用 Hook/插件。实际绑定当前客户端 registry slug：

- `minimax-cn/MiniMax-M3`
- `alibaba-token-plan/qwen3.8-flash`
- `alibaba-token-plan-2/qwen3.8-flash`
- `command-code/deepseek-deepseek-v4.1-flash`（客户端显示名为 commandcode-auth/deepseek-deepseek-v4.1-flash）
- `ollama-cloud/glm-5.3-flash`

两条 Alibaba 是两个 provider 下的同一 Qwen3.8 Flash 家族，按通道分开记录，按模型家族解释。旧 `opencode-go/deepseek-v4-flash` 和小写 MiniMax 别名未计入本轮。

四类真实写稿均完成有效 max/max 配对：长篇限字报告（MiniMax，压缩交互）、字段拆行/删增字段（Alibaba Qwen，字段交互）、正式函压缩（command-code DeepSeek）和 Word 正文排版（Ollama GLM）。候选稿未出现基线没有的事实、状态或结构硬错误；差异是措辞、空行密度和是否附带执行说明等正常模型波动。长报告双方均保持 650—750 字和给定数字、日期、责任、未决状态；字段稿候选去除了基线的过程旁白；函的请求、邮箱、日期、联系人和附件均保留；Word 稿小标题独立成段、普通编号句不机械拆行，两臂结构一致。

## 技术不可判定项与门禁归因

`alibaba-token-plan-2/qwen3.8-flash` 的脚本调用题在 max 和唯一 high 回退均 300 秒无有效正文；候选和基线都未形成可比稿，归因为 provider/脚本执行技术不可用，不计写作失败，也不计候选回退。`alibaba-token-plan/qwen3.8-flash` 在同类脚本题补跑时同样出现候选 max/high 技术失败，故脚本交互本项只作覆盖缺口，不以门禁结果否定组合。原始失败回执保留在 `output/recheck-detail-combination-20260912-r2` 和 `-r3`，没有用后续结果覆盖。

因此，本轮没有发现候选独有的失败、过严门禁导致的假阴性或与改动区域无关的负点。证据支持组合在已完成的四类真实写稿中不劣于该合成基线；对脚本执行路径仍是“技术不可判定”，不宣称五通道全覆盖或统计意义上的普遍稳定性提高。

## 工程验证与冻结结论

- `quick_validate.py chinese-official-writing`：通过（`Skill is valid!`）。
- 受影响边界套件：102/102 通过。
- `git diff --check`、Python 语法检查：通过。

适当范围的三项组合可冻结为 v1.6.34 候选，保留在分支 `codex/release-v1.6.34-baseline-20260912`，不合并 main、不打 tag、不推送、不发布。脚本题和第二 Alibaba provider 的技术缺口留待明早以可用 provider 或修复后的执行环境补测，再决定是否扩大本版本范围。
