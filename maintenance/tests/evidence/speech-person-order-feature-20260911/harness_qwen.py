"""Isolated, single-attempt MIT A/B writing host.

Generic Qwen Code isolation/stream collection adapted from the public test-host
method inspected at owp-mit-loop-validation-20260911, commit 0f8b59a7.
No Pro product, Hook, Loop, revision or adjudication implementation is imported.
Preparation and --help never call a model. Each write command makes one
fresh-session CLI invocation, with no automatic model substitution or retry.
Single-pair, tool-free inline cold review lives in harness_cold_inline.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
WRITERS = ("alibaba-token-plan/qwen3.8-flash", "alibaba-token-plan-2/qwen3.8-flash")
REVIEWER = "alibaba-token-plan-2/qwen3.8-max"
DISABLED = ["run_shell_command", "write_file", "edit", "web_fetch", "web_search",
            "save_memory", "agent", "list_agents", "send_message", "task_stop",
            "enter_plan_mode", "exit_plan_mode", "create_goal", "update_goal", "get_goal",
            "ask_user_question", "todo_write", "browser", "lsp", "notebook_edit",
            "record_artifact", "enter_worktree", "exit_worktree", "tool_search"]
# Exact built-in registry names inspected in installed Qwen Code 0.22.0
# chunks/chunk-6NFAEG54.js, packages/core/src/tools/tool-names.ts. Empty tools.core
# alone means unrestricted, so inline review disables every registry name.
INLINE_DISABLED = sorted(set(DISABLED) | {
    "read_file", "zoom_image", "grep_search", "glob", "skill", "image_gen", "list_directory",
    "cron_create", "cron_list", "cron_delete", "loop_wakeup", "create_sub_session",
    "task_create", "task_update", "task_list", "team_create", "team_delete", "team_plan_approval",
    "structured_output", "monitor", "read_mcp_resource", "workflow", "artifact", "display_image",
})
NETWORK_GUARD = r"""const net = require('node:net');
const fs = require('node:fs');
const original = net.Socket.prototype.connect;
net.Socket.prototype.connect = function(...args) {
  let first = args[0]; if (Array.isArray(first)) first = first[0];
  const host = typeof first === 'object' && first !== null ? (first.host || 'localhost')
    : (typeof args[1] === 'string' ? args[1] : 'localhost');
  if (!['127.0.0.1', 'localhost', '::1'].includes(host)) {
    fs.appendFileSync(process.env.QWEN_HARNESS_NETWORK_LOG,
      JSON.stringify({event:'blocked_non_loopback',host})+'\n');
    throw new Error('Writing test permits loopback connections only');
  }
  return original.apply(this, args);
};
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def manifest(folder: Path) -> dict:
    return {p.relative_to(folder).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
            for p in sorted(folder.rglob("*")) if p.is_file()}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def prepare(plan_path: Path, out: Path) -> None:
    plan = read(plan_path)
    assert plan["writers"] == list(WRITERS), "Writer routes must be explicitly preregistered"
    assert plan["reviewer"] == REVIEWER
    assert plan["effort"] in {"low", "medium", "high", "max"}
    assert plan["cold_effort"] in {"low", "medium", "high", "max"}
    assert len({c["id"] for c in plan["cases"]}) == len(plan["cases"])
    out.mkdir(parents=True, exist_ok=False)
    commits, manifests = {}, {}
    for arm in ("baseline", "candidate"):
        # Resolve once, before enumerating or reading the frozen tree.
        commit = git("rev-parse", plan[arm + "_commit"] + "^{commit}").decode().strip()
        commits[arm] = commit
        target = out / "frozen" / arm
        for name in git("ls-tree", "-r", "--name-only", commit, "--", "chinese-official-writing").decode().splitlines():
            relative = Path(name).relative_to("chinese-official-writing")
            dest = target / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(git("show", commit + ":" + name))
        manifests[arm] = manifest(target)
        save(out / (arm + "-manifest.json"), manifests[arm])
    actual_diff = sorted(p for p in manifests["baseline"].keys() | manifests["candidate"].keys()
                         if manifests["baseline"].get(p) != manifests["candidate"].get(p))
    assert actual_diff == sorted(plan["expected_diff"]), {"actual_diff": actual_diff}
    prompts = {}
    for case in plan["cases"]:
        assert case["id"] and all(c.isalnum() or c in "-_" for c in case["id"])
        source = Path(case["prompt_file"])
        if not source.is_absolute():
            source = plan_path.parent / source
        data = source.read_bytes()
        target = out / "prompts" / (case["id"] + ".txt")
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(data)
        prompts[case["id"]] = sha(data)
    freeze = {"commits": commits, "expected_diff": actual_diff, "plan": plan,
              "plan_sha256": sha(plan_path.read_bytes()), "prompt_sha256": prompts,
              "harness_sha256": sha(Path(__file__).read_bytes()),
              "cold_harness_sha256": sha(Path(__file__).with_name("harness_cold_inline.py").read_bytes()),
              "automatic_retries": 0, "hook_enabled": False,
              "source_scope": "Complete canonical Git tree; no other installed skill or Pro implementation."}
    save(out / "freeze.json", freeze)
    print(json.dumps({"prepared": True, "commits": commits, "actual_diff": actual_diff}), flush=True)


def settings(model: str, timeout: int, max_tokens: int, effort: str, *, mode="writer") -> dict:
    assert effort in {"low", "medium", "high", "max"}
    assert mode in {"writer", "inline_cold"}
    disabled = INLINE_DISABLED if mode == "inline_cold" else DISABLED
    return {"general": {"enableAutoUpdate": False, "showSessionRecap": False},
            "privacy": {"usageStatisticsEnabled": False}, "telemetry": {"enabled": False},
            "security": {"auth": {"selectedType": "openai"}},
            "modelProviders": {"openai": [{"id": model, "baseUrl": "http://127.0.0.1:10100/v1",
                "envKey": "OPENAI_API_KEY", "generationConfig": {"timeout": timeout * 1000,
                    "maxRetries": 0, "samplingParams": {"max_tokens": max_tokens, "reasoning_effort": effort}}}]},
            "model": {"name": model, "maxSessionTurns": 1 if mode == "inline_cold" else 18},
            "context": {"fileName": "QWEN_HARNESS_NO_CONTEXT.md", "loadFromIncludeDirectories": False},
            "memory": {"enableManagedAutoMemory": False, "enableManagedAutoDream": False,
                       "enableAutoSkill": False, "enableTeamMemory": False, "enableTeamMemorySync": False},
            "disableAllHooks": True, "hooks": {}, "mcpServers": {},
            "tools": {"core": [] if mode == "inline_cold" else ["read_file", "glob", "grep_search"], "disabled": disabled,
                      "computerUse": {"enabled": False}, "approvalMode": "default"},
            "permissions": {"allow": [] if mode == "inline_cold" else ["Read", "Glob", "Grep"], "deny": disabled}}


def child_env(home: Path, run: Path) -> dict:
    keep = {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT", "TEMP", "TMP",
            "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS"}
    env = {k: v for k, v in os.environ.items() if k.upper() in keep}
    env.update({"HOME": str(home), "USERPROFILE": str(home), "QWEN_HOME": str(home / ".qwen"),
                "APPDATA": str(home / "AppData/Roaming"), "LOCALAPPDATA": str(home / "AppData/Local"),
                "XDG_CONFIG_HOME": str(home / ".config"), "OPENAI_API_KEY": "test-local-proxy-placeholder",
                "OPENAI_BASE_URL": "http://127.0.0.1:10100/v1", "NO_PROXY": "127.0.0.1,localhost,::1",
                "QWEN_CODE_SYSTEM_SETTINGS_PATH": str(run / "system-settings.json"),
                "QWEN_CODE_SYSTEM_DEFAULTS_PATH": str(run / "system-defaults.json"),
                "NODE_OPTIONS": "--require=" + str(run / "loopback-only.cjs"),
                "QWEN_HARNESS_NETWORK_LOG": str(run / "network.jsonl"), "CI": "true",
                "NO_COLOR": "1", "GEMINI_TELEMETRY_ENABLED": "false"})
    return env


def terminate_owned(process: subprocess.Popen) -> dict:
    result = {"owned_pid": process.pid, "method": "taskkill_tree" if os.name == "nt" else "process_group"}
    try:
        if os.name == "nt":
            stopped = subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                                     capture_output=True, timeout=30, creationflags=0x08000000)
            result.update(exit_code=stopped.returncode, tree_stopped=stopped.returncode == 0)
        else:
            assert os.getpgid(process.pid) == process.pid
            os.killpg(process.pid, signal.SIGKILL)
            result["tree_stopped"] = True
        process.wait(timeout=30)
    except (OSError, subprocess.TimeoutExpired, AssertionError) as exc:
        result.update(error=type(exc).__name__, tree_stopped=False)
    return result


def collect(run: Path, snapshot: Path, model: str, code, timed_out: bool, cleanup,
            elapsed: float, config: dict, client_metadata: dict, *, persist=True) -> dict:
    events, malformed = [], []
    for number, line in enumerate((run / "stdout.jsonl").read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            malformed.append(number)
    calls, results = [], {}
    for event_index, event in enumerate(events):
        for part in event.get("message", {}).get("content", []):
            if not isinstance(part, dict):
                continue
            if part.get("type") == "tool_use":
                calls.append({"event_index": event_index, **part})
            elif part.get("type") == "tool_result":
                results.setdefault(part.get("tool_use_id"), []).append({"event_index": event_index, **part})
    trace = []
    for call in calls:
        returned = results.get(call.get("id"), [])
        record = {"call": call, "results": returned,
                  "result_sha256": [sha(json.dumps(r, ensure_ascii=False, sort_keys=True).encode()) for r in returned]}
        if call.get("name") == "read_file":
            raw = call.get("input", {}).get("file_path", "")
            path = Path(raw)
            path = (path if path.is_absolute() else run / "workspace" / path).resolve()
            inside = path.is_relative_to(snapshot.resolve())
            record.update(path=str(path), within_snapshot=inside,
                          success=bool(returned) and all(not r.get("is_error", False) for r in returned))
            if inside and path.is_file():
                record.update(relative_path=path.relative_to(snapshot.resolve()).as_posix(),
                              file_sha256=sha(path.read_bytes()), file_bytes=path.stat().st_size)
        trace.append(record)
    save(run / "tool-trace.json", trace)
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    body = result.get("result", "") if result else ""
    if not isinstance(body, str):
        body = json.dumps(body, ensure_ascii=False)
    (run / "final.md").write_text(body, encoding="utf-8")
    reads = [r for r in trace if r["call"].get("name") == "read_file"]
    result_ok = bool(result) and result.get("subtype") == "success" and not result.get("is_error", False)
    model_ok = bool(init) and init.get("model") == model
    version_ok = (bool(init) and init.get("qwen_code_version") == client_metadata["installed_package_version"]
                  == client_metadata.get("expected_package_version", "0.22.0"))
    read_boundary = all(r.get("within_snapshot", False) for r in reads)
    tool_boundary = all(c.get("name") in {"read_file", "glob", "grep_search"} for c in calls)
    status = ("UNAVAILABLE" if not model_ok or not version_ok else "TERMINATED" if timed_out or code != 0
              else "COMPLETE" if result_ok and body.strip() and read_boundary and tool_boundary else "INVALID")
    receipt = {"model_requested": model, "actual_client_model": init.get("model") if init else None,
               "init": init, "client_metadata": client_metadata, "client_version_matches": version_ok,
               "configured_effort": config["modelProviders"]["openai"][0]["generationConfig"]["samplingParams"]["reasoning_effort"],
               "effort_evidence": "generationConfig.samplingParams.reasoning_effort; init does not echo effort",
               "model_identity_scope": "Native Qwen Code init identifies configured client route, not upstream wire identity",
               "status": status, "technical_valid": status == "COMPLETE", "exit_code": code,
               "timed_out": timed_out, "cleanup": cleanup, "elapsed_seconds": round(elapsed, 3),
               "non_json_line_numbers": malformed, "fresh_session": True, "automatic_retries": 0,
               "hook_enabled": False, "read_paths_within_snapshot": read_boundary,
               "actual_tool_allowlist_pass": tool_boundary, "read_calls": len(reads),
               "tool_calls_count": len(calls),
               "read_evidence_limit": "A file hash binds source bytes, not a claim that the whole page was read. Use each read offset/limit and raw tool result. Glob/grep results remain in tool-trace; their search summaries do not establish full-page exposure.",
               "successful_read_calls": sum(r["success"] for r in reads),
               "actual_read_pages": [{k: r[k] for k in ("relative_path", "file_sha256", "file_bytes", "success") if k in r}
                                     | {"input": r["call"].get("input", {}), "result_sha256": r["result_sha256"]} for r in reads],
               "configuration": config, "result_event": result,
               "hashes": {n: sha((run / n).read_bytes()) for n in ("prompt.txt", "stdout.jsonl", "stderr.txt", "final.md", "tool-trace.json")}}
    if persist:
        save(run / "receipt.json", receipt)
    return receipt


def execute(run: Path, model: str, prompt_builder, snapshot_builder, plan: dict, *, mode="writer", verifier=None) -> dict:
    run.mkdir(parents=True, exist_ok=False)
    home, work = run / "home", run / "workspace"
    (home / ".qwen").mkdir(parents=True)
    (work / ".git").mkdir(parents=True)
    snapshot = work / "input"
    snapshot_builder(snapshot)
    before = manifest(snapshot)
    save(run / "source-manifest.json", before)
    config = settings(model, plan.get("request_timeout_seconds", 240), plan.get("max_output_tokens", 12000),
                      plan["cold_effort"] if mode == "inline_cold" else plan["effort"], mode=mode)
    save(home / ".qwen/settings.json", config)
    for name in ("system-settings.json", "system-defaults.json"):
        save(run / name, {})
    (run / "loopback-only.cjs").write_text(NETWORK_GUARD, encoding="utf-8")
    prompt = prompt_builder(snapshot)
    (run / "prompt.txt").write_text(prompt, encoding="utf-8")
    node = shutil.which("node")
    cli = Path(os.environ["APPDATA"]) / "npm/node_modules/@qwen-code/qwen-code/cli-entry.js"
    assert node and cli.is_file(), "Installed Qwen Code or Node unavailable"
    metadata = {"node": node, "cli": str(cli), "cli_sha256": sha(cli.read_bytes()),
                "installed_package_version": read(cli.parent / "package.json")["version"],
                "expected_package_version": plan.get("client_version_expected", "0.22.0"),
                "python": sys.executable, "python_version": sys.version}
    command = [node, str(cli), "--model", model, "--output-format", "stream-json", "--prompt", prompt]
    save(run / "command.json", {"argv": command, "cwd": str(work), "client_metadata": metadata})
    started, timed_out, cleanup = time.time(), False, None
    with (run / "stdout.jsonl").open("wb") as stdout, (run / "stderr.txt").open("wb") as stderr:
        proc = subprocess.Popen(command, cwd=work, env=child_env(home, run), stdout=stdout, stderr=stderr,
                                start_new_session=os.name != "nt", creationflags=0x08000000 if os.name == "nt" else 0)
        try:
            proc.wait(timeout=plan.get("timeout_seconds", 600))
        except subprocess.TimeoutExpired:
            timed_out = True
            cleanup = terminate_owned(proc)
    receipt = collect(run, snapshot, model, proc.returncode, timed_out, cleanup, time.time() - started, config, metadata,
                      persist=False)
    receipt["snapshot_unchanged"] = before == manifest(snapshot)
    if not receipt["snapshot_unchanged"]:
        receipt.update(technical_valid=False, status="INVALID")
    receipt["mode"] = mode
    if verifier is not None:
        verifier(receipt, run)
    save(run / "receipt.json", receipt)
    print(json.dumps({k: receipt[k] for k in ("model_requested", "status", "exit_code", "timed_out", "elapsed_seconds", "read_calls")}), flush=True)
    return receipt


def write_case(args) -> dict:
    freeze = read(args.out / "freeze.json")
    assert sha(Path(__file__).read_bytes()) == freeze["harness_sha256"], "Runner changed after freeze"
    assert args.route in freeze["plan"]["writers"]
    assert args.case in freeze["prompt_sha256"]
    task = args.out / "prompts" / (args.case + ".txt")
    assert sha(task.read_bytes()) == freeze["prompt_sha256"][args.case]
    source = args.out / "frozen" / args.arm
    assert manifest(source) == read(args.out / (args.arm + "-manifest.json"))
    run = args.out / "runs" / args.route.split("/")[0] / args.case / args.arm / ("attempt-" + str(args.attempt))
    def prompt(snapshot):
        return ("这是一次只读、隔离的真实写稿测试。请先读取 " + (snapshot / "SKILL.md").as_posix() +
                "，按入口选择任务所需参考页，不整批读取。只允许读取该 input 目录内的 Skill 文件；"
                "不读其他目录、历史或记忆，不联网，不启用 Hook，不执行脚本。遵从下列原始请求的交付要求。\n\n" +
                task.read_text(encoding="utf-8-sig"))
    return execute(run, args.route, prompt, lambda dest: shutil.copytree(source, dest), freeze["plan"])


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--plan", type=Path, required=True)
    prep.add_argument("--out", type=Path, required=True)
    write = sub.add_parser("write")
    write.add_argument("--out", type=Path, required=True)
    write.add_argument("--route", choices=WRITERS, required=True)
    write.add_argument("--case", required=True)
    write.add_argument("--arm", choices=("baseline", "candidate"), required=True)
    write.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()
    args.out = args.out.resolve()
    if args.action == "prepare":
        prepare(args.plan.resolve(), args.out)
        return 0
    receipt = write_case(args)
    return 0 if receipt["technical_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
