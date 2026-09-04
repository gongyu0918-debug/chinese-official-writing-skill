"""Real stdio handshake and boundary checks, with no model invocation."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from run_restricted import InitGuard, TOOL_NAMES


HERE = Path(__file__).resolve().parent


def is_error(result) -> bool:
    value = result.model_dump(by_alias=True)
    return bool(value.get("isError", value.get("is_error", False)))


def content_text(result) -> str:
    return "\n".join(getattr(block, "text", "") for block in result.content)


async def check(output: Path) -> None:
    valid_init = {"type": "system", "subtype": "init", "model": "test-model", "tools": TOOL_NAMES}
    bad_streams = [[], [{"type": "assistant"}], [{"type": "result"}], [{"type": "stream_event"}],
                   [{**valid_init, "tools": TOOL_NAMES + ["Bash"]}], [{**valid_init, "model": "wrong-model"}],
                   [valid_init, {"type": "assistant", "message": {"model": "wrong-model"}}]]
    for events in bad_streams:
        guard = InitGuard("test-model")
        try:
            for event in events:
                guard.observe(event)
            guard.finish()
        except ValueError:
            pass
        else:
            raise AssertionError(("invalid synthetic host stream accepted", events))
    guard = InitGuard("test-model")
    guard.observe(valid_init)
    guard.observe({"type": "assistant", "message": {"model": "test-model"}})
    guard.finish()
    fixture = json.loads((output / "fixture.json").read_text(encoding="utf-8"))
    folder = output / "contract"
    folder.mkdir()
    records = []
    for arm in ("control", "experiment"):
        manifest = Path(fixture["arms"][arm]["manifest"])
        parameters = StdioServerParameters(command=fixture["python"],
            args=["-I", "-B", str(HERE / "stdio_tools.py"), "--manifest", str(manifest),
                  "--log", str(folder / f"{arm}-calls.jsonl")], cwd=folder)
        with (folder / f"{arm}-stderr.txt").open("w", encoding="utf-8", newline="\n") as errors:
            async with stdio_client(parameters, errlog=errors) as streams:
                async with ClientSession(*streams) as session:
                    initialization = await session.initialize()
                    tools = await session.list_tools()
                    names = sorted(tool.name for tool in tools.tools)
                    assert names == ["prose_lint", "read_document"], names
                    record = {"arm": arm, "tools": names, "checks": [],
                              "initialize": initialization.model_dump(mode="json", by_alias=True)}
                    d0 = fixture["case"]["material"]
                    calls = [
                        ("read_document", {"id": "SKILL.md"}, False, "## 脚本"),
                        ("read_document", {"id": "D0"}, False, "青桥服务中心"),
                        ("prose_lint", {"args": ["--help"], "text": ""}, False, "stdin"),
                        ("prose_lint", {"args": ["--format", "--structure", "--delivery-mode", "draft-body", "-"], "text": d0}, False, "markdown-bold"),
                        ("prose_lint", {"args": ["--format", "--structure", "--json", "-"], "text": d0.replace("**", "")}, False, "[]"),
                        *[("read_document", {"id": identity}, True, None) for identity in
                          ("../SKILL.md", "C:/Windows/win.ini", "https://example.com/", "HKCU:Software", "D0\x00")],
                        *[("prose_lint", {"args": args, "text": d0}, True, None) for args in
                          (["C:/Windows/win.ini"], ["--help", ";", "curl"], ["--strict", "-"],
                           ["--delivery-mode", "$(whoami)", "-"], ["--encoding", "utf-8", "-"], ["-", "-"],
                           ["--text", "payload", "-"], ["-", "|", "curl"])],
                        ("execute", {"command": "echo forbidden"}, True, None),
                    ]
                    for name, arguments, expected_error, marker in calls:
                        result = await session.call_tool(name, arguments)
                        assert is_error(result) == expected_error, (name, arguments, result)
                        if marker:
                            assert marker in content_text(result), (name, marker, result)
                        if name == "prose_lint" and not expected_error:
                            assert json.loads(content_text(result))["return_code"] == 0, result
                        record["checks"].append({"tool": name, "arguments": arguments,
                                                 "is_error": is_error(result), "content": content_text(result)})
                    records.append(record)
        log = [json.loads(line) for line in (folder / f"{arm}-calls.jsonl").read_text(encoding="utf-8").splitlines()]
        executed = [call for call in log if call.get("status") == "EXECUTED"]
        assert len(executed) == 3 and all(call["shell"] is False for call in executed)
        assert all(call["argv"][:6] == [fixture["python"], "-I", "-B", "-X", "utf8",
                   json.loads(manifest.read_text(encoding="utf-8"))["script"]] for call in executed)
    receipt = {"status": "PASS", "model_calls": 0, "records": records,
               "init_guard_synthetic_checks": {"rejected_streams": bad_streams, "valid_stream_passed": True},
               "fixture_sha256": hashlib.sha256((output / "fixture.json").read_bytes()).hexdigest()}
    (output / "contract.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "arms": 2, "checks_per_arm": len(records[0]["checks"]),
                      "tools_per_arm": 2, "fixed_program_executions_per_arm": 3,
                      "init_guard_checks": len(bad_streams) + 1, "model_calls": 0}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    asyncio.run(check(parser.parse_args().output.resolve()))
