"""Build the established flat WorkBuddy ZIP from a committed canonical Skill."""

from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SLUG = "chinese-official-writing"


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def committed_files(ref: str) -> tuple[str, dict[str, bytes]]:
    commit = git_bytes("rev-parse", f"{ref}^{{commit}}").decode().strip()
    listing = git_bytes("ls-tree", "-r", commit, "--", SLUG).decode().splitlines()
    files = {}
    for row in listing:
        attributes, path = row.split("\t", 1)
        if attributes.split()[0] not in {"100644", "100755"}:
            raise ValueError(f"Unsupported source entry: {path}")
        name = PurePosixPath(path).relative_to(SLUG).as_posix()
        parts = PurePosixPath(name).parts
        allowed = name in {"SKILL.md", "README.md", "LICENSE", "agents/openai.yaml"}
        allowed |= parts[0] == "references" and name.endswith(".md")
        allowed |= parts[0] == "scripts" and name.endswith(".py")
        if not allowed or ".." in parts or "__pycache__" in parts:
            raise ValueError(f"Unexpected product file: {name}")
        files[name] = git_bytes("show", f"{commit}:{path}")
    if not {"SKILL.md", "README.md", "LICENSE"} <= files.keys():
        raise ValueError("Incomplete canonical Skill")
    return commit, files


def workbuddy_entry(source: bytes, version: str) -> bytes:
    text = source.decode("utf-8-sig")
    marker = f"name: {SLUG}\n"
    if text.count(marker) != 1:
        raise ValueError("Unexpected canonical Skill identity")
    fields = {
        "version": version,
        "display_name": "中文公文写作",
        "display_name_en": "Chinese Official Writing",
        "description_zh": "中文公文、事务性材料和新闻稿件的起草、改写、审校与格式处理",
        "description_en": "Draft, revise, and review Chinese official documents, administrative materials, and news writing.",
    }
    additions = "".join(f"{key}: {json.dumps(value, ensure_ascii=False)}\n" for key, value in fields.items())
    return text.replace(marker, marker + additions, 1).encode("utf-8")


def build(ref: str, version: str, output_dir: Path, snapshot: Path, manifest: Path) -> dict:
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        raise ValueError("Invalid version")
    commit, source = committed_files(ref)
    snapshot.mkdir(parents=True, exist_ok=False)
    for name, data in source.items():
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    payload = {**source, "SKILL.md": workbuddy_entry(source["SKILL.md"], version)}
    archive = output_dir.resolve() / f"中文公文写作-WorkBuddy-v{version}-{commit[:8]}-无Hooks.zip"
    timestamp = time.gmtime(int(git_bytes("show", "-s", "--format=%ct", commit)))[:6]
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    result = {
        "version": version, "source_commit": commit, "archive": str(archive),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "layout": "flat-root", "snapshot": str(snapshot.resolve()),
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payload.items())},
        "adapted_files": ["SKILL.md frontmatter only"],
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    result = build(args.ref, args.version, args.output_dir, args.snapshot, args.manifest)
    print(json.dumps({key: value for key, value in result.items() if key != "files"}, ensure_ascii=False, indent=2))
