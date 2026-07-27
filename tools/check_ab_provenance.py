from __future__ import annotations

import argparse
import json
import ntpath
from pathlib import Path
from typing import Any


UNAVAILABLE_VALUES = {"", "unavailable", "unknown", "none", "null", "n/a"}


def _available(value: Any) -> bool:
    return value is not None and str(value).strip().lower() not in UNAVAILABLE_VALUES


def _first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


def _normal_path(value: Any) -> str:
    raw = str(value).replace("/", "\\")
    return ntpath.normcase(ntpath.normpath(raw)).rstrip("\\")


def _is_under(path: Any, root: Any) -> bool:
    normal_path = _normal_path(path)
    normal_root = _normal_path(root)
    try:
        return ntpath.commonpath([normal_path, normal_root]) == normal_root
    except ValueError:
        return False


def _runtime_value(data: dict[str, Any], *keys: str) -> Any:
    receipt = data.get("runtime_receipt")
    if isinstance(receipt, dict):
        value = _first(receipt, *keys)
        if value is not None:
            return value
    return _first(data, *keys)


def _source_commit(data: dict[str, Any]) -> Any:
    return _runtime_value(data, "source_commit", "commit", "git_commit", "head_sha")


def _root(data: dict[str, Any]) -> Any:
    return _first(
        data,
        "candidate_root",
        "baseline_root",
        "skill_root",
        "worktree_root",
        "repository_root",
    )


def _references(output: dict[str, Any]) -> list[Any]:
    value = _first(
        output,
        "route_files_used",
        "actual_references",
        "reference_files_used",
    )
    return value if isinstance(value, list) else []


def _outputs(
    data: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    outputs = data.get("outputs")
    if not isinstance(outputs, list):
        return {}, set()

    result: dict[str, dict[str, Any]] = {}
    duplicates: set[str] = set()
    for item in outputs:
        if not isinstance(item, dict):
            continue
        task_id = item.get("task_id")
        if _available(task_id):
            key = str(task_id)
            if key in result:
                duplicates.add(key)
                continue
            result[key] = item
    return result, duplicates


def _issue(
    issues: list[dict[str, str]],
    code: str,
    message: str,
    *,
    side: str | None = None,
    task_id: str | None = None,
) -> None:
    item = {"code": code, "message": message}
    if side is not None:
        item["side"] = side
    if task_id is not None:
        item["task_id"] = task_id
    issues.append(item)


def assess_pair(
    candidate: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Classify whether two A/B runtime receipts support strict comparison."""

    issues: list[dict[str, str]] = []
    sides = {"candidate": candidate, "baseline": baseline}

    scalar_fields = {
        "actual_model": ("actual_model",),
        "actual_reasoning_effort": (
            "actual_reasoning_effort",
            "actual_reasoning",
        ),
        "source_commit": (),
        "host_context_sha256": ("host_context_sha256",),
        "root": (),
    }
    values: dict[str, dict[str, Any]] = {}

    for side, data in sides.items():
        values[side] = {}
        for label, keys in scalar_fields.items():
            if label == "source_commit":
                value = _source_commit(data)
            elif label == "root":
                value = _root(data)
            else:
                value = _runtime_value(data, *keys)
            values[side][label] = value
            if not _available(value):
                _issue(
                    issues,
                    f"{label}_unavailable",
                    f"{side} did not provide a trustworthy {label}",
                    side=side,
                )

    for label in ("actual_model", "actual_reasoning_effort", "host_context_sha256"):
        left = values["candidate"][label]
        right = values["baseline"][label]
        if _available(left) and _available(right) and left != right:
            _issue(
                issues,
                f"{label}_mismatch",
                f"candidate and baseline use different {label}",
            )

    candidate_root = values["candidate"]["root"]
    baseline_root = values["baseline"]["root"]
    if (
        _available(candidate_root)
        and _available(baseline_root)
        and _normal_path(candidate_root) == _normal_path(baseline_root)
    ):
        _issue(
            issues,
            "root_reused",
            "candidate and baseline reuse the same declared root",
        )

    candidate_outputs, candidate_duplicates = _outputs(candidate)
    baseline_outputs, baseline_duplicates = _outputs(baseline)
    for side, duplicates in (
        ("candidate", candidate_duplicates),
        ("baseline", baseline_duplicates),
    ):
        for task_id in sorted(duplicates):
            _issue(
                issues,
                "duplicate_task_id",
                f"{side} contains more than one output for the same task id",
                side=side,
                task_id=task_id,
            )
    if not candidate_outputs:
        _issue(
            issues,
            "outputs_unavailable",
            "candidate did not provide task-level outputs",
            side="candidate",
        )
    if not baseline_outputs:
        _issue(
            issues,
            "outputs_unavailable",
            "baseline did not provide task-level outputs",
            side="baseline",
        )

    candidate_ids = set(candidate_outputs)
    baseline_ids = set(baseline_outputs)
    if candidate_ids != baseline_ids:
        _issue(
            issues,
            "task_set_mismatch",
            "candidate and baseline do not contain the same task ids",
        )

    for task_id in sorted(candidate_ids & baseline_ids):
        task_pair = {
            "candidate": candidate_outputs[task_id],
            "baseline": baseline_outputs[task_id],
        }
        task_hashes: dict[str, Any] = {}
        for side, output in task_pair.items():
            task_hash = output.get("task_sha256")
            task_hashes[side] = task_hash
            if not _available(task_hash):
                _issue(
                    issues,
                    "task_sha256_unavailable",
                    f"{side} did not record the input hash",
                    side=side,
                    task_id=task_id,
                )

            references = _references(output)
            if not references:
                _issue(
                    issues,
                    "references_unavailable",
                    f"{side} did not record actual Skill/reference reads",
                    side=side,
                    task_id=task_id,
                )
            root = values[side]["root"]
            if _available(root):
                for reference in references:
                    if not _is_under(reference, root):
                        _issue(
                            issues,
                            "reference_outside_root",
                            f"{side} read a Skill/reference outside its declared root",
                            side=side,
                            task_id=task_id,
                        )
                        break

            if output.get("first_technical_validity") is not True:
                _issue(
                    issues,
                    "first_output_not_valid",
                    f"{side} did not identify this as the first technically valid output",
                    side=side,
                    task_id=task_id,
                )
            if output.get("generation_attempt") != 1:
                _issue(
                    issues,
                    "generation_attempt_not_one",
                    f"{side} did not use the first generation attempt",
                    side=side,
                    task_id=task_id,
                )

        if (
            _available(task_hashes["candidate"])
            and _available(task_hashes["baseline"])
            and task_hashes["candidate"] != task_hashes["baseline"]
        ):
            _issue(
                issues,
                "task_sha256_mismatch",
                "candidate and baseline did not receive byte-identical task input",
                task_id=task_id,
            )

    for side, data in sides.items():
        policy = data.get("generation_policy")
        if not isinstance(policy, dict):
            _issue(
                issues,
                "generation_policy_unavailable",
                f"{side} did not provide generation policy evidence",
                side=side,
            )
            continue
        if policy.get("first_technically_valid_output_only") is not True:
            _issue(
                issues,
                "first_output_policy_not_proven",
                f"{side} did not prove first-output-only generation",
                side=side,
            )
        if policy.get("resampling_count") != 0:
            _issue(
                issues,
                "resampling_detected",
                f"{side} used or did not rule out resampling",
                side=side,
            )
        if policy.get("post_generation_revision_count") != 0:
            _issue(
                issues,
                "post_generation_revision_detected",
                f"{side} used or did not rule out post-generation revision",
                side=side,
            )

    status = "strict-comparable" if not issues else "exploratory"
    return {
        "status": status,
        "strict_comparable": status == "strict-comparable",
        "task_count": len(candidate_ids & baseline_ids),
        "issues": issues,
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify whether two real-writing provenance receipts support strict A/B comparison."
    )
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument(
        "--require-strict",
        action="store_true",
        help="return exit code 2 when the pair is exploratory",
    )
    args = parser.parse_args()

    result = assess_pair(
        _read_json(args.candidate),
        _read_json(args.baseline),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.require_strict and not result["strict_comparable"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
