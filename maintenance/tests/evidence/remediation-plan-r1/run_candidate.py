from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
CONFIG_PATH = HERE / "candidate-config.json"
OUTPUT_ROOT = REPO / "output/remediation-plan-r1/candidate-r1"
BASELINE_OUTPUT = REPO / "output/remediation-plan-r1/baseline"
WRITER_OUTPUT_ROOT = BASELINE_OUTPUT
BASELINE_RUNNER_PATH = HERE / "run_baseline.py"


def load_baseline_runner():
    spec = importlib.util.spec_from_file_location("wr028_candidate_base", BASELINE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {BASELINE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_inputs() -> tuple[dict, dict, list[dict]]:
    baseline = load_baseline_runner()
    cases_config = baseline.load_cases()
    candidate_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    indexed = {case["id"]: case for case in cases_config["cases"]}
    cases = [indexed[case_id] for case_id in candidate_config["case_ids"]]
    return cases_config, candidate_config, cases


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout.strip()


def load_writer():
    baseline = load_baseline_runner()
    baseline.OUTPUT_ROOT = WRITER_OUTPUT_ROOT
    base = baseline.load_base_runner()
    return base, base.load_writer()


def recover_record(provider_id: str, model: str, case: dict, effort: str, writer) -> dict | None:
    root = writer.runtime_root(provider_id, "candidate")
    raw = WRITER_OUTPUT_ROOT / "raw" / provider_id
    stem = f"{case['id']}-candidate"
    final_path = raw / f"{stem}.final.txt"
    trace_path = raw / f"{stem}.trace.jsonl"
    stderr_path = raw / f"{stem}.stderr.txt"
    if not (final_path.is_file() and trace_path.is_file() and stderr_path.is_file()):
        return None

    final = final_path.read_text(encoding="utf-8", errors="replace")
    stdout = trace_path.read_text(encoding="utf-8", errors="replace")
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    commands = writer.normalized_commands(stdout)
    exact_skill = (root / ".agents/skills/chinese-official-writing/SKILL.md").as_posix().casefold()
    exact_seen = exact_skill in commands or ".agents/skills/chinese-official-writing/skill.md" in commands
    global_seen = [
        path.as_posix() for path in writer.USER_SKILLS if path.as_posix().casefold() in commands
    ]
    combined_log = f"{stdout}\n{stderr}".casefold()
    hook_markers = [
        marker
        for marker in (
            "<hook_prompt",
            "chinese-official-writing@chinese-official-writing-local:hooks/",
            "official-writing-pro@official-writing-pro-local:hooks/",
        )
        if marker in combined_log
    ]
    completed_trace = '"type":"turn.completed"' in stdout
    technical = []
    if not completed_trace:
        technical.append("recovered_trace_incomplete")
    if not final.strip():
        technical.append("missing_final")
    if not exact_seen:
        technical.append("missing_exact_skill_trace")
    if global_seen:
        technical.append("user_skill_contamination")
    if hook_markers:
        technical.append("hook_contamination")
    body_chars = len(writer.compact(final))
    return {
        "provider_id": provider_id,
        "model": model,
        "case_id": case["id"],
        "arm": "candidate",
        "return_code": 0 if completed_trace else None,
        "seconds": None,
        "codex_path": None,
        "codex_version": None,
        "exact_skill_trace": exact_seen,
        "user_skill_paths_in_trace": global_seen,
        "hook_contamination_markers": hook_markers,
        "technical_failures": technical,
        "hard_failures": [] if technical else writer.hard_failures(case, final),
        "prompt_chars_nonspace": len(writer.compact(case["prompt"])),
        "material_chars_nonspace": len(writer.compact(case["material"])),
        "final_chars_nonspace": body_chars,
        "shorter_than_prompt": body_chars < len(writer.compact(case["prompt"])),
        "shorter_than_material": body_chars < len(writer.compact(case["material"])),
        "quality_markers_present": [
            marker for marker in case["quality_markers"] if marker in final
        ],
        "usage": writer.trace_usage(stdout),
        "final_sha256": writer.sha256_bytes(final.encode("utf-8")) if final else None,
        "final_file": str(final_path.relative_to(WRITER_OUTPUT_ROOT)),
        "trace_file": str(trace_path.relative_to(WRITER_OUTPUT_ROOT)),
        "stderr_file": str(stderr_path.relative_to(WRITER_OUTPUT_ROOT)),
        "recovered_after_runner_path_error": True,
    }


def prepare() -> dict:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")
    cases_config, config, cases = load_inputs()
    baseline = git_text("rev-parse", f"{config['baseline_commit']}^{{commit}}")
    candidate = git_text("rev-parse", f"{config['candidate_commit']}^{{commit}}")
    changed = set(
        filter(
            None,
            git_text(
                "diff", "--name-only", baseline, candidate, "--", "chinese-official-writing"
            ).splitlines(),
        )
    )
    expected = set(config["allowed_product_diff"])
    if changed != expected:
        raise RuntimeError(f"unexpected product diff: actual={sorted(changed)} expected={sorted(expected)}")

    _, writer = load_writer()
    staging = OUTPUT_ROOT / "staging"
    exported = OUTPUT_ROOT / "exports/candidate"
    staging.mkdir(parents=True)
    exported.parent.mkdir(parents=True, exist_ok=True)
    writer.export_skill(candidate, exported, staging)
    count, fingerprint = writer.tree_fingerprint(exported)
    for provider_id in cases_config["providers"]:
        runtime = writer.runtime_root(provider_id, "candidate")
        skill_root = runtime / ".agents/skills/chinese-official-writing"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(exported, skill_root)
        subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    shutil.rmtree(staging)
    fixture = {
        "schema_version": 1,
        "baseline_commit": baseline,
        "candidate_commit": candidate,
        "changed_product": sorted(changed),
        "file_count": count,
        "tree_fingerprint": fingerprint,
        "providers": cases_config["providers"],
        "case_ids": [case["id"] for case in cases],
    }
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return fixture


def run_provider(provider_id: str) -> dict:
    cases_config, _, cases = load_inputs()
    if provider_id not in cases_config["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    records = []
    if result_path.exists():
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        if payload.get("provider_id") != provider_id:
            raise RuntimeError(f"provider result mismatch: {result_path}")
        records = payload.get("records", [])
    base, writer = load_writer()
    completed = {record["case_id"] for record in records}
    for case in cases:
        if case["id"] in completed:
            continue
        recovered = recover_record(
            provider_id,
            cases_config["providers"][provider_id],
            case,
            cases_config["reasoning_effort"],
            writer,
        )
        if recovered is not None:
            recovered["atoms"] = case["atoms"]
            files, loaded_bytes = base.skill_reads(
                (WRITER_OUTPUT_ROOT / recovered["trace_file"]).read_text(
                    encoding="utf-8", errors="replace"
                ),
                writer.runtime_root(provider_id, "candidate"),
            )
            recovered["skill_files_read"] = files
            recovered["loaded_bytes"] = loaded_bytes
            records.append(recovered)
            completed.add(case["id"])
    result_path.write_text(
        json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    for case in cases:
        if case["id"] in completed:
            continue
        record = writer.run_one(
            provider_id,
            cases_config["providers"][provider_id],
            "candidate",
            case,
            cases_config["reasoning_effort"],
        )
        trace = (WRITER_OUTPUT_ROOT / record["trace_file"]).read_text(
            encoding="utf-8", errors="replace"
        )
        files, loaded_bytes = base.skill_reads(trace, writer.runtime_root(provider_id, "candidate"))
        record["atoms"] = case["atoms"]
        record["skill_files_read"] = files
        record["loaded_bytes"] = loaded_bytes
        record["recovered_after_runner_path_error"] = False
        records.append(record)
        result_path.write_text(
            json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
    return {
        "provider_id": provider_id,
        "record_count": len(records),
        "resumed_from": len(completed),
        "artifact_root": str(WRITER_OUTPUT_ROOT.relative_to(REPO)),
    }


def summarize() -> dict:
    cases_config, config, cases = load_inputs()
    pairs = []
    missing = []
    for provider_id in cases_config["providers"]:
        baseline_path = BASELINE_OUTPUT / "providers" / f"{provider_id}.json"
        candidate_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if not baseline_path.is_file() or not candidate_path.is_file():
            missing.append(provider_id)
            continue
        baseline_records = {
            item["case_id"]: item
            for item in json.loads(baseline_path.read_text(encoding="utf-8"))["records"]
        }
        candidate_records = {
            item["case_id"]: item
            for item in json.loads(candidate_path.read_text(encoding="utf-8"))["records"]
        }
        for case in cases:
            baseline_record = baseline_records[case["id"]]
            candidate_record = candidate_records[case["id"]]
            pairs.append(
                {
                    "provider_id": provider_id,
                    "case_id": case["id"],
                    "technical_ok": not baseline_record["technical_failures"]
                    and not candidate_record["technical_failures"],
                    "baseline_technical_failures": baseline_record["technical_failures"],
                    "candidate_technical_failures": candidate_record["technical_failures"],
                    "baseline_files": baseline_record["skill_files_read"],
                    "candidate_files": candidate_record["skill_files_read"],
                    "baseline_loaded_bytes": baseline_record["loaded_bytes"],
                    "candidate_loaded_bytes": candidate_record["loaded_bytes"],
                    "loaded_bytes_delta": candidate_record["loaded_bytes"]
                    - baseline_record["loaded_bytes"],
                    "baseline_hard_failures": baseline_record["hard_failures"],
                    "candidate_hard_failures": candidate_record["hard_failures"],
                    "baseline_chars": baseline_record["final_chars_nonspace"],
                    "candidate_chars": candidate_record["final_chars_nonspace"],
                    "baseline_file": baseline_record["final_file"],
                    "candidate_file": candidate_record["final_file"],
                }
            )
    read_counts = {}
    for case in cases:
        counter = Counter()
        for pair in pairs:
            if pair["case_id"] == case["id"] and not pair["candidate_technical_failures"]:
                counter.update(pair["candidate_files"])
        read_counts[case["id"]] = dict(sorted(counter.items()))
    summary = {
        "schema_version": 1,
        "baseline_commit": config["baseline_commit"],
        "candidate_commit": config["candidate_commit"],
        "missing_providers": missing,
        "pair_count": len(pairs),
        "technical_pair_count": sum(pair["technical_ok"] for pair in pairs),
        "candidate_read_counts": read_counts,
        "candidate_artifact_root": str(WRITER_OUTPUT_ROOT.relative_to(REPO)),
        "pairs": pairs,
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    providers = tuple(load_inputs()[0]["providers"])
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=providers)
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        result = prepare()
    elif args.provider:
        result = run_provider(args.provider)
    else:
        result = summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
