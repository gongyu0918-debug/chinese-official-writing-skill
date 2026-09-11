"""Offline technical audit and allowlisted evidence archive for the feature batch.

This script reads receipts and compact tool traces only; it never calls a model.
The archive intentionally excludes homes, caches, auth state and workspaces.
Source manuscripts, stdout, receipts, traces, pure run configuration and cold
packets are copied by filename allowlist, leaving the original output untouched.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EXPECTED_WRITERS = {
    "alibaba-token-plan/qwen3.8-flash",
    "alibaba-token-plan-2/qwen3.8-flash",
}
EXPECTED_NEW_LEAF = "references/speech-person-order.md"
EDIT_CASES = ("respectful_local", "formal_letter_control")
KEEP_FILES = {
    "freeze.json", "writer-dispatch.json", "confirmation-dispatch.json", "batch-smoke.json", "batch-remaining.json",
    "plan.json", "preregister.md", "cold-instructions.md", "model-registry.json", "command.json",
    "source-manifest.json", "receipt.json", "tool-trace.json", "stdout.jsonl", "stderr.txt", "final.md",
    "prompt.txt", "parsed-review.json", "cold-review.json", "cold-receipt.json", "packet.json", "instructions.md",
    "mapping.json", "anonymous-mapping.json", "network.jsonl", "system-settings.json", "system-defaults.json",
    "loopback-only.cjs",
    "harness_cold_receipts.json", "availability-initial-results.json", "availability-preregister.json",
    "availability-task.txt",
    "baseline-install-check.json", "engineering-result.md", "root-adjudication.md", "scope-clarification.md",
}
EXCLUDE_DIRS = {"home", ".qwen", "cache", "auth", "workspace", ".git", "node_modules"}
KEEP_DIRS = {"prompts", "cold-packets", "cold-mappings", "anonymous", "mappings", "frozen", "availability"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def path_from_input(value, base):
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    if any(x in value for x in ("*", "?", "[")):
        # A glob pattern is still bounded by its non-wildcard parent.
        prefix = value
        while any(x in prefix for x in ("*", "?", "[")):
            prefix = str(Path(prefix).parent)
        value = prefix
    path = Path(value)
    return (path if path.is_absolute() else base / path).resolve()


def trace_boundary(trace_path, receipt):
    # The receipt is stored beside tool-trace.json; newer frozen receipts do
    # not repeat the absolute artifact path, avoiding a second path authority.
    run = trace_path.parent.resolve()
    workspace, snapshot = run / "workspace", run / "workspace/input"
    rows, violations, new_leaf = [], [], []
    trace = load(trace_path)
    for item in trace:
        call = item.get("call", {})
        name, inputs = call.get("name"), call.get("input", {})
        if not isinstance(inputs, dict):
            inputs = {}
        # These are the only input fields that designate a filesystem path.
        path_fields = [key for key in ("file_path", "path", "target_directory", "directory", "cwd") if key in inputs]
        paths = [(key, path_from_input(inputs[key], workspace)) for key in path_fields]
        paths = [(key, value) for key, value in paths if value is not None]
        allowed_tools = {"read_file", "glob", "grep_search", "skill"}
        if name not in allowed_tools:
            violations.append({"name": name, "reason": "tool_not_in_read_only_allowlist"})
        for key, path in paths:
            if not within(path, workspace):
                violations.append({"name": name, "field": key, "reason": "path_outside_workspace"})
        if name == "skill" and not paths:
            # Qwen's skill input is a name rather than a file path; resolution is
            # bounded by this fresh workspace's skill root and later read traces.
            rows.append({"name": name, "input": inputs, "scope": "workspace_skill_resolution"})
        else:
            rows.append({"name": name, "input": inputs,
                         "paths": [{"field": key, "relative": path.relative_to(workspace).as_posix() if within(path, workspace) else None,
                                    "within_workspace": within(path, workspace),
                                    "within_input": within(path, snapshot)} for key, path in paths]})
        for key, path in paths:
            if name == "read_file" and within(path, snapshot):
                relative = path.relative_to(snapshot).as_posix()
                page = {"relative_path": relative, "offset": inputs.get("offset"), "limit": inputs.get("limit"),
                        "success": all(not result.get("is_error", False) for result in item.get("results", [])),
                        "result_sha256": item.get("result_sha256", [])}
                if relative == EXPECTED_NEW_LEAF:
                    new_leaf.append(page)
                rows[-1].setdefault("read_pages", []).append(page)
    return {"calls": rows, "violations": violations, "new_leaf_reads": new_leaf}


def writer_receipts(out):
    files = sorted(out.glob("runs/*/*/*/attempt-1/receipt.json"))
    if len(files) != 16:
        raise AssertionError(f"Expected 16 feature writer receipts, found {len(files)}")
    records, pair_map = [], {}
    for path in files:
        receipt = load(path)
        route, case, arm = receipt["model_requested"], path.parts[-4], path.parts[-3]
        if route not in EXPECTED_WRITERS or receipt["actual_client_model"] != route:
            raise AssertionError(f"Route mismatch in {path}")
        if receipt["init"]["qwen_code_version"] != "0.22.0":
            raise AssertionError(f"Qwen Code version mismatch in {path}")
        audit = trace_boundary(path.parent / "tool-trace.json", receipt)
        record = {"path": path.relative_to(out).as_posix(), "case": case, "arm": arm, "route": route,
                  "status": receipt["status"], "technical_valid": receipt["technical_valid"],
                  "api_error_placeholder": receipt["api_error_placeholder"], "init_version": receipt["init"]["qwen_code_version"],
                  "configured_effort": receipt["configured_effort"], "read_calls": receipt["read_calls"],
                  "successful_read_calls": receipt["successful_read_calls"], "tool_calls_count": receipt["tool_calls_count"],
                  "read_boundary_violations": audit["violations"], "actual_read_pages": [p for c in audit["calls"] for p in c.get("read_pages", [])],
                  "new_leaf_reads": audit["new_leaf_reads"], "final_sha256": receipt["hashes"]["final.md"],
                  "receipt_sha256": digest(path), "snapshot_unchanged": receipt["snapshot_unchanged"]}
        records.append(record)
        pair_map.setdefault(case, {})[arm] = record
    technical_failures = [r for r in records if r["status"] != "COMPLETE" or not r["technical_valid"]
                          or r["api_error_placeholder"] or r["read_boundary_violations"] or not r["snapshot_unchanged"]]
    edits = {}
    for case in EDIT_CASES:
        arms = pair_map.get(case, {})
        values = {}
        for arm, record in arms.items():
            final = out / record["path"].replace("/receipt.json", "/final.md")
            values[arm] = {"path": final.relative_to(out).as_posix(), "sha256": digest(final), "bytes": final.stat().st_size}
        edits[case] = {"arms": values, "byte_identical": len(values) == 2 and len({v["sha256"] for v in values.values()}) == 1}
    return {"expected_calls": 16, "observed_calls": len(records), "technical_failures": technical_failures,
            "all_technical_boundaries_pass": not technical_failures, "exact_edit_pairs": edits,
            "new_leaf_trigger_by_call": [{"case": r["case"], "arm": r["arm"], "route": r["route"],
                                           "read_count": len(r["new_leaf_reads"]), "reads": r["new_leaf_reads"]} for r in records],
            "records": records}


def verify(args):
    out = args.out.resolve()
    freeze = load(out / "freeze.json")
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "scope": "feature writer technical audit only",
              "out": str(out), "baseline_commit": freeze["commits"]["baseline"],
              "candidate_commit": freeze["commits"]["candidate"], "freeze_sha256": digest(out / "freeze.json"),
              "writer": writer_receipts(out)}
    target = args.report.resolve() if args.report else HERE / "writer-technical-report.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(target), "calls": report["writer"]["observed_calls"],
                      "technical_pass": report["writer"]["all_technical_boundaries_pass"]}), flush=True)


def copy_allowlist(source, destination):
    source, destination = source.resolve(), destination.resolve()
    if not source.is_dir():
        return 0
    copied = []
    for path in sorted(source.rglob("*")):
        if not path.is_file() or any(part.lower() in EXCLUDE_DIRS for part in path.relative_to(source).parts):
            continue
        relative = path.relative_to(source)
        first = relative.parts[0].lower() if relative.parts else ""
        if (path.name not in KEEP_FILES and not first in KEEP_DIRS
                and not path.name.startswith("harness_")
                and path.name not in {"make_pair_packet.py", "availability_probe.py"}):
            continue
        dest = destination / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        copied.append({"source": path.as_posix(), "destination": dest.relative_to(destination.parent).as_posix(),
                       "bytes": path.stat().st_size, "source_sha256": digest(path), "sha256": digest(dest)})
    return copied


def archive(args):
    out, destination = args.out.resolve(), args.destination.resolve()
    if destination == out or within(destination, out) or destination.exists():
        raise SystemExit("Archive destination must be a new directory outside OUT")
    destination.mkdir(parents=True)
    copied = copy_allowlist(out, destination / "feature-output")
    for index, extra in enumerate(args.extra_root or (), 1):
        copied.extend(copy_allowlist(Path(extra), destination / f"extra-{index}"))
    for item in copied:
        target = destination / item["destination"]
        if item["bytes"] != target.stat().st_size or item["sha256"] != digest(target):
            raise AssertionError(f"Destination hash changed during archive: {target}")
    file_paths = sorted(item["destination"] for item in copied)
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "source": str(out),
                "destination": str(destination), "copied_files": len(copied), "files": copied,
                "excluded_directory_names": sorted(EXCLUDE_DIRS), "allowlisted_filenames": sorted(KEEP_FILES)}
    manifest_path = destination / "archive-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    zip_path = destination.with_suffix(".zip")
    if zip_path.exists():
        raise SystemExit("Archive ZIP already exists; refusing overwrite")
    zip_members = file_paths + ["archive-manifest.json"]
    with zipfile.ZipFile(zip_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in file_paths:
            archive.write(destination / relative, relative)
        archive.write(manifest_path, "archive-manifest.json")
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = sorted(archive.namelist())
        if names != sorted(zip_members):
            raise AssertionError("ZIP member set differs from allowlisted destination files")
        for item in copied:
            data = archive.read(item["destination"])
            if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise AssertionError(f"ZIP readback hash mismatch: {item['destination']}")
        if archive.read("archive-manifest.json") != manifest_path.read_bytes():
            raise AssertionError("ZIP archive-manifest.json differs from external manifest")
    receipt = {"created_utc": datetime.now(timezone.utc).isoformat(), "zip_path": str(zip_path),
               "zip_sha256": digest(zip_path), "zip_file_count": len(names),
               "destination_readback_verified": True, "zip_readback_verified": True,
               "manifest_sha256": digest(manifest_path), "manifest_path": str(manifest_path)}
    receipt_path = destination / "archive-receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"destination": str(destination), "copied_files": len(copied), "manifest": str(manifest_path),
                      "zip": str(zip_path), "zip_file_count": len(names), "readback_verified": True,
                      "receipt": str(receipt_path)}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("verify")
    check.add_argument("--out", type=Path, required=True)
    check.add_argument("--report", type=Path)
    pack = sub.add_parser("archive")
    pack.add_argument("--out", type=Path, required=True)
    pack.add_argument("--destination", type=Path, required=True)
    pack.add_argument("--extra-root", type=Path, action="append")
    args = parser.parse_args()
    if args.action == "verify":
        verify(args)
    else:
        archive(args)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
