"""Compare the bounded DOCX font-size prototype without modifying source files."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/prose-docx-zero-r17"
INVENTORY = ROOT / "output/final-word-qa-r17/artifact-inventory.json"
CANONICAL = ROOT / "chinese-official-writing/scripts/prose_lint.py"
BASE_HASH = "d69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc"
BAD_ID = "m4-scope_word_complete_signoff-candidate"
BAD_HASH = "0989cecd96b1e85a5bc7eccdb7b0e4ca16260ecb23ae61161a5fd5fe19a6e068"
LABEL = "docx-zero-font-size"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
SCRIPTS = {arm: OUT / arm / "scripts/prose_lint.py" for arm in ("baseline", "candidate")}
CALLS: list[dict] = []
CHECKS: list[str] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, description: str) -> None:
    assert condition, description
    CHECKS.append(description)


def run(case: str, arm: str, path: Path | str, flags: list[str], stdin: str | None = None) -> dict:
    folder = OUT / "calls" / case / arm
    folder.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-B", str(SCRIPTS[arm]), *flags, str(path)]
    completed = subprocess.run(
        command, input=stdin.encode("utf-8") if stdin is not None else None,
        capture_output=True, cwd=ROOT, timeout=30,
    )
    (folder / "stdout.txt").write_bytes(completed.stdout)
    (folder / "stderr.txt").write_bytes(completed.stderr)
    findings = json.loads(completed.stdout.decode("utf-8")) if "--json" in flags else None
    record = {
        "case": case, "arm": arm, "command": command, "exit_code": completed.returncode,
        "script_sha256": sha(SCRIPTS[arm]),
        "input_sha256": sha(path) if isinstance(path, Path) and path.is_file() else None,
        "stdin_sha256": hashlib.sha256(stdin.encode("utf-8")).hexdigest() if stdin is not None else None,
        "stdout": str(folder / "stdout.txt"), "stdout_sha256": sha(folder / "stdout.txt"),
        "stderr": str(folder / "stderr.txt"), "stderr_sha256": sha(folder / "stderr.txt"),
        "finding_count": len(findings) if findings is not None else None,
        "zero_size_count": sum(item["label"] == LABEL for item in findings) if findings is not None else None,
    }
    (folder / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CALLS.append(record)
    return {**record, "findings": findings, "stdout_bytes": completed.stdout, "stderr_bytes": completed.stderr}


def pair(case: str, path: Path | str, flags: list[str], stdin: str | None = None) -> tuple[dict, dict]:
    return tuple(run(case, arm, path, flags, stdin) for arm in SCRIPTS)


def compatible(base: dict, candidate: dict, case: str) -> None:
    ordinary = [item for item in candidate["findings"] if item["label"] != LABEL]
    check(ordinary == base["findings"], f"{case}: existing findings unchanged")
    expected_keys = {"path", "line", "severity", "label", "match", "excerpt"}
    check(all(set(item) == expected_keys for item in candidate["findings"]), f"{case}: six-field JSON schema unchanged")


def docx(name: str, body: str, extra: dict[str, str] | None = None, namespace: str = W) -> Path:
    path = OUT / "fixtures" / (name + ".docx")
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", f'<w:document xmlns:w="{namespace}"><w:body>{body}</w:body></w:document>')
        for part, xml in (extra or {}).items():
            archive.writestr(part, xml)
    return path


def r(text: str, properties: str = "") -> str:
    return f"<w:r><w:rPr>{properties}</w:rPr><w:t>{text}</w:t></w:r>"


def p(text: str) -> str:
    return f"<w:p>{text}</w:p>"


def load(arm: str):
    name = "zero_font_probe_" + arm
    spec = importlib.util.spec_from_file_location(name, SCRIPTS[arm])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    check(sha(CANONICAL) == BASE_HASH == sha(SCRIPTS["baseline"]), "canonical and baseline hash binding")
    candidate_hash = sha(SCRIPTS["candidate"])
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    check(len(inventory) == 12 and len({row["id"] for row in inventory}) == 12, "12 unique real artifacts")
    frozen = {}
    for row in inventory:
        path = Path(row["recovered"])
        check(path.is_file() and sha(path) == row["docx_sha256"], row["id"] + ": source hash matches inventory")
        frozen[str(path)] = sha(path)
        if row["id"] == BAD_ID:
            check(sha(path) == BAD_HASH, "known failure DOCX exact hash")
    (OUT / "input-manifest.json").write_text(json.dumps({
        "canonical_sha256": BASE_HASH, "baseline_sha256": BASE_HASH, "candidate_sha256": candidate_hash,
        "inventory_sha256": sha(INVENTORY), "real_inputs": frozen,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    real_results = []
    for row in inventory:
        path = Path(row["recovered"])
        base, candidate = pair(row["id"] + "-format", path, ["--json", "--format", "--structure", "--delivery-mode", "draft-body"])
        expected = 6 if row["id"] == BAD_ID else 0
        check(base["zero_size_count"] == 0 and candidate["zero_size_count"] == expected, row["id"] + ": expected zero-size detection")
        check(base["exit_code"] == candidate["exit_code"] == 0, row["id"] + ": warnings keep default exit 0")
        compatible(base, candidate, row["id"])
        off_base, off_candidate = pair(row["id"] + "-without-format", path, ["--json", "--structure", "--delivery-mode", "draft-body"])
        check(off_base["stdout_bytes"] == off_candidate["stdout_bytes"] and off_base["exit_code"] == off_candidate["exit_code"], row["id"] + ": without-format output unchanged")
        real_results.append({"id": row["id"], "docx_sha256": sha(path), "baseline_zero": base["zero_size_count"], "candidate_zero": expected, "existing_findings_equal": True, "without_format_equal": True})

    # Direct ZIP/XML fixtures exercise the existing reader; these are not rendered Word examples.
    zero = '<w:sz w:val="0"/>'
    zcs = '<w:szCs w:val="0"/>'
    positive = docx("explicit-size", p(r("学校：", zero)) + p(r("确认内容。", zero + zcs)) + p(r("型号ABC", '<w:sz w:val="00"/>')) + p(r("正常正文。", '<w:sz w:val="32"/>')))
    base, candidate = pair("fixture-explicit-size", positive, ["--json", "--format"])
    check(candidate["zero_size_count"] == 3, "explicit sz zero, dual property and zero lexical form detected once per run")
    compatible(base, candidate, "fixture-explicit-size")
    zeros = [item for item in candidate["findings"] if item["label"] == LABEL]
    check([item["line"] for item in zeros] == [2, 3, 4], "locations match extracted text lines")
    check(all("word/document.xml" in item["match"] and "文本运行" in item["match"] and "w:sz=0" in item["match"] for item in zeros), "part and run location included")

    negatives = (
        p(r("", zero)) + p(r("  \t", zero)) + p(f"<w:r><w:rPr>{zero}</w:rPr><w:br/><w:tab/></w:r>")
        + f"<w:p><w:pPr><w:rPr>{zero}</w:rPr></w:pPr>{r('普通正文。')}</w:p>"
        + p(r("历史格式。", f"<w:rPrChange><w:rPr>{zero}</w:rPr></w:rPrChange>"))
        + p(f"<w:r><w:rPr>{zero}</w:rPr><w:instrText>PAGE</w:instrText></w:r>")
        + p(r("普通ABC中文", zcs)) + p(r("hidden", zero + '<w:vanish/>'))
    )
    negative = docx("nonvisible-and-nonapplicable", negatives)
    base, candidate = pair("fixture-negative", negative, ["--json", "--format"])
    check(candidate["zero_size_count"] == 0, "empty whitespace no-text paragraph history szCs-only and explicitly hidden runs do not flag")
    compatible(base, candidate, "fixture-negative")
    visible = docx("hidden-off", p(r("可见正文。", zero + '<w:vanish w:val="0"/>')) + p(r("普通正文。", zero + '<w:webHidden w:val="1"/>')))
    _, candidate = pair("fixture-hidden-off", visible, ["--json", "--format"])
    check(candidate["zero_size_count"] == 2, "vanish=false and webHidden do not exclude ordinary zero-size text")

    extras = {f"word/{part}.xml": f'<w:{tag} xmlns:w="{W}">{p(r("附属文字。", zero))}</w:{tag}>' for part, tag in [("header1", "hdr"), ("footer1", "ftr"), ("footnotes", "footnotes"), ("endnotes", "endnotes"), ("comments", "comments")]}
    all_parts = docx("table-and-parts", f"<w:tbl><w:tr><w:tc>{p(r('表内正文。', zero))}</w:tc></w:tr></w:tbl>", extras)
    _, candidate = pair("fixture-table-and-parts", all_parts, ["--json", "--format"])
    check(candidate["zero_size_count"] == 6, "body table and existing five ancillary part types reuse format scan")
    strict_docx = docx("strict-namespace", p(r("正文。", zero)), namespace="http://purl.oclc.org/ooxml/wordprocessingml/main")
    _, candidate = pair("fixture-strict-namespace", strict_docx, ["--json", "--format"])
    check(candidate["zero_size_count"] == 1, "OOXML strict namespace direct run detection")

    inherited = docx("inherited-size", p(r("正文。")), {"word/styles.xml": f'<w:styles xmlns:w="{W}"><w:style w:type="paragraph" w:styleId="Normal"><w:rPr>{zero}</w:rPr></w:style></w:styles>'})
    _, candidate = pair("fixture-inherited-uncovered", inherited, ["--json", "--format"])
    check(candidate["zero_size_count"] == 0, "inherited zero explicitly remains outside prototype coverage")

    plain = OUT / "fixtures/plain.txt"
    plain.write_text("普通正文。w:sz=0", encoding="utf-8")
    for case, path, stdin in [("fixture-text", plain, None), ("fixture-stdin", "-", "普通正文。w:sz=0")]:
        base, candidate = pair(case, path, ["--json", "--format"], stdin)
        check(base["stdout_bytes"] == candidate["stdout_bytes"] and base["exit_code"] == candidate["exit_code"], case + ": unchanged")
    for mode in ("draft-body", "gap-note-allowed", "review-only"):
        base, candidate = pair("fixture-mode-" + mode, positive, ["--json", "--format", "--delivery-mode", mode])
        check(candidate["zero_size_count"] == 3, mode + ": format detector applies to the input DOCX")
        compatible(base, candidate, mode)
    base, candidate = pair("fixture-strict-exit", visible, ["--json", "--format", "--strict", "--fail-on", "high"])
    check(base["exit_code"] == 0 and candidate["exit_code"] == 1, "existing opt-in strict high exit contract")
    _, candidate = pair("fixture-human-output", visible, ["--format"])
    check(LABEL.encode() in candidate["stdout_bytes"] and candidate["exit_code"] == 0, "human output includes new risk without default failure")

    broken = docx("broken-late-part", p(r("正文。", zero)), {"word/header1.xml": "<broken"})
    base, candidate = pair("fixture-read-error", broken, ["--json", "--format"])
    check(base["exit_code"] == candidate["exit_code"] == 2 and base["findings"] == candidate["findings"] == [], "late XML error drops partial findings and keeps read-error exit")
    check(base["stderr_bytes"] == candidate["stderr_bytes"], "read-error stderr unchanged")

    modules = {arm: load(arm) for arm in SCRIPTS}
    for scope in ("main-document", "all"):
        for row in inventory:
            path = Path(row["recovered"])
            check(modules["baseline"].read_docx(path, scope) == modules["candidate"].read_docx(path, scope), row["id"] + ": read_docx text unchanged for " + scope)
    check(modules["baseline"].scan("label.docx", "普通正文。", include_format=True) == [], "pure scan baseline clean fixture")
    check(modules["candidate"].scan("label.docx", "普通正文。", include_format=True) == [], "pure text API does not open a DOCX-like label")
    check(all(sha(Path(path)) == digest for path, digest in frozen.items()), "12 real source DOCX bytes unchanged")
    check(sha(CANONICAL) == BASE_HASH == sha(SCRIPTS["baseline"]) and sha(SCRIPTS["candidate"]) == candidate_hash, "canonical and both frozen script hashes unchanged during probe")
    result = {"status": "PASS", "script_baseline_sha256": BASE_HASH, "script_candidate_sha256": candidate_hash,
              "real_artifacts": real_results, "checks": CHECKS, "check_count": len(CHECKS), "calls": CALLS,
              "native_candidate_invocation": "NOT_RUN", "models_invoked": 0,
              "limitations": ["szCs-only", "style inheritance", "font installation", "character compression", "rendering", "full script and hidden-state resolution"]}
    (OUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: 12 real DOCX; known failure adds 6 size risks; 11 controls add 0; {len(CHECKS)} bounded checks; {len(CALLS)} CLI calls; native NOT_RUN")


if __name__ == "__main__":
    main()
