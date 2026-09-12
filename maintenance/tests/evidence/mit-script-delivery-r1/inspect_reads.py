"""Describe successful native read commands without inferring writing quality."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re


READ = re.compile(r"(?i)\b(?:get-content|cat|gc|type)\b|\.read_(?:text|bytes)\s*\(|\bopen\s*\(")


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def inspect(root: Path) -> dict:
    records = []
    for result_file in sorted(root.glob("*.result.json")):
        result = json.loads(result_file.read_text(encoding="utf-8"))
        snapshot = root / "snapshots" / ("candidate" if result["arm"] == "candidate" else "main")
        pages = {p.relative_to(snapshot).as_posix(): p.read_text(encoding="utf-8")
                 for p in snapshot.rglob("*.md")}
        events = []
        for call in result["commands"]:
            command = re.sub(r"/+", "/", call.get("command", "").replace("\\", "/"))
            if call.get("exit_code") != 0 or not READ.search(command):
                continue
            output = compact(call.get("aggregated_output", ""))
            if not output:
                continue
            named = sorted(p for p in pages if re.search(
                r"(?<![\w.-])" + re.escape(Path(p).name) + r"(?![\w.-])", command, re.I))
            full = sorted(p for p, body in pages.items()
                          if len(compact(body)) >= 80 and compact(body) in output)
            if named or full:
                events.append({"command_id": call.get("id"), "named_pages": named,
                               "full_content_observed": full})
        counts = Counter(p for event in events for p in event["full_content_observed"])
        named_pages = sorted({p for event in events for p in event["named_pages"]})
        records.append({"result": result_file.name, "model": result["model"],
                        "case": result["case"], "arm": result["arm"], "invalid": result["invalid"],
                        "named_pages": named_pages, "full_content_observed": sorted(counts),
                        "repeated_full_reads": {p: n for p, n in counts.items() if n > 1},
                        "named_file_characters_upper_bound": sum(len(pages[p]) for p in named_pages),
                        "events": events})
    return {"scope": "Successful native read commands only. Named pages may be partial reads; "
                     "full-content matches confirm text returned. Absence of a full match is not proof "
                     "of no read. Character bounds are not tokens. Scripts and writing quality are not graded.",
            "records": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    result = inspect(args.run)
    output = args.run / "read-analysis.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(result["records"]), "output": str(output)}, ensure_ascii=False))
