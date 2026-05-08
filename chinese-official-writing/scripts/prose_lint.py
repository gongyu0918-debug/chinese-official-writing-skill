#!/usr/bin/env python3
"""Warn about AI-flavor, side-commentary, and casual phrasing in Chinese official drafts.

The script reports risks only. It does not rewrite text.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


@dataclass
class Finding:
    path: str
    line: int
    severity: str
    label: str
    match: str
    excerpt: str


PATTERNS: list[tuple[str, str, str, str]] = [
    ("high", "paired-summary", r"不是[^。；;\n]{0,80}而是", "改为直接肯定结论，避免二元包装。"),
    ("high", "paired-summary", r"不仅[^。；;\n]{0,80}还", "拆成具体事实或只保留关键判断。"),
    ("high", "paired-summary", r"不但[^。；;\n]{0,80}而且", "拆成具体事实或只保留关键判断。"),
    ("high", "paired-summary", r"既[^。；;\n]{0,80}又", "改为具体并列事项，避免套话。"),
    ("high", "paired-summary", r"一方面[^。；;\n]{0,100}另一方面", "改为按业务或数据自然分段。"),
    ("high", "side-commentary", r"本方案重点说明", "删除写作说明，改成方案正文判断。"),
    ("high", "side-commentary", r"重点说明\s*Token\s*用在哪里", "改为年度调用需求来源描述。"),
    ("medium", "side-commentary", r"以下(直接)?列出", "改为正文承接，不写提示语。"),
    ("medium", "side-commentary", r"本文将从", "改为直接进入结论或事实。"),
    ("medium", "side-commentary", r"本节主要(介绍|说明)", "改为正文判断。"),
    ("medium", "side-commentary", r"需要指出的是", "保留实质内容，删除提示语。"),
    ("medium", "side-commentary", r"值得注意的是", "保留实质内容，删除提示语。"),
    ("medium", "side-commentary", r"为了便于理解", "正式文稿中通常不需要解释腔。"),
    ("medium", "casual", r"租赁方式更稳[，,、]?\s*也更省", "改为成本和服务保障更具确定性。"),
    ("medium", "casual", r"用不完", "改为阶段性资源余量或资源利用率。"),
    ("medium", "casual", r"AI味", "改为表述偏泛或判断不够具体。"),
    ("low", "empty-filler", r"全面赋能", "确认是否有具体机制支撑。"),
    ("low", "empty-filler", r"充分发挥", "确认后文是否说明发挥方式。"),
    ("low", "empty-filler", r"不断提升", "确认是否有具体对象或目标。"),
    ("low", "template-phrase", r"形成一批", "确认是否有明确对象、数量或结果形态。"),
    ("low", "template-phrase", r"重点任务包括", "避免用一个总括句承接长清单，改为分项任务条款。"),
    ("low", "template-phrase", r"保障措施包括", "避免泛化清单，改为组织、资金、督导、责任等具体措施。"),
    ("low", "template-phrase", r"总体看", "确认是否只是过渡填充；可直接写判断。"),
    ("medium", "ai-compute-vague", r"先进算力", "算力文件中应补充GPU/服务器/Token/并发/SLA等可验收指标。"),
    ("medium", "ai-compute-vague", r"强大平台", "补充调度、监控、隔离、计量、运维等具体平台能力。"),
    ("medium", "ai-compute-vague", r"成本更低", "补充比较周期、需求假设和成本项目。"),
    ("medium", "ai-compute-vague", r"满足未来发展需要", "补充用户、Token、并发、模型升级或智能体工作流依据。"),
]

REPEAT_TERMS: dict[str, int] = {
    "口径": 4,
    "边界": 4,
    "底座": 6,
    "闭环": 4,
    "赋能": 3,
    "生态": 4,
    "抓手": 3,
    "矩阵": 3,
}


def read_docx(path: Path) -> str:
    pieces: list[str] = []
    xml_names = (
        "word/document.xml",
        "word/header1.xml",
        "word/header2.xml",
        "word/header3.xml",
        "word/footer1.xml",
        "word/footer2.xml",
        "word/footer3.xml",
        "word/footnotes.xml",
        "word/endnotes.xml",
        "word/comments.xml",
    )
    with zipfile.ZipFile(path) as zf:
        for name in xml_names:
            if name not in zf.namelist():
                continue
            root = ElementTree.fromstring(zf.read(name))
            for elem in root.iter():
                tag = elem.tag.rsplit("}", 1)[-1]
                if tag == "t" and elem.text:
                    pieces.append(elem.text)
                elif tag in {"p", "br"}:
                    pieces.append("\n")
                elif tag == "tab":
                    pieces.append("\t")
    return "".join(pieces)


def read_text(path_arg: str, encoding: str | None) -> tuple[str, str]:
    if path_arg == "-":
        return "<stdin>", sys.stdin.read()

    path = Path(path_arg)
    if path.suffix.lower() == ".docx":
        return str(path), read_docx(path)

    raw = path.read_bytes()
    encodings = [encoding] if encoding else ["utf-8-sig", "utf-8", "gb18030"]
    for enc in encodings:
        if not enc:
            continue
        try:
            return str(path), raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return str(path), raw.decode(encodings[-1], errors="replace")


def excerpt(line: str, start: int, end: int) -> str:
    left = max(0, start - 28)
    right = min(len(line), end + 28)
    value = line[left:right].strip()
    return re.sub(r"\s+", " ", value)


def scan(path_label: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines() or [text]

    compiled = [(severity, label, re.compile(pattern), advice) for severity, label, pattern, advice in PATTERNS]
    for line_no, line in enumerate(lines, start=1):
        for severity, label, regex, advice in compiled:
            for match in regex.finditer(line):
                findings.append(
                    Finding(
                        path=path_label,
                        line=line_no,
                        severity=severity,
                        label=label,
                        match=match.group(0),
                        excerpt=f"{excerpt(line, match.start(), match.end())} | {advice}",
                    )
                )

    for term, threshold in REPEAT_TERMS.items():
        count = text.count(term)
        if count >= threshold:
            findings.append(
                Finding(
                    path=path_label,
                    line=1,
                    severity="low",
                    label="term-overuse",
                    match=term,
                    excerpt=f"`{term}` appears {count} times; consider replacing some occurrences with concrete nouns.",
                )
            )

    return findings


def print_text(findings: Iterable[Finding]) -> None:
    for item in findings:
        print(f"{item.path}:{item.line}: {item.severity}: {item.label}: {item.match}")
        print(f"  {item.excerpt}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Warn about Chinese official-writing prose risks.")
    parser.add_argument("files", nargs="+", help="Text/Markdown/DOCX files to scan, or '-' for stdin.")
    parser.add_argument("--encoding", help="Encoding for plain-text files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON findings.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when findings exist.")
    args = parser.parse_args(argv)

    all_findings: list[Finding] = []
    for file_arg in args.files:
        path_label, text = read_text(file_arg, args.encoding)
        all_findings.extend(scan(path_label, text))

    if args.json:
        print(json.dumps([asdict(item) for item in all_findings], ensure_ascii=False, indent=2))
    else:
        print_text(all_findings)
        if not all_findings:
            print("No prose risks found.")

    return 1 if args.strict and all_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
