"""Prepare, then collect and render only final-linked R19 Word deliverables read-only."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
from xml.etree import ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/docx-input-qa-r19"
SOURCE = ROOT / "output/docx-input-native-r19/received-application.docx"
SOURCE_SHA256 = "0989cecd96b1e85a5bc7eccdb7b0e4ca16260ecb23ae61161a5fd5fe19a6e068"
BATCHES = {name: ROOT / ("output/docx-input-native-r19-" + name) for name in ("deepseek", "glm")}
LEGACY_PATH = ROOT / "maintenance/tests/evidence/final-word-r17/qa.py"
spec = importlib.util.spec_from_file_location("r19_reused_word_qa", LEGACY_PATH)
assert spec is not None and spec.loader is not None
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def input_integrity(path: Path, expected: str = SOURCE_SHA256) -> dict:
    actual = legacy.sha256(path) if path.is_file() else None
    return {"path": str(path), "expected_sha256": expected, "actual_sha256": actual,
            "status": "UNCHANGED" if actual == expected else "MISSING" if actual is None else "CHANGED"}


def copy_bound(source: Path, target: Path) -> dict:
    if not legacy.inside(target, OUT):
        raise ValueError("collection target escapes this R19 output")
    target.parent.mkdir(parents=True, exist_ok=True)
    before = legacy.sha256(source)
    if target.exists() and legacy.sha256(target) != before:
        raise RuntimeError("refusing to overwrite different collected bytes: " + str(target))
    shutil.copy2(source, target)
    copied, after = legacy.sha256(target), legacy.sha256(source)
    return {"original": str(source), "recovered": str(target), "sha256_before": before,
            "sha256_after": after, "sha256": copied, "source_copy_hash_match": before == copied == after,
            "bytes": target.stat().st_size}


def explicit_font_sizes(path: Path) -> dict:
    """Record direct run attributes; rendering is still required to establish readability."""
    records = []
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        for number, paragraph in enumerate(root.iter(legacy.W + "p"), 1):
            for run_number, run in enumerate(paragraph.iter(legacy.W + "r"), 1):
                text = "".join(item.text or "" for item in run.findall(legacy.W + "t"))
                if not text.strip():
                    continue
                props = run.find(legacy.W + "rPr")
                values = {}
                for name in ("sz", "szCs"):
                    node = props.find(legacy.W + name) if props is not None else None
                    values[name] = node.get(legacy.W + "val") if node is not None else None
                records.append({"paragraph": number, "run": run_number, "text": text, **values})
    def zero(value):
        return value is not None and value.strip() and set(value.strip()) == {"0"}
    return {"direct_text_run_sizes": records,
            "direct_zero_sz_runs": [row for row in records if zero(row["sz"])],
            "direct_zero_szCs_runs": [row for row in records if zero(row["szCs"])],
            "size_interpretation": "szCs-only is not a Chinese/Latin readability failure; inheritance not resolved",
            "readability": "PENDING_RENDER_AND_EVERY_PAGE_VISUAL_REVIEW"}


def bind_delivery(final_text: str | None, workspace: Path, allowed: list[Path], documents: list[dict], received: Path) -> dict:
    links = [legacy.resolve_link(target, workspace, allowed, documents)
             for target in legacy.final_link_targets(final_text or "")]
    linked = {row["document_id"] for row in links if row["resolved"]}
    for document in documents:
        original = Path(document["original"]).resolve()
        is_input = original == received.resolve()
        document["linked_from_final"] = document["document_id"] in linked
        document["role"] = "received-input" if is_input else "final-delivery" if document["linked_from_final"] else "unlinked-docx-debug-or-intermediate"
        document["render_eligible"] = (document["role"] == "final-delivery"
                                       and document["source_copy_hash_match"] and not document.get("read_error"))
        if document["role"] == "final-delivery" and not document["render_eligible"]:
            document["render_skip_reason"] = "invalid-DOCX-or-unstable-copy; delivery problem retained"
    delivered = [doc for doc in documents if doc["role"] == "final-delivery"]
    status = "FINAL_MISSING" if not final_text else "WORD_DELIVERED" if delivered else "NO_SEPARATELY_SAVED_WORD_LINK"
    return {"final_links": links, "delivery_status": status, "separately_saved_delivered_docx": len(delivered),
            "render_selected_docx": sum(doc["render_eligible"] for doc in documents)}


def collect(completed_batches: bool) -> None:
    if not completed_batches:
        raise RuntimeError("wait for explicit parent confirmation that both batches are terminal")
    if (OUT / "artifact-inventory.json").exists() or (OUT / "collection-index.json").exists():
        raise RuntimeError("collection already exists; preserve this snapshot")
    OUT.mkdir(parents=True, exist_ok=True)
    shared_source = input_integrity(SOURCE)
    source_snapshot = None
    source_content = None
    if SOURCE.is_file():
        source_snapshot = copy_bound(SOURCE, OUT / "source/received-application.docx")
        if shared_source["status"] == "UNCHANGED" and source_snapshot["source_copy_hash_match"]:
            source_content = legacy.read_docx(Path(source_snapshot["recovered"]))
    calls, batches = [], []
    for alias, batch in BATCHES.items():
        binding_path = batch / "binding.json"
        if not binding_path.is_file():
            batches.append({"id": alias, "error": "binding missing after parent-confirmed completion", "expected_calls": 2, "result_records": 0})
            continue
        binding_snapshot = copy_bound(binding_path, OUT / "batches" / alias / "binding.json")
        binding = json.loads(Path(binding_snapshot["recovered"]).read_text(encoding="utf-8-sig"))
        runtime = Path(binding["runtime"]).resolve()
        if runtime.parent != Path(tempfile.gettempdir()).resolve() or not runtime.name.startswith("cow-native-" + batch.name + "-"):
            raise ValueError("runtime does not match this batch's isolated temporary directory")
        bound_input = binding.get("input_document", {})
        if Path(bound_input.get("source", "")).resolve() != SOURCE.resolve() or bound_input.get("sha256") != SOURCE_SHA256 or bound_input.get("name") != SOURCE.name:
            raise ValueError("batch input binding differs from the authorized DOCX")
        result_paths = sorted(batch.glob("*.result.json"))
        batches.append({"id": alias, "binding": binding, "binding_snapshot": binding_snapshot,
                        "expected_calls": 2, "result_records": len(result_paths), "count_matches_expected": len(result_paths) == 2})
        for result_path in result_paths:
            native_id = result_path.name.removesuffix(".result.json")
            call_id = alias + "--" + native_id
            call_out = OUT / "calls" / call_id
            result_snapshot = copy_bound(result_path, call_out / "native.result.json")
            result = json.loads(Path(result_snapshot["recovered"]).read_text(encoding="utf-8-sig"))
            workspace, temporary = runtime / native_id / "workspace", runtime / native_id / "tmp"
            allowed = [workspace, temporary]
            received = workspace / SOURCE.name
            row = {"id": call_id, "batch": alias, "native_id": native_id,
                   "case": result.get("case", "review_existing_docx"), "arm": result.get("arm"), "model": result.get("model"),
                   "result_snapshot": result_snapshot, "native_result": result,
                   "native_reported_technical_invalid": result.get("technical_invalid"),
                   "received_input": input_integrity(received), "workspace": str(workspace), "tmp": str(temporary),
                   "runtime_files": [], "documents": [], "errors": [],
                   "fact_review": "PENDING_MANUAL_COMPARISON; paragraph changes are not automatic factual failures"}
            # A changed/missing received file is an integrity issue, never relabeled as a timeout.
            row["input_integrity_issue"] = row["received_input"]["status"] != "UNCHANGED"
            for source_root in allowed:
                if not legacy.inside(source_root, runtime):
                    row["errors"].append("runtime directory escapes batch")
                    continue
                if not source_root.is_dir():
                    row["errors"].append("missing runtime directory: " + str(source_root))
                    continue
                for source in sorted(source_root.rglob("*")):
                    relative = source.relative_to(source_root)
                    if any(part in {".agents", ".git", "__pycache__", ".venv", "node_modules"} for part in relative.parts) or not source.is_file():
                        continue
                    if not legacy.inside(source, source_root):
                        row["errors"].append("escaped runtime file: " + str(source))
                        continue
                    copied = copy_bound(source, call_out / source_root.name / relative)
                    row["runtime_files"].append(copied)
                    if source.suffix.lower() != ".docx":
                        continue
                    document = copied | {"document_id": f"docx-{len(row['documents']) + 1:03d}", "docx_sha256": copied["sha256"]}
                    try:
                        document["content"] = legacy.read_docx(Path(copied["recovered"]))
                        document["font_size_audit"] = explicit_font_sizes(Path(copied["recovered"]))
                        document["paragraph_comparison"] = legacy.exact_paragraph_check(source_content["paragraphs"], document["content"]["paragraphs"]) if source_content is not None else {"unavailable": "shared source no longer bound to original hash"}
                    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as error:
                        document["read_error"] = str(error)
                    row["documents"].append(document)
            final_path = batch / (native_id + ".final.txt")
            row["final_present"] = final_path.is_file()
            row["final_text"] = None
            if final_path.is_file():
                row["final_snapshot"] = copy_bound(final_path, call_out / "native.final.txt")
                row["final_text"] = Path(row["final_snapshot"]["recovered"]).read_text(encoding="utf-8-sig")
            row["native_evidence"] = [
                copy_bound(artifact, call_out / "native-evidence" / artifact.name)
                for artifact in sorted(batch.glob(native_id + ".*"))
                if artifact.is_file() and artifact not in {result_path, final_path}
            ]
            row.update(bind_delivery(row["final_text"], workspace, allowed, row["documents"], received))
            calls.append(row)
    inventory = {"stage": "collected-after-parent-completion", "expected_calls": 4, "result_records": len(calls),
                 "shared_source_before": shared_source, "shared_source_after_collection": input_integrity(SOURCE),
                 "source_snapshot": source_snapshot, "batches": batches, "calls": calls,
                 "qa_state": "COLLECTED_NOT_RENDERED; facts and readability remain separate"}
    legacy.write_json(OUT / "artifact-inventory.json", inventory)
    index = {"stage": inventory["stage"], "collection_root": str(OUT), "inventory": str(OUT / "artifact-inventory.json"),
             "inventory_sha256": legacy.sha256(OUT / "artifact-inventory.json"),
             "selection": "only final-linked separately-saved DOCX with stable copies and readable XML",
             "calls": [{"id": row["id"], "documents": [doc for doc in row["documents"] if doc["render_eligible"]]} for row in calls],
             "visual_review_status": "NOT_PERFORMED"}
    legacy.write_json(OUT / "collection-index.json", index)
    print(json.dumps({"calls": len(calls), "documents": sum(len(row["documents"]) for row in calls),
                      "render_selected": sum(row["render_selected_docx"] for row in calls), "stage": "collected, not rendered"}, ensure_ascii=False))


def pages() -> None:
    index = json.loads((OUT / "collection-index.json").read_text(encoding="utf-8-sig"))
    if index.get("stage") != "collected-after-parent-completion":
        raise RuntimeError("no parent-completed collection")
    if legacy.sha256(OUT / "artifact-inventory.json") != index["inventory_sha256"]:
        raise RuntimeError("inventory changed after render selection")
    legacy.OUT = OUT  # Reuse the existing page converter, never the R17 collection.
    legacy.pages()
    inventory = json.loads((OUT / "artifact-inventory.json").read_text(encoding="utf-8-sig"))
    legacy.write_json(OUT / "source-integrity-after-render.json", {
        "shared_source": input_integrity(SOURCE),
        "received_inputs": [{"id": row["id"], "at_collection": row["received_input"],
                             "after_render": input_integrity(Path(row["received_input"]["path"]))} for row in inventory["calls"]],
        "visual_review": "PENDING_EVERY_PAGE_INSPECTION; extracted text is not readability proof",
    })


def self_test() -> None:
    folder = OUT / "preparation/helper-fixtures"
    workspace, temporary = folder / "workspace", folder / "tmp"
    workspace.mkdir(parents=True, exist_ok=True)
    temporary.mkdir(parents=True, exist_ok=True)
    documents = []
    for number, name in enumerate(("received-application.docx", "另存申请.docx", "debug.docx"), 1):
        path = workspace / name
        xml = f'<w:document xmlns:w="{legacy.W[1:-1]}"><w:body><w:p><w:r><w:rPr><w:sz w:val="{0 if number != 2 else 32}"/><w:szCs w:val="0"/></w:rPr><w:t>原有正文。</w:t></w:r></w:p></w:body></w:document>'
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", xml)
        documents.append({"original": str(path), "recovered": str(path), "document_id": str(number),
                          "docx_sha256": legacy.sha256(path), "source_copy_hash_match": True})
    final = "[另存稿](另存申请.docx)\n[原文件](received-application.docx)"
    bound = bind_delivery(final, workspace, [workspace, temporary], documents, workspace / SOURCE.name)
    assert bound["render_selected_docx"] == 1 and [doc["document_id"] for doc in documents if doc["render_eligible"]] == ["2"]
    assert documents[0]["role"] == "received-input" and documents[2]["role"] == "unlinked-docx-debug-or-intermediate"
    assert bind_delivery(None, workspace, [workspace, temporary], documents, workspace / SOURCE.name)["render_selected_docx"] == 0
    assert bind_delivery("[missing](missing.docx)", workspace, [workspace, temporary], documents, workspace / SOURCE.name)["delivery_status"] == "NO_SEPARATELY_SAVED_WORD_LINK"
    assert not legacy.resolve_link(str(ROOT / "outside.docx"), workspace, [workspace, temporary], documents)["resolved"]
    assert len(explicit_font_sizes(workspace / SOURCE.name)["direct_zero_sz_runs"]) == 1
    repaired = explicit_font_sizes(workspace / "另存申请.docx")
    assert not repaired["direct_zero_sz_runs"] and len(repaired["direct_zero_szCs_runs"]) == 1
    assert legacy.read_docx(workspace / "另存申请.docx")["paragraphs"] == ["原有正文。"]
    assert input_integrity(workspace / SOURCE.name)["status"] == "CHANGED"
    try:
        collect(False)
    except RuntimeError:
        pass
    else:
        raise AssertionError("collection ran without completion flag")
    import pdf2image
    import pypdf
    assert (legacy.POPLER / "pdftoppm.exe").is_file() and (legacy.POPLER / "pdfinfo.exe").is_file()
    legacy.write_json(OUT / "preparation/helper-result.json", {
        "status": "PASS", "checks": ["received/debug DOCX excluded from render selection", "exact final link binding",
        "missing final and unresolved link kept separate", "outside path refused", "direct sz versus szCs recorded separately",
        "legacy paragraph reader reused", "changed input recorded as integrity", "completion flag required", "page dependencies available"],
        "actual_native_collection": False, "Word_started": False, "rendered_native_documents": 0,
        "interpreter": sys.executable, "shared_source": input_integrity(SOURCE), "legacy_qa_sha256": legacy.sha256(LEGACY_PATH),
    })
    print("PREPARATION PASS: helper checks only; no native collection or Word rendering")


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    collector = commands.add_parser("collect")
    collector.add_argument("--completed-batches", action="store_true", required=True)
    commands.add_parser("pages")
    commands.add_parser("self-test")
    args = parser.parse_args()
    if args.command == "collect":
        collect(args.completed_batches)
    elif args.command == "pages":
        pages()
    else:
        self_test()


if __name__ == "__main__":
    main()
