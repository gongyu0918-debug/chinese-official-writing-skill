# S15/C01 真实 A/B 运行证据审计

## 审计边界

- 审计对象：`S15`、`C01` 的 `M/N/draft.txt`、`provenance.json`，两套 Skill 包及 `blind` 下匿名副本。
- 只核验运行证据、文件哈希、路径、Git 对象和运行对称性；不评价稿件语言，不读取任何盲审结论。
- 匿名稿仅计算文件长度和 SHA-256，未读取正文。
- `provenance.json` 中没有原始模型调用回执、调用 ID 或完整工具轨迹时，只确认字段已记录，不把自报字段升级为独立复验结果。

## 总结论

两题的任务、源材料、输出、已记录 reference 和匿名副本哈希均与现存文件一致；M/N 包各有 29 个同路径文件，唯一字节差异是 `references/information-selection.md` 的一行，M 包逐文件对应候选提交 `a3134679be2198ea59290cf87292e0cfd0b8140c`，N 包逐文件对应其父提交 `da470508dc9bf27703d5f9ccd5825cdf6f82c234`。已记录的 reference 均位于各自臂的包内，未发现已记录路径跨臂。

但两题均不足以作为严格 A/B：

1. 四臂仅能确认请求条件均为 `gpt-5.6-terra / high`；实际模型和实际 thinking 均为 `unavailable`，不能证明两臂实际运行条件相同。
2. 四臂都记录 `single_call=true`，但没有原始调用回执可独立复验；M 两臂没有 `first_output_status`，因此 M 是否为首个技术有效输出为 `unavailable`。N 两臂明确记录 `first_output_status=technically_valid`。
3. 同题两臂的实际 reference 读取集合明显不对称。该差异可能是 Skill 运行链的结果，也可能受未记录的运行差异影响；现有证据不能区分，不能将其静默当作逐字一致的生成上下文。
4. N 两臂记录了运行期间预存的 5 个 tracked 修改并发消失；M 两臂记录的 index/stat 快照则前后一致。当前 worktree 已 clean，但当前状态不能追溯证明当时不存在其他并发影响。
5. M 两臂记录 `prohibited_reads`，N 两臂没有同类字段。可以确认 N 已列出的读取均来自 N 包，但是否存在未记录的跨臂、根 worktree 或其他读取为 `unavailable`。

因此，这四份输出只能作为“请求条件相同、静态包单变量成立、文件身份可复验”的探索性真实运行对照；不能据此单独下达严格 A/B 的质量胜负结论。

## 静态包与 Git 对象

### 包路径

- M：`packages/M/chinese-official-writing`
- N：`packages/N/chinese-official-writing`
- 两套包路径均存在，均声明版本 `1.5.28`。
- M/N 文件集合均为 29 个文件，无单边缺失。

### 唯一包差异

全包逐文件 SHA-256 比较只有一处差异：

| 路径 | M SHA-256 | N SHA-256 | 字节差异 |
|---|---|---|---|
| `references/information-selection.md` | `fd51598230a4e9caf53c0db76091cb7567a23e49c0e686975651021aac7df3fc` | `cb79903d764ce18aaf3586434bdf24339f3ebc07afa0188c4ab6053f48e4bcee` | 一行增加一句；其余内容一致 |

其余 28 个文件字节一致。静态单变量成立。

### Git 对象对应关系

- 当前候选 worktree HEAD：`a3134679be2198ea59290cf87292e0cfd0b8140c`。
- M 包 29 个文件经 Git clean filter 计算的 blob 与该 HEAD 下 canonical 包逐文件一致，差异数为 0。
- N 包 29 个文件与 `a313467^`，即 `da470508dc9bf27703d5f9ccd5825cdf6f82c234` 下 canonical 包逐文件一致，差异数为 0。
- 当前审计时 `git status --short --branch` 只显示分支行，无 tracked 或 untracked 改动；`git diff --check` 无输出。
- M provenance 中的 `skill_source_manifest_sha256=4fbc51...` 没有附生成算法或 manifest 原文，无法独立重算，准确性为 `unavailable`。N provenance 未提供对应 manifest 字段。

## S15

### M 臂

| 项目 | 核验结果 |
|---|---|
| task/source | 均指向 `S15/request.txt`；现存文件 SHA-256 为 `eae3de80509e44f1c5e82419fbc15d72a833f9909351a5a4f3c7e5b044ad9110`，与两项记录一致 |
| output | `S15/M/draft.txt` SHA-256 为 `ea24ddacda24d331af9f68ec648931ba3dc252b95b44767e656946eccdececb0`，与记录一致；3374 UTF-8 字节、1220 个含空白字符、1189 个非空白字符，均与记录一致 |
| single call | provenance 记录 `true`；无原始调用回执，独立复验为 `unavailable` |
| first technical output | provenance 无对应字段，结论为 `unavailable` |
| 模型/thinking | requested=`gpt-5.6-terra/high`；actual=`unavailable/unavailable` |
| Skill 路径 | 绝对路径解析到 `packages/M/chinese-official-writing` |
| reference | 记录 10 个读取；逐一重算 SHA-256 均匹配，路径均位于 M 包内 |
| 跨臂读取 | 已记录路径未跨臂；provenance 自报 `packages_N=false`；未记录读取是否存在无法独立确认 |
| tracked worktree | 自报 index 与 683 个 stage-0 tracked 路径 stat 快照前后一致；当前 HEAD 与记录一致，历史快照本身没有独立原始清单可重算 |

M 已记录读取：

`SKILL.md`、`information-selection.md`、`task-route-cards.md`、`workflow.md`、`genre-playbooks.md`、`handling-elements.md`、`argument-chains.md`、`official-style.md`、`final-review-layers.md`、`proofreading-checklist.md`。

证据有效性：文件身份、静态包身份和已记录读取有效；首个技术有效输出及实际模型条件不可确认。M 臂为部分有效证据。

### N 臂

| 项目 | 核验结果 |
|---|---|
| task/source | 均指向同一 `S15/request.txt`；SHA-256 与 M 臂及记录一致 |
| output | `S15/N/draft.txt` SHA-256 为 `862423aef66ccae0bc8aa2b757cc5b3e73213fd056094b88a905578a794a7bcf`，与记录一致；3568 UTF-8 字节、1296 个含空白字符，与记录的 `chars=1296` 一致 |
| single call | provenance 记录 `true`；无原始调用回执，独立复验为 `unavailable` |
| first technical output | provenance 明确记录 `technically_valid`；无原始调用回执可独立复验 |
| 模型/thinking | requested=`gpt-5.6-terra/high`；actual=`unavailable/unavailable` |
| Skill 路径 | `../../packages/N/chinese-official-writing` 从 `S15/N` 解析到 N 包 |
| reference | 记录 7 个读取，`read_count=7`、字符合计 27967；逐一重算 SHA-256 均匹配，路径均位于 N 包内 |
| 跨臂读取 | 已记录路径未跨臂；未提供 `prohibited_reads` 字段，未记录读取为 `unavailable` |
| tracked worktree | 记录初始存在 5 个 `SKILL.md` 修改，结束时变为 clean，并称非本任务写入；并发消失原因未提供可复验证据 |

N 已记录读取：

`SKILL.md`、`information-selection.md`、`workflow.md`、`genre-playbooks.md`、`argument-chains.md`、`final-review-layers.md`、`proofreading-checklist.md`。

证据有效性：文件身份、静态包身份和已记录读取有效；实际模型条件及未记录读取不可确认，且 worktree 有并发状态噪声。N 臂为带保留的有效证据。

### S15 成对结论

- 同一任务文件和 source 哈希：成立。
- 静态 Skill 包单变量：成立。
- 请求模型/thinking 对称：成立。
- 实际模型/thinking 对称：`unavailable`。
- 首个技术有效输出对称：不成立；N 有字段，M 为 `unavailable`。
- 实际读取对称：不成立，M 为 10 个，N 为 7 个；M 独有 `task-route-cards.md`、`handling-elements.md`、`official-style.md`。
- 严格 A/B：证据不足。

## C01

### M 臂

| 项目 | 核验结果 |
|---|---|
| task/source | 均指向 `C01/request.txt`；现存文件 SHA-256 为 `30eeccf23f27dc179474a4d5593067f5ea3fc221e73deef06e377e610909ebf9`，与两项记录一致 |
| output | `C01/M/draft.txt` SHA-256 为 `3c624a4cae7a7a668eae29685205034d4e5cfa0ca1b65bcd71646d4ee8995551`，与记录一致；1548 UTF-8 字节、562 个含空白字符、541 个非空白字符，均与记录一致 |
| single call | provenance 记录 `true`；无原始调用回执，独立复验为 `unavailable` |
| first technical output | provenance 无对应字段，结论为 `unavailable` |
| 模型/thinking | requested=`gpt-5.6-terra/high`；actual=`unavailable/unavailable` |
| Skill 路径 | 绝对路径解析到 `packages/M/chinese-official-writing` |
| reference | 与 S15/M 相同的 10 个读取；逐一重算 SHA-256 均匹配，路径均位于 M 包内 |
| 跨臂读取 | 已记录路径未跨臂；provenance 自报 `packages_N=false`；未记录读取无法独立确认 |
| tracked worktree | 与 S15/M 记录相同的稳定 index/stat 快照；当前 HEAD 与记录一致 |

证据有效性：文件身份、静态包身份和已记录读取有效；首个技术有效输出及实际模型条件不可确认。M 臂为部分有效证据。

### N 臂

| 项目 | 核验结果 |
|---|---|
| task/source | 均指向同一 `C01/request.txt`；SHA-256 与 M 臂及记录一致 |
| output | `C01/N/draft.txt` SHA-256 为 `1b28b17bd1d91612ccc1f038d62649c48471d88c6ee3598e0ea6488e88d01011`，与记录一致；1432 UTF-8 字节、524 个含空白字符，与记录的 `chars=524` 一致 |
| single call | provenance 记录 `true`；无原始调用回执，独立复验为 `unavailable` |
| first technical output | provenance 明确记录 `technically_valid`；无原始调用回执可独立复验 |
| 模型/thinking | requested=`gpt-5.6-terra/high`；actual=`unavailable/unavailable` |
| Skill 路径 | `../../packages/N/chinese-official-writing` 从 `C01/N` 解析到 N 包 |
| reference | 记录 3 个读取，`read_count=3`、字符合计 13050；逐一重算 SHA-256 均匹配，路径均位于 N 包内 |
| 跨臂读取 | 已记录路径未跨臂；未提供 `prohibited_reads` 字段，未记录读取为 `unavailable` |
| tracked worktree | 与 S15/N 相同，记录初始 5 个 tracked 修改在运行期间并发消失；原因无法复验 |

N 已记录读取：

`SKILL.md`、`information-selection.md`、`task-route-cards.md`。

证据有效性：文件身份、静态包身份和已记录读取有效；实际模型条件及未记录读取不可确认，且 worktree 有并发状态噪声。N 臂为带保留的有效证据。

### C01 成对结论

- 同一任务文件和 source 哈希：成立。
- 静态 Skill 包单变量：成立。
- 请求模型/thinking 对称：成立。
- 实际模型/thinking 对称：`unavailable`。
- 首个技术有效输出对称：不成立；N 有字段，M 为 `unavailable`。
- 实际读取对称：不成立，M 为 10 个，N 为 3 个；共同读取为 `SKILL.md`、`information-selection.md`、`task-route-cards.md`，M 另读 7 个 reference。
- 严格 A/B：证据不足。

## 匿名副本

未发现独立匿名映射 manifest；以下映射由匿名副本与原始 draft 的字节级 SHA-256 相等关系确定：

| 场景 | 匿名稿 | SHA-256 | 对应原始臂 | 结论 |
|---|---|---|---|---|
| S15 | A | `862423aef66ccae0bc8aa2b757cc5b3e73213fd056094b88a905578a794a7bcf` | N | 字节一致 |
| S15 | B | `ea24ddacda24d331af9f68ec648931ba3dc252b95b44767e656946eccdececb0` | M | 字节一致 |
| C01 | A | `3c624a4cae7a7a668eae29685205034d4e5cfa0ca1b65bcd71646d4ee8995551` | M | 字节一致 |
| C01 | B | `1b28b17bd1d91612ccc1f038d62649c48471d88c6ee3598e0ea6488e88d01011` | N | 字节一致 |

匿名副本本身准确，无转码或内容漂移。由于没有单独的 mapping 文件，无法核验“预先登记的映射记录”是否与上述关系一致；该项为 `unavailable`。

## 运行不对称与环境噪声

1. 四臂均报告初次 PowerShell 进程创建因 `CreateProcessAsUserW error 5` 失败，随后跨出失败边界完成只读操作。该噪声各臂都有记录。
2. M 使用 index SHA-256 与 tracked stat 快照前后对比；N 使用 initial/final `git status`，两侧 tracked-worktree 证明方法不一致。
3. N 两臂运行期间 5 个预存 tracked 修改并发消失；M 两臂未记录这一变化。当前 worktree clean 只能确认审计时状态。
4. M/N provenance schema 不一致：M 有 `prohibited_reads`、manifest 和非空白字符计数，但没有 `first_output_status`；N 有 `first_output_status`、读取字符数和汇总，但没有 `prohibited_reads` 或包 manifest。
5. S15 的实际读取数为 M 10、N 7；C01 为 M 10、N 3。已记录文件均真实存在且哈希匹配，但生成上下文并非逐项对称。
6. 原始调用回执、实际模型 ID、实际 thinking、调用时间、调用 ID、完整工具调用日志均未提供，相关事项均为 `unavailable`。
