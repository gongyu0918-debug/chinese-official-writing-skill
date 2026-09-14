"""Refine two formulaic-use lines in a new copy of the frozen correspondence arm."""
from pathlib import Path
import difflib
import json
import shutil
import sys

sys.dont_write_bytecode = True
from build import ROOT, EVIDENCE, manifest, fingerprint, changed_reference_links

DEST = ROOT / "output/genre-purpose-r16/correspondence-v2"
PAGE = "references/formulaic-language.md"
REPLACEMENTS = [
    (
        "- 报告不写请批语，函不写成命令，通知、批复、请示和函的口吻保持各自功能。",
        "- 报告不写请批语；函按商洽、请求批准或有权审批答复的实际用途选择措辞，语气与收发双方权限相符。",
    ),
    (
        "| 请示收束 | `妥否，请批示`、`请予审批`、`请予批复` | 只用于有明确请批事项的请示或申请 |",
        "| 请批收束 | `妥否，请批示`、`请予审批`、`请予批准`、`请予批复` | 请示、申请或请求批准的函有明确请批事项时，按行文关系和收文方权限选择 |",
    ),
]


def main():
    assert not DEST.exists(), f"Destination must be new: {DEST}"
    frozen = json.loads((EVIDENCE / "build.json").read_text(encoding="utf-8"))
    for arm, record in frozen["arms"].items():
        assert manifest(ROOT / record["path"]) == record["files"], arm
    source = ROOT / frozen["arms"]["correspondence"]["path"]
    source_files = manifest(source)
    canonical_before = manifest(ROOT / "chinese-official-writing")
    shutil.copytree(source, DEST)
    page = DEST / PAGE
    before = page.read_text(encoding="utf-8")
    after = before
    for old, new in REPLACEMENTS:
        assert after.count(old) == 1, old
        after = after.replace(old, new)
    assert sum(a != b for a, b in zip(before.splitlines(), after.splitlines())) == 2
    assert len(before.splitlines()) == len(after.splitlines())
    page.write_text(after, encoding="utf-8", newline="\n")
    files = manifest(DEST)
    assert files.keys() == source_files.keys()
    changes_from_parent = sorted(p for p in files if files[p] != source_files[p])
    assert changes_from_parent == [PAGE]
    baseline_files = frozen["arms"]["baseline"]["files"]
    changes_from_baseline = sorted(p for p in files if files[p] != baseline_files[p])
    assert changes_from_baseline == [
        "references/formal-addressing.md", PAGE, "references/genre-playbook-correspondence.md"
    ]
    links = changed_reference_links(DEST, [PAGE])
    for arm, record in frozen["arms"].items():
        assert manifest(ROOT / record["path"]) == record["files"], arm
    assert manifest(ROOT / "chinese-official-writing") == canonical_before
    diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                   fromfile="correspondence/" + PAGE, tofile="correspondence-v2/" + PAGE))
    (DEST.parent / "correspondence-v2.diff").write_text(diff, encoding="utf-8")
    record = {
        "source": source.relative_to(ROOT).as_posix(),
        "source_fingerprint": fingerprint(source_files),
        "baseline_fingerprint": frozen["arms"]["baseline"]["fingerprint"],
        "path": DEST.relative_to(ROOT).as_posix(), "fingerprint": fingerprint(files),
        "file_count": len(files), "files": files,
        "changed_from_correspondence": changes_from_parent,
        "changed_from_baseline": changes_from_baseline,
        "replaced_lines": [{"before": old, "after": new} for old, new in REPLACEMENTS],
        "changed_reference_links": links, "old_three_arms_unchanged": True,
        "canonical_unchanged": True, "real_writing_run": False,
        "dependency": "Combine the existing route prototype for the index and genre-routing changes.",
    }
    with (EVIDENCE / "correspondence-v2.binding.json").open("x", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({k: v for k, v in record.items() if k != "files"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
