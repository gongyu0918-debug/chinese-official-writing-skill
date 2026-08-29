from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parent
CASES_PATH = ROOT / "cases.json"


def load_prompt(case_id: str) -> str:
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case in payload["cases"]:
        if case["id"] == case_id:
            return str(case["prompt"]).strip()
    raise ValueError(f"unknown case: {case_id}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument(
        "--prompt-mode", choices=("stdin", "append", "none"), default="append"
    )
    parser.add_argument("--prompt-prefix", default="")
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command.pop(0)
    if not command:
        parser.error("missing command after --")

    prompt = args.prompt_prefix + load_prompt(args.case_id)
    if args.prompt_mode == "append":
        command.append(prompt)
    stdin_text = prompt if args.prompt_mode == "stdin" else None

    output = Path(args.out).resolve()
    cwd = Path(args.cwd).resolve()
    output.mkdir(parents=True, exist_ok=True)
    cwd.mkdir(parents=True, exist_ok=True)

    environment = dict(os.environ)
    for item in args.env:
        key, separator, value = item.partition("=")
        if not separator or not key:
            parser.error(f"invalid --env value: {item!r}")
        environment[key] = value

    started = time.time()
    timed_out = False
    launch_error = None
    try:
        completed = subprocess.run(
            command,
            input=stdin_text,
            cwd=str(cwd),
            env=environment,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
    except OSError as exc:
        exit_code = 127
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}\n"
        launch_error = type(exc).__name__

    stdout_bytes = stdout.encode("utf-8")
    stderr_bytes = stderr.encode("utf-8")
    (output / "stdout.txt").write_bytes(stdout_bytes)
    (output / "stderr.txt").write_bytes(stderr_bytes)
    receipt = {
        "case_id": args.case_id,
        "command_argv_without_prompt": command[:-1]
        if args.prompt_mode == "append"
        else command,
        "cwd": str(cwd),
        "elapsed_seconds": round(time.time() - started, 3),
        "exit_code": exit_code,
        "launch_error": launch_error,
        "prompt_mode": args.prompt_mode,
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "stderr_sha256": sha256_bytes(stderr_bytes),
        "stdout_sha256": sha256_bytes(stdout_bytes),
        "timed_out": timed_out,
    }
    (output / "receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
