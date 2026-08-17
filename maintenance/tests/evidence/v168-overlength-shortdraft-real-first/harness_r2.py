from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import argparse


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HARNESS = HERE / "harness.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("v168_real_first", HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load R1 harness")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(output_name: str) -> int:
    output = ROOT / "output" / "v168-overlength-shortdraft-real-first" / output_name
    if output.exists():
        raise RuntimeError(f"Refusing to reuse output: {output}")
    base = load_harness()
    base.OUTPUT = output
    payload = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    cases = {case["id"]: dict(case) for case in payload["cases"]}
    cases["R01"]["mode"] = "readme-r2"
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable not found")
    records = [
        base.run_case(claude, payload["models"], cases[case_id])
        for case_id in ("O01", "R01")
    ]
    manifest = {
        "schema_version": 1,
        "calls": len(records),
        "technical_valid": sum(bool(item["technical_valid"]) for item in records),
        "records": records,
    }
    base.BASE.atomic_json(output / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["technical_valid"] == len(records) else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-name", default="formal-r2")
    args = parser.parse_args()
    raise SystemExit(main(args.output_name))
