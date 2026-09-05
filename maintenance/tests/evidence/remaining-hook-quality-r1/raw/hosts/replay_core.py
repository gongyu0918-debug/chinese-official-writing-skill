"""Replay stored real drafts through a frozen core; no model or native host."""
from pathlib import Path
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASELINE = "37f22146f64cf2dfcaea7a8a5afba40750215803"
OLD = Path("F:/Workspaces/chinese-official-writing-skill-worktrees/hook-four-fixes-r1/output/hook-four-fixes-r1/echo-prototype")
archive = subprocess.run(["git", "archive", "--format=zip", BASELINE, "chinese-official-writing"], cwd=ROOT, capture_output=True, check=True).stdout
frozen = OUT / "frozen-baseline"
frozen.mkdir(exist_ok=False)
with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
    bundle.extractall(frozen)
for filename in ("d0.txt", "wrong_real_draft.txt", "request.txt"):
    (OUT / filename).write_bytes((OLD / filename).read_bytes())
skill = frozen / "chinese-official-writing"
core = skill / "hooks/core/gate_stop_hook.py"
draft = (OUT / "d0.txt").read_text(encoding="utf-8")
wrong = (OUT / "wrong_real_draft.txt").read_text(encoding="utf-8")
request = (OUT / "request.txt").read_text(encoding="utf-8")
data = OUT / "core-replay-data"
events = []
def emit(name, **kwargs):
    event = {"hook_event_name": name, "session_id": "stored-real-d0", "turn_id": "echo-failure", "cwd": str(skill), **kwargs}
    argv = [sys.executable, "-X", "utf8", "-B", str(core)]
    result = subprocess.run(argv, input=json.dumps(event, ensure_ascii=False), text=True, encoding="utf-8", capture_output=True, env={**os.environ, "COW_GATE_HOOK_DATA": str(data), "COW_GATE_CAPABILITY": "delivery_review"}, timeout=35, check=True)
    response = json.loads(result.stdout)
    record_file = next((data / "candidate-ai-gate-hook/stored-real-d0").glob("*.json"))
    record = json.loads(record_file.read_text(encoding="utf-8"))
    events.append({"argv": argv, "input": event, "response": response, "exit_code": result.returncode, "stderr": result.stderr, "record_after": record})
    return response, record
emit("UserPromptSubmit", prompt=request)
emit("PostToolUse", tool_input={"cmd": f'Get-Content "{skill / "SKILL.md"}"'}, tool_response={"exit_code": 0})
response, record = emit("Stop", stop_hook_active=False, last_assistant_message=draft)
assert response.get("decision") == "block" and record["emitted_sha256"] == hashlib.sha256(draft.encode()).hexdigest()
for _ in range(5):
    response, record = emit("Stop", stop_hook_active=True, last_assistant_message=wrong)
assert response["continue"] is False and record["delivery_verified"] is False
assert record["data_retention_state"] == "raw_turn_data_redacted"
(OUT / "core-replay-events.json").write_text(json.dumps(events, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "hard-stop.json").write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"scope": "REAL_D0_CORE_REPLAY_NOT_NATIVE_HOST", "model_calls": 0, "baseline": BASELINE, "d0_sha256": hashlib.sha256(draft.encode()).hexdigest(), "wrong_sha256": hashlib.sha256(wrong.encode()).hexdigest(), "response": response, "delivery_verified": record["delivery_verified"]}, ensure_ascii=False))
