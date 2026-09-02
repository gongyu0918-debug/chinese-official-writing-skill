from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
SOURCE_OUTPUT = REPO / "output/complaint-reflection-r1/candidate-r3"
WRITER_PATH = HERE / "desktop_writer.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    config = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=tuple(config["providers"]))
    parser.add_argument("--case", required=True, choices=tuple(item["id"] for item in config["cases"]))
    parser.add_argument("--output-name", required=True)
    args = parser.parse_args()

    output_root = REPO / "output/complaint-reflection-r1" / args.output_name
    if output_root.exists():
        raise RuntimeError(f"output already exists: {output_root}")

    source_runtime = SOURCE_OUTPUT / "runtime" / args.provider / "candidate"
    target_runtime = output_root / "runtime" / args.provider / "candidate"
    shutil.copytree(source_runtime, target_runtime)

    case = next(item.copy() for item in config["cases"] if item["id"] == args.case)
    case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
    writer_adapter = load_module("wr027_desktop_writer_retry", WRITER_PATH)
    writer = writer_adapter.load_writer(REPO, CASES_PATH, output_root)
    record = writer.run_one(
        args.provider,
        config["providers"][args.provider],
        "candidate",
        case,
        config["reasoning_effort"],
    )
    trace = (output_root / record["trace_file"]).read_text(encoding="utf-8", errors="replace")
    reader = load_module(
        "wr027_skill_reader_retry",
        REPO / "maintenance/tests/evidence/reference-slimming-r2/run_probe.py",
    )
    files, loaded_bytes = reader.skill_reads(trace, target_runtime)
    record["skill_files_read"] = files
    record["loaded_bytes"] = loaded_bytes
    (output_root / "result.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
