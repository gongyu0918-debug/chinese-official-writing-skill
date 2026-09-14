"""Narrow the inherited inference bridge in one copied prototype script."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "output/reference-integration-r16-final/candidate/scripts/prose_lint.py"
OUT = ROOT / "output/prose-business-conditional-r16"
TARGET = OUT / "candidate/scripts/prose_lint.py"
SOURCE_SHA256 = "513934d60e145087d992b2383dc92a522ecd9497446194ce1885e937800486fc"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError("Expected exactly one source anchor")
    return text.replace(old, new, 1)


def main() -> None:
    data = SOURCE.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("Final frozen script no longer matches the specified baseline")
    original = data.decode("utf-8")
    candidate = replace_once(original, "PROTECTIVE_INFERENCE_BRIDGE_CHARS = 70\n", "")
    candidate = replace_once(
        candidate,
        '        r"(?:尚|仍|还|目前)?(?:不能|无法|不足以|不宜)(?:仅凭|单凭|据此|直接据此|由此)?"\n'
        '        rf"[^。！？\\n]{{0,{PROTECTIVE_INFERENCE_BRIDGE_CHARS}}}"\n',
        '        r"(?:尚|仍|还|目前)?(?:不能|无法|不足以|不宜)"\n'
        '        r"(?:(?:直接)?(?:据此|由此))?"\n'
        '        r"(?:(?:直接|充分|准确)地?)?"\n',
    )
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, TARGET)
    TARGET.write_text(candidate, encoding="utf-8", newline="\n")
    patch = "".join(difflib.unified_diff(
        original.splitlines(keepends=True), candidate.splitlines(keepends=True),
        fromfile="final-frozen/scripts/prose_lint.py", tofile="candidate/scripts/prose_lint.py"))
    (OUT / "candidate.diff").write_text(patch, encoding="utf-8")
    manifest = {"source": str(SOURCE), "source_sha256": SOURCE_SHA256,
                "candidate": str(TARGET), "candidate_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
                "source_unchanged": SOURCE.read_bytes() == data,
                "candidate_files": [path.relative_to(OUT / "candidate").as_posix()
                                    for path in (OUT / "candidate").rglob("*") if path.is_file()]}
    (OUT / "build.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
