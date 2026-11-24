#!/usr/bin/env python3
"""Zero-dependency deterministic GB/T 9704-2012 Chinese official document DOCX builder.

Uses Python 3 standard library only (zipfile + OpenXML). Supports:
- ordinary          : Standard office/internal official document (A4, GB/T 9704 fonts/spacing, no redhead)
- formal-preprinted : Formal GB/T 9704 layout reserving space for preprinted red letterhead paper, mirrored margins, odd/even page numbers
- formal-digital    : Full electronic redhead GB/T 9704 layout (only when explicitly requested)
- minutes           : Official meeting minutes layout with header banner and divider line
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from xml.sax.saxutils import escape as xml_escape
import zipfile

# Resolve sibling prose_lint for post-build verification
sys.path.insert(0, str(Path(__file__).resolve().parent))
import math
from prose_lint import read_docx, scan  # noqa: E402

PROFILES = ("ordinary", "formal-preprinted", "formal-digital", "minutes")
SEAL_MODES = ("stamped", "unstamped")
PAGE_NUMBER_MODES = ("auto", "standard", "center", "none")

# Exact GB/T 9704-2012 dimensions in twips (1 mm = 1440 / 25.4 twips)
def mm_to_twips(mm: float) -> int:
    return round(mm * 1440.0 / 25.4)


A4_W = mm_to_twips(210.0)   # 11906
A4_H = mm_to_twips(297.0)   # 16838
M_TOP = mm_to_twips(37.0)   # 2098
M_BOT = mm_to_twips(35.0)   # 1984
M_LEFT = mm_to_twips(28.0)  # 1587 (inside/binding edge)
M_RIGHT = mm_to_twips(26.0) # 1474 (outside edge)
CONTENT_W = A4_W - M_LEFT - M_RIGHT  # 8845 dxa (156mm exact GB/T 9704 text box width)
M_FOOTER = mm_to_twips(23.0) # 1304 (~7mm below text bottom edge)
M_HEADER = mm_to_twips(15.0)

FONT_TITLE = "方正小标宋简体"
FONT_BODY = "仿宋_GB2312"
FONT_H1 = "黑体"
FONT_H2 = "楷体_GB2312"
FONT_PAGE = "宋体"
FONT_ASCII = "Times New Roman"
RED_HEX = "CC0000"

DATE_LINE_RE = re.compile(r"^\d{4}年\d{1,2}月\d{1,2}日$")
ZERO_PAD_DATE_RE = re.compile(r"20\d{2}年0[1-9]月|月0[1-9]日")
H1_RE = re.compile(r"^[一二三四五六七八九十]+、\S")
CHAPTER_RE = re.compile(r"^第[一二三四五六七八九十百]+[章节](?:\s|　|$)")
H2_RE = re.compile(r"^（[一二三四五六七八九十]+）\S")
H3_RE = re.compile(r"^\d+\.\s*\S")
H4_RE = re.compile(r"^（\d+）\S")
ARTICLE_RE = re.compile(r"^(第[一二三四五六七八九十百]+条)([\s　]+)(.+)$")
ATTENDANCE_RE = re.compile(r"^(出席|请假|列席)[：:]\s*(.+)$")
ATTACHMENT_START_RE = re.compile(r"^附件[：:]\s*(.*)$")
ATTACHMENT_CONT_RE = re.compile(r"^\d+\.\s*\S")
RECIPIENT_RE = re.compile(r"^[^。！？；\n]{1,42}[：:]$")
NON_UNIT_PREFIX_RE = re.compile(r"^(?:附件|特此|妥否|当否|以上|此复|此致|请予|一、|（一）|第[一二三四五六七八九十百]+[条章]|文后提示)")


def _rpr(
    east_asia: str,
    sz_half_pt: int,
    *,
    bold: bool = False,
    color: str | None = None,
    ascii_font: str = FONT_ASCII,
) -> str:
    b_xml = "<w:b/><w:bCs/>" if bold else ""
    c_xml = f'<w:color w:val="{color}"/>' if color else ""
    return (
        "<w:rPr>"
        f'<w:rFonts w:ascii="{xml_escape(ascii_font)}" w:hAnsi="{xml_escape(ascii_font)}" '
        f'w:eastAsia="{xml_escape(east_asia)}" w:cs="{xml_escape(ascii_font)}"/>'
        f"{b_xml}{c_xml}"
        f'<w:sz w:val="{sz_half_pt}"/><w:szCs w:val="{sz_half_pt}"/>'
        "</w:rPr>"
    )


def _run(text: str, east_asia: str, sz_half_pt: int, *, bold: bool = False, color: str | None = None) -> str:
    return f'<w:r>{_rpr(east_asia, sz_half_pt, bold=bold, color=color)}<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'


def _p(
    runs_xml: str,
    *,
    jc: str = "both",
    line_twips: int = 560,
    line_rule: str = "exact",
    before: int = 0,
    after: int = 0,
    first_line_chars: int = 0,
    left_chars: int = 0,
    right_chars: int = 0,
    hanging_chars: int = 0,
    style_id: str | None = None,
    outline_lvl: int | None = None,
    keep_next: bool = False,
    bottom_border: tuple[str, int, str] | None = None,
    top_border: tuple[str, int, str] | None = None,
) -> str:
    ppr_parts: list[str] = []
    if style_id:
        ppr_parts.append(f'<w:pStyle w:val="{xml_escape(style_id)}"/>')
    if keep_next:
        ppr_parts.append("<w:keepNext/>")
    if top_border or bottom_border:
        b_items = []
        if top_border:
            b_items.append(f'<w:top w:val="{top_border[0]}" w:sz="{top_border[1]}" w:space="4" w:color="{top_border[2]}"/>')
        if bottom_border:
            b_items.append(f'<w:bottom w:val="{bottom_border[0]}" w:sz="{bottom_border[1]}" w:space="4" w:color="{bottom_border[2]}"/>')
        ppr_parts.append(f"<w:pBdr>{''.join(b_items)}</w:pBdr>")
    ppr_parts.append(f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line_twips}" w:lineRule="{line_rule}"/>')
    ind_attrs = []
    if left_chars:
        ind_attrs.append(f'w:leftChars="{left_chars}" w:left="{round(left_chars * 3.2)}"')
    if right_chars:
        ind_attrs.append(f'w:rightChars="{right_chars}" w:right="{round(right_chars * 3.2)}"')
    if first_line_chars:
        ind_attrs.append(f'w:firstLineChars="{first_line_chars}" w:firstLine="{round(first_line_chars * 3.2)}"')
    if hanging_chars:
        ind_attrs.append(f'w:hangingChars="{hanging_chars}" w:hanging="{round(hanging_chars * 3.2)}"')
    elif left_chars and not first_line_chars:
        ind_attrs.append('w:firstLineChars="0" w:firstLine="0"')
    if ind_attrs:
        ppr_parts.append(f"<w:ind {' '.join(ind_attrs)}/>")
    ppr_parts.append(f'<w:jc w:val="{jc}"/>')
    if outline_lvl is not None:
        ppr_parts.append(f'<w:outlineLvl w:val="{outline_lvl}"/>')
    return f"<w:p><w:pPr>{''.join(ppr_parts)}</w:pPr>{runs_xml}</w:p>"


def _blank_p(line_twips: int = 560) -> str:
    return _p("", jc="left", line_twips=line_twips)


def _strip_md_noise(line: str) -> str:
    s = line.strip().lstrip("\u3000")
    # Strip accidental Markdown heading markers or outer bold markers
    s = re.sub(r"^#{1,6}\s+", "", s)
    if s.startswith("**") and s.endswith("**") and len(s) > 4 and "**" not in s[2:-2]:
        s = s[2:-2].strip()
    return s.lstrip("\u3000")


def _wrap_trapezoid_title(title: str, max_chars_per_line: float = 19.0) -> list[str]:
    """按 GB/T 9704 §7.3.1 将超长标题智能排布为梯形/菱形多行，不劈词、不留孤字。"""
    t = title.strip()
    w = _display_width_chars(t)
    if w <= max_chars_per_line or "\n" in t:
        return [seg.strip() for seg in t.splitlines() if seg.strip()] or [t]

    # Preferred break triggers (break right AFTER these boundary phrases, or right BEFORE suffixes)
    after_tokens = ("关于", "开展", "印发", "批准", "加强", "推进", "做好", "进一步", "全面", "加快", "全市", "全省", "市级", "省级", "以及", "有关", "专项", "工作", "建设", "管理", "运营")
    before_tokens = ("的通知", "的请示", "的报告", "的意见", "的批复", "的通报", "的决定", "的办法", "的方案", "的函", "的通告", "的公告", "的纪要", "实施", "专项", "安全", "管理", "采购", "经费", "建设", "推进")
    protected_suffix = re.search(r"的(?:通知|请示|报告|意见|批复|通报|决定|办法|方案|通告|公告|纪要|函|说明|预案|细则|规程|规定)$", t)
    protect_start = protected_suffix.start() if protected_suffix else len(t)

    n_lines = 2 if w <= max_chars_per_line * 1.95 else 3
    lines: list[str] = []
    rem = t
    for seg_idx in range(n_lines - 1):
        rem_w = _display_width_chars(rem)
        left_lines = n_lines - seg_idx
        if rem_w <= max_chars_per_line:
            break
        # Target slightly wider upper line for balanced trapezoid (e.g., 55% / 45% for 2 lines)
        target_w = min(max_chars_per_line, rem_w * (0.56 if left_lines == 2 else 0.36))
        best_pos = None
        best_score = -1e9
        cur_w = 0.0
        for pos in range(1, len(rem)):
            cur_w += 0.5 if ord(rem[pos - 1]) < 128 else 1.0
            tail_w = rem_w - cur_w
            if cur_w > max_chars_per_line or cur_w < 6.0 or tail_w < 5.0:
                continue
            # Never split inside ASCII/digit run (e.g. 2026年, 120TB) or right before 年/月/日
            prev_ch, next_ch = rem[pos - 1], rem[pos]
            if prev_ch.isalnum() and prev_ch.isascii() and (next_ch.isalnum() and next_ch.isascii() or next_ch in "年月日%"):
                continue
            # Never split inside the protected final "的+文种" suffix (splitting right BEFORE "的" is bad too unless unavoidable)
            if seg_idx == n_lines - 2 and pos > (protect_start - (len(t) - len(rem))) and pos < len(rem):
                continue
            score = -abs(cur_w - target_w) * 2.0
            # Prefer trapezoid (upper >= lower) slightly
            if left_lines == 2 and cur_w >= tail_w:
                score += 1.5
            # Semantic boundary bonuses
            left_part, right_part = rem[:pos], rem[pos:]
            if any(left_part.endswith(tok) for tok in after_tokens):
                score += 3.5
            if any(right_part.startswith(tok) for tok in before_tokens):
                score += 3.0
            if prev_ch in "、，》）”":
                score += 4.0
            if next_ch in "《（“":
                score += 3.5
            if next_ch == "的":
                score -= 2.5
            if score > best_score:
                best_score = score
                best_pos = pos
        if best_pos is None:
            break
        lines.append(rem[:best_pos])
        rem = rem[best_pos:]
    lines.append(rem)
    return lines


def parse_document(raw_text: str, explicit_title: str | None = None) -> dict:
    """Parse plain-text Chinese official document into structured elements."""
    raw_lines = [line.rstrip() for line in raw_text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    non_empty = [_strip_md_noise(l) for l in raw_lines if l.strip()]
    if not non_empty:
        raise ValueError("输入文本为空，无法生成 DOCX")

    warnings: list[str] = []
    idx = 0
    if explicit_title:
        title = explicit_title.strip()
        if non_empty and non_empty[0] == title:
            idx = 1
    else:
        title = non_empty[0]
        idx = 1

    # Detect optional trailing sign-off unit + date (and optional postscript excluded or kept)
    sign_date: str | None = None
    sign_unit: str | None = None
    end = len(non_empty)

    # Check if last line is a Chinese date
    if end > idx and DATE_LINE_RE.match(non_empty[end - 1]):
        sign_date = non_empty[end - 1]
        if ZERO_PAD_DATE_RE.search(sign_date):
            warnings.append(f"成文日期含补零（{sign_date}），国标规范一般不补零")
        end -= 1
        if end > idx:
            cand = non_empty[end - 1]
            if (
                2 <= len(cand) <= 32
                and not re.search(r"[。！？!?；;：:,，]", cand)
                and not NON_UNIT_PREFIX_RE.match(cand)
            ):
                sign_unit = cand
                end -= 1

    # Detect recipient line right after title
    recipient: str | None = None
    if idx < end and RECIPIENT_RE.match(non_empty[idx]) and not ATTACHMENT_START_RE.match(non_empty[idx]):
        recipient = non_empty[idx]
        idx += 1

    # Separate body items and optional trailing attachment block
    body_items: list[tuple[str, str]] = []
    attachments: list[str] = []
    in_attachments = False

    for line in non_empty[idx:end]:
        if in_attachments:
            is_new_section = (
                CHAPTER_RE.match(line)
                or H1_RE.match(line)
                or H2_RE.match(line)
                or ARTICLE_RE.match(line)
                or ATTENDANCE_RE.match(line)
            )
            if ATTACHMENT_CONT_RE.match(line) or (not is_new_section and len(line) <= 48 and not line.endswith("。")):
                attachments.append(line)
                continue
            in_attachments = False
        m_att = ATTACHMENT_START_RE.match(line)
        if m_att:
            in_attachments = True
            attachments.append(line)
            continue

        if CHAPTER_RE.match(line):
            body_items.append(("chapter", line))
        elif H1_RE.match(line) and len(line) <= 42 and not line.endswith("。"):
            body_items.append(("h1", line))
        elif H2_RE.match(line):
            body_items.append(("h2", line))
        elif H3_RE.match(line):
            body_items.append(("h3", line))
        elif H4_RE.match(line):
            body_items.append(("h4", line))
        elif ARTICLE_RE.match(line):
            body_items.append(("article", line))
        elif ATTENDANCE_RE.match(line):
            body_items.append(("attendance", line))
        else:
            body_items.append(("body", line))

    return {
        "title": title,
        "recipient": recipient,
        "body_items": body_items,
        "attachments": attachments,
        "sign_unit": sign_unit,
        "sign_date": sign_date,
        "warnings": warnings,
    }


def _render_inline_heading_or_body(kind: str, text: str) -> str:
    """Render GB/T 9704 headings and paragraphs accurately using native Heading1-4 styles."""
    if kind == "chapter":
        return _p(_run(text, FONT_H1, 32), jc="center", before=120, after=80, style_id="Heading1", outline_lvl=0, keep_next=True)
    if kind == "h1":
        return _p(_run(text, FONT_H1, 32), first_line_chars=200, style_id="Heading1", outline_lvl=0, keep_next=True)
    if kind == "h2":
        # Standalone H2 (no period inside) vs inline-lead H2 ("（一）某某。正文……")
        period = text.find("。")
        if period != -1 and period < len(text) - 1:
            lead, rest = text[: period + 1], text[period + 1 :]
            runs = _run(lead, FONT_H2, 32) + _run(rest, FONT_BODY, 32)
            return _p(runs, first_line_chars=200, style_id="Heading2", outline_lvl=1)
        return _p(_run(text, FONT_H2, 32), first_line_chars=200, style_id="Heading2", outline_lvl=1, keep_next=True)
    if kind == "h3":
        period = text.find("。")
        if period != -1 and period < len(text) - 1:
            lead, rest = text[: period + 1], text[period + 1 :]
            runs = _run(lead, FONT_BODY, 32, bold=True) + _run(rest, FONT_BODY, 32)
            return _p(runs, first_line_chars=200, style_id="Heading3", outline_lvl=2)
        return _p(_run(text, FONT_BODY, 32, bold=True), first_line_chars=200, style_id="Heading3", outline_lvl=2, keep_next=True)
    if kind == "h4":
        period = text.find("。")
        if period != -1 and period < len(text) - 1:
            lead, rest = text[: period + 1], text[period + 1 :]
            runs = _run(lead, FONT_BODY, 32) + _run(rest, FONT_BODY, 32)
            return _p(runs, first_line_chars=200, style_id="Heading4", outline_lvl=3)
        return _p(_run(text, FONT_BODY, 32), first_line_chars=200, style_id="Heading4", outline_lvl=3)
    if kind == "article":
        m = ARTICLE_RE.match(text)
        if m:
            runs = _run(m.group(1) + "　", FONT_BODY, 32, bold=True) + _run(m.group(3), FONT_BODY, 32)
            return _p(runs, first_line_chars=200)
    if kind == "attendance":
        m = ATTENDANCE_RE.match(text)
        if m:
            runs = _run(f"{m.group(1)}：", FONT_H1, 32) + _run(m.group(2), FONT_BODY, 32)
            return _p(runs, left_chars=500, hanging_chars=300)
    return _p(_run(text, FONT_BODY, 32), first_line_chars=200)


def _display_width_chars(s: str) -> float:
    w = 0.0
    for ch in s:
        w += 0.5 if ord(ch) < 128 else 1.0
    return w


def _build_footer_xml(align: str, *, right_chars: int = 0, left_chars: int = 0) -> str:
    rpr = _rpr(FONT_PAGE, 28)
    page_field = (
        f'<w:r>{rpr}<w:t xml:space="preserve">— </w:t></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r>{rpr}<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r>{rpr}<w:t>1</w:t></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>'
        f'<w:r>{rpr}<w:t xml:space="preserve"> —</w:t></w:r>'
    )
    p_xml = _p(page_field, jc=align, line_twips=360, left_chars=left_chars, right_chars=right_chars)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"{p_xml}"
        "</w:ftr>"
    )


def build_docx(
    raw_text: str,
    output_path: Path,
    *,
    profile: str = "ordinary",
    title: str | None = None,
    org: str | None = None,
    doc_no: str | None = None,
    signer: str | None = None,
    cc: str | None = None,
    print_org: str | None = None,
    print_date: str | None = None,
    seal_mode: str = "stamped",
    page_numbers: str = "auto",
    letterhead_reserve_mm: float = 72.0,
    overwrite: bool = False,
) -> dict:
    if profile not in PROFILES:
        raise ValueError(f"unsupported profile: {profile}")
    if seal_mode not in SEAL_MODES:
        raise ValueError(f"unsupported seal_mode: {seal_mode}")
    if page_numbers not in PAGE_NUMBER_MODES:
        raise ValueError(f"unsupported page_numbers: {page_numbers}")
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"目标文件已存在（如需覆盖请显式传 --overwrite）: {output_path}")

    parsed = parse_document(raw_text, explicit_title=title)
    warnings: list[str] = list(parsed["warnings"])

    if doc_no and profile in {"formal-preprinted", "formal-digital"}:
        if "〔" not in doc_no or "〕" not in doc_no:
            warnings.append(f"发文字号“{doc_no}”未使用六角括号〔〕，建议按国标改用如“××发〔2026〕1号”")
    if print_date and ZERO_PAD_DATE_RE.search(print_date):
        warnings.append(f"印发日期含补零（{print_date}），国标规范一般不补零")

    effective_pn = page_numbers
    if effective_pn == "auto":
        effective_pn = "standard" if profile in {"formal-preprinted", "formal-digital"} else "center"
    is_formal = profile in {"formal-preprinted", "formal-digital"}

    blocks: list[str] = []

    # 1. Letterhead / Header zone
    if profile == "formal-preprinted":
        extra_mm = max(letterhead_reserve_mm - 37.0, 0.0)
        if extra_mm > 0:
            blocks.append(_p("", jc="left", line_twips=mm_to_twips(extra_mm)))
        if doc_no and signer:
            # Upward doc: doc_no left-1-char, signer right-1-char on same line using borderless 2-col table
            blocks.append(_doc_no_signer_table(doc_no, signer))
        elif doc_no:
            blocks.append(_p(_run(doc_no, FONT_BODY, 32), jc="center", after=120))
        blocks.append(_blank_p())
        blocks.append(_blank_p())
    elif profile == "formal-digital":
        banner_text = (org or parsed["sign_unit"] or "").strip()
        if banner_text:
            blocks.append(
                _p(_run(banner_text, FONT_TITLE, 72, color=RED_HEX), jc="center", line_twips=860, before=100, after=240)
            )
        if doc_no and signer:
            blocks.append(_doc_no_signer_table(doc_no, signer, red_rule=False))
            blocks.append(_p("", jc="left", line_twips=60, after=80, bottom_border=("single", 18, RED_HEX)))
        elif doc_no:
            blocks.append(
                _p(_run(doc_no, FONT_BODY, 32), jc="center", after=160, bottom_border=("single", 18, RED_HEX))
            )
        else:
            blocks.append(_p("", jc="left", line_twips=120, bottom_border=("single", 18, RED_HEX)))
        blocks.append(_blank_p())
        blocks.append(_blank_p())
    elif profile == "minutes":
        if org:
            blocks.append(_p(_run(org, FONT_TITLE, 56, color=RED_HEX), jc="center", line_twips=720, after=120))
        if doc_no:
            blocks.append(_p(_run(doc_no, FONT_BODY, 32), jc="center", after=120, bottom_border=("single", 12, RED_HEX)))
        elif org:
            blocks.append(_p("", jc="left", line_twips=80, bottom_border=("single", 12, RED_HEX)))
        blocks.append(_blank_p())

    # 2. Main Title (独立样式，不入目录，二号方正小标宋简体，梯形/菱形智能断行，居中不加粗，固定行距31磅=620 twips)
    title_lines = _wrap_trapezoid_title(parsed["title"])
    if not (profile == "minutes" and org and org.strip() == parsed["title"].strip()):
        title_runs_parts: list[str] = []
        for idx_t, t_seg in enumerate(title_lines):
            if idx_t > 0:
                title_runs_parts.append(f'<w:r>{_rpr(FONT_TITLE, 44)}<w:br/></w:r>')
            title_runs_parts.append(_run(t_seg, FONT_TITLE, 44))
        blocks.append(
            _p(
                "".join(title_runs_parts),
                jc="center",
                line_twips=620,
                before=0,
                after=0,
                style_id="GongwenTitle",
                keep_next=True,
            )
        )
        blocks.append(_blank_p())

    # 3. Main Recipient
    if parsed["recipient"]:
        blocks.append(_p(_run(parsed["recipient"], FONT_BODY, 32), jc="left", keep_next=True))

    # 4. Body Paragraphs & Headings
    heading_count = 0
    for kind, text in parsed["body_items"]:
        if kind in {"chapter", "h1", "h2", "h3", "h4"}:
            heading_count += 1
        blocks.append(_render_inline_heading_or_body(kind, text))

    # 5. Attachments Note (国标：正文下空一行，左空二字，多件悬挂对齐，keepNext 防跨页劈裂)
    if parsed["attachments"]:
        blocks.append(_blank_p())
        att_total = len(parsed["attachments"])
        for idx_a, att_line in enumerate(parsed["attachments"]):
            kn = idx_a < att_total - 1
            if idx_a == 0:
                blocks.append(_p(_run(att_line, FONT_BODY, 32), left_chars=500, hanging_chars=300, keep_next=kn))
            else:
                blocks.append(_p(_run(att_line, FONT_BODY, 32), left_chars=500, keep_next=kn))

    # 6. Sign-off Unit & Date (sign_unit 绑定 keepNext，确保单位与成文日期绝不跨页拆散)
    sign_unit = parsed["sign_unit"]
    sign_date = parsed["sign_date"]
    if sign_unit or sign_date:
        if is_formal and seal_mode == "unstamped":
            blocks.append(_blank_p())
            if sign_unit and sign_date:
                uw = _display_width_chars(sign_unit)
                dw = _display_width_chars(sign_date)
                if uw >= dw + 2.0:
                    unit_rc = 200
                    date_rc = max(round((uw - dw - 2.0) * 100) + 200, 0)
                else:
                    date_rc = 200
                    unit_rc = round((dw - uw + 2.0) * 100) + 200
                blocks.append(_p(_run(sign_unit, FONT_BODY, 32), jc="right", right_chars=unit_rc, keep_next=True))
                blocks.append(_p(_run(sign_date, FONT_BODY, 32), jc="right", right_chars=date_rc))
            elif sign_unit:
                blocks.append(_p(_run(sign_unit, FONT_BODY, 32), jc="right", right_chars=200))
            elif sign_date:
                blocks.append(_p(_run(sign_date, FONT_BODY, 32), jc="right", right_chars=200))
        elif is_formal and seal_mode == "stamped":
            blocks.append(_blank_p())
            blocks.append(_blank_p())
            if sign_unit and sign_date:
                uw = _display_width_chars(sign_unit)
                dw = _display_width_chars(sign_date)
                date_rc = 400
                # Center sign_unit directly above sign_date
                unit_rc = max(round(date_rc + (dw - uw) * 50), 0)
                blocks.append(_p(_run(sign_unit, FONT_BODY, 32), jc="right", right_chars=unit_rc, keep_next=True))
                blocks.append(_p(_run(sign_date, FONT_BODY, 32), jc="right", right_chars=date_rc))
            elif sign_unit:
                blocks.append(_p(_run(sign_unit, FONT_BODY, 32), jc="right", right_chars=400))
            elif sign_date:
                blocks.append(_p(_run(sign_date, FONT_BODY, 32), jc="right", right_chars=400))
        else:
            # ordinary / minutes: 2 blank lines, unit right-2-chars, date centered below
            blocks.append(_blank_p())
            blocks.append(_blank_p())
            if sign_unit and sign_date:
                uw = _display_width_chars(sign_unit)
                dw = _display_width_chars(sign_date)
                unit_rc = 200
                date_rc = max(round(unit_rc + (uw - dw) * 50), 0)
                blocks.append(_p(_run(sign_unit, FONT_BODY, 32), jc="right", right_chars=unit_rc, keep_next=True))
                blocks.append(_p(_run(sign_date, FONT_BODY, 32), jc="right", right_chars=date_rc))
            elif sign_unit:
                blocks.append(_p(_run(sign_unit, FONT_BODY, 32), jc="right", right_chars=200))
            elif sign_date:
                blocks.append(_p(_run(sign_date, FONT_BODY, 32), jc="right", right_chars=200))

    # 7. Optional Colophon (版记，四号仿宋，156mm 定宽表格保障 Word/WPS/QuickLook 一致渲染)
    if cc or print_org or print_date:
        blocks.append(_blank_p())
        p_org = print_org or org or sign_unit or ""
        p_date = print_date or sign_date or ""
        blocks.append(_colophon_table(cc=cc, print_org=p_org, print_date=p_date))

    # Section properties (A4, GB/T 9704 margins, footers)
    footer_refs = ""
    if effective_pn == "standard":
        footer_refs = (
            '<w:footerReference w:type="default" r:id="rIdFooterOdd"/>'
            '<w:footerReference w:type="even" r:id="rIdFooterEven"/>'
        )
    elif effective_pn == "center":
        footer_refs = '<w:footerReference w:type="default" r:id="rIdFooterCenter"/>'

    sect_pr = (
        "<w:sectPr>"
        f"{footer_refs}"
        f'<w:pgSz w:w="{A4_W}" w:h="{A4_H}"/>'
        f'<w:pgMar w:top="{M_TOP}" w:right="{M_RIGHT}" w:bottom="{M_BOT}" w:left="{M_LEFT}" '
        f'w:header="{M_HEADER}" w:footer="{M_FOOTER}" w:gutter="0"/>'
        '<w:docGrid w:type="lines" w:linePitch="560" w:charSpace="0"/>'
        "</w:sectPr>"
    )

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{''.join(blocks)}{sect_pr}</w:body>"
        "</w:document>"
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:docDefaults><w:rPrDefault>"
        f"{_rpr(FONT_BODY, 32)}"
        "</w:rPrDefault><w:pPrDefault><w:pPr>"
        '<w:spacing w:before="0" w:after="0" w:line="560" w:lineRule="exact"/>'
        "</w:pPr></w:pPrDefault></w:docDefaults>"
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/>'
        f"{_rpr(FONT_BODY, 32)}"
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="GongwenTitle">'
        '<w:name w:val="公文标题"/>'
        '<w:basedOn w:val="Normal"/>'
        f"{_rpr(FONT_TITLE, 44)}"
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="Heading1">'
        '<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:outlineLvl w:val="0"/></w:pPr>'
        f"{_rpr(FONT_H1, 32)}"
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="Heading2">'
        '<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:outlineLvl w:val="1"/></w:pPr>'
        f"{_rpr(FONT_H2, 32)}"
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="Heading3">'
        '<w:name w:val="heading 3"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:outlineLvl w:val="2"/></w:pPr>'
        f"{_rpr(FONT_BODY, 32, bold=True)}"
        "</w:style>"
        '<w:style w:type="paragraph" w:styleId="Heading4">'
        '<w:name w:val="heading 4"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:outlineLvl w:val="3"/></w:pPr>'
        f"{_rpr(FONT_BODY, 32)}"
        "</w:style>"
        "</w:styles>"
    )

    settings_flags = ""
    if is_formal:
        settings_flags += "<w:mirrorMargins/>"
    if effective_pn == "standard":
        settings_flags += "<w:evenAndOddHeaders/>"
    settings_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"{settings_flags}"
        "<w:compat><w:compatSetting w:name=\"compatibilityMode\" w:uri=\"http://schemas.microsoft.com/office/word\" w:val=\"15\"/></w:compat>"
        "</w:settings>"
    )

    rels_entries = [
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
        '<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>',
    ]
    ct_overrides = [
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>',
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>',
    ]
    extra_parts: dict[str, str] = {}
    if effective_pn == "standard":
        rels_entries.append('<Relationship Id="rIdFooterOdd" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer_odd.xml"/>')
        rels_entries.append('<Relationship Id="rIdFooterEven" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer_even.xml"/>')
        ct_overrides.append('<Override PartName="/word/footer_odd.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>')
        ct_overrides.append('<Override PartName="/word/footer_even.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>')
        extra_parts["word/footer_odd.xml"] = _build_footer_xml("right", right_chars=100)
        extra_parts["word/footer_even.xml"] = _build_footer_xml("left", left_chars=100)
    elif effective_pn == "center":
        rels_entries.append('<Relationship Id="rIdFooterCenter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer_center.xml"/>')
        ct_overrides.append('<Override PartName="/word/footer_center.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>')
        extra_parts["word/footer_center.xml"] = _build_footer_xml("center")

    doc_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(rels_entries)}"
        "</Relationships>"
    )
    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f"{''.join(ct_overrides)}"
        "</Types>"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml.encode("utf-8"))
        zf.writestr("_rels/.rels", root_rels_xml.encode("utf-8"))
        zf.writestr("word/_rels/document.xml.rels", doc_rels_xml.encode("utf-8"))
        zf.writestr("word/document.xml", document_xml.encode("utf-8"))
        zf.writestr("word/styles.xml", styles_xml.encode("utf-8"))
        zf.writestr("word/settings.xml", settings_xml.encode("utf-8"))
        for part_name, part_xml in extra_parts.items():
            zf.writestr(part_name, part_xml.encode("utf-8"))

    # Self-verify ZIP integrity, GB/T 9704 OpenXML compliance, pagination estimate, and prose_lint
    est_pages, tail_lines = _estimate_pagination(
        profile=profile,
        letterhead_reserve_mm=letterhead_reserve_mm,
        has_org=bool(org),
        has_doc_no=bool(doc_no),
        title_line_count=len(title_lines),
        parsed=parsed,
        has_colophon=bool(cc or print_org or print_date),
        seal_mode=seal_mode,
    )
    pagination_note = ""
    if est_pages >= 2 and 1 <= tail_lines <= 3:
        pagination_note = f"按国标22行/页粗略估算约{est_pages}页、末页余约{tail_lines}行（仅供参考，非实际渲染页数），打印前可在 Word/WPS 核对分页"

    verify_report = verify_docx(output_path, profile=profile)
    if not verify_report["zip_ok"]:
        raise OSError(f"DOCX ZIP CRC 校验失败: {verify_report.get('error')}")

    extracted = read_docx(output_path, scope="main-document")
    lint_items = scan(
        str(output_path),
        extracted,
        include_format=True,
        include_structure=True,
        delivery_mode="draft-body",
    )
    lint_labels = [item.label for item in lint_items]

    return {
        "ok": verify_report["ok"],
        "output": str(output_path.resolve()),
        "profile": profile,
        "seal_mode": seal_mode,
        "page_numbers": effective_pn,
        "mirror_margins": is_formal,
        "title": parsed["title"],
        "title_lines": title_lines,
        "body_paragraphs": len(parsed["body_items"]),
        "headings_with_outline": heading_count,
        "attachments": len(parsed["attachments"]),
        "extracted_nonws_chars": len(re.sub(r"\s+", "", extracted)),
        "estimated_pages": est_pages,
        "pages_verified": False,
        "tail_lines_on_last_page": tail_lines,
        "pagination_note": pagination_note,
        "zip_ok": verify_report["zip_ok"],
        "gbt9704_checks_passed": f"{verify_report['passed']}/{verify_report['total']}",
        "gbt9704_failed": verify_report["failed_items"],
        "lint_findings_count": len(lint_items),
        "lint_labels": lint_labels,
        "warnings": warnings,
    }


def _estimate_pagination(
    *,
    profile: str,
    letterhead_reserve_mm: float,
    has_org: bool,
    has_doc_no: bool,
    title_line_count: int,
    parsed: dict,
    has_colophon: bool,
    seal_mode: str = "stamped",
) -> tuple[int, int]:
    """按 GB/T 9704-2012 每面 22 行 × 每行 28 字估算总页数与末页行数。"""
    lines = 0
    if profile == "formal-preprinted":
        lines += max(round((letterhead_reserve_mm - 37.0) / 9.88), 0) + (1 if has_doc_no else 0) + 2
    elif profile == "formal-digital":
        lines += (3 if has_org else 0) + (1 if has_doc_no else 0) + 2
    elif profile == "minutes":
        lines += (2 if has_org else 0) + (1 if has_doc_no else 0) + 1
    lines += title_line_count + 1  # title + blank line
    if parsed["recipient"]:
        lines += max(1, math.ceil(_display_width_chars(parsed["recipient"]) / 28.0))
    for _, text in parsed["body_items"]:
        w = _display_width_chars(text) + 2.0  # first-line 2-char indent
        lines += max(1, math.ceil(w / 28.0))
    if parsed["attachments"]:
        lines += 1
        for att in parsed["attachments"]:
            lines += max(1, math.ceil((_display_width_chars(att) + 3.0) / 28.0))
    if parsed["sign_unit"] or parsed["sign_date"]:
        sign_blank = 1 if (profile in {"formal-preprinted", "formal-digital"} and seal_mode == "unstamped") else 2
        lines += sign_blank + (1 if parsed["sign_unit"] else 0) + (1 if parsed["sign_date"] else 0)
    if has_colophon:
        lines += 3
    pages = max(1, math.ceil(lines / 22.0))
    tail = lines - (pages - 1) * 22
    return pages, tail


def verify_docx(docx_path: Path, *, profile: str | None = None) -> dict:
    """确定性核验任意 .docx 文件是否符合 GB/T 9704-2012 关键 OpenXML 版式规范。"""
    if not docx_path.is_file():
        return {"ok": False, "zip_ok": False, "error": f"文件不存在: {docx_path}", "passed": 0, "total": 0, "failed_items": ["file-exists"]}

    checks: list[tuple[str, bool, str]] = []
    with zipfile.ZipFile(docx_path, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            return {"ok": False, "zip_ok": False, "error": f"ZIP CRC 损坏: {bad}", "passed": 0, "total": 1, "failed_items": ["zip-crc"]}
        names = set(zf.namelist())
        doc_xml = zf.read("word/document.xml").decode("utf-8", errors="replace") if "word/document.xml" in names else ""
        sty_xml = zf.read("word/styles.xml").decode("utf-8", errors="replace") if "word/styles.xml" in names else ""
        set_xml = zf.read("word/settings.xml").decode("utf-8", errors="replace") if "word/settings.xml" in names else ""
        all_xml = doc_xml + "\n" + sty_xml
        footer_xmls = [zf.read(n).decode("utf-8", errors="replace") for n in names if "footer" in n.lower()]
        footer_all = "\n".join(footer_xmls)

        checks.append(("a4-page-size", f'w:w="{A4_W}"' in doc_xml and f'w:h="{A4_H}"' in doc_xml, "A4 (210mm×297mm)"))
        checks.append(
            (
                "gbt9704-margins",
                all(tok in doc_xml for tok in (f'w:top="{M_TOP}"', f'w:bottom="{M_BOT}"', f'w:left="{M_LEFT}"', f'w:right="{M_RIGHT}"')),
                "上37mm/下35mm/左28mm/右26mm",
            )
        )
        checks.append(("body-font-fangsong", "仿宋_GB2312" in all_xml or "仿宋" in all_xml, "正文三号仿宋_GB2312"))
        checks.append(("title-font-xiaobiaosong", "方正小标宋简体" in all_xml or "方正小标宋" in all_xml, "标题二号方正小标宋简体"))
        checks.append(("exact-28pt-line-spacing", 'w:line="560"' in all_xml and 'w:lineRule="exact"' in all_xml, "28磅固定行距"))
        checks.append(("heading-styles-defined", all(f'w:styleId="Heading{n}"' in sty_xml for n in (1, 2, 3, 4)), "Heading1-4 样式已定义"))
        checks.append(("page-number-footer", "PAGE" in footer_all and "—" in footer_all, "一字线页码域"))

        if profile in {"formal-preprinted", "formal-digital"}:
            checks.append(("mirror-margins", "mirrorMargins" in set_xml, "镜像页边距"))
            checks.append(("even-odd-footers", "evenAndOddHeaders" in set_xml and len(footer_xmls) >= 2, "奇偶不同页脚"))
        if profile == "formal-preprinted":
            checks.append(("no-redhead-drawn", f'w:val="{RED_HEX}"' not in doc_xml and 'w:val="FF0000"' not in doc_xml, "预印套打不重绘红头红线"))
        if profile == "formal-digital":
            checks.append(("digital-redhead-present", f'w:val="{RED_HEX}"' in doc_xml or 'w:val="FF0000"' in doc_xml, "电子红头含红色要素"))

    failed = [name for name, ok, _ in checks if not ok]
    return {
        "ok": len(failed) == 0,
        "zip_ok": True,
        "file": str(docx_path.resolve()),
        "profile": profile or "auto",
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed_items": failed,
        "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
    }


def _doc_no_signer_table(doc_no: str, signer: str, *, red_rule: bool = False) -> str:
    col_l = CONTENT_W // 2
    col_r = CONTENT_W - col_l
    bdr_bot = f'<w:bottom w:val="single" w:sz="18" w:space="0" w:color="{RED_HEX}"/>' if red_rule else '<w:bottom w:val="none"/>'
    return (
        "<w:tbl><w:tblPr>"
        f'<w:tblW w:w="{CONTENT_W}" w:type="dxa"/>'
        '<w:tblLayout w:type="fixed"/>'
        "<w:tblBorders>"
        '<w:top w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f"{bdr_bot}"
        '<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        "</w:tblBorders></w:tblPr>"
        f'<w:tblGrid><w:gridCol w:w="{col_l}"/><w:gridCol w:w="{col_r}"/></w:tblGrid>'
        "<w:tr>"
        f'<w:tc><w:tcPr><w:tcW w:w="{col_l}" w:type="dxa"/></w:tcPr>{_p(_run(doc_no, FONT_BODY, 32), jc="left", left_chars=100, after=80)}</w:tc>'
        f'<w:tc><w:tcPr><w:tcW w:w="{col_r}" w:type="dxa"/></w:tcPr>{_p(_run("签发人：", FONT_BODY, 32) + _run(signer, FONT_H2, 32), jc="right", right_chars=100, after=80)}</w:tc>'
        "</w:tr></w:tbl>"
    )


def _colophon_table(*, cc: str | None, print_org: str, print_date: str) -> str:
    col_l = round(CONTENT_W * 0.58)
    col_r = CONTENT_W - col_l
    date_label = f"{print_date}印发" if print_date and not print_date.endswith("印发") else print_date
    rows: list[str] = []
    if cc:
        cc_p = _p(_run(f"抄送：{cc}", FONT_BODY, 28), jc="both", line_twips=440, left_chars=100, right_chars=100)
        rows.append(
            "<w:tr><w:tc><w:tcPr>"
            f'<w:tcW w:w="{CONTENT_W}" w:type="dxa"/><w:gridSpan w:val="2"/>'
            "<w:tcBorders>"
            '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
            '<w:left w:val="none"/><w:right w:val="none"/>'
            "</w:tcBorders></w:tcPr>"
            f"{cc_p}</w:tc></w:tr>"
        )
    if print_org or date_label:
        top_bdr = (
            '<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
            if cc
            else '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        )
        cell_bdr = (
            "<w:tcBorders>"
            f"{top_bdr}"
            '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            '<w:left w:val="none"/><w:right w:val="none"/>'
            "</w:tcBorders>"
        )
        rows.append(
            "<w:tr>"
            f'<w:tc><w:tcPr><w:tcW w:w="{col_l}" w:type="dxa"/>{cell_bdr}</w:tcPr>'
            f'{_p(_run(print_org, FONT_BODY, 28), jc="left", left_chars=100, line_twips=440)}</w:tc>'
            f'<w:tc><w:tcPr><w:tcW w:w="{col_r}" w:type="dxa"/>{cell_bdr}</w:tcPr>'
            f'{_p(_run(date_label, FONT_BODY, 28), jc="right", right_chars=100, line_twips=440)}</w:tc>'
            "</w:tr>"
        )
    return (
        "<w:tbl><w:tblPr>"
        '<w:tblpPr w:leftFromText="0" w:rightFromText="0" w:topFromText="180" w:bottomFromText="0" '
        'w:vertAnchor="margin" w:horzAnchor="margin" w:tblpXSpec="center" w:tblpYSpec="bottom"/>'
        '<w:tblOverlap w:val="never"/>'
        f'<w:tblW w:w="{CONTENT_W}" w:type="dxa"/>'
        '<w:tblLayout w:type="fixed"/>'
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="none"/>'
        "</w:tblBorders>"
        '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
        "</w:tblPr>"
        f'<w:tblGrid><w:gridCol w:w="{col_l}"/><w:gridCol w:w="{col_r}"/></w:tblGrid>'
        f"{''.join(rows)}</w:tbl>"
    )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="UTF-8 纯文本/Markdown 路径，或传 '-' 从标准输入读取。")
    parser.add_argument("--output", help="输出 .docx 文件路径。")
    parser.add_argument("--verify", help="仅核验模式：检测既有 .docx 文件是否符合 GB/T 9704 关键版式规范。")
    parser.add_argument("--profile", choices=PROFILES, default="ordinary")
    parser.add_argument("--title", help="显式指定主标题（省略时取首行）。")
    parser.add_argument("--org", help="发文机关标志（用于 formal-digital 或 minutes）。")
    parser.add_argument("--doc-no", help="发文字号（如“××发〔2026〕1号”）或纪要期号。")
    parser.add_argument("--signer", help="上行文签发人姓名（可选）。")
    parser.add_argument("--cc", help="版记抄送机关（可选，传入时自动生成版记）。")
    parser.add_argument("--print-org", help="版记印发机关（可选）。")
    parser.add_argument("--print-date", help="版记印发日期（如“2026年11月22日”，可选）。")
    parser.add_argument("--seal-mode", choices=SEAL_MODES, default="stamped")
    parser.add_argument("--page-numbers", choices=PAGE_NUMBER_MODES, default="auto")
    parser.add_argument("--letterhead-reserve-mm", type=float, default=72.0, help="formal-preprinted 首面预留红头高度（毫米，默认 72）。")
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已存在的输出文件。")
    args = parser.parse_args(argv)
    try:
        if args.verify:
            v_res = verify_docx(Path(args.verify), profile=args.profile)
            print(json.dumps(v_res, ensure_ascii=False, indent=2))
            return 0 if v_res["ok"] else 1
        if not args.input or not args.output:
            raise ValueError("生成模式必须同时提供 --input 和 --output（核验既有文件请用 --verify <docx>）")
        if args.input == "-":
            raw = sys.stdin.read().lstrip("\ufeff")
        else:
            raw = Path(args.input).read_bytes().decode("utf-8-sig")
        result = build_docx(
            raw,
            Path(args.output),
            profile=args.profile,
            title=args.title,
            org=args.org,
            doc_no=args.doc_no,
            signer=args.signer,
            cc=args.cc,
            print_org=args.print_org,
            print_date=args.print_date,
            seal_mode=args.seal_mode,
            page_numbers=args.page_numbers,
            letterhead_reserve_mm=args.letterhead_reserve_mm,
            overwrite=args.overwrite,
        )
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
