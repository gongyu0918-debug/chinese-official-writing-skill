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
OUTPUT_ROOT = REPO / "output" / "wr001-date-r2"
CATALOG = Path.home() / ".codex" / "opencodex-catalog.json"
TARGET = "chinese-official-writing/references/genre-playbook-news-message.md"
BASE_LINE = "- 正文按事件进程或信息层次，展开材料已给的时间、地点、主体、动作、数字、结果和背景。"
CANDIDATE_LINE = "- 正文按事件进程或信息层次，展开材料已给的时间、地点、主体、动作、数字、结果和背景；完整年月日照录，不缩为月日；材料仅有月日时不补年份。"
USER_SKILLS = (
    Path.home() / ".agents/skills/chinese-official-writing/SKILL.md",
    Path.home() / ".codex/skills/chinese-official-writing/SKILL.md",
)


def load_cases() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def compact(text: str) -> str:
    return "".join(text.split())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint(root: Path) -> tuple[int, str]:
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rows.append(f"{path.relative_to(root).as_posix()}:{sha256(path.read_bytes())}\n")
    return len(rows), sha256("".join(rows).encode("utf-8"))


def export_skill(ref: str, destination: Path, archive: Path) -> str:
    commit = subprocess.run(
        ["git", "rev-parse", f"{ref}^{{commit}}"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={archive}", commit, "chinese-official-writing"],
        cwd=REPO,
        check=True,
    )
    extracted = archive.with_suffix("")
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(extracted)
    shutil.copytree(extracted / "chinese-official-writing", destination)
    return commit


def verify_single_atom(baseline: Path, candidate: Path) -> None:
    baseline_files = sorted(path.relative_to(baseline).as_posix() for path in baseline.rglob("*") if path.is_file())
    candidate_files = sorted(path.relative_to(candidate).as_posix() for path in candidate.rglob("*") if path.is_file())
    if baseline_files != candidate_files:
        raise RuntimeError("Skill file sets differ")
    for relative in baseline_files:
        left = (baseline / relative).read_bytes()
        right = (candidate / relative).read_bytes()
        if relative == "references/genre-playbook-news-message.md":
            candidate_text = (candidate / relative).read_text(encoding="utf-8")
            if candidate_text.count(CANDIDATE_LINE) != 1:
                raise RuntimeError("candidate date line is missing or duplicated")
            normalized = candidate_text.replace(CANDIDATE_LINE, BASE_LINE)
            if normalized != (baseline / relative).read_text(encoding="utf-8"):
                raise RuntimeError("target reference differs outside the frozen sentence")
            continue
        if left != right:
            raise RuntimeError(f"unexpected Skill difference: {relative}")


def root_for(provider_id: str, arm: str) -> Path:
    return OUTPUT_ROOT / "runtime" / provider_id / arm


def prepare() -> dict:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    config = load_cases()
    exports = {}
    commits = {}
    staging = OUTPUT_ROOT / "staging"
    staging.mkdir(parents=True)
    for arm, ref in config["arms"].items():
        destination = OUTPUT_ROOT / "exports" / arm
        destination.parent.mkdir(parents=True, exist_ok=True)
        commits[arm] = export_skill(ref, destination, staging / f"{arm}.zip")
        exports[arm] = destination
    verify_single_atom(exports["baseline"], exports["candidate"])
    for provider_id in config["providers"]:
        for arm, source in exports.items():
            root = root_for(provider_id, arm)
            skill = root / ".agents" / "skills" / "chinese-official-writing"
            skill.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, skill)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
    shutil.rmtree(staging)
    fixture = {"schema_version": 1, "commits": commits, "arms": {}}
    for arm, source in exports.items():
        count, digest = fingerprint(source)
        fixture["arms"][arm] = {"file_count": count, "tree_fingerprint": digest}
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return fixture


def disabled_skills() -> str:
    items = ",".join(f'{{path="{path.as_posix()}",enabled=false}}' for path in USER_SKILLS)
    return f"skills.config=[{items}]"


def trace_commands(trace: str) -> str:
    commands = []
    for line in trace.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = payload.get("item")
        if isinstance(item, dict) and item.get("type") == "command_execution" and isinstance(item.get("command"), str):
            commands.append(item["command"])
    return re.sub(r"/+", "/", "\n".join(commands).replace("\\", "/")).casefold()


def usage(trace: str) -> dict:
    for line in reversed(trace.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") == "turn.completed" and isinstance(payload.get("usage"), dict):
            return payload["usage"]
    return {}


def body_checks(final: str) -> list[str]:
    body = compact(final)
    checks = []
    required = (
        ("2026年8月20日",),
        ("48名", "48人"),
        ("45名", "45人"),
        ("3名", "3人"),
        ("46份",),
        ("先列问题再读文章",),
        ("尚未完成", "尚未汇总", "正在汇总", "正在对意见卡进行汇总", "反馈正在汇总", "意见卡正在汇总"),
    )
    for group in required:
        if not any(compact(item) in body for item in group):
            checks.append("missing_any:" + "|".join(group))
    for forbidden in ("按年龄分组", "指定篇目", "书面作答", "优化活动安排", "形成长效机制"):
        if forbidden in body:
            checks.append("forbidden:" + forbidden)
    if "```" in final or "**" in final or final.lstrip().startswith("#"):
        checks.append("markdown_wrapper")
    return checks


def run_one(provider_id: str, model: str, arm: str, prompt: str, effort: str) -> dict:
    root = root_for(provider_id, arm)
    raw = OUTPUT_ROOT / "raw" / provider_id
    raw.mkdir(parents=True, exist_ok=True)
    final_path = raw / f"{arm}.final.txt"
    trace_path = raw / f"{arm}.trace.jsonl"
    stderr_path = raw / f"{arm}.stderr.txt"
    command = [
        shutil.which("codex") or "codex", "exec", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "-C", str(root), "-m", model,
        "-c", 'openai_base_url="http://127.0.0.1:10100/v1"',
        "-c", f'model_catalog_json="{CATALOG.as_posix()}"',
        "-c", f'model_reasoning_effort="{effort}"', "-c", disabled_skills(),
        "-s", "read-only", "--ephemeral", "--json", "--output-last-message", str(final_path), "-",
    ]
    print(f"START {provider_id} {arm}", flush=True)
    started = time.monotonic()
    completed = subprocess.run(
        command, input=prompt, text=True, encoding="utf-8", errors="replace",
        capture_output=True, timeout=900, check=False,
    )
    trace_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(completed.stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
    commands = trace_commands(completed.stdout)
    exact = (root / ".agents/skills/chinese-official-writing/SKILL.md").as_posix().casefold()
    exact_seen = exact in commands or ".agents/skills/chinese-official-writing/skill.md" in commands
    global_seen = [path.as_posix() for path in USER_SKILLS if path.as_posix().casefold() in commands]
    technical = []
    if completed.returncode != 0:
        technical.append("nonzero_exit")
    if not final.strip():
        technical.append("missing_final")
    if not exact_seen:
        technical.append("missing_exact_skill_trace")
    if global_seen:
        technical.append("user_skill_contamination")
    return {
        "provider_id": provider_id, "model": model, "arm": arm,
        "return_code": completed.returncode, "seconds": round(time.monotonic() - started, 3),
        "exact_skill_trace": exact_seen, "user_skill_paths_in_trace": global_seen,
        "technical_failures": technical, "body_checks": [] if technical else body_checks(final),
        "final_chars_nonspace": len(compact(final)), "usage": usage(completed.stdout),
        "final_sha256": sha256(final.encode("utf-8")) if final else None,
        "final_file": str(final_path.relative_to(OUTPUT_ROOT)),
        "trace_file": str(trace_path.relative_to(OUTPUT_ROOT)),
        "stderr_file": str(stderr_path.relative_to(OUTPUT_ROOT)),
    }


def run_provider(provider_id: str) -> dict:
    config = load_cases()
    if provider_id not in config["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    order = ["baseline", "candidate"] if list(config["providers"]).index(provider_id) % 2 == 0 else ["candidate", "baseline"]
    records = []
    for arm in order:
        records.append(run_one(provider_id, config["providers"][provider_id], arm, config["case"]["prompt"], config["reasoning_effort"]))
        result_path.write_text(json.dumps({"records": records}, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return {"provider_id": provider_id, "records": records}


def summarize() -> dict:
    config = load_cases()
    records = []
    missing = []
    for provider_id in config["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if not path.is_file():
            missing.append(provider_id)
        else:
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
    summary = {"schema_version": 1, "missing_providers": missing, "record_count": len(records), "records": records}
    (OUTPUT_ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--provider", choices=list(load_cases()["providers"]))
    actions.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    result = prepare() if args.prepare else run_provider(args.provider) if args.provider else summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
