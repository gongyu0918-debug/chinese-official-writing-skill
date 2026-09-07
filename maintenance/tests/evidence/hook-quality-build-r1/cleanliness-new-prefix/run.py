"""One real cleanliness chain on the frozen native minutes prefix example."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "output/hook-quality-build-r1/continuity/native-r4-minutes/round-5"
RUNTIME = ROOT / "chinese-official-writing/hooks/capabilities/delivery_cleanliness/runtime.py"
HELPER = ROOT / "output/hook-quality-build-r1/cleanliness/run_cleanliness.py"
REAL = ROOT / "maintenance/tests/evidence/date-source-real-r1/run.py"
MODEL = "alibaba-token-plan-2/deepseek-v4-flash-0731"


def sha(data: bytes | str) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value) -> None:
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
        raise RuntimeError("Refuse to overwrite fixture")
    invocation = read(SOURCE / "invocation.json")
    records = [json.loads(line) for line in (SOURCE / "stream.jsonl").read_text(encoding="utf-8").splitlines()]
    results = [r for r in records if r.get("type") == "result"]
    assert len(results) == 1 and results[0].get("subtype") == "success" and results[0].get("is_error") is False
    d0 = results[0]["result"]
    assert d0 == (SOURCE / "final.txt").read_text(encoding="utf-8")
    prefix, body = d0.split("\n\n---\n\n")
    assert prefix.startswith("以下正文约") and "是" not in prefix and "为" not in prefix
    assert body.startswith("清源图书馆服务改进专题会议纪要")
    assistants = ["".join(b.get("text", "") for b in (r.get("message") or {}).get("content", [])
                         if isinstance(b, dict) and b.get("type") == "text")
                  for r in records if r.get("type") == "assistant"]
    assistants = [t for t in assistants if t]
    assert any(t == d0 for t in assistants)
    case = {"id": "NATIVE-MINUTES-R4-R5-PREFIX", "kind": "native_real_D0_cleanliness_replay",
            "provider": "alibaba2", "request": invocation["prompt"], "d0": d0, "expected": body, "body": body,
            "expected_method": "Delete first paragraph plus separator only. Oracle is never injected as a revision or verdict."}
    for key in ("request", "d0", "expected", "body"):
        case[key + "_sha256"] = sha(case[key])
    source_proof = {"source": str(SOURCE.relative_to(ROOT)), "source_sha256": {},
                    "native_result_count": 1, "session_id": results[0].get("session_id"),
                    "assistant_text_sha256": [sha(t) for t in assistants], "result_matches_assistant_D0": True,
                    "result_matches_final_file": True, "removed_prefix": prefix,
                    "counts_nonspace": {"d0": len("".join(d0.split())), "body": len("".join(body.split()))}}
    for name in ("stream.jsonl", "invocation.json", "final.txt"):
        data = (SOURCE / name).read_bytes()
        source_proof["source_sha256"][name] = sha(data)
        target = HERE / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (HERE / "runtime-baseline.py").write_bytes(RUNTIME.read_bytes())
    (HERE / "helper-snapshot.py").write_bytes(HELPER.read_bytes())
    fixture = {"case": case, "source_proof": source_proof, "models": {"alibaba2": MODEL},
               "max_continuations_per_case": 4, "call_timeout_seconds": 180, "retry_count": 0,
               "runtime_sha256": sha((HERE / "runtime-baseline.py").read_bytes()),
               "helper_sha256": sha((HERE / "helper-snapshot.py").read_bytes()),
               "cli_helper_sha256": sha(REAL.read_bytes()),
               "method": "Native real D0 source; current cleanliness runtime driven with real isolated no-tool replies. This new cleanup replay is not a native Hook run.",
               "acceptance": "Revision, real verdict, selected D1 and actual final must match original body bytes; original body length/factual problems are outside this cleanup target."}
    save(HERE / "fixture.json", fixture)
    print(json.dumps({"fixture_sha256": sha((HERE / "fixture.json").read_bytes()), "d0_sha256": case["d0_sha256"],
                      "expected_sha256": case["expected_sha256"], "counts": source_proof["counts_nonspace"]}, ensure_ascii=False))


def run() -> None:
    f = read(HERE / "fixture.json")
    assert sha((HERE / "runtime-baseline.py").read_bytes()) == f["runtime_sha256"]
    assert sha((HERE / "helper-snapshot.py").read_bytes()) == f["helper_sha256"]
    assert sha(REAL.read_bytes()) == f["cli_helper_sha256"]
    helper = load("new_prefix_existing_runner", HERE / "helper-snapshot.py")
    helper.HERE = HERE
    helper.ROOT = ROOT
    real = load("new_prefix_cheap_cli", REAL)
    executable = shutil.which("claude")
    assert executable
    result = helper.run_case(f["case"], f, real, executable)
    save(HERE / "result.json", result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare else run()
