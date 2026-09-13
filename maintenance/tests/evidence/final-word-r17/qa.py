"""Read-only collection and text/page QA after the parent closes the R17 batch."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote
from xml.etree import ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[4]
BATCH = ROOT / "output/final-word-native-r17"
OUT = ROOT / "output/final-word-qa-r17"
RECOVERY = ROOT / "output/rewrite-word-recovery-r15/recovery-index.json"
POPLER = Path("C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inside(path: Path, parent: Path) -> bool:
    return path.resolve().is_relative_to(parent.resolve())


def paragraphs_from_xml(data: bytes) -> list[str]:
    root = ET.fromstring(data)

    def visible(element, owner) -> str:
        if element.tag == W + "p" and element is not owner:
            return ""
        if element.tag == W + "t":
            return element.text or ""
        if element.tag == W + "tab":
            return "\t"
        if element.tag in {W + "br", W + "cr"}:
            return "\n"
        if element.tag == W + "noBreakHyphen":
            return "\u2011"
        if element.tag == W + "softHyphen":
            return "\u00ad"
        return "".join(visible(child, owner) for child in element)

    return [visible(paragraph, paragraph) for paragraph in root.iter(W + "p")]


def read_docx(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        main = archive.read("word/document.xml")
        root = ET.fromstring(main)
        other = {}
        for name in names:
            if re.fullmatch(r"word/(?:header[^/]*|footer[^/]*|footnotes|endnotes|comments)\.xml", name):
                other[name] = paragraphs_from_xml(archive.read(name))
        return {"paragraphs": paragraphs_from_xml(main), "other_story_text": other,
                "tables": len(list(root.iter(W + "tbl"))), "insertions": len(list(root.iter(W + "ins"))),
                "deletions": len(list(root.iter(W + "del"))),
                "deleted_text": [element.text or "" for element in root.iter(W + "delText")],
                "has_macros": any(name.lower().endswith("vbaproject.bin") for name in names)}


def nonempty_paragraphs(paragraphs: list[str]) -> list[str]:
    # Only layout-created empty paragraphs are ignored; no trimming within a text paragraph.
    return [paragraph for paragraph in paragraphs if paragraph.strip()]


def exact_paragraph_check(expected: list[str], actual: list[str]) -> dict:
    expected, actual = nonempty_paragraphs(expected), nonempty_paragraphs(actual)
    return {"exact": expected == actual, "expected": expected, "actual": actual,
            "expected_count": len(expected), "actual_count": len(actual),
            "repr_diff": list(difflib.unified_diff([repr(p) + "\n" for p in expected],
                                                   [repr(p) + "\n" for p in actual],
                                                   fromfile="requested", tofile="docx"))}


def final_link_targets(text: str) -> list[str]:
    found = []
    for match in re.finditer(r"\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\n)]+))\s*\)", text):
        found.append(match.group(1) or match.group(2))
    found.extend(re.findall(r':codex-file-citation\{[^}]*\bpath="([^"]+)"', text))
    found.extend(re.findall(r"`([^`\n]+\.docx)`", text, flags=re.I))
    found.extend(re.findall(r"(?:/?[A-Za-z]:[\\/])[^\n<>`\"]+?\.docx", text, flags=re.I))
    return list(dict.fromkeys(target.strip() for target in found))


def resolve_link(target: str, workspace: Path, allowed: list[Path], documents: list[dict]) -> dict:
    raw = target
    target = unquote(target.strip().strip("<>"))
    target = re.sub(r"[?#].*$", "", target)
    row = {"raw": raw, "resolved": False}
    if not target.lower().endswith(".docx"):
        return row | {"kind": "non-docx-link"}
    if target.lower().startswith("file:///"):
        target = target[8:]
    if re.match(r"^/[A-Za-z]:/", target):
        target = target[1:]
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) and not re.match(r"^[A-Za-z]:[\\/]", target):
        return row | {"kind": "unsupported-uri", "target": target}
    path = Path(target)
    absolute = path.is_absolute()
    path = path if absolute else workspace / path
    path = path.resolve()
    row.update({"kind": "absolute-path" if absolute else "workspace-relative", "target": str(path)})
    if not any(inside(path, parent) for parent in allowed):
        return row | {"reason": "outside-bound-workspace-or-tmp"}
    matches = [doc for doc in documents if Path(doc["original"]).resolve() == path]
    if len(matches) == 1:
        return row | {"resolved": True, "document_id": matches[0]["document_id"],
                      "sha256": matches[0]["docx_sha256"]}
    return row | {"reason": "no-exact-inventory-match" if not matches else "ambiguous-inventory-match"}


def text_checks(case: str, prompt: str, content: dict, draft_date: str) -> dict:
    paragraphs = content["paragraphs"]
    text = "\n".join(paragraphs)
    compact = re.sub(r"\s+", "", text)
    common = {"paragraphs": paragraphs, "other_story_text": content["other_story_text"],
              "wrapper_terms": [term for term in ("文后提示", "结构说明", "脚本复核", "检查结果", "文件位置") if term in text],
              "manual_fact_and_layout_review_required": True}
    if case == "scope_word_format_only":
        parts = prompt.split("\n\n", 1)
        if len(parts) != 2:
            return common | {"error": "format-only-source-paragraphs-not-found"}
        check = exact_paragraph_check(parts[1].splitlines(), paragraphs)
        return common | {"format_only": check, "source_has_five_paragraphs": check["expected_count"] == 5,
                         "empty_date_exact": "日期：____年__月__日" in nonempty_paragraphs(paragraphs)}
    year, month, day = (int(value) for value in draft_date.split("-"))
    return common | {"anchor_probes": {
        "one_unit_mentioned": bool(re.search(r"(?:一|1)台", compact)),
        "budget_1800_mentioned": bool(re.search(r"(?:1,?800(?:\.00)?|壹仟捌佰|一千八百)元", compact)),
        "jam_mentioned": "卡纸" in compact, "request_action_mentioned": "申请" in compact or "请予批准" in compact,
        "recipient_candidates": [p for p in nonempty_paragraphs(paragraphs)[:4] if "学校" in p and ("：" in p or ":" in p)],
        "signature_exact_paragraph": "教务处" in nonempty_paragraphs(paragraphs),
        "expected_draft_date": draft_date,
        "expected_date_mentioned": bool(re.search(rf"{year}年0?{month}月0?{day}日", compact)),
        "dates_found": re.findall(r"(?:\d{4}年)?\d{1,2}月\d{1,2}日", compact),
        "quantity_contexts": re.findall(r"[^。；\n]{0,22}(?:一|\d+)台[^。；\n]{0,22}", text),
        "amount_contexts": re.findall(r"[^。；\n]{0,22}\d[\d,.]*\s*元[^。；\n]{0,22}", text),
        "repair_expected": case == "scope_word_today",
        "repair_date_mentioned": "8月20日" in compact,
        "repair_contexts": [p for p in paragraphs if any(word in p for word in ("维修", "检修", "修理"))],
        "funding_source_contexts_for_review": [p for p in paragraphs if "列支" in p or "资金来源" in p],
    }}


def collect(args) -> None:
    if not args.completed_batch:
        raise RuntimeError("Collect only after the parent explicitly confirms this batch has ended")
    if (OUT / "collection-index.json").exists():
        raise RuntimeError("Collection already exists; preserve it instead of overwriting")
    binding_path = BATCH / "binding.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8-sig"))
    runtime = Path(binding["runtime"]).resolve()
    old_cases = json.loads(RECOVERY.read_text(encoding="utf-8-sig"))["binding"]["cases"]
    case_prompts = binding.get("cases", {})
    results = sorted(BATCH.glob("*.result.json"))
    OUT.mkdir(parents=True, exist_ok=True)
    calls = []
    for result_path in results:
        call_id = result_path.name.removesuffix(".result.json")
        result = json.loads(result_path.read_text(encoding="utf-8-sig"))
        case = result.get("case") or next((name for name in old_cases if name in call_id), "unknown")
        workspace, temporary = runtime / call_id / "workspace", runtime / call_id / "tmp"
        allowed = [workspace, temporary]
        prompt = case_prompts.get(case, "")
        row = {"id": call_id, "case": case, "arm": result.get("arm", call_id.rsplit("-", 1)[-1]),
               "model": result.get("model"), "result_path": str(result_path), "result_sha256": sha256(result_path),
               "result": result, "workspace": str(workspace), "tmp": str(temporary),
               "prompt": prompt, "prompt_matches_original_r8": prompt == old_cases.get(case),
               "runtime_files": [], "documents": [], "errors": []}
        for source_root in allowed:
            if not inside(source_root, runtime):
                row["errors"].append("call directory resolves outside bound runtime")
                continue
            if not source_root.is_dir():
                row["errors"].append("missing runtime directory: " + str(source_root))
                continue
            for source in sorted(source_root.rglob("*")):
                if not source.is_file():
                    continue
                if not inside(source, source_root):
                    row["errors"].append("escaped runtime file: " + str(source))
                    continue
                relative = source.relative_to(source_root)
                target = OUT / "calls" / call_id / source_root.name / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                before = sha256(source)
                if target.exists() and sha256(target) != before:
                    raise RuntimeError("Refusing to overwrite different collected bytes: " + str(target))
                shutil.copy2(source, target)
                copied = sha256(target)
                file_row = {"original": str(source), "copied": str(target), "sha256": before,
                            "source_copy_hash_match": copied == before == sha256(source),
                            "bytes": source.stat().st_size, "source_mtime_ns": source.stat().st_mtime_ns}
                row["runtime_files"].append(file_row)
                if source.suffix.lower() != ".docx" or ".agents" in relative.parts:
                    continue
                document = file_row | {"document_id": f"docx-{len(row['documents']) + 1:03d}",
                                       "recovered": str(target), "docx_sha256": copied, "linked_from_final": False}
                try:
                    document["content"] = read_docx(target)
                    document["text_checks"] = text_checks(case, prompt, document["content"], args.draft_date)
                except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as error:
                    document["read_error"] = str(error)
                row["documents"].append(document)
        final_path = BATCH / f"{call_id}.final.txt"
        row["final_path"] = str(final_path)
        row["final_present"] = final_path.is_file()
        row["final_text"] = final_path.read_text(encoding="utf-8-sig") if final_path.is_file() else None
        row["final_sha256"] = sha256(final_path) if final_path.is_file() else None
        row["final_links"] = [resolve_link(link, workspace, allowed, row["documents"])
                              for link in final_link_targets(row["final_text"] or "")]
        linked = {link["document_id"] for link in row["final_links"] if link["resolved"]}
        for document in row["documents"]:
            document["linked_from_final"] = document["document_id"] in linked
        calls.append(row)
    index = {"stage": "collected-after-parent-completion", "batch": str(BATCH), "binding": binding,
             "binding_sha256": sha256(binding_path), "runtime": str(runtime), "draft_date_basis": args.draft_date,
             "expected_calls": 12, "result_records": len(results), "count_matches_expected": len(results) == 12,
             "calls": calls, "visual_review_status": "not-yet-performed"}
    write_json(OUT / "collection-index.json", index)
    print(json.dumps({"calls": len(calls), "docx": sum(len(call["documents"]) for call in calls),
                      "output": str(OUT / "collection-index.json")}, ensure_ascii=False))


def pages() -> None:
    from pdf2image import convert_from_path
    from pypdf import PdfReader

    index = json.loads((OUT / "collection-index.json").read_text(encoding="utf-8-sig"))
    rendered = json.loads((OUT / "word-render-results.json").read_text(encoding="utf-8-sig"))
    if isinstance(rendered, dict):
        rendered = [rendered]
    documents = {(call["id"], doc["document_id"]): doc for call in index["calls"] for doc in call["documents"]}
    results = []
    for render in rendered:
        row = dict(render)
        document = documents[(row["id"], row["document_id"])]
        if row.get("success"):
            try:
                pdf = Path(row["pdf"])
                if not inside(pdf, OUT):
                    raise ValueError("render path is outside this QA output")
                images = convert_from_path(str(pdf), dpi=130, poppler_path=str(POPLER))
                row["pngs"] = []
                for number, image in enumerate(images, 1):
                    target = pdf.parent / f"page-{number:03d}.png"
                    image.save(target)
                    image.close()
                    row["pngs"].append({"path": str(target), "sha256": sha256(target)})
                row["pdf_sha256"] = sha256(pdf)
                pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)
                row["pdf_text"] = pdf_text
                expected = document.get("content", {}).get("paragraphs", [])
                word_text = row.get("word_text", "").replace("\r", "\n").replace("\x07", "")
                row["word_xml_exact_paragraphs"] = exact_paragraph_check(expected, word_text.splitlines())
                row["pdf_nonspace_matches_body_xml"] = re.sub(r"\s+", "", pdf_text) == re.sub(r"\s+", "", "\n".join(expected))
                row["page_count_matches_word"] = len(images) == row.get("pages")
                row["collected_docx_unchanged"] = sha256(Path(document["recovered"])) == document["docx_sha256"]
                original = Path(document["original"])
                row["original_still_available"] = original.is_file()
                row["original_still_same_sha"] = original.is_file() and sha256(original) == document["docx_sha256"]
                row["visual_review_status"] = "pending-every-page-inspection"
            except Exception as error:
                row["page_qa_error"] = str(error)
        results.append(row)
    write_json(OUT / "page-index.json", results)
    print(json.dumps({"documents": len(results), "pages": sum(len(row.get("pngs", [])) for row in results),
                      "visual_review_status": "not-yet-performed"}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    collector = commands.add_parser("collect")
    collector.add_argument("--completed-batch", action="store_true", required=True)
    collector.add_argument("--draft-date", required=True, help="Date supported by the completed batch context, YYYY-MM-DD")
    commands.add_parser("pages")
    args = parser.parse_args()
    if args.command == "collect":
        collect(args)
    else:
        pages()


if __name__ == "__main__":
    main()
