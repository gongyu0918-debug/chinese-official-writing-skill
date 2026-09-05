"""Isolated native Claude Stop lifecycle; optional labeled input corruption."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location("native_real", HERE.parent / "date-source-real-r1/run.py")
assert spec and spec.loader
REAL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(REAL)

# Same adapter and core. Only the documented event boundary is instrumented.
WRAPPER = '''import importlib.util,json,os,sys
from pathlib import Path
p=Path(__file__).with_name("gate_original.py")
s=importlib.util.spec_from_file_location("native_adapter",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
event=json.load(sys.stdin)
original=dict(event)
injected=False
if os.environ.get("FOUR_FIXES_INJECT_ECHO") == "1" and event.get("hook_event_name") == "Stop" and event.get("stop_hook_active") is True:
    event["last_assistant_message"]="错误回显：该项目已批准采购。"
    injected=True
response=m.handle(event)
with open(os.environ["FOUR_FIXES_TRACE"],"a",encoding="utf-8") as f:
    f.write(json.dumps({"native_event":original,"core_input_event":event,"fault_injected":injected,"response":response},ensure_ascii=False)+"\\n")
print(json.dumps(response,ensure_ascii=False))
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inject-wrong-echo", action="store_true")
    args = parser.parse_args()
    lane = args.output.resolve()
    lane.mkdir(parents=True, exist_ok=False)
    companion = lane / "companion"
    assembled = subprocess.run([sys.executable, "-B", str(ROOT / "maintenance/tools/assemble_hook_companion.py"),
                               "--host", "claude-code", "--capability", "delivery_review", "--output", str(companion)],
                              text=True, encoding="utf-8", capture_output=True, check=True)
    (lane / "assembly.json").write_text(assembled.stdout, encoding="utf-8", newline="\n")
    entry = companion / "scripts/gate_stop_hook.py"
    shutil.copyfile(entry, entry.with_name("gate_original.py"))
    entry.write_text(WRAPPER, encoding="utf-8", newline="\n")
    model = "alibaba-token-plan-2/deepseek-v4-flash-0731"
    env = REAL.BASE.build_environment(model, lane / "runtime")
    env.update(FOUR_FIXES_TRACE=str(lane / "native-events.jsonl"),
               FOUR_FIXES_INJECT_ECHO="1" if args.inject_wrong_echo else "0")
    cli = shutil.which("claude")
    if not cli:
        raise RuntimeError("existing Claude CLI unavailable")
    skill = companion / "skills/chinese-official-writing"
    request = REAL.read_json(HERE.parent / "date-source-real-r1/case.json")["prompt"]
    prompt = (f"先用 Read 读取本次插件的 {skill / 'SKILL.md'} 与 {skill / 'references/genre-playbook-news-message.md'}。"
              "只读取这两份文件，随后完成用户任务。不要联网，不要写文件。\n\n" + request)
    command = [cli, "--setting-sources", "", "--no-session-persistence", "--tools", "Read",
               "--allowedTools", "Read", "--permission-mode", "dontAsk", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--plugin-dir", str(companion), "--add-dir", str(companion), "--include-hook-events", "--print",
               "--verbose", "--output-format", "stream-json", "--model", model, "--effort", "max"]
    (lane / "prompt.txt").write_text(prompt, encoding="utf-8", newline="\n")
    REAL.save(lane / "fixture.json", {"model": model, "command": command,
              "claude_version": subprocess.check_output([cli, "--version"], text=True).strip(),
              "inject_wrong_echo": args.inject_wrong_echo,
              "source_hashes": {str(p.relative_to(companion)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in companion.rglob("*") if p.is_file()}})
    started = time.monotonic()
    code, failure = None, None
    with (lane / "stream.jsonl").open("w", encoding="utf-8", newline="\n") as stdout, (lane / "stderr.txt").open("w", encoding="utf-8", newline="\n") as stderr:
        try:
            completed = subprocess.run(command, cwd=lane / "runtime/work", env=env, input=prompt,
                                       text=True, encoding="utf-8", stdout=stdout, stderr=stderr, timeout=420)
            code = completed.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            failure = type(exc).__name__
    parsed = REAL.BASE.parse_stream(lane / "stream.jsonl")
    final = parsed.pop("final")
    (lane / "final.txt").write_text(final, encoding="utf-8", newline="\n")
    events = [json.loads(x) for x in (lane / "native-events.jsonl").read_text(encoding="utf-8").splitlines()] if (lane / "native-events.jsonl").exists() else []
    stops = [x for x in events if x["native_event"]["hook_event_name"] == "Stop"]
    result = {"return_code": code, "failure": failure, "seconds": round(time.monotonic()-started, 3),
              "stream": parsed, "stop_responses": [x["response"] for x in stops],
              "fault_injected": sum(x["fault_injected"] for x in stops), "final": final}
    REAL.save(lane / "result.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
