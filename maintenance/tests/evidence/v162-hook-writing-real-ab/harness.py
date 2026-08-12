#!/usr/bin/env python3
"""Run the frozen v1.6.2 Claude companion Hook enabled/disabled writing A/B."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading
import time
from typing import Any, Iterable
from urllib import request as urllib_request


ROOT = Path(__file__).resolve().parents[4]
EVAL_ROOT = Path(__file__).resolve().parent
CASES_PATH = EVAL_ROOT / "cases.json"
PRODUCT_COMMIT = "0d53b3656e351020600b3754d1fe06ff2fc26ddd"
SKILL_ROOT = ROOT / "chinese-official-writing"
ASSEMBLER_PATH = ROOT / "maintenance/tools/assemble_hook_companion.py"
PLUGIN_DIR = ROOT / "output/v162-hook-writing-real-ab/frozen-claude-companion"
PLUGIN_SKILL_ROOT = PLUGIN_DIR / "skills/chinese-official-writing"
SKILL_PATH = PLUGIN_SKILL_ROOT / "SKILL.md"
GATE_PLUGIN_NAME = "chinese-official-writing-gate"
GATEWAY = "http://127.0.0.1:10100"
DUMMY_TOKEN = "local-v162-hook-writing-dummy"
TIMEOUT_SECONDS = 1200
AUTHORIZATION_ENV = "V162_HOOK_WRITING_AUTH"
AUTHORIZATION_VALUE = "APPROVED_BY_USER_20260812"
CLAUDE_MIN_VERSION = "2.1.195"
MAX_PROVIDER_LANES = 3

MODELS = {
    "opencode": "opencode-go/deepseek-v4-flash-0731",
    "ollama": "ollama-cloud/deepseek-v4-flash-0731",
    "alibaba2": "alibaba-token-plan-2/deepseek-v4-flash-0731",
}

PAIR_SPECS = [
    {"pair_id": "P001", "provider": "opencode", "case_id": "T1", "order": ["disabled", "enabled"]},
    {"pair_id": "P002", "provider": "opencode", "case_id": "T2", "order": ["enabled", "disabled"]},
    {"pair_id": "P003", "provider": "opencode", "case_id": "T3", "order": ["disabled", "enabled"]},
    {"pair_id": "P004", "provider": "ollama", "case_id": "T1", "order": ["enabled", "disabled"]},
    {"pair_id": "P005", "provider": "ollama", "case_id": "T2", "order": ["disabled", "enabled"]},
    {"pair_id": "P006", "provider": "ollama", "case_id": "T3", "order": ["enabled", "disabled"]},
    {"pair_id": "P007", "provider": "alibaba2", "case_id": "T1", "order": ["disabled", "enabled"]},
    {"pair_id": "P008", "provider": "alibaba2", "case_id": "T2", "order": ["enabled", "disabled"]},
    {"pair_id": "P009", "provider": "alibaba2", "case_id": "T3", "order": ["disabled", "enabled"]},
]

BLIND_PLAN = [
    {"group": "G01", "pair_id": "P006", "first": "B", "second": "A"},
    {"group": "G02", "pair_id": "P002", "first": "A", "second": "B"},
    {"group": "G03", "pair_id": "P009", "first": "B", "second": "A"},
    {"group": "G04", "pair_id": "P004", "first": "A", "second": "B"},
    {"group": "G05", "pair_id": "P001", "first": "B", "second": "A"},
    {"group": "G06", "pair_id": "P008", "first": "A", "second": "B"},
    {"group": "G07", "pair_id": "P003", "first": "A", "second": "B"},
    {"group": "G08", "pair_id": "P007", "first": "B", "second": "A"},
    {"group": "G09", "pair_id": "P005", "first": "A", "second": "B"},
]

SENSITIVE_ENV_KEYS = {
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_OAUTH_TOKEN",
    "CLAUDE_CODE_OAUTH_TOKEN",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "GOOGLE_APPLICATION_CREDENTIALS",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def load_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload["cases"]}


def prompt_for(case: dict[str, Any]) -> str:
    return (
        "你必须先使用 Read 工具读取唯一指定的 Skill 入口："
        + str(SKILL_PATH.resolve())
        + "。按该 SKILL.md 的实际路由，只读取完成本题必需的同目录 references；"
        "禁止读取其他 Skill、AGENTS.md、测试、证据、记忆或用户目录，不联网，不创建或修改文件，不运行命令。"
        "完成后严格按题面指定的交付范围输出，不说明读取、推理或复核过程。\n\n"
        + str(case["request"])
    )


def build_command(claude_exe: str, model: str, enabled: bool) -> list[str]:
    command = [
        claude_exe,
        "--setting-sources",
        "",
        "--no-session-persistence",
        "--tools",
        "Read",
        "--add-dir",
        str(PLUGIN_SKILL_ROOT.resolve()),
        "--include-hook-events",
        "--print",
        "--verbose",
        "--output-format",
        "stream-json",
        "--model",
        model,
        "--effort",
        "max",
    ]
    if enabled:
        command.extend(["--plugin-dir", str(PLUGIN_DIR.resolve())])
    return command


def without_plugin(command: list[str]) -> list[str]:
    result: list[str] = []
    index = 0
    while index < len(command):
        if command[index] == "--plugin-dir":
            index += 2
            continue
        result.append(command[index])
        index += 1
    return result


def build_run_environment(model: str, config_root: Path, temp_root: Path) -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if key not in SENSITIVE_ENV_KEYS}
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        environment[key] = ""
    environment.update(
        {
            "NO_PROXY": "127.0.0.1,localhost",
            "no_proxy": "127.0.0.1,localhost",
            "ANTHROPIC_BASE_URL": GATEWAY,
            "ANTHROPIC_AUTH_TOKEN": DUMMY_TOKEN,
            "ANTHROPIC_MODEL": model,
            "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
            "ANTHROPIC_DEFAULT_SONNET_MODEL": model,
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
            "ANTHROPIC_CUSTOM_MODEL_OPTION": model,
            "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": model,
            "ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES": (
                "effort,xhigh_effort,max_effort,thinking,adaptive_thinking,interleaved_thinking"
            ),
            "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1",
            "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
            "CLAUDE_CONFIG_DIR": str(config_root),
            "CLAUDE_CODE_TMPDIR": str(temp_root),
        }
    )
    return environment


def normalized_environment_contract(environment: dict[str, str]) -> dict[str, str]:
    keys = (
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy",
        "NO_PROXY", "no_proxy", "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "ANTHROPIC_CUSTOM_MODEL_OPTION", "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME",
        "ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES", "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS",
        "CLAUDE_CODE_ATTRIBUTION_HEADER", "CLAUDE_CONFIG_DIR", "CLAUDE_CODE_TMPDIR",
    )
    result = {key: environment.get(key, "<ABSENT>") for key in keys}
    result["ANTHROPIC_AUTH_TOKEN"] = "<NON_SECRET_DUMMY>"
    result["CLAUDE_CONFIG_DIR"] = "<ISOLATED_CONFIG>"
    result["CLAUDE_CODE_TMPDIR"] = "<ISOLATED_TMP>"
    return result


def auth_environment(config_root: Path) -> dict[str, str]:
    environment = dict(os.environ)
    for key in list(environment):
        if key.startswith("ANTHROPIC_") or key in SENSITIVE_ENV_KEYS:
            environment.pop(key, None)
    environment.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
    environment["CLAUDE_CONFIG_DIR"] = str(config_root)
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        environment[key] = ""
    environment["NO_PROXY"] = "127.0.0.1,localhost"
    environment["no_proxy"] = "127.0.0.1,localhost"
    return environment


def _replace_all(value: str, replacements: Iterable[tuple[str, str]]) -> str:
    result = value
    for old, new in replacements:
        if old:
            result = result.replace(old, new).replace(old.replace("\\", "/"), new)
    return result


def sanitizing_replacements(runtime_root: Path, config_root: Path, temp_root: Path) -> list[tuple[str, str]]:
    return [
        (str(config_root.resolve()), "<CLAUDE_CONFIG>"),
        (str(temp_root.resolve()), "<CLAUDE_TMP>"),
        (str(runtime_root.resolve()), "<RUNTIME>"),
        (str(ROOT.resolve()), "<WORKTREE>"),
        (str(Path.home()), "<USER_HOME>"),
    ]


def sanitize_file(source: Path, destination: Path, replacements: list[tuple[str, str]]) -> None:
    try:
        value = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return
    atomic_write_text(destination, _replace_all(value, replacements))


def parse_stream(path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    invalid_json_lines: list[int] = []
    if path.is_file():
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                invalid_json_lines.append(number)
                continue
            if isinstance(value, dict):
                records.append(value)
    inits = [item for item in records if item.get("type") == "system" and item.get("subtype") == "init"]
    hook_started = [item for item in records if item.get("subtype") == "hook_started"]
    hook_responses = [item for item in records if item.get("subtype") == "hook_response"]
    results = [item for item in records if item.get("type") == "result"]
    assistant_models: list[str] = []
    reads: list[str] = []
    for item in records:
        message = item.get("message")
        if not isinstance(message, dict):
            continue
        model = message.get("model")
        if isinstance(model, str):
            assistant_models.append(model)
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use" or block.get("name") != "Read":
                continue
            tool_input = block.get("input")
            if isinstance(tool_input, dict) and isinstance(tool_input.get("file_path"), str):
                reads.append(tool_input["file_path"])
    final = results[-1].get("result", "") if results else ""
    if not isinstance(final, str):
        final = ""
    model_usage: list[str] = []
    for item in results:
        usage = item.get("modelUsage")
        if isinstance(usage, dict):
            model_usage.extend(str(key) for key in usage)
    plugins: list[dict[str, Any]] = []
    for item in inits:
        raw_plugins = item.get("plugins")
        if isinstance(raw_plugins, list):
            plugins.extend(entry for entry in raw_plugins if isinstance(entry, dict))
    return {
        "record_count": len(records),
        "invalid_json_lines": invalid_json_lines,
        "init_models": sorted({str(item.get("model")) for item in inits if item.get("model")}),
        "assistant_models": sorted(set(assistant_models)),
        "model_usage": sorted(set(model_usage)),
        "api_key_sources": sorted({str(item.get("apiKeySource")) for item in inits if item.get("apiKeySource") is not None}),
        "hook_started": [str(item.get("hook_event") or item.get("hook_name") or "") for item in hook_started],
        "hook_responses": [
            {
                "event": str(item.get("hook_event") or item.get("hook_name") or ""),
                "exit_code": item.get("exit_code"),
                "outcome": item.get("outcome"),
                "output_sha256": sha256_text(str(item.get("output") or "")),
                "decision_block": '"decision":"block"' in str(item.get("output") or "").replace(" ", ""),
                "continue_true": '"continue":true' in str(item.get("output") or "").replace(" ", ""),
            }
            for item in hook_responses
        ],
        "plugins": plugins,
        "reads": reads,
        "result_count": len(results),
        "result_subtypes": [item.get("subtype") for item in results],
        "result_is_error": [item.get("is_error") for item in results],
        "num_turns": results[-1].get("num_turns") if results else None,
        "final": final,
        "final_sha256": sha256_text(final),
    }


def _resolved_read(path_text: str) -> Path | None:
    try:
        path = Path(path_text)
        if not path.is_absolute():
            path = ROOT / path
        return path.resolve()
    except OSError:
        return None


def read_scope_summary(reads: list[str]) -> dict[str, Any]:
    skill_root = PLUGIN_SKILL_ROOT.resolve()
    skill_path = SKILL_PATH.resolve()
    valid = [item for item in (_resolved_read(value) for value in reads) if item is not None]
    out_of_scope = []
    for item in valid:
        try:
            item.relative_to(skill_root)
        except ValueError:
            out_of_scope.append(str(item))
    return {
        "skill_entry_read": skill_path in valid,
        "read_count": len(reads),
        "out_of_scope_reads": out_of_scope,
    }


def copy_plugin_data(config_root: Path, destination: Path, replacements: list[tuple[str, str]]) -> list[dict[str, Any]]:
    data_root = config_root / "plugins/data"
    inventory: list[dict[str, Any]] = []
    if not data_root.is_dir():
        return inventory
    for source in sorted(data_root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not source.is_file():
            continue
        relative = source.relative_to(data_root)
        target = destination / relative
        sanitize_file(source, target, replacements)
        inventory.append(
            {
                "path": relative.as_posix(),
                "raw_sha256": sha256_bytes(source.read_bytes()),
                "sanitized_sha256": sha256_bytes(target.read_bytes()),
                "bytes": source.stat().st_size,
            }
        )
    return inventory


def auth_status(claude_exe: str, config_root: Path, arm_dir: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [claude_exe, "auth", "status", "--json"], cwd=ROOT, env=auth_environment(config_root),
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, check=False,
        )
        stdout, stderr, code = completed.stdout, completed.stderr, completed.returncode
    except (OSError, subprocess.SubprocessError) as exc:
        stdout, stderr, code = "", repr(exc), -1
    atomic_write_text(arm_dir / "auth-status.stdout.json", stdout)
    atomic_write_text(arm_dir / "auth-status.stderr.txt", stderr)
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        parsed = None
    return {"return_code": code, "parsed": parsed, "stderr_sha256": sha256_text(stderr)}


def plugin_state_summary(inventory: list[dict[str, Any]], copied_root: Path) -> dict[str, Any]:
    turn_files = [item for item in inventory if "claude-adapter-turns/" in item["path"]]
    state_files = [item for item in inventory if item["path"].endswith("/state.json")]
    states: list[str] = []
    selections: list[str] = []
    for item in state_files:
        try:
            payload = json.loads((copied_root / item["path"]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            if isinstance(payload.get("state"), str):
                states.append(payload["state"])
            if isinstance(payload.get("selection"), str):
                selections.append(payload["selection"])
    return {
        "adapter_turn_files": len(turn_files),
        "transaction_state_files": len(state_files),
        "states": sorted(set(states)),
        "selections": sorted(set(selections)),
    }


def run_arm(
    claude_exe: str,
    runtime_root: Path,
    evidence_root: Path,
    pair: dict[str, Any],
    slot: str,
    treatment: str,
    case: dict[str, Any],
) -> dict[str, Any]:
    enabled = treatment == "enabled"
    arm_key = f"{pair['pair_id']}-{slot}"
    arm_dir = evidence_root / "raw" / arm_key
    config_root = runtime_root / arm_key / "claude-config"
    temp_root = runtime_root / arm_key / "claude-tmp"
    raw_stream = runtime_root / arm_key / "stream.raw.jsonl"
    raw_stderr = runtime_root / arm_key / "stderr.raw.txt"
    for directory in (arm_dir, config_root, temp_root, raw_stream.parent):
        directory.mkdir(parents=True, exist_ok=True)
    prompt = prompt_for(case)
    model = MODELS[pair["provider"]]
    command = build_command(claude_exe, model, enabled)
    environment = build_run_environment(model, config_root, temp_root)
    replacements = sanitizing_replacements(runtime_root, config_root, temp_root)
    atomic_write_text(arm_dir / "prompt.sanitized.txt", _replace_all(prompt, replacements))
    started, start_monotonic = utc_now(), time.monotonic()
    timeout, exception, return_code = False, None, -1
    with raw_stream.open("w", encoding="utf-8", newline="\n") as stdout_handle, raw_stderr.open(
        "w", encoding="utf-8", newline="\n"
    ) as stderr_handle:
        try:
            completed = subprocess.run(
                command, cwd=ROOT, env=environment, input=prompt, stdout=stdout_handle, stderr=stderr_handle,
                text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_SECONDS, check=False,
            )
            return_code = completed.returncode
        except subprocess.TimeoutExpired as exc:
            timeout, exception, return_code = True, repr(exc), -9
        except OSError as exc:
            exception, return_code = repr(exc), -1
    duration, finished = round(time.monotonic() - start_monotonic, 3), utc_now()
    sanitize_file(raw_stream, arm_dir / "stream.sanitized.jsonl", replacements)
    sanitize_file(raw_stderr, arm_dir / "stderr.sanitized.txt", replacements)
    parsed = parse_stream(raw_stream)
    atomic_write_text(arm_dir / "final.txt", parsed["final"])
    auth = auth_status(claude_exe, config_root, arm_dir)
    plugin_destination = arm_dir / "plugin-data"
    inventory = copy_plugin_data(config_root, plugin_destination, replacements)
    plugin_summary = plugin_state_summary(inventory, plugin_destination)
    scope = read_scope_summary(parsed["reads"])
    requested_plugin = any(item.get("name") == GATE_PLUGIN_NAME for item in parsed["plugins"])
    expected_events = {"UserPromptSubmit", "PostToolUse", "Stop"}
    started_events = set(parsed["hook_started"])
    response_events = {str(item["event"]) for item in parsed["hook_responses"]}
    auth_parsed = auth.get("parsed")
    model_bound = (
        parsed["init_models"] == [model]
        and parsed["assistant_models"] == [model]
        and parsed["model_usage"] == [model]
    )
    common_validity = {
        "return_code_zero": return_code == 0,
        "not_timed_out": not timeout,
        "single_terminal_result": parsed["result_count"] == 1,
        "terminal_success": parsed["result_subtypes"] == ["success"] and parsed["result_is_error"] == [False],
        "final_nonempty": bool(parsed["final"].strip()),
        "model_bound": model_bound,
        "api_key_source_none": parsed["api_key_sources"] == ["none"],
        "skill_entry_read": scope["skill_entry_read"],
        "no_out_of_scope_read": not scope["out_of_scope_reads"],
        "auth_logged_in_false": isinstance(auth_parsed, dict) and auth_parsed.get("loggedIn") is False,
        "valid_json_stream": not parsed["invalid_json_lines"],
    }
    if enabled:
        treatment_validity = {
            "plugin_registered": requested_plugin,
            "hook_started_events_complete": expected_events.issubset(started_events),
            "hook_response_events_complete": expected_events.issubset(response_events),
            "adapter_turn_persisted": plugin_summary["adapter_turn_files"] >= 1,
            "gate_transaction_persisted": plugin_summary["transaction_state_files"] >= 1,
        }
    else:
        treatment_validity = {
            "plugin_not_registered": not requested_plugin,
            "no_hook_started_events": not parsed["hook_started"],
            "no_hook_response_events": not parsed["hook_responses"],
            "no_gate_plugin_data": not inventory,
        }
    technical_valid = all(common_validity.values()) and all(treatment_validity.values())
    length = len("".join(parsed["final"].split()))
    lower, upper = case["length_non_whitespace"]
    meta = {
        "schema_version": 1,
        "arm_key": arm_key,
        "pair_id": pair["pair_id"],
        "slot": slot,
        "treatment": treatment,
        "provider": pair["provider"],
        "model": model,
        "effort": "max",
        "timeout_seconds": TIMEOUT_SECONDS,
        "outer_retry_count": 0,
        "started_utc": started,
        "finished_utc": finished,
        "duration_seconds": duration,
        "return_code": return_code,
        "timeout": timeout,
        "exception": exception,
        "raw_stream_sha256": sha256_bytes(raw_stream.read_bytes()),
        "raw_stderr_sha256": sha256_bytes(raw_stderr.read_bytes()),
        "prompt_sha256": sha256_text(prompt),
        "command": [_replace_all(item, replacements) for item in command],
        "normalized_environment_contract": normalized_environment_contract(environment),
        "stream": {key: value for key, value in parsed.items() if key != "final"},
        "read_scope": scope,
        "auth_status": auth,
        "plugin_inventory": inventory,
        "plugin_state": plugin_summary,
        "common_validity": common_validity,
        "treatment_validity": treatment_validity,
        "technical_valid": technical_valid,
        "mechanical_observations": {
            "non_whitespace_length": length,
            "length_range": [lower, upper],
            "length_in_range": lower <= length <= upper,
            "missing_exact_tokens": [token for token in case["required_tokens"] if token not in parsed["final"]],
        },
    }
    atomic_write_json(arm_dir / "meta.json", meta)
    return meta


def build_mapping() -> dict[str, Any]:
    pairs = {item["pair_id"]: item for item in PAIR_SPECS}
    groups = []
    for plan in BLIND_PLAN:
        pair = pairs[plan["pair_id"]]
        slot_to_treatment = {"A": pair["order"][0], "B": pair["order"][1]}
        groups.append(
            {
                "group": plan["group"],
                "pair_id": pair["pair_id"],
                "provider": pair["provider"],
                "model": MODELS[pair["provider"]],
                "case_id": pair["case_id"],
                "稿件甲_source_slot": plan["first"],
                "稿件甲_treatment": slot_to_treatment[plan["first"]],
                "稿件乙_source_slot": plan["second"],
                "稿件乙_treatment": slot_to_treatment[plan["second"]],
            }
        )
    return {"schema_version": 1, "product_commit": PRODUCT_COMMIT, "groups": groups}


def build_blind_packet(evidence_root: Path, manifest: dict[str, Any]) -> str:
    cases = load_cases()
    pairs = {item["pair_id"]: item for item in PAIR_SPECS}
    meta_by_arm = {item["arm_key"]: item for item in manifest["arms"]}
    lines = [
        "# v1.6.2 Hook writing A/B blind packet",
        "",
        "只评价下列匿名稿件。不得推测系统、provider、运行顺序或处理身份。",
        "",
        "## 判分口径",
        "",
        "逐稿给 PASS、WARN 或 FAIL；逐组给甲胜、乙胜或难分。分别检查事实与数字、未决状态强度、篇幅、输出范围、要素完整、文体、紧凑自然和直接可用性。一般性的衔接或按既有事项继续办理，不因措辞本身判外扩；只有新增具体主体、数字、期限、程序、结果、职责或与材料状态冲突时才判事实/状态硬失败。硬边界优先于文风偏好，不得因某稿更长或更短直接判胜。",
        "",
    ]
    for plan in BLIND_PLAN:
        pair = pairs[plan["pair_id"]]
        first_key, second_key = f"{pair['pair_id']}-{plan['first']}", f"{pair['pair_id']}-{plan['second']}"
        if not (meta_by_arm[first_key]["technical_valid"] and meta_by_arm[second_key]["technical_valid"]):
            continue
        case = cases[pair["case_id"]]
        first = (evidence_root / "raw" / first_key / "final.txt").read_text(encoding="utf-8")
        second = (evidence_root / "raw" / second_key / "final.txt").read_text(encoding="utf-8")
        lines.extend(
            [
                f"## {plan['group']} | {case['id']} {case['title']}", "", "### 任务", "",
                str(case["judge_request"]), "", "### 稿件甲", "", first.rstrip(), "", "### 稿件乙", "", second.rstrip(), "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def verdict_template(valid_groups: list[str]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "groups": [
            {
                "group": group,
                "甲_grade": "PASS|WARN|FAIL",
                "乙_grade": "PASS|WARN|FAIL",
                "winner": "甲|乙|难分",
                "甲_hard_boundaries": {"facts": "PASS|FAIL", "state": "PASS|FAIL", "length": "PASS|FAIL", "output_scope": "PASS|FAIL"},
                "乙_hard_boundaries": {"facts": "PASS|FAIL", "state": "PASS|FAIL", "length": "PASS|FAIL", "output_scope": "PASS|FAIL"},
                "reason": "",
            }
            for group in valid_groups
        ],
        "overall_observations": [],
    }


def count_tokens_probe(model: str) -> dict[str, Any]:
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": "probe"}]}).encode("utf-8")
    request = urllib_request.Request(
        GATEWAY + "/v1/messages/count_tokens",
        data=payload,
        headers={"content-type": "application/json", "x-api-key": DUMMY_TOKEN, "anthropic-version": "2023-06-01"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            return {"status": response.status, "body": parsed, "ok": response.status == 200 and isinstance(parsed.get("input_tokens"), int)}
    except Exception as exc:
        return {"status": None, "body": repr(exc), "ok": False}


def preflight(claude_exe: str) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "root": str(ROOT),
        "product_commit": PRODUCT_COMMIT,
        "skill_exists": SKILL_PATH.is_file(),
        "plugin_exists": PLUGIN_DIR.is_dir(),
        "cases": sorted(load_cases()),
        "model_probes": {model: count_tokens_probe(model) for model in MODELS.values()},
    }
    try:
        version = subprocess.run([claude_exe, "--version"], capture_output=True, text=True, encoding="utf-8", timeout=10, check=False)
        checks["claude_version_stdout"] = version.stdout.strip()
        checks["claude_version_ok"] = version.returncode == 0 and CLAUDE_MIN_VERSION in version.stdout
    except (OSError, subprocess.SubprocessError) as exc:
        checks["claude_version_stdout"], checks["claude_version_ok"] = repr(exc), False
    try:
        with socket.create_connection(("127.0.0.1", 10100), timeout=3):
            checks["gateway_listening"] = True
    except OSError:
        checks["gateway_listening"] = False
    diff = subprocess.run(
        ["git", "diff", "--quiet", PRODUCT_COMMIT, "--", "chinese-official-writing"], cwd=ROOT, timeout=15, check=False
    )
    checks["product_unchanged_from_fixed_root"] = diff.returncode == 0
    command_checks = []
    for model in MODELS.values():
        disabled, enabled = build_command(claude_exe, model, False), build_command(claude_exe, model, True)
        command_checks.append(without_plugin(enabled) == disabled and enabled[-2:] == ["--plugin-dir", str(PLUGIN_DIR.resolve())])
    checks["only_plugin_command_difference"] = all(command_checks)
    checks["matrix_pairs"], checks["matrix_calls"], checks["blind_groups"] = len(PAIR_SPECS), len(PAIR_SPECS) * 2, len(BLIND_PLAN)
    checks["errors"] = [
        name for name in ("skill_exists", "plugin_exists", "claude_version_ok", "gateway_listening", "product_unchanged_from_fixed_root", "only_plugin_command_difference")
        if not checks.get(name)
    ]
    if not all(item["ok"] for item in checks["model_probes"].values()):
        checks["errors"].append("model_probes")
    return checks


def execute(claude_exe: str, evidence_root: Path) -> int:
    if os.environ.get(AUTHORIZATION_ENV) != AUTHORIZATION_VALUE:
        raise SystemExit(f"missing {AUTHORIZATION_ENV}={AUTHORIZATION_VALUE}")
    if evidence_root.exists():
        raise SystemExit(f"evidence output already exists: {evidence_root}")
    runtime_root = ROOT / "output/v162-hook-writing-real-ab/runtime" / evidence_root.name
    if runtime_root.exists():
        raise SystemExit(f"runtime output already exists: {runtime_root}")
    checks = preflight(claude_exe)
    if checks["errors"]:
        raise SystemExit("preflight failed: " + ", ".join(checks["errors"]))
    evidence_root.mkdir(parents=True)
    runtime_root.mkdir(parents=True)
    atomic_write_json(evidence_root / "preflight.json", checks)
    atomic_write_json(evidence_root / "mapping.json", build_mapping())
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "product_commit": PRODUCT_COMMIT,
        "started_utc": utc_now(),
        "finished_utc": None,
        "planned_pairs": len(PAIR_SPECS),
        "planned_calls": len(PAIR_SPECS) * 2,
        "completed_calls": 0,
        "timeout_seconds_per_arm": TIMEOUT_SECONDS,
        "outer_retry_count": 0,
        "arms": [],
        "pairs": [],
    }
    atomic_write_json(evidence_root / "manifest.json", manifest)
    cases = load_cases()
    manifest_lock = threading.Lock()

    def run_provider_lane(provider: str) -> None:
        lane_pairs = [item for item in PAIR_SPECS if item["provider"] == provider]
        for pair in lane_pairs:
            pair_arms = []
            for slot, treatment in zip(("A", "B"), pair["order"]):
                meta = run_arm(
                    claude_exe,
                    runtime_root,
                    evidence_root,
                    pair,
                    slot,
                    treatment,
                    cases[pair["case_id"]],
                )
                pair_arms.append(meta)
                with manifest_lock:
                    manifest["arms"].append(meta)
                    manifest["completed_calls"] = len(manifest["arms"])
                    atomic_write_json(evidence_root / "manifest.json", manifest)
                    print(
                        json.dumps(
                            {
                                "completed": manifest["completed_calls"],
                                "planned": manifest["planned_calls"],
                                "arm_key": meta["arm_key"],
                                "technical_valid": meta["technical_valid"],
                                "timeout": meta["timeout"],
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
            pair_meta = {
                "pair_id": pair["pair_id"],
                "provider": pair["provider"],
                "case_id": pair["case_id"],
                "technical_valid": all(item["technical_valid"] for item in pair_arms),
                "prompt_sha_equal": pair_arms[0]["prompt_sha256"] == pair_arms[1]["prompt_sha256"],
                "normalized_environment_equal": pair_arms[0]["normalized_environment_contract"] == pair_arms[1]["normalized_environment_contract"],
                "command_only_plugin_difference": without_plugin(pair_arms[1]["command"]) == without_plugin(pair_arms[0]["command"]),
            }
            with manifest_lock:
                manifest["pairs"].append(pair_meta)
                atomic_write_json(evidence_root / "manifest.json", manifest)

    with ThreadPoolExecutor(max_workers=MAX_PROVIDER_LANES) as executor:
        futures = [executor.submit(run_provider_lane, provider) for provider in MODELS]
        for future in as_completed(futures):
            future.result()
    manifest["arms"].sort(key=lambda item: (item["pair_id"], item["slot"]))
    manifest["pairs"].sort(key=lambda item: item["pair_id"])
    manifest["finished_utc"] = utc_now()
    manifest["valid_pairs"] = sum(1 for item in manifest["pairs"] if item["technical_valid"])
    manifest["valid_pairs_by_provider"] = {
        provider: sum(1 for item in manifest["pairs"] if item["provider"] == provider and item["technical_valid"])
        for provider in MODELS
    }
    manifest["valid_pairs_by_case"] = {
        case_id: sum(1 for item in manifest["pairs"] if item["case_id"] == case_id and item["technical_valid"])
        for case_id in cases
    }
    manifest["minimum_coverage_met"] = (
        manifest["valid_pairs"] >= 6
        and all(value >= 2 for value in manifest["valid_pairs_by_provider"].values())
        and all(value >= 2 for value in manifest["valid_pairs_by_case"].values())
    )
    atomic_write_json(evidence_root / "manifest.json", manifest)
    packet = build_blind_packet(evidence_root, manifest)
    atomic_write_text(evidence_root / "blind-packet.md", packet)
    valid_pair_ids = {item["pair_id"] for item in manifest["pairs"] if item["technical_valid"]}
    valid_groups = [item["group"] for item in BLIND_PLAN if item["pair_id"] in valid_pair_ids]
    atomic_write_json(evidence_root / "blind-verdict-template.json", verdict_template(valid_groups))
    hashes = {
        name: sha256_bytes((evidence_root / name).read_bytes())
        for name in ("manifest.json", "mapping.json", "blind-packet.md", "blind-verdict-template.json", "preflight.json")
    }
    atomic_write_json(evidence_root / "hashes.json", hashes)
    print(json.dumps({"complete": True, "valid_pairs": manifest["valid_pairs"], "hashes": hashes}, ensure_ascii=False), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-bin", default=shutil.which("claude") or "claude")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.execute:
        if args.out is None:
            parser.error("--execute requires --out")
        return execute(args.claude_bin, args.out.resolve())
    checks = preflight(args.claude_bin)
    print(json.dumps(checks, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not checks["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
