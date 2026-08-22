from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
SOURCE_SKILL = REPO / "chinese-official-writing"
OUTPUT_ROOT = REPO / "output" / "mt005c-codex-cli-20260822"
USER_SKILLS = (
    Path("C:/Users/admin/.agents/skills/chinese-official-writing/SKILL.md"),
    Path("C:/Users/admin/.codex/skills/chinese-official-writing/SKILL.md"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cases() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def replace_description(skill_path: Path, old: str, new: str) -> None:
    text = skill_path.read_text(encoding="utf-8")
    old_line = f"description: {old}"
    new_line = f"description: {new}"
    if text.count(old_line) != 1:
        raise RuntimeError("baseline description was not found exactly once")
    skill_path.write_text(text.replace(old_line, new_line), encoding="utf-8", newline="\n")


def prepare_runtime(cases: dict) -> dict[str, Path]:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    roots: dict[str, Path] = {}
    for arm in ("baseline", "candidate"):
        root = OUTPUT_ROOT / "runtime" / arm
        skill_root = root / ".agents" / "skills" / "chinese-official-writing"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE_SKILL, skill_root)
        if arm == "candidate":
            replace_description(
                skill_root / "SKILL.md",
                cases["arms"]["baseline"],
                cases["arms"]["candidate"],
            )
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        roots[arm] = root

    base_skill = roots["baseline"] / ".agents/skills/chinese-official-writing/SKILL.md"
    cand_skill = roots["candidate"] / ".agents/skills/chinese-official-writing/SKILL.md"
    base_text = base_skill.read_text(encoding="utf-8")
    cand_text = cand_skill.read_text(encoding="utf-8")
    normalized_candidate = cand_text.replace(cases["arms"]["candidate"], cases["arms"]["baseline"])
    if normalized_candidate != base_text:
        raise RuntimeError("the two SKILL.md files differ outside description")

    base_files = sorted(str(path.relative_to(base_skill.parent)) for path in base_skill.parent.rglob("*") if path.is_file())
    cand_files = sorted(str(path.relative_to(cand_skill.parent)) for path in cand_skill.parent.rglob("*") if path.is_file())
    if base_files != cand_files:
        raise RuntimeError("the two Skill trees contain different file sets")
    for relative in base_files:
        if relative == "SKILL.md":
            continue
        if sha256(base_skill.parent / relative) != sha256(cand_skill.parent / relative):
            raise RuntimeError(f"unexpected non-description difference: {relative}")

    fixture = {
        "baseline_skill_sha256": sha256(base_skill),
        "candidate_skill_sha256": sha256(cand_skill),
        "shared_file_count": len(base_files),
        "only_description_diff": True,
    }
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return roots


def normalize_trace(text: str) -> str:
    commands: list[str] = []
    for line in text.splitlines():
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


def trace_usage(text: str) -> dict:
    for line in reversed(text.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("type") == "turn.completed" and isinstance(payload.get("usage"), dict):
            return payload["usage"]
    return {}


def hard_failures(case: dict, final: str) -> list[str]:
    compact = "".join(final.split())
    failures: list[str] = []
    if not compact:
        return ["empty_final"]
    for value in case["required"]:
        if "".join(value.split()) not in compact:
            failures.append(f"missing:{value}")
    for value in case["forbidden"]:
        if "".join(value.split()) in compact:
            failures.append(f"forbidden:{value}")
    if "```" in final or "读取过程" in final or "Skill" in final:
        failures.append("non_body_output")
    return failures


def disabled_skills_config() -> str:
    items = ",".join(
        f'{{path="{path.as_posix()}",enabled=false}}' for path in USER_SKILLS
    )
    return f"skills.config=[{items}]"


def run_one(cases: dict, case: dict, arm: str, root: Path) -> dict:
    raw = OUTPUT_ROOT / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    stem = f"{case['id']}-{arm}"
    final_path = raw / f"{stem}.final.txt"
    trace_path = raw / f"{stem}.trace.jsonl"
    stderr_path = raw / f"{stem}.stderr.txt"
    exact_skill = root / ".agents/skills/chinese-official-writing/SKILL.md"
    command = [
        shutil.which("codex") or "codex",
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-C",
        str(root),
        "-m",
        cases["model"],
        "-c",
        f'model_reasoning_effort="{cases["reasoning_effort"]}"',
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
    print(f"START {case['id']} {arm}", flush=True)
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
        error = "timeout_after_900_seconds"
        stdout = str(exc.stdout or "")
        stderr = str(exc.stderr or "")
    trace_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
    normalized = normalize_trace(stdout)
    exact_seen = exact_skill.as_posix().casefold() in normalized
    global_seen = [path.as_posix() for path in USER_SKILLS if path.as_posix().casefold() in normalized]
    technical: list[str] = []
    if return_code != 0:
        technical.append("nonzero_exit")
    if error:
        technical.append(error)
    if not final.strip():
        technical.append("missing_final")
    if global_seen:
        technical.append("user_skill_contamination")
    expected = bool(case["expected_skill"])
    if expected and not exact_seen:
        technical.append("missing_exact_skill_trace")
    if not expected and exact_seen:
        technical.append("unexpected_skill_trigger")
    record = {
        "case_id": case["id"],
        "arm": arm,
        "model": cases["model"],
        "return_code": return_code,
        "seconds": round(time.monotonic() - started, 3),
        "exact_skill_trace": exact_seen,
        "user_skill_paths_in_trace": global_seen,
        "technical_failures": technical,
        "hard_failures": hard_failures(case, final) if not technical else [],
        "usage": trace_usage(stdout),
        "final_chars_nonspace": len("".join(final.split())),
        "final_sha256": hashlib.sha256(final.encode("utf-8")).hexdigest() if final else None,
        "final_file": str(final_path.relative_to(OUTPUT_ROOT)),
        "trace_file": str(trace_path.relative_to(OUTPUT_ROOT)),
        "stderr_file": str(stderr_path.relative_to(OUTPUT_ROOT)),
    }
    print(
        f"DONE {case['id']} {arm} rc={return_code} skill={exact_seen} "
        f"technical={technical} hard={record['hard_failures']} seconds={record['seconds']}",
        flush=True,
    )
    return record


def reanalyze_one(cases: dict, case: dict, arm: str, root: Path, previous: dict) -> dict:
    raw = OUTPUT_ROOT / "raw"
    stem = f"{case['id']}-{arm}"
    final_path = raw / f"{stem}.final.txt"
    trace_path = raw / f"{stem}.trace.jsonl"
    stderr_path = raw / f"{stem}.stderr.txt"
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
    trace = trace_path.read_text(encoding="utf-8", errors="replace") if trace_path.is_file() else ""
    normalized = normalize_trace(trace)
    exact_skill = root / ".agents/skills/chinese-official-writing/SKILL.md"
    exact_seen = exact_skill.as_posix().casefold() in normalized
    global_seen = [path.as_posix() for path in USER_SKILLS if path.as_posix().casefold() in normalized]
    technical: list[str] = []
    return_code = previous.get("return_code")
    if return_code != 0:
        technical.append("nonzero_exit")
    if not final.strip():
        technical.append("missing_final")
    if global_seen:
        technical.append("user_skill_contamination")
    expected = bool(case["expected_skill"])
    if expected and not exact_seen:
        technical.append("missing_exact_skill_trace")
    if not expected and exact_seen:
        technical.append("unexpected_skill_trigger")
    return {
        "case_id": case["id"],
        "arm": arm,
        "model": cases["model"],
        "return_code": return_code,
        "seconds": previous.get("seconds"),
        "exact_skill_trace": exact_seen,
        "user_skill_paths_in_trace": global_seen,
        "technical_failures": technical,
        "hard_failures": hard_failures(case, final) if not technical else [],
        "usage": trace_usage(trace),
        "final_chars_nonspace": len("".join(final.split())),
        "final_sha256": hashlib.sha256(final.encode("utf-8")).hexdigest() if final else None,
        "final_file": str(final_path.relative_to(OUTPUT_ROOT)),
        "trace_file": str(trace_path.relative_to(OUTPUT_ROOT)),
        "stderr_file": str(stderr_path.relative_to(OUTPUT_ROOT)),
    }


def write_summary(cases: dict, records: list[dict]) -> dict:
    by_id = {item["id"]: item for item in cases["cases"]}
    positive_candidate = [r for r in records if r["arm"] == "candidate" and by_id[r["case_id"]]["expected_skill"]]
    negative_candidate = [r for r in records if r["arm"] == "candidate" and not by_id[r["case_id"]]["expected_skill"]]
    summary = {
        "schema_version": 1,
        "codex_version": subprocess.run(
            [shutil.which("codex") or "codex", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        ).stdout.strip(),
        "records": records,
        "candidate_target_met": bool(
            positive_candidate
            and all(not r["technical_failures"] and not r["hard_failures"] and r["exact_skill_trace"] for r in positive_candidate)
            and all(not r["technical_failures"] and not r["hard_failures"] and not r["exact_skill_trace"] for r in negative_candidate)
        ),
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--reanalyze", action="store_true")
    args = parser.parse_args()
    cases = load_cases()
    if args.reanalyze:
        if not (OUTPUT_ROOT / "summary.json").is_file():
            raise RuntimeError("existing summary is required for --reanalyze")
        roots = {arm: OUTPUT_ROOT / "runtime" / arm for arm in ("baseline", "candidate")}
        previous = json.loads((OUTPUT_ROOT / "summary.json").read_text(encoding="utf-8"))
        prior = {(item["case_id"], item["arm"]): item for item in previous["records"]}
        by_id = {item["id"]: item for item in cases["cases"]}
        records = [
            reanalyze_one(cases, by_id[case_id], arm, roots[arm], prior[(case_id, arm)])
            for case_id, arm in cases["run_order"]
        ]
        summary = write_summary(cases, records)
        print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
        return 0
    roots = prepare_runtime(cases)
    if args.preflight:
        print(json.dumps(json.loads((OUTPUT_ROOT / "fixture.json").read_text(encoding="utf-8")), indent=2))
        return 0

    by_id = {item["id"]: item for item in cases["cases"]}
    records = [run_one(cases, by_id[case_id], arm, roots[arm]) for case_id, arm in cases["run_order"]]
    summary = write_summary(cases, records)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
