#!/usr/bin/env python3
"""Run Promptfoo official-writing ablation and summarize release metrics."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import textwrap
from typing import Any


EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parents[1]
OUTPUT_DIR = REPO_ROOT / "output" / "promptfoo"
CONFIG_PATH = EVAL_DIR / "promptfooconfig.yaml"
RUBRIC_PATH = EVAL_DIR / "rubrics" / "pairwise-judge.md"
DATASET_PATH = EVAL_DIR / "datasets" / "cases.jsonl"
GRADER_PATH = EVAL_DIR / "graders" / "official_writing_rubric.py"
PROVIDER_PATH = EVAL_DIR / "providers" / "agent_writer.py"
FULL_NEEDS_MANUAL_REVIEW_RATE_MAX = 0.02
SKILL_HARD_RULE_PASS_RATE_MIN = 0.98
SKILL_PLACEHOLDER_RISK_RATE_MAX = 0.0
SKILL_WIN_OR_TIE_RATE_MIN = 0.90
THRESHOLD_ENV_VARS = {
    "needs_manual_review": "OFFICIAL_WRITING_FULL_NEEDS_MANUAL_REVIEW_RATE_MAX",
    "hard_rule_pass": "OFFICIAL_WRITING_SKILL_HARD_RULE_PASS_RATE_MIN",
    "placeholder_risk": "OFFICIAL_WRITING_SKILL_PLACEHOLDER_RISK_RATE_MAX",
    "win_or_tie": "OFFICIAL_WRITING_SKILL_WIN_OR_TIE_RATE_MIN",
}


class EvalError(RuntimeError):
    pass


def threshold_from_env(env_name: str, default: float) -> float:
    value = os.environ.get(env_name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise EvalError(f"{env_name} must be a float, got {value!r}") from exc


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


grader = _load_module("official_writing_eval_grader", GRADER_PATH)
agent_writer = _load_module("official_writing_agent_writer", PROVIDER_PATH)


def load_cases(limit: int | None = None) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for line in DATASET_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        cases.append(item)
    if limit is not None:
        return cases[:limit]
    return cases


def case_vars(case: dict[str, Any]) -> dict[str, Any]:
    return case.get("vars") or {}


def case_id(case: dict[str, Any]) -> str:
    return str(case_vars(case).get("case_id", "")).strip()


def command_name(name: str) -> str:
    if os.name == "nt":
        found = shutil.which(f"{name}.cmd") or shutil.which(f"{name}.exe") or shutil.which(name)
    else:
        found = shutil.which(name)
    if not found:
        raise EvalError(f"cannot find command: {name}")
    return found


def run_promptfoo(suite: str, limit: int | None) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_out = OUTPUT_DIR / f"official-writing-{suite}-promptfoo.json"
    html_out = OUTPUT_DIR / f"official-writing-{suite}-promptfoo.html"
    npx = command_name("npx")
    cmd = [
        npx,
        "promptfoo",
        "eval",
        "-c",
        str(CONFIG_PATH),
        "-o",
        str(json_out),
        "-o",
        str(html_out),
        "--no-share",
        "--max-concurrency",
        "1",
        "--no-cache",
        "--no-progress-bar",
    ]
    if limit is not None:
        cmd.extend(["--filter-first-n", str(limit)])

    env = os.environ.copy()
    env["PROMPTFOO_PYTHON"] = sys.executable
    env["PROMPTFOO_CONFIG_DIR"] = str(REPO_ROOT / ".promptfoo")
    env["PROMPTFOO_LOG_DIR"] = str(REPO_ROOT / ".promptfoo" / "logs")
    env["PROMPTFOO_DISABLE_WAL_MODE"] = "true"
    env["IS_TESTING"] = "true"
    env["REQUEST_TIMEOUT_MS"] = env.get("REQUEST_TIMEOUT_MS", "3600000")
    env["OFFICIAL_WRITING_EVAL_SUITE"] = suite
    if limit is not None:
        env["OFFICIAL_WRITING_EVAL_LIMIT"] = str(limit)
    else:
        env.pop("OFFICIAL_WRITING_EVAL_LIMIT", None)

    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if result.returncode != 0:
        raise EvalError(f"promptfoo eval failed with exit code {result.returncode}")
    if not json_out.exists():
        raise EvalError(f"promptfoo did not write JSON output: {json_out}")
    return json_out, html_out


def _records_from_payload(payload: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[int] = set()

    def walk(obj: Any) -> None:
        if id(obj) in seen:
            return
        seen.add(id(obj))
        if isinstance(obj, list):
            if obj and all(isinstance(item, dict) for item in obj):
                for item in obj:
                    if "response" in item and ("vars" in item or "testCase" in item or "metadata" in item):
                        found.append(item)
            for item in obj:
                walk(item)
        elif isinstance(obj, dict):
            for value in obj.values():
                walk(value)

    walk(payload)

    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in found:
        output = output_text(record)
        vars_ = record_vars(record)
        metadata = record_metadata(record)
        cid = str(metadata.get("case_id") or vars_.get("case_id") or "")
        mode = str(metadata.get("mode") or provider_mode(record) or "")
        key = (cid, mode, hashlib.sha256(output.encode("utf-8")).hexdigest())
        unique[key] = record
    return list(unique.values())


def record_vars(record: dict[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("vars"), dict):
        return record["vars"]
    test_case = record.get("testCase") or record.get("test") or {}
    if isinstance(test_case, dict) and isinstance(test_case.get("vars"), dict):
        return test_case["vars"]
    return {}


def record_metadata(record: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    if isinstance(record.get("metadata"), dict):
        metadata.update(record["metadata"])
    response = record.get("response") or {}
    if isinstance(response, dict) and isinstance(response.get("metadata"), dict):
        metadata.update(response["metadata"])
    return metadata


def provider_mode(record: dict[str, Any]) -> str:
    provider = record.get("provider") or record.get("providerLabel") or ""
    provider_text = ""
    if isinstance(provider, dict):
        provider_text = " ".join(str(provider.get(key, "")) for key in ("label", "id"))
    else:
        provider_text = str(provider)
    if "skill" in provider_text.lower():
        return "skill"
    if "baseline" in provider_text.lower():
        return "baseline"
    return ""


def output_text(record: dict[str, Any]) -> str:
    if isinstance(record.get("text"), str):
        return record["text"]
    response = record.get("response") or {}
    if isinstance(response, dict):
        output = response.get("output")
        if isinstance(output, str):
            return output
        if output is not None:
            return json.dumps(output, ensure_ascii=False)
    output = record.get("output")
    if isinstance(output, str):
        return output
    return ""


def load_promptfoo_outputs(path: Path, cases: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = _records_from_payload(payload)
    outputs: dict[str, dict[str, dict[str, Any]]] = {}
    known_cases = {case_id(case): case for case in cases}
    for record in records:
        text = output_text(record).strip()
        vars_ = record_vars(record)
        metadata = record_metadata(record)
        cid = str(metadata.get("case_id") or vars_.get("case_id") or "").strip()
        mode = str(metadata.get("mode") or provider_mode(record)).strip()
        if cid not in known_cases or mode not in {"baseline", "skill"}:
            continue
        outputs.setdefault(cid, {})[mode] = {
            "text": text,
            "vars": vars_ or case_vars(known_cases[cid]),
            "metadata": metadata,
            "latencyMs": int(record.get("latencyMs") or 0),
            "cost": float(record.get("cost") or 0.0),
            "promptfoo_pass": bool(record.get("success", record.get("pass", False))),
            "promptfoo_score": float(record.get("score") or 0.0),
        }
    return outputs


def normalize_judge_json(raw: str) -> Any:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    if text.startswith("{") or text.startswith("["):
        return json.loads(text)
    array_start = text.find("[")
    array_end = text.rfind("]")
    if array_start != -1 and array_end > array_start:
        return json.loads(text[array_start : array_end + 1])
    object_start = text.find("{")
    object_end = text.rfind("}")
    if object_start != -1 and object_end > object_start:
        return json.loads(text[object_start : object_end + 1])
    raise ValueError("judge output did not contain JSON")


def randomized_pair(case: dict[str, Any], pair: dict[str, dict[str, Any]], repeat_index: int) -> dict[str, Any]:
    seed = int(hashlib.sha256(f"{case_id(case)}:{repeat_index}:official-writing".encode("utf-8")).hexdigest()[:8], 16)
    skill_as_a = random.Random(seed).choice([True, False])
    if repeat_index % 2 == 1:
        skill_as_a = not skill_as_a
    a_mode = "skill" if skill_as_a else "baseline"
    b_mode = "baseline" if skill_as_a else "skill"
    return {
        "case_id": case_id(case),
        "genre": case_vars(case).get("genre", ""),
        "scenario": case_vars(case).get("scenario", ""),
        "task": case_vars(case).get("task", ""),
        "A": pair[a_mode]["text"],
        "B": pair[b_mode]["text"],
        "label_map": {"A": a_mode, "B": b_mode},
    }


def judge_cache_path(suite: str, repeat_index: int, judge_cases: list[dict[str, Any]]) -> Path:
    digest_payload = [
        {"case_id": item["case_id"], "A": item["A"], "B": item["B"], "label_map": item["label_map"]}
        for item in judge_cases
    ]
    digest_payload.append({"stub": agent_writer.use_stub({})})
    digest = hashlib.sha256(json.dumps(digest_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:20]
    return OUTPUT_DIR / "cache" / f"judge-{suite}-r{repeat_index + 1}-{digest}.json"


def stub_judge(judge_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in judge_cases:
        score_a = grader.score_text(item["A"], {"genre": item["genre"], "case_id": item["case_id"]})["score"]
        score_b = grader.score_text(item["B"], {"genre": item["genre"], "case_id": item["case_id"]})["score"]
        if abs(score_a - score_b) < 0.03:
            winner = "tie"
        else:
            winner = "A" if score_a > score_b else "B"
        rows.append(
            {
                "case_id": item["case_id"],
                "winner": winner,
                "scores": {
                    "genre_fit": 4,
                    "viewpoint": 4,
                    "handling_elements": 4,
                    "argument_chain": 4,
                    "official_tone": 4,
                    "low_ai_flavor": 4,
                    "factual_restraint": 4,
                    "editable_first_draft_value": 4,
                },
                "reasons": ["stub judge compares deterministic rubric scores"],
                "uncertainty": "low",
                "rule_failures": [],
            }
        )
    return rows


def call_judge_batch(suite: str, repeat_index: int, judge_cases: list[dict[str, Any]], timeout_seconds: int) -> list[dict[str, Any]]:
    cache_path = judge_cache_path(suite, repeat_index, judge_cases)
    if cache_path.exists() and not os.environ.get("OFFICIAL_WRITING_EVAL_REFRESH"):
        return json.loads(cache_path.read_text(encoding="utf-8"))
    if agent_writer.use_stub({}):
        rows = stub_judge(judge_cases)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        return rows

    rubric = RUBRIC_PATH.read_text(encoding="utf-8")
    cases_payload = [
        {
            "case_id": item["case_id"],
            "genre": item["genre"],
            "scenario": item["scenario"],
            "task": item["task"],
            "candidate_A": item["A"],
            "candidate_B": item["B"],
        }
        for item in judge_cases
    ]
    prompt = textwrap.dedent(
        f"""
        {rubric}

        Evaluate every case in this JSON array. Return a JSON array with one result object per case_id.
        Do not omit any case_id.

        Cases:
        {json.dumps(cases_payload, ensure_ascii=False, indent=2)}
        """
    ).strip()
    raw, code, _chars = agent_writer.call_model_prompt(prompt, REPO_ROOT, timeout_seconds, retries=1)
    if code != 0 and not raw.strip():
        raise EvalError(f"judge returned code {code} with empty output")
    parsed = normalize_judge_json(raw)
    rows = parsed.get("results", parsed) if isinstance(parsed, dict) else parsed
    if not isinstance(rows, list):
        raise EvalError("judge JSON must be a list")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


def normalize_winner(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"a", "candidate_a", "candidate a", "output_a", "output a"}:
        return "A"
    if text in {"b", "candidate_b", "candidate b", "output_b", "output b"}:
        return "B"
    if text in {"tie", "draw", "平局", "并列", "相当"}:
        return "tie"
    return "invalid"


def judge_chunked(
    suite: str,
    cases: list[dict[str, Any]],
    outputs: dict[str, dict[str, dict[str, Any]]],
    repeats: int,
    batch_size: int,
    timeout_seconds: int,
) -> dict[str, list[dict[str, Any]]]:
    all_results: dict[str, list[dict[str, Any]]] = {case_id(case): [] for case in cases}

    def run_chunk(repeat_index: int, chunk: list[dict[str, Any]]) -> list[dict[str, Any]]:
        judge_cases = [randomized_pair(case, outputs[case_id(case)], repeat_index) for case in chunk]
        ids = ",".join(item["case_id"] for item in judge_cases)
        print(f"judge repeat={repeat_index + 1} cases={ids}", flush=True)
        try:
            rows = call_judge_batch(suite, repeat_index, judge_cases, timeout_seconds)
            by_case = {str(row.get("case_id", "")).strip(): row for row in rows if isinstance(row, dict)}
            missing = [item["case_id"] for item in judge_cases if item["case_id"] not in by_case]
            if missing:
                raise EvalError(f"judge omitted case ids: {', '.join(missing)}")
            normalized: list[dict[str, Any]] = []
            for item in judge_cases:
                row = by_case[item["case_id"]]
                winner = normalize_winner(row.get("winner"))
                mapped = item["label_map"].get(winner, "tie" if winner == "tie" else "invalid")
                row = dict(row)
                row["winner_display"] = winner
                row["winner_mapped"] = mapped
                row["label_map"] = item["label_map"]
                row["repeat_index"] = repeat_index
                normalized.append(row)
            return normalized
        except Exception:
            if len(chunk) == 1:
                raise
            mid = len(chunk) // 2
            return run_chunk(repeat_index, chunk[:mid]) + run_chunk(repeat_index, chunk[mid:])

    for repeat_index in range(repeats):
        for start in range(0, len(cases), batch_size):
            chunk = cases[start : start + batch_size]
            for row in run_chunk(repeat_index, chunk):
                all_results[str(row.get("case_id"))].append(row)
    return all_results


def summarize(
    suite: str,
    cases: list[dict[str, Any]],
    outputs: dict[str, dict[str, dict[str, Any]]],
    judge_results: dict[str, list[dict[str, Any]]],
    promptfoo_json: Path,
    promptfoo_html: Path,
) -> dict[str, Any]:
    missing_outputs: list[str] = []
    case_rows: list[dict[str, Any]] = []
    pairwise_counts = {"skill": 0, "baseline": 0, "tie": 0, "invalid": 0, "needs_manual_review": 0}
    deterministic_by_mode = {
        "baseline": {"hard_pass": 0, "assert_pass": 0, "placeholder_risk": 0, "lint_risk": 0, "latency": 0, "cost": 0.0},
        "skill": {"hard_pass": 0, "assert_pass": 0, "placeholder_risk": 0, "lint_risk": 0, "latency": 0, "cost": 0.0},
    }
    lint_drop = 0

    for case in cases:
        cid = case_id(case)
        pair = outputs.get(cid, {})
        if not pair.get("baseline", {}).get("text") or not pair.get("skill", {}).get("text"):
            missing_outputs.append(cid)
            pairwise_counts["invalid"] += 1
            continue

        scored: dict[str, Any] = {}
        for mode in ("baseline", "skill"):
            result = grader.score_text(pair[mode]["text"], case_vars(case))
            scored[mode] = result
            deterministic_by_mode[mode]["hard_pass"] += int(result["hard_rule_pass"])
            deterministic_by_mode[mode]["assert_pass"] += int(result["pass"])
            deterministic_by_mode[mode]["placeholder_risk"] += int(result["placeholder_echo_count"] > 0)
            deterministic_by_mode[mode]["lint_risk"] += int(result["lint"]["risk_weight"])
            deterministic_by_mode[mode]["latency"] += int(pair[mode].get("latencyMs") or 0)
            deterministic_by_mode[mode]["cost"] += float(pair[mode].get("cost") or 0.0)

        if scored["skill"]["lint"]["risk_weight"] < scored["baseline"]["lint"]["risk_weight"]:
            lint_drop += 1

        judges = judge_results.get(cid, [])
        valid_winners = [row.get("winner_mapped") for row in judges if row.get("winner_mapped") in {"skill", "baseline", "tie"}]
        invalid_judges = len(judges) != len(valid_winners)
        if invalid_judges or not judges:
            final_winner = "invalid"
        elif len(set(valid_winners)) > 1:
            final_winner = "needs_manual_review"
        else:
            final_winner = valid_winners[0]
        pairwise_counts[final_winner] += 1

        case_rows.append(
            {
                "case_id": cid,
                "genre": case_vars(case).get("genre"),
                "scenario": case_vars(case).get("scenario"),
                "final_winner": final_winner,
                "deterministic": scored,
                "judge_results": judges,
            }
        )

    case_count = len(cases)
    metrics_by_mode: dict[str, Any] = {}
    for mode, item in deterministic_by_mode.items():
        metrics_by_mode[mode] = {
            "hard_rule_pass_rate": round(item["hard_pass"] / case_count, 4) if case_count else 0,
            "deterministic_assert_pass_rate": round(item["assert_pass"] / case_count, 4) if case_count else 0,
            "placeholder_risk_rate": round(item["placeholder_risk"] / case_count, 4) if case_count else 0,
            "avg_lint_risk_weight": round(item["lint_risk"] / case_count, 4) if case_count else 0,
            "avg_latency_ms": round(item["latency"] / case_count, 2) if case_count else 0,
            "estimated_cost_usd": round(item["cost"], 6),
        }

    valid_pairwise = case_count - pairwise_counts["invalid"]
    consistent = valid_pairwise - pairwise_counts["needs_manual_review"]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suite": suite,
        "case_count": case_count,
        "promptfoo": {
            "config": str(CONFIG_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "json_output": str(promptfoo_json.relative_to(REPO_ROOT)).replace("\\", "/"),
            "html_output": str(promptfoo_html.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "pairwise": {
            "counts": pairwise_counts,
            "skill_win_rate": round(pairwise_counts["skill"] / case_count, 4) if case_count else 0,
            "baseline_win_rate": round(pairwise_counts["baseline"] / case_count, 4) if case_count else 0,
            "tie_rate": round(pairwise_counts["tie"] / case_count, 4) if case_count else 0,
            "invalid_rate": round(pairwise_counts["invalid"] / case_count, 4) if case_count else 0,
            "needs_manual_review_rate": round(pairwise_counts["needs_manual_review"] / case_count, 4) if case_count else 0,
            "judge_consistency_rate": round(consistent / valid_pairwise, 4) if valid_pairwise else 0,
        },
        "deterministic": {
            "by_mode": metrics_by_mode,
            "lint_risk_drop_rate": round(lint_drop / case_count, 4) if case_count else 0,
            "missing_output_cases": missing_outputs,
        },
        "cases": case_rows,
    }
    return summary


def write_summary(suite: str, summary: dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if suite == "full":
        out_path = OUTPUT_DIR / "official-writing-results.json"
    else:
        out_path = OUTPUT_DIR / f"official-writing-{suite}-results.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = OUTPUT_DIR / "official-writing-latest-results.json"
    latest.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def enforce_failure_policy(summary: dict[str, Any]) -> None:
    suite = summary["suite"]
    counts = summary["pairwise"]["counts"]
    missing = summary["deterministic"]["missing_output_cases"]
    if missing:
        raise EvalError(f"missing provider outputs: {', '.join(missing[:10])}")
    if counts["invalid"]:
        raise EvalError(f"invalid pairwise judge cases: {counts['invalid']}")
    manual_rate = summary["pairwise"]["needs_manual_review_rate"]
    threshold = (
        threshold_from_env(THRESHOLD_ENV_VARS["needs_manual_review"], FULL_NEEDS_MANUAL_REVIEW_RATE_MAX)
        if suite == "full"
        else 1.0
    )
    if manual_rate > threshold:
        raise EvalError(f"needs_manual_review rate {manual_rate:.2%} exceeds threshold {threshold:.2%}")
    skill_metrics = summary["deterministic"]["by_mode"].get("skill", {})
    baseline_metrics = summary["deterministic"]["by_mode"].get("baseline", {})
    hard_threshold = threshold_from_env(THRESHOLD_ENV_VARS["hard_rule_pass"], SKILL_HARD_RULE_PASS_RATE_MIN)
    hard_rate = float(skill_metrics.get("hard_rule_pass_rate", 0))
    if hard_rate < hard_threshold:
        raise EvalError(f"skill hard_rule_pass_rate {hard_rate:.2%} is below {hard_threshold:.2%}")
    placeholder_threshold = threshold_from_env(
        THRESHOLD_ENV_VARS["placeholder_risk"], SKILL_PLACEHOLDER_RISK_RATE_MAX
    )
    placeholder_rate = float(skill_metrics.get("placeholder_risk_rate", 0))
    if placeholder_rate > placeholder_threshold:
        raise EvalError(
            f"skill placeholder_risk_rate {placeholder_rate:.2%} exceeds threshold {placeholder_threshold:.2%}"
        )
    skill_lint = float(skill_metrics.get("avg_lint_risk_weight", 0))
    baseline_lint = float(baseline_metrics.get("avg_lint_risk_weight", 0))
    if skill_lint > baseline_lint:
        raise EvalError(
            f"skill avg_lint_risk_weight {skill_lint:.4f} exceeds baseline {baseline_lint:.4f}"
        )
    win_or_tie_rate = summary["pairwise"]["skill_win_rate"] + summary["pairwise"]["tie_rate"]
    win_threshold = threshold_from_env(THRESHOLD_ENV_VARS["win_or_tie"], SKILL_WIN_OR_TIE_RATE_MIN)
    if win_or_tie_rate < win_threshold:
        raise EvalError(f"skill win+tie rate {win_or_tie_rate:.2%} is below {win_threshold:.2%}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--judge-repeats", type=int, default=2)
    parser.add_argument("--judge-batch-size", type=int, default=10)
    parser.add_argument("--judge-timeout-seconds", type=int, default=720)
    args = parser.parse_args()

    limit = 10 if args.suite == "smoke" else None
    cases = load_cases(limit)
    promptfoo_json, promptfoo_html = run_promptfoo(args.suite, limit)
    outputs = load_promptfoo_outputs(promptfoo_json, cases)

    missing_for_judge = [
        case_id(case)
        for case in cases
        if not outputs.get(case_id(case), {}).get("baseline", {}).get("text")
        or not outputs.get(case_id(case), {}).get("skill", {}).get("text")
    ]
    if missing_for_judge:
        judge_results = {case_id(case): [] for case in cases}
    else:
        judge_results = judge_chunked(
            args.suite,
            cases,
            outputs,
            args.judge_repeats,
            args.judge_batch_size,
            args.judge_timeout_seconds,
        )

    summary = summarize(args.suite, cases, outputs, judge_results, promptfoo_json, promptfoo_html)
    summary_path = write_summary(args.suite, summary)
    print(f"summary: {summary_path}")
    print(json.dumps(summary["pairwise"], ensure_ascii=False, indent=2))
    enforce_failure_policy(summary)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        raise SystemExit(main())
    except EvalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
