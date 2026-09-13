"""Freeze the R15 owner-consolidation atoms without changing the canonical Skill.

Run once from any directory. Existing output is never overwritten or removed.
Only the two explicitly retired pages are unlinked from fresh candidate copies.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "chinese-official-writing"
DEST = ROOT / "output/common-layer-owners-r15"
AUDIT = Path(__file__).with_name("owner-audit.md")
EXPECTED_HEAD = "01c2a659c26cfef320622356b847bb3e88401a7a"

HANDLING = "references/handling-elements.md"
STYLE = "references/official-style.md"
WRITING = "references/writing-rules.md"
ANTI = "references/anti-ai-patterns.md"
INDEX = "references/reference-index.md"
REQUEST = "references/genre-playbook-request.md"
REVIEW = "references/genre-playbook-review-opinion.md"
SPEECH = "references/genre-playbook-speech-address.md"

OLD_REVIEW = (
    "对照材料和主文种检查事实、状态、必要要素及本轮修改是否落实；整体任务检查全文，局部任务检查改动及关联内容。"
    "存在跨段论证、多主体责任、表格或附件时，核对相互对应的结论、数值、字段、期限和指向。"
    "Word 稿按已选模板核对样式，保留要求的批注和修订痕迹。"
)
NEW_REVIEW = (
    "按材料和主文种核对事实、状态、必要要素及改动；整体查全文，局部查改动及关联内容。"
    "跨段论证、多主体责任、表格和附件，核对对应的主体、结论、字段名称、数值及实测/测算/估算口径、顺序、状态、期限和指向。"
    "Word按模板查样式，保留要求的批注和修订痕迹。"
)
OLD_FIDELITY = (
    "修改保持原意、引用、主体、对象、否定范围和论断强度，避免用口语或情绪化表达代替正式语体。"
    "“更稳、更省”分别对应稳定性和成本，改写时保留两层含义。"
)
NEW_FIDELITY = (
    "口语或情绪化表达改为同义正式语体，保持叙述身份、原意、引用、主体、对象、否定范围、先后和论断强度。"
    "“更稳、更省”仍分别说明稳定性和成本。"
)

# These anchors bind the current canonical callers, including R14's narrower
# request condition, rather than the older quotation in the owner audit.
REPLACEMENTS = {
    "A": {
        WRITING: (OLD_REVIEW, NEW_REVIEW),
        REQUEST: (
            "需要核对多主体责任、分项金额或正文与附件的对应关系时加读 `handling-elements.md`，",
            "",
        ),
        REVIEW: (
            "需要核对办理主体、时限或附件时，读取 `handling-elements.md`。",
            "",
        ),
    },
    "B": {ANTI: (OLD_FIDELITY, NEW_FIDELITY)},
}
REMOVED_LINES = {
    "A": {INDEX: "| `handling-elements.md` |"},
    "B": {
        INDEX: "| `official-style.md` |",
        SPEECH: "- 需要统一正式、平实的发言语气时加读 `official-style.md`。",
    },
}
RETIRED = {"A": HANDLING, "B": STYLE}
EXPECTED_CHANGES = {
    "A": {HANDLING, WRITING, INDEX, REQUEST, REVIEW},
    "B": {STYLE, ANTI, INDEX, SPEECH},
}
EXPECTED_CHANGES["AB"] = EXPECTED_CHANGES["A"] | EXPECTED_CHANGES["B"]


def require(condition: bool, detail: object) -> None:
    if not condition:
        raise RuntimeError(str(detail))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def snapshot(directory: Path) -> dict[str, bytes]:
    result = {}
    for path in sorted(directory.rglob("*")):
        rel = path.relative_to(directory)
        if "__pycache__" in rel.parts or path.suffix == ".pyc":
            continue
        require(not path.is_symlink(), f"Symlink is outside this build's copy scope: {path}")
        if path.is_file():
            result[rel.as_posix()] = path.read_bytes()
    return result


def count_chars(data: bytes | str) -> int:
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    return len(re.sub(r"\s", "", text))


def apply_atom(source: dict[str, bytes], atom: str) -> dict[str, bytes]:
    result = source.copy()
    for name, (old, new) in REPLACEMENTS[atom].items():
        old_bytes = old.encode("utf-8")
        require(result[name].count(old_bytes) == 1, (atom, name, "replacement anchor must occur once"))
        result[name] = result[name].replace(old_bytes, new.encode("utf-8"))
    for name, prefix in REMOVED_LINES[atom].items():
        lines = result[name].splitlines(keepends=True)
        selected = [line for line in lines if line.startswith(prefix.encode("utf-8"))]
        require(len(selected) == 1, (atom, name, "removed caller line must occur once"))
        result[name] = b"".join(line for line in lines if line != selected[0])
    result.pop(RETIRED[atom])
    return result


def changed_paths(baseline: dict[str, bytes], candidate: dict[str, bytes]) -> set[str]:
    return {name for name in baseline.keys() | candidate.keys() if baseline.get(name) != candidate.get(name)}


def local_links(tree: dict[str, bytes]) -> set[tuple[str, str]]:
    """Resolve Markdown and backtick .md references in SKILL and reference pages."""
    edges = set()
    for name, content in tree.items():
        if name != "SKILL.md" and not (name.startswith("references/") and name.endswith(".md")):
            continue
        text = content.decode("utf-8-sig")
        tokens = set(re.findall(r"`([^`\s]+\.md)`", text))
        tokens.update(re.findall(r"\]\(([^\s)]+\.md)(?:#[^)]*)?\)", text))
        for token in tokens:
            if "://" in token:
                continue
            parent = PurePosixPath(name).parent
            options = [(parent / token).as_posix(), token]
            if "/" not in token:
                options.append("references/" + token)
            target = next((option for option in options if option in tree), None)
            require(target is not None, (name, token, "unresolved local Markdown reference"))
            edges.add((name, target))
    return edges


def manifest(tree: dict[str, bytes]) -> dict:
    hashes = {name: sha256(content) for name, content in sorted(tree.items())}
    chars = {name: count_chars(content) for name, content in sorted(tree.items()) if name.endswith(".md")}
    common = [WRITING, ANTI, "references/prose-lint-usage.md"]
    return {
        "files": hashes,
        "fingerprint": sha256(json.dumps(hashes, sort_keys=True).encode("utf-8")),
        "file_count": len(tree),
        "reference_page_count": sum(name.startswith("references/") and name.endswith(".md") for name in tree),
        "bytes": {name: len(content) for name, content in sorted(tree.items())},
        "non_whitespace_chars": chars,
        "markdown_non_whitespace_chars": sum(chars.values()),
        "reference_non_whitespace_chars": sum(value for name, value in chars.items() if name.startswith("references/")),
        "common_non_whitespace_chars": sum(chars[name] for name in common),
        "common_pages": common,
    }


def exact_diff(baseline: dict[str, bytes], candidate: dict[str, bytes], arm: str) -> bytes:
    result = []
    for name in sorted(changed_paths(baseline, candidate)):
        old = baseline.get(name, b"").decode("utf-8")
        new = candidate.get(name, b"").decode("utf-8")
        result.extend(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=f"baseline/{name}",
            tofile=f"{arm}/{name}" if name in candidate else "/dev/null",
        ))
    return "".join(result).encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    require(git("rev-parse", "HEAD") == EXPECTED_HEAD, "Source HEAD changed; review the new baseline before building")
    require(not git("status", "--porcelain", "--untracked-files=all", "--", "chinese-official-writing"), "Canonical Skill is not clean")
    require(not DEST.exists(), f"Refusing to overwrite existing freeze: {DEST}")
    source = snapshot(SOURCE)
    require(source, "Empty source Skill")
    require(count_chars(OLD_REVIEW) == count_chars(NEW_REVIEW) == 123, "Review paragraph count changed")
    require((count_chars(OLD_FIDELITY), count_chars(NEW_FIDELITY)) == (72, 68), "Fidelity paragraph count changed")
    # Plan every byte and check scope/links before creating any output directories.
    plans = {"baseline": source, "A": apply_atom(source, "A"), "B": apply_atom(source, "B")}
    plans["AB"] = apply_atom(plans["A"], "B")
    require(plans["AB"] == apply_atom(plans["B"], "A"), "A and B do not compose independently")
    base_links = local_links(source)
    validation = {}
    for arm, tree in plans.items():
        changed = changed_paths(source, tree)
        require(changed == EXPECTED_CHANGES.get(arm, set()), (arm, "unexpected changed paths", sorted(changed)))
        require(not tree.keys() - source.keys(), (arm, "unexpected new Skill file"))
        links = local_links(tree)
        require(links <= base_links, (arm, "new routing edge", sorted(links - base_links)))
        for atom in ("A", "B"):
            if atom in arm and arm != "baseline":
                token = Path(RETIRED[atom]).name.encode("utf-8")
                require(all(token not in content for content in tree.values()), (arm, "retired page still referenced", token))
        validation[arm] = {
            "changed_paths_match": True,
            "local_markdown_links_resolve": True,
            "local_markdown_edge_count": len(links),
            "new_routing_edges": 0,
            "all_other_files_byte_identical": True,
        }

    DEST.mkdir(parents=True)
    copy_ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(SOURCE, DEST / "baseline", ignore=copy_ignore)
    require(snapshot(DEST / "baseline") == source, "Canonical changed during baseline copy")
    deleted_targets = []
    for arm in ("A", "B", "AB"):
        target = DEST / arm
        shutil.copytree(DEST / "baseline", target, ignore=copy_ignore)
        planned = plans[arm]
        for name in sorted(changed_paths(source, planned)):
            path = target / name
            if name in planned:
                path.write_bytes(planned[name])
                continue
            # Only these known copied pages may be deleted. Verify the final
            # absolute path and original bytes before each non-recursive unlink.
            require(name in (HANDLING, STYLE), (arm, "unapproved deletion", name))
            resolved = path.resolve(strict=True)
            expected = target.resolve(strict=True) / "references" / Path(name).name
            require(resolved == expected and resolved.is_relative_to(DEST.resolve()), (arm, "deletion escaped candidate", resolved))
            require(not path.is_symlink() and path.read_bytes() == source[name], (arm, "deletion target is not the fresh baseline page", name))
            deleted_targets.append(str(resolved))
            path.unlink()
        require(snapshot(target) == planned, (arm, "written candidate does not match planned bytes"))

    require(snapshot(SOURCE) == source, "Canonical changed during build")
    require(not git("status", "--porcelain", "--untracked-files=all", "--", "chinese-official-writing"), "Canonical was modified during build")
    records = {}
    artifact_hashes = {}
    for arm, tree in plans.items():
        records[arm] = manifest(tree)
        records[arm]["changed_paths"] = sorted(changed_paths(source, tree))
        records[arm]["markdown_chars_delta"] = records[arm]["markdown_non_whitespace_chars"] - records["baseline"]["markdown_non_whitespace_chars"]
        manifest_path = DEST / f"{arm}.manifest.json"
        write_json(manifest_path, records[arm])
        artifact_hashes[manifest_path.name] = sha256(manifest_path.read_bytes())
        if arm != "baseline":
            diff_path = DEST / f"{arm}.diff"
            diff_path.write_bytes(exact_diff(source, tree, arm))
            artifact_hashes[diff_path.name] = sha256(diff_path.read_bytes())
    build = {
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_head": EXPECTED_HEAD,
        "owner_audit": AUDIT.relative_to(ROOT).as_posix(),
        "owner_audit_sha256": sha256(AUDIT.read_bytes()),
        "builder_sha256": sha256(Path(__file__).read_bytes()),
        "excluded_runtime_cache": ["__pycache__", "*.pyc"],
        "fingerprint_definition": "SHA256(UTF-8 json.dumps(path_to_file_sha256, sort_keys=True))",
        "char_count_definition": "Unicode characters after removing Python regex \\s; Markdown source, not tokens or measured model reads",
        "composition_order_independent": True,
        "canonical_unchanged": True,
        "deleted_fresh_copy_paths": deleted_targets,
        "arms": records,
        "validation": validation,
        "artifact_sha256": artifact_hashes,
        "validation_limits": "Build, byte scope, composition and local Markdown references only; no model runs or writing-quality claim. No new route edge can introduce a cycle; existing route behavior was not rerun.",
        "notes": [
            "Request caller removal uses the current R14 narrow condition, not the older audit quotation.",
            "A replaces only the existing review paragraph and its retired-page callers; B replaces only the existing fidelity paragraph and its retired-page callers.",
            "SKILL.md, scripts, delivery, 80-character floor, date/inference rules and other capability pages retain baseline bytes except the two declared common paragraphs.",
        ],
    }
    write_json(DEST / "build.json", build)
    print(json.dumps({
        "output": str(DEST),
        "build_json_sha256": sha256((DEST / "build.json").read_bytes()),
        "arms": {arm: {key: record[key] for key in ("fingerprint", "file_count", "reference_page_count", "markdown_chars_delta", "common_non_whitespace_chars", "changed_paths")} for arm, record in records.items()},
        "validation": "PASS: frozen bytes, exact scope, composition, local links, no new route edges, canonical unchanged",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
