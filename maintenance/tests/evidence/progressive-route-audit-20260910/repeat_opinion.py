"""Run the single authorized exact-prompt opinion-request repeat pair."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import runpy
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = Path(__file__).resolve().parent
    runner = evidence / "run_atom.py"
    config_path = evidence / "correspondence.json"
    original_argv = sys.argv[:]
    try:
        sys.argv = [str(runner), str(config_path)]
        namespace = runpy.run_path(str(runner), run_name="opinion_repeat_runner")
    finally:
        sys.argv = original_argv
    config = namespace["config"]
    assert config["baseline"] == "e8103f53"
    assert config["candidate"] == "30902fbd"
    assert namespace["m"].MODELS[1] == "alibaba-token-plan/qwen3.8-flash"
    out = namespace["OUT"]
    arms = ("baseline", "candidate")
    originals = {
        arm: out / "runs" / "1" / "opinion_request" / arm / "max"
        for arm in arms
    }
    for folder in originals.values():
        assert not (folder / "repeat1").exists(), "One repeat only; refuse to overwrite"
        assert (folder / "prompt.txt").is_file()
        assert (folder / "final.txt").is_file()
    original_hashes = {
        arm: {name: digest(folder / name) for name in ("prompt.txt", "final.txt")}
        for arm, folder in originals.items()
    }
    one = namespace["one"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            arm: pool.submit(one, 1, "opinion_request", arm, repeat=True)
            for arm in arms
        }
        receipts = {arm: future.result() for arm, future in futures.items()}
    for arm, folder in originals.items():
        for name in ("prompt.txt", "final.txt"):
            assert digest(folder / name) == original_hashes[arm][name]
        assert digest(folder / "repeat1" / "prompt.txt") == original_hashes[arm]["prompt.txt"]
    summary = {
        "purpose": "One paired exact-prompt repeat for opinion wording and process narration",
        "effort": "max",
        "fallback": False,
        "original_hashes": original_hashes,
        "prompt_bytes_unchanged": True,
        "original_finals_unchanged": True,
        "receipts": receipts,
    }
    namespace["save"](out / "repeat-opinion-receipts.json", summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
