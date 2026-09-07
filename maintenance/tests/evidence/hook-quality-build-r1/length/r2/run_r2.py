"""One explicit clean-body/400-char variant, reusing R1 CLI and runtime replay."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("length_r1_runner", HERE.parent / "run.py")
assert spec and spec.loader
BASE = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BASE
spec.loader.exec_module(BASE)
ROOT = BASE.ROOT
REQUEST = "请把这份纪要压到400字以内，保留全部事实、责任、期限和未决状态，只输出完整正文。"
CASE_ID = "M6-CLEAN-BODY-400"


def prepare() -> None:
    if (HERE / "fixture.json").exists():
        raise RuntimeError("Refuse to overwrite R2 fixture")
    source = ROOT / "output/hook-quality-build-r1/cleanliness/r2-full/M6"
    source_result = json.loads((source / "result.json").read_text(encoding="utf-8"))
    d0 = (source / "final-visible.txt").read_text(encoding="utf-8")
    expected = "761c588587bbf7831d5072059a813f07460ef2bb843f31f1471db0fcf23eacc4"
    assert BASE.digest(d0) == source_result["selected_sha256"] == source_result["final_visible_sha256"] == expected
    assert source_result["audit"]["delivery_verified"] is True
    frozen = {}
    for arm in ("baseline", "candidate"):
        frozen[arm] = {}
        for asset in BASE.ASSETS:
            path = HERE / "product" / arm / asset
            path.parent.mkdir(parents=True, exist_ok=True)
            data = ((ROOT / asset).read_bytes() if arm == "candidate" and asset in (BASE.RUNTIME, BASE.GATE)
                    else (HERE.parent / "product/baseline" / asset).read_bytes())
            path.write_bytes(data)
            frozen[arm][asset] = BASE.digest(data)
    fixture = {"case": CASE_ID, "request": REQUEST, "request_sha256": BASE.digest(REQUEST),
               "d0": d0, "d0_sha256": expected, "d0_count": 447, "maximum": 400,
               "original_M6_request_reused": False, "source_path": str(source.relative_to(ROOT)),
               "source_result_sha256": BASE.digest((source / "result.json").read_bytes()),
               "frozen_sha256": frozen, "model": BASE.MODELS["minimax"], "retry_count": 0,
               "method": "Explicit new 400-char request on the verified cleanliness D1; offline capability runtime with real no-tool CLI continuations. Not the original M6 request or a native host Hook."}
    BASE.save(HERE / "fixture.json", fixture)
    controls = []
    for arm in frozen:
        runtime = BASE.load(f"length_r2_prepare_{arm}", HERE / "product" / arm / BASE.RUNTIME)
        gate = BASE.load(f"gate_r2_prepare_{arm}", HERE / "product" / arm / BASE.GATE)
        for request in (REQUEST, "请只审稿，不改写；检查是否需要压缩到500字以内。", "请判断是否应压到500字以内。", "请检查压到500字以内是否合适。"):
            record = {"request": request}
            controls.append({"arm": arm, "request": request, "spec": runtime.parse_spec(request),
                             "gate_bounds": gate._length_bounds(request),
                             "triggered": runtime.start({"last_assistant_message": d0}, record) is not None})
    BASE.save(HERE / "baseline-prototype.json", controls)
    print(json.dumps({"fixture_sha256": BASE.digest((HERE / "fixture.json").read_bytes()), "controls": controls}, ensure_ascii=False))


def run() -> None:
    f = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
    for arm, assets in f["frozen_sha256"].items():
        for asset, expected in assets.items():
            assert BASE.digest((HERE / "product" / arm / asset).read_bytes()) == expected
    runtime = BASE.load("length_r2_real", HERE / "product/candidate" / BASE.RUNTIME)
    cli = BASE.load("length_r2_cli", ROOT / "maintenance/tests/evidence/date-source-real-r1/run.py")
    cli.REPLAY.CLI_TIMEOUT = 300
    lane = HERE / "minimax"
    lane.mkdir(parents=True, exist_ok=False)
    executable = shutil.which("claude")
    assert executable
    record = {"request": f["request"]}
    response = runtime.start({"last_assistant_message": f["d0"]}, record)
    events = [{"event": "D0", "response": response, "record": json.loads(json.dumps(record))}]
    calls = []
    final, error = f["d0"], None
    try:
        for index in range(1, 8):
            if response is None or response.get("decision") != "block":
                break
            phase = record["over_length"]["phase"]
            call_dir = lane / f"{index:02d}-{phase}"
            BASE.save(lane / f"{index:02d}-invocation.json", {"argv": cli.command(executable, f["model"]),
                      "stdin_sha256": BASE.digest(response["reason"]), "cwd": str(call_dir / "runtime/work"),
                      "phase": phase, "timeout_seconds": 300, "retry_count": 0})
            final, receipt = cli.restricted_reply(f["model"], response["reason"], call_dir, executable)
            calls.append({"phase": phase, "receipt": str((call_dir / "receipt.json").relative_to(HERE)),
                          "technical_valid": receipt["technical_valid"], "reply_sha256": BASE.digest(final)})
            response = runtime.advance({"last_assistant_message": final}, record)
            events.append({"event": phase, "response": response, "record": json.loads(json.dumps(record))})
            BASE.save(lane / "events.json", events)
            print(json.dumps({"phase": phase, "next": record["over_length"]["phase"], "calls": len(calls)}), flush=True)
        else:
            error = "call_budget_exhausted"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    (lane / "final-visible.txt").write_text(final, encoding="utf-8", newline="\n")
    BASE.save(lane / "events.json", events)
    BASE.save(lane / "result.json", {"case": CASE_ID, "method": f["method"], "model": f["model"],
              "d0_sha256": f["d0_sha256"], "request_sha256": f["request_sha256"],
              "final_sha256": BASE.digest(final), "final_count": runtime.count_text(final, "full"),
              "calls": calls, "state": record.get("over_length"), "response": response, "error": error})
    print(json.dumps({"final_count": runtime.count_text(final, "full"), "audit": record.get("over_length", {}).get("audit"), "error": error}, ensure_ascii=False))
    if error:
        raise SystemExit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare else run()
