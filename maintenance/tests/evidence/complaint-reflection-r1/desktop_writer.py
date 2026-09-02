from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
UPSTREAM_PATH = HERE.parents[3] / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"


def desktop_codex() -> tuple[Path, str]:
    local_app_data = Path(os.environ["LOCALAPPDATA"])
    binary_root = local_app_data / "OpenAI/Codex/bin"
    candidates = [binary_root / "codex.exe", *binary_root.glob("*/codex.exe")]
    resolved: list[tuple[tuple[int, int, int], Path, str]] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        completed = subprocess.run(
            [str(candidate), "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        version_text = completed.stdout.strip()
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_text)
        if completed.returncode == 0 and match:
            resolved.append((tuple(int(value) for value in match.groups()), candidate, version_text))
    if not resolved:
        fallback = shutil.which("codex")
        if fallback:
            completed = subprocess.run(
                [fallback, "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if completed.returncode == 0:
                return Path(fallback), completed.stdout.strip()
        raise RuntimeError("Codex Desktop CLI was not found")
    _, path, version = max(resolved, key=lambda item: item[0])
    return path, version


def load_writer(repo: Path, cases_path: Path, output_root: Path):
    spec = importlib.util.spec_from_file_location("wr027_upstream_writer", UPSTREAM_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load writer: {UPSTREAM_PATH}")
    writer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(writer)
    writer.REPO = repo
    writer.CASES_PATH = cases_path
    writer.OUTPUT_ROOT = output_root

    def run_one(provider_id: str, model: str, arm: str, case: dict, effort: str) -> dict:
        root = writer.runtime_root(provider_id, arm)
        raw = output_root / "raw" / provider_id
        raw.mkdir(parents=True, exist_ok=True)
        stem = f"{case['id']}-{arm}"
        final_path = raw / f"{stem}.final.txt"
        trace_path = raw / f"{stem}.trace.jsonl"
        stderr_path = raw / f"{stem}.stderr.txt"
        codex_path, codex_version = desktop_codex()
        command = [
            str(codex_path),
            "exec",
            "--skip-git-repo-check",
            "-C",
            str(root),
            "-m",
            model,
            "-c",
            "features.plugins=false",
            "-c",
            "features.apps=false",
            "-c",
            "features.memories=false",
            "-c",
            writer.disabled_skills_config(),
            "-c",
            'openai_base_url="http://127.0.0.1:10100/v1"',
            "-c",
            f'model_catalog_json="{writer.CATALOG.as_posix()}"',
            "-c",
            f'model_reasoning_effort="{effort}"',
            "-c",
            'approval_policy="never"',
            "-s",
            "read-only",
            "--ephemeral",
            "--json",
            "--output-last-message",
            str(final_path),
            "-",
        ]
        print(f"START {provider_id} {case['id']} {arm}", flush=True)
        started = time.monotonic()
        error = None
        try:
            completed = subprocess.run(
                command,
                input=case["prompt"],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=900,
                check=False,
            )
            return_code = completed.returncode
            stdout, stderr = completed.stdout, completed.stderr
        except subprocess.TimeoutExpired as exc:
            return_code = None
            stdout, stderr = str(exc.stdout or ""), str(exc.stderr or "")
            error = "timeout_after_900_seconds"

        trace_path.write_text(stdout, encoding="utf-8", newline="\n")
        stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
        final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
        commands = writer.normalized_commands(stdout)
        exact_skill = (root / ".agents/skills/chinese-official-writing/SKILL.md").as_posix().casefold()
        relative_skill = ".agents/skills/chinese-official-writing/skill.md"
        exact_seen = exact_skill in commands or relative_skill in commands
        global_seen = [path.as_posix() for path in writer.USER_SKILLS if path.as_posix().casefold() in commands]
        combined_log = f"{stdout}\n{stderr}".casefold()
        hook_markers = [
            marker
            for marker in (
                "<hook_prompt",
                "chinese-official-writing@chinese-official-writing-local:hooks/",
                "official-writing-pro@official-writing-pro-local:hooks/",
            )
            if marker in combined_log
        ]
        technical = []
        if return_code != 0:
            technical.append("nonzero_exit")
        if error:
            technical.append(error)
        if not final.strip():
            technical.append("missing_final")
        if not exact_seen:
            technical.append("missing_exact_skill_trace")
        if global_seen:
            technical.append("user_skill_contamination")
        if hook_markers:
            technical.append("hook_contamination")
        body_chars = len(writer.compact(final))
        prompt_chars = len(writer.compact(case["prompt"]))
        material_chars = len(writer.compact(case["material"]))
        return {
            "provider_id": provider_id,
            "model": model,
            "case_id": case["id"],
            "arm": arm,
            "return_code": return_code,
            "seconds": round(time.monotonic() - started, 3),
            "codex_path": str(codex_path),
            "codex_version": codex_version,
            "exact_skill_trace": exact_seen,
            "user_skill_paths_in_trace": global_seen,
            "hook_contamination_markers": hook_markers,
            "technical_failures": technical,
            "hard_failures": [] if technical else writer.hard_failures(case, final),
            "prompt_chars_nonspace": prompt_chars,
            "material_chars_nonspace": material_chars,
            "final_chars_nonspace": body_chars,
            "shorter_than_prompt": body_chars < prompt_chars,
            "shorter_than_material": body_chars < material_chars,
            "quality_markers_present": [marker for marker in case["quality_markers"] if marker in final],
            "usage": writer.trace_usage(stdout),
            "final_sha256": writer.sha256_bytes(final.encode("utf-8")) if final else None,
            "final_file": str(final_path.relative_to(output_root)),
            "trace_file": str(trace_path.relative_to(output_root)),
            "stderr_file": str(stderr_path.relative_to(output_root)),
        }

    writer.run_one = run_one
    return writer
