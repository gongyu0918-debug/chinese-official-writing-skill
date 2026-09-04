"""Derive corrected Windows read metrics; never overwrite frozen raw records."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4] / "output/reference-route-audit-r1/r1"
FILE_RE = re.compile(r"""(?i)(?:^|[/'"])(SKILL\.md|references/[A-Za-z0-9_.-]+\.md)""")
READ_RE = re.compile(r"(?i)\b(?:get-content|cat|gc|type)\b|\.read_(?:text|bytes)\s*\(|\bopen\s*\(")


def recount(root: Path) -> dict:
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    corrected = []
    for original in summary["records"]:
        record = dict(original)
        trace_path = root / original["trace_file"]
        raw = trace_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != original["trace_sha256"]:
            raise RuntimeError(f"trace changed: {trace_path}")
        skill = root / "runtime" / original["provider_id"] / original["arm"] / ".agents/skills/chinese-official-writing"
        all_files, events = set(), []
        for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = event.get("item", {})
            command = re.sub(r"/+", "/", item.get("command", "").replace("\\", "/"))
            if (event.get("type") != "item.completed" or item.get("type") != "command_execution"
                    or item.get("exit_code") != 0 or not item.get("aggregated_output") or not READ_RE.search(command)):
                continue
            files = {"SKILL.md" if f.casefold() == "skill.md" else f for f in FILE_RE.findall(command)}
            files = {f for f in files if (skill / f).is_file()}
            if files:
                events.append({"trace_line": line_number, "files": sorted(files),
                               "full_file_bytes": sum((skill / f).stat().st_size for f in files)})
                all_files.update(files)
        record.update(uncorrected_loaded_bytes=original["loaded_bytes"], skill_files_read=sorted(all_files),
                      loaded_bytes=sum((skill / f).stat().st_size for f in all_files),
                      read_events=events, repeated_read_full_file_bytes=sum(e["full_file_bytes"] for e in events))
        corrected.append(record)
    result = {"schema_version": 1, "reason": "Collapse repeated Windows path separators before matching references.",
              "scope": "Derived analysis only; original provider records and trace hashes preserved.",
              "read_metric": "Unique successful-read file bytes; repeated-read bytes also reported. Partial/truncated reads use full-file upper bounds. Not tokens.",
              "records": corrected, "pairs": []}
    for r in corrected:
        if r["arm"] != "baseline":
            continue
        c = next(x for x in corrected if x["provider_id"] == r["provider_id"] and x["case_id"] == r["case_id"] and x["arm"] == "candidate")
        result["pairs"].append({"provider_id": r["provider_id"], "case_id": r["case_id"],
                                "valid": not r["technical_failures"] and not c["technical_failures"],
                                "baseline_bytes": r["loaded_bytes"], "candidate_bytes": c["loaded_bytes"],
                                "delta_bytes": c["loaded_bytes"] - r["loaded_bytes"],
                                "files_removed": sorted(set(r["skill_files_read"]) - set(c["skill_files_read"])),
                                "files_added": sorted(set(c["skill_files_read"]) - set(r["skill_files_read"]))})
    target = root / "read-analysis-corrected.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    result = recount(ROOT)
    print(json.dumps({"records": len(result["records"]), "pairs": result["pairs"]}, ensure_ascii=False, indent=2))
