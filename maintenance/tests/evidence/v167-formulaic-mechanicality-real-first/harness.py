#!/usr/bin/env python3
"""Run the frozen v1.6.6 vs structure-first formulaic-language real-writing A/B."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import threading
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_ROOT = Path(__file__).resolve().parent
CASES_PATH = EVIDENCE_ROOT / "cases.json"
PROTOTYPE_PATH = EVIDENCE_ROOT / "prototype-formulaic-language.md"
BASELINE_COMMIT = "b49da7f2a5a8ac2327252d29efd66f1d54ccbc35"
BASELINE_PRODUCT_TREE = "7d9e56cfe4f33ad79de3c97e95be60a6db53ae9a"
BASELINE_FORMULAIC_SHA256 = "a4940b83c337ec5e0a7f0389de49113df8ccf3ae012b5c3fc498f0982b73bb16"
PROTOTYPE_SHA256 = "7ed20aa24167e07e32a666efc0a4bf0d3074a73aed4a0035ce4c50c473087563"
CASES_SHA256 = "0bab8696cd2bc82cb6a8e40244cb41fcef717385bf684f7b5df541e3b5780ba9"
GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 10100
GATEWAY = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}"
DUMMY_TOKEN = "local-v167-formulaic-dummy"
TIMEOUT_SECONDS = 1200
AUTH_ENV = "V167_FORMULAIC_REAL_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260816"
MAX_PROVIDER_LANES = 3

SENSITIVE_ENV_KEYS = {
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_OAUTH_TOKEN",
    "CLAUDE_CODE_OAUTH_TOKEN",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "GOOGLE_APPLICATION_CREDENTIALS",
}

PHRASE_PATTERNS = {
    "formulaic_open": re.compile(r"现(?:将|就).{0,24}(?:如下|报告如下|通知如下|答复如下|反映如下|综合如下)"),
    "generic_transition": re.compile(r"(?:^|[。；\n])\s*(?:为此|据此|有鉴于此|综上所述|总之)[，,:：]"),
    "formulaic_close": re.compile(r"(?:特此(?:通知|通告|公告|报告|批复|函复|函达)|此复|妥否，请批示|当否，请批示|请予批复)[。！]?$"),
}
HEADING_RE = re.compile(r"^\s*(?:[一二三四五六七八九十]+、|（[一二三四五六七八九十]+）|[0-9]+[.、])\s*(.+?)\s*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_normalized_text(path: Path) -> str:
    return sha256_text(path.read_text(encoding="utf-8").replace("\r\n", "\n"))


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="strict", timeout=60, check=True,
    )
    return completed.stdout.strip()


def load_payload() -> dict[str, Any]:
    if sha256_normalized_text(CASES_PATH) != CASES_SHA256:
        raise RuntimeError("cases hash mismatch")
    if sha256_normalized_text(PROTOTYPE_PATH) != PROTOTYPE_SHA256:
        raise RuntimeError("prototype hash mismatch")
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 24:
        raise RuntimeError("expected 24 cases")
    ids = [str(item.get("id")) for item in cases]
    if len(set(ids)) != len(ids):
        raise RuntimeError("duplicate case id")
    for provider in payload["models"]:
        if sum(item.get("provider") == provider for item in cases) != 8:
            raise RuntimeError(f"provider balance mismatch: {provider}")
    return payload


def baseline_paths() -> list[str]:
    tree = run_git("rev-parse", f"{BASELINE_COMMIT}:chinese-official-writing")
    if tree != BASELINE_PRODUCT_TREE:
        raise RuntimeError(f"baseline product tree mismatch: {tree}")
    paths = run_git("ls-tree", "-r", "--name-only", BASELINE_COMMIT, "--", "chinese-official-writing")
    return [line for line in paths.splitlines() if line]


def export_baseline(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for repo_path in baseline_paths():
        relative = Path(repo_path).relative_to("chinese-official-writing")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            ["git", "show", f"{BASELINE_COMMIT}:{repo_path}"], cwd=ROOT,
            capture_output=True, timeout=60, check=True,
        )
        target.write_bytes(completed.stdout)
    current_hash = sha256_bytes((destination / "references/formulaic-language.md").read_bytes())
    if current_hash != BASELINE_FORMULAIC_SHA256:
        raise RuntimeError("exported baseline formulaic hash mismatch")


def tree_manifest(root: Path) -> list[dict[str, Any]]:
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_bytes(path.read_bytes()), "bytes": path.stat().st_size}
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()) if path.is_file()
    ]


def prepare_skill_roots(runtime: Path) -> dict[str, Any]:
    roots = runtime / "skills"
    baseline = roots / "baseline/chinese-official-writing"
    candidate = roots / "candidate/chinese-official-writing"
    if roots.exists():
        shutil.rmtree(roots)
    export_baseline(baseline)
    shutil.copytree(baseline, candidate)
    (candidate / "references/formulaic-language.md").write_text(
        PROTOTYPE_PATH.read_text(encoding="utf-8").replace("\r\n", "\n"),
        encoding="utf-8", newline="\n",
    )
    base_manifest = tree_manifest(baseline)
    candidate_manifest = tree_manifest(candidate)
    differing = [
        left["path"] for left, right in zip(base_manifest, candidate_manifest)
        if left["sha256"] != right["sha256"]
    ]
    if len(base_manifest) != len(candidate_manifest) or differing != ["references/formulaic-language.md"]:
        raise RuntimeError(f"unexpected prototype diff: {differing}")
    receipt = {
        "baseline_commit": BASELINE_COMMIT,
        "baseline_product_tree": BASELINE_PRODUCT_TREE,
        "baseline_root": str(baseline.resolve()),
        "candidate_root": str(candidate.resolve()),
        "file_count": len(base_manifest),
        "differing_paths": differing,
        "baseline_manifest_sha256": sha256_text(json.dumps(base_manifest, sort_keys=True)),
        "candidate_manifest_sha256": sha256_text(json.dumps(candidate_manifest, sort_keys=True)),
    }
    atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


def build_environment(model: str, arm_runtime: Path) -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if key not in SENSITIVE_ENV_KEYS}
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        environment[key] = ""
    home = arm_runtime / "home"
    config = arm_runtime / "claude-config"
    temp = arm_runtime / "tmp"
    work = arm_runtime / "work"
    for path in (home, config, temp, work):
        path.mkdir(parents=True, exist_ok=True)
    environment.update({
        "HOME": str(home), "USERPROFILE": str(home),
        "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost",
        "ANTHROPIC_BASE_URL": GATEWAY, "ANTHROPIC_AUTH_TOKEN": DUMMY_TOKEN,
        "ANTHROPIC_MODEL": model,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": model,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
        "ANTHROPIC_CUSTOM_MODEL_OPTION": model,
        "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": model,
        "ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES": "effort,xhigh_effort,max_effort,thinking,adaptive_thinking,interleaved_thinking",
        "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1",
        "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
        "CLAUDE_CONFIG_DIR": str(config),
        "CLAUDE_CODE_TMPDIR": str(temp),
    })
    return environment


def parse_stream(path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    invalid: list[int] = []
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            invalid.append(number)
            continue
        if isinstance(item, dict):
            records.append(item)
    inits = [item for item in records if item.get("type") == "system" and item.get("subtype") == "init"]
    results = [item for item in records if item.get("type") == "result"]
    models: list[str] = []
    reads: list[str] = []
    for item in records:
        message = item.get("message")
        if not isinstance(message, dict):
            continue
        if isinstance(message.get("model"), str):
            models.append(message["model"])
        for block in message.get("content", []):
            if not isinstance(block, dict) or block.get("type") != "tool_use" or block.get("name") != "Read":
                continue
            tool_input = block.get("input")
            if isinstance(tool_input, dict) and isinstance(tool_input.get("file_path"), str):
                reads.append(tool_input["file_path"])
    final = results[0].get("result", "") if len(results) == 1 else ""
    if not isinstance(final, str):
        final = ""
    usage_models: list[str] = []
    for item in results:
        usage = item.get("modelUsage")
        if isinstance(usage, dict):
            usage_models.extend(str(key) for key in usage)
    return {
        "record_count": len(records), "invalid_json_lines": invalid,
        "init_models": sorted({str(item.get("model")) for item in inits if item.get("model")}),
        "assistant_models": sorted(set(models)), "usage_models": sorted(set(usage_models)),
        "api_key_sources": sorted({str(item.get("apiKeySource")) for item in inits if item.get("apiKeySource") is not None}),
        "plugins": [entry for item in inits for entry in item.get("plugins", []) if isinstance(entry, dict)],
        "reads": reads, "result_count": len(results),
        "result_subtypes": [item.get("subtype") for item in results],
        "result_errors": [item.get("is_error") for item in results],
        "final": final, "final_sha256": sha256_text(final),
    }


def resolve_read(value: str, work: Path) -> Path | None:
    try:
        path = Path(value)
        return (path if path.is_absolute() else work / path).resolve()
    except OSError:
        return None


def read_scope(reads: list[str], skill_root: Path, work: Path) -> dict[str, Any]:
    root = skill_root.resolve()
    entry = (skill_root / "SKILL.md").resolve()
    resolved = [item for item in (resolve_read(value, work) for value in reads) if item is not None]
    outside: list[str] = []
    for item in resolved:
        try:
            item.relative_to(root)
        except ValueError:
            outside.append(str(item))
    return {"entry_read": entry in resolved, "read_count": len(reads), "outside": outside}


def formulaic_metrics(text: str) -> dict[str, Any]:
    phrase_hits = {name: len(pattern.findall(text)) for name, pattern in PHRASE_PATTERNS.items()}
    headings = [match.group(1).strip() for line in text.splitlines() if (match := HEADING_RE.match(line))]
    active_groups = sum(count > 0 for count in phrase_hits.values())
    return {
        "non_whitespace_chars": len(re.sub(r"\s+", "", text)),
        "phrase_hits": phrase_hits,
        "formulaic_cluster_flag": active_groups >= 2,
        "headings": headings,
        "heading_signature": " | ".join(headings),
    }


def system_prompt(skill_root: Path) -> str:
    return (
        "你是独立的中文正式材料写稿 Agent。必须先使用 Read 工具读取唯一指定入口："
        f"{(skill_root / 'SKILL.md').resolve()}。按该入口的实际路由，只读取该 Skill 根内完成本题必需的 references。"
        "禁止读取其他 Skill、AGENTS.md、maintenance、tests、evidence、记忆或用户目录；不得联网、创建或修改文件、运行命令。"
        "严格按用户题面输出可直接使用的完整正文，不说明读取、推理、复核或测试过程。"
    )


def command(claude: str, model: str, skill_root: Path, prompt: str) -> list[str]:
    return [
        claude, "--setting-sources", "", "--no-session-persistence", "--tools", "Read",
        "--add-dir", str(skill_root.resolve()), "--append-system-prompt", prompt,
        "--print", "--verbose", "--output-format", "stream-json",
        "--model", model, "--effort", "max",
    ]


def run_arm(
    claude: str, output: Path, runtime: Path, skill_roots: dict[str, Path], models: dict[str, str],
    case: dict[str, Any], treatment: str,
) -> dict[str, Any]:
    arm_id = f"{case['id']}-{treatment}"
    arm_output = output / "raw" / arm_id
    arm_runtime = runtime / "arms" / arm_id
    arm_output.mkdir(parents=True, exist_ok=False)
    arm_runtime.mkdir(parents=True, exist_ok=False)
    skill_root = skill_roots[treatment]
    model = models[case["provider"]]
    prompt = system_prompt(skill_root)
    user_request = str(case["request"])
    env = build_environment(model, arm_runtime)
    work = arm_runtime / "work"
    raw_stream = arm_runtime / "stream.jsonl"
    raw_stderr = arm_runtime / "stderr.txt"
    run_command = command(claude, model, skill_root, prompt)
    started = utc_now()
    before = time.monotonic()
    return_code = -1
    timed_out = False
    exception = None
    with raw_stream.open("w", encoding="utf-8", newline="\n") as stdout_handle, raw_stderr.open("w", encoding="utf-8", newline="\n") as stderr_handle:
        try:
            completed = subprocess.run(
                run_command, cwd=work, env=env, input=user_request,
                stdout=stdout_handle, stderr=stderr_handle, text=True,
                encoding="utf-8", errors="replace", timeout=TIMEOUT_SECONDS, check=False,
            )
            return_code = completed.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            exception = repr(exc)
            return_code = -9
        except OSError as exc:
            exception = repr(exc)
    parsed = parse_stream(raw_stream)
    scope = read_scope(parsed["reads"], skill_root, work)
    model_bound = (
        parsed["init_models"] == [model]
        and parsed["assistant_models"] == [model]
        and parsed["usage_models"] == [model]
    )
    checks = {
        "return_code_zero": return_code == 0,
        "not_timed_out": not timed_out,
        "single_result": parsed["result_count"] == 1,
        "terminal_success": parsed["result_subtypes"] == ["success"] and parsed["result_errors"] == [False],
        "final_nonempty": bool(parsed["final"].strip()),
        "model_bound": model_bound,
        "api_key_source_none": parsed["api_key_sources"] == ["none"],
        "entry_read": scope["entry_read"],
        "read_scope": not scope["outside"],
        "no_plugins": not parsed["plugins"],
        "valid_stream": not parsed["invalid_json_lines"],
    }
    final = parsed.pop("final")
    atomic_text(arm_output / "final.txt", final)
    shutil.copyfile(raw_stderr, arm_output / "stderr.txt")
    metadata = {
        "schema_version": 1, "arm_id": arm_id, "case_id": case["id"], "genre": case["genre"],
        "provider": case["provider"], "model": model, "treatment": treatment,
        "effort": "max", "timeout_seconds": TIMEOUT_SECONDS, "retry_count": 0,
        "started_utc": started, "finished_utc": utc_now(),
        "duration_seconds": round(time.monotonic() - before, 3),
        "return_code": return_code, "timed_out": timed_out, "exception": exception,
        "system_prompt_sha256": sha256_text(prompt), "user_request_sha256": sha256_text(user_request),
        "raw_stream_sha256": sha256_bytes(raw_stream.read_bytes()),
        "stderr_sha256": sha256_bytes(raw_stderr.read_bytes()),
        "stream": parsed, "read_scope": scope, "checks": checks,
        "technical_valid": all(checks.values()), "final_sha256": sha256_text(final),
        "metrics": formulaic_metrics(final),
    }
    atomic_json(arm_output / "meta.json", metadata)
    return metadata


def blind_order(case_id: str) -> tuple[str, str]:
    return ("candidate", "baseline") if int(case_id[1:]) % 2 else ("baseline", "candidate")


def build_packets(output: Path, cases: list[dict[str, Any]], arms: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm = {item["arm_id"]: item for item in arms}
    packet = [
        "# WR-005 常用语机械化匿名写稿包", "",
        "逐组检查事实、状态、篇幅、用户结构、文种功能、自然度和直接使用成本。单个正式连接词不判机械化；只有无功能的固定开头、承启、总结、尾语或段落骨架成簇复现才计风险。不得推测处理身份。", "",
    ]
    mapping: list[dict[str, Any]] = []
    eligible: list[str] = []
    for case in cases:
        first, second = blind_order(case["id"])
        first_meta = by_arm[f"{case['id']}-{first}"]
        second_meta = by_arm[f"{case['id']}-{second}"]
        if not (first_meta["technical_valid"] and second_meta["technical_valid"]):
            continue
        group = f"G{int(case['id'][1:]):02d}"
        first_text = (output / "raw" / f"{case['id']}-{first}" / "final.txt").read_text(encoding="utf-8")
        second_text = (output / "raw" / f"{case['id']}-{second}" / "final.txt").read_text(encoding="utf-8")
        packet.extend([
            f"## {group} | {case['genre']}", "", "### 任务", "", str(case["request"]), "",
            "### 稿件甲", "", first_text.rstrip(), "", "### 稿件乙", "", second_text.rstrip(), "",
        ])
        mapping.append({"group": group, "case_id": case["id"], "稿件甲": first, "稿件乙": second})
        eligible.append(group)
    packet_text = "\n".join(packet).rstrip() + "\n"
    atomic_text(output / "judge-export/blind-packet.md", packet_text)
    atomic_json(output / "restricted/mapping.json", {"schema_version": 1, "groups": mapping})
    template = {
        "schema_version": 1,
        "allowed_draft_verdicts": ["PASS", "WARN", "FAIL"],
        "allowed_winners": ["甲", "乙", "难分"],
        "groups": [
            {
                "group": group,
                "稿件甲": {"facts": "PASS|WARN|FAIL", "state": "PASS|WARN|FAIL", "length": "PASS|WARN|FAIL", "user_structure": "PASS|WARN|FAIL", "genre": "PASS|WARN|FAIL", "mechanicality": "PASS|WARN|FAIL", "direct_use_cost": "0|1|2|3|4"},
                "稿件乙": {"facts": "PASS|WARN|FAIL", "state": "PASS|WARN|FAIL", "length": "PASS|WARN|FAIL", "user_structure": "PASS|WARN|FAIL", "genre": "PASS|WARN|FAIL", "mechanicality": "PASS|WARN|FAIL", "direct_use_cost": "0|1|2|3|4"},
                "winner": "甲|乙|难分", "reason": "string",
            }
            for group in eligible
        ],
    }
    atomic_json(output / "judge-export/judge-template.json", template)
    freeze = {
        "blind_packet_sha256": sha256_text(packet_text),
        "judge_template_sha256": sha256_bytes((output / "judge-export/judge-template.json").read_bytes()),
        "eligible_groups": eligible,
    }
    atomic_json(output / "judge-export/freeze.json", freeze)
    return freeze


def run_lane(
    claude: str, output: Path, runtime: Path, skill_roots: dict[str, Path], models: dict[str, str],
    cases: list[dict[str, Any]], progress: list[dict[str, Any]], lock: threading.Lock,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case in cases:
        order = ["baseline", "candidate"] if int(case["id"][1:]) % 2 else ["candidate", "baseline"]
        for treatment in order:
            result = run_arm(claude, output, runtime, skill_roots, models, case, treatment)
            results.append(result)
            with lock:
                progress.append({"arm_id": result["arm_id"], "technical_valid": result["technical_valid"], "finished_utc": result["finished_utc"]})
                atomic_json(output / "progress.json", {"completed": len(progress), "total": 48, "arms": progress})
    return results


def preflight(claude: str) -> dict[str, Any]:
    with socket.create_connection((GATEWAY_HOST, GATEWAY_PORT), timeout=5):
        pass
    version = subprocess.run([claude, "--version"], capture_output=True, text=True, encoding="utf-8", timeout=20, check=True).stdout.strip()
    payload = load_payload()
    return {"checked_utc": utc_now(), "gateway": GATEWAY, "claude": claude, "claude_version": version, "cases": len(payload["cases"]), "calls": 48}


def execute(output: Path) -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing exact authorization marker {AUTH_ENV}")
    if output.exists():
        raise RuntimeError(f"output must not exist: {output}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable not found")
    payload = load_payload()
    output.mkdir(parents=True)
    runtime = ROOT / "output/v167-formulaic-mechanicality-real-first/runtime" / output.name
    if runtime.exists():
        raise RuntimeError(f"runtime must not exist: {runtime}")
    runtime.mkdir(parents=True)
    atomic_json(output / "preflight.json", preflight(claude))
    roots_receipt = prepare_skill_roots(runtime)
    skill_roots = {
        "baseline": Path(roots_receipt["baseline_root"]),
        "candidate": Path(roots_receipt["candidate_root"]),
    }
    by_provider = {
        provider: [case for case in payload["cases"] if case["provider"] == provider]
        for provider in payload["models"]
    }
    progress: list[dict[str, Any]] = []
    lock = threading.Lock()
    all_results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_PROVIDER_LANES) as executor:
        futures = {
            executor.submit(run_lane, claude, output, runtime, skill_roots, payload["models"], cases, progress, lock): provider
            for provider, cases in by_provider.items()
        }
        for future in as_completed(futures):
            all_results.extend(future.result())
    all_results.sort(key=lambda item: item["arm_id"])
    freeze = build_packets(output, payload["cases"], all_results)
    manifest = {
        "schema_version": 1, "finished_utc": utc_now(), "baseline_commit": BASELINE_COMMIT,
        "calls_planned": 48, "calls_completed": len(all_results),
        "technical_valid": sum(item["technical_valid"] for item in all_results),
        "pairs_eligible": len(freeze["eligible_groups"]), "arms": all_results,
    }
    atomic_json(output / "manifest.json", manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-plan", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = load_payload()
    if args.show_plan:
        print(json.dumps({"cases": len(payload["cases"]), "calls": 48, "providers": {name: 8 for name in payload["models"]}, "models": payload["models"]}, ensure_ascii=False, indent=2))
        return 0
    if args.prepare_only:
        target = ROOT / "output/v167-formulaic-mechanicality-real-first/prepare-fixture"
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        print(json.dumps(prepare_skill_roots(target), ensure_ascii=False, indent=2))
        shutil.rmtree(target)
        return 0
    if args.execute:
        if args.out is None:
            parser.error("--execute requires --out")
        execute(args.out.resolve())
        return 0
    parser.error("choose --show-plan, --prepare-only, or --execute")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
