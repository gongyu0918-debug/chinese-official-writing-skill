"""Freeze upload directories from Git and verify their mechanical interfaces."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
OUTPUT = ROOT / "output/release-2.0.4"
PRODUCT = "f8b2e86f2cefa9a660c21faca37b24f42cb3ee64"
BASELINE = "20d89158"
VERSION = "2.0.4"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def save(name, value):
    (EVIDENCE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def manifest(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file()}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=False)
    source = OUTPUT / "source"
    for name in git("ls-tree", "-r", "--name-only", PRODUCT, "chinese-official-writing").decode().splitlines():
        target = source / Path(name).relative_to("chinese-official-writing")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git("show", f"{PRODUCT}:{name}"))

    spec = importlib.util.spec_from_file_location("skillhub_builder", ROOT / "maintenance/tools/build_skillhub_package.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.CANONICAL = source
    builder.ROOT_LICENSE = source / "LICENSE"
    skillhub = OUTPUT / "skillhub"
    builder.build_package(skillhub, version=VERSION)

    clawhub = OUTPUT / "clawhub"
    clawhub.mkdir()
    for name in manifest(source):
        if name == "agents/openai.yaml":
            continue
        target = clawhub / ("LICENSE.md" if name == "LICENSE" else name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)

    source_files = manifest(source)
    for folder in (skillhub, clawhub):
        for name in manifest(folder):
            assert "hooks" not in Path(name).parts and not name.endswith("review_gate.py")
            assert "maintenance" not in Path(name).parts and "__pycache__" not in Path(name).parts
            if name == "_meta.json":
                assert json.loads((folder / name).read_text()) == {"slug": "chinese-official-writing", "version": VERSION}
            elif name == "SKILL.md" and folder == skillhub:
                assert builder.split_skill((folder / name).read_text(encoding="utf-8"))[1] == builder.split_skill((source / name).read_text(encoding="utf-8"))[1]
            else:
                original = "LICENSE" if name == "LICENSE.md" else name
                assert (folder / name).read_bytes() == (source / original).read_bytes(), name
    assert not git("diff", BASELINE, PRODUCT, "--", "chinese-official-writing/SKILL.md", "chinese-official-writing/references", "chinese-official-writing/scripts")

    checks = {}

    def run(label, command, expected=0):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        checks[label] = {"command": command, "exit_code": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr}
        save("checks.json", checks)
        assert result.returncode == expected, (label, result.stdout, result.stderr)

    run("product_paths", [sys.executable, "maintenance/tools/audit_product_surface.py", "--root", str(source)])
    run("skill_format", [sys.executable, str(Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"), str(source)])
    clean = OUTPUT / "clean.txt"
    clean.write_text("检查情况说明\n\n本次检查发现两处接线松动，已完成紧固。检查记录结论为未发现重大隐患。\n", encoding="utf-8")
    marked = OUTPUT / "marked.txt"
    marked.write_text("_关于更新设备的申请_\n\n+ 请审核本次申请。\n", encoding="utf-8")
    placeholder = OUTPUT / "placeholder.txt"
    placeholder.write_text("关于更新设备的申请\n\n[单位名称]申请更新设备。\n", encoding="utf-8")
    lint = [sys.executable, str(skillhub / "scripts/prose_lint.py"), "--delivery-mode", "draft-body", "--structure", "--format", "--strict"]
    run("supported_statement", [*lint, str(clean)])
    run("markdown_detected", [*lint, str(marked)], 1)
    run("requested_markdown_allowed", [*lint, "--allow-markdown", str(marked)])
    run("placeholder_detected", [*lint, str(placeholder)], 1)
    run("word_count", [sys.executable, str(skillhub / "scripts/draft_length.py"), "--json", str(clean)])
    measured = json.loads(checks["word_count"]["stdout"])[0]["count"]
    assert measured == sum(not char.isspace() for char in clean.read_text(encoding="utf-8"))
    run("skillhub_local_preflight", [sys.executable, str(Path.home() / ".skillhub/skills_store_cli.py"), "--skip-self-upgrade", "publish", str(skillhub), "--version", VERSION, "--dry-run", "--json"])

    expected_files = set(source_files) - {"agents/openai.yaml", "LICENSE"} | {"LICENSE.md"}
    assert set(manifest(clawhub)) == expected_files
    assert set(manifest(skillhub)) == expected_files | {"_meta.json"}

    save("upload-manifest.json", {"version": VERSION, "product_commit": PRODUCT,
        "source_tree": git("rev-parse", f"{PRODUCT}:chinese-official-writing").decode().strip(),
        "canonical_sha256": source_files,
        "skillhub": {"path": str(skillhub), "files": manifest(skillhub)},
        "clawhub": {"path": str(clawhub), "files": manifest(clawhub)}})
    save("preflight.json", {"version": VERSION, "product_commit": PRODUCT, "baseline_main": BASELINE,
        "rules_and_scripts_match_approved_main": True, "upload_sources_match_committed_product": True,
        "checks": list(checks), "checks_passed": True, "new_native_writing_calls": 0,
        "existing_writing_evidence": "../script-fixes-merge-20260916/assessment.md",
        "existing_script_tests": "142 checks; same script bytes, not rerun",
        "desktop_and_adaptation_archives": "NOT_CHANGED"})
    print(json.dumps({"status": "PASS", "canonical_files": len(source_files),
        "skillhub_files": len(manifest(skillhub)), "clawhub_files": len(manifest(clawhub)),
        "checks": len(checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
