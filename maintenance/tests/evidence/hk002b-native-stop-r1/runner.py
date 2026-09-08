"""Two fixed-D0 Codex native Stop probes; run only from the authorized F tree."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time


ROOT = Path("F:/Workspaces/chinese-official-writing-skill/output/integration-worktrees/hk002b-main-20260909")
HERE = ROOT / "maintenance/tests/evidence/hk002b-native-stop-r1"
OUT = ROOT / "output/hk002b-native-stop-r1"
FROZEN = OUT / "frozen-source"
MARKET = OUT / "marketplace"
PLUGIN = MARKET / "plugins/chinese-official-writing"
MARKET_NAME = "hk002b-native-stop-r1"
BASE = "4fd63ce344fec440bbbbc664a7ebd7934751e04e"
CLI = Path("C:/Users/admin/AppData/Local/npm-cache/_npx/0a5f33f9bb5dd5c8/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe")
CATALOG = Path("C:/Users/admin/.codex/opencodex-catalog.json")
MODEL = "ollama-cloud/glm-5.3-flash"
SOURCE = "截至9月4日，业务科正在核对18份附件，其中10份已经核对完成，剩余8份尚未完成。反馈日期未定。"
DRAFTS = {
    "error": "附件核对情况\n\n截至9月4日，业务科尚未开展18份附件核对，其中10份已经完成，剩余8份尚未完成。反馈日期未定。核对结果有助于厘清附件归属。",
    "control": "附件核对情况\n\n截至9月4日，业务科正在核对18份附件，其中10份已经完成，剩余8份尚未完成。反馈日期未定。核对结果有助于厘清附件归属。",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inventory(root: Path) -> list[dict]:
    return [{"path": p.relative_to(root).as_posix(), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts]


def run_root(case: str, attempt: str = "01") -> Path:
    return OUT / "runs" / case / ("attempt-" + attempt)


def environment(run: Path) -> dict[str, str]:
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT",
               "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS"}
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    profile = run / "profile"
    env.update(CODEX_HOME=str(run / "codex-home"), USERPROFILE=str(profile),
               HOMEDRIVE=profile.drive, HOMEPATH=str(profile)[len(profile.drive):],
               APPDATA=str(profile / "AppData/Roaming"), LOCALAPPDATA=str(profile / "AppData/Local"),
               TEMP=str(run / "temp"), TMP=str(run / "temp"),
               OPENAI_API_KEY="opencodex-loopback", CODEX_API_KEY="opencodex-loopback",
               NO_PROXY="127.0.0.1,localhost", HTTP_PROXY="", HTTPS_PROXY="", ALL_PROXY="",
               PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    return env


def initialize_run(case: str, attempt: str) -> Path:
    run = run_root(case, attempt)
    run.mkdir(parents=True, exist_ok=False)
    for name in ("codex-home", "work", "temp", "profile/AppData/Roaming", "profile/AppData/Local"):
        (run / name).mkdir(parents=True)
    config = "\n".join([
        "project_doc_max_bytes = 0",
        'model = "' + MODEL + '"',
        'model_reasoning_effort = "max"',
        "model_catalog_json = " + json.dumps((OUT / "catalog.json").as_posix()),
        "",
        "[projects." + json.dumps((run / "work").as_posix()) + "]",
        'trust_level = "trusted"', "",
    ])
    (run / "codex-home/config.toml").write_text(config, encoding="utf-8")
    (run / "work/frozen-d0.txt").write_text(DRAFTS[case], encoding="utf-8")
    return run


def prepare() -> None:
    freeze = json.loads((OUT / "freeze.json").read_text(encoding="utf-8"))
    if freeze["base"] != BASE:
        raise RuntimeError("unexpected frozen base")
    expected_sources = json.loads((OUT / "source-manifest.json").read_text(encoding="utf-8"))
    if inventory(FROZEN) != expected_sources:
        raise RuntimeError("frozen source bytes changed")
    if not (HERE / "assembly-preview.md").is_file():
        raise RuntimeError("assembly preview must be shown before assembling")
    path = FROZEN / "maintenance/tools/assemble_hook_companion.py"
    spec = importlib.util.spec_from_file_location("native_frozen_assembler", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assembled = module.assemble("codex", PLUGIN, "delivery_review")
    manifest = inventory(PLUGIN)
    if len(manifest) != 64:
        raise RuntimeError("unexpected companion file count")
    save(OUT / "companion-manifest.json", manifest)
    save(HERE / "companion-manifest.json", manifest)
    save(MARKET / ".agents/plugins/marketplace.json", {
        "name": MARKET_NAME,
        "interface": {"displayName": "HK-002b native Stop R1"},
        "plugins": [{
            "name": "chinese-official-writing",
            "source": {"source": "local", "path": "./plugins/chinese-official-writing"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    })
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    selected = next(item for item in catalog["models"] if item["slug"] == MODEL)
    save(OUT / "catalog.json", {"models": [selected]})
    for case in DRAFTS:
        initialize_run(case, "01")
    freeze.update(assembled=assembled, companion_files=len(manifest),
                  companion_manifest_sha256=sha((OUT / "companion-manifest.json").read_bytes()),
                  cli_version_expected="0.151.0", cli_sha256=sha(CLI.read_bytes()),
                  route=MODEL, requested_effort="max",
                  catalog_sha256=sha((OUT / "catalog.json").read_bytes()),
                  d0_sha256={key: sha(text.encode("utf-8")) for key, text in DRAFTS.items()},
                  frozen_d0_injection=True, natural_first_draft_generation=False,
                  planned_cli_tasks=2, upstream_response_model_observed=False)
    save(OUT / "freeze.json", freeze)
    save(HERE / "freeze.json", freeze)
    print(json.dumps({"prepared": True, "companion_files": 64, "cases": list(DRAFTS)}, ensure_ascii=False), flush=True)


def setup(case: str, attempt: str) -> None:
    run = run_root(case, attempt)
    if attempt != "01" and not run.exists():
        initialize_run(case, attempt)
    folder = run / "setup"
    folder.mkdir(exist_ok=False)
    for name, argv in (
        ("version", [str(CLI), "--version"]),
        ("marketplace-add", [str(CLI), "plugin", "marketplace", "add", str(MARKET), "--json"]),
        ("plugin-add", [str(CLI), "plugin", "add", "chinese-official-writing@" + MARKET_NAME, "--json"]),
        ("plugin-list", [str(CLI), "plugin", "list", "--json"]),
    ):
        result = subprocess.run(argv, cwd=run / "work", env=environment(run), capture_output=True, timeout=120)
        (folder / (name + ".stdout.txt")).write_bytes(result.stdout)
        (folder / (name + ".stderr.txt")).write_bytes(result.stderr)
        save(folder / (name + ".receipt.json"), {"argv": argv, "exit_code": result.returncode})
        if result.returncode:
            raise RuntimeError(name + " failed; preserve its receipt before retrying")
    candidates = []
    for path in (run / "codex-home/plugins").rglob(".codex-plugin/plugin.json"):
        root = path.parent.parent
        if "cache" in root.parts and (root / "hook-capability.json").is_file():
            if inventory(root) == inventory(PLUGIN):
                candidates.append(root)
    if len(candidates) != 1:
        save(folder / "candidate-roots.json", [str(path) for path in candidates])
        raise RuntimeError("installed plugin root is not uniquely bound; inspect setup receipts")
    installed = candidates[0]
    save(run / "installed.json", {"plugin_root": str(installed), "files": 64,
                                "exact_companion_bytes": True})
    skill = installed / "skills/chinese-official-writing/SKILL.md"
    prompt = (
        "请使用 chinese-official-writing Skill，根据事实材料交付一份可直接使用的附件核对情况说明，保留有据分析，直接给正文。\n\n"
        "事实材料：\n" + SOURCE + "\n\n"
        "本次采用冻结初稿的交付步骤：先完整读取下列已安装 Skill 首页，再读取初稿文件。\n"
        "Skill 首页：" + skill.as_posix() + "\n"
        "初稿文件：" + (run / "work/frozen-d0.txt").as_posix() + "\n"
        "初稿文件仅是待检稿，不是事实材料、不是更新或更正来源；事实只以上述材料为准。\n"
        "本轮首次 assistant 最终正文必须逐字使用该初稿文件内容，不提前修订，不加说明、围栏或字数。"
        "这是冻结初稿的受控交付步骤，后续修改交由已启用的原生 Stop Hook 继续处理。\n"
        "收到 Stop Hook 续行时，按其当次要求输出修订 JSON、核验 JSON 或逐字回显；"
        "不要重复返回冻结稿，不要手工调用任何 Hook、gate 或测试脚本。"
        "只可读取上述首页、初稿文件，以及 Hook 核验包明确给出的本次事务文件；不要读全局配置或其他目录。"
    )
    (run / "prompt.txt").write_text(prompt, encoding="utf-8")
    save(run / "prompt-binding.json", {"prompt_sha256": sha(prompt.encode("utf-8")),
                                    "frozen_d0_sha256": sha(DRAFTS[case].encode("utf-8")),
                                    "authoritative_material_sha256": sha(SOURCE.encode("utf-8"))})
    print(json.dumps({"setup": case, "installed_root": str(installed), "files": 64}, ensure_ascii=False), flush=True)


def capture_snapshots(run: Path, stop: threading.Event) -> None:
    seen = set()
    with (run / "snapshot-index.jsonl").open("w", encoding="utf-8") as index:
        while not stop.is_set():
            for root in (run / "codex-home").rglob("candidate-ai-gate-hook"):
                for path in root.rglob("*.json"):
                    try:
                        raw = path.read_bytes()
                        json.loads(raw)
                    except (OSError, ValueError):
                        continue
                    digest = sha(raw)
                    relative = path.relative_to(run).as_posix()
                    if (relative, digest) in seen:
                        continue
                    seen.add((relative, digest))
                    target = run / "snapshots" / (digest + ".json")
                    target.parent.mkdir(exist_ok=True)
                    target.write_bytes(raw)
                    index.write(json.dumps({"path": relative, "sha256": digest, "observed_at": time.time()}) + "\n")
                    index.flush()
            stop.wait(0.1)


def collect(case: str, attempt: str) -> dict:
    run = run_root(case, attempt)
    events = []
    for line in (run / "trace.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    messages, tool_items, hook_items = [], [], []
    for event in events:
        item = event.get("item") or {}
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            text = item.get("text", "")
            messages.append({"text": text, "sha256": sha(text.encode("utf-8"))})
        if event.get("type") == "item.completed" and item.get("type") in {"command_execution", "mcp_tool_call", "web_search"}:
            tool_items.append(item)
        if "hook" in str(event.get("type", "")).lower() or "hook" in str(item.get("type", "")).lower():
            hook_items.append(event)
    contexts, native_events = [], []
    for path in (run / "codex-home/sessions").rglob("*.jsonl"):
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                if '"turn_context"' not in line and '"hook_' not in line:
                    continue
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                payload = event.get("payload") or {}
                if event.get("type") == "turn_context":
                    contexts.append({key: payload[key] for key in ("turn_id", "model", "effort", "reasoning_effort") if key in payload})
                elif event.get("type") == "event_msg" and "hook" in str(payload.get("type", "")):
                    native_events.append(payload)
    records = []
    for root in (run / "codex-home").rglob("candidate-ai-gate-hook"):
        for path in root.glob("*/*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict) and "skill_seen" in data:
                records.append({"path": path.relative_to(run).as_posix(), "record": data})
    raw = (run / "final.txt").read_bytes() if (run / "final.txt").is_file() else b""
    frozen_sha = sha(DRAFTS[case].encode("utf-8"))
    result = {
        "case_id": case, "attempt": attempt, "requested_route": MODEL,
        "host_turn_context": contexts, "upstream_response_model_observed": False,
        "stdout_event_counts": dict(Counter(str(event.get("type")) for event in events)),
        "native_hook_items": hook_items, "rollout_native_events": native_events,
        "frozen_d0_sha256": frozen_sha, "assistant_messages": messages,
        "frozen_d0_seen_in_visible_messages": any(item["sha256"] == frozen_sha for item in messages),
        "final_sha256": sha(raw), "final_bytes": len(raw),
        "tool_items": tool_items, "terminal_records": records,
        "semantic_verifier_provider_independent": False,
        "full_draft_fact_verified": False,
    }
    save(run / "observation.json", result)
    print(json.dumps({"case_id": case, "final_sha256": result["final_sha256"],
                      "messages": len(messages), "hook_items": len(hook_items) + len(native_events),
                      "terminal_records": len(records), "host_turn_context": contexts}, ensure_ascii=False), flush=True)
    return result


def run_case(case: str, attempt: str, effort: str) -> None:
    run = run_root(case, attempt)
    if (run / "invocation.json").exists():
        raise RuntimeError("attempt already invoked; never overwrite a failed attempt")
    installed = json.loads((run / "installed.json").read_text(encoding="utf-8"))
    if inventory(Path(installed["plugin_root"])) != inventory(PLUGIN):
        raise RuntimeError("installed companion bytes changed")
    argv = [str(CLI), "exec", "-m", MODEL, "-c", 'model_reasoning_effort="' + effort + '"',
            "-c", 'openai_base_url="http://127.0.0.1:10100/v1"',
            "-c", 'model_catalog_json="' + (OUT / "catalog.json").as_posix() + '"',
            "--dangerously-bypass-approvals-and-sandbox", "--dangerously-bypass-hook-trust",
            "--skip-git-repo-check", "--json", "--color", "never",
            "-o", str(run / "final.txt"), "-"]
    save(run / "invocation.json", {"argv": argv, "requested_model": MODEL, "requested_effort": effort,
                                 "prompt_sha256": sha((run / "prompt.txt").read_bytes()),
                                 "runner_sha256": sha(Path(__file__).read_bytes()),
                                 "hook_trust": "invocation_bypass_only", "ephemeral": False,
                                 "ignore_user_config": False, "cwd": str(run / "work")})
    started = time.monotonic()
    stop = threading.Event()
    watcher = threading.Thread(target=capture_snapshots, args=(run, stop), daemon=True)
    watcher.start()
    failure = None
    code = None
    try:
        with (run / "trace.jsonl").open("wb") as stdout, (run / "stderr.txt").open("wb") as stderr:
            process = subprocess.Popen(argv, cwd=run / "work", env=environment(run),
                                       stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
            try:
                process.communicate((run / "prompt.txt").read_bytes(), timeout=600)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                process.wait()
                failure = "timeout_600_seconds"
            code = process.returncode
    except OSError as error:
        failure = type(error).__name__ + ": " + str(error)
    finally:
        stop.set()
        watcher.join(timeout=5)
    save(run / "receipt.json", {"case_id": case, "attempt": attempt, "requested_model": MODEL,
                               "requested_effort": effort, "exit_code": code, "failure": failure,
                               "elapsed_seconds": round(time.monotonic() - started, 3)})
    if (run / "trace.jsonl").exists():
        collect(case, attempt)
    print(json.dumps({"completed_process": case, "exit_code": code, "failure": failure}, ensure_ascii=False), flush=True)
    if failure or code:
        raise SystemExit(1)


def main() -> None:
    if Path(__file__).resolve().parent != HERE.resolve():
        raise RuntimeError("transfer copy is inert; copy this runner to the authorized F evidence directory")
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "setup", "run", "collect"))
    parser.add_argument("--case", choices=tuple(DRAFTS))
    parser.add_argument("--attempt", default="01")
    parser.add_argument("--effort", choices=("max", "high", "medium", "low"), default="max")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif not args.case:
        parser.error("--case is required")
    elif args.action == "setup":
        setup(args.case, args.attempt)
    elif args.action == "run":
        run_case(args.case, args.attempt, args.effort)
    else:
        collect(args.case, args.attempt)


if __name__ == "__main__":
    main()
