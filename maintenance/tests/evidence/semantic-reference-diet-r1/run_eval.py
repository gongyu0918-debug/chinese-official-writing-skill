from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
OUTPUT_ROOT = REPO / "output" / "semantic-reference-diet-r1" / "semantic-ab-r2"
CATALOG = Path.home() / ".codex" / "opencodex-catalog.json"
USER_SKILLS = (
    Path.home() / ".agents/skills/chinese-official-writing/SKILL.md",
    Path.home() / ".codex/skills/chinese-official-writing/SKILL.md",
)


def compact(text: str) -> str:
    return "".join(text.split())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_fingerprint(root: Path) -> tuple[int, str]:
    lines = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        lines.append(f"{relative}:{sha256_bytes(path.read_bytes())}\n")
    return len(lines), sha256_bytes("".join(lines).encode("utf-8"))


def load_cases() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def runtime_root(provider_id: str, arm: str) -> Path:
    return OUTPUT_ROOT / "runtime" / provider_id / arm


def export_skill(tag: str, destination: Path, staging_root: Path) -> None:
    archive = staging_root / f"{tag}.zip"
    extracted = staging_root / tag
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={archive}", tag, "chinese-official-writing"],
        cwd=REPO,
        check=True,
    )
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(extracted)
    shutil.copytree(extracted / "chinese-official-writing", destination)


def prepare() -> dict:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    cases = load_cases()
    staging = OUTPUT_ROOT / "staging"
    staging.mkdir(parents=True)
    fixture = {"schema_version": 1, "arms": {}, "providers": list(cases["providers"])}

    exports: dict[str, Path] = {}
    for arm, arm_info in cases["arms"].items():
        exported = OUTPUT_ROOT / "exports" / arm
        exported.parent.mkdir(parents=True, exist_ok=True)
        export_skill(arm_info["tag"], exported, staging)
        resolved = subprocess.run(
            ["git", "rev-parse", f"{arm_info['tag']}^{{commit}}"],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip()
        if resolved != arm_info["commit"]:
            raise RuntimeError(f"tag mismatch for {arm}: {resolved}")
        count, fingerprint = tree_fingerprint(exported)
        fixture["arms"][arm] = {
            "tag": arm_info["tag"],
            "commit": resolved,
            "file_count": count,
            "tree_fingerprint": fingerprint,
        }
        exports[arm] = exported

    for provider_id in cases["providers"]:
        for arm, exported in exports.items():
            root = runtime_root(provider_id, arm)
            skill_root = root / ".agents" / "skills" / "chinese-official-writing"
            skill_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(exported, skill_root)
            subprocess.run(["git", "init", "-q", str(root)], check=True)

    shutil.rmtree(staging)
    fixture_path = OUTPUT_ROOT / "fixture.json"
    fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return fixture


def disabled_skills_config() -> str:
    entries = ",".join(f'{{path="{path.as_posix()}",enabled=false}}' for path in USER_SKILLS)
    return f"skills.config=[{entries}]"


def normalized_commands(trace: str) -> str:
    commands = []
    for line in trace.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = payload.get("item")
        if isinstance(item, dict) and item.get("type") == "command_execution":
            command = item.get("command")
            if isinstance(command, str):
                commands.append(command)
    return re.sub(r"/+", "/", "\n".join(commands).replace("\\", "/")).casefold()


def trace_usage(trace: str) -> dict:
    for line in reversed(trace.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") == "turn.completed" and isinstance(payload.get("usage"), dict):
            return payload["usage"]
    return {}


def hard_failures(case: dict, final: str) -> list[str]:
    body = compact(final)
    if not body:
        return ["empty_final"]
    failures = []
    for group in case["required_groups"]:
        if not any(compact(value) in body for value in group):
            failures.append("missing_any:" + "|".join(group))
    for value in case["forbidden"]:
        if compact(value) in body:
            failures.append("forbidden:" + value)
    if "```" in final or "读取Skill" in body or "核验过程" in body or "字符数" in body:
        failures.append("non_body_output")
    return failures


def run_one(provider_id: str, model: str, arm: str, case: dict, effort: str) -> dict:
    root = runtime_root(provider_id, arm)
    raw = OUTPUT_ROOT / "raw" / provider_id
    raw.mkdir(parents=True, exist_ok=True)
    stem = f"{case['id']}-{arm}"
    final_path = raw / f"{stem}.final.txt"
    trace_path = raw / f"{stem}.trace.jsonl"
    stderr_path = raw / f"{stem}.stderr.txt"
    command = [
        shutil.which("codex") or "codex",
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-C",
        str(root),
        "-m",
        model,
        "-c",
        'openai_base_url="http://127.0.0.1:10100/v1"',
        "-c",
        f'model_catalog_json="{CATALOG.as_posix()}"',
        "-c",
        f'model_reasoning_effort="{effort}"',
        "-c",
        disabled_skills_config(),
        "-s",
        "read-only",
        "--ephemeral",
        "--json",
        "--output-last-message",
        str(final_path),
        "-",
    ]
    print(f"START {provider_id} {case['id']} {arm}", flush=True)
    started = time.monotonic()
    error = None
    try:
        completed = subprocess.run(
            command,
            input=case["prompt"],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=900,
            check=False,
        )
        return_code = completed.returncode
        stdout, stderr = completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        return_code = None
        stdout, stderr = str(exc.stdout or ""), str(exc.stderr or "")
        error = "timeout_after_900_seconds"

    trace_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
    commands = normalized_commands(stdout)
    exact_skill = (root / ".agents/skills/chinese-official-writing/SKILL.md").as_posix().casefold()
    relative_skill = ".agents/skills/chinese-official-writing/skill.md"
    exact_seen = exact_skill in commands or relative_skill in commands
    global_seen = [path.as_posix() for path in USER_SKILLS if path.as_posix().casefold() in commands]
    technical = []
    if return_code != 0:
        technical.append("nonzero_exit")
    if error:
        technical.append(error)
    if not final.strip():
        technical.append("missing_final")
    if not exact_seen:
        technical.append("missing_exact_skill_trace")
    if global_seen:
        technical.append("user_skill_contamination")
    body_chars = len(compact(final))
    prompt_chars = len(compact(case["prompt"]))
    material_chars = len(compact(case["material"]))
    return {
        "provider_id": provider_id,
        "model": model,
        "case_id": case["id"],
        "arm": arm,
        "return_code": return_code,
        "seconds": round(time.monotonic() - started, 3),
        "exact_skill_trace": exact_seen,
        "user_skill_paths_in_trace": global_seen,
        "technical_failures": technical,
        "hard_failures": [] if technical else hard_failures(case, final),
        "prompt_chars_nonspace": prompt_chars,
        "material_chars_nonspace": material_chars,
        "final_chars_nonspace": body_chars,
        "shorter_than_prompt": body_chars < prompt_chars,
        "shorter_than_material": body_chars < material_chars,
        "quality_markers_present": [marker for marker in case["quality_markers"] if marker in final],
        "usage": trace_usage(stdout),
        "final_sha256": sha256_bytes(final.encode("utf-8")) if final else None,
        "final_file": str(final_path.relative_to(OUTPUT_ROOT)),
        "trace_file": str(trace_path.relative_to(OUTPUT_ROOT)),
        "stderr_file": str(stderr_path.relative_to(OUTPUT_ROOT)),
    }


def run_provider(provider_id: str) -> dict:
    cases = load_cases()
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    if provider_id not in cases["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    provider_index = list(cases["providers"]).index(provider_id)
    arm_order = ["baseline", "candidate"] if provider_index % 2 == 0 else ["candidate", "baseline"]
    records = []
    for case in cases["cases"]:
        for arm in arm_order:
            records.append(
                run_one(
                    provider_id,
                    cases["providers"][provider_id],
                    arm,
                    case,
                    cases["reasoning_effort"],
                )
            )
            result_path.write_text(
                json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
                encoding="utf-8",
                newline="\n",
            )
    return {"provider_id": provider_id, "records": records}


def summarize() -> dict:
    cases = load_cases()
    records = []
    missing = []
    for provider_id in cases["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if not path.is_file():
            missing.append(provider_id)
            continue
        records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
    summary = {
        "schema_version": 1,
        "codex_version": subprocess.run(
            [shutil.which("codex") or "codex", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        ).stdout.strip(),
        "missing_providers": missing,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "hard_failure_count": sum(bool(item["hard_failures"]) for item in records),
        "shorter_than_prompt_count": sum(item["shorter_than_prompt"] for item in records),
        "shorter_than_material_count": sum(item["shorter_than_material"] for item in records),
        "records": records,
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=list(load_cases()["providers"]))
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
