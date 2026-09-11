"""Make a target-only ablation commit from the current main product."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
TARGET = {
    "chinese-official-writing/SKILL.md": {
        "compression": ("2d47c341^", "压缩、润色修改或去口语化"),
        "field": ("b68660a1^", "申请表、证明、采购明细"),
        "prose": ("8ca06ebb^", "检查 `.txt`"),
    },
    "chinese-official-writing/references/workflow.md": {
        "field": ("b68660a1^", "**字段和单元边界**"),
    },
}
LEAVES = [
    "chinese-official-writing/references/compression-details.md",
    "chinese-official-writing/references/field-editing.md",
    "chinese-official-writing/references/prose-lint-usage.md",
]

def git_old(ref, path, needle):
    text = subprocess.check_output(["git", "show", f"{ref}:" + path], cwd=ROOT, text=True, encoding="utf-8")
    return next(line for line in text.splitlines() if needle in line)

def replace_one(path, specs):
    file_path = ROOT / path
    lines = file_path.read_text(encoding="utf-8").splitlines()
    for _name, (ref, needle) in specs.items():
        old = git_old(ref, path, needle)
        marker = next(i for i, line in enumerate(lines) if needle in line or (needle == "检查 `.txt`" and "检查 `.txt`" in line))
        lines[marker] = old
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

for path, specs in TARGET.items():
    replace_one(path, specs)
for leaf in LEAVES:
    (ROOT / leaf).unlink()
print("target-only ablation prepared")
