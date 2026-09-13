"""Build a fresh, bounded R16 directory-cleanup prototype; never overwrite it."""

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
DEST = ROOT / "output/genre-router-cleanup-r16"
EXPECTED_HEAD = "35ea2ef441755d0708ea41d771c11f367a24f118"
EXPECTED_PRODUCT = "5816a97c745d7e1f2af139f987ce973b12e3e7c5b076011046962da873f62d3b"
INDEX = "references/reference-index.md"
ROUTING = "references/genre-routing.md"
CHECKLIST = "references/genre-checklist.md"
CHANGED = {"SKILL.md", INDEX, ROUTING, CHECKLIST}
OLD_CORRESPONDENCE = "- 不相隶属单位之间的函、复函、征求意见函：`genre-playbook-correspondence.md`。"
NEW_CORRESPONDENCE = "- 不相隶属单位之间商洽、询答、请求批准或答复审批事项的函、复函、征求意见函：`genre-playbook-correspondence.md`。"
GENRE_SOURCE = ROOT / "maintenance/tests/evidence/common-layer-r14/genre-source-check-r14.md"

ENTRY_SECTION = """### 第二步：选择文种

需要处理正文内容时，以用户模板、最新版底稿、明确标题和用途选路。用户限定仅排版、保留文字时，直接按格式任务处理。

按 `references/reference-index.md` 为每份稿件选定一个主叶；标题、模板、正文用途或行文关系有冲突时，先读 `references/genre-routing.md` 判定，再选主叶。

"""
FALLBACK_SECTION = """### 目录未命中时

事务名称未列出时，按实际用途匹配上述专页。用途已明确且没有适用专页时，读取 `genre-checklist.md`。

"""
ROUTING_TEXT = """# 文种冲突判定

结合本轮交付目的，处理标题、模板、正文功能或行文关系之间的矛盾。

- 按用户要求保留模板、最新版底稿的结构及限定的标题、字段，再判断正文要完成的事项。标题可调整时使其与用途一致；标题固定时，正文仍完成实际用途，并保留需要说明的标题冲突。
- 依据主要办理或表达目的选文种，背景、下一步安排以及技术、采购内容服务该目的。情况说明以解释事实、原因或回应疑问为主时按说明处理，以汇报进展和处置为主时按报告处理；需要批准时，结合收文方权限和行文关系确定文种。
- 按材料确定叙述身份和接收对象，以实际行文关系校准语气及决定权限。不相隶属单位间商洽、询答、请求批准或在权限范围内答复审批事项，按函或复函处理；上级答复下级请示按批复处理。研究报告上报或公开时仍呈现研究发现，纪要按会议事项组织。
- 通知正文与独立方案、制度或技术需求附件分别按自身用途判断。
- 审核、压缩和排版沿用被处理稿件的文种；依据评审记录起草审查意见时，按独立审查意见处理。
- 发言稿按具体用途判断：现场述职以履职汇报为主，主持词组织会序，另作的主题讲话表达观点。
"""
CHECKLIST_TEXT = """# 未覆盖文种的功能核对

按用户模板、材料和已确认的通用写法组织正文，完成本稿的办理或表达目的。通用写法、必备要素或格式不熟悉时，按首页的核查规则定向查证。

- 结合主体、接收对象和用途核对行文关系。
- 保留用户限定的标题和字段，核对模板与通用要求能否兼容；仍有冲突时明确具体问题。
"""


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(str(message))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def snapshot(directory: Path) -> dict[str, bytes]:
    files = {}
    for path in sorted(directory.rglob("*")):
        rel = path.relative_to(directory)
        if "__pycache__" in rel.parts or path.suffix == ".pyc":
            continue
        require(not path.is_symlink(), ("unsupported source symlink", path))
        if path.is_file():
            files[rel.as_posix()] = path.read_bytes()
    return files


def hashes(tree: dict[str, bytes]) -> dict[str, str]:
    return {name: sha256(data) for name, data in sorted(tree.items())}


def fingerprint(tree: dict[str, bytes]) -> str:
    return sha256(json.dumps(hashes(tree), sort_keys=True).encode("utf-8"))


def encode_like(text: str, original: bytes) -> bytes:
    newline = "\r\n" if b"\r\n" in original else "\n"
    return text.replace("\n", newline).encode("utf-8")


def segment(data: bytes, start: str, end: str) -> bytes:
    left, right = start.encode("utf-8"), end.encode("utf-8")
    require(data.count(left) == data.count(right) == 1, ("section anchors", start, end))
    return data[data.index(left):data.index(right)]


def replace_section(data: bytes, start: str, end: str, text: str) -> bytes:
    old = segment(data, start, end)
    return data.replace(old, encode_like(text, old), 1)


def reference_graph(tree: dict[str, bytes]) -> dict[str, set[str]]:
    graph = {}
    for name, data in tree.items():
        if name != "SKILL.md" and not (name.startswith("references/") and name.endswith(".md")):
            continue
        text = data.decode("utf-8-sig")
        tokens = set(re.findall(r"`([^`\s]+\.md)`", text))
        tokens.update(re.findall(r"\]\(([^\s)]+\.md)(?:#[^)]*)?\)", text))
        targets = set()
        for token in tokens:
            if "://" in token:
                continue
            choices = [(PurePosixPath(name).parent / token).as_posix(), token]
            if "/" not in token:
                choices.append("references/" + token)
            target = next((choice for choice in choices if choice in tree), None)
            require(target is not None, ("unresolved local reference", name, token))
            targets.add(target)
        graph[name] = targets
    return graph


def reachable(graph: dict[str, set[str]], start: str) -> set[str]:
    seen, pending = set(), [start]
    while pending:
        current = pending.pop()
        if current not in seen:
            seen.add(current)
            pending.extend(graph.get(current, set()))
    return seen


def check_reference_cycles(graph: dict[str, set[str]]) -> None:
    # SKILL mentions establish entry/workflow context, not reference-page calls.
    active, done = set(), set()

    def visit(name: str) -> None:
        require(name not in active, ("reference-page cycle", name))
        if name in done:
            return
        active.add(name)
        for target in graph.get(name, set()):
            if target.startswith("references/"):
                visit(target)
        active.remove(name)
        done.add(name)

    for name in graph:
        if name.startswith("references/"):
            visit(name)


def manifest(tree: dict[str, bytes]) -> dict:
    chars = {
        name: len(re.sub(r"\s", "", data.decode("utf-8-sig")))
        for name, data in tree.items() if name.endswith(".md")
    }
    return {
        "files": hashes(tree),
        "fingerprint": fingerprint(tree),
        "file_count": len(tree),
        "reference_page_count": sum(name.startswith("references/") for name in chars),
        "non_whitespace_chars": chars,
        "markdown_non_whitespace_chars": sum(chars.values()),
    }


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    require(git("rev-parse", "HEAD") == EXPECTED_HEAD, "Review the changed source HEAD before building")
    require(not git("status", "--porcelain", "--untracked-files=all", "--", "chinese-official-writing"), "Canonical is not clean")
    require(not DEST.exists(), f"Refusing to overwrite existing output: {DEST}")
    baseline = snapshot(SOURCE)
    require(fingerprint(baseline) == EXPECTED_PRODUCT, "Canonical differs from the registered product baseline")
    candidate = baseline.copy()
    candidate["SKILL.md"] = replace_section(baseline["SKILL.md"], "### 第二步：选择文种", "### 第三步：按任务加读", ENTRY_SECTION)
    candidate[INDEX] = replace_section(baseline[INDEX], "### 需先确定主文种的场景", "## 共性能力页", FALLBACK_SECTION)
    require(candidate[INDEX].count(OLD_CORRESPONDENCE.encode("utf-8")) == 1, "Correspondence directory anchor changed")
    candidate[INDEX] = candidate[INDEX].replace(OLD_CORRESPONDENCE.encode("utf-8"), NEW_CORRESPONDENCE.encode("utf-8"), 1)
    candidate[ROUTING] = encode_like(ROUTING_TEXT, baseline[ROUTING])
    candidate[CHECKLIST] = encode_like(CHECKLIST_TEXT, baseline[CHECKLIST])
    require({name for name in baseline if baseline[name] != candidate[name]} == CHANGED, "Unexpected changed paths")
    require(candidate.keys() == baseline.keys(), "Added or deleted Skill file")

    old_catalog = segment(baseline[INDEX], "### 文种专页", "### 需先确定主文种的场景")
    new_catalog = segment(candidate[INDEX], "### 文种专页", "### 目录未命中时")
    require(old_catalog.replace(OLD_CORRESPONDENCE.encode("utf-8"), NEW_CORRESPONDENCE.encode("utf-8"), 1) == new_catalog, "Genre directory changed beyond the approved correspondence purpose line")
    require(baseline[INDEX].split("## 共性能力页".encode())[1] == candidate[INDEX].split("## 共性能力页".encode())[1], "Capability index changed")
    for name in ("references/handling-elements.md", "references/official-style.md", "references/writing-rules.md", "references/anti-ai-patterns.md", "references/prose-lint-usage.md", "scripts/draft_length.py", "scripts/prose_lint.py"):
        require(candidate[name] == baseline[name], ("Out-of-scope owner or script change", name))

    graphs = {"baseline": reference_graph(baseline), "candidate": reference_graph(candidate)}
    refs = {name for name in baseline if name.startswith("references/") and name.endswith(".md")}
    for arm, graph in graphs.items():
        check_reference_cycles(graph)
        require(refs <= reachable(graph, "SKILL.md"), (arm, "unreachable references", sorted(refs - reachable(graph, "SKILL.md"))))
    graph = graphs["candidate"]
    require(ROUTING not in graph[INDEX] and INDEX not in graph[ROUTING], "Index and conflict page call each other")
    require(not graph[ROUTING], "Conflict page contains a new routing directory or file call")
    require(CHECKLIST in graph[INDEX], "Unmatched-purpose destination disappeared")
    old_routing_targets = {name for name in graphs["baseline"][ROUTING] if name.startswith("references/")}
    require(old_routing_targets <= reachable(graph, INDEX), "A removed table target lost its directory route")
    before_edges = {(source, target) for source, targets in graphs["baseline"].items() for target in targets}
    after_edges = {(source, target) for source, targets in graph.items() for target in targets}
    require(after_edges <= before_edges, "Unexpected new file-call edge")
    for name in CHANGED:
        for marker in (b"maintenance/", b"git commit", b"worktree", b"R16", b"baseline", b"fingerprint"):
            require(marker not in candidate[name], ("maintenance text in product", name, marker))

    # Preflight is complete; both directories are created fresh and never deleted.
    DEST.mkdir(parents=True)
    shutil.copytree(SOURCE, DEST / "baseline", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    require(snapshot(DEST / "baseline") == baseline, "Baseline copy drift")
    shutil.copytree(DEST / "baseline", DEST / "candidate")
    for name in sorted(CHANGED):
        (DEST / "candidate" / name).write_bytes(candidate[name])
    require(snapshot(DEST / "candidate") == candidate, "Candidate copy drift")
    require(snapshot(SOURCE) == baseline, "Canonical changed during build")

    patch = []
    for name in sorted(CHANGED):
        patch.extend(difflib.unified_diff(
            baseline[name].decode("utf-8").splitlines(keepends=True),
            candidate[name].decode("utf-8").splitlines(keepends=True),
            fromfile=f"baseline/{name}", tofile=f"candidate/{name}",
        ))
    (DEST / "changes.diff").write_bytes("".join(patch).encode("utf-8"))
    records = {"baseline": manifest(baseline), "candidate": manifest(candidate)}
    for arm, record in records.items():
        write_json(DEST / f"{arm}.manifest.json", record)
    char_changes = {
        name: {"baseline": records["baseline"]["non_whitespace_chars"][name], "candidate": records["candidate"]["non_whitespace_chars"][name]}
        for name in sorted(CHANGED)
    }
    build = {
        "source_head": EXPECTED_HEAD,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "builder_sha256": sha256(Path(__file__).read_bytes()),
        "preregister_sha256": sha256(Path(__file__).with_name("preregister.md").read_bytes()),
        "genre_source_check": GENRE_SOURCE.relative_to(ROOT).as_posix(),
        "genre_source_check_sha256": sha256(GENRE_SOURCE.read_bytes()),
        "proposal": "output/genre-router-cleanup-r16-plan.md",
        "excluded_runtime_cache": ["__pycache__", "*.pyc"],
        "fingerprint_definition": "SHA256(UTF-8 json.dumps(path_to_file_sha256, sort_keys=True))",
        "character_definition": "Markdown Unicode characters excluding Python regex whitespace; not tokens or measured reads",
        "arms": records,
        "changed_paths": sorted(CHANGED),
        "changed_page_chars": char_changes,
        "catalog_line_change": {"old": OLD_CORRESPONDENCE, "new": NEW_CORRESPONDENCE, "reason": "Retain the already verified approval-request and approval-response functions of correspondence, distinct from reply to a subordinate request."},
        "markdown_chars_delta": records["candidate"]["markdown_non_whitespace_chars"] - records["baseline"]["markdown_non_whitespace_chars"],
        "semantic_ownership": [
            {"function": "existing genre and capability choices", "owner": INDEX, "evidence": "All directory rows retain their files; only the approved correspondence-purpose line changes wording. All other directory and capability text is byte-identical, and former conflict-table targets remain reachable."},
            {"function": "template, purpose, relationship, mixed-document and task-operation conflicts", "owner": ROUTING, "evidence": "Retained as purpose judgments without a second filename directory; manual text review still required."},
            {"function": "one primary per independent draft and common writing/review/delivery", "owner": "SKILL.md", "evidence": "Only step 2 changes; step 1 and all steps after selection retain baseline bytes, as do all shared rule and script files."},
            {"function": "unfamiliar general writing conventions", "owner": "SKILL.md + references/external-research.md", "evidence": "Original inquiry and external-research instructions retain baseline bytes; fallback points to their existing use."},
        ],
        "intentional_semantic_changes": [
            "For a clear purpose with no matching genre page, the existing genre-checklist supports drafting from the user's template, materials and confirmed conventions; it no longer redirects to the nearest other primary page. Not claimed as purely equivalent deletion.",
            "Correspondence purposes now explicitly include requests for approval and approval responses according to actual relationship and authority. The correspondence leaf and formal-addressing are separate pending work, unchanged here.",
        ],
        "validation": {
            "exactly_four_changed_paths": True,
            "same_complete_file_set": True,
            "directory_unchanged_except_approved_correspondence_wording": True,
            "capability_index_unchanged": True,
            "all_references_reachable": len(refs),
            "local_links_resolve": True,
            "reference_graph_acyclic_excluding_skill_context_links": True,
            "index_conflict_page_no_mutual_calls": True,
            "new_file_call_edges": 0,
            "former_table_targets_reachable_from_index": len(old_routing_targets),
            "all_other_files_byte_identical": True,
            "copied_fingerprints_match": True,
            "canonical_unchanged": True,
        },
        "artifact_sha256": {name: sha256((DEST / name).read_bytes()) for name in ("baseline.manifest.json", "candidate.manifest.json", "changes.diff")},
        "not_run": ["writing models", "network", "public test runner", "canonical or mirror adoption", "commit"],
        "limits": "Structural and ownership checks only. Reachability is not evidence of actual reads; fallback and writing behavior need separate real-task evidence.",
    }
    write_json(DEST / "build.json", build)
    print(json.dumps({
        "output": str(DEST),
        "build_json_sha256": sha256((DEST / "build.json").read_bytes()),
        "fingerprints": {arm: record["fingerprint"] for arm, record in records.items()},
        "changed_page_chars": char_changes,
        "markdown_chars_delta": build["markdown_chars_delta"],
        "validation": build["validation"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
