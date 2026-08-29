from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "live_cases.json"
OUTPUT_ROOT = REPO / "output" / "ah002-news-date-completeness-r1" / "live"
BASE_PATH = REPO / "maintenance/tests/evidence/v162-hook-writing-real-ab/harness.py"
ASSEMBLER_PATH = REPO / "maintenance/tools/assemble_hook_companion.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = _load_module("ah002_live_base", BASE_PATH)
ASSEMBLER = _load_module("ah002_live_assembler", ASSEMBLER_PATH)


def load_cases() -> dict[str, Any]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout.strip()


def configure_base(payload: dict[str, Any]) -> None:
    companion = OUTPUT_ROOT / "companion"
    BASE.ROOT = REPO
    BASE.PRODUCT_COMMIT = git_text("rev-parse", "HEAD")
    BASE.PLUGIN_DIR = companion
    BASE.PLUGIN_SKILL_ROOT = companion / "skills/chinese-official-writing"
    BASE.SKILL_PATH = BASE.PLUGIN_SKILL_ROOT / "SKILL.md"
    BASE.MODELS = payload["providers"]
    BASE.TIMEOUT_SECONDS = 900


def runtime_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        **case,
        "length_non_whitespace": [1, 10000],
        "required_tokens": [group[0] for group in case["required_groups"]],
    }


def prepare() -> dict[str, Any]:
    payload = load_cases()
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    current_tree = git_text("rev-parse", "HEAD:chinese-official-writing")
    if current_tree != payload["product_tree"]:
        raise RuntimeError(f"product tree drift: {current_tree}")
    OUTPUT_ROOT.mkdir(parents=True)
    assembled = ASSEMBLER.assemble("claude-code", OUTPUT_ROOT / "companion", "delivery_review")
    configure_base(payload)
    fixture = {
        "schema_version": 1,
        "source_commit": git_text("rev-parse", "HEAD"),
        "product_tree": current_tree,
        "claude_version": subprocess.run(
            [shutil.which("claude") or "claude", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip(),
        "assembled": assembled,
        "providers": payload["providers"],
        "cases": [case["id"] for case in payload["cases"]],
    }
    BASE.atomic_write_json(OUTPUT_ROOT / "fixture.json", fixture)
    return fixture


def _assistant_texts(stream_path: Path) -> list[str]:
    texts: list[str] = []
    for line in stream_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = item.get("message") if isinstance(item, dict) else None
        if item.get("type") != "assistant" or not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        text = "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
        if text and (not texts or texts[-1] != text):
            texts.append(text)
    return texts


def _plugin_receipts(root: Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for path in root.rglob("*.json"):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(item, dict) and (
            "source_bound_date" in item or item.get("data_retention_state") == "raw_turn_data_redacted"
        ):
            receipts.append(item)
    return receipts


def analyze(case: dict[str, Any], arm_dir: Path, meta: dict[str, Any]) -> dict[str, Any]:
    texts = _assistant_texts(arm_dir / "stream.sanitized.jsonl")
    drafts = [text for text in texts if case["entity"] in text]
    initial = drafts[0] if drafts else ""
    final = (arm_dir / "final.txt").read_text(encoding="utf-8")
    receipts = _plugin_receipts(arm_dir / "plugin-data")
    audits = [item["source_bound_date"] for item in receipts if isinstance(item.get("source_bound_date"), dict)]
    audit = audits[-1] if audits else None
    selected = isinstance(audit, dict) and audit.get("selected") is True
    expected = initial
    if case["full_date"] not in initial and initial.count(case["short_date"]) == 1:
        expected = initial.replace(case["short_date"], case["full_date"], 1)
    hook_events = set(meta["stream"]["hook_started"])
    technical = bool(
        meta["return_code"] == 0
        and not meta["timeout"]
        and initial
        and final.strip()
        and meta["read_scope"]["skill_entry_read"]
        and not meta["read_scope"]["out_of_scope_reads"]
        and {"UserPromptSubmit", "PostToolUse", "Stop"}.issubset(hook_events)
        and any(item.get("data_retention_state") == "raw_turn_data_redacted" for item in receipts)
    )
    if case["mode"] == "target":
        status = (
            "PASS_EXACT_REPAIR"
            if technical
            and case["full_date"] not in initial
            and initial.count(case["short_date"]) == 1
            and selected
            and final == expected
            else "TARGET_NOT_REPRODUCED"
            if technical and case["full_date"] in initial and not selected and final == initial
            else "FAIL"
        )
    else:
        status = (
            "PASS_UNCHANGED"
            if technical and case["full_date"] in initial and not selected and final == initial
            else "FAIL"
        )
    return {
        "technical_valid": technical,
        "status": status,
        "assistant_text_count": len(texts),
        "initial_sha256": BASE.sha256_text(initial) if initial else None,
        "final_sha256": BASE.sha256_text(final),
        "initial_has_full_date": case["full_date"] in initial,
        "initial_short_date_count": initial.count(case["short_date"]),
        "source_bound_selected": selected,
        "exact_mechanical_output": final == expected,
        "missing_final_groups": [
            group for group in case["required_groups"] if not any(value in final for value in group)
        ],
        "audit": audit,
    }


def run_provider(provider_id: str) -> dict[str, Any]:
    payload = load_cases()
    if provider_id not in payload["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    configure_base(payload)
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result exists: {result_path}")
    probe = BASE.count_tokens_probe(payload["providers"][provider_id])
    if not probe.get("ok"):
        raise RuntimeError(f"provider probe failed: {probe}")
    claude_exe = shutil.which("claude") or "claude"
    records = []
    for index, case in enumerate(payload["cases"], start=1):
        pair = {"pair_id": f"{provider_id}-{index:02d}", "provider": provider_id}
        meta = BASE.run_arm(
            claude_exe,
            OUTPUT_ROOT / "runtime",
            OUTPUT_ROOT,
            pair,
            "A",
            "enabled",
            runtime_case(case),
        )
        arm_dir = OUTPUT_ROOT / "raw" / f"{pair['pair_id']}-A"
        records.append({"case_id": case["id"], "meta": meta, "analysis": analyze(case, arm_dir, meta)})
        BASE.atomic_write_json(result_path, {"provider_id": provider_id, "probe": probe, "records": records})
    return {"provider_id": provider_id, "probe": probe, "records": records}


def summarize() -> dict[str, Any]:
    payload = load_cases()
    providers = []
    for provider_id in payload["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if not path.is_file():
            continue
        item = json.loads(path.read_text(encoding="utf-8"))
        statuses = [record["analysis"]["status"] for record in item["records"]]
        item["qualifies"] = "PASS_EXACT_REPAIR" in statuses and "PASS_UNCHANGED" in statuses
        providers.append(item)
    summary = {
        "schema_version": 1,
        "provider_count": len(providers),
        "qualifying_provider_count": sum(bool(item["qualifies"]) for item in providers),
        "providers": providers,
    }
    BASE.atomic_write_json(OUTPUT_ROOT / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(load_cases()["providers"]))
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    result = prepare() if args.prepare else run_provider(args.provider) if args.provider else summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
