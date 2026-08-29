from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import zipfile


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CONFIG_PATH = HERE / "underlength-cases.json"
OUTPUT_ROOT = REPO / "output/short-inference-r1/underlength-r10"
CATALOG = Path.home() / ".codex/opencodex-catalog.json"
USER_SKILLS = (
    Path.home() / ".agents/skills/chinese-official-writing/SKILL.md",
    Path.home() / ".codex/skills/chinese-official-writing/SKILL.md",
)


def config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def compact(text: str) -> str:
    return "".join(text.split())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", check=True,
    ).stdout.strip()


def load_runtime(arm: str):
    path = OUTPUT_ROOT / "arms" / arm / "chinese-official-writing/hooks/capabilities/under_length/runtime.py"
    spec = importlib.util.spec_from_file_location(f"underlength_r10_{arm}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runtime: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def export_hooks(commit: str, destination: Path) -> None:
    staging = OUTPUT_ROOT / "staging" / destination.name
    archive = staging / "hooks.zip"
    extracted = staging / "extracted"
    staging.mkdir(parents=True)
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={archive}", commit,
         "chinese-official-writing/hooks"],
        cwd=REPO, check=True,
    )
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(extracted)
    shutil.copytree(extracted / "chinese-official-writing", destination / "chinese-official-writing")


def prepare(candidate_commit: str) -> dict:
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    data = config()
    arms = {
        "baseline": git_text("rev-parse", f"{data['baseline_commit']}^{{commit}}"),
        "candidate": git_text("rev-parse", f"{candidate_commit}^{{commit}}"),
    }
    for arm, commit in arms.items():
        export_hooks(commit, OUTPUT_ROOT / "arms" / arm)
    shutil.rmtree(OUTPUT_ROOT / "staging")
    prompts = {}
    for arm in arms:
        runtime = load_runtime(arm)
        prompts[arm] = {}
        for case in data["cases"]:
            prompts[arm][case["id"]] = runtime._revision_instruction(
                case["request"], case["d0"], case["spec"]
            )
    prompt_path = OUTPUT_ROOT / "prompts.json"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(
        json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    for provider_id in data["providers"]:
        root = OUTPUT_ROOT / "runtime" / provider_id
        root.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
    fixture = {"schema_version": 1, "arms": arms, "providers": list(data["providers"])}
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return fixture


def disabled_skills_config() -> str:
    entries = ",".join(f'{{path="{path.as_posix()}",enabled=false}}' for path in USER_SKILLS)
    return f"skills.config=[{entries}]"


def trace_usage(trace: str) -> dict:
    for line in reversed(trace.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") == "turn.completed" and isinstance(payload.get("usage"), dict):
            return payload["usage"]
    return {}


def body_count(text: str) -> int:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and len(lines[0]) <= 30 and not re.search(r"[。！？!?]", lines[0]):
        lines = lines[1:]
    return len(compact("\n".join(lines)))


def observations(case: dict, final: str) -> list[str]:
    body = compact(final)
    items = []
    for group in case["required_groups"]:
        if not any(compact(value) in body for value in group):
            items.append("missing_any:" + "|".join(group))
    for value in case["forbidden"]:
        if compact(value) in body:
            items.append("forbidden:" + value)
    if "```" in final or "字数" in body or "修改说明" in body or "核验" in body:
        items.append("non_body_output")
    return items


def run_one(provider_id: str, model: str, arm: str, case: dict, effort: str, prompt: str) -> dict:
    raw = OUTPUT_ROOT / "raw" / provider_id
    raw.mkdir(parents=True, exist_ok=True)
    stem = f"{case['id']}-{arm}"
    final_path = raw / f"{stem}.final.txt"
    trace_path = raw / f"{stem}.trace.jsonl"
    stderr_path = raw / f"{stem}.stderr.txt"
    command = [
        shutil.which("codex") or "codex", "exec", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "-C", str(OUTPUT_ROOT / "runtime" / provider_id),
        "-m", model, "-c", 'openai_base_url="http://127.0.0.1:10100/v1"',
        "-c", f'model_catalog_json="{CATALOG.as_posix()}"',
        "-c", f'model_reasoning_effort="{effort}"', "-c", disabled_skills_config(),
        "-s", "read-only", "--ephemeral", "--json", "--output-last-message", str(final_path), "-",
    ]
    print(f"START {provider_id} {case['id']} {arm}", flush=True)
    started = time.monotonic()
    error = None
    try:
        completed = subprocess.run(
            command, input=prompt, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=900, check=False,
        )
        return_code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        return_code = None
        stdout, stderr = str(exc.stdout or ""), str(exc.stderr or "")
        error = "timeout_after_900_seconds"
    trace_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
    technical = []
    if return_code != 0:
        technical.append("nonzero_exit")
    if error:
        technical.append(error)
    if not final.strip():
        technical.append("missing_final")
    count = body_count(final)
    return {
        "provider_id": provider_id, "model": model, "case_id": case["id"], "arm": arm,
        "return_code": return_code, "seconds": round(time.monotonic() - started, 3),
        "technical_failures": technical,
        "observations": [] if technical else observations(case, final),
        "body_chars_nonspace": count,
        "within_requested_range": case["spec"]["minimum"] <= count <= case["spec"]["maximum"],
        "d0_echo": final.strip() == case["d0"].strip(),
        "relation_markers_present": [item for item in case["relation_markers"] if item in final],
        "usage": trace_usage(stdout),
        "final_sha256": sha256_text(final) if final else None,
        "final_file": str(final_path.relative_to(OUTPUT_ROOT)),
        "trace_file": str(trace_path.relative_to(OUTPUT_ROOT)),
        "stderr_file": str(stderr_path.relative_to(OUTPUT_ROOT)),
    }


def run_provider(provider_id: str, *, candidate_only: bool = False) -> dict:
    data = config()
    if provider_id not in data["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"result exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    prompts = json.loads((OUTPUT_ROOT / "prompts.json").read_text(encoding="utf-8"))
    provider_index = list(data["providers"]).index(provider_id)
    arm_order = (
        ["candidate"]
        if candidate_only
        else (["baseline", "candidate"] if provider_index % 2 == 0 else ["candidate", "baseline"])
    )
    records = []
    for case in data["cases"]:
        for arm in arm_order:
            records.append(run_one(
                provider_id, data["providers"][provider_id], arm, case,
                data["reasoning_effort"], prompts[arm][case["id"]],
            ))
            result_path.write_text(
                json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
                encoding="utf-8", newline="\n",
            )
    return {"provider_id": provider_id, "record_count": len(records)}


def summarize() -> dict:
    data = config()
    records, missing = [], []
    for provider_id in data["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if path.is_file():
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(provider_id)
    result = {
        "schema_version": 1, "missing_providers": missing, "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "records": records,
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return result


def main() -> int:
    global OUTPUT_ROOT
    data = config()
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(data["providers"]))
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--candidate-commit")
    parser.add_argument("--candidate-only", action="store_true")
    parser.add_argument("--output-root", default="output/short-inference-r1/underlength-r10")
    args = parser.parse_args()
    relative_output = Path(args.output_root)
    if relative_output.is_absolute() or ".." in relative_output.parts:
        parser.error("--output-root must be a repository-relative path without '..'")
    OUTPUT_ROOT = REPO / relative_output
    if args.prepare:
        if not args.candidate_commit:
            parser.error("--candidate-commit is required with --prepare")
        result = prepare(args.candidate_commit)
    elif args.provider:
        result = run_provider(args.provider, candidate_only=args.candidate_only)
    else:
        result = summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
