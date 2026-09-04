"""New offline archival reproduction, separate from the three original cases."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

BASELINE = "5fbb2d26c49d0b780ad11fc4cff008854995ad3f"
REQUEST = "本次关闭Hook。请写一份情况说明。材料：测试工作已完成。"
DRAFT = "情况说明\n\n测试工作已完成。"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root, output = args.core_root.resolve(), args.output.resolve()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if head != BASELINE or subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        raise RuntimeError("use the unchanged fixed baseline audit tree")
    output.mkdir(parents=True, exist_ok=False)
    core = root / "chinese-official-writing/hooks/core/gate_stop_hook.py"
    data = output / "core-data"
    environment = dict(os.environ, COW_GATE_HOOK_DATA=str(data), COW_GATE_CAPABILITY="delivery_review")
    record_path = data / "candidate-ai-gate-hook/offline-archive/terminal-replay.json"
    steps = []
    sequence = [
        {"hook_event_name": "UserPromptSubmit", "prompt": REQUEST},
        {"hook_event_name": "Stop", "stop_hook_active": False, "last_assistant_message": DRAFT},
        {"hook_event_name": "UserPromptSubmit", "prompt": REQUEST},
        {"hook_event_name": "Stop", "stop_hook_active": False, "last_assistant_message": DRAFT},
    ]
    for fields in sequence:
        payload = {"session_id": "offline-archive", "turn_id": "terminal-replay", "cwd": str(root), **fields}
        serialized = json.dumps(payload, ensure_ascii=False)
        completed = subprocess.run([sys.executable, "-B", str(core)], input=serialized, env=environment,
                                   text=True, encoding="utf-8", capture_output=True, timeout=35, check=False)
        try:
            response = json.loads(completed.stdout)
        except json.JSONDecodeError:
            response = None
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.is_file() else {}
        steps.append({
            "step": len(steps) + 1,
            "input_without_cwd": {k: v for k, v in payload.items() if k != "cwd"},
            "input_utf8_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
            "return_code": completed.returncode, "response": response, "stdout": completed.stdout,
            "stderr": completed.stderr, "record_after": record,
            "request_present": "request" in record,
            "data_retention_state": record.get("data_retention_state"),
            "hook_phase": record.get("hook_phase"),
        })
    reproduced = (
        all(s["return_code"] == 0 and s["response"] == {"continue": True} for s in steps)
        and steps[0]["record_after"].get("request") == REQUEST
        and not steps[1]["request_present"]
        and steps[1]["data_retention_state"] == "raw_turn_data_redacted"
        and steps[2]["record_after"].get("request") == REQUEST
        and steps[2]["data_retention_state"] == "raw_turn_data_redacted"
        and steps[3]["record_after"].get("request") == REQUEST
        and steps[3]["data_retention_state"] == "raw_turn_data_redacted"
    )
    result = {
        "case": "terminal_user_prompt_replay_restores_request",
        "origin": "new offline archival run; not part of the two original scripts",
        "core_commit": head,
        "core_file_sha256": hashlib.sha256(core.read_bytes()).hexdigest(),
        "script_file_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cwd_provenance": "Each actual event cwd is the resolved --core-root argument, omitted from input_without_cwd; its exact serialized payload is hashed.",
        "request": REQUEST, "draft": DRAFT, "steps": steps,
        "bug_reproduced": reproduced,
        "status": "REPRODUCED_OFFLINE" if reproduced else "NOT_REPRODUCED",
        "scope": "Synthetic request and real local core subprocesses; no model, network or product modification. Not an online incidence estimate.",
    }
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
