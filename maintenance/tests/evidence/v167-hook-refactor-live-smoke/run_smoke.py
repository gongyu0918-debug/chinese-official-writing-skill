#!/usr/bin/env python3
"""Run one real Claude Code lifecycle smoke against the current Hook companion."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_DIR = Path(__file__).resolve().parent
BASE_HARNESS = ROOT / "maintenance/tests/evidence/v162-hook-writing-real-ab/harness.py"
COMPANION = ROOT / "output/v167-hook-refactor-live-smoke/companion-r1"
FROZEN_PRODUCT_TREE = "61763a444411b09ce3181303f35491633397476e"
MODEL = "alibaba-token-plan-2/deepseek-v4-flash-0731"
AUTH_ENV = "V167_HOOK_REFACTOR_LIVE_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260817"


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("v162_hook_live_base", BASE_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen lifecycle harness")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def product_tree() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD:chinese-official-writing"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return completed.stdout.strip()


def selection_closure(plugin_data: Path, final_sha256: str) -> dict[str, Any]:
    claims = []
    for path in sorted(plugin_data.rglob("selection.claim.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        claims.append(
            {
                "path": path.relative_to(plugin_data).as_posix(),
                "selected": payload.get("selected"),
                "output_sha256": payload.get("output_sha256"),
            }
        )
    return {
        "claims": claims,
        "final_matches_claim": any(item["output_sha256"] == final_sha256 for item in claims),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise SystemExit(f"missing {AUTH_ENV}={AUTH_VALUE}")
    output = args.out.resolve()
    runtime = ROOT / "output/v167-hook-refactor-live-smoke/runtime-r1"
    if output.exists() or runtime.exists():
        raise SystemExit("refusing to reuse smoke output")
    if product_tree() != FROZEN_PRODUCT_TREE:
        raise SystemExit("product tree drifted from preregistration")
    if not COMPANION.is_dir():
        raise SystemExit("assembled companion is missing")

    base = load_base()
    base.PRODUCT_COMMIT = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    base.PLUGIN_DIR = COMPANION
    base.PLUGIN_SKILL_ROOT = COMPANION / "skills/chinese-official-writing"
    base.SKILL_PATH = base.PLUGIN_SKILL_ROOT / "SKILL.md"
    base.MODELS = {"alibaba2": MODEL}

    probe = base.count_tokens_probe(MODEL)
    if not probe.get("ok"):
        raise SystemExit("gateway model preflight failed")
    claude_exe = shutil.which("claude") or "claude"
    case = base.load_cases()["T1"]
    output.mkdir(parents=True)
    runtime.mkdir(parents=True)
    meta = base.run_arm(
        claude_exe,
        runtime,
        output,
        {"pair_id": "L001", "provider": "alibaba2"},
        "A",
        "enabled",
        case,
    )
    plugin_data = output / "raw/L001-A/plugin-data"
    closure = selection_closure(plugin_data, meta["stream"]["final_sha256"])
    manifest = {
        "schema_version": 1,
        "product_tree": FROZEN_PRODUCT_TREE,
        "companion_fingerprint": tree_fingerprint(COMPANION),
        "model": MODEL,
        "effort": "max",
        "outer_retry_count": 0,
        "model_probe": probe,
        "arm": meta,
        "selection_closure": closure,
    }
    manifest["passed"] = bool(meta["technical_valid"] and closure["final_matches_claim"])
    base.atomic_write_json(output / "manifest.json", manifest)
    print(json.dumps({"passed": manifest["passed"], "manifest": str(output / "manifest.json")}, ensure_ascii=False))
    return 0 if manifest["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
