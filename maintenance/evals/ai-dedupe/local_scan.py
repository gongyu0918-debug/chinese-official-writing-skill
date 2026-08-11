#!/usr/bin/env python3
"""Local AI-flavor and similarity scan for generated official-writing samples.

This script is intentionally advisory. It records prose-lint findings and
cross-sample similarity signals, but it does not enforce a quality gate.
"""

from __future__ import annotations

import argparse
import importlib.util
import hashlib
import json
import math
import re
import sys
from collections import Counter
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from typing import Any


def load_samples(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        samples = data
    elif isinstance(data, dict) and isinstance(data.get("samples"), list):
        samples = data["samples"]
    elif isinstance(data, dict) and isinstance(data.get("rounds"), list):
        samples = []
        for item in data["rounds"]:
            if isinstance(item, dict) and isinstance(item.get("samples"), list):
                samples.extend(item["samples"])
    else:
        raise SystemExit(f"Unsupported sample JSON shape: {path}")

    normalized: list[dict[str, Any]] = []
    for index, sample in enumerate(samples, start=1):
        if not isinstance(sample, dict):
            continue
        text = str(sample.get("output") or sample.get("text") or "")
        if not text.strip():
            continue
        normalized.append(
            {
                "id": str(sample.get("id") or f"S{index:03d}"),
                "genre": str(sample.get("genre") or ""),
                "prompt": str(sample.get("prompt") or ""),
                "output": text,
            }
        )
    return normalized


def char_ngrams(text: str, n: int = 3) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    if len(compact) <= n:
        return [compact] if compact else []
    return [compact[i : i + n] for i in range(len(compact) - n + 1)]


def simhash_distance(a: str, b: str) -> int:
    return (simhash(a) ^ simhash(b)).bit_count()


def simhash(text: str, bits: int = 64) -> int:
    vector = [0] * bits
    for token, weight in Counter(char_ngrams(text, 3)).items():
        digest = int(hashlib.blake2b(token.encode("utf-8"), digest_size=8).hexdigest(), 16)
        for bit in range(bits):
            if digest & (1 << bit):
                vector[bit] += weight
            else:
                vector[bit] -= weight
    value = 0
    for bit, score in enumerate(vector):
        if score >= 0:
            value |= 1 << bit
    return value


def cosine(a: Counter[str], b: Counter[str], idf: dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a[key] * idf[key] * b[key] * idf[key] for key in keys)
    norm_a = math.sqrt(sum((a[key] * idf[key]) ** 2 for key in a))
    norm_b = math.sqrt(sum((b[key] * idf[key]) ** 2 for key in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def build_similarity(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counters = {item["id"]: Counter(char_ngrams(item["output"], 3)) for item in samples}
    doc_freq: Counter[str] = Counter()
    for counter in counters.values():
        doc_freq.update(counter.keys())
    total = len(samples)
    idf = {token: math.log((1 + total) / (1 + freq)) + 1 for token, freq in doc_freq.items()}

    pairs: list[dict[str, Any]] = []
    for left, right in combinations(samples, 2):
        left_id = left["id"]
        right_id = right["id"]
        left_set = set(counters[left_id])
        right_set = set(counters[right_id])
        pairs.append(
            {
                "pair": [left_id, right_id],
                "simhash_distance": simhash_distance(left["output"], right["output"]),
                "tfidf_cosine": round(cosine(counters[left_id], counters[right_id], idf), 4),
                "char_jaccard": round(jaccard(left_set, right_set), 4),
            }
        )
    return pairs


def run_prose_lint(samples: list[dict[str, Any]], repo_root: Path) -> list[dict[str, Any]]:
    lint_script = repo_root / "chinese-official-writing" / "scripts" / "prose_lint.py"
    if not lint_script.exists():
        return [
            {
                "id": item["id"],
                "count": 0,
                "findings": [],
                "error": f"missing prose_lint.py at {lint_script}",
            }
            for item in samples
        ]

    spec = importlib.util.spec_from_file_location("official_prose_lint", lint_script)
    if spec is None or spec.loader is None:
        return [
            {
                "id": item["id"],
                "count": 0,
                "findings": [],
                "error": f"failed to load prose_lint.py at {lint_script}",
            }
            for item in samples
        ]
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    results: list[dict[str, Any]] = []
    for item in samples:
        findings = [
            asdict(entry)
            for entry in module.scan(
                f"{item['id']}.txt",
                item["output"],
                include_format=True,
                include_structure=True,
            )
        ]
        results.append(
            {
                "id": item["id"],
                "count": len(findings),
                "findings": [
                    f"{entry['severity']}:{entry['label']}:{entry['match']}"
                    for entry in findings
                ],
            }
        )
    return results


def summarize(results: dict[str, Any]) -> dict[str, Any]:
    lint_counts = [item["count"] for item in results["prose_lint"]]
    pairs = results["pair_similarity"]
    return {
        "sample_count": len(results["samples"]),
        "prose_lint_total_findings": sum(lint_counts),
        "prose_lint_max_findings": max(lint_counts, default=0),
        "min_simhash_distance": min((item["simhash_distance"] for item in pairs), default=None),
        "max_tfidf_cosine": max((item["tfidf_cosine"] for item in pairs), default=None),
        "max_char_jaccard": max((item["char_jaccard"] for item in pairs), default=None),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan generated samples for prose and similarity risks.")
    parser.add_argument("samples_json", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    (repo_root / "tmp").mkdir(exist_ok=True)
    samples = load_samples(args.samples_json)
    results: dict[str, Any] = {
        "samples": [{"id": item["id"], "genre": item["genre"]} for item in samples],
        "prose_lint": run_prose_lint(samples, repo_root),
        "pair_similarity": build_similarity(samples),
    }
    results["summary"] = summarize(results)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
