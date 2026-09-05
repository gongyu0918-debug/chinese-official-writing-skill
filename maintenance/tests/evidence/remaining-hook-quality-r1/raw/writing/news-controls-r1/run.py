"""Reuse the frozen real writer for three paired drafting/editing atoms."""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "maintenance/tests/evidence/date-source-real-r1/run.py"
spec = importlib.util.spec_from_file_location("remaining_real_writer", SOURCE)
real = importlib.util.module_from_spec(spec)
spec.loader.exec_module(real)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=("alibaba2", "minimax"))
    args = parser.parse_args()
    fixture = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
    cli = shutil.which("claude")
    assert cli
    for case in fixture["cases"]:
        for arm in ("candidate",):
            lane = HERE / args.provider / case["id"] / arm
            prompt = ("以下是本轮固定写作上下文。你没有工具，直接完成末尾用户任务。\n\n"
                      + "\n\n".join("=== " + p + " ===\n" + fixture["arms"][arm][p]
                                    for p in case["context_paths"])
                      + "\n\n=== 用户任务 ===\n" + case["prompt"])
            print("START", args.provider, case["id"], arm, flush=True)
            final, receipt = real.restricted_reply(fixture["providers"][args.provider], prompt, lane, cli)
            print(json.dumps({"provider": args.provider, "case": case["id"], "arm": arm,
                              "technical_valid": receipt["technical_valid"], "chars": len(final),
                              "seconds": receipt["seconds"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
