"""Read-only validation of original stream-bound D0 and final extraction; zero models."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def assistant_text(row):
    if row.get("type") != "assistant":
        return ""
    blocks = row.get("message", {}).get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def main():
    extracted = json.loads((HERE / "extracted.json").read_text(encoding="utf-8"))
    for expected in extracted["rounds"]:
        directory = HERE.parent / expected["run"] / f'round-{expected["round"]}'
        stream = directory / "stream.jsonl"
        assert digest(stream.read_bytes()) == expected["stream_sha256"]
        rows = [json.loads(line) for line in stream.read_text(encoding="utf-8").splitlines()]
        stops = [i for i, r in enumerate(rows) if r.get("subtype") == "hook_started" and r.get("hook_event") == "Stop"]
        assert stops[0] + 1 == expected["first_stop_line"]
        candidates = [(i, r) for i, r in enumerate(rows[:stops[0]]) if assistant_text(r).strip()]
        index, message = candidates[-1]
        assert index + 1 == expected["d0_assistant_line"]
        assert "tool_use" not in [b.get("type") for b in message["message"]["content"]]
        d0 = assistant_text(message)
        assert d0 == expected["d0"]
        assert digest(d0.encode("utf-8")) == expected["d0_sha256"]
        result = [r for r in rows if r.get("type") == "result"]
        assert len(result) == 1 and result[0]["subtype"] == "success"
        assert result[0]["result"] == expected["final"]
        assert digest(result[0]["result"].encode("utf-8")) == expected["final_sha256"]
        assert digest((directory / "final.txt").read_bytes()) == expected["final_file_sha256"]
        assert result[0]["result"].replace("\r\n", "\n") == (directory / "final.txt").read_text(encoding="utf-8")
        assert len(stops) == expected["stop_started_count"]
    print(json.dumps({"source_bound_extractions_verified": len(extracted["rounds"]), "new_model_calls": 0,
                      "product_changes": 0, "original_streams_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
