#!/usr/bin/env python3
"""Run isolated Codex Stop lifecycles for the implicit under-length candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CONFIG_PATH = HERE / "cases.json"
ASSEMBLER = ROOT / "maintenance/tools/assemble_hook_companion.py"
CATALOG = Path.home() / ".codex/opencodex-catalog.json"
OUTPUT_ROOT = ROOT / "output/ul006-implicit-underlength-r2-live-r2"
MARKETPLACE_NAME = "ul006-r2-local"
PLUGIN_NAME = "chinese-official-writing"
TIMEOUT_SECONDS = 1200


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", check=True,
    ).stdout.strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def body_text(value: str) -> str:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    body: list[str] = []
    for index, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+", line):
            continue
        if re.match(r"^(?:[一二三四五六七八九十]+、|\d+[.、])\s*[^。！？!?；;]{1,40}$", line):
            continue
        if index == 0 and len(line) <= 30 and not re.search(r"[。！？!?]", line):
            continue
        body.append(line)
    return "\n".join(body)


def tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    count = 0
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        count += 1
    return f"{count}:{digest.hexdigest()}"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )


def prepare() -> dict[str, Any]:
    config = load_config()
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean")
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    candidate = git_text("rev-parse", f"{config['candidate_commit']}^{{commit}}")
    if candidate != config["candidate_commit"]:
        raise RuntimeError("candidate commit mismatch")
    candidate_tree = git_text("rev-parse", f"{candidate}:chinese-official-writing")
    current_tree = git_text("rev-parse", "HEAD:chinese-official-writing")
    if candidate_tree != current_tree:
        raise RuntimeError("current product tree differs from candidate")

    marketplace = OUTPUT_ROOT / "marketplace"
    plugin = marketplace / "plugins" / PLUGIN_NAME
    completed = subprocess.run(
        [sys.executable, "-B", str(ASSEMBLER), "--host", "codex",
         "--capability", "under_length", "--output", str(plugin)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    assembly = json.loads(completed.stdout)
    write_json(
        marketplace / ".agents/plugins/marketplace.json",
        {
            "name": MARKETPLACE_NAME,
            "interface": {"displayName": "UL006 R2 Local"},
            "plugins": [{
                "name": PLUGIN_NAME,
                "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }],
        },
    )
    for provider_id in config["providers"]:
        (OUTPUT_ROOT / "runtime" / provider_id).mkdir(parents=True)
    fixture = {
        "schema_version": 1,
        "candidate_commit": candidate,
        "product_tree": candidate_tree,
        "codex_version": subprocess.run(
            [shutil.which("codex") or "codex", "--version"], capture_output=True,
            text=True, encoding="utf-8", check=True,
        ).stdout.strip(),
        "assembly": assembly,
        "companion_fingerprint": tree_fingerprint(plugin),
        "providers": config["providers"],
    }
    write_json(OUTPUT_ROOT / "fixture.json", fixture)
    return fixture


def isolated_environment(codex_home: Path) -> dict[str, str]:
    environment = dict(os.environ)
    environment["CODEX_HOME"] = str(codex_home)
    return environment


def install_plugin(codex_home: Path) -> dict[str, Any]:
    codex_home.mkdir(parents=True)
    environment = isolated_environment(codex_home)
    codex = shutil.which("codex") or "codex"
    marketplace = str((OUTPUT_ROOT / "marketplace").resolve())
    added = subprocess.run(
        [codex, "plugin", "marketplace", "add", marketplace, "--json"],
        env=environment, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    installed = subprocess.run(
        [codex, "plugin", "add", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}", "--json"],
        env=environment, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return {"marketplace": json.loads(added.stdout), "plugin": json.loads(installed.stdout)}


def prompt_for(case: dict[str, Any], skill_path: Path) -> str:
    return (
        "请先使用终端只读命令完整读取唯一指定的 Skill 入口："
        + str(skill_path.resolve())
        + "。然后按该入口实际路由，只读取完成本题必需的同目录 references。"
        "不要读取其他 Skill、AGENTS、测试或证据，不联网，不修改文件。"
        "最终严格按题面交付，不说明读取、推理、修订或复核过程。\n\n"
        + str(case["request"])
    )


def parse_agent_messages(trace: str) -> list[str]:
    messages: list[str] = []
    for line in trace.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = item.get("item") if isinstance(item, dict) else None
        if (
            item.get("type") == "item.completed"
            and isinstance(payload, dict)
            and payload.get("type") == "agent_message"
            and isinstance(payload.get("text"), str)
        ):
            messages.append(payload["text"])
    return messages


def trace_usage(trace: str) -> dict[str, Any]:
    for line in reversed(trace.splitlines()):
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "turn.completed" and isinstance(item.get("usage"), dict):
            return item["usage"]
    return {}


def hook_records(codex_home: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in codex_home.rglob("*.json"):
        if "cache" in path.parts:
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if not isinstance(value, dict):
            continue
        if "under_length" not in value and "under_length_bypass" not in value:
            continue
        records.append({"path": str(path.relative_to(codex_home)), "record": value})
    return records


def message_by_hash(messages: list[str], digest: Any) -> str | None:
    if not isinstance(digest, str):
        return None
    return next((message for message in messages if sha256_text(message) == digest), None)


def observations(case: dict[str, Any], final: str) -> dict[str, Any]:
    compact_final = compact(final)
    return {
        "missing_required": [token for token in case["required"] if compact(token) not in compact_final],
        "present_forbidden": [token for token in case["forbidden"] if compact(token) in compact_final],
        "body_chars": len(compact(body_text(final))),
        "material_chars": len(compact(case["material"])),
        "longer_than_material": len(compact(body_text(final))) > len(compact(case["material"])),
        "non_body_wrapper": bool(re.search(r"(?:字数|修改说明|核验结果|以下为|下面是)", final)),
    }


def run_one(provider_id: str, model: str, case: dict[str, Any], effort: str) -> dict[str, Any]:
    case_root = OUTPUT_ROOT / "runtime" / provider_id / case["id"]
    codex_home = case_root / "codex-home"
    workspace = case_root / "workspace"
    workspace.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(workspace)], check=True)
    install = install_plugin(codex_home)
    installed_path = Path(install["plugin"]["installedPath"])
    skill_path = installed_path / "skills/chinese-official-writing/SKILL.md"
    prompt = prompt_for(case, skill_path)
    raw_root = OUTPUT_ROOT / "raw" / provider_id / case["id"]
    raw_root.mkdir(parents=True)
    final_path = raw_root / "final.txt"
    codex = shutil.which("codex") or "codex"
    command = [
        codex, "-a", "never", "--dangerously-bypass-hook-trust",
        "--enable", "hooks", "exec", "--ignore-rules", "--skip-git-repo-check",
        "-C", str(workspace), "-m", model,
        "-c", 'openai_base_url="http://127.0.0.1:10100/v1"',
        "-c", f'model_catalog_json="{CATALOG.as_posix()}"',
        "-c", f'model_reasoning_effort="{effort}"',
        "-s", "read-only", "--ephemeral", "--json",
        "--output-last-message", str(final_path), "-",
    ]
    started = time.monotonic()
    timeout = False
    try:
        completed = subprocess.run(
            command, env=isolated_environment(codex_home), input=prompt,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT_SECONDS, check=False,
        )
        return_code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        timeout = True
        return_code = None
        stdout = str(exc.stdout or "")
        stderr = str(exc.stderr or "")
    (raw_root / "trace.jsonl").write_text(stdout, encoding="utf-8", newline="\n")
    (raw_root / "stderr.txt").write_text(stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
    messages = parse_agent_messages(stdout)
    records = hook_records(codex_home)
    write_json(raw_root / "hook-records.json", records)
    record = records[-1]["record"] if records else {}
    state = record.get("under_length") if isinstance(record.get("under_length"), dict) else {}
    audit = state.get("audit") if isinstance(state.get("audit"), dict) else {}
    original = message_by_hash(messages, audit.get("original_sha256"))
    candidate = message_by_hash(messages, audit.get("candidate_sha256"))
    final_hash = sha256_text(final) if final else None
    expected = case["kind"]
    if expected == "target":
        lifecycle_ok = bool(
            state.get("phase") == "under_length_complete"
            and audit.get("trigger") == "implicit_under"
            and audit.get("delivery_verified") is True
            and audit.get("delivery_sha256") == final_hash
        )
    else:
        lifecycle_ok = bool(
            not state
            and record.get("under_length_bypass") == case["expected_bypass"]
        )
    technical_failures = []
    if return_code != 0:
        technical_failures.append("nonzero_exit")
    if timeout:
        technical_failures.append("timeout")
    if not final.strip():
        technical_failures.append("missing_final")
    if not records:
        technical_failures.append("missing_hook_record")
    if not lifecycle_ok:
        technical_failures.append("lifecycle_contract_not_met")
    result = {
        "provider_id": provider_id,
        "model": model,
        "effort": effort,
        "case_id": case["id"],
        "kind": expected,
        "return_code": return_code,
        "timeout": timeout,
        "seconds": round(time.monotonic() - started, 3),
        "technical_failures": technical_failures,
        "agent_message_count": len(messages),
        "message_hashes": [sha256_text(message) for message in messages],
        "original_found": original is not None,
        "candidate_found": candidate is not None,
        "original_chars": len(compact(body_text(original or ""))),
        "candidate_chars": len(compact(body_text(candidate or ""))),
        "final_sha256": final_hash,
        "under_length_phase": state.get("phase"),
        "under_length_bypass": record.get("under_length_bypass"),
        "selection": audit.get("selection"),
        "selection_reason": audit.get("reason"),
        "delivery_verified": audit.get("delivery_verified"),
        "spec": state.get("spec"),
        "observations": observations(case, final),
        "usage": trace_usage(stdout),
        "files": {
            "final": str(final_path.relative_to(OUTPUT_ROOT)),
            "trace": str((raw_root / "trace.jsonl").relative_to(OUTPUT_ROOT)),
            "stderr": str((raw_root / "stderr.txt").relative_to(OUTPUT_ROOT)),
            "hook_records": str((raw_root / "hook-records.json").relative_to(OUTPUT_ROOT)),
        },
    }
    write_json(raw_root / "result.json", result)
    return result


def run_provider(provider_id: str) -> dict[str, Any]:
    config = load_config()
    if provider_id not in config["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"result exists: {result_path}")
    records: list[dict[str, Any]] = []
    for case in config["cases"]:
        print(f"START {provider_id} {case['id']}", flush=True)
        records.append(run_one(
            provider_id, config["providers"][provider_id], case,
            config["reasoning_effort"],
        ))
        write_json(result_path, {"provider_id": provider_id, "records": records})
    return {"provider_id": provider_id, "record_count": len(records)}


def summarize() -> dict[str, Any]:
    config = load_config()
    records: list[dict[str, Any]] = []
    missing: list[str] = []
    for provider_id in config["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if path.is_file():
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(provider_id)
    targets = [item for item in records if item["kind"] == "target"]
    summary = {
        "schema_version": 1,
        "missing_providers": missing,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "target_count": len(targets),
        "target_d1_selected_count": sum(item["selection"] == "D1" for item in targets),
        "target_d0_selected_count": sum(item["selection"] == "D0" for item in targets),
        "target_longer_than_material_count": sum(item["observations"]["longer_than_material"] for item in targets),
        "records": records,
    }
    write_json(OUTPUT_ROOT / "summary.json", summary)
    return summary


def main() -> int:
    config = load_config()
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(config["providers"]))
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        result = prepare()
    elif args.provider:
        result = run_provider(args.provider)
    else:
        result = summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
