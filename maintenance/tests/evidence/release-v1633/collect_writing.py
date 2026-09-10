"""Collect exact receipts and reference exposure; this is not a quality judge."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
OUT = ROOT / "output/release-v1633/word-guidance"
freeze = json.loads((OUT / "freeze.json").read_text(encoding="utf-8"))
rows = []
for path in sorted((OUT / "runs").glob("*/*/*/*/receipt.json")):
    row = json.loads(path.read_text(encoding="utf-8"))
    directory = path.parent
    prompt = (directory / "prompt.txt").read_bytes()
    assert hashlib.sha256(prompt).hexdigest() == row["prompt_sha256"]
    normalized = prompt.decode().replace(
        (OUT / "frozen input" / row["arm"] / "SKILL.md").as_posix(), "{SKILL}/SKILL.md"
    )
    row["normalized_prompt_sha256"] = hashlib.sha256(normalized.encode()).hexdigest()
    row["prompt_path"] = str(directory / "prompt.txt")
    row["trace_path"] = str(directory / "trace.jsonl")
    final = directory / "final.txt"
    row["final_path"] = str(final) if final.exists() else None
    row["final_sha256"] = hashlib.sha256(final.read_bytes()).hexdigest() if final.exists() else None
    references = {
        p.name: p.read_text(encoding="utf-8").strip()
        for p in (OUT / "frozen input" / row["arm"] / "references").glob("*.md")
    }
    matches = set()
    commands = []
    error_events = []
    for line in (directory / "trace.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") in {"error", "turn.failed"}:
            # Record diagnostic classes without copying transport addresses.
            message = str(event.get("message", event.get("error", "")))
            error_events.append({
                "event": event["type"],
                "duplicate_tool_result": "duplicate tool result" in message,
                "http_502": "502" in message,
            })
        if event.get("type") != "item.completed" or item.get("type") != "command_execution":
            continue
        command = item.get("command", "")
        output = item.get("aggregated_output", "").replace("\r\n", "\n").replace("\r", "\n")
        returned = [name for name, text in references.items() if text and text in output]
        matches.update(returned)
        commands.append({
            "index": len(commands) + 1,
            "reference_names": sorted(set(re.findall(r"[A-Za-z0-9_-]+\.md", command))),
            "output_lf_chars": len(output),
            "exit_code": item.get("exit_code"),
            "full_references_returned": returned,
        })
    row["commands"] = commands
    row["error_event_classes"] = error_events
    row["full_references_returned"] = sorted(matches)
    row["target_full_return_count"] = sum(
        "anti-ai-patterns.md" in c["full_references_returned"] for c in commands
    )
    row["unique_full_reference_lf_chars"] = sum(len(references[name]) for name in matches)
    row["all_command_output_lf_chars"] = sum(c["output_lf_chars"] for c in commands)
    rows.append(row)

pairs = []
for provider, cases in freeze["config"]["assignments"].items():
    for case in cases:
        pair = {"provider": int(provider), "case": case, "same_effort_complete": False}
        for effort in ("max", "high"):
            arms = {
                arm: next((r for r in rows if r["provider"] == int(provider) and r["case"] == case
                           and r["arm"] == arm and r["effort"] == effort and r["valid_final"]), None)
                for arm in ("baseline", "candidate")
            }
            if all(arms.values()):
                assert len({r["normalized_prompt_sha256"] for r in arms.values()}) == 1
                pair.update(same_effort_complete=True, selected_effort=effort, arms={
                    arm: {key: r[key] for key in (
                        "model", "prompt_path", "final_path", "final_sha256", "trace_path",
                        "target_full_return_count", "full_references_returned",
                        "unique_full_reference_lf_chars", "all_command_output_lf_chars",
                    )} for arm, r in arms.items()
                })
                break
        pairs.append(pair)

summary = {
    "baseline_commit": freeze["config"]["baseline"],
    "writing_candidate_commit": freeze["config"]["candidate"],
    "attempts": len(rows),
    "technical_valid_finals": sum(r["valid_final"] for r in rows),
    "complete_same_effort_pairs": sum(p["same_effort_complete"] for p in pairs),
    "pairs": pairs,
    "receipts": rows,
    "limits": "Exact full-reference matches are exposure evidence, not quality. Unique reference characters omit excerpts and repeats; all command output includes diagnostics and non-document operations. Neither is a token measure.",
}
(EVIDENCE / "writing-summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({key: summary[key] for key in (
    "attempts", "technical_valid_finals", "complete_same_effort_pairs"
)}, ensure_ascii=False))
