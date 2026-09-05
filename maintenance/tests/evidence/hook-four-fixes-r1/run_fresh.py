"""Two preregistered, tool-free real drafting calls; no automatic retries."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE.parent / "date-source-real-r1/run.py"
spec = importlib.util.spec_from_file_location("four_fixes_real", SOURCE)
assert spec and spec.loader
REAL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(REAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=("alibaba2", "minimax"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = REAL.read_json(HERE.parent / "date-source-real-r1/case.json")
    paths = [ROOT / p for p in config["context_files"]]
    sources = paths + [Path(__file__), SOURCE, REAL.REPLAY_PATH, REAL.REPLAY.BASE_PATH]
    fixture = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    prompt = ("以下是本轮固定写作上下文。材料事实仅以末尾用户任务为准。你没有任何工具；直接完成写稿。\n\n"
              + "\n\n".join(f"=== {p.relative_to(ROOT).as_posix()} ===\n{p.read_text(encoding='utf-8')}" for p in paths)
              + "\n\n=== 用户任务 ===\n" + config["prompt"])
    lane = args.output / args.provider
    lane.mkdir(parents=True, exist_ok=False)
    REAL.save(lane / "fixture.json", {"request": config["prompt"], "sources": fixture,
              "activation": "Frozen Skill/news leaf injected; not a native Read tool claim"})
    cli = shutil.which("claude")
    if not cli:
        raise RuntimeError("existing Claude CLI unavailable")
    model = config["providers"][args.provider]
    d0, receipt = REAL.restricted_reply(model, prompt, lane / "generation", cli)
    REAL.save(lane / "sample.json", {"id": args.provider, "model": model,
              "request": config["prompt"], "d0": d0, "receipt": receipt})
    print(json.dumps({"provider": args.provider, "d0": d0,
                      "technical_valid": receipt["technical_valid"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
