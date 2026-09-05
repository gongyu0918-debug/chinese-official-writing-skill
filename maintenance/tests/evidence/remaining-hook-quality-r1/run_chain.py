"""Run the existing seven-turn CLI test against this round's frozen product."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = "37f22146f64cf2dfcaea7a8a5afba40750215803"
SOURCE = HERE.parent / "revision-stability-audit-r1/run_chain.py"
spec = importlib.util.spec_from_file_location("remaining_revision_chain", SOURCE)
chain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chain)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=("alibaba2", "minimax"))
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--arm", choices=("baseline", "candidate"))
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_root.resolve()
    if args.prepare:
        config = json.loads((SOURCE.parent / "cases.json").read_text(encoding="utf-8"))
        config["baseline_commit"] = BASELINE
        config["candidate_commit"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        config_path = output.parent / (output.name + "-cases.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(config, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        chain.CASES_PATH = config_path
        result = chain.prepare(output)
        # Freeze the wrapper and the probe omitted by the old runner's fixture.
        for path in (Path(__file__), chain.BASE.PROBE_PATH):
            result["sources_sha256"][path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        result["scope"] = "Current baseline versus reference candidate; four persistent sessions, seven original round prompts each."
        chain.BASE.write_json(output / "fixture.json", result)
        result = {"prepared": True, "arms": result["arms"], "expected_records": result["expected_records"]}
    elif args.provider:
        if not args.arm:
            parser.error("--provider requires --arm")
        result = chain.run_session(output, args.provider, args.arm)
    else:
        result = chain.summarize(output)
        result = {key: result[key] for key in ("session_count", "record_count", "technical_failure_count")}
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
