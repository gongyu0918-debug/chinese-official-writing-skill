from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "cases.json"
OUTPUT = ROOT / "output" / "v168-overlength-shortdraft-real-first" / "formal-r1"
TIMEOUT_SECONDS = 1200
BASE_HARNESS = (
    ROOT
    / "maintenance/tests/evidence/v167-formulaic-mechanicality-real-first/harness.py"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("v167_formulaic_harness", BASE_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the existing isolated model runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def non_whitespace_chars(value: str) -> int:
    return sum(not char.isspace() for char in value)


def read_files(case: dict[str, Any]) -> list[Path]:
    mode = case["mode"]
    if mode == "overlength":
        return [HERE / "prototype-overlength.md"]
    if mode == "shortdraft":
        return [
            ROOT / "chinese-official-writing/SKILL.md",
            ROOT / "chinese-official-writing/references/information-selection.md",
            ROOT / "chinese-official-writing/references/short-draft-naturalness.md",
            HERE / "prototype-shortdraft.md",
        ]
    if mode in {"readme", "readme-r2"}:
        paths = [
            ROOT / "chinese-official-writing/SKILL.md",
            ROOT / "chinese-official-writing/references/information-selection.md",
            ROOT / "chinese-official-writing/references/genre-playbook-institution-rules.md",
            ROOT / "chinese-official-writing/references/official-style.md",
        ]
        if mode == "readme-r2":
            paths.append(HERE / "prototype-institution.md")
        return paths
    raise ValueError(f"Unknown mode: {mode}")


def system_prompt(case: dict[str, Any]) -> str:
    paths = read_files(case)
    listed = "\n".join(f"- {path.resolve()}" for path in paths)
    return (
        "你是独立的中文正式材料写稿 Agent。先用 Read 工具逐一读取下列文件，"
        "只允许读取这些文件，不得读取其他 Skill、维护记录、测试证据或用户目录，"
        "不得联网、创建文件或运行命令：\n"
        f"{listed}\n"
        "按用户题面输出可直接使用的完整正文，不说明读取、推理、压缩、复核或测试过程。"
    )


def command(claude: str, model: str, prompt: str) -> list[str]:
    return [
        claude,
        "--setting-sources",
        "",
        "--no-session-persistence",
        "--tools",
        "Read",
        "--add-dir",
        str(ROOT),
        "--append-system-prompt",
        prompt,
        "--print",
        "--verbose",
        "--output-format",
        "stream-json",
        "--model",
        model,
        "--effort",
        "max",
    ]


def run_case(
    claude: str,
    models: dict[str, str],
    case: dict[str, Any],
) -> dict[str, Any]:
    case_id = str(case["id"])
    case_output = OUTPUT / "raw" / case_id
    case_runtime = OUTPUT / "runtime" / case_id
    case_output.mkdir(parents=True, exist_ok=False)
    case_runtime.mkdir(parents=True, exist_ok=False)
    model = models[case["provider"]]
    prompt = system_prompt(case)
    environment = BASE.build_environment(model, case_runtime)
    work = case_runtime / "work"
    stream = case_runtime / "stream.jsonl"
    stderr = case_runtime / "stderr.txt"
    started = time.monotonic()
    return_code = -1
    timed_out = False
    error = None
    with stream.open("w", encoding="utf-8", newline="\n") as out, stderr.open(
        "w", encoding="utf-8", newline="\n"
    ) as err:
        try:
            completed = subprocess.run(
                command(claude, model, prompt),
                cwd=work,
                env=environment,
                input=str(case["request"]),
                stdout=out,
                stderr=err,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
            return_code = completed.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            error = repr(exc)
        except OSError as exc:
            error = repr(exc)
    parsed = BASE.parse_stream(stream)
    final = parsed.pop("final")
    allowed = {path.resolve() for path in read_files(case)}
    resolved_reads = {
        Path(value).resolve()
        for value in parsed["reads"]
        if isinstance(value, str) and Path(value).is_absolute()
    }
    checks = {
        "return_code_zero": return_code == 0,
        "not_timed_out": not timed_out,
        "single_success": parsed["result_count"] == 1
        and parsed["result_subtypes"] == ["success"]
        and parsed["result_errors"] == [False],
        "final_nonempty": bool(final.strip()),
        "model_bound": parsed["init_models"] == [model]
        and parsed["assistant_models"] == [model]
        and parsed["usage_models"] == [model],
        "no_plugins": not parsed["plugins"],
        "all_required_read": allowed.issubset(resolved_reads),
        "no_extra_read": resolved_reads.issubset(allowed),
        "valid_stream": not parsed["invalid_json_lines"],
    }
    metadata = {
        "id": case_id,
        "mode": case["mode"],
        "provider": case["provider"],
        "model": model,
        "effort": "max",
        "timeout_seconds": TIMEOUT_SECONDS,
        "retry_count": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "return_code": return_code,
        "timed_out": timed_out,
        "error": error,
        "request_sha256": sha256_text(str(case["request"])),
        "system_sha256": sha256_text(prompt),
        "final_sha256": sha256_text(final),
        "non_whitespace_chars": non_whitespace_chars(final),
        "upper": case.get("upper"),
        "lower": case.get("lower"),
        "reads": sorted(str(path) for path in resolved_reads),
        "checks": checks,
        "technical_valid": all(checks.values()),
    }
    BASE.atomic_text(case_output / "final.txt", final)
    BASE.atomic_json(case_output / "meta.json", metadata)
    shutil.copyfile(stderr, case_output / "stderr.txt")
    return metadata


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to reuse output: {OUTPUT}")
    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable not found")
    OUTPUT.mkdir(parents=True)
    cases = payload["cases"]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        grouped.setdefault(case["provider"], []).append(case)

    def lane(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [run_case(claude, payload["models"], case) for case in items]

    records: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(grouped)) as pool:
        futures = [pool.submit(lane, items) for items in grouped.values()]
        for future in concurrent.futures.as_completed(futures):
            records.extend(future.result())
    records.sort(key=lambda item: item["id"])
    manifest = {
        "schema_version": 1,
        "cases_sha256": hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(),
        "calls": len(records),
        "technical_valid": sum(bool(item["technical_valid"]) for item in records),
        "records": records,
    }
    BASE.atomic_json(OUTPUT / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["technical_valid"] == len(records) else 2


if __name__ == "__main__":
    raise SystemExit(main())
