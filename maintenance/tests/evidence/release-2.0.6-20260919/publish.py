"""Submit the frozen 2.0.6 package once per authorized platform."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
VERSION = "2.0.6"
PRODUCT = "82b26779abd4ddaff346a953877192871a374382"
REPO = "gongyu0918-debug/chinese-official-writing-skill"


def verify_packages():
    manifest = json.loads((HERE / "upload-manifest.json").read_text(encoding="utf-8"))
    if manifest["product_commit"] != PRODUCT or manifest["version"] != VERSION:
        raise RuntimeError("Release binding differs")
    for name in ("skillhub", "clawhub"):
        folder = Path(manifest[name]["path"])
        actual = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in folder.rglob("*") if p.is_file()}
        if actual != manifest[name]["files"]:
            raise RuntimeError("Upload directory changed: " + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("surface", choices=("github", "skillhub", "clawhub"))
    args = parser.parse_args()
    verify_packages()
    notes = (HERE / "release-notes.md").read_text(encoding="utf-8")
    commands = {
        "github": ["C:/Program Files/GitHub CLI/gh.exe", "release", "create", VERSION,
                   "--repo", REPO, "--verify-tag", "--title", "中文公文写作 " + VERSION,
                   "--notes-file", str(HERE / "release-notes.md"), "--latest"],
        "skillhub": ["C:/Users/admin/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe",
                     str(Path.home() / ".skillhub/skills_store_cli.py"), "--skip-self-upgrade", "publish",
                     str(ROOT / "output/release-2.0.6/skillhub"), "--version", VERSION,
                     "--changelog", notes, "--json"],
        "clawhub": ["C:/Program Files/nodejs/node.exe",
                    "C:/Users/admin/AppData/Roaming/npm/node_modules/clawhub/bin/clawdhub.js", "publish",
                    str(ROOT / "output/release-2.0.6/clawhub"), "--slug", "chinese-official-writing",
                    "--name", "中文公文写作", "--owner", "gongyu0918-debug", "--version", VERSION,
                    "--changelog", notes, "--tags", "latest", "--source-repo", REPO,
                    "--source-commit", PRODUCT, "--source-ref", VERSION,
                    "--source-path", "chinese-official-writing", "--json"],
    }
    command = commands[args.surface]
    attempt = {"time": datetime.now(timezone.utc).isoformat(), "version": VERSION,
               "product_commit": PRODUCT, "command": command}
    # Existing attempt records stop duplicate submissions, including ambiguous exits.
    with (HERE / (args.surface + "-submission-attempt.json")).open("x", encoding="utf-8") as stream:
        json.dump(attempt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    result = {"exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    (HERE / (args.surface + "-result.json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / (args.surface + "-publish.json")).write_text(completed.stdout, encoding="utf-8")
    (HERE / (args.surface + "-publish.stderr")).write_text(completed.stderr, encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if completed.returncode:
        raise SystemExit(completed.returncode)
    if args.surface != "github":
        receipt = json.loads(completed.stdout)
        if receipt.get("ok") is not True or receipt.get("version") != VERSION:
            raise RuntimeError("Ambiguous receipt; stop without resubmitting")
    else:
        expected = "https://github.com/" + REPO + "/releases/tag/" + VERSION
        if completed.stdout.strip() != expected:
            raise RuntimeError("Unexpected release response; stop without resubmitting")


if __name__ == "__main__":
    main()
