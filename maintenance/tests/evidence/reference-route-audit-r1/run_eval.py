"""Frozen, no-Hook reference-route A/B using the existing isolated desktop writer."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
DEFAULT_OUTPUT = REPO / "output/reference-route-audit-r1/r1"
WRITER_PATH = REPO / "maintenance/tests/evidence/complaint-reflection-r1/desktop_writer.py"
PROBE_PATH = REPO / "maintenance/tests/evidence/reference-slimming-r2/run_probe.py"
ARMS = ("baseline", "candidate")
READ_COMMAND = re.compile(r"(?i)\b(?:get-content|cat|gc|type)\b|\.read_(?:text|bytes)\s*\(|\bopen\s*\(")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", check=True,
    ).stdout


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_writer(output: Path):
    return load_module("route_audit_desktop", WRITER_PATH).load_writer(REPO, CASES_PATH, output)


def frozen_cases(config: dict) -> dict:
    """Read the original prompts verbatim from the fixed baseline commit."""
    config = dict(config)
    source_path = Path(config["case_source"])
    prefix = config["baseline_commit"] + ":"
    source = json.loads(git_text("show", prefix + source_path.as_posix()))
    indexed = {case["id"]: case for case in source["cases"]}
    config["cases"] = []
    for case_id in config["case_ids"]:
        case = dict(indexed[case_id])
        prompt_path = (source_path.parent / case["prompt_file"]).as_posix()
        case["prompt"] = git_text("show", prefix + prompt_path)
        case["prompt_sha256"] = hashlib.sha256(case["prompt"].encode("utf-8")).hexdigest()
        config["cases"].append(case)
    return config


def prepare(output: Path, candidate: str) -> dict:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing output: {output}")
    if git_text("status", "--porcelain").strip():
        raise RuntimeError("worktree must be clean before --prepare; commit the candidate and harness first")
    config = frozen_cases(json.loads(CASES_PATH.read_text(encoding="utf-8")))
    commits = {
        "baseline": git_text("rev-parse", f"{config['baseline_commit']}^{{commit}}").strip(),
        "candidate": git_text("rev-parse", f"{candidate}^{{commit}}").strip(),
    }
    if commits["baseline"] != config["baseline_commit"]:
        raise RuntimeError("baseline commit mismatch")
    writer = load_writer(output)
    sources = (CASES_PATH, Path(__file__), WRITER_PATH, PROBE_PATH, Path(writer.__file__))
    fixture = {
        "schema_version": 1, "harness_commit": git_text("rev-parse", "HEAD").strip(),
        "config": config, "arms": {}, "expected_records": len(config["providers"]) * len(config["cases"]) * 2,
        "hook_mode": "plugins disabled by desktop_writer; no install or activation; contamination invalidates the sample",
        "read_metric": "successful read-command paths; unique full-file bytes, an upper bound for partial reads, not tokens",
        "sources_sha256": {str(path.relative_to(REPO)): file_hash(path) for path in sources},
    }
    for arm, commit in commits.items():
        staging = output / "staging" / arm
        staging.mkdir(parents=True)
        exported = output / "exports" / arm
        exported.parent.mkdir(parents=True, exist_ok=True)
        writer.export_skill(commit, exported, staging)
        count, fingerprint = writer.tree_fingerprint(exported)
        fixture["arms"][arm] = {"commit": commit, "file_count": count, "tree_fingerprint": fingerprint}
        for provider in config["providers"]:
            runtime = writer.runtime_root(provider, arm)
            skill = runtime / ".agents/skills/chinese-official-writing"
            skill.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(exported, skill)
            subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    write_json(output / "fixture.json", fixture)
    return fixture


def load_fixture(output: Path) -> dict:
    path = output / "fixture.json"
    if not path.is_file():
        raise RuntimeError("run --prepare first")
    fixture = json.loads(path.read_text(encoding="utf-8"))
    for source, digest in fixture["sources_sha256"].items():
        if file_hash(REPO / source) != digest:
            raise RuntimeError(f"harness changed after preparation: {source}; use a new output root")
    return fixture


def observed_reads(trace: str, runtime: Path, probe) -> tuple[list[str], int, list[dict]]:
    successful, events = [], []
    for line_number, line in enumerate(trace.splitlines(), 1):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = payload.get("item", {})
        if (payload.get("type") != "item.completed" or item.get("type") != "command_execution"
                or item.get("exit_code") != 0 or not item.get("aggregated_output")
                or not READ_COMMAND.search(item.get("command", ""))):
            continue
        files, _ = probe.skill_reads(line, runtime)
        if files:
            successful.append(line)
            events.append({"trace_line": line_number, "files": files})
    files, loaded_bytes = probe.skill_reads("\n".join(successful), runtime)
    return files, loaded_bytes, events


def run_provider(output: Path, provider: str) -> dict:
    fixture = load_fixture(output)
    config = fixture["config"]
    if provider not in config["providers"]:
        raise RuntimeError(f"unknown provider: {provider}")
    result_path = output / "providers" / f"{provider}.json"
    # A provider is a single write owner; other providers may run concurrently.
    lock = result_path.with_suffix(".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("x", encoding="utf-8"):
        pass
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {"provider_id": provider, "records": []}
        if payload["provider_id"] != provider:
            raise RuntimeError("provider result mismatch")
        records = payload["records"]
        completed = {(item["case_id"], item["arm"]) for item in records}
        writer, probe = load_writer(output), load_module("route_audit_probe", PROBE_PATH)
        provider_index = list(config["providers"]).index(provider)
        for case_index, case in enumerate(config["cases"]):
            order = ARMS if (provider_index + case_index) % 2 == 0 else tuple(reversed(ARMS))
            for arm in order:
                if (case["id"], arm) in completed:
                    continue
                runtime = writer.runtime_root(provider, arm)
                skill = runtime / ".agents/skills/chinese-official-writing"
                if writer.tree_fingerprint(skill)[1] != fixture["arms"][arm]["tree_fingerprint"]:
                    raise RuntimeError(f"runtime snapshot changed: {provider}/{arm}")
                raw = output / "raw" / provider
                if list(raw.glob(f"{case['id']}-{arm}.*")):
                    raise RuntimeError(f"orphan raw evidence exists for {case['id']}/{arm}; preserve it and use a new output root")
                record = writer.run_one(provider, config["providers"][provider], arm, case, config["reasoning_effort"])
                trace_path = output / record["trace_file"]
                trace = trace_path.read_text(encoding="utf-8", errors="replace")
                files, size, events = observed_reads(trace, runtime, probe)
                record.update(atoms=case["atoms"], commit=fixture["arms"][arm]["commit"], skill_files_read=files,
                              loaded_bytes=size, read_events=events, prompt_sha256=case["prompt_sha256"],
                              trace_sha256=file_hash(trace_path), stderr_sha256=file_hash(output / record["stderr_file"]))
                if "SKILL.md" not in files:
                    record["technical_failures"].append("missing_successful_skill_read")
                if writer.tree_fingerprint(skill)[1] != fixture["arms"][arm]["tree_fingerprint"]:
                    record["technical_failures"].append("runtime_snapshot_changed")
                records.append(record)
                write_json(result_path, payload)
        return {"provider_id": provider, "record_count": len(records), "resumed_from": len(completed)}
    finally:
        lock.unlink()


def summarize(output: Path) -> dict:
    fixture = load_fixture(output)
    config, records = fixture["config"], []
    for provider in config["providers"]:
        path = output / "providers" / f"{provider}.json"
        if path.is_file():
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
    indexed = {(r["provider_id"], r["case_id"], r["arm"]): r for r in records}
    pairs, missing = [], []
    for provider in config["providers"]:
        for case in config["cases"]:
            arms = {arm: indexed.get((provider, case["id"], arm)) for arm in ARMS}
            missing.extend({"provider_id": provider, "case_id": case["id"], "arm": arm} for arm, r in arms.items() if r is None)
            if all(arms.values()):
                baseline, candidate = arms["baseline"], arms["candidate"]
                pairs.append({"provider_id": provider, "case_id": case["id"],
                              "both_technically_valid": not baseline["technical_failures"] and not candidate["technical_failures"],
                              "loaded_bytes_delta": candidate["loaded_bytes"] - baseline["loaded_bytes"],
                              "final_chars_delta": candidate["final_chars_nonspace"] - baseline["final_chars_nonspace"],
                              "files_removed": sorted(set(baseline["skill_files_read"]) - set(candidate["skill_files_read"])),
                              "files_added": sorted(set(candidate["skill_files_read"]) - set(baseline["skill_files_read"]))})
    summary = {"schema_version": 1, "arms": fixture["arms"], "expected_records": fixture["expected_records"],
               "record_count": len(records), "missing_runs": missing,
               "technical_failure_count": sum(bool(r["technical_failures"]) for r in records),
               "hard_failure_count_observation_only": sum(bool(r["hard_failures"]) for r in records),
               "read_metric": fixture["read_metric"], "pairs": pairs, "records": records}
    write_json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider")
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--candidate", default="HEAD", help="candidate commit/ref, resolved and frozen only by --prepare")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output_root.resolve()
    result = prepare(output, args.candidate) if args.prepare else run_provider(output, args.provider) if args.provider else summarize(output)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
