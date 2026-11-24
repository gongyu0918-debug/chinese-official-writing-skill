#!/usr/bin/env python3
"""Zero-dependency high-fidelity DOCX surgical patcher, Track Changes, and Comment injector.

Uses Python 3 standard library only (zipfile + xml.etree.ElementTree).
Preserves 100% of untouched ZIP entries (redheads, shapes, images, headers, footers, styles,
themes, tables) while supporting:
  1. --inspect <file.docx>: List body and table-cell paragraphs with indices and text.
  2. --input <src.docx> --output <dst.docx> --plan <-|plan.json>:
     - Surgical in-place text replacement preserving original run formatting (<w:rPr>)
     - Native Word Track Changes (<w:del> + <w:ins>) for accept/reject review workflows
     - Native Word Comments (<w:commentRangeStart>/<w:commentRangeEnd>/<w:commentReference> + word/comments.xml)
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"
W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
COMMENTS_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
COMMENTS_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"

DEFAULT_NS = {
    "w": W_NS,
    "r": R_NS,
    "w15": W15_NS,
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
}


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def _extract_root_xmlns(xml_bytes: bytes) -> list[tuple[str, str]]:
    """Extract all xmlns:prefix declarations from the document root opening tag."""
    m = re.search(rb"<[^?>!\s][^>]*>", xml_bytes[:16384])
    if not m:
        return []
    tag_str = m.group(0).decode("utf-8", errors="ignore")
    return re.findall(r'xmlns:([A-Za-z0-9_.-]+)=["\']([^"\']+)["\']', tag_str)


def _restore_missing_root_xmlns(serialized: bytes, orig_xmlns: list[tuple[str, str]]) -> bytes:
    """Re-attach any source root xmlns:* declarations (e.g. mc:Ignorable prefixes) pruned by ET."""
    if not orig_xmlns:
        return serialized
    m = re.search(rb"<[^?>!\s][^>]*>", serialized[:32768])
    if not m:
        return serialized
    tag_str = m.group(0).decode("utf-8", errors="replace")
    existing = set(re.findall(r'xmlns:([A-Za-z0-9_.-]+)=', tag_str))
    missing = [
        (p, u) for p, u in orig_xmlns
        if p != "xml" and not re.fullmatch(r"ns\d+", p) and p not in existing
    ]
    if not missing:
        return serialized
    parts = []
    for prefix, uri in missing:
        safe_uri = uri.replace("&", "&amp;").replace('"', "&quot;")
        parts.append(f' xmlns:{prefix}="{safe_uri}"')
    extra = "".join(parts).encode("utf-8")
    close_offset = m.end() - 2 if m.group(0).endswith(b"/>") else m.end() - 1
    return serialized[:close_offset] + extra + serialized[close_offset:]


def _register_namespaces_from_xml(xml_bytes: bytes) -> None:
    """Register standard + source document namespace prefixes so ET preserves prefixes cleanly."""
    for prefix, uri in DEFAULT_NS.items():
        ET.register_namespace(prefix, uri)
    head = xml_bytes[:16384].decode("utf-8", errors="ignore")
    for prefix, uri in re.findall(r'xmlns:([A-Za-z0-9_.-]+)=["\']([^"\']+)["\']', head):
        if prefix == "xml" or re.fullmatch(r"ns\d+", prefix):
            continue
        ET.register_namespace(prefix, uri)


def _iter_paragraphs(body: ET.Element) -> list[tuple[int, str, ET.Element]]:
    """Collect all <w:p> nodes across top-level body, table cells, and content controls in document order."""
    result: list[tuple[int, str, ET.Element]] = []
    tbl_idx = 0

    def walk_container(container: ET.Element, prefix: str) -> None:
        nonlocal tbl_idx
        for child in list(container):
            if child.tag == _w("p"):
                result.append((len(result), prefix, child))
            elif child.tag == _w("tbl"):
                cur_t = tbl_idx
                tbl_idx += 1
                r_idx = 0
                for tr in child.findall(_w("tr")):
                    c_idx = 0
                    for tc in tr.findall(_w("tc")):
                        walk_container(tc, f"table[{cur_t}].r[{r_idx}].c[{c_idx}]")
                        c_idx += 1
                    r_idx += 1
            elif child.tag == _w("sdt"):
                sdt_content = child.find(_w("sdtContent"))
                if sdt_content is not None:
                    walk_container(sdt_content, f"{prefix}.sdt")

    walk_container(body, "body")
    return result


def _explode_compound_runs(p: ET.Element) -> None:
    """Split multi-child direct <w:r> elements into single-payload runs so <w:br/>/<w:tab/> are never dropped."""
    for child in list(p):
        if child.tag != _w("r"):
            continue
        rpr = child.find(_w("rPr"))
        payload = [c for c in list(child) if c.tag != _w("rPr")]
        if len(payload) <= 1:
            continue
        idx = list(p).index(child)
        p.remove(child)
        for offset_i, sub in enumerate(payload):
            new_r = ET.Element(_w("r"))
            if rpr is not None:
                new_r.append(copy.deepcopy(rpr))
            new_r.append(copy.deepcopy(sub))
            p.insert(idx + offset_i, new_r)


def _strip_proof_errors(p: ET.Element) -> None:
    """Remove direct <w:proofErr> markers inside an edited paragraph to avoid orphaned spellStart/spellEnd tags."""
    for child in list(p):
        if child.tag == _w("proofErr"):
            p.remove(child)


def _collect_direct_text_runs(p: ET.Element) -> list[tuple[int, ET.Element, int, int, str]]:
    """Collect direct child <w:r> elements containing <w:t> text (skipping runs inside <w:del>/<w:ins>)."""
    runs: list[tuple[int, ET.Element, int, int, str]] = []
    offset = 0
    for child_idx, child in enumerate(list(p)):
        if child.tag != _w("r"):
            continue
        t_nodes = child.findall(_w("t"))
        if not t_nodes:
            continue
        text = "".join(t.text or "" for t in t_nodes)
        if not text:
            continue
        runs.append((child_idx, child, offset, offset + len(text), text))
        offset += len(text)
    return runs


def _collect_visible_segments(p: ET.Element) -> list[tuple[int, ET.Element, str, int, int, str]]:
    """Collect visible text segments across direct <w:r> and <w:ins> elements (excluding <w:del>)."""
    segs: list[tuple[int, ET.Element, str, int, int, str]] = []
    offset = 0
    for child_idx, child in enumerate(list(p)):
        if child.tag == _w("r"):
            t_nodes = child.findall(_w("t"))
            if not t_nodes:
                continue
            text = "".join(t.text or "" for t in t_nodes)
            if not text:
                continue
            segs.append((child_idx, child, "r", offset, offset + len(text), text))
            offset += len(text)
        elif child.tag == _w("ins"):
            text = "".join(t.text or "" for r in child.findall(_w("r")) for t in r.findall(_w("t")))
            if not text:
                continue
            segs.append((child_idx, child, "ins", offset, offset + len(text), text))
            offset += len(text)
    return segs


def _para_visible_text(p: ET.Element) -> str:
    """Read visible text of a paragraph (direct runs + inserted runs, skipping deleted runs)."""
    return "".join(seg[5] for seg in _collect_visible_segments(p))


def _clone_rpr(run_el: ET.Element) -> ET.Element | None:
    rpr = run_el.find(_w("rPr"))
    return copy.deepcopy(rpr) if rpr is not None else None


def _make_text_run(text: str, rpr: ET.Element | None, *, deleted: bool = False) -> ET.Element:
    r = ET.Element(_w("r"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = ET.SubElement(r, _w("delText" if deleted else "t"))
    t.set(f"{{{XML_NS}}}space", "preserve")
    t.text = text
    return r


def _split_runs_at_span(p: ET.Element, start: int, end: int) -> tuple[list[ET.Element], ET.Element | None]:
    """Explode compound runs then split direct <w:r> runs at [start, end); return matched runs & first rPr."""
    _explode_compound_runs(p)
    runs = _collect_direct_text_runs(p)
    if not runs:
        return [], None

    # Split from right boundary first, then left boundary, keeping preceding offsets valid.
    for cut in (end, start):
        runs = _collect_direct_text_runs(p)
        for child_idx, r_el, r_start, r_end, r_text in runs:
            if r_start < cut < r_end:
                split_at = cut - r_start
                left_txt = r_text[:split_at]
                right_txt = r_text[split_at:]
                rpr = _clone_rpr(r_el)
                left_run = _make_text_run(left_txt, rpr)
                right_run = _make_text_run(right_txt, rpr)
                p.remove(r_el)
                p.insert(child_idx, left_run)
                p.insert(child_idx + 1, right_run)
                break

    runs = _collect_direct_text_runs(p)
    matched: list[ET.Element] = []
    first_rpr: ET.Element | None = None
    for _, r_el, r_start, r_end, _ in runs:
        if r_start >= start and r_end <= end:
            if first_rpr is None:
                first_rpr = _clone_rpr(r_el)
            matched.append(r_el)
    return matched, first_rpr


def _split_visible_at_span(p: ET.Element, start: int, end: int) -> list[ET.Element]:
    """Locate visible nodes (<w:r> and <w:ins>) overlapping [start, end), splitting plain <w:r> boundaries."""
    _explode_compound_runs(p)
    if not _collect_visible_segments(p):
        return []

    for cut in (end, start):
        segs = _collect_visible_segments(p)
        for child_idx, el, kind, seg_start, seg_end, seg_text in segs:
            if kind == "r" and seg_start < cut < seg_end:
                split_at = cut - seg_start
                rpr = _clone_rpr(el)
                left_run = _make_text_run(seg_text[:split_at], rpr)
                right_run = _make_text_run(seg_text[split_at:], rpr)
                p.remove(el)
                p.insert(child_idx, left_run)
                p.insert(child_idx + 1, right_run)
                break

    segs = _collect_visible_segments(p)
    return [el for _, el, _, seg_start, seg_end, _ in segs if seg_end > start and seg_start < end]


def _max_existing_id(root: ET.Element, tags: tuple[str, ...]) -> int:
    max_id = 0
    for tag in tags:
        for el in root.iter(_w(tag)):
            val = el.get(_w("id"))
            if val and val.isdigit():
                max_id = max(max_id, int(val))
    return max_id


def inspect_docx(docx_path: Path) -> dict:
    """Return read-only summary of all non-empty paragraphs across body and tables."""
    if not docx_path.is_file():
        raise FileNotFoundError(f"文件不存在: {docx_path}")
    with zipfile.ZipFile(docx_path, "r") as zf:
        if "word/document.xml" not in zf.namelist():
            raise ValueError(f"无效 DOCX（缺少 word/document.xml）: {docx_path}")
        doc_xml = zf.read("word/document.xml")
        has_comments = "word/comments.xml" in zf.namelist()
        parts_count = len(zf.namelist())

    root = ET.fromstring(doc_xml)
    body = root.find(_w("body"))
    if body is None:
        raise ValueError("DOCX 缺少 <w:body>")

    items = []
    for p_idx, loc, p in _iter_paragraphs(body):
        txt = _para_visible_text(p)
        if not txt.strip():
            continue
        has_rev = (p.find(_w("ins")) is not None) or (p.find(_w("del")) is not None)
        items.append({
            "p_index": p_idx,
            "location": loc,
            "text": txt,
            "has_track_changes": has_rev,
        })
    return {
        "file": str(docx_path.resolve()),
        "parts_count": parts_count,
        "has_comments_part": has_comments,
        "non_empty_paragraphs": len(items),
        "paragraphs": items,
    }


def _register_comments_content_type(ct_bytes: bytes) -> bytes:
    ET.register_namespace("", CT_NS)
    root = ET.fromstring(ct_bytes)
    for ov in root.findall(f"{{{CT_NS}}}Override"):
        if ov.get("PartName") == "/word/comments.xml":
            return ct_bytes
    ov = ET.SubElement(root, f"{{{CT_NS}}}Override")
    ov.set("PartName", "/word/comments.xml")
    ov.set("ContentType", COMMENTS_CONTENT_TYPE)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _register_comments_relationship(rels_bytes: bytes) -> bytes:
    ET.register_namespace("", REL_NS)
    root = ET.fromstring(rels_bytes)
    max_num = 0
    for rel in root.findall(f"{{{REL_NS}}}Relationship"):
        if rel.get("Type") == COMMENTS_REL_TYPE or rel.get("Target") == "comments.xml":
            return rels_bytes
        rid = rel.get("Id", "")
        m = re.match(r"^rId(\d+)$", rid)
        if m:
            max_num = max(max_num, int(m.group(1)))
    rel = ET.SubElement(root, f"{{{REL_NS}}}Relationship")
    rel.set("Id", f"rId{max_num + 1}")
    rel.set("Type", COMMENTS_REL_TYPE)
    rel.set("Target", "comments.xml")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _build_or_append_comments_xml(existing_bytes: bytes | None, new_comments: list[tuple[int, str, str, str]]) -> bytes:
    ET.register_namespace("w", W_NS)
    ET.register_namespace("w15", W15_NS)
    if existing_bytes:
        _register_namespaces_from_xml(existing_bytes)
        root = ET.fromstring(existing_bytes)
    else:
        root = ET.Element(_w("comments"))

    for cid, author, iso_date, text in new_comments:
        c = ET.SubElement(root, _w("comment"))
        c.set(_w("id"), str(cid))
        c.set(_w("author"), author)
        c.set(_w("date"), iso_date)
        for line in text.splitlines() or [text]:
            p = ET.SubElement(c, _w("p"))
            r = ET.SubElement(p, _w("r"))
            t = ET.SubElement(r, _w("t"))
            t.set(f"{{{XML_NS}}}space", "preserve")
            t.text = line
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def patch_docx(
    input_path: Path,
    output_path: Path,
    plan: dict,
    *,
    overwrite: bool = False,
) -> dict:
    """Apply surgical replacements, Track Changes, and/or Comments while preserving all other DOCX parts."""
    if not input_path.is_file():
        raise FileNotFoundError(f"源文件不存在: {input_path}")
    if input_path.resolve() == output_path.resolve():
        raise ValueError("禁止原地覆盖原稿，请将 --output 指向新文件路径")
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"目标文件已存在（如需覆盖请显式传 --overwrite）: {output_path}")
    if not isinstance(plan, dict):
        raise ValueError("修改计划必须为 JSON 对象")

    default_author = str(plan.get("author") or "公文核稿")
    replacements = plan.get("replacements") or []
    comments = plan.get("comments") or []
    if not isinstance(replacements, list) or not isinstance(comments, list):
        raise ValueError("replacements 与 comments 必须为列表")

    iso_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with zipfile.ZipFile(input_path, "r") as zf:
        entries = {name: zf.read(name) for name in zf.namelist()}
    if "word/document.xml" not in entries:
        raise ValueError(f"无效 DOCX（缺少 word/document.xml）: {input_path}")

    doc_bytes = entries["word/document.xml"]
    orig_xmlns = _extract_root_xmlns(doc_bytes)
    _register_namespaces_from_xml(doc_bytes)
    root = ET.fromstring(doc_bytes)
    body = root.find(_w("body"))
    if body is None:
        raise ValueError("DOCX 缺少 <w:body>")

    paragraphs = _iter_paragraphs(body)
    rev_id = _max_existing_id(root, ("ins", "del"))
    comment_id = _max_existing_id(root, ("commentRangeStart", "commentRangeEnd"))
    if "word/comments.xml" in entries:
        c_root = ET.fromstring(entries["word/comments.xml"])
        comment_id = max(comment_id, _max_existing_id(c_root, ("comment",)))

    applied_plain = 0
    applied_tracked = 0
    applied_comments = 0
    applied_details: list[dict] = []
    missed: list[dict] = []
    comments_to_write: list[tuple[int, str, str, str]] = []

    def _find_target_para(needle: str, p_index: int | None, occurrence: int | None) -> tuple[ET.Element | None, int, int]:
        candidates = (
            [paragraphs[p_index]] if (isinstance(p_index, int) and 0 <= p_index < len(paragraphs)) else paragraphs
        )
        seen_occ = 0
        want_occ = occurrence if isinstance(occurrence, int) and occurrence >= 1 else 1
        for _, _, p in candidates:
            runs = _collect_direct_text_runs(p)
            direct_txt = "".join(r[4] for r in runs)
            search_from = 0
            while True:
                pos = direct_txt.find(needle, search_from)
                if pos == -1:
                    break
                seen_occ += 1
                if seen_occ == want_occ:
                    return p, pos, pos + len(needle)
                search_from = pos + len(needle)
        return None, -1, -1

    def _find_comment_target(needle: str, p_index: int | None, occurrence: int | None) -> tuple[ET.Element | None, int, int]:
        candidates = (
            [paragraphs[p_index]] if (isinstance(p_index, int) and 0 <= p_index < len(paragraphs)) else paragraphs
        )
        seen_occ = 0
        want_occ = occurrence if isinstance(occurrence, int) and occurrence >= 1 else 1
        for _, _, p in candidates:
            segs = _collect_visible_segments(p)
            visible_txt = "".join(seg[5] for seg in segs)
            search_from = 0
            while True:
                pos = visible_txt.find(needle, search_from)
                if pos == -1:
                    break
                seen_occ += 1
                if seen_occ == want_occ:
                    return p, pos, pos + len(needle)
                search_from = pos + len(needle)
        return None, -1, -1

    # 1. Apply replacements (silent high-fidelity OR native Word Track Changes)
    for item in replacements:
        if not isinstance(item, dict) or not isinstance(item.get("old"), str) or not item["old"]:
            raise ValueError("每条 replacement 必须包含非空字符串字段 old")
        old_txt = item["old"]
        new_txt = str(item.get("new", ""))
        tracked = bool(item.get("track_changes", False))
        author = str(item.get("author") or default_author)
        p_index = item.get("p_index")
        occurrence = item.get("occurrence")

        p, start, end = _find_target_para(old_txt, p_index, occurrence)
        if p is None:
            missed.append({"kind": "replacement", "old": old_txt[:60], "reason": "未在目标段落直接文本中找到精确匹配"})
            continue

        matched_runs, first_rpr = _split_runs_at_span(p, start, end)
        if not matched_runs:
            missed.append({"kind": "replacement", "old": old_txt[:60], "reason": "run 拆分失败"})
            continue

        _strip_proof_errors(p)
        insert_pos = list(p).index(matched_runs[0])
        for r_el in matched_runs:
            p.remove(r_el)

        if tracked:
            nodes_to_insert: list[ET.Element] = []
            if old_txt:
                rev_id += 1
                del_el = ET.Element(_w("del"))
                del_el.set(_w("id"), str(rev_id))
                del_el.set(_w("author"), author)
                del_el.set(_w("date"), iso_now)
                del_el.append(_make_text_run(old_txt, first_rpr, deleted=True))
                nodes_to_insert.append(del_el)
            if new_txt:
                rev_id += 1
                ins_el = ET.Element(_w("ins"))
                ins_el.set(_w("id"), str(rev_id))
                ins_el.set(_w("author"), author)
                ins_el.set(_w("date"), iso_now)
                ins_el.append(_make_text_run(new_txt, first_rpr, deleted=False))
                nodes_to_insert.append(ins_el)
            for offset_i, node in enumerate(nodes_to_insert):
                p.insert(insert_pos + offset_i, node)
            applied_tracked += 1
            applied_details.append({"kind": "track_change", "old": old_txt, "new": new_txt})
        else:
            if new_txt:
                p.insert(insert_pos, _make_text_run(new_txt, first_rpr, deleted=False))
            applied_plain += 1
            applied_details.append({"kind": "replacement", "old": old_txt, "new": new_txt})

    # 2. Inject Word Native Comments anchored to exact visible substrings (including <w:ins>) or paragraphs
    for item in comments:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str) or not item["text"].strip():
            raise ValueError("每条 comment 必须包含非空字符串字段 text")
        anchor = item.get("anchor")
        comment_text = item["text"].strip()
        author = str(item.get("author") or default_author)
        p_index = item.get("p_index")
        occurrence = item.get("occurrence")

        target_p: ET.Element | None = None
        matched_nodes: list[ET.Element] = []
        if isinstance(anchor, str) and anchor:
            target_p, start, end = _find_comment_target(anchor, p_index, occurrence)
            if target_p is not None:
                matched_nodes = _split_visible_at_span(target_p, start, end)
        elif isinstance(p_index, int) and 0 <= p_index < len(paragraphs):
            target_p = paragraphs[p_index][2]
            segs = _collect_visible_segments(target_p)
            matched_nodes = [seg[1] for seg in segs]

        if target_p is None or not matched_nodes:
            missed.append({"kind": "comment", "anchor": str(anchor or f"p_index={p_index}")[:60], "reason": "未定位到可锚定文本"})
            continue

        comment_id += 1
        cid_str = str(comment_id)
        crs = ET.Element(_w("commentRangeStart"))
        crs.set(_w("id"), cid_str)
        cre = ET.Element(_w("commentRangeEnd"))
        cre.set(_w("id"), cid_str)
        ref_run = ET.Element(_w("r"))
        ref_rpr = ET.SubElement(ref_run, _w("rPr"))
        ref_style = ET.SubElement(ref_rpr, _w("rStyle"))
        ref_style.set(_w("val"), "CommentReference")
        ref_el = ET.SubElement(ref_run, _w("commentReference"))
        ref_el.set(_w("id"), cid_str)

        start_idx = list(target_p).index(matched_nodes[0])
        target_p.insert(start_idx, crs)
        end_idx = list(target_p).index(matched_nodes[-1])
        target_p.insert(end_idx + 1, cre)
        target_p.insert(end_idx + 2, ref_run)

        comments_to_write.append((comment_id, author, iso_now, comment_text))
        applied_comments += 1
        applied_details.append({
            "kind": "comment",
            "id": comment_id,
            "anchor": str(anchor or f"p_index={p_index}"),
            "text": comment_text,
        })

    # 3. Serialize modified XML parts while keeping every untouched part byte-identical
    mutated = {"word/document.xml"} | (
        {"word/comments.xml", "[Content_Types].xml", "word/_rels/document.xml.rels"}
        if comments_to_write
        else set()
    )
    untouched_names = sorted(n for n in entries if n not in mutated)

    _register_namespaces_from_xml(doc_bytes)
    serialized_doc = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    entries["word/document.xml"] = _restore_missing_root_xmlns(serialized_doc, orig_xmlns)

    if comments_to_write:
        entries["word/comments.xml"] = _build_or_append_comments_xml(entries.get("word/comments.xml"), comments_to_write)
        if "[Content_Types].xml" in entries:
            entries["[Content_Types].xml"] = _register_comments_content_type(entries["[Content_Types].xml"])
        if "word/_rels/document.xml.rels" in entries:
            entries["word/_rels/document.xml.rels"] = _register_comments_relationship(entries["word/_rels/document.xml.rels"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)

    # 4. Self-verify ZIP CRC & XML well-formedness
    with zipfile.ZipFile(output_path, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            raise OSError(f"输出 DOCX ZIP CRC 校验失败: {bad}")
        ET.fromstring(zf.read("word/document.xml"))
        if comments_to_write:
            ET.fromstring(zf.read("word/comments.xml"))

    return {
        "ok": len(missed) == 0,
        "zip_ok": True,
        "untouched_parts_preserved": True,
        "untouched_parts": untouched_names,
        "input": str(input_path.resolve()),
        "output": str(output_path.resolve()),
        "preserved_parts_count": len(entries),
        "applied_replacements": applied_plain,
        "applied_track_changes": applied_tracked,
        "applied_comments": applied_comments,
        "applied_details": applied_details,
        "missed_items": missed,
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect", help="只读检查既有 .docx，列出正文和表格中的全部非空段落及索引。")
    parser.add_argument("--input", help="源 .docx 模板或原稿路径。")
    parser.add_argument("--output", help="输出新 .docx 路径（禁止覆盖原稿）。")
    parser.add_argument("--plan", help="修改计划 JSON 路径，或传 '-' 从标准输入读取。")
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已存在的目标输出文件（仍禁止覆盖 --input）。")
    args = parser.parse_args(argv)
    try:
        if args.inspect:
            res = inspect_docx(Path(args.inspect))
            print(json.dumps(res, ensure_ascii=False, indent=2))
            return 0
        if not args.input or not args.output or not args.plan:
            raise ValueError("改稿模式必须同时提供 --input、--output 和 --plan（查看段落请用 --inspect <docx>）")
        if args.plan == "-":
            raw = sys.stdin.read().lstrip("\ufeff")
        else:
            raw = Path(args.plan).read_bytes().decode("utf-8-sig")
        plan = json.loads(raw)
        res = patch_docx(Path(args.input), Path(args.output), plan, overwrite=args.overwrite)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
