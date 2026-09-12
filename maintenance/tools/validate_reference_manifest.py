"""Validate the rebuilt reference routing contract without loading model prompts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chinese-official-writing"
REFS = SKILL / "references"
MANIFEST = REFS / "route-manifest.json"


def validate() -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest unreadable: {exc}"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("entry") != "SKILL.md":
        errors.append("entry must be SKILL.md")
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        return ["pages must be a non-empty list"]
    seen: set[str] = set()
    allowed_kinds = {"router", "genre", "workflow", "review", "language", "overlay", "tool"}
    for page in pages:
        if not isinstance(page, dict):
            errors.append("page entry must be an object")
            continue
        path = page.get("path")
        if not isinstance(path, str) or not path.startswith("references/"):
            errors.append(f"invalid page path: {path!r}")
            continue
        if path in seen:
            errors.append(f"duplicate page: {path}")
        seen.add(path)
        if not (SKILL / path).is_file():
            errors.append(f"missing page: {path}")
        if page.get("kind") not in allowed_kinds:
            errors.append(f"invalid kind for {path}: {page.get('kind')!r}")
        if not page.get("purpose") or not page.get("stop_when"):
            errors.append(f"missing purpose/stop_when: {path}")
        allowed = page.get("allowed_reads")
        forbidden = page.get("forbidden_reads")
        if not isinstance(allowed, list) or path not in allowed:
            errors.append(f"allowed_reads must include itself: {path}")
        if not isinstance(forbidden, list):
            errors.append(f"forbidden_reads must be a list: {path}")
        if isinstance(allowed, list):
            for ref in allowed:
                if ref != "SKILL.md" and not (SKILL / ref).is_file():
                    errors.append(f"missing allowed read {ref} from {path}")
        if isinstance(forbidden, list) and path in forbidden:
            errors.append(f"page forbids itself: {path}")
    actual = {f"references/{p.name}" for p in REFS.glob("*.md")}
    if actual != seen:
        errors.append(
            "manifest/page drift: "
            f"missing={sorted(actual - seen)}, extra={sorted(seen - actual)}"
        )
    routes = data.get("routes")
    if not isinstance(routes, list) or not routes:
        errors.append("routes must be a non-empty list")
    else:
        for route in routes:
            if not isinstance(route, dict) or not route.get("id"):
                errors.append("route must have an id")
                continue
            primary = route.get("primary")
            if not isinstance(primary, list) or len(primary) != 1:
                errors.append(f"route {route['id']} must have one primary leaf")
                continue
            for ref in primary + route.get("overlays", []) + route.get("review", []):
                if ref not in seen:
                    errors.append(f"route {route['id']} points to unknown page {ref}")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print(f"reference manifest valid: {len(json.loads(MANIFEST.read_text(encoding='utf-8'))['pages'])} pages")
