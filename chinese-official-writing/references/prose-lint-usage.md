# 脚本工具使用指南（计数、扫描、定位与精确替换）

本页供需要实测篇幅、机械风险扫描、原文定位或精确逐字替换时使用。所有脚本均为 Python 3 标准库实现（macOS/Linux 优先用 `python3`，Windows 可用 `python` 或 `py -3`），按已读 `SKILL.md` 所在目录定位，命令统一加 `-B` 避免生成字节码缓存。工具输出仅供内部核对，不写入最终回复（用户明确要求检查报告时除外）；工具受限时直接人工核对，不宣称实测达标。

---

## 一、字数统计与合并扫描（`scripts/draft_length.py`）

用于用户明确限定字数上下限，或需一次完成计数 + 机械风险扫描的场景。优先用 `-` 经 UTF-8 标准输入传入全文（零落盘）；已有 TXT/MD/DOCX 可传路径。

- **计数口径**：默认计全部非空白字符（含标点、数字、字母及标题/主送/落款）；只计汉字加 `--count-mode cjk`（Unicode 17.0 统一/兼容汉字及“〇”）。DOCX 仅计主文档正文与表格，**默认跳过显式标记 `w:vanish` 的隐藏运行**（不解析样式继承；需计入直接隐藏运行时加 `--include-hidden`）。
- **范围与交付模式**：
  - `--delivery-mode draft-body`（默认）：只交付稿件，计全文并检查是否残留正文外提示。
  - `--delivery-mode gap-note-allowed`：允许文后提示区，`auto` 口径自动排除 `文后提示` 之后内容；若用户限定整条回复总字数，加 `--count-scope full`。
  - `--delivery-mode review-only`：仅审稿意见，计全文并豁免引文内规则。
  - `--trial`：核对试写固定尾行 `文后提示：本稿为拟生成稿件。`（仅当交付含该标识时使用）。
- **常用命令（计数与扫描一次合并执行，无需重复跑两次）：**

```text
python3 -B -X utf8 "<Skill目录>/scripts/draft_length.py" --scan --delivery-mode draft-body --min-chars <下限> --max-chars <上限> --fail-on-violation -
```

- 仅计数不扫描时去掉 `--scan`（需 JSON 加 `--json`，单侧限字只传对应上下限，不给短稿加默认下限；`--outline` 可观察各段首句及字数占比）。
- 带 `--fail-on-violation` 时超界返回退出码 1，读取失败返回 2；无论退出码如何都须读取输出的计数结果。

## 二、独立机械风险与公开脱敏扫描（`scripts/prose_lint.py`）

无字数要求、仅需检查机械风险（AI 旁白、交付外壳、未完成占位符、重复标题、同节/跨节高相似复述、保护性尾句、Markdown 残留、机关格式硬差错如“截止/截至”、日期补零、括号全半角混配、发文字号六角括号、层次序号与独立小标题句号、标题语意重复、附件尾标点与裸后缀、落款空行、长条款/序号跳号、主次结构失衡如导语头重脚轻/空壳节/收尾打算反超主体、DOCX 零字号与修订批注痕迹）或对外公开稿脱敏体检时使用：

```text
python3 -B -X utf8 "<Skill目录>/scripts/prose_lint.py" --delivery-mode draft-body --format --structure -
```

- **对外公开发布稿（公示/通告/公开答复/公开通报）**：追加 `--public`（也支持 `draft_length.py --scan --public`），确定性拦截未脱敏 11 位手机号、18 位身份证号、精确户室住址及“内部掌握/勿公开/密级”标记。
- 用户明确要求 Markdown 输出时加 `--allow-markdown`。
- `draft_length.py --scan` 已内置 `--structure --format` 全部检查，无需再重复调用 `prose_lint.py`。
- **使用原则**：所有命中项（`review_candidates`）均为**待核线索**，退出码 0 不证明事实正确。回到材料和上下文确认：保留合法的业务条款、制度适用范围、正常公文三级编号（`1.`）及必要承接，只修已证实的问题；实质修改后最多复扫一次。

## 三、精确逐字替换（`scripts/edit_scope.py`）

**适用边界**：仅用于“指定文字替换、其余逐字保留”任务；自由改写、润色或 Word 排版不适用。

### 方式 A：零落盘内存模式（推荐，敏感材料与聊天原稿均适用）
经标准输入传一条 UTF-8 JSON，在内存中完成精确校验与生成，**脚本自身不读写任何磁盘文件**（宿主自身的工具日志与标准输出留存仍按宿主安全策略处理）：

```text
python3 -B -X utf8 "<Skill目录>/scripts/edit_scope.py" --stdin
```

标准输入 JSON 格式：
```json
{"original": "完整原稿文本", "edits": [{"old": "预算38万元", "new": "预算36万元"}]}
```
- 返回 JSON 中的 `output_text` 即为严格逐字保留的改后全文（含 `source_sha256`、`output_sha256`）。
- 需校验已有改稿是否严格等于替换计划时，在 JSON 中增加 `"candidate": "待校验改后稿"`：完全一致返回退出码 0，不一致返回 1 并给出首处差异与上下文。

### 方式 B：文件模式（本地已有 UTF-8 TXT/MD 原稿且允许落盘时）
1. 目标 `old` 在原稿多次出现时，先用下节 `material_diff.py` 查清全部位置和 0 基字符偏移 `start`，再写入计划。
2. 预先写好替换计划 JSON（`{"edits": [{"old": "...", "new": "...", "start": 12}]}`，可选 `source_sha256` 绑定原稿哈希）。
3. 执行生成（`--output -` 直接向 stdout 输出纯文本不落盘；传新文件路径则排他创建，绝不覆盖原稿）：

```text
python3 -B -X utf8 "<Skill目录>/scripts/edit_scope.py" --original "<原稿路径>" --output "<新稿路径或->" --plan "<计划JSON路径>"
```
- `old` 须非空；删除用 `new: ""`，插入用相邻原文作 `old` 锚点，空 `edits` 表示逐字保留；替换范围不得重叠。
- 核对交付时，若用户只要求改后全文，最终回复直接从改后第一字开始、最后一字结束，不附脚本结果或说明。

## 四、关键原文定位与数字/日期自动对账（`scripts/material_diff.py`）

### 方式 A：素材↔成稿数字/日期/书名号自动对账（`--audit`，多数据/多日期长稿推荐）
无需手动列词，一次自动双向核对 `draft_only_dates`、`source_only_dates`、`draft_only_quantities`、`source_only_quantities`、`draft_only_titles`、`source_only_titles`，快速抓出误改日期、凭空新增数字或意外漏数：

```text
python3 -B -X utf8 "<Skill目录>/scripts/material_diff.py" --stdin --audit
```
标准输入 JSON：`{"source": "有效材料", "draft": "成稿全文"}`（本地文件模式传 `--source "<材料>" --draft "<成稿>" --audit`）。

### 方式 B：精确子串坐标定位（配 `edit_scope.py` 用）
多份材料含补充更正、或需定位重复替换目标的精确 0 基偏移 `start` 时使用，支持 `--stdin` 零落盘 JSON 及本地 TXT/MD/DOCX 文件：

```text
python3 -B -X utf8 "<Skill目录>/scripts/material_diff.py" --stdin
```
标准输入 JSON：`{"source": "有效材料", "draft": "稿件", "literals": ["预算38万元", "建议分期实施"]}`

本地文件模式：
```text
python3 -B -X utf8 "<Skill目录>/scripts/material_diff.py" --source "<材料路径>" --draft "<稿件路径>" --literal "预算38万元"
```
- 工具只提供精确坐标或机械对账线索，不判定事实对错（合理合计值或有意删略项结合上下文判断）。DOCX 文件返回的是主文档提取文本坐标（不代表 Word 原生字符偏移，不可直接用作纯文本替换计划的 `start`）；`--stdin` 仅接收 UTF-8 文本 JSON。

## 五、零依赖 GB/T 9704-2012 公文 Word 生成与验版（`scripts/build_docx.py`）

用户要求交付规范 Word（`.docx`）公文时，直接从标准输入或纯文本文件一次生成并内置 GB/T 9704 + `prose_lint` 自检（详见 `references/format-gbt9704.md`）：

```text
python3 -B -X utf8 "<Skill目录>/scripts/build_docx.py" --input - --output "<输出.docx>" --profile ordinary
```
- 支持 `--profile ordinary | formal-preprinted | formal-digital | minutes`、`--doc-no`、`--org`、`--signer`、`--cc`、`--print-org`、`--print-date`、`--seal-mode stamped|unstamped`、`--overwrite`。
- 独立核验既有 `.docx` 版式合规性：`python3 -B -X utf8 "<Skill目录>/scripts/build_docx.py" --verify "<文件.docx>" --profile formal-preprinted`。

*Windows 宿主提示*：优先通过宿主标准输入接口直接传 UTF-8 字符串；若经 PowerShell 管道传文本，先确认编码与引号/美元符号/换行字面保真。
