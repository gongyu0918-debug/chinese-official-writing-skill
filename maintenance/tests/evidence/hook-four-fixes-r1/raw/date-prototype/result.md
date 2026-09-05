# 日期来源歧义最小原型

状态：`PROTOTYPE_NOT_CANONICAL_NOT_ADMITTED`。基线为 main `3532afd6619ac6256558e9552b92d03da5ae9c0f`；准备原型时工作分支为 `codex/hook-four-fixes-r1`，HEAD `259d1693a3ceca76c09076fa29f7c0848771fff5`。本目录独立运行，未修改 canonical 日期模块，也没有模型调用。

## 结果与样本边界

共 10 个输入、20 次纯日期函数调用，冻结预期全部符合。完整输入在 [inputs.json](inputs.json)，完整输出在 [results.json](results.json)。本次没有执行 core 子进程、宿主 Hook 生命周期或新生稿。

| 类别 | 数量 | 基线 | 候选 |
| --- | ---: | --- | --- |
| 旧真实漏年 D0 + 原始请求 | 3 | 精确补回材料中的 2026 年 | 输出与基线完全相同 |
| 旧真实完整日期 D0 + 原始请求 | 1 | 原文不动 | 原文不动 |
| 同一旧真实 D0 + 来源角色请求变体 | 2 | 均把 9月2日错补成 2020年9月2日 | 均逐字保留原始 D0 |
| 前文/原稿/模板普通提及、引号事实反控 | 2 | 正常补回 2026 年 | 输出与基线完全相同 |
| 历史手写故障反控、新增纯示例反控 | 2 | 均从非事实示例补入 2020 年 | 均逐字保留原始 D0 |

前四例的 D0 从已归档 `repair_cases.json` 读取，并与原 AH002 worktree 的原始模型 final 文件逐字节核对。原请求完整取自 `cases.json`，没有用手写摘要替代。三份漏年 D0 来自 Ollama Cloud DeepSeek V4 Flash 0731；完整日期 D0 来自 MiniMax M3。原路径、当前证据文件 hash、原始文件 hash、模型路线和完整正文均保存在输入包。

两个来源角色请求变体复用同一份真实 TRAINING D0：仅将原请求中的事实日期由 `2026年9月2日` 改为同值 `2026-09-02`，然后附加明确不属于本次事实的格式示例或旧稿示例 `2020年9月2日`。两臂收到完全相同的变体请求和 D0。**这属于真实旧稿的反事实修订输入，不能写成原始自然成稿配对，也不能据此推算自然发生率。** 候选阻止了新添错误年份，但保留了 D0 既有漏年状态。

历史手写反例只从归档脚本的 AST 提取原始 `REQUEST`/`DRAFT` 常量，没有重新执行旧脚本。新增纯示例例独立标注，专门检查非事实标签分支；不冒充历史结果或真实模型稿。

## 改动

[candidate.patch](candidate.patch) 只涉及 `hooks/shared/source_bound_dates.py`，未接入 core 或适配器：

1. 把可识别的其他完整日期写法作为“拒绝自动补年”的信号。ISO、斜线、点分、带空格中文和中文数字年份只用于检测，不从这些写法推导年份。
2. 若唯一可解析完整日期都紧跟明确示例/非事实日期标签，保留 D0。不按全请求中的“前文”“原稿”“底稿”“模板”关键词一概禁用，也不屏蔽普通引号事实。

原有文种、显式省年、中文完整事实日期唯一性、同月日歧义、完整 D0 和唯一目标检查保持不变。候选代码为 [source_bound_dates_candidate.py](source_bound_dates_candidate.py)，冻结基线代码为 [source_bound_dates_baseline.py](source_bound_dates_baseline.py)。

## 验证与复放

实际执行 `python -B -X utf8 output/hook-four-fixes-r1/date-prototype/replay.py`，exit 0，10/10 符合预冻结预期。脚本、输入包与两份模块均绑定 hash；已有结果路径会拒绝覆盖。再次检查时运行：

```powershell
python -B -X utf8 output/hook-four-fixes-r1/date-prototype/replay.py --output output/hook-four-fixes-r1/date-prototype/results-repeat.json
```

`--help`、Python AST、JSON 解析、本说明本地链接、`git apply --check candidate.patch` 和 `git diff --check` 的实际结果见 [validation.json](validation.json)。没有全量测试或新真实模型调用。后续两路新生稿由主代理统一执行，不计入本文件结果。

## 未完成与剩余风险

- 本次只证明日期函数在列明的同输入比较中降低错误补年风险；尚未证明默认 Hook 的最终可见稿、恢复或各宿主行为。
- 日期写法检测和紧邻标签不是完备的来源角色解析。未覆盖的格式、非紧邻的来源标签、未标明角色的旧稿仍有剩余风险。
- 出现这些未分类格式时，即使人可以判定年份，候选也会放弃补年。这是保守旁路；没有新增通用模型门，也不承诺完整补年率。
- core 对正常自动修订仍会先产生 `draft_for_gate`；本原型没有解决原始宿主 D0 的独立恢复快照问题。
- 只核对候选相对 D0 的增量日期变化；旧稿中的其他文句质量不因此获得背书。

## 固定 hash

| 文件/文本 | SHA-256 |
| --- | --- |
| 冻结日期模块基线 | `d1e5b9da5607bfa7b3e27be8642e77e34a352617c52cf8d41fba8c19e0fbd015` |
| 日期模块候选 | `5f28a20b0b32cda9f4610fbbabfbb7592819272662abba852d8c3f96b85aae3a` |
| candidate.patch | `7e9086a6a108513dc9cfbccc9937b3523215d8f47700b63118ad70e956922542` |
| inputs.json | `6ade05483c423b58141458791185e18845d332abf5e402a97045d5767be8a7c1` |
| results.json | `dc4bc429becdefa803912018a9677e5bd9850945875565f1b063cb6b51f2608d` |
| 复用真实 TRAINING D0 | `17a3dcf945d316b7a95b22a1a60b67480c099fe9fcd71391aaa53f1033731f2a` |
| 两个变体的基线错误输出 | `a548568de3af04b0b6d78f83817a95738fd3fad4e37c4ab8ce4d04c66993b4be` |
