"""Seven real Codex CLI turns per session; follow-ups use explicit exec resume IDs."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
OUTPUT = REPO / "output/revision-stability-audit-r1/r1"
BASE_PATH = HERE.parent / "reference-route-audit-r1/run_eval.py"
ARMS = ("baseline", "candidate")


def load_base():
    spec = importlib.util.spec_from_file_location("revision_audit_base", BASE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def prepare(output: Path) -> dict:
    if output.exists():
        raise RuntimeError(f"refusing to overwrite {output}")
    if BASE.git_text("status", "--porcelain").strip():
        raise RuntimeError("commit the harness before --prepare; worktree must be clean")
    config = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if len(config["providers"]) != 2 or [r["round"] for r in config["rounds"]] != list(range(1, 8)):
        raise RuntimeError("this audit is fixed to two providers and seven ordered rounds")
    writer = BASE.load_writer(output)
    desktop = BASE.load_module("revision_desktop", BASE.WRITER_PATH)
    cli, version = desktop.desktop_codex()
    fixture = {"schema_version": 1, "config": config, "arms": {}, "cli": str(cli), "cli_version": version,
               "harness_commit": BASE.git_text("rev-parse", "HEAD").strip(), "expected_records": 28,
               "context_method": "initial persistent exec; subsequent exec resume with exact thread_id; only current round prompt sent",
               "hook_mode": "plugins disabled; no Hook install or activation",
               "sources_sha256": {str(p.relative_to(REPO)): BASE.file_hash(p) for p in
                                   (CASES_PATH, Path(__file__), BASE_PATH, BASE.WRITER_PATH, Path(writer.__file__))}}
    for arm in ARMS:
        commit = BASE.git_text("rev-parse", f"{config[arm + '_commit']}^{{commit}}").strip()
        if commit != config[arm + "_commit"]:
            raise RuntimeError(f"{arm} commit mismatch")
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
            BASE.shutil.copytree(exported, skill)
            subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    BASE.write_json(output / "fixture.json", fixture)
    return fixture


def command_for(cli: str, writer, root: Path, model: str, effort: str, final: Path, session: str | None) -> list[str]:
    skill = root / ".agents/skills/chinese-official-writing"
    entries = [f'{{path="{skill.as_posix()}",enabled=true}}']
    entries.extend(f'{{path="{p.parent.as_posix()}",enabled=false}}' for p in writer.USER_SKILLS)
    config = ["features.plugins=false", "features.apps=false", "features.memories=false",
              f"skills.config=[{','.join(entries)}]", 'openai_base_url="http://127.0.0.1:10100/v1"',
              f'model_catalog_json="{writer.CATALOG.as_posix()}"', f'model_reasoning_effort="{effort}"',
              'approval_policy="never"', 'sandbox_mode="read-only"']
    command = [cli, "exec", *( ["resume", session] if session else ["-C", str(root)] ), "-m", model]
    for setting in config:
        command.extend(["-c", setting])
    return [*command, "--skip-git-repo-check", "--json", "--output-last-message", str(final), "-"]


def text_output(value) -> str:
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""


def run_round(output: Path, fixture: dict, provider: str, arm: str, case: dict, session: str | None, writer) -> dict:
    root = writer.runtime_root(provider, arm)
    raw = output / "raw" / provider / arm
    raw.mkdir(parents=True, exist_ok=True)
    stem = f"round-{case['round']:02d}"
    if list(raw.glob(stem + ".*")):
        raise RuntimeError(f"orphan/existing evidence at {raw / stem}; do not overwrite or automatically rerun")
    final_path, trace_path, stderr_path = (raw / f"{stem}.{suffix}" for suffix in ("final.txt", "trace.jsonl", "stderr.txt"))
    command = command_for(fixture["cli"], writer, root, fixture["config"]["providers"][provider],
                          fixture["config"]["reasoning_effort"], final_path, session)
    BASE.write_json(raw / f"{stem}.invocation.json", {"argv_without_prompt": command,
                    "prompt": case["prompt"], "source_session_id": session, "cwd": str(root)})
    print(f"START {provider} {arm} round={case['round']} resume={session or 'NEW'}", flush=True)
    started, timeout = time.monotonic(), False
    try:
        result = subprocess.run(command, cwd=root, input=case["prompt"], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=900, check=False)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr, timeout = None, text_output(exc.stdout), text_output(exc.stderr), True
    except OSError as exc:
        code, stdout, stderr = None, "", f"{type(exc).__name__}: {exc}"
    trace_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.exists() else ""
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    ids = {e.get("thread_id") for e in events if e.get("type") == "thread.started" and e.get("thread_id")}
    observed_id = next(iter(ids)) if len(ids) == 1 else None
    commands = writer.normalized_commands(stdout)
    reads = [str(p) for p in writer.USER_SKILLS if p.as_posix().casefold() in commands]
    hook_markers = [m for m in ("<hook_prompt", "chinese-official-writing@chinese-official-writing-local:hooks/",
                               "official-writing-pro@official-writing-pro-local:hooks/") if m in (stdout + stderr).casefold()]
    technical = []
    for failed, reason in ((code != 0, "nonzero_exit"), (timeout, "timeout_after_900_seconds"),
                           (not final.strip(), "missing_final"), (observed_id is None, "missing_or_ambiguous_thread_id"),
                           (bool(session) and observed_id != session, "resume_thread_id_mismatch"),
                           (not any(e.get("type") == "turn.completed" for e in events), "missing_turn_completed"),
                           (bool(reads), "user_skill_contamination"), (bool(hook_markers), "hook_contamination")):
        if failed:
            technical.append(reason)
    probe = BASE.load_module("revision_reads_probe", BASE.PROBE_PATH)
    original_commands = probe.trace_commands
    probe.trace_commands = lambda trace: [re.sub(r"/+", "/", c.replace("\\", "/")) for c in original_commands(trace)]
    files, size, read_events = BASE.observed_reads(stdout, root, probe)
    if session is None and "SKILL.md" not in files:
        technical.append("missing_initial_successful_skill_read")
    observation = writer.hard_failures(case, final) if final else ["empty_final"]
    count = len(writer.compact(final))
    if case.get("min_chars") and count < case["min_chars"]:
        observation.append(f"under_min_chars:{count}<{case['min_chars']}")
    if case.get("max_chars") and count > case["max_chars"]:
        observation.append(f"over_max_chars:{count}>{case['max_chars']}")
    return {"provider_id": provider, "arm": arm, "round": case["round"], "source_session_id": session,
            "thread_id": observed_id, "resumed": session is not None, "return_code": code,
            "seconds": round(time.monotonic() - started, 3), "technical_failures": technical,
            "hard_failures_observation_only": observation, "final_chars_nonspace": count,
            "usage": writer.trace_usage(stdout), "skill_files_read": files, "loaded_bytes": size, "read_events": read_events,
            "user_skill_paths_in_trace": reads, "hook_contamination_markers": hook_markers,
            "final_sha256": writer.sha256_bytes(final.encode("utf-8")) if final else None,
            "trace_sha256": BASE.file_hash(trace_path), "final_file": str(final_path.relative_to(output)),
            "trace_file": str(trace_path.relative_to(output)), "stderr_file": str(stderr_path.relative_to(output))}


def run_session(output: Path, provider: str, arm: str) -> dict:
    fixture = BASE.load_fixture(output)
    config = fixture["config"]
    if provider not in config["providers"] or arm not in ARMS:
        raise RuntimeError("unknown provider or arm")
    path = output / "sessions" / f"{provider}-{arm}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(".lock")
    with lock.open("x", encoding="utf-8"):
        pass
    try:
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "provider_id": provider, "arm": arm, "thread_id": None, "records": []}
        if payload["provider_id"] != provider or payload["arm"] != arm:
            raise RuntimeError("session identity mismatch")
        writer = BASE.load_writer(output)
        for case in config["rounds"]:
            if len(payload["records"]) >= case["round"]:
                continue
            if payload["records"] and payload["records"][-1]["technical_failures"]:
                break
            runtime_skill = writer.runtime_root(provider, arm) / ".agents/skills/chinese-official-writing"
            if writer.tree_fingerprint(runtime_skill)[1] != fixture["arms"][arm]["tree_fingerprint"]:
                raise RuntimeError("runtime snapshot changed")
            record = run_round(output, fixture, provider, arm, case, payload["thread_id"], writer)
            if payload["thread_id"] is None:
                payload["thread_id"] = record["thread_id"]
            payload["records"].append(record)
            BASE.write_json(path, payload)
        return {"provider_id": provider, "arm": arm, "thread_id": payload["thread_id"],
                "record_count": len(payload["records"]), "halted_technical": bool(payload["records"][-1]["technical_failures"])}
    finally:
        lock.unlink()


def exact_round7_reorder(output: Path, records: list[dict], writer) -> dict:
    selected = {r["round"]: r for r in records if r["round"] in (6, 7)}
    if set(selected) != {6, 7}:
        return {"status": "NOT_RUN"}
    paths = {n: output / r["final_file"] for n, r in selected.items()}
    if not all(p.is_file() for p in paths.values()):
        return {"status": "NOT_EVALUABLE_MISSING_FINAL"}
    before, after = (paths[n].read_text(encoding="utf-8").strip() for n in (6, 7))
    headings = ("（一）场景核验", "（二）目录归集", "二、存在问题")
    if any(before.count(h) != 1 for h in headings):
        return {"status": "NOT_EVALUABLE_R6_STRUCTURE"}
    first, second, end = (before.index(h) for h in headings)
    if not first < second < end:
        return {"status": "NOT_EVALUABLE_R6_STRUCTURE"}
    scenario = before[first:second].replace(headings[0], "（二）场景核验", 1)
    catalog = before[second:end].replace(headings[1], "（一）目录归集", 1)
    expected = before[:first] + catalog + scenario + before[end:]
    return {"status": "PASS" if after == expected else "FAIL", "base_round": 6,
            "scope": "only two subsection blocks and their numbering; LF normalized and outer whitespace ignored",
            "expected_sha256": writer.sha256_bytes(expected.encode("utf-8")),
            "observed_sha256": writer.sha256_bytes(after.encode("utf-8"))}


def summarize(output: Path) -> dict:
    fixture = BASE.load_fixture(output)
    sessions = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((output / "sessions").glob("*.json"))]
    records = [r for session in sessions for r in session["records"]]
    writer = BASE.load_writer(output)
    ids = [s["thread_id"] for s in sessions if s.get("thread_id")]
    for session in sessions:
        session["round7_exact_reorder"] = exact_round7_reorder(output, session["records"], writer)
    summary = {"schema_version": 1, "arms": fixture["arms"], "expected_sessions": 4, "expected_records": 28,
               "session_count": len(sessions), "record_count": len(records),
               "unique_session_ids": len(set(ids)) == len(ids),
               "technical_failure_count": sum(bool(r["technical_failures"]) for r in records),
               "judgment": "manual review required; literal observations do not establish writing reliability",
               "context_method": fixture["context_method"], "sessions": sessions}
    BASE.write_json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider")
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--arm", choices=ARMS)
    parser.add_argument("--output-root", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.provider and not args.arm:
        parser.error("--provider requires --arm so each invocation owns one explicit session")
    output = args.output_root.resolve()
    result = prepare(output) if args.prepare else run_session(output, args.provider, args.arm) if args.provider else summarize(output)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
