"""Build independent, complete R16 purpose prototypes without changing canonical."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
SOURCE = ROOT / "chinese-official-writing"
DEST = ROOT / "output/genre-purpose-r16"
PRODUCT_BASE = "01c2a659"

PROCUREMENT = """# 采购公告

采购公告公开采购项目的征集响应、结果或终止事项，按本次发布目的选择要素；内部采购申请或审查按实际交付件处理。

## 成稿骨架

先交代采购主体、项目及适用包次，再按发布目的展开：

- 征集响应：采购内容、数量、预算或上限 → 已给的资格或响应条件 → 文件获取、响应期限和提交方式。
- 结果告知：已形成的中标或成交结果 → 对应供应商、结果金额及主要标的信息。
- 终止事项：终止的项目或包次、范围 → 当前状态和已给原因 → 材料已有的后续安排。

联系方式、公告期限、附件以及评审或后续安排，按本次材料、模板及适用发布要求保留。只提示影响当前发布目的的缺项，不把响应条件、递交期限等征集要素强加给结果或终止公告。

保持客观告知语气，核对项目或包次与公开事项相符；预算或上限、估算价与中标或成交金额不互换。结果未定不写成既定，终止不自行改为重新采购或项目永久取消。

AI 算力场景按首页条件叠加 `ai-compute-docs.md`。
"""

CORRESPONDENCE = """# 函、复函与征求意见函

函用于不相隶属单位间商洽、询问答复、征求意见、请求批准和答复审批事项，按实际用途与收发双方职权确定写法。上级答复下级请示用批复，转 `genre-playbook-reply.md`。

## 成稿骨架

来文或事项背景 → 本次商洽、答复、征求意见或请批事项 → 办理意见与必要反馈信息。

- 商洽、询问或征求意见：写明具体事项，用平等沟通语气；需要对方反馈时写清反馈路径。
- 请求批准：说明理由和具体请求，使用请批语，保留尚待批准的状态。
- 审批答复：承接来函，在有权范围内按材料已有结论明确同意、不同意及条件和范围；缺少授权或结论依据时不代作批准。

称谓服从用户模板和已给主体；对不相隶属单位可用“贵单位”等中性称谓。商洽可用“商请”“请予支持”，请批可用“请予批准”，复函对应来文作出答复，结语随本次用途确定。

材料已给或办理确有需要时，保留反馈期限、方式、联系人和附件；材料未给且不影响办理时不把这些内容补成固定要素。
"""

ADDRESS_REPLACEMENTS = [
    (
        "函、复函、征求意见函和协商材料对不相隶属单位可用“贵单位”，自称“我单位/我厅/我局”。商请可用“商请贵单位”“请予支持”“请研究反馈”“请于……前函复”；复函可用“来函收悉。经研究，现函复如下”。语气平等、简明，不使用命令式或审批式措辞。",
        "函、复函、征求意见函和协商材料对不相隶属单位可用“贵单位”，自称“我单位/我厅/我局”。商洽可用“商请贵单位”“请予支持”“请研究反馈”；请批函可用“请予批准”；复函可用“现函复如下”。有权范围内的审批复函按材料已有结论和条件明确答复，措辞服从本次用途与职权。",
    ),
    (
        "结尾语服务文种功能，并位于正文末段、落款和日期之前：请示用请批语，报告用报告语，函用函达/盼复/请予支持，复函用函复，通知用落实或报送要求，公示用异议和联系方式。报告不写请批语，函不写上级批复口吻，通知不写成感谢信；申请按模板和审批语境处理。",
        "结尾语服务文种功能，并位于正文末段、落款和日期之前：请示用请批语，报告用报告语，函按用途用函达/盼复/请予支持或请批语，复函用函复，通知用落实或报送要求，公示用异议和联系方式。报告不写请批语，通知不写成感谢信；申请按模板和审批语境处理。",
    ),
]


def manifest(path):
    return {
        p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(path.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def changed_reference_links(arm, paths):
    """Check actual local reference targets in changed pages; do not scan old outputs."""
    rows = []
    for name in paths:
        page = arm / name
        for target in re.findall(r"`([^`\n]+\.md)`", page.read_text(encoding="utf-8")):
            resolved = page.parent / target
            assert resolved.is_file(), (name, target)
            rows.append({"page": name, "target": target, "exists": True})
    return rows


def main():
    assert not DEST.exists(), f"Destination must be new: {DEST}"
    subprocess.run(
        ["git", "diff", "--quiet", PRODUCT_BASE, "--", "chinese-official-writing"],
        cwd=ROOT, check=True,
    )
    source_before = manifest(SOURCE)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    records = {}
    DEST.mkdir()
    for name in ("baseline", "procurement", "correspondence"):
        arm = DEST / name
        shutil.copytree(SOURCE, arm, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if name == "procurement":
            (arm / "references/genre-playbook-procurement-announcement.md").write_text(
                PROCUREMENT, encoding="utf-8", newline="\n")
        if name == "correspondence":
            (arm / "references/genre-playbook-correspondence.md").write_text(
                CORRESPONDENCE, encoding="utf-8", newline="\n")
            p = arm / "references/formal-addressing.md"
            text = p.read_text(encoding="utf-8")
            for old, new in ADDRESS_REPLACEMENTS:
                assert text.count(old) == 1, old
                text = text.replace(old, new)
            p.write_text(text, encoding="utf-8", newline="\n")
        files = manifest(arm)
        assert files.keys() == source_before.keys(), "A complete Skill must retain all product files"
        changed = sorted(p for p in files if files[p] != source_before[p])
        expected = {
            "baseline": [],
            "procurement": ["references/genre-playbook-procurement-announcement.md"],
            "correspondence": ["references/formal-addressing.md", "references/genre-playbook-correspondence.md"],
        }[name]
        assert changed == expected, (name, changed)
        patch = []
        sizes = {}
        for rel in changed:
            old = (SOURCE / rel).read_text(encoding="utf-8")
            new = (arm / rel).read_text(encoding="utf-8")
            patch.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                         fromfile="baseline/" + rel, tofile=name + "/" + rel))
            sizes[rel] = {"before_nonspace": len(re.sub(r"\s", "", old)),
                          "after_nonspace": len(re.sub(r"\s", "", new))}
        if patch:
            (DEST / (name + ".diff")).write_text("".join(patch), encoding="utf-8")
        records[name] = {"path": arm.relative_to(ROOT).as_posix(), "file_count": len(files),
                         "changed_paths": changed, "fingerprint": fingerprint(files),
                         "files": files, "sizes": sizes,
                         "changed_reference_links": changed_reference_links(arm, changed)}
    assert manifest(SOURCE) == source_before, "Canonical changed during build"
    result = {"source": "chinese-official-writing", "product_base": PRODUCT_BASE,
              "source_head": head, "source_fingerprint": fingerprint(source_before),
              "ignored_build_cache": ["__pycache__", "*.pyc"], "canonical_unchanged": True,
              "protected_files_unchanged": ["SKILL.md", "references/reference-index.md", "references/genre-routing.md"],
              "arms": records, "real_writing_run": False}
    (EVIDENCE / "build.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({name: {"fingerprint": r["fingerprint"], "changed_paths": r["changed_paths"],
                            "file_count": r["file_count"], "sizes": r["sizes"]}
                      for name, r in records.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
