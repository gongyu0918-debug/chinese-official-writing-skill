"""Record the completed R17 page inspection and audit the preserved bytes.

The page notes below were written after viewing all twelve PNGs individually.
They are human observations, not conclusions inferred from XML/text equality.
This script only reads source artifacts and writes this batch's QA evidence.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from qa import BATCH, OUT, inside, sha256, write_json

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
NOTES = {
    "m2-scope_word_complete_signoff-baseline": "一页。标题居中，正文分段，单位日期右置；文字清晰，未见重叠、裁切或丢字。",
    "m2-scope_word_complete_signoff-candidate": "一页。标题居中加粗，正文一大段，单位日期右置；字形与间距正常，无遮挡。",
    "m2-scope_word_format_only-baseline": "一页。五段及空日期均可见；标题居中加粗，单位日期右置，正文正常换行。",
    "m2-scope_word_format_only-candidate": "一页。五段及空日期均可见；标题居中，正文与落款分区清楚，无重叠或裁切。",
    "m2-scope_word_today-baseline": "一页。标题居中加粗，主送缩进约两字；维修日期、金额、落款日期均清晰。主送缩进仅记录，不增设严格公文格式门槛。",
    "m2-scope_word_today-candidate": "一页。标题为请示；维修日期、金额、落款完整可读。预算1800与元分行，元。独占短行，可改善但不判排版失败。",
    "m4-scope_word_complete_signoff-baseline": "一页。标题居中，主送与正文清楚，单位日期右置；无重叠或裁切。",
    "m4-scope_word_complete_signoff-candidate": "一页。只有标题正常；主送、正文和落款缩成细点，部分字形叠在一起，无法正常阅读。XML及提取文本完整不等于可读。",
    "m4-scope_word_format_only-baseline": "一页。五段及日期下划线均正常可见，单位日期右置；无重叠或丢字。",
    "m4-scope_word_format_only-candidate": "一页。五段及日期下划线正常，正文和落款可读；最终链接问题另记。",
    "m4-scope_word_today-baseline": "一页。标题、主送、正文及落款可读；8月20日、1台、1800元、完整日期均可见。",
    "m4-scope_word_today-candidate": "一页。标题、主送、正文及落款可读；维修后仍卡纸、金额与完整日期均可见。",
}
FAILED_PAGE = "m4-scope_word_complete_signoff-candidate"


def properties(node):
    if node is None:
        return []
    return [{"tag": child.tag.rsplit("}", 1)[-1],
             "attributes": {key.rsplit("}", 1)[-1]: value for key, value in child.attrib.items()},
             "children": properties(child)} for child in node]


def inspect_xml(document, call_id):
    path = Path(document["recovered"])
    if not inside(path, OUT):
        raise ValueError("XML diagnostic input escapes this QA output")
    with zipfile.ZipFile(path) as archive:
        parts = {name: archive.read(name) for name in
                 ("word/document.xml", "word/styles.xml", "word/settings.xml")}
    root = ET.fromstring(parts["word/document.xml"])
    paragraphs = []
    zero_size_nonempty_runs = []
    for number, paragraph in enumerate(root.findall("w:body/w:p", NS), 1):
        runs = []
        for run in paragraph.findall(".//w:r", NS):
            text = "".join(node.text or "" for node in run.findall(".//w:t", NS))
            size = run.find("w:rPr/w:sz", NS)
            value = None if size is None else size.get(f"{{{W}}}val")
            runs.append({"text": text, "direct_size_half_points": value,
                         "run_properties": properties(run.find("w:rPr", NS))})
            if text and value == "0":
                zero_size_nonempty_runs.append({"paragraph": number, "text": text})
        paragraphs.append({"number": number, "paragraph_properties": properties(paragraph.find("w:pPr", NS)),
                           "runs": runs})
    styles = ET.fromstring(parts["word/styles.xml"])
    settings = ET.fromstring(parts["word/settings.xml"])
    row = {"id": call_id, "docx_sha256": sha256(path),
           "part_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in parts.items()},
           "paragraphs": paragraphs,
           "zero_size_nonempty_runs": zero_size_nonempty_runs,
           "normal_style": properties(styles.find("w:style[@w:styleId='Normal']", NS)),
           "doc_defaults": properties(styles.find("w:docDefaults", NS)),
           "explicit_character_width_scales": [dict(node.attrib) for node in root.findall(".//w:rPr/w:w", NS)],
           "character_spacing_control": None}
    spacing = settings.find("w:characterSpacingControl", NS)
    row["character_spacing_control"] = dict(spacing.attrib) if spacing is not None else None
    if zero_size_nonempty_runs:
        for name, data in parts.items():
            target = OUT / "xml-diagnostics" / call_id / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return row


def main():
    collection_path = OUT / "collection-index.json"
    page_path = OUT / "page-index.json"
    collection = json.loads(collection_path.read_text(encoding="utf-8-sig"))
    pages = json.loads(page_path.read_text(encoding="utf-8-sig"))
    if {page["id"] for page in pages} != set(NOTES) or any(len(p.get("pngs", [])) != 1 for p in pages):
        raise ValueError("Manual notes cover exactly the twelve inspected one-page R17 artifacts")
    visual = []
    for page in pages:
        png = page["pngs"][0]
        if sha256(Path(png["path"])) != png["sha256"]:
            raise ValueError("Inspected image bytes changed")
        visual.append({"id": page["id"], "document_id": page["document_id"], "page": 1,
                       "png": png["path"], "png_sha256": png["sha256"],
                       "method": "individual full-page image inspection at original 130-dpi PNG size",
                       "readability": "FAIL" if page["id"] == FAILED_PAGE else "PASS",
                       "notes": NOTES[page["id"]]})
    write_json(OUT / "visual-review.json", visual)

    audit = {"collection_sha256": sha256(collection_path), "page_index_sha256": sha256(page_path),
             "checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
             "runtime_files": 0, "unchanged_source_and_copy": 0, "failures": [], "calls": [], "receipts": []}
    receipt_paths = [(BATCH / "binding.json", collection["binding_sha256"])]
    xml = []
    inventory = []
    for call in collection["calls"]:
        for file in call["runtime_files"]:
            source, copy = Path(file["original"]), Path(file["copied"])
            if not any(inside(source, Path(call[key])) for key in ("workspace", "tmp")) or not inside(copy, OUT):
                raise ValueError("Preserved file escapes this call's bound directories")
            okay = source.is_file() and copy.is_file() and sha256(source) == sha256(copy) == file["sha256"]
            audit["runtime_files"] += 1
            audit["unchanged_source_and_copy"] += int(okay)
            if not okay:
                audit["failures"].append({"original": str(source), "copied": str(copy), "expected": file["sha256"]})
        receipt_paths.append((Path(call["result_path"]), call["result_sha256"]))
        if call["final_present"]:
            receipt_paths.append((Path(call["final_path"]), call["final_sha256"]))
        audit["calls"].append({"id": call["id"], "runtime_files": len(call["runtime_files"]),
                               "final_present": call["final_present"],
                               "final_receipt_hash_matches": call["result"].get("draft_sha256") == call["final_sha256"] if call["final_present"] else None})
        for document in call["documents"]:
            xml.append(inspect_xml(document, call["id"]))
            page = next(p for p in pages if (p["id"], p["document_id"]) == (call["id"], document["document_id"]))
            inventory.append({"id": call["id"], "technical_invalid": call["result"]["invalid"],
                              "original": document["original"], "recovered": document["recovered"],
                              "docx_sha256": document["docx_sha256"], "linked_from_final": document["linked_from_final"],
                              "final_path": call["final_path"], "final_sha256": call["final_sha256"],
                              "final_links": call["final_links"], "result_path": call["result_path"],
                              "result_sha256": call["result_sha256"], "pdf": page["pdf"],
                              "pdf_sha256": page["pdf_sha256"], "pngs": page["pngs"]})
    for source, expected in receipt_paths:
        if not inside(source, BATCH) or sha256(source) != expected:
            raise ValueError("Completed batch receipt changed or escaped its directory")
        target = OUT / "receipts" / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha256(target) != expected:
            raise ValueError("Refusing to overwrite changed receipt bytes")
        shutil.copy2(source, target)
        audit["receipts"].append({"original": str(source), "preserved": str(target), "sha256": expected,
                                  "source_copy_hash_match": sha256(target) == expected})
    write_json(OUT / "xml-format-audit.json", xml)
    write_json(OUT / "artifact-inventory.json", inventory)
    write_json(OUT / "preservation-audit.json", audit)
    summary = {"calls": len(collection["calls"]),
               "technical_complete": sum(c["result"]["returncode"] == 0 and not c["result"]["invalid"] and c["final_present"] for c in collection["calls"]),
               "docx": len(inventory), "final_messages": sum(c["final_present"] for c in collection["calls"]),
               "calls_with_bound_docx_final_link": sum(any(link["resolved"] for link in c["final_links"]) for c in collection["calls"]),
               "read_only_word_exports": sum(p["success"] and p["read_only"] for p in pages),
               "pages_inspected": len(visual), "readable_pages": sum(v["readability"] == "PASS" for v in visual),
               "format_only_exact": sum(d["text_checks"].get("format_only", {}).get("exact", False) for c in collection["calls"] for d in c["documents"]),
               "original_and_copied_runtime_files_unchanged": audit["unchanged_source_and_copy"],
               "runtime_files": audit["runtime_files"], "preservation_failures": len(audit["failures"]),
               "xml_zero_size_documents": [r["id"] for r in xml if r["zero_size_nonempty_runs"]],
               "com_cleanup_warnings": [{"id": p["id"], key: p[key]} for p in pages for key in ("close_error", "quit_error") if p.get(key)],
               "note": "Technical completion, text preservation, linked delivery, and visual readability are separate axes; no aggregate product pass is inferred."}
    write_json(OUT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
