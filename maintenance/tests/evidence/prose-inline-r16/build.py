"""Build only the reviewed F03 prose-lint prototype outside the frozen package."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "output/reference-integration-r16/candidate/scripts/prose_lint.py"
OUT = ROOT / "output/prose-inline-r16"
TARGET = OUT / "candidate/scripts/prose_lint.py"
SOURCE_SHA256 = "e843ddb35ec19653fe702e09ffc9e2e962113dcd015ae51c7547f3026ed3c4b8"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError("Expected exactly one reviewed patch anchor")
    return text.replace(old, new, 1)


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source no longer matches the fully reviewed candidate")
    original = source_bytes.decode("utf-8")
    candidate = replace_once(
        original,
        'def inside_inline_code(line: str, start: int, end: int) -> bool:\n'
        '    """匹配内容完全位于 Markdown 行内代码范围时返回 True。"""\n',
        'def inline_code_spans(line: str) -> list[tuple[int, int]]:\n'
        '    """返回 Markdown 行内代码范围，供普通豁免和交付残留检查共用。"""\n',
    )
    candidate = replace_once(
        candidate,
        '    return any(left <= start and end <= right for left, right in spans)\n\n\n'
        'def quoted_spans_by_line',
        '    return spans\n\n\n'
        'def inside_inline_code(line: str, start: int, end: int) -> bool:\n'
        '    """匹配内容完全位于 Markdown 行内代码范围时返回 True。"""\n'
        '    return any(left <= start and end <= right for left, right in inline_code_spans(line))\n\n\n'
        'def quoted_spans_by_line',
    )
    candidate = replace_once(
        candidate,
        '    """完成正文逐行扫描；不承担正文外复核和全文统计。"""\n\n'
        '    findings: list[Finding] = []\n'
        '    in_fence = False\n',
        '    """完成正文逐行扫描；不承担正文外复核和全文统计。"""\n\n'
        '    findings: list[Finding] = []\n'
        '    inline_patterns = pattern_sets.delivery_absolute + [\n'
        '        pattern for pattern in pattern_sets.primary if pattern[1] in DELIVERY_BODY_ONLY_LABELS\n'
        '    ]\n'
        '    in_fence = False\n',
    )
    candidate = replace_once(
        candidate,
        '                pattern_sets.primary,\n'
        '                delivery_mode,\n'
        '            )\n'
        '        )\n'
        '    return findings\n\n\n'
        'def delivery_section_findings',
        '                pattern_sets.primary,\n'
        '                delivery_mode,\n'
        '            )\n'
        '        )\n'
        '        if delivery_mode in {"draft-body", "gap-note-allowed"} and line_index < len(source.body_only_lines):\n'
        '            # 行内代码保留普通技术内容豁免；已知身份、推理和制作残留仍给出复核线索。\n'
        '            for left, right in inline_code_spans(line):\n'
        '                findings.extend(\n'
        '                    fence_findings(path_label, line_no, line[left + 1 : right - 1], inline_patterns)\n'
        '                )\n'
        '    return findings\n\n\n'
        'def delivery_section_findings',
    )
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, TARGET)
    TARGET.write_text(candidate, encoding="utf-8", newline="\n")
    manifest = {
        "source": str(SOURCE), "source_sha256": SOURCE_SHA256,
        "target": str(TARGET), "target_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
        "source_unchanged": SOURCE.read_bytes() == source_bytes,
        "candidate_files": [str(path.relative_to(OUT / "candidate"))
                            for path in sorted((OUT / "candidate").rglob("*")) if path.is_file()],
    }
    (OUT / "build.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "candidate.diff").write_text("".join(difflib.unified_diff(
        original.splitlines(keepends=True), candidate.splitlines(keepends=True),
        fromfile="reviewed/scripts/prose_lint.py", tofile="candidate/scripts/prose_lint.py")), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
