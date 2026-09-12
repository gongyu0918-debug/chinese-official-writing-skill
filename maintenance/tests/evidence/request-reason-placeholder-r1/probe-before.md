# 申请缺原因占位漏检诊断

## 结论

当前 `chinese-official-writing/scripts/prose_lint.py` 对以下两种交付正文占位稳定漏检：

- `因＿＿＿＿＿＿＿＿，现申请将资料核对完成时间延至9月27日。`
- `〔延期原因〕，现申请将资料核对完成时间延至9月27日。`

在 `draft-body` 中，Python `scan()` 均返回空 findings；CLI 使用 `--structure --format --json --strict --fail-on medium` 也均输出 `[]` 并退出 `0`。第一句放在 `gap-note-allowed` 的正文区时结果相同。脚本因此可以在正文仍有必要性缺口时自报无风险。

原因明确：现有 `unfinished-placeholder` 只覆盖带“具体、待、填写、补充、确认”等词的方括号、带少数提示词或字段名的括号/六角括号、`X/XXXX` 和 `YYYY年MM月DD日`；它既不识别连续全角下划线，也不把不含提示词的 `〔延期原因〕` 视为占位。现有规则本身位于通用 `PATTERNS`，没有申请原因的句法约束。

## 实测边界

| 样例 | 模式/选项 | 当前结果 | 建议结果 |
| --- | --- | --- | --- |
| `因＿＿＿＿＿＿＿＿，现申请延期。` | `draft-body` | 无 finding，CLI 0 | `unfinished-reason-placeholder`，medium |
| `〔延期原因〕，现申请延期。` | `draft-body` | 无 finding，CLI 0 | `unfinished-reason-placeholder`，medium |
| 上述下划线在正文，后接标准 `文后提示` | `gap-note-allowed` | 正文也无 finding，CLI 0 | 只报正文占位 |
| 文后提示写“请补充‘因＿＿＿’和‘〔延期原因〕’” | `gap-note-allowed` | 无 finding | 保持无 finding；提示区允许说明缺项 |
| `延期原因：＿＿＿＿＿＿`、字段表中的同类空位 | `draft-body` | 无 finding | 保持无 finding；可能是用户要求保留的模板/字段空白，脚本无任务意图参数 |
| `————————` | `--format` | 无 finding | 保持无 finding；不把中文长横线一概当占位或 Markdown |
| `---` | `--format` | `markdown-horizontal-rule`，low | 保持既有结果 |
| YAML frontmatter 的 `---` | `--format` | 无 finding | 保持既有豁免 |
| 明确材料原文中的两种占位 | `draft-body` | 当前新形态因漏检而无 finding | 新规则应在明确原文边界内豁免 |
| 普通正文“申请理由写为‘因＿＿＿，现申请延期’” | `draft-body` | 无 finding | 应报；引号本身不等于材料原文保护 |

`scan()` 与 CLI 对全部 probe 输出一致。现有回归 `maintenance.tests.test_placeholder_blind_spot_fix` 及横线、frontmatter、提示区三项定向测试共 7 项通过，说明上述结论是新增形态盲点，不是既有断言失败。

正向对照 `因[具体延期原因]，现申请延期。` 当前会报 medium `unfinished-placeholder`，CLI 退出 1。把它写成 `材料原文：“因[具体延期原因]，现申请延期。”` 后，`draft-body` 仍报，`review-only` 才因通用引文豁免不报。这证明新规则若直接加入正文阶段，必须同时增加仅限新 label 的明确原文保护，不能假定 `draft-body` 已自动保护引文。

## 最小补丁草案

建议把新规则放进 `DRAFT_BODY_PATTERNS`，只在 `draft-body` 和 `gap-note-allowed` 的正文区启用，不扩写通用占位符词典：

```python
DRAFT_BODY_PATTERNS: list[PatternSpec] = [
    (
        "medium",
        "unfinished-reason-placeholder",
        r"(?:(?:因|由于|鉴于)\s*[＿_]{3,}|"
        r"〔[^〕\n]{0,12}(?:原因|事由|理由)〕)"
        r"(?=\s*[，,；;])",
        "交付正文不应以空白线或字段名代替申请缘由；缺项改为正文外提示。",
    ),
    # 原有三条 DRAFT_BODY_PATTERNS ……
]
```

句法限制有四个：下划线前须有 `因/由于/鉴于`；至少连续 3 个半角或全角下划线；六角括号内须有 `原因/事由/理由`；两种形态后须接逗号或分号。这样不会命中字段式 `延期原因：＿＿＿`、空白签名栏、中文长横线或 Markdown 横线。

为保护材料明确引用，复用现有 `SOURCE_EXCERPT_PREFIX_PATTERN`、`quoted_spans_by_line()` 和 `inside_spans()`，只对这个新规则增加窄例外。不要把所有引号都豁免，否则普通正文用引号包装占位即可绕过检查。示意补丁：

```python
def is_explicit_source_quote(
    source: ScanSource,
    line_index: int,
    line: str,
    start: int,
    end: int,
) -> bool:
    prefix = SOURCE_EXCERPT_PREFIX_PATTERN.match(line)
    return bool(
        prefix
        and start >= prefix.end()
        and inside_spans(source.quoted_spans[line_index], start, end)
    )

# plain_line_findings() 的 match 循环中，inline-code 判断之后：
if label == "unfinished-reason-placeholder" and is_explicit_source_quote(
    source, line_index, line, match.start(), match.end()
):
    continue
```

独立 label 使引用豁免只作用于这两个新形态，不改变已有 `unfinished-placeholder` 对方括号、X 和日期占位的行为，也无需修改 `PatternSpec` 或引入专用扫描器。

## 必要回归

新增一个小测试类即可，至少固定：

1. 两个正文漏检样例在 `draft-body` 和正文部分的 `gap-note-allowed` 均为 medium finding，严格 CLI 退出 1；
2. 同字面只在标准 `文后提示` 区时不报；
3. 模板字段/表格空位、`————————`、ASCII `---` 及 YAML frontmatter 维持上述边界；
4. `材料原文：“……”`、`材料原句：“……”` 中不报，而未标为材料原文的普通引号仍报；
5. Python API 和 CLI 对相同文本给出一致 finding。

若希望支持“材料原文：”后另起一行的逐字片段，应另行复用并补齐现有跨行来源摘录判定；本次不要仅凭上一行前缀吞掉下一行，因为边界结束位置不明确，容易使后续正文逃逸。本原子只需覆盖明确前缀与同一行引号包围的材料原文。

## 本次验证

```text
python chinese-official-writing/scripts/prose_lint.py --delivery-mode draft-body --structure --format --json --strict --fail-on medium -
# 两个漏检样例均输出 []，EXIT=0

python -m unittest maintenance.tests.test_placeholder_blind_spot_fix maintenance.tests.test_review_regressions.ProseLintCliTests.test_markdown_horizontal_rule_is_format_finding maintenance.tests.test_review_regressions.ProseLintCliTests.test_yaml_frontmatter_delimiters_are_not_horizontal_rule_findings maintenance.tests.test_review_regressions.ProseLintCliTests.test_cli_postscript_exempts_body_risks_and_retains_identity_checks
# Ran 7 tests ... OK
```

诊断基线为 `f375e0478f86c94b7519ab5193e3394fe4cd4607`；脚本 SHA-256 为 `58D31397327F75BFF1C1ADDBDBA870768A489E39C2802EF12D5B5DF770BAC294`。本次未改 canonical 脚本或测试。
