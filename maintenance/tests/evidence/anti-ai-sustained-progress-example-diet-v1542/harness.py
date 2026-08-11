from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path


BASELINE_ROOT = Path(
    r"F:\Workspaces\chinese-official-writing-skill\output\research-baselines"
    r"\anti-ai-sustained-progress-example-diet-v1542-base"
)
CANDIDATE_ROOT = Path(
    r"F:\Workspaces\chinese-official-writing-skill\output\research-baselines"
    r"\anti-ai-sustained-progress-example-diet-v1542-candidate"
)
OUT = Path(
    r"F:\Workspaces\chinese-official-writing-skill\output"
    r"\anti-ai-sustained-progress-example-diet-v1542-real"
)
RUNTIME = Path(r"C:\Users\admin\Documents\Codex\anti-ai-sustained-progress-example-diet-v1542-real")
CATALOG = Path(r"C:\Users\admin\.codex\opencodex-catalog.json")
BASE_URL = "http://127.0.0.1:10100/v1"

BASELINE_COMMIT = "9968038b0bc68c942eac78cffe7b4968d674f801"
CANDIDATE_COMMIT = "75eb98fa5147a2fff2bc806b12e6955daf42154c"
EXPECTED_REMOVED_LINE = "- `持续推进`\n"
REFERENCE_PATHS = (
    "SKILL.md",
    "references/information-selection.md",
    "references/genre-playbooks.md",
    "references/genre-playbook-work-summary.md",
    "references/genre-playbook-plan-construction.md",
    "references/anti-ai-patterns.md",
    "references/final-review-layers.md",
    "references/proofreading-checklist.md",
)
MODELS = {
    "alibaba": "alibaba-token-plan/deepseek-v4-flash-0731",
    "ollama": "ollama-cloud/deepseek-v4-flash:0731",
}
HEADINGS = ("R1", "R2", "R3", "C1", "C2")
PAIR_ORDER = {
    ("alibaba", 1): ("baseline", "candidate"),
    ("alibaba", 2): ("candidate", "baseline"),
    ("alibaba", 3): ("candidate", "baseline"),
    ("alibaba", 4): ("baseline", "candidate"),
    ("ollama", 1): ("baseline", "candidate"),
    ("ollama", 2): ("candidate", "baseline"),
    ("ollama", 3): ("candidate", "baseline"),
    ("ollama", 4): ("baseline", "candidate"),
}
MIN_VALID_PAIRS_PER_PROVIDER = 3

TASKS = r"""
## R1

把下面原稿改成可直接使用的正式情况说明，只输出改后正文。

材料：2026年8月，市档案馆完成7个库房温湿度监测设备巡检，发现2台设备数据上传间断；已更换2台设备的通信模块，8月26日恢复上传。材料没有后续计划、成效评价、责任分工或验收结论。

原稿：本次巡检意义重大，持续推进设备管理优化，不断提升运行保障能力，全面赋能档案安全管理，形成一批可复制成果，为后续工作提供有力支撑。

边界：保留7个库房、2台、通信模块更换和8月26日恢复上传；不得补验收、责任、后续安排、成效、成果数量或推广结论。

## R2

根据材料起草一份2026年上半年政务服务事项标准化工作总结，只输出正文，约450字。

材料：1月8日启动工作，覆盖6个区和11个市级部门，对132个事项和486份申请表单核查名称、申请材料、表单字段、办理渠道、承诺时限。6月30日前完成第一轮逐项核查，记录74个问题；58个问题完成修改并通过复核，其余16个已发送事项主管部门确认。5月20日完成已确认37个问题的系统更新；6月18日抽取24个已更新事项核验，22个线上展示、窗口指南和表单字段一致，2个仍有字段显示顺序差异，已纳入后续修改范围。材料未给表彰、排名、经验推广、完成期限或新增责任安排。

## R3

根据材料起草政务大厅叫号系统建设方案正文，只输出正文，约500字。

材料：建设目标为替换大厅原有单窗口叫号设备，覆盖导办台、综合窗口和不动产窗口共18个窗口；建设内容包括18台窗口终端、2块候办区信息屏、预约取号模块和与现有评价系统的数据接口；实施周期为2026年9月至11月，其中9月完成设备到货和安装，10月完成接口联调和试运行，11月完成验收；由信息中心负责项目统筹，政务服务中心负责现场配合，供应商负责设备安装、接口联调和技术支持；验收依据为设备数量、窗口叫号、预约取号、信息屏展示和评价系统数据接口可用。材料未给预算、厂商、型号、采购方式、服务级别、培训计划或扩展范围。

## C1

把下列材料写成一段正式进展说明，只输出正文：数据共享目录更新工作持续推进。8月5日，数据资源处完成12个部门目录字段核对；8月12日，已向各部门发送37项字段差异清单；各部门应于8月30日前反馈确认结果，数据资源处负责汇总。保留“持续推进”及其对应的主体、动作、日期和责任，不得弱化为笼统表态或新增事项。

## C2

按用户固定模板整理下列内容，只输出正文；必须逐字保留“重点任务包括”“保障措施包括”两个标题及其顺序。

重点任务包括：9月完成接口清单核对；10月完成联调测试；11月完成验收。
保障措施包括：信息中心负责统筹；业务处室配合测试；供应商提供技术支持。
""".strip()

JUDGE_FACTS = r"""
每个配对包含 R1、R2、R3、C1、C2 五项正文。先判事实、数字、日期、主体、状态、用户模板和输出范围；再判空泛表达、直接修改成本和可用性；不得猜测 A/B 身份。

R1 必须保留7个库房、2台设备、通信模块更换和8月26日恢复上传；不得新增验收、责任、后续安排、成效、成果数量或推广。原稿的“意义重大、持续推进、不断提升、全面赋能、形成一批、提供有力支撑”均没有材料支撑，保留或同义扩写可记质量风险。

R2 必须保留6个区、11个市级部门、132个事项、486份表单、74个问题、58个已修改复核、16个待主管部门确认、37个系统更新、24项抽样、22项一致、2项字段顺序差异及其纳入后续修改范围；不得新增排名、表彰、推广、完成期限或责任。

R3 必须保留18个窗口、18台终端、2块信息屏、预约取号、评价系统接口、9月至11月的三个阶段、三方职责和五项验收依据；不得补预算、厂商、型号、采购方式、服务级别、培训或扩展范围。

C1 必须保留“持续推进”、12个部门、8月5日、37项、8月12日、8月30日、数据资源处汇总和各部门反馈确认。C2 必须逐字保留“重点任务包括”“保障措施包括”标题及其顺序，保留9月、10月、11月和三方职责。C1/C2 的词语、模板、事实或顺序遗漏、弱化或改写均为硬回退。

逐对输出 A/B 各项 PASS、WARN 或 FAIL；总体 A优、B优或难分；指出 Candidate 独有硬回退、空泛表达差异及理由。
""".strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, encoding="utf-8", capture_output=True, check=True
    )
    return result.stdout.strip()


def build_context(root: Path) -> tuple[str, dict[str, str]]:
    skill_root = root / "chinese-official-writing"
    hashes: dict[str, str] = {}
    chunks: list[str] = []
    for relative_path in REFERENCE_PATHS:
        text = normalized_text(skill_root / relative_path)
        hashes[relative_path] = sha256(text.encode("utf-8"))
        chunks.append(f"## {relative_path}\n{text}")
    return "\n\n".join(chunks), hashes


def build_prompt(context: str) -> str:
    heading_list = "、".join(f"`## {heading}`" for heading in HEADINGS)
    return (
        "你是中文公文 Skill 写作代理。以下 Skill context 已由外部编排层从固定提交逐文件读取并冻结。\n\n"
        "只使用已提供的 Skill 入口与 references，分别完成五项互不相关的任务。不要解释规则、读取过程或测试目的；"
        f"最终消息只按 {heading_list} 五个标题依次输出可直接使用正文，不增加其他标题或旁白。\n\n"
        f"Skill context:\n```text\n{context}\n```\n\n任务：\n{TASKS}\n"
    )


def validate_roots() -> tuple[dict[str, str], dict[str, str], str, str]:
    roots = {"baseline": (BASELINE_ROOT, BASELINE_COMMIT), "candidate": (CANDIDATE_ROOT, CANDIDATE_COMMIT)}
    for arm, (root, expected_commit) in roots.items():
        if git(root, "rev-parse", "HEAD") != expected_commit:
            raise RuntimeError(f"{arm} detached HEAD does not match fixed commit")
        if git(root, "status", "--porcelain", "--untracked-files=no"):
            raise RuntimeError(f"{arm} tracked worktree is dirty")

    baseline_context, baseline_hashes = build_context(BASELINE_ROOT)
    candidate_context, candidate_hashes = build_context(CANDIDATE_ROOT)
    changed = [path for path in REFERENCE_PATHS if baseline_hashes[path] != candidate_hashes[path]]
    if changed != ["references/anti-ai-patterns.md"]:
        raise RuntimeError(f"unexpected frozen-context diff: {changed}")
    base_ref = normalized_text(BASELINE_ROOT / "chinese-official-writing/references/anti-ai-patterns.md")
    candidate_ref = normalized_text(CANDIDATE_ROOT / "chinese-official-writing/references/anti-ai-patterns.md")
    if base_ref.replace(EXPECTED_REMOVED_LINE, "", 1) != candidate_ref or base_ref.count(EXPECTED_REMOVED_LINE) != 1:
        raise RuntimeError("anti-ai reference is not exactly the approved one-line deletion")
    return baseline_hashes, candidate_hashes, build_prompt(baseline_context), build_prompt(candidate_context)


def headings_complete(final: str) -> bool:
    expected = [f"## {heading}" for heading in HEADINGS]
    actual = [line.strip() for line in final.splitlines() if line.strip().startswith("## ")]
    if actual != expected or final[: final.find(expected[0])].strip():
        return False
    positions = [final.find(heading) for heading in expected]
    return all(final[start + len(heading) : end].strip() for start, end, heading in zip(positions, positions[1:] + [len(final)], expected))


def run_one(provider: str, replicate: int, arm: str, order: int, prompt: str) -> dict[str, object]:
    model = MODELS[provider]
    slug = f"{provider}-r{replicate}-{arm}"
    final_path = OUT / f"{slug}.txt"
    stdout_path = OUT / f"{slug}.stdout.txt"
    stderr_path = OUT / f"{slug}.stderr.txt"
    command = [
        shutil.which("codex") or "codex", "exec", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
        "-C", str(RUNTIME), "-m", model,
        "-c", f'openai_base_url="{BASE_URL}"',
        "-c", f'model_catalog_json="{CATALOG}"',
        "-c", 'model_reasoning_effort="max"',
        "-s", "read-only", "--ephemeral", "--output-last-message", str(final_path), "-",
    ]
    started = time.monotonic()
    timeout = False
    try:
        result = subprocess.run(command, input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=900)
        return_code = result.returncode
        stdout, stderr = result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        timeout, return_code = True, None
        stdout, stderr = exc.stdout or "", exc.stderr or ""
    stdout_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8") if final_path.exists() else ""
    return {
        "provider": provider, "model": model, "replicate": replicate, "arm": arm, "order": order,
        "return_code": return_code, "timeout": timeout, "duration_seconds": round(time.monotonic() - started, 3),
        "retry_count": 0, "prose_lint_executed_by_harness": False,
        "prompt_chars": len(prompt), "prompt_sha256": sha256(prompt.encode("utf-8")),
        "final_file": final_path.name, "final_chars": len(final),
        "final_sha256": sha256(final.encode("utf-8")) if final else None,
        "headings_complete": headings_complete(final),
    }


def valid_pairs(records: list[dict[str, object]]) -> list[tuple[str, int]]:
    indexed = {(r["provider"], r["replicate"], r["arm"]): r for r in records}
    valid: list[tuple[str, int]] = []
    for provider, replicate in PAIR_ORDER:
        arms = [indexed[(provider, replicate, arm)] for arm in ("baseline", "candidate")]
        if all(r["return_code"] == 0 and not r["timeout"] and r["final_chars"] and r["headings_complete"] for r in arms):
            valid.append((provider, replicate))
    return valid


def write_blind_packet(records: list[dict[str, object]], pairs: list[tuple[str, int]]) -> tuple[str, dict[str, dict[str, object]]]:
    indexed = {(r["provider"], r["replicate"], r["arm"]): r for r in records}
    mapping: dict[str, dict[str, object]] = {}
    lines = ["# ANTI-AI ‘持续推进’重复例子微减载匿名 A/B", "", JUDGE_FACTS, ""]
    rng = secrets.SystemRandom()
    for pair_number, (provider, replicate) in enumerate(pairs, start=1):
        pair_id, arms = f"P{pair_number}", ["baseline", "candidate"]
        rng.shuffle(arms)
        mapping[pair_id] = {"provider": provider, "replicate": replicate, "A": arms[0], "B": arms[1]}
        lines.extend([f"## {pair_id}", ""])
        for label, arm in zip(("A", "B"), arms):
            record = indexed[(provider, replicate, arm)]
            body = (OUT / str(record["final_file"])).read_text(encoding="utf-8").strip()
            lines.extend([f"### {label}", "", body, ""])
    return "\n".join(lines).rstrip() + "\n", mapping


def preflight() -> int:
    baseline_hashes, candidate_hashes, baseline_prompt, candidate_prompt = validate_roots()
    print(json.dumps({
        "baseline_commit": BASELINE_COMMIT, "candidate_commit": CANDIDATE_COMMIT,
        "changed_refs": [path for path in REFERENCE_PATHS if baseline_hashes[path] != candidate_hashes[path]],
        "baseline_prompt_chars": len(baseline_prompt), "candidate_prompt_chars": len(candidate_prompt),
        "prompt_char_delta": len(candidate_prompt) - len(baseline_prompt),
        "baseline_prompt_sha256": sha256(baseline_prompt.encode("utf-8")),
        "candidate_prompt_sha256": sha256(candidate_prompt.encode("utf-8")),
        "pair_order": {f"{provider}-r{replicate}": arms for (provider, replicate), arms in PAIR_ORDER.items()},
        "calls_planned": len(PAIR_ORDER) * 2, "retry_count": 0,
        "prose_lint_executed_by_harness": False,
    }, ensure_ascii=False, indent=2))
    return 0


def execute() -> int:
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError(f"output directory is not empty: {OUT}")
    if not CATALOG.is_file():
        raise RuntimeError(f"catalog missing: {CATALOG}")
    baseline_hashes, candidate_hashes, baseline_prompt, candidate_prompt = validate_roots()
    OUT.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    (OUT / "baseline-prompt.txt").write_text(baseline_prompt, encoding="utf-8", newline="\n")
    (OUT / "candidate-prompt.txt").write_text(candidate_prompt, encoding="utf-8", newline="\n")
    records: list[dict[str, object]] = []
    for (provider, replicate), arms in PAIR_ORDER.items():
        for order, arm in enumerate(arms, start=1):
            records.append(run_one(provider, replicate, arm, order, baseline_prompt if arm == "baseline" else candidate_prompt))
    pairs = valid_pairs(records)
    by_provider = {provider: sum(p[0] == provider for p in pairs) for provider in MODELS}
    manifest: dict[str, object] = {
        "baseline_commit": BASELINE_COMMIT, "candidate_commit": CANDIDATE_COMMIT,
        "reference_sha256": {"baseline": baseline_hashes, "candidate": candidate_hashes},
        "changed_refs": ["references/anti-ai-patterns.md"], "retry_count": 0,
        "prose_lint_executed_by_harness": False,
        "pair_order": {f"{provider}-r{replicate}": arms for (provider, replicate), arms in PAIR_ORDER.items()},
        "records": records, "valid_pair_keys": [f"{p}-r{r}" for p, r in pairs], "valid_pairs_by_provider": by_provider,
    }
    if any(count < MIN_VALID_PAIRS_PER_PROVIDER for count in by_provider.values()):
        (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"status": "insufficient-valid-pairs", "valid_pairs_by_provider": by_provider}, ensure_ascii=False), file=sys.stderr)
        return 2
    packet, mapping = write_blind_packet(records, pairs)
    packet_bytes = packet.encode("utf-8")
    mapping_bytes = (json.dumps(mapping, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (OUT / "blind-packet.md").write_bytes(packet_bytes)
    (OUT / "blind-mapping.json").write_bytes(mapping_bytes)
    manifest["blind_packet_sha256"] = sha256(packet_bytes)
    manifest["blind_mapping_sha256"] = sha256(mapping_bytes)
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "ready-for-blind-review", "valid_pairs_by_provider": by_provider, "records": len(records)}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.preflight == args.run:
        parser.error("choose exactly one of --preflight or --run")
    return preflight() if args.preflight else execute()


if __name__ == "__main__":
    raise SystemExit(main())
