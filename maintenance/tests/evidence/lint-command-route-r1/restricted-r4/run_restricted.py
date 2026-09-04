"""Frozen two-arm MCP-only writing test; never launches the native-shell writer."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
OUTPUT = REPO / "output/lint-command-route-r1/restricted-r4"
SERVER = HERE / "stdio_tools.py"
BASE_PATH = HERE.parents[1] / "v167-formulaic-mechanicality-real-first/harness.py"
spec = importlib.util.spec_from_file_location("restricted_claude_base", BASE_PATH)
BASE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BASE)
TOOL_NAMES = ["mcp__audit__read_document", "mcp__audit__prose_lint"]


class InitGuard:
    def __init__(self, model: str):
        self.model, self.initialized = model, False

    def observe(self, event: dict) -> None:
        if not isinstance(event, dict):
            raise ValueError("invalid_host_event")
        if event.get("type") == "system" and event.get("subtype") == "init":
            if sorted(event.get("tools", [])) != sorted(TOOL_NAMES) or event.get("model") != self.model:
                raise ValueError("init_tool_or_model_mismatch_stopped")
            self.initialized = True
        elif event.get("type") in ("assistant", "user", "result", "stream_event") and not self.initialized:
            raise ValueError("execution_before_initialization_stopped")
        elif event.get("type") == "assistant" and event.get("message", {}).get("model") != self.model:
            raise ValueError("assistant_model_mismatch_stopped")

    def finish(self) -> None:
        if not self.initialized:
            raise ValueError("missing_initialization_stopped")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=REPO)


def prepare(output: Path) -> dict:
    if output.exists() or git("status", "--porcelain").strip():
        raise RuntimeError("commit the prototype and use a new output directory")
    case = json.loads((HERE.parent / "cases.json").read_text(encoding="utf-8"))
    control = git("rev-parse", "5cb696fe").decode().strip()
    experiment = git("rev-parse", "HEAD").decode().strip()
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("existing Claude CLI missing")
    catalog = json.loads((Path.home() / ".codex/opencodex-catalog.json").read_text(encoding="utf-8"))["models"]
    for model in case["providers"].values():
        match = next((item for item in catalog if item.get("slug") == model), None)
        if not match or "max" not in {r["effort"] for r in match.get("supported_reasoning_levels", [])}:
            raise RuntimeError("exact existing model/max binding missing")
    fixture = {"host": "Claude CLI MCP-only; not a native command A/B", "case": case,
               "claude": claude, "claude_version": subprocess.check_output([claude, "--version"], text=True).strip(),
               "python": str(Path(sys.executable).resolve()), "python_sha256": sha(Path(sys.executable).read_bytes()),
               "harness_commit": experiment, "arms": {}, "tool_names": TOOL_NAMES,
               "source_sha256": {str(p.relative_to(REPO)): sha(p.read_bytes()) for p in (SERVER, Path(__file__), BASE_PATH, HERE / "check_contract.py")},
               "system_prompt": "你是中文正式材料改稿助手。当前项目的 Skill 入口对应 read_document 的 ID SKILL.md；通知原稿.md 对应 ID D0。参考资料及脚本源码按工具列出的文档 ID 按需读取。校对工具是 prose_lint；没有文件系统、Shell 或网络工具。先读取本次 Skill 和 D0，再完成用户任务。",
               "prompt_sha256": sha(case["prompt"].encode("utf-8"))}
    for arm, commit in (("control", control), ("experiment", experiment)):
        root = output / "snapshots" / arm
        files = git("ls-tree", "-r", "--name-only", commit, "chinese-official-writing").decode().splitlines()
        documents = {}
        for name in files:
            relative = Path(name).relative_to("chinese-official-writing").as_posix()
            selected = relative in ("SKILL.md", "scripts/prose_lint.py") or relative.startswith("references/")
            if not selected or relative == "references/delivery-review-gate.md":
                continue
            data = git("show", f"{commit}:{name}")
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            documents[relative] = {"path": str(target), "sha256": sha(data), "bytes": len(data)}
        d0 = root / "D0.txt"
        d0.write_text(case["material"], encoding="utf-8", newline="\n")
        documents["D0"] = {"path": str(d0), "sha256": sha(d0.read_bytes()), "bytes": d0.stat().st_size}
        script = root / "scripts/prose_lint.py"
        manifest = {"commit": commit, "documents": documents, "script": str(script),
                    "script_sha256": sha(script.read_bytes()), "python": fixture["python"],
                    "python_sha256": fixture["python_sha256"]}
        write_json(root / "manifest.json", manifest)
        fixture["arms"][arm] = {"commit": commit, "manifest": str(root / "manifest.json"),
                                "manifest_sha256": sha((root / "manifest.json").read_bytes())}
    manifests = [json.loads(Path(fixture["arms"][a]["manifest"]).read_text(encoding="utf-8"))["documents"]
                 for a in ("control", "experiment")]
    changes = [key for key in manifests[0] if manifests[0][key]["sha256"] != manifests[1][key]["sha256"]]
    if changes not in (["references/final-review-layers.md"], ["SKILL.md"]) or set(manifests[0]) != set(manifests[1]):
        raise RuntimeError(f"not the frozen single product atom: {changes}")
    fixture["product_changed_documents"] = changes
    write_json(output / "fixture.json", fixture)
    return fixture


def run(output: Path, provider: str, arm: str) -> dict:
    if (output / "STOP_BATCH.json").exists():
        raise RuntimeError("a prior technical failure stopped this batch; no further model calls")
    fixture = json.loads((output / "fixture.json").read_text(encoding="utf-8"))
    contract = json.loads((output / "contract.json").read_text(encoding="utf-8"))
    if contract["status"] != "PASS" or contract["fixture_sha256"] != sha((output / "fixture.json").read_bytes()):
        raise RuntimeError("matching no-model tool contract must pass before model invocation")
    for relative, expected in fixture["source_sha256"].items():
        if sha((REPO / relative).read_bytes()) != expected:
            raise RuntimeError("frozen harness source changed")
    root = output / "runs" / provider / arm
    if root.exists():
        raise RuntimeError("preserve existing run; no automatic retry")
    root.mkdir(parents=True)
    manifest = Path(fixture["arms"][arm]["manifest"])
    if sha(manifest.read_bytes()) != fixture["arms"][arm]["manifest_sha256"]:
        raise RuntimeError("frozen manifest changed")
    log = root / "tool-calls.jsonl"
    mcp = {"mcpServers": {"audit": {"command": fixture["python"],
            "args": ["-I", "-B", str(SERVER), "--manifest", str(manifest), "--log", str(log)]}}}
    config = root / "mcp.json"
    write_json(config, mcp)
    model = fixture["case"]["providers"][provider]
    environment = BASE.build_environment(model, root / "runtime")
    command = [fixture["claude"], "--setting-sources", "", "--no-session-persistence", "--disable-slash-commands",
               "--tools", "", "--strict-mcp-config", "--mcp-config", str(config),
               "--allowedTools", ",".join(TOOL_NAMES), "--permission-mode", "dontAsk",
               "--system-prompt", fixture["system_prompt"], "--print", "--verbose", "--output-format", "stream-json",
               "--model", model, "--effort", "max"]
    write_json(root / "invocation.json", {"argv": command, "prompt": fixture["case"]["prompt"],
              "prompt_sha256": fixture["prompt_sha256"], "cwd": str(root / "runtime/work"),
              "model_binding": model, "effort": "max", "gateway": BASE.GATEWAY,
              "credential": "existing process-local dummy token; no real credential copied"})
    stream, stderr = root / "stream.jsonl", root / "stderr.txt"
    print(f"START {provider} {arm} tools={TOOL_NAMES}", flush=True)
    started = time.monotonic()
    early_failure = []
    guard = InitGuard(model)
    with stream.open("w", encoding="utf-8", newline="\n") as stdout, stderr.open("w", encoding="utf-8", newline="\n") as errors:
        with subprocess.Popen(command, cwd=root / "runtime/work", env=environment, stdin=subprocess.PIPE,
                              text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE,
                              stderr=errors, shell=False) as process:
            def expire():
                early_failure.append("timeout_900_seconds")
                write_json(output / "STOP_BATCH.json", {"provider": provider, "arm": arm, "reasons": early_failure})
                process.kill()
            timer = threading.Timer(900, expire)
            timer.start()
            try:
                process.stdin.write(fixture["case"]["prompt"])
                process.stdin.close()
                for line in process.stdout:
                    stdout.write(line)
                    stdout.flush()
                    try:
                        event = json.loads(line)
                        guard.observe(event)
                    except (json.JSONDecodeError, ValueError) as failure:
                        early_failure.append(str(failure))
                        write_json(output / "STOP_BATCH.json", {"provider": provider, "arm": arm, "reasons": early_failure})
                        process.kill()
                        break
                    if event.get("type") == "system" and event.get("subtype") == "init":
                        print(f"INIT_CHECK PASS {provider} {arm} tools={event['tools']}", flush=True)
                return_code = process.wait()
            finally:
                timer.cancel()
    try:
        guard.finish()
    except ValueError as failure:
        early_failure.append(str(failure))
        write_json(output / "STOP_BATCH.json", {"provider": provider, "arm": arm, "reasons": early_failure})
    parsed = BASE.parse_stream(stream)
    (root / "final.txt").write_text(parsed["final"], encoding="utf-8", newline="\n")
    events = []
    for line in stream.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    inits = [e for e in events if e.get("type") == "system" and e.get("subtype") == "init"]
    results = [e for e in events if e.get("type") == "result"]
    tools_exposed = sorted({name for init in inits for name in init.get("tools", [])})
    violations = list(early_failure)
    if tools_exposed != sorted(TOOL_NAMES):
        violations.append("unexpected_exposed_tool_set")
    for field in ("init_models", "assistant_models", "usage_models"):
        if parsed[field] != [model]:
            violations.append(f"model_binding:{field}")
    if return_code != 0 or parsed["result_count"] != 1 or parsed["result_errors"] != [False] or not parsed["final"].strip():
        violations.append("incomplete_result")
    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    read_ids = {c.get("id") for c in calls if c["tool"] == "read_document" and c["status"] == "OK"}
    if not {"SKILL.md", "D0"}.issubset(read_ids):
        violations.append("missing_skill_or_d0_read")
    if violations:
        write_json(output / "STOP_BATCH.json", {"provider": provider, "arm": arm, "reasons": violations})
    receipt = {"provider": provider, "arm": arm, "seconds": round(time.monotonic() - started, 3),
               "return_code": return_code, "technical_violations": violations, "parsed": parsed,
               "tools_exposed": tools_exposed, "mcp_servers": [s for init in inits for s in init.get("mcp_servers", [])],
               "tool_calls": calls, "read_utf8_bytes": sum(c.get("returned_utf8_bytes", 0) for c in calls),
               "reported_cost_and_usage": [{k: e.get(k) for k in ("total_cost_usd", "usage", "modelUsage", "num_turns")} for e in results],
               "cost_scope": "CLI-reported estimate and usage; not a provider billing receipt"}
    write_json(root / "receipt.json", receipt)
    print(f"END {provider} {arm}: {violations}", flush=True)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=OUTPUT)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--provider", choices=("alibaba2", "minimax"))
    parser.add_argument("--arm", choices=("control", "experiment"))
    args = parser.parse_args()
    if args.provider and not args.arm:
        parser.error("--provider requires one explicit --arm")
    result = prepare(args.output_root.resolve()) if args.prepare else run(args.output_root.resolve(), args.provider, args.arm)
    print(json.dumps({"action": "prepare" if args.prepare else f"{args.provider}/{args.arm}",
                      "technical_violations": result.get("technical_violations")}, ensure_ascii=False), flush=True)
    if result.get("technical_violations"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
