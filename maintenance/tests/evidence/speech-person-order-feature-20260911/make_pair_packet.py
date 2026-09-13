"""Bind one completed preregistered pair without changing delivered final text."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make(out, case):
    plan = json.loads((out / "freeze.json").read_text(encoding="utf-8"))["plan"]
    assert case in plan["cold_cases"]
    spec = next(c for c in plan["cases"] if c["id"] == case)
    target = out / "anonymous" / (case + ".json")
    assert not target.exists(), "Anonymous input must never be overwritten"
    task = out / "prompts" / (case + ".txt")
    assert sha(task) == spec["task_sha256"]
    identity = "P" + str(plan["cold_cases"].index(case) + 1).zfill(2)
    record = {"id": identity, "task": task.read_text(encoding="utf-8-sig")}
    binding = {"id": identity, "case": case, "writer": spec["route"], "task_sha256": sha(task)}
    order = ["baseline", "candidate"]
    if secrets.randbelow(2):
        order.reverse()
    for label, arm in zip(("A", "B"), order):
        root = out / "runs" / spec["route"].split("/")[0] / case / arm / "attempt-1"
        receipt = json.loads((root / "receipt.json").read_text(encoding="utf-8"))
        assert receipt["technical_valid"] and receipt["actual_client_model"] == spec["route"]
        assert receipt["configured_effort"] == plan["effort"] and receipt["snapshot_unchanged"]
        assert sha(root / "final.md") == receipt["hashes"]["final.md"]
        record[label] = (root / "final.md").read_text(encoding="utf-8")
        binding[label] = {"arm": arm, "final": (root / "final.md").relative_to(out).as_posix(), "sha256": sha(root / "final.md")}
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({"cases": [record]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    binding["packet_sha256"] = sha(target)
    destination = out / "mappings" / (case + ".json")
    destination.parent.mkdir(exist_ok=True)
    assert not destination.exists()
    destination.write_text(json.dumps(binding, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"case": case, "packet_sha256": sha(target)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--case", required=True)
    a = p.parse_args()
    print(json.dumps(make(a.out, a.case), ensure_ascii=False))
