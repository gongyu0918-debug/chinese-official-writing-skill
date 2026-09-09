"""Look up cold evidence metadata; extract one verified file into ignored output/."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "maintenance/docs/evidence/archive-index.jsonl"


def load_index(path: Path = INDEX) -> dict[str, dict]:
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        name = item["path"]
        relative = PurePosixPath(name)
        if (relative.is_absolute() or ".." in relative.parts or "\\" in name
                or not name.startswith("maintenance/tests/evidence/")):
            raise ValueError(f"unsafe evidence path: {name}")
        if name in entries:
            raise ValueError(f"duplicate archive entry: {name}")
        entries[name] = item
    return entries


def verified_bytes(item: dict, archive: Path | None = None) -> bytes:
    if archive is not None:
        with zipfile.ZipFile(archive) as package:
            data = package.read(item["path"])
    else:
        blob = item["git_blob"]
        if len(blob) != 40 or any(c not in "0123456789abcdef" for c in blob):
            raise ValueError("invalid Git blob id")
        result = subprocess.run(
            ["git", "cat-file", "blob", blob], cwd=ROOT,
            capture_output=True, check=False,
        )
        if result.returncode:
            raise ValueError("archive blob unavailable; use a full Git clone or --archive ZIP")
        data = result.stdout
    if len(data) != item["size"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
        raise ValueError(f"archive checksum mismatch: {item['path']}")
    return data


def extract(item: dict, output: Path, archive: Path | None = None) -> Path:
    target = output.resolve() / item["path"]
    if not target.resolve().is_relative_to((ROOT / "output").resolve()):
        raise ValueError("extraction destination must stay inside repository output/")
    data = verified_bytes(item, archive)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(data)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    lookup = sub.add_parser("find", help="search paths only; do not load original evidence")
    lookup.add_argument("query")
    lookup.add_argument("--limit", type=int, default=20)
    restore = sub.add_parser("extract", help="restore exactly one file, without overwriting")
    restore.add_argument("path")
    restore.add_argument("--output", type=Path, default=ROOT / "output/evidence-extracted")
    restore.add_argument("--archive", type=Path)
    args = parser.parse_args()
    index = load_index()
    if args.command == "find":
        matches = [v for k, v in index.items() if args.query.casefold() in k.casefold()]
        print(json.dumps({"matches": len(matches), "entries": matches[:max(0, args.limit)]}, ensure_ascii=False, indent=2))
    else:
        if args.path not in index:
            parser.error("path is not in the cold archive index")
        target = extract(index[args.path], args.output, args.archive)
        print(json.dumps({"path": str(target), "sha256": index[args.path]["sha256"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
