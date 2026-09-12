"""Summarize completed native traces without running writers or product scripts."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def normalize(text: str, numbered: bool = False) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    if numbered:
        text = re.sub(r"(?m)^\d+:", "", text)
    return text.strip()


def inspect(run: Path) -> dict:
    binding = json.loads((run / "binding.json").read_text(encoding="utf-8-sig"))
    result = []
    for receipt in sorted(run.glob("*.result.json")):
        stem = receipt.name.removesuffix(".result.json")
        item = json.loads(receipt.read_text(encoding="utf-8-sig"))
        arm = item["arm"]
        snapshot = run / "snapshots" / arm
        if not snapshot.exists() and arm == "baseline":
            snapshot = run / "snapshots" / "main"
        paths = [snapshot / "SKILL.md", *sorted((snapshot / "references").glob("*.md"))]
        pages = {p.relative_to(snapshot).as_posix(): normalize(p.read_text(encoding="utf-8-sig")) for p in paths}
        trace = run / f"{stem}.trace.jsonl"
        events = [json.loads(line) for line in trace.read_text(encoding="utf-8-sig").splitlines()]
        commands = [e["item"] for e in events if e.get("type") == "item.completed" and e["item"].get("type") == "command_execution"]
        returns: Counter[str] = Counter()
        script_calls = []
        for ordinal, command in enumerate(commands):
            text = command.get("command", "")
            output = normalize(command.get("aggregated_output", ""))
            numbered = normalize(command.get("aggregated_output", ""), numbered=True)
            for name, page in pages.items():
                if page and (page in output or page in numbered):
                    returns[name] += 1
            # Count shell commands containing a script, not each invocation in a compound command.
            execution = re.search(r"(?:^|[\s'\"])(?:python(?:3(?:\.\d+)?)?(?:\.exe)?|py(?:\.exe)?)(?=[\s'\"])", text, re.I)
            if execution and "--help" not in text:
                for script in ("prose_lint.py", "draft_length.py"):
                    if script in text:
                        script_calls.append({"script": script, "command_index": ordinal, "item_id": command["id"], "exit_code": command.get("exit_code"), "command": text, "stdout": command.get("aggregated_output", "")})
        usages = item.get("usage") or []
        total_input = sum(u.get("input_tokens", 0) for u in usages if u)
        cached = sum(u.get("cached_input_tokens", 0) for u in usages if u)
        final = run / f"{stem}.final.txt"
        result.append({
            "stem": stem, "case": item["case"], "model": item["model"], "arm": arm,
            "invalid": item.get("invalid", []), "seconds": item["seconds"],
            "commands": len(commands), "unique_pages": sorted(returns), "page_returns": dict(returns),
            "read_chars_unique": sum(len((snapshot / name).read_text(encoding="utf-8-sig")) for name in returns),
            "script_calls": script_calls,
            "input_tokens": total_input, "cached_input_tokens": cached,
            "uncached_input_tokens": total_input - cached,
            "output_tokens": sum(u.get("output_tokens", 0) for u in usages if u),
            "trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest(),
            "final_sha256": hashlib.sha256(final.read_bytes()).hexdigest() if final.exists() else None,
        })
    summary = {}
    for arm in sorted({r["arm"] for r in result}):
        records = [r for r in result if r["arm"] == arm]
        summary[arm] = {k: sum(r[k] for r in records) for k in ("commands", "read_chars_unique", "input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "seconds")}
        summary[arm]["calls"] = len(records)
        summary[arm]["technical_valid"] = sum(not r["invalid"] for r in records)
        for script in ("prose_lint.py", "draft_length.py"):
            summary[arm][script] = sum(c["script"] == script for r in records for c in r["script_calls"])
        summary[arm]["anti_ai_page_returned"] = sum("references/anti-ai-patterns.md" in r["unique_pages"] for r in records)
        summary[arm]["tasks_with_prose_command"] = sum(any(c["script"] == "prose_lint.py" for c in r["script_calls"]) for r in records)
    pairs = {}
    for row in result:
        pairs.setdefault((row["model"], row["case"]), {})[row["arm"]] = row
    comparable = [pair for pair in pairs.values() if len(pair) == 2 and all(
        not row["invalid"] and "references/anti-ai-patterns.md" in row["unique_pages"]
        and any(c["script"] == "prose_lint.py" for c in row["script_calls"])
        for row in pair.values())]
    comparable_summary = {"pairs": len(comparable), "scope": "Cost diagnostic for pairs with anti-AI page returned and a prose-script command on both arms. Not a quality-selected subset, proof of effective checking, or proof of equal length checks."}
    for arm in summary:
        comparable_summary[arm] = {key: sum(pair[arm][key] for pair in comparable) for key in ("read_chars_unique", "uncached_input_tokens", "commands", "seconds")}
    return {"method": "Full returned page text matching, including numbered rg output; per-task deduplication. Legacy script_calls fields count shell commands containing each script, not individual processes: one compound command may scan multiple files. Counts do not prove nonempty input, semantic review, or writing quality. Failed calls remain visible; totals are not a paired quality result or monetary cost.", "binding_fingerprints": binding.get("fingerprints"), "records": result, "summary": summary, "matched_anti_prose_pairs": comparable_summary}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.run)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
