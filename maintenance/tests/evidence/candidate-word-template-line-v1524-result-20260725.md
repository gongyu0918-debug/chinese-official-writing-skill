# Word 来源模板规则单行减载结果（2026-07-25）

## 结论

`PASS`，具备合并资格。

本候选只从通用 `review-checklist.md` 删除一条已由 `format-gbt9704.md` 承担的来源模板规则，其余四条 Word 复核规则、入口、路由、加载条件、输出模式、复核顺序、脚本和版本号均未修改。两题严格对称真实 A/B 均由 Candidate 小胜，固定 1.5.24 基线无胜题；两侧均无事实、数字、日期、主体、状态、文种、模板结构、Markdown、落款日期或材料外事实硬失败。

## 提交与差异

- 固定基线：`d5a875ec19a02e6a664e5c77587c5750791cb2f9`
- 预注册：`4eb8d84c988fb103ff5ee0a6cb3a2a463f8e2ffc`
- 产品提交：`be5ba9d715aadd294985f9a3f5bdd273d0bb5357`
- 产品 diff：canonical 与五个发行镜像各删除同一行；增加两个确定性断言，合计 7 个文件、2 行新增、6 行删除。

删除行：

> Word 格式是否保留来源模板；正式红头格式是否有用户模板或明确要求。

保留来源：`format-gbt9704.md` 继续明确要求用户提供单位模板、企业模板或内部审批样式时优先保留来源模板。

## 工程验证

| 验证 | 结果 |
| --- | --- |
| 定向 `test_skill_boundary` | 53/53 通过 |
| 全量 unittest | 沙箱内 149 个系统临时目录权限错误；同一提交用系统 Python 非沙箱复跑 368/368 通过 |
| Promptfoo smoke | 20/20 通过，0 failure，0 error |
| 固定 1.5.24 确定性消融 | baseline 108/108；current 108/108 |
| quick validate | `Skill is valid!` |
| canonical 与五个镜像 | `fc /b` 均无差异 |
| `git diff --check` | 通过 |

首次全量 unittest 的 149 个错误均为沙箱拒绝写 `C:\Users\admin\AppData\Local\Temp`，不是产品断言失败；保留环境失败记录，不改写为产品通过。真实工程结论取同一提交在获批环境的 368/368 复跑结果。

## 真实 A/B 有效性

T1、T2 双方均：

- 使用逐字一致原始任务；
- 按相同顺序读取 `SKILL.md`、`information-selection.md`、`genre-playbooks.md`、`genre-checklist.md`、`format-gbt9704.md`、`review-checklist.md`；
- 保留首个技术有效输出，未补抽、未二次修改；
- 模型和 thinking 均为 `unavailable`，没有单侧覆盖，不能宣称具体配置已经核验。

T2 基线在稿件交付后的文件验证中误对 T1 文件计算大小和 SHA-256，但未显示或读取 T1 正文。独立运行审计将其认定为 `post-write non-content deviation`，不影响 T2 生成内容；该偏差仍保留在 provenance 和运行审计中。

## 匿名盲审

匿名打包对每题独立使用系统加密安全随机数；匿名稿与源稿 SHA-256 一致。独立 judge 只读取原始任务与 A/B 稿，不读取映射、运行审计、产品 diff 或历史结论。

| 题目 | 映射 | 硬检查 | 匿名结论 | 还原结论 |
| --- | --- | --- | --- | --- |
| T1 正式通知直接改稿 | A=Candidate，B=基线 | 两侧通过 | A 小胜 | Candidate 小胜 |
| T2 企业内部模板只审不改 | A=基线，B=Candidate | 两侧通过 | B 小胜 | Candidate 小胜 |

T1 Candidate 只完成用户点名的 Markdown 清理和核对卡补充，固定基线额外增加“自”“工作”两个非必要词。T2 Candidate 在覆盖同等硬要素时更紧凑，并保持栏目顺序、全部数字、处理状态、落款和日期。

原始稿、provenance、匿名稿、随机映射、运行审计和 judge 原始回执保存在 ignored `output/candidate-word-template-line-v1524-real-ab/`。

## 剩余风险

- 真实样本只覆盖一题正式通知直接改稿和一题企业内部模板只审不改，不能代替所有 Word 模板、DOCX 工具和正式排版矩阵。
- 本次净减载只有一行，收益小但因果边界清楚；不与此前一次删除五条、已判 FAIL 的候选合并计算。
- 模型和 thinking 元数据不可用，结论限于双方默认运行条件对称且无单侧覆盖。

## 处置

独立轻量 release-gate 复核产品 diff、工程产物、真实运行对称性、随机映射和 judge 原始回执后，若无 P0/P1，可快进合并本地主线；不推送、不发布。
