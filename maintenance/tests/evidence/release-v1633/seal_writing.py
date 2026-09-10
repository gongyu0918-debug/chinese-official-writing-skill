"""Seal the twelve Q1 executions and frozen inputs; exclude runtime profiles."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
OUT = ROOT / "output/release-v1633/word-guidance"
summary = json.loads((EVIDENCE / "writing-summary.json").read_text(encoding="utf-8"))
assert summary["attempts"] == 12
assert summary["technical_valid_finals"] == 11
assert summary["complete_same_effort_pairs"] == 5
files = {p for p in (OUT / "frozen input").rglob("*") if p.is_file()}
for name in ("final.txt", "prompt.txt", "receipt.json", "trace.jsonl", "stderr.txt"):
    files.update((OUT / "runs").glob("*/*/*/*/" + name))
assert len(list((OUT / "runs").glob("*/*/*/*/receipt.json"))) == 12
assert len(list((OUT / "runs").glob("*/*/*/*/final.txt"))) == 11
files.update(OUT.glob("catalog-*.json"))
files.update([OUT / "freeze.json", OUT / "receipts.json"])
files.update(p for p in EVIDENCE.iterdir() if p.is_file() and p.name != "archive.json")
files.add(ROOT / "maintenance/docs/release-v1633-writing-validation.md")
manifest = {
    p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(files)
}
archive = Path(
    "F:/Workspaces/chinese-official-writing-skill-archives/experiments/"
    "skill-lightening-20260911/v1633-q1-writing-evidence.zip"
)
archive.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(archive, "x", compression=ZIP_DEFLATED) as bundle:
    for name in manifest:
        bundle.write(ROOT / name, name)
    bundle.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
with ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    for name, expected in manifest.items():
        assert hashlib.sha256(bundle.read(name)).hexdigest() == expected
record = {
    "archive": str(archive),
    "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "members_verified": len(manifest),
    "archive_member_count_including_manifest": len(manifest) + 1,
    "attempts": 12,
    "valid_finals": 11,
    "complete_same_effort_pairs": 5,
    "baseline_commit": summary["baseline_commit"],
    "writing_candidate_commit": summary["writing_candidate_commit"],
    "scope": "Both complete frozen product trees; all twelve prompts, receipts, traces and stderr; eleven valid finals; registered tasks and writing review. Includes the GLM max transport failure. No account profiles, codex-home, temporary work/cache folders, or engineering/package results.",
}
(EVIDENCE / "archive.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(record, ensure_ascii=False))
