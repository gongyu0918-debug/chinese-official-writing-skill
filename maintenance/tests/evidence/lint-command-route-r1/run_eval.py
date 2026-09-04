"""One notice, two independent arms and two providers; ordinary installed Skill cwd."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import time
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = REPO / "output/lint-command-route-r1/r1"
CASES = HERE / "cases.json"
DESKTOP_PATH = HERE.parent / "complaint-reflection-r1/desktop_writer.py"
spec = importlib.util.spec_from_file_location("lint_desktop", DESKTOP_PATH)
DESKTOP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(DESKTOP)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True, encoding="utf-8").strip()


def writer_for(output: Path):
    return DESKTOP.load_writer(REPO, CASES, output)


def prepare(output: Path) -> dict:
    if output.exists() or git("status", "--porcelain"):
        raise RuntimeError("use a new output root and commit the candidate/preregistration first")
    case = json.loads(CASES.read_text(encoding="utf-8"))
    writer = writer_for(output)
    models = json.loads(writer.CATALOG.read_text(encoding="utf-8"))["models"]
    chosen = {name: next((m for m in models if m.get("slug") == slug), None)
              for name, slug in case["providers"].items()}
    for name, model in chosen.items():
        if model is None or "max" not in {r["effort"] for r in model.get("supported_reasoning_levels", [])}:
            raise RuntimeError(f"exact catalog slug or max effort unavailable: {name}")
    cli, version = DESKTOP.desktop_codex()
    runtime = output / "runtime"
    fixture = {"case": case, "harness_commit": git("rev-parse", "HEAD"), "cli": str(cli),
               "cli_version": version, "runtime": str(runtime), "arms": {},
               "prompt_sha256": writer.sha256_bytes(case["prompt"].encode("utf-8")),
               "sources_sha256": {str(p.relative_to(REPO)): writer.sha256_bytes(p.read_bytes())
                                   for p in (CASES, Path(__file__), DESKTOP_PATH, Path(writer.__file__))}}
    for arm, ref in (("baseline", case["baseline_commit"]), ("candidate", case["candidate_product_commit"])):
        commit = git("rev-parse", ref)
        archive = output / "exports" / f"{arm}.zip"
        archive.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "archive", "--format=zip", f"--output={archive}", commit,
                        "chinese-official-writing"], cwd=REPO, check=True)
        exported = output / "exports" / arm
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                relative = Path(member.filename).relative_to("chinese-official-writing")
                if member.is_dir() or not relative.parts or relative.parts[0] == "hooks":
                    continue
                if relative.as_posix() in ("scripts/review_gate.py", "references/delivery-review-gate.md"):
                    continue
                target = exported / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(bundle.read(member))
        count, fingerprint = writer.tree_fingerprint(exported)
        fixture["arms"][arm] = {"commit": commit, "file_count": count, "tree_fingerprint": fingerprint}
        for provider in case["providers"]:
            root = runtime / provider / arm
            skill = root / ".agents/skills/chinese-official-writing"
            skill.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(exported, skill)
            (root / case["material_filename"]).write_text(case["material"], encoding="utf-8", newline="\n")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
    write_json(output / "fixture.json", fixture)
    return fixture


def successful_reads(commands: list[dict], root: Path) -> list[dict]:
    """Conservative observed paths, not a substring match against a global installation."""
    skill = root / ".agents/skills/chinese-official-writing"
    candidates = list(skill.rglob("*"))
    result = []
    read_verbs = re.compile(r"get-content|read_text|readalltext|\bcat\b|\btype\b", re.I)
    for event in commands:
        command = re.sub(r"/+", "/", event["command"].replace("\\", "/"))
        if event.get("exit_code") != 0 or not read_verbs.search(command):
            continue
        for path in candidates:
            if not path.is_file():
                continue
            absolute = path.as_posix()
            relative = path.relative_to(root).as_posix()
            exact = re.search(re.escape(absolute) + r"(?=[\s\"'`;]|$)", command, re.I)
            local = re.search(r"(?<![A-Za-z0-9_:/.-])(?:\./)?" + re.escape(relative)
                              + r"(?=[\s\"'`;]|$)", command, re.I)
            if exact or local:
                result.append({"file": str(path), "relative": path.relative_to(skill).as_posix(),
                               "file_bytes_upper_bound": path.stat().st_size,
                               "command_id": event.get("id"), "path_basis": "absolute" if exact else "project cwd relative",
                               "requires_manual_review_for_cd_or_computed_paths": True})
    return result


def run_one(output: Path, fixture: dict, provider: str, arm: str) -> dict:
    case, writer = fixture["case"], writer_for(output)
    root = Path(fixture["runtime"]) / provider / arm
    skill_file = root / ".agents/skills/chinese-official-writing/SKILL.md"
    raw = output / "raw" / provider / arm
    if raw.exists():
        raise RuntimeError(f"preserve existing run, do not overwrite {raw}")
    raw.mkdir(parents=True)
    final_path, trace_path, stderr_path = (raw / name for name in ("final.txt", "trace.jsonl", "stderr.txt"))
    entries = [f'{{path="{skill_file.as_posix()}",enabled=true}}',
               *(f'{{path="{p.as_posix()}",enabled=false}}' for p in writer.USER_SKILLS)]
    settings = ["features.plugins=false", "features.apps=false", "features.memories=false",
                f"skills.config=[{','.join(entries)}]", 'openai_base_url="http://127.0.0.1:10100/v1"',
                f'model_catalog_json="{writer.CATALOG.as_posix()}"', 'model_reasoning_effort="max"',
                'approval_policy="never"']
    command = [fixture["cli"], "exec", "--skip-git-repo-check", "-C", str(root), "-m", case["providers"][provider]]
    for setting in settings:
        command.extend(["-c", setting])
    command.extend(["-s", "read-only", "--ephemeral", "--json", "--output-last-message", str(final_path), "-"])
    write_json(raw / "invocation.json", {"argv": command, "cwd": str(root), "prompt": case["prompt"],
                                        "prompt_sha256": fixture["prompt_sha256"]})
    if writer.tree_fingerprint(skill_file.parent)[1] != fixture["arms"][arm]["tree_fingerprint"]:
        raise RuntimeError("runtime skill differs before invocation")
    print(f"START {provider} {arm}", flush=True)
    start, failure = time.monotonic(), None
    with trace_path.open("w", encoding="utf-8", newline="\n") as stdout, stderr_path.open("w", encoding="utf-8", newline="\n") as stderr:
        try:
            run = subprocess.run(command, cwd=root, input=case["prompt"], text=True, encoding="utf-8",
                                 errors="replace", stdout=stdout, stderr=stderr, timeout=900, check=False)
            code = run.returncode
        except subprocess.TimeoutExpired:
            code, failure = None, "timeout_after_900_seconds"
    trace = trace_path.read_text(encoding="utf-8", errors="replace")
    errors = stderr_path.read_text(encoding="utf-8", errors="replace")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.exists() else ""
    events = []
    for line in trace.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    commands = [e["item"] for e in events if e.get("type") == "item.completed"
                and e.get("item", {}).get("type") == "command_execution"]
    reads = successful_reads(commands, root)
    normalized = writer.normalized_commands(trace)
    global_paths = [str(p) for p in writer.USER_SKILLS if p.as_posix().casefold() in normalized]
    hook_markers = [m for m in ("<hook_prompt", "chinese-official-writing@chinese-official-writing-local:hooks/",
                               "official-writing-pro@official-writing-pro-local:hooks/") if m in (trace + errors).casefold()]
    technical = [label for condition, label in (
        (code != 0, "nonzero_exit"), (bool(failure), failure), (not final.strip(), "missing_final"),
        (not any(e.get("type") == "turn.completed" for e in events), "missing_turn_completed"),
        (not any(r["relative"] == "SKILL.md" for r in reads), "exact_successful_skill_read_needs_manual_resolution"),
        (bool(global_paths), "global_skill_path_in_commands"), (bool(hook_markers), "hook_contamination"),
        (writer.tree_fingerprint(skill_file.parent)[1] != fixture["arms"][arm]["tree_fingerprint"], "runtime_skill_changed")
    ) if condition]
    record = {"provider": provider, "model": case["providers"][provider], "arm": arm, "return_code": code,
              "seconds": round(time.monotonic() - start, 3), "technical_observations": technical,
              "required_literal_observations_only": writer.hard_failures(case, final),
              "final_chars_nonspace": len(writer.compact(final)), "usage": writer.trace_usage(trace),
              "successful_read_observations": reads, "commands": commands, "global_skill_paths": global_paths,
              "hook_markers": hook_markers, "sha256": {p.name: writer.sha256_bytes(p.read_bytes())
                for p in raw.iterdir() if p.is_file()}, "manual_quality_review": "PENDING"}
    write_json(raw / "record.json", record)
    print(f"END {provider} {arm} exit={code} observations={technical}", flush=True)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--provider", choices=("alibaba2", "minimax"))
    parser.add_argument("--output-root", type=Path, default=OUTPUT)
    args = parser.parse_args()
    output = args.output_root.resolve()
    if args.prepare:
        result = prepare(output)
    else:
        fixture = json.loads((output / "fixture.json").read_text(encoding="utf-8"))
        order = ("baseline", "candidate") if args.provider == "alibaba2" else ("candidate", "baseline")
        result = []
        for arm in order:
            record = run_one(output, fixture, args.provider, arm)
            result.append(record)
            if record["technical_observations"]:
                break
        write_json(output / "providers" / f"{args.provider}.json", result)
    print(json.dumps({"action": "prepare" if args.prepare else args.provider,
                      "output": str(output), "completed": len(result) if isinstance(result, list) else 0}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
