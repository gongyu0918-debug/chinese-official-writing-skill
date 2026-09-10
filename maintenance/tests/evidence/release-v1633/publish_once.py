"""Publish the verified 1.6.33 payload once per platform; preserve every receipt."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
OUT = ROOT / "output/release-v1633-publication"
VERSION = "1.6.33"
mode = sys.argv[1]
freeze = json.loads((OUT / "freeze.json").read_text("utf-8"))
commit = freeze["release_commit"]
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() == commit
assert subprocess.check_output(["git", "rev-parse", "HEAD:chinese-official-writing"], cwd=ROOT).decode().strip() == freeze["canonical_tree"]
assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip()
assert subprocess.check_output(["git", "rev-parse", "v1.6.33^{commit}"], cwd=ROOT).decode().strip() == commit
packages = json.loads((ROOT / "maintenance/tests/evidence/release-v1633-engineering/package-manifests.json").read_text("utf-8"))
for label, surface in packages["surfaces"].items():
    root = Path(surface["directory"])
    actual = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
    assert actual == surface["files"], label
    archive = surface["zip"]
    assert hashlib.sha256(Path(archive["path"]).read_bytes()).hexdigest() == archive["sha256"]
notes = (E / "release-notes.md").read_text("utf-8")
assert not any(term in notes for term in ["拆分", "拆出", "拆了一", "拆出来"])
commands = {
    "github-push": ["git", "push", "--atomic", "origin", "HEAD:refs/heads/main", "refs/tags/v1.6.33"],
    "github-release": ["C:/Program Files/GitHub CLI/gh.exe", "release", "create", "v1.6.33",
        packages["surfaces"]["github"]["zip"]["path"], "--repo", "gongyu0918-debug/chinese-official-writing-skill",
        "--verify-tag", "--title", "v1.6.33", "--notes-file", str(E / "release-notes.md")],
    "skillhub": ["C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe", "C:/Users/admin/.skillhub/skills_store_cli.py",
        "--skip-self-upgrade", "publish", packages["surfaces"]["skillhub"]["directory"], "--version", VERSION, "--changelog", notes, "--json"],
    "clawhub": ["C:/Program Files/nodejs/node.exe", "C:/Users/admin/AppData/Roaming/npm/node_modules/clawhub/bin/clawdhub.js",
        "publish", packages["surfaces"]["clawhub"]["directory"], "--slug", "chinese-official-writing", "--name", "中文公文写作",
        "--owner", "gongyu0918-debug", "--version", VERSION, "--tags", "latest", "--topics", "chinese-writing,official-writing,office-productivity,content-creation",
        "--source-repo", "https://github.com/gongyu0918-debug/chinese-official-writing-skill", "--source-commit", commit,
        "--source-ref", "v1.6.33", "--source-path", "chinese-official-writing", "--changelog", notes, "--json"],
}
command = commands[mode]
with (OUT / (mode + "-attempt.json")).open("x", encoding="utf-8") as f:
    json.dump({"formal_attempt": 1, "command": command, "release_commit": commit}, f, ensure_ascii=False, indent=2)
started = time.monotonic()
try:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    receipt = {"command": command, "exit_code": result.returncode, "seconds": round(time.monotonic() - started, 2),
               "stdout": result.stdout, "stderr": result.stderr}
except subprocess.TimeoutExpired as error:
    receipt = {"command": command, "exit_code": None, "error": "timeout_300_unconfirmed_do_not_resubmit",
               "seconds": round(time.monotonic() - started, 2)}
    (OUT / (mode + "-receipt.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise
(OUT / (mode + "-receipt.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"target": mode, "exit_code": result.returncode, "stdout": result.stdout[-2500:], "stderr": result.stderr[-1200:]}, ensure_ascii=False))
sys.exit(result.returncode)
