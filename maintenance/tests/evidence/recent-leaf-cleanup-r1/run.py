"""Two frozen writing/review cases using the existing tool-free cheap CLI helper."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HELPER_PATH = HERE.parent / "date-source-real-r1/run.py"
SPEC = importlib.util.spec_from_file_location("leaf_cleanup_existing_cli", HELPER_PATH)
assert SPEC and SPEC.loader
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def dependencies() -> dict:
    paths = [Path(__file__), HERE / "cases.json", HELPER_PATH, HELPER.REPLAY_PATH, HELPER.REPLAY.BASE_PATH]
    return {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in paths}


def prepare(output: Path) -> dict:
    if git("status", "--porcelain").strip():
        raise RuntimeError("commit prototype and preregistration before freezing")
    config = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    candidate = git("rev-parse", "HEAD").decode().strip()
    baseline = config["baseline_commit"]
    changed = git("diff", "--name-only", baseline, candidate, "--", "chinese-official-writing").decode().splitlines()
    expected = ["chinese-official-writing/references/genre-playbook-complaint-reflection.md",
                "chinese-official-writing/references/review-direct-checklist.md"]
    if sorted(changed) != sorted(expected):
        raise RuntimeError(f"unexpected product delta: {changed}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("existing Claude CLI required; no installation")
    output.mkdir(parents=True, exist_ok=False)
    contexts = {}
    paths = sorted({p for case in config["cases"] for p in case["context_files"]})
    for arm, commit in {"baseline": baseline, "candidate": candidate}.items():
        contexts[arm] = {}
        for p in paths:
            data = git("show", f"{commit}:chinese-official-writing/{p}")
            contexts[arm][p] = {"text": data.decode("utf-8"), "sha256": digest(data), "bytes": len(data)}
    fixture = {"config": config, "arms": {"baseline": baseline, "candidate": candidate},
               "context_method": "Frozen Skill, common fact rules and task references injected identically except two deleted example spans; content ablation, not autonomous routing or a Hook lifecycle.",
               "contexts": contexts, "sources_sha256": dependencies(), "claude": claude,
               "claude_sha256": digest(Path(claude).read_bytes()),
               "claude_version": subprocess.check_output([claude, "--version"], text=True, encoding="utf-8").strip()}
    save(output / "fixture.json", fixture)
    return {"prepared": True, "calls": 8, "candidate": candidate, "baseline": baseline}


def run_provider(output: Path, provider: str) -> dict:
    fixture = json.loads((output / "fixture.json").read_text(encoding="utf-8"))
    if fixture["sources_sha256"] != dependencies():
        raise RuntimeError("frozen harness source changed")
    if digest(Path(fixture["claude"]).read_bytes()) != fixture["claude_sha256"]:
        raise RuntimeError("frozen CLI changed")
    config = fixture["config"]
    model = config["providers"][provider]
    orders = {"alibaba2": [("complaint", "baseline"), ("complaint", "candidate"), ("review", "candidate"), ("review", "baseline")],
              "minimax": [("complaint", "candidate"), ("complaint", "baseline"), ("review", "baseline"), ("review", "candidate")]}
    cases = {case["id"]: case for case in config["cases"]}
    rows = []
    for case_id, arm in orders[provider]:
        case = cases[case_id]
        contexts = fixture["contexts"][arm]
        prompt = ("以下为本轮固定Skill和命中reference上下文。业务事实以末尾用户任务为准；本会话没有工具，请完成用户任务。\n\n"
                  + "\n\n".join(f"=== {p} ===\n{contexts[p]['text']}" for p in case["context_files"])
                  + "\n\n=== 用户任务 ===\n" + case["prompt"])
        lane = output / "runs" / provider / case_id / arm
        lane.mkdir(parents=True, exist_ok=False)
        save(lane / "invocation.json", {"model": model, "arm": arm, "case_id": case_id,
                                      "argv": HELPER.command(fixture["claude"], model),
                                      "prompt_sha256": digest(prompt.encode()), "context_paths": case["context_files"]})
        print(f"START {provider} {case_id} {arm}", flush=True)
        body, receipt = HELPER.restricted_reply(model, prompt, lane / "call", fixture["claude"])
        events = [json.loads(line) for line in (lane / "call/stream.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        session_ids = [e["session_id"] for e in events if e.get("type") == "system" and e.get("subtype") == "init"]
        if len(session_ids) != 1 or session_ids[0] in {r["session_id"] for r in rows}:
            raise RuntimeError("each writing task requires one distinct real CLI session")
        row = {"provider": provider, "case_id": case_id, "arm": arm, "model": model,
               "session_id": session_ids[0], "body": body, "body_sha256": digest(body.encode()),
               "context_bytes": sum(contexts[p]["bytes"] for p in case["context_files"]),
               "technical_valid": receipt["technical_valid"], "seconds": receipt["seconds"]}
        rows.append(row)
        save(lane / "result.json", row)
        save(output / f"{provider}-summary.json", {"rows": rows})
        print(f"DONE {provider} {case_id} {arm} valid={receipt['technical_valid']} seconds={receipt['seconds']}", flush=True)
    return {"provider": provider, "calls": len(rows), "technical_valid": all(r["technical_valid"] for r in rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=("alibaba2", "minimax"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output.resolve()) if args.prepare else run_provider(args.output.resolve(), args.provider)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
