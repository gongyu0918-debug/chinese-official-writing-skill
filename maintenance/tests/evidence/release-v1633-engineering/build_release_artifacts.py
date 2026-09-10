"""Build and verify local release artifacts; never submit or publish them."""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
FIRST_OUTPUT = ROOT / "output/release-v1633-artifacts"
OUTPUT = ROOT / "output/release-v1633-artifacts-final"
VERSION = "1.6.33"
PRODUCT_COMMIT = "5d84c5d3e52dac0b006d6c6aa5a06d32e080d2b0"
PRODUCT_TREE = "bc9f538eab44cf8d83d3e6af33018c52bd24d658"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_tool(name: str):
    path = ROOT / "maintenance/tools" / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def file_manifest(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): digest(path.read_bytes())
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def package_zip(label: str, directory: Path, files: dict[str, str]) -> dict:
    path = OUTPUT / f"chinese-official-writing-v{VERSION}-{label}.zip"
    timestamp = int(git("show", "-s", "--format=%ct", PRODUCT_COMMIT))
    stamp = datetime.fromtimestamp(timestamp, timezone.utc).timetuple()[:6]
    if not path.exists():
        with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for relative in files:
                item = zipfile.ZipInfo(directory.name + "/" + relative, stamp)
                item.create_system = 3
                item.external_attr = 0o100644 << 16
                archive.writestr(item, (directory / relative).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        expected = {directory.name + "/" + name: sha for name, sha in files.items()}
        assert set(archive.namelist()) == set(expected)
        assert all(digest(archive.read(name)) == sha for name, sha in expected.items())
    return {"path": str(path), "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size, "verified_members": len(files)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finalize-existing", action="store_true", help="Verify existing completed builds and reuse recorded quick checks; do not rebuild or rerun checks")
    args = parser.parse_args()
    full = json.loads((EVIDENCE / "full-engineering.json").read_text(encoding="utf-8"))
    assert full["exit_code"] == 0 and full["full_run_number"] == 1
    assert git("rev-parse", "HEAD:chinese-official-writing").decode().strip() == PRODUCT_TREE
    assert not git("diff", "--name-only", "HEAD", "--", "chinese-official-writing").strip()
    if args.finalize_existing:
        assert FIRST_OUTPUT.is_dir() and not OUTPUT.exists()
        shutil.copytree(FIRST_OUTPUT, OUTPUT)
    else:
        assert not OUTPUT.exists(), "Choose a new audited destination instead of overwriting artifacts"
        OUTPUT.mkdir(parents=True)
    canonical = ROOT / "chinese-official-writing"
    tracked = git("ls-tree", "-r", "--name-only", PRODUCT_COMMIT, "--", "chinese-official-writing").decode().splitlines()
    relative_files = {name.removeprefix("chinese-official-writing/") for name in tracked}
    actual_files = {
        path.relative_to(canonical).as_posix()
        for path in canonical.rglob("*") if path.is_file()
        and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    assert actual_files == relative_files, "Untracked canonical content must not enter generated packages"

    github = OUTPUT / "github/chinese-official-writing"
    if not args.finalize_existing:
        for relative in sorted(relative_files):
            target = github / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git("show", f"{PRODUCT_COMMIT}:chinese-official-writing/{relative}"))
    assert file_manifest(github) == {name: digest(git("show", f"{PRODUCT_COMMIT}:chinese-official-writing/{name}")) for name in relative_files}

    sync = load_tool("sync_adapters")
    package_root = (OUTPUT / "compatibility-packages").resolve()
    for mode, template in sync.TARGETS.items():
        target = (package_root / template.relative_to(sync.PACKAGES)).resolve()
        assert target.is_relative_to(package_root)
        for relative in sync.TARGET_EXCLUDES[mode]:
            assert (target / relative).resolve().is_relative_to(target)
    skillhub = OUTPUT / "skillhub/chinese-official-writing"
    if args.finalize_existing:
        targets = {mode: package_root / template.relative_to(sync.PACKAGES) for mode, template in sync.TARGETS.items()}
        assert all(target.is_dir() for target in targets.values()) and skillhub.is_dir()
        skillhub_result = {"output": str(skillhub), "state": "completed build reused after manifest-only EOL diagnosis"}
    else:
        targets = sync.build_packages(package_root)
        skillhub_result = load_tool("build_skillhub_package").build_package(skillhub, version=VERSION)
    clawhub = targets["openclaw"]

    # This unchanged page was LF in the previous public artifacts. Keep its
    # original Git bytes when the Windows checkout adds CRLF during copying.
    index_name = "references/reference-index.md"
    index_bytes = git("show", f"{PRODUCT_COMMIT}:chinese-official-writing/{index_name}")
    assert index_bytes == git("show", f"v1.6.32:chinese-official-writing/{index_name}")
    preserved = []
    for directory in [skillhub, *targets.values()]:
        path = directory / index_name
        before = path.read_bytes()
        assert before.replace(b"\r\n", b"\n") == index_bytes
        if before != index_bytes:
            path.write_bytes(index_bytes)
            preserved.append({"path": str(path), "before_sha256": digest(before), "after_sha256": digest(index_bytes)})

    validator = Path("C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py")
    quick_roots = [canonical, *[targets[key] for key in ("agents", "qwen", "qwenwork", "hermes")]]
    if args.finalize_existing:
        quick = json.loads((EVIDENCE / "quick-validation.json").read_text(encoding="utf-8"))
        expected_roots = [canonical, *[FIRST_OUTPUT / path.relative_to(OUTPUT) for path in quick_roots[1:]]]
        assert [item["root"] for item in quick] == [str(path) for path in expected_roots]
    else:
        quick = []
        for directory in quick_roots:
            command = [sys.executable, str(validator), str(directory)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True)
            quick.append({"root": str(directory), "command": command, "exit_code": result.returncode,
                          "stdout": result.stdout.decode("utf-8", errors="replace"),
                          "stderr": result.stderr.decode("utf-8", errors="replace")})
        write_json(EVIDENCE / "quick-validation.json", quick)
    assert len(quick) == 5 and all(item["exit_code"] == 0 for item in quick)

    old_manifests = json.loads((ROOT / "maintenance/tests/evidence/release-v1632/package-manifests.json").read_text(encoding="utf-8"))
    version_files = {
        "hooks/adapters/" + name for name in (
            "claude-code/manifest.json", "codebuddy/manifest.json", "codex/manifest.json",
            "deepseek-harness/package.json", "kimi-code/manifest.json",
            "qwen-code/manifest.json", "zcode/manifest.json",
        )
    }
    surfaces = {}
    checksums = []
    for label, directory in (("github", github), ("skillhub", skillhub), ("clawhub", clawhub)):
        files = file_manifest(directory)
        forbidden = [name for name in files if any(part in {".git", "__pycache__", "maintenance", "output", "paid"} for part in Path(name).parts) or name.endswith(".pyc")]
        assert not forbidden, (label, forbidden)
        changes = None
        if label in old_manifests:
            old_files = old_manifests[label]["files"]
            assert set(files) == set(old_files), (label, "public package file set changed")
            changes = sorted(name for name in files if files[name] != old_files[name])
            allowed = {"SKILL.md", "references/anti-ai-patterns.md"}
            if label == "skillhub":
                allowed |= version_files | {"_meta.json"}
            assert set(changes) == allowed, (label, changes, allowed)
        if label == "clawhub":
            assert not any(name.startswith("hooks/") for name in files)
            assert not {"references/delivery-review-gate.md", "scripts/review_gate.py", "agents/openai.yaml"} & set(files)
        manifest = OUTPUT / "manifests" / f"{label}.json"
        write_json(manifest, {"version": VERSION, "surface": label, "count": len(files), "files": files})
        archive = package_zip(label, directory, files)
        surfaces[label] = {"directory": str(directory), "count": len(files), "files": files,
                           "directory_content_sha256": digest(json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()),
                           "manifest": {"path": str(manifest), "sha256": digest(manifest.read_bytes())},
                           "zip": archive, "changed_from_v1632_manifest": changes}
        checksums.extend([f"{archive['sha256']}  {Path(archive['path']).name}", f"{digest(manifest.read_bytes())}  manifests/{label}.json"])
    sums = OUTPUT / "SHA256SUMS.txt"
    sums.write_text("\n".join(checksums) + "\n", encoding="utf-8")
    assert git("rev-parse", "HEAD:chinese-official-writing").decode().strip() == PRODUCT_TREE
    assert not git("diff", "--name-only", "HEAD", "--", "chinese-official-writing").strip()
    record = {"version": VERSION, "source_product_commit": PRODUCT_COMMIT, "head_at_build": git("rev-parse", "HEAD").decode().strip(),
              "canonical_tree_git_sha1": PRODUCT_TREE, "base_tag": "v1.6.32", "surfaces": surfaces,
              "skillhub_builder_result": skillhub_result, "quick_validation_passed": 5,
              "quick_validation_reused_after_byte_preservation": args.finalize_existing,
              "unchanged_page_byte_preservation": preserved,
              "first_attempt_artifacts_preserved": str(FIRST_OUTPUT) if args.finalize_existing else None,
              "checksums": {"path": str(sums), "sha256": digest(sums.read_bytes())},
              "directory_hash_definition": "SHA-256 of UTF-8 compact sorted JSON mapping relative file path to file SHA-256",
              "external_submission_performed": False, "product_bytes_unchanged": True}
    write_json(EVIDENCE / "package-manifests.json", record)
    print(json.dumps({"surfaces": {key: {"count": item["count"], "zip": item["zip"], "manifest": item["manifest"]} for key, item in surfaces.items()}, "checksums": record["checksums"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
