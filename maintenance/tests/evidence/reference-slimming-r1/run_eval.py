from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
OUTPUT_BASE = REPO / "output" / "reference-slimming-r1"
UPSTREAM_PATH = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def experiment_config(experiment_id: str) -> dict:
    config = load_config()
    try:
        return config["experiments"][experiment_id]
    except KeyError as exc:
        raise RuntimeError(f"unknown experiment: {experiment_id}") from exc


def output_root(experiment_id: str) -> Path:
    return OUTPUT_BASE / experiment_id


def load_writer(experiment_id: str):
    writer = load_module(f"reference_slimming_writer_{experiment_id}", UPSTREAM_PATH)
    writer.REPO = REPO
    writer.CASES_PATH = CASES_PATH
    writer.OUTPUT_ROOT = output_root(experiment_id)
    return writer


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def export_skill(commit: str, destination: Path, staging: Path) -> None:
    archive = staging / f"{commit}.zip"
    extracted = staging / commit
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={archive}", commit, "chinese-official-writing"],
        cwd=REPO,
        check=True,
    )
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(extracted)
    shutil.copytree(extracted / "chinese-official-writing", destination)


def prepare(experiment_id: str, baseline_ref: str, candidate_ref: str) -> dict:
    root = output_root(experiment_id)
    if root.exists():
        raise RuntimeError(f"output already exists: {root}")
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")

    config = load_config()
    experiment = experiment_config(experiment_id)
    baseline = git_text("rev-parse", f"{baseline_ref}^{{commit}}")
    candidate = git_text("rev-parse", f"{candidate_ref}^{{commit}}")
    changed_product = set(
        filter(
            None,
            git_text("diff", "--name-only", baseline, candidate, "--", "chinese-official-writing").splitlines(),
        )
    )
    allowed = set(experiment["allowed_product_diff"])
    if changed_product != allowed:
        raise RuntimeError(
            f"unexpected product diff: actual={sorted(changed_product)} expected={sorted(allowed)}"
        )

    writer = load_writer(experiment_id)
    staging = root / "staging"
    staging.mkdir(parents=True)
    exports: dict[str, Path] = {}
    fixture = {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "baseline_commit": baseline,
        "candidate_commit": candidate,
        "changed_product": sorted(changed_product),
        "providers": config["providers"],
        "arms": {},
    }
    for arm, commit in (("baseline", baseline), ("candidate", candidate)):
        exported = root / "exports" / arm
        exported.parent.mkdir(parents=True, exist_ok=True)
        export_skill(commit, exported, staging)
        count, fingerprint = writer.tree_fingerprint(exported)
        sizes = {}
        for relative in experiment["tracked_files"]:
            path = exported / relative
            sizes[relative] = path.stat().st_size if path.is_file() else 0
        fixture["arms"][arm] = {
            "commit": commit,
            "file_count": count,
            "tree_fingerprint": fingerprint,
            "tracked_file_bytes": sizes,
        }
        exports[arm] = exported

    for provider_id in config["providers"]:
        for arm, exported in exports.items():
            runtime = writer.runtime_root(provider_id, arm)
            skill_root = runtime / ".agents" / "skills" / "chinese-official-writing"
            skill_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(exported, skill_root)
            subprocess.run(["git", "init", "-q", str(runtime)], check=True)

    shutil.rmtree(staging)
    (root / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return fixture


def trace_commands(trace: str) -> list[str]:
    commands = []
    for line in trace.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = payload.get("item")
        if (
            isinstance(item, dict)
            and item.get("type") == "command_execution"
            and item.get("status") == "completed"
            and item.get("exit_code") == 0
        ):
            command = item.get("command")
            if isinstance(command, str):
                commands.append(command)
    return commands


def read_files_from_trace(trace: str, runtime: Path) -> tuple[list[str], int]:
    normalized = "\n".join(trace_commands(trace)).replace("\\", "/")
    matches = set()
    pattern = re.compile(r"(?i)(?:^|[/'\"])(SKILL\.md|references/[A-Za-z0-9_.-]+\.md)")
    for match in pattern.finditer(normalized):
        relative = match.group(1)
        relative = "SKILL.md" if relative.casefold() == "skill.md" else relative
        path = runtime / ".agents" / "skills" / "chinese-official-writing" / relative
        if path.is_file():
            matches.add(relative)
    ordered = sorted(matches)
    loaded_bytes = sum(
        (runtime / ".agents" / "skills" / "chinese-official-writing" / relative).stat().st_size
        for relative in ordered
    )
    return ordered, loaded_bytes


def missing_groups(groups: list[list[str]], final: str) -> list[str]:
    compact = "".join(final.split())
    return ["|".join(group) for group in groups if not any("".join(value.split()) in compact for value in group)]


def evaluate_route_rule(rule: dict, baseline: dict, candidate: dict) -> dict:
    baseline_files = set(baseline["skill_files_read"])
    candidate_files = set(candidate["skill_files_read"])
    failures = []
    for relative in rule.get("baseline_all", []):
        if relative not in baseline_files:
            failures.append(f"baseline_missing:{relative}")
    for relative in rule.get("candidate_all", []):
        if relative not in candidate_files:
            failures.append(f"candidate_missing:{relative}")
    for relative in rule.get("candidate_none", []):
        if relative in candidate_files:
            failures.append(f"candidate_unexpected:{relative}")
    if rule.get("require_negative_delta") and candidate["tracked_loaded_bytes"] >= baseline["tracked_loaded_bytes"]:
        failures.append("candidate_not_lower_bytes")
    return {"kind": rule["kind"], "passed": not failures, "failures": failures}


def run_provider(experiment_id: str, provider_id: str) -> dict:
    root = output_root(experiment_id)
    if not (root / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    config = load_config()
    experiment = experiment_config(experiment_id)
    if provider_id not in config["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    result_path = root / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)

    writer = load_writer(experiment_id)
    provider_index = list(config["providers"]).index(provider_id)
    arm_order = ["baseline", "candidate"] if provider_index % 2 == 0 else ["candidate", "baseline"]
    records = []
    for case in experiment["cases"]:
        for arm in arm_order:
            record = writer.run_one(
                provider_id,
                config["providers"][provider_id],
                arm,
                case,
                config["reasoning_effort"],
            )
            trace_path = root / record["trace_file"]
            trace = trace_path.read_text(encoding="utf-8", errors="replace")
            files, loaded_bytes = read_files_from_trace(trace, writer.runtime_root(provider_id, arm))
            record["experiment_id"] = experiment_id
            record["skill_files_read"] = files
            record["tracked_loaded_bytes"] = loaded_bytes
            final_path = root / record["final_file"]
            final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
            record["output_shape_failures"] = missing_groups(case.get("output_shape_groups", []), final)
            records.append(record)
            result_path.write_text(
                json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
                encoding="utf-8",
                newline="\n",
            )
    return {"provider_id": provider_id, "records": records}


def summarize(experiment_id: str) -> dict:
    root = output_root(experiment_id)
    config = load_config()
    experiment = experiment_config(experiment_id)
    records = []
    missing = []
    for provider_id in config["providers"]:
        path = root / "providers" / f"{provider_id}.json"
        if path.is_file():
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(provider_id)

    indexed = {(item["provider_id"], item["case_id"], item["arm"]): item for item in records}
    pairs = []
    for provider_id in config["providers"]:
        for case in experiment["cases"]:
            baseline = indexed.get((provider_id, case["id"], "baseline"))
            candidate = indexed.get((provider_id, case["id"], "candidate"))
            if baseline is None or candidate is None:
                continue
            pair = {
                    "provider_id": provider_id,
                    "case_id": case["id"],
                    "technical_ok": not baseline["technical_failures"] and not candidate["technical_failures"],
                    "baseline_files": baseline["skill_files_read"],
                    "candidate_files": candidate["skill_files_read"],
                    "baseline_loaded_bytes": baseline["tracked_loaded_bytes"],
                    "candidate_loaded_bytes": candidate["tracked_loaded_bytes"],
                    "loaded_bytes_delta": candidate["tracked_loaded_bytes"] - baseline["tracked_loaded_bytes"],
                    "baseline_hard_failures": baseline["hard_failures"],
                    "candidate_hard_failures": candidate["hard_failures"],
                    "baseline_chars": baseline["final_chars_nonspace"],
                    "candidate_chars": candidate["final_chars_nonspace"],
                    "candidate_output_shape_failures": candidate.get("output_shape_failures", []),
                    "route_checks": [],
            }
            for rule in experiment.get("route_rules", []):
                if case["id"] in rule["case_ids"]:
                    pair["route_checks"].append(evaluate_route_rule(rule, baseline, candidate))
            pairs.append(pair)
    summary = {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "missing_providers": missing,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "hard_failure_count_observation_only": sum(bool(item["hard_failures"]) for item in records),
        "route_check_pass_count": sum(
            check["passed"] for pair in pairs for check in pair["route_checks"] if check["kind"] == "target"
        ),
        "route_check_target_count": sum(
            1 for pair in pairs for check in pair["route_checks"] if check["kind"] == "target"
        ),
        "control_contamination_count": sum(
            not check["passed"]
            for pair in pairs
            for check in pair["route_checks"]
            if check["kind"] in {"control", "shape_control", "capability_control"}
        ),
        "pairs": pairs,
        "records": records,
    }
    (root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    config = load_config()
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", choices=tuple(config["experiments"]), required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", nargs=2, metavar=("BASELINE", "CANDIDATE"))
    action.add_argument("--provider", choices=tuple(config["providers"]))
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        result = prepare(args.experiment, args.prepare[0], args.prepare[1])
    elif args.provider:
        result = run_provider(args.experiment, args.provider)
    else:
        result = summarize(args.experiment)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
