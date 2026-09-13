"""Check local product links and leaked developer commands, not rule wording."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "chinese-official-writing"
DEVELOPER_MARKERS = ("git commit", "git push", "python -m unittest", "pytest", "maintenance/", "route-manifest.json")
REMOVED_HOOK_ROUTES = ("hooks/", "scripts/review_gate.py", "references/delivery-review-gate.md")
LOCAL_NAME = r"(?:references/|scripts/)?[A-Za-z0-9_.-]+\.(?:md|py)"
LOCAL_LINK = re.compile(rf"`({LOCAL_NAME})`|\[[^\]]*\]\(({LOCAL_NAME})\)")


def linked_paths(path: Path, product: Path, text: str) -> set[Path]:
    links = set()
    for code_link, markdown_link in LOCAL_LINK.findall(text):
        name = code_link or markdown_link
        if "/" in name or name in {"SKILL.md", "README.md"}:
            target = product / name
        elif name.endswith(".py"):
            target = product / "scripts" / name
        else:
            target = path.parent / name
        links.add(target)
    return links


def audit(product: Path | None = None) -> list[str]:
    product = PRODUCT if product is None else product
    entry = product / "SKILL.md"
    files = [entry, *sorted((product / "references").glob("*.md"))]
    errors, graph = [], {}
    for path in files:
        rel = path.relative_to(product).as_posix()
        if not path.is_file():
            errors.append(f"missing file: {rel}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for marker in DEVELOPER_MARKERS + REMOVED_HOOK_ROUTES:
            if marker.lower() in text.lower():
                errors.append(f"{rel}: developer command or removed route: {marker!r}")
        links = linked_paths(path, product, text)
        graph[path] = links
        for target in sorted(links):
            if not target.is_file():
                errors.append(f"{rel}: missing linked file {target.relative_to(product).as_posix()}")
    visited, pending = set(), [entry]
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        pending.extend(graph.get(path, set()) - visited)
    for path in files[1:]:
        if path not in visited:
            errors.append(f"unreachable reference: {path.relative_to(product).as_posix()}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PRODUCT)
    problems = audit(parser.parse_args().root)
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("product paths reachable; rule readability and semantics require independent review")
