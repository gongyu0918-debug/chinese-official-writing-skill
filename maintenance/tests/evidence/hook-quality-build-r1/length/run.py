"""Frozen same-D0 length replay; reuse the existing no-tool cheap CLI runner."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE_COMMIT = "b77f6381438c8fa01f8576c205d13af4b8a987fd"
RUNTIME = "chinese-official-writing/hooks/capabilities/over_length/runtime.py"
GATE = "chinese-official-writing/scripts/review_gate.py"
ASSETS = (RUNTIME, GATE,
          "chinese-official-writing/hooks/capabilities/protective_expansion/contract.py",
          "chinese-official-writing/hooks/shared/hard_anchors.py")
MODELS = {"alibaba2": "alibaba-token-plan-2/deepseek-v4-flash-0731",
          "minimax": "minimax-cn/MiniMax-M3"}
PACKETS = {"P6": "report-fourth-packet.json", "M6": "minutes-third-packet.json"}
EXPECTED = {
    "P6": ("3127a9501441b66a585be4f3ddcb811a61ea3de1f5f6357dd8baa813be4c4124", "586720c868897f08513d9421ef2b930d19b3cabb6a0b4d230c621025c9d9de5f"),
    "M6": ("e203b8981e83ed9e7f81236ed9b3c3a2f4f9a89d62abbe426f3c6dd82e4b5178", "8c3d2b83b83fd095553ab2d8d013bd868066a098cfd26e364414bc26e935e343"),
}


def digest(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def prepare() -> None:
    if (HERE / "fixture.json").exists():
        raise RuntimeError("Refuse to overwrite the frozen fixture")
    cases = {}
    for case_id, name in PACKETS.items():
        path = ROOT / "maintenance/tests/evidence/natural-writing-stability-r1/raw/r2" / name
        assert digest(path.read_bytes()) == EXPECTED[case_id][0]
        chain, = json.loads(path.read_text(encoding="utf-8"))["chains"]
        assert chain["id"] == case_id
        r5 = chain["rounds"][-1]
        assert digest(r5["text"]) == r5["sha256"] == EXPECTED[case_id][1]
        cases[case_id] = {"packet": str(path.relative_to(ROOT)), "packet_sha256": EXPECTED[case_id][0],
                          "request": r5["prompt"], "request_sha256": digest(r5["prompt"]),
                          "d0": r5["text"], "d0_sha256": r5["sha256"],
                          "original_hook_mode": "off", "round": 5}
    frozen = {}
    for arm in ("baseline", "candidate"):
        frozen[arm] = {}
        for asset in ASSETS:
            data = ((ROOT / asset).read_bytes() if arm == "candidate" and asset in (RUNTIME, GATE)
                    else subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{asset}"], cwd=ROOT))
            path = HERE / "product" / arm / asset
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            frozen[arm][asset] = digest(data)
    save(HERE / "fixture.json", {"base_commit": BASE_COMMIT, "models": MODELS, "retry_count": 0,
                                 "timeout_per_call_seconds": 300, "frozen_sha256": frozen, "cases": cases,
                                 "method": "Offline capability runtime dispatch with real no-tool CLI continuations; historical D0, not native host Hook or newly generated D0."})
    checks = []
    for arm in frozen:
        runtime = load(f"length_{arm}", HERE / "product" / arm / RUNTIME)
        gate = load(f"gate_{arm}", HERE / "product" / arm / GATE)
        for case_id, case in cases.items():
            record = {"request": case["request"]}
            response = runtime.start({"last_assistant_message": case["d0"]}, record)
            checks.append({"arm": arm, "case": case_id, "spec": runtime.parse_spec(case["request"]),
                           "review_gate_bounds": gate._length_bounds(case["request"]),
                           "full_count": runtime.count_text(case["d0"], "full"),
                           "tolerance_ratio": runtime.OVER_TOLERANCE_RATIO,
                           "triggered": response is not None, "phase": record.get("over_length", {}).get("phase")})
    save(HERE / "baseline-prototype.json", checks)
    print(json.dumps({"fixture_sha256": digest((HERE / "fixture.json").read_bytes()), "checks": checks}, ensure_ascii=False))


def run(provider: str) -> None:
    fixture = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
    for arm, assets in fixture["frozen_sha256"].items():
        for asset, expected in assets.items():
            assert digest((HERE / "product" / arm / asset).read_bytes()) == expected
    runtime = load(f"length_real_{provider}", HERE / "product/candidate" / RUNTIME)
    cli = load(f"length_cli_{provider}", ROOT / "maintenance/tests/evidence/date-source-real-r1/run.py")
    cli.REPLAY.CLI_TIMEOUT = fixture["timeout_per_call_seconds"]
    model = MODELS[provider]
    executable = shutil.which("claude")
    assert executable
    lane = HERE / "providers" / provider
    lane.mkdir(parents=True, exist_ok=False)
    case = fixture["cases"]["M6"]
    record = {"request": case["request"]}
    response = runtime.start({"last_assistant_message": case["d0"]}, record)
    calls = []
    events = [{"event": "D0", "response": response, "record": json.loads(json.dumps(record))}]
    final = case["d0"]
    error = None
    try:
        for index in range(1, 8):
            if response is None or response.get("decision") != "block":
                break
            phase = record["over_length"]["phase"]
            prompt = response["reason"]
            call_dir = lane / f"{index:02d}-{phase}"
            save(lane / f"{index:02d}-invocation.json", {"argv": cli.command(executable, model),
                 "stdin_sha256": digest(prompt), "cwd": str(call_dir / "runtime/work"),
                 "phase": phase, "timeout_seconds": cli.REPLAY.CLI_TIMEOUT, "retry_count": 0})
            final, receipt = cli.restricted_reply(model, prompt, call_dir, executable)
            calls.append({"phase": phase, "receipt": str((call_dir / "receipt.json").relative_to(HERE)),
                          "reply_sha256": digest(final), "count": runtime.count_text(final, "full"),
                          "technical_valid": receipt["technical_valid"]})
            response = runtime.advance({"last_assistant_message": final}, record)
            events.append({"event": phase, "reply_sha256": digest(final), "response": response,
                           "record": json.loads(json.dumps(record))})
            save(lane / "events.json", events)
            print(json.dumps({"provider": provider, "phase": phase, "next": record["over_length"]["phase"],
                              "calls": len(calls)}, ensure_ascii=False), flush=True)
        else:
            error = "harness_call_budget_exhausted"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    (lane / "final-visible.txt").write_text(final, encoding="utf-8", newline="\n")
    save(lane / "events.json", events)
    result = {"provider": provider, "model": model, "method": fixture["method"], "case": "M6/R5",
              "d0_sha256": case["d0_sha256"], "final_sha256": digest(final),
              "final_count": runtime.count_text(final, "full"), "unchanged_from_d0": final == case["d0"],
              "calls": calls, "response": response, "state": record["over_length"], "error": error}
    save(lane / "result.json", result)
    print(json.dumps({k: result[k] for k in ("provider", "final_count", "unchanged_from_d0", "error")}, ensure_ascii=False), flush=True)
    if error:
        raise SystemExit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--provider", choices=MODELS)
    args = parser.parse_args()
    prepare() if args.prepare else run(args.provider)
