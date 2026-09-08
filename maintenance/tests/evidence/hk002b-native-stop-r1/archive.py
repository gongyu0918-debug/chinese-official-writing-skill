"""Archive only the two controlled native probes; never copy homes or sessions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


ROOT = Path("F:/Workspaces/chinese-official-writing-skill/output/integration-worktrees/hk002b-main-20260909")
OUT = ROOT / "output/hk002b-native-stop-r1"
HERE = ROOT / "maintenance/tests/evidence/hk002b-native-stop-r1"
TRANSFER = Path("C:/Users/admin/.codex/worktrees/5039/chinese-official-writing-skill/output/hk002b-native-transfer")
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "provider_token": re.compile(r"\b(?:sk-(?:ant-)?[A-Za-z0-9_-]{24,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b"),
    "authorization_value": re.compile(r"(?i)(?:authorization|proxy-authorization)[\"'\s]*[:=][\"'\s]*(?:bearer|basic)\s+[A-Za-z0-9+/_.=-]{12,}"),
    "assigned_credential": re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|cookie)[\"'\s]*[:=]\s*[\"'][^\"'\r\n]{8,}[\"']"),
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def unique(items: list) -> list:
    return list(dict.fromkeys(items))


def gather() -> tuple[dict[str, bytes], dict]:
    artifacts: dict[str, bytes] = {}
    cases = []
    for case in ("error", "control"):
        run = OUT / "runs" / case / "attempt-01"
        obs = json.loads((run / "observation.json").read_text(encoding="utf-8"))
        receipt = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
        prefix = "raw/" + case + "/attempt-01/"
        paths = [
            ("prompt.txt", run / "prompt.txt"),
            ("frozen-d0.txt", run / "work/frozen-d0.txt"),
            *[(name, run / name) for name in (
                "final.txt", "invocation.json", "receipt.json", "trace.jsonl",
                "stderr.txt", "installed.json", "prompt-binding.json", "snapshot-index.jsonl",
            )],
        ]
        paths.extend(("setup/" + path.name, path) for path in sorted((run / "setup").iterdir())
                     if path.is_file() and path.suffix in {".json", ".txt"})
        rows = [json.loads(line) for line in (run / "snapshot-index.jsonl").read_text(encoding="utf-8").splitlines() if line]
        phases, states = [], []
        request_bound = False
        for row in rows:
            path = run / "snapshots" / (row["sha256"] + ".json")
            raw = path.read_bytes()
            if sha(raw) != row["sha256"]:
                raise RuntimeError("snapshot SHA mismatch: " + row["sha256"])
            artifacts[prefix + "snapshots/" + path.name] = raw
            value = json.loads(raw)
            if row["path"].endswith("/state.json"):
                states.append(value)
            elif "/transactions/" not in row["path"]:
                request_bound |= "request" in value
                if value.get("hook_phase"):
                    phases.append(value["hook_phase"])
        for relative, path in paths:
            if not path.resolve().is_relative_to(run.resolve()):
                raise RuntimeError("archive input escaped the exact run")
            artifacts[prefix + relative] = path.read_bytes()
        for name, value in (
            ("host-context.json", obs["host_turn_context"]),
            ("assistant-messages.json", obs["assistant_messages"]),
            ("terminal-records.json", obs["terminal_records"]),
            ("tool-observations.json", obs["tool_items"]),
        ):
            artifacts[prefix + name] = encoded(value)
        final_state = states[-1] if states else {}
        terminal = obs["terminal_records"][-1]["record"] if obs["terminal_records"] else {}
        messages = obs["assistant_messages"]
        body_indices = [index for index, item in enumerate(messages)
                        if item["sha256"] == obs["frozen_d0_sha256"]]
        parsed_messages = []
        for item in messages:
            try:
                value = json.loads(item["text"])
            except ValueError:
                continue
            if isinstance(value, dict):
                parsed_messages.append(value)
        errors = []
        for line in (run / "trace.jsonl").read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "error":
                errors.append(event["item"]["message"])
        cases.append({
            "case_id": case, "attempt": "01", "exit_code": receipt["exit_code"],
            "elapsed_seconds": receipt["elapsed_seconds"], "failure": receipt["failure"],
            "host_turn_context": obs["host_turn_context"],
            "frozen_d0_sha256": obs["frozen_d0_sha256"],
            "frozen_d0_hash_definition": "UTF-8 of decoded draft text with LF newlines",
            "frozen_d0_raw_file_sha256": sha((run / "work/frozen-d0.txt").read_bytes()),
            "frozen_d0_file_crlf_count": (run / "work/frozen-d0.txt").read_bytes().count(b"\r\n"),
            "final_sha256": obs["final_sha256"],
            "frozen_d0_visible_message_indices_zero_based": body_indices,
            "gate_d0_matches_frozen": final_state.get("d0_sha256") == obs["frozen_d0_sha256"],
            "visible_assistant_message_count": len(messages),
            "visible_non_body_messages_before_d0": body_indices[0] if body_indices else None,
            "repair_json_count": sum("repairs" in item for item in parsed_messages),
            "verdict_json_count": sum("verdict" in item for item in parsed_messages),
            "native_hook_event_envelopes_in_cli_trace": len(obs["native_hook_items"]),
            "exact_native_stop_event_count": None,
            "request_bound_snapshot_observed": request_bound,
            "observed_core_phases": unique(phases),
            "transaction_state_trace": final_state.get("state_trace"),
            "selected": final_state.get("selected"),
            "selection_reason": final_state.get("reason"),
            "detect_count": final_state.get("detect_count"),
            "repair_count": final_state.get("repair_count"),
            "verify_count": final_state.get("verify_count"),
            "repair_agent_call_count_field": final_state.get("repair_agent_call_count"),
            "verdict_agent_call_count_field": final_state.get("verdict_agent_call_count"),
            "terminal_delivery_verified": terminal.get("delivery_verified"),
            "emitted_sha_matches_final": terminal.get("emitted_sha256") == obs["final_sha256"],
            "data_retention_state": terminal.get("data_retention_state"),
            "raw_artifact_delete_failures": terminal.get("raw_artifact_delete_failures"),
            "stop_attempts_field": terminal.get("stop_attempts"),
            "tool_command_count": len(obs["tool_items"]),
            "tool_command_summaries": [{
                "id": item.get("id"), "command": item.get("command"),
                "exit_code": item.get("exit_code"), "status": item.get("status"),
                "aggregated_output_bytes": len(item.get("aggregated_output", "").encode("utf-8")),
            } for item in obs["tool_items"]],
            "cli_error_items": errors,
            "websocket_426_log_observed": "426 Upgrade Required" in (run / "stderr.txt").read_text(encoding="utf-8", errors="replace"),
            "final_equals_frozen": obs["final_sha256"] == obs["frozen_d0_sha256"],
        })
    summary = {
        "schema_version": 1,
        "verdict": "PASS_BOUNDED_NATIVE_LIFECYCLE_WITH_READING_NOISE",
        "product_base": "4fd63ce344fec440bbbbc664a7ebd7934751e04e",
        "cli_version": "0.151.0", "requested_route": "ollama-cloud/glm-5.3-flash",
        "requested_effort": "max", "cli_tasks": 2, "attempts": 2, "companion_files": 64,
        "cases": cases, "upstream_model_identity_observed": False,
        "upstream_request_count": None,
        "native_cross_provider_verification": False,
        "frozen_d0_injection": True, "naturally_generated_erroneous_first_draft": False,
        "full_draft_fact_verified": False,
        "scope": "one explicit ongoing-state error and one correct frozen control",
        "limits": [
            "CLI trace has no separate native Hook event envelopes; request-bound snapshots, successful reads, core transitions and native continuation responses jointly establish this lifecycle.",
            "Same-session same-route repair/verdict are not provider-independent verification.",
            "Control includes six visible progress messages while obtaining file content; it is not a noise-free body-only trial.",
            "Two CLI tasks and visible assistant-message counts are not upstream API-request or Stop-event counts.",
            "Hook-trust warning items and observed WebSocket 426 logs are retained; neither is silently relabeled as a failed writing sample.",
            "Full sessions, homes, configuration, catalog content, cache and login state are not archived.",
        ],
    }
    return artifacts, summary


def scan(artifacts: dict[str, bytes]) -> None:
    matches = []
    for path, raw in artifacts.items():
        text = raw.decode("utf-8", errors="replace")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                matches.append({"path": path, "pattern": name})
    if matches:
        raise RuntimeError("credential-like content requires review; no archive written: " + json.dumps(matches))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    artifacts, summary = gather()
    scan(artifacts)
    summary["credential_pattern_scan"] = {"files": len(artifacts), "hits": 0,
                                          "limit": "bounded pattern scan, not a universal secret detector"}
    if args.summary_only:
        target = TRANSFER / "summary.json"
        target.write_bytes(encoded(summary))
        print(json.dumps({"summary": str(target), "archive_files_planned": len(artifacts)}))
        return
    if Path(__file__).resolve().parent != HERE.resolve():
        raise RuntimeError("copy archive.py to the exact F evidence directory before archival")
    for relative, raw in artifacts.items():
        target = HERE / relative
        if not target.resolve().is_relative_to((HERE / "raw").resolve()):
            raise RuntimeError("archive target escaped raw/")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != raw:
            raise RuntimeError("refusing to overwrite different archived evidence")
        target.write_bytes(raw)
    (HERE / "summary.json").write_bytes(encoded(summary))
    manifest = [{"path": name, "sha256": sha(raw), "bytes": len(raw)}
                for name, raw in sorted(artifacts.items())]
    (HERE / "archive-manifest.json").write_bytes(encoded(manifest))
    print(json.dumps({"archived_files": len(manifest), "credential_scan_hits": 0,
                      "summary": str(HERE / "summary.json")}))


if __name__ == "__main__":
    main()
