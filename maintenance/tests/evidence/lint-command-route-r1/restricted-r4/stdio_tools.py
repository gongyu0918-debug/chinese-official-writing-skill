"""Two closed stdio MCP tools for a frozen writing experiment; no generic execution."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import threading
from pathlib import Path

from mcp.server.mcpserver import MCPServer


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FrozenTools:
    def __init__(self, manifest: Path, log: Path):
        self.fixture = json.loads(manifest.read_text(encoding="utf-8"))
        self.documents = {}
        for identity, item in self.fixture["documents"].items():
            data = Path(item["path"]).read_bytes()
            if digest(data) != item["sha256"]:
                raise ValueError("frozen document hash mismatch")
            self.documents[identity] = data.decode("utf-8")
        self.script = Path(self.fixture["script"])
        self.python = Path(self.fixture["python"])
        self.log, self.lock, self.sequence = log, threading.Lock(), 0
        self.verify_program()

    def verify_program(self) -> None:
        if digest(self.script.read_bytes()) != self.fixture["script_sha256"]:
            raise ValueError("fixed lint script changed")
        if digest(self.python.read_bytes()) != self.fixture["python_sha256"]:
            raise ValueError("fixed interpreter changed")

    def record(self, value: dict) -> None:
        with self.lock:
            self.sequence += 1
            with self.log.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps({"sequence": self.sequence, **value}, ensure_ascii=False) + "\n")

    def read_document(self, id: str) -> str:
        if id not in self.documents:
            self.record({"tool": "read_document", "id": id, "status": "REJECTED_UNKNOWN_ID"})
            raise ValueError("Unknown document ID; arbitrary paths and URLs are not accepted")
        text = self.documents[id]
        self.record({"tool": "read_document", "id": id, "status": "OK",
                     "returned_utf8_bytes": len(text.encode("utf-8")), "sha256": digest(text.encode("utf-8"))})
        return text

    def prose_lint(self, args: list[str], text: str = "") -> dict:
        try:
            self.validate_arguments(args, text)
            self.verify_program()
        except ValueError as error:
            self.record({"tool": "prose_lint", "args": args, "text": text,
                         "status": "REJECTED", "reason": str(error)})
            raise
        command = [str(self.python), "-I", "-B", "-X", "utf8", str(self.script), *args]
        completed = subprocess.run(command, input=text, text=True, encoding="utf-8", errors="replace",
                                   capture_output=True, shell=False, timeout=30, cwd=self.script.parent)
        result = {"return_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
        self.record({"tool": "prose_lint", "args": args, "text": text, "status": "EXECUTED",
                     "argv": command, "shell": False, "input_utf8_bytes": len(text.encode("utf-8")),
                     "text_sha256": digest(text.encode("utf-8")), **result})
        return result

    @staticmethod
    def validate_arguments(args: list[str], text: str) -> None:
        if len(args) > 10 or len(text.encode("utf-8")) > 80000:
            raise ValueError("argument or input limit exceeded")
        if args == ["--help"] and not text:
            return
        switches = {"--format", "--structure", "--json"}
        modes = {"generic", "draft-body", "review-only", "gap-note-allowed"}
        seen, position = set(), 0
        while position < len(args):
            token = args[position]
            if token in seen:
                raise ValueError("duplicate argument")
            seen.add(token)
            if token == "--delivery-mode":
                position += 1
                if position >= len(args) or args[position] not in modes:
                    raise ValueError("invalid delivery mode")
            elif token not in switches and token != "-":
                raise ValueError("only enumerated lint flags and stdin '-' are accepted")
            position += 1
        if "-" not in seen:
            raise ValueError("file input is unavailable; use stdin '-' or standalone --help")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    options = parser.parse_args()
    tools = FrozenTools(options.manifest.resolve(), options.log.resolve())
    server = MCPServer("audit", log_level="WARNING")
    server.tool(name="read_document", description="Read one frozen document by ID. Available IDs: "
                + ", ".join(tools.documents))(tools.read_document)
    server.tool(name="prose_lint", description="Run the fixed prose lint program with enumerated arguments and text input. "
                "Supports --help. It cannot open arbitrary files or run other programs.")(tools.prose_lint)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
