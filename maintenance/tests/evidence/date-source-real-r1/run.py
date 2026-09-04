"""Frozen natural news D0 and baseline core replay with no model tools."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REPLAY_PATH = HERE.parent / "hook-audit-quality-r1/replay_real_d0.py"
spec = importlib.util.spec_from_file_location("date_real_replay", REPLAY_PATH)
assert spec and spec.loader
REPLAY = importlib.util.module_from_spec(spec)
spec.loader.exec_module(REPLAY)
BASE = REPLAY.BASE


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def command(claude: str, model: str) -> list[str]:
    return [claude, "--setting-sources", "", "--no-session-persistence", "--disable-slash-commands",
            "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--permission-mode", "dontAsk", "--print", "--verbose", "--output-format", "stream-json",
            "--model", model, "--effort", "max"]


def restricted_reply(model: str, prompt: str, out: Path, claude: str) -> tuple[str, dict]:
    out.mkdir(parents=True, exist_ok=False)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8", newline="\n")
    environment = BASE.build_environment(model, out / "runtime")
    started = time.monotonic()
    code, failure = None, None
    with (out / "stream.jsonl").open("w", encoding="utf-8", newline="\n") as stdout, (out / "stderr.txt").open("w", encoding="utf-8", newline="\n") as stderr:
        try:
            result = subprocess.run(command(claude, model), cwd=out / "runtime/work", env=environment,
                                    input=prompt, text=True, encoding="utf-8", stdout=stdout, stderr=stderr,
                                    timeout=REPLAY.CLI_TIMEOUT, check=False)
            code = result.returncode
        except (subprocess.TimeoutExpired, OSError) as exc:
            failure = type(exc).__name__
    parsed = BASE.parse_stream(out / "stream.jsonl")
    final = parsed.pop("final")
    records = []
    for line in (out / "stream.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    inits = [r for r in records if r.get("type") == "system" and r.get("subtype") == "init"]
    inventory = [{k: r.get(k) for k in ("tools", "mcp_servers", "skills", "plugins")} for r in inits]
    tool_uses = [b.get("name") for r in records for b in (r.get("message") or {}).get("content", [])
                 if isinstance(b, dict) and b.get("type") == "tool_use"]
    disabled = bool(inventory) and all(all(r[k] == [] for k in ("tools", "mcp_servers", "skills", "plugins")) for r in inventory) and not tool_uses
    valid = (code == 0 and bool(final.strip()) and parsed["result_count"] == 1
             and parsed["result_subtypes"] == ["success"] and parsed["result_errors"] == [False]
             and not parsed["invalid_json_lines"] and disabled
             and all(parsed[k] == [model] for k in ("init_models", "assistant_models", "usage_models")))
    receipt = {"model": model, "return_code": code, "failure": failure, "technical_valid": valid,
               "seconds": round(time.monotonic() - started, 3), "disabled_inventory": inventory,
               "tool_uses": tool_uses, "usage_reports": [{k: r.get(k) for k in ("usage", "modelUsage", "total_cost_usd", "duration_ms")} for r in records if r.get("type") == "result"], **parsed}
    (out / "reply.txt").write_text(final, encoding="utf-8", newline="\n")
    save(out / "receipt.json", receipt)
    if not valid:
        raise RuntimeError("model binding/tool isolation/response failure; preserve raw and do not retry")
    return final, receipt


def source_hashes(core_root: Path, config: dict) -> dict:
    paths = [(p, core_root / p) for p in config["context_files"]]
    paths += [(str(p.relative_to(ROOT)), p) for p in (Path(__file__), HERE / "case.json", REPLAY_PATH, REPLAY.BASE_PATH)]
    return {name: sha(path) for name, path in paths}


def check_core(core_root: Path, config: dict) -> None:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=core_root, text=True).strip()
    if head != config["core_commit"]:
        raise RuntimeError("core root must be the fixed baseline audit tree")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=core_root, text=True).strip():
        raise RuntimeError("core baseline tree must be clean")


def prepare(output: Path, core_root: Path) -> dict:
    config = read_json(HERE / "case.json")
    check_core(core_root, config)
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise RuntimeError("commit preregistration and harness before preparation")
    output.mkdir(parents=True, exist_ok=False)
    contexts = [{"path": p, "text": (core_root / p).read_text(encoding="utf-8")} for p in config["context_files"]]
    fixture = {"config": config, "sources_sha256": source_hashes(core_root, config), "contexts": contexts,
               "context_method": "Harness injects frozen Skill and news leaf; replay activation maps this host read, not a Claude tool call.",
               "harness_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    save(output / "fixture.json", fixture)
    return {"prepared": True, "case": config["id"], "providers": list(config["providers"])}


def run_provider(output: Path, core_root: Path, provider: str) -> dict:
    fixture = read_json(output / "fixture.json")
    config = fixture["config"]
    check_core(core_root, config)
    if source_hashes(core_root, config) != fixture["sources_sha256"]:
        raise RuntimeError("frozen sources changed")
    model = config["providers"][provider]
    lane = output / "providers" / provider
    lane.mkdir(parents=True, exist_ok=False)
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("existing Claude CLI required; no installation")
    prompt = ("以下是本轮固定写作上下文。材料事实仅以末尾用户任务为准。你没有任何工具；直接完成写稿。\n\n"
              + "\n\n".join(f"=== {c['path']} ===\n{c['text']}" for c in fixture["contexts"])
              + "\n\n=== 用户任务 ===\n" + config["prompt"])
    d0, generation = restricted_reply(model, prompt, lane / "generation", claude)
    sample = {"id": f"date-real-{provider}", "provider": provider, "case_id": config["id"],
              "arm": "baseline", "request": config["prompt"], "d0": d0, "source_model": model,
              "activation_evidence": fixture["context_method"]}
    REPLAY.cli_reply = restricted_reply
    replay = REPLAY.run_sample(sample, core_root, lane / "hook", claude, set(config["providers"].values()))
    final = (lane / "hook/final-visible.txt").read_text(encoding="utf-8") if replay["status"] == "allowed" else None
    events = read_json(lane / "hook/events.json")
    date_checks = [e["record_after"]["source_bound_date"] for e in events
                   if e.get("record_after") and "source_bound_date" in e["record_after"]]
    reproduced = "2020" not in d0 and final is not None and "2020年9月5日" in final
    result = {"provider": provider, "model": model, "case_id": config["id"], "prompt": config["prompt"],
              "d0": d0, "final_visible": final, "d0_sha256": REPLAY.digest(d0),
              "final_visible_sha256": REPLAY.digest(final) if final is not None else None,
              "generation": generation, "hook": {k: replay[k] for k in ("status", "call_count", "finding_count", "delivery_verified", "unchanged_from_d0", "calls")},
              "date_checks": date_checks, "wrong_year_introduced_by_hook": reproduced,
              "status": "REPRODUCED_REQUIRES_HUMAN_CHECK" if reproduced else "NOT_REPRODUCED",
              "raw_files_sha256": {str(p.relative_to(lane)): sha(p) for p in lane.rglob("*") if p.is_file() and p.suffix in (".txt", ".json", ".jsonl") and "runtime" not in p.parts and "core-data" not in p.parts}}
    save(lane / "result.json", result)
    return {k: result[k] for k in ("provider", "status", "d0", "final_visible", "wrong_year_introduced_by_hook")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--provider", choices=("alibaba2", "minimax"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--core-root", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output.resolve(), args.core_root.resolve()) if args.prepare else run_provider(args.output.resolve(), args.core_root.resolve(), args.provider)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
