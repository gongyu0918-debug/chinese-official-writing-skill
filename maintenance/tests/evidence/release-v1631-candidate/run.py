"""Capture checks and prove the selected v1.6.31 slice without model calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = "d2f97ba05e592712ec4b73decceefb3fd29d7c5e"
SOURCE = "a440f97e8787a1143835c2c04342a3d28e00068f"
SKILL_ROOTS = ["chinese-official-writing"] + [
    f"packages/{host}/skills/chinese-official-writing"
    for host in ("agent-skills", "qwen-code", "qwenwork", "hermes")
] + ["packages/openclaw/skills/chinese_official_writing"]


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def blob(ref, name):
    return git("show", ref + ":" + name)


def scope():
    paths = git("ls-tree", "-r", "--name-only", BASE, "--", "chinese-official-writing", "packages").decode().splitlines()
    current = git("ls-files", "--", "chinese-official-writing", "packages").decode().splitlines()
    assert set(paths) == set(current), "product assets added or removed"
    entry = "chinese-official-writing/SKILL.md"
    paragraph = blob(SOURCE, entry).decode().split("## 任务模式路由与交付模式\n\n", 1)[1].split("\n\n", 1)[0] + "\n\n"
    facts = blob(SOURCE, "chinese-official-writing/references/information-selection.md")
    changed = []
    writing_count = 0
    metadata_count = 0
    for name in paths:
        old = blob(BASE, name)
        expected = old
        if name in {root + "/SKILL.md" for root in SKILL_ROOTS}:
            expected = old.replace("## 任务模式路由与交付模式\n\n".encode(), ("## 任务模式路由与交付模式\n\n" + paragraph).encode(), 1)
            writing_count += 1
            if name.startswith("packages/openclaw/"):
                expected = expected.replace(b'version: "1.6.30"', b'version: "1.6.31"', 1)
        elif name in {root + "/references/information-selection.md" for root in SKILL_ROOTS}:
            expected = facts
            writing_count += 1
        elif name.startswith("chinese-official-writing/hooks/adapters/") and b'"version": "1.6.30"' in old:
            expected = old.replace(b'"version": "1.6.30"', b'"version": "1.6.31"', 1)
            metadata_count += 1
        actual = (ROOT / name).read_bytes()
        assert actual == expected, "unexpected bytes: " + name
        if actual != old:
            changed.append(dict(path=name, bytes=len(actual), delta_bytes=len(actual)-len(old), sha256=hashlib.sha256(actual).hexdigest()))
    assert writing_count == 12 and metadata_count == 7
    historical = json.loads((OUT / "historical-evidence-manifest.json").read_text(encoding="utf-8"))
    for item in historical["files"]:
        assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
    save("scope-check.json", dict(base=BASE, selected_source=SOURCE, result="PASS", product_files=len(paths), changed_files=changed, writing_files=12, version_manifests=7, historical_files=len(historical["files"]), new_model_calls=0, excluded=["R26", "R9", "R10", "HK-002b"]))
    print(json.dumps(dict(scope="PASS", changed=len(changed), historical=len(historical["files"]))))


def run(name, command):
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace", timeout=900)
    save(name + ".json", dict(command=command, return_code=result.returncode, seconds=round(time.monotonic()-started, 3), stdout=result.stdout, stderr=result.stderr))
    print(json.dumps(dict(check=name, return_code=result.returncode, tail=(result.stdout+result.stderr)[-1400:]), ensure_ascii=False))
    return result.returncode


if __name__ == "__main__":
    if sys.argv[1] == "scope":
        scope()
    else:
        sys.exit(run(sys.argv[1], sys.argv[2:]))
