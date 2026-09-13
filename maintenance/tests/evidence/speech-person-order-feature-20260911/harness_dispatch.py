"""Dispatch only the frozen feature-writing budget, serially per exact route.

Each route's first pair must establish matching native identity and a non-error
final before that lane continues. Pair order alternates within each route. No
retry, model substitution, cold review, preparation or frozen-input mutation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PYTHON = Path("C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe")
HOST = HERE / "harness_qwen.py"
LOCK = threading.Lock()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    freeze = read(out / "freeze.json")
    assert sha(HOST) == freeze["harness_sha256"]
    assert sha(HERE / "harness_cold_inline.py") == freeze["cold_harness_sha256"]
    plan = freeze["plan"]
    path = out / "writer-dispatch.json"
    assert not path.exists(), "Dispatch already exists; preserve prior attempts"
    summary = {"started_unix": time.time(), "completed": False, "writer_lanes_released": False,
               "expected_calls": plan["budget"]["initial_writer_calls"], "automatic_retries": 0,
               "freeze_sha256": sha(out / "freeze.json"), "dispatcher_sha256": sha(Path(__file__)),
               "python": str(PYTHON), "configured_effort": plan["effort"], "runs": [], "pairs": [], "lane_status": {}}
    save(path, summary)

    def lane(route):
        cases = [c for c in plan["cases"] if c["route"] == route]
        for index, case in enumerate(cases):
            pair = []
            arms = ("baseline", "candidate") if index % 2 == 0 else ("candidate", "baseline")
            for arm in arms:
                receipt_path = out / "runs" / route.split("/")[0] / case["id"] / arm / "attempt-1/receipt.json"
                assert not receipt_path.parent.exists(), "Attempt already exists; no overwrite"
                command = [str(PYTHON), str(HOST), "write", "--out", str(out), "--route", route,
                           "--case", case["id"], "--arm", arm, "--attempt", "1"]
                started = time.time()
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
                row = {"route": route, "case": case["id"], "arm": arm, "attempt": 1,
                       "started_unix": started, "finished_unix": time.time(), "argv": command,
                       "dispatcher_exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
                       "receipt_path": str(receipt_path), "receipt_exists": receipt_path.exists()}
                protocol_valid = False
                if receipt_path.exists():
                    receipt = read(receipt_path)
                    protocol_valid = (receipt["technical_valid"] and receipt["actual_client_model"] == route
                                      and receipt["init"]["qwen_code_version"] == plan["client_version_expected"]
                                      and not receipt["api_error_placeholder"])
                    row.update(receipt_sha256=sha(receipt_path), status=receipt["status"],
                               actual_client_model=receipt["actual_client_model"],
                               init_version=(receipt.get("init") or {}).get("qwen_code_version"),
                               api_error_placeholder=receipt["api_error_placeholder"],
                               final_sha256=receipt["hashes"]["final.md"], read_calls=receipt["read_calls"])
                row["protocol_valid"] = protocol_valid
                pair.append(row)
                with LOCK:
                    summary["runs"].append(row)
                    save(path, summary)
                    print(json.dumps({k: row.get(k) for k in ("route", "case", "arm", "status", "init_version", "api_error_placeholder", "read_calls")}), flush=True)
                if not receipt_path.exists() or (index == 0 and not protocol_valid):
                    with LOCK:
                        summary["lane_status"][route] = "STOPPED_FIRST_PAIR_TECHNICAL_FAILURE" if index == 0 else "STOPPED_MISSING_RECEIPT"
                        save(path, summary)
                    return
            with LOCK:
                event = {"route": route, "case": case["id"], "pair_finished": True,
                         "both_protocol_valid": all(r["protocol_valid"] for r in pair)}
                summary["pairs"].append(event)
                save(path, summary)
                print(json.dumps(event), flush=True)
        with LOCK:
            summary["lane_status"][route] = "COMPLETE"
            save(path, summary)

    with ThreadPoolExecutor(max_workers=len(plan["writers"])) as pool:
        list(pool.map(lane, plan["writers"]))
    summary.update(completed=True, writer_lanes_released=True, finished_unix=time.time(), observed_calls=len(summary["runs"]))
    save(path, summary)
    print(json.dumps({"writer_lanes_released": True, "calls": len(summary["runs"]), "lane_status": summary["lane_status"]}), flush=True)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
