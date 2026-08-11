from __future__ import annotations

import concurrent.futures
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path


BASELINE_ROOT = Path(r"F:\Workspaces\chinese-official-writing-skill")
CANDIDATE_ROOT = Path(
    r"F:\Workspaces\chinese-official-writing-skill\output\research-worktrees"
    r"\anti-ai-continuous-negation-anywhere-v1543-candidate"
)
OUT = Path(
    r"F:\Workspaces\chinese-official-writing-skill\output"
    r"\anti-ai-continuous-negation-anywhere-v1543-real"
)
RUNTIME = Path(r"C:\Users\admin\Documents\Codex\anti-ai-continuous-negation-anywhere-v1543-real")
CATALOG = Path(r"C:\Users\admin\.codex\opencodex-catalog.json")
BASE_URL = "http://127.0.0.1:10100/v1"

BASELINE_COMMIT = "03c13d2dea8924d3eb2e8c487956da45ce6b0692"
CANDIDATE_COMMIT = "fcc1d960a857fa418afa83714fbabdd0b5fed431"

REFERENCE_PATHS = [
    "SKILL.md",
    "references/information-selection.md",
    "references/genre-checklist-report.md",
    "references/anti-ai-patterns.md",
    "references/final-review-layers.md",
    "references/proofreading-checklist.md",
]

MODELS = {
    "alibaba": "alibaba-token-plan/deepseek-v4-flash-0731",
    "ollama": "ollama-cloud/deepseek-v4-flash:0731",
}

PAIR_ORDER = {
    ("alibaba", 1): ["baseline", "candidate"],
    ("alibaba", 2): ["candidate", "baseline"],
    ("alibaba", 3): ["baseline", "candidate"],
    ("ollama", 1): ["candidate", "baseline"],
    ("ollama", 2): ["baseline", "candidate"],
    ("ollama", 3): ["candidate", "baseline"],
}

TASKS = r"""
## T1

请按材料把原稿改成一段可直接使用的情况说明，只输出改后正文。

材料：2026年8月8日10时05分，统一查询接口出现超时；监测系统记录超时4次；影响3个内部查询页面；10时20分接口恢复；故障原因正在核查。材料没有说明3个页面是否恢复，也没有说明影响是否完全消除。

原稿：统一查询接口已于10时20分恢复，但这不代表3个内部查询页面已全部恢复，也不能说明问题已经彻底解决，当前尚不能据此认定影响已经消除，故障原因尚未形成结论。

边界：保留10时05分、4次、3个内部页面、10时20分和原因正在核查；不得补页面恢复、影响消除、根因、责任部门、损失、整改或后续安排。

## T2

请按材料压缩原稿，写成一段可直接使用的核验情况，只输出改后正文。

材料：本次核验12个系统；A系统发现1项权限配置问题，已登记整改；其余11个系统未发现同类问题；未发现数据缺失。材料没有提供后续安排和责任分工。

原稿：本次仅完成12个系统核验，尚不能据此判断整体情况，当前也不能直接说明风险已经消除。有关整改安排尚未明确，责任分工也尚未确定，暂不具备作出进一步判断的条件。

边界：必须保留12个系统、A系统1项权限配置问题且已登记整改、其余11个系统未发现同类问题、未发现数据缺失；不得补风险结论、安排、责任、期限或处置成效。

## T3

根据以下材料写一段可直接使用的设备试用阶段情况，只输出正文。

材料：2026年6月1日至20日，2台自助设备累计服务318次；6月20日完成本轮试用；6月25日馆务会听取运行情况。材料没有采购、预算、责任分工、评估结论、整改或后续安排。

边界：准确保留日期、2台、318次和馆务会听取运行情况；不得补采购决定、预算判断、责任、成效、问题、整改或后续动作。

## C1

把下列材料写成一句正式核验结论，只输出正文：本次核验12个系统；A系统发现1项权限配置问题并已登记整改；其余11个系统未发现同类问题；未发现数据缺失。

边界：两个否定事实均须保留，不得合并成笼统的“总体正常”。

## C2

把下列要求写成一句正式通知，只输出正文：系统更新安排在8月12日；测试通过前不得上线；未经批准不得操作生产账号。

边界：日期和两个禁令的对象、强度均须保留。

## C3

把下列要求写成一句正式通知，只输出正文；引号内原话必须逐字保留，包括中文引号和引号内句号：工作要求为“发现异常要及时报告，不迟报、不漏报、不瞒报。”
""".strip()

JUDGE_FACTS = r"""
每个配对包含六项互不相关正文。先逐项检查事实、数字、对象、状态、否定范围、输出范围，再计目标事件，最后判直接使用质量。

T1必须保留10:05、4次、3个内部页面、10:20和原因正在核查；页面状态未知。材料外的“页面未恢复、影响未消除、不能说明彻底解决、尚不能认定影响消除、原因未形成结论”等，每个独立分句计1个目标事件；同句或相邻句出现两个以上目标否定分句，另计1组连续否定。

T2必须保留12个系统、A系统1项且已登记整改、其余11个系统未发现同类问题、未发现数据缺失。后续安排、责任、期限和整体风险结论均未给；相应材料外否定分句按同一口径计数。两个已给否定事实不计目标事件。

T3必须保留6月1日至20日、2台、318次、6月20日完成试用、6月25日馆务会听取运行情况。采购、预算、责任、评估、整改和后续均未给；围绕这些事项追加的否定说明计目标事件。

C1必须同时保留“其余11个系统未发现同类问题”和“未发现数据缺失”；C2必须保留8月12日及两个禁令；C3必须逐字保留“发现异常要及时报告，不迟报、不漏报、不瞒报。”及中文引号、引号内句号。C1—C3不计目标事件，任何遗漏、弱化、对象错配或引语失真均为硬回退。

逐对输出：A/B各项PASS、WARN或FAIL；A/B的T1—T3目标分句总数和连续否定组数；A优、B优或难分；理由。不得猜测身份。
""".strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def git(*args: str, cwd: Path) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=cwd, text=True, encoding="utf-8", capture_output=True, check=True
    )
    return completed.stdout.strip()


def build_context(root: Path) -> tuple[str, dict[str, str]]:
    parts: list[str] = []
    hashes: dict[str, str] = {}
    skill_root = root / "chinese-official-writing"
    for relative in REFERENCE_PATHS:
        content = normalized_text(skill_root / relative)
        hashes[relative] = sha256_bytes(content.encode("utf-8"))
        parts.append(f"## {relative}\n{content}")
    return "\n\n".join(parts), hashes


def build_prompt(context: str) -> str:
    return (
        "你是中文公文 Skill 写作代理。以下 Skill context 已由外部编排层从固定提交逐文件读取并冻结。\n\n"
        "只使用已提供的 Skill 入口与 references，分别完成六项互不相关的任务。不要解释规则、读取过程或测试目的；"
        "不要修改文件。最终消息只按 `## T1`、`## T2`、`## T3`、`## C1`、`## C2`、`## C3` "
        "六个标题输出对应的可直接使用正文，不增加其他标题或旁白。\n\n"
        f"Skill context:\n```text\n{context}\n```\n\n任务：\n{TASKS}\n"
    )


def validate_roots() -> tuple[dict[str, str], dict[str, str], str, str]:
    expected = {"baseline": BASELINE_COMMIT, "candidate": CANDIDATE_COMMIT}
    roots = {"baseline": BASELINE_ROOT, "candidate": CANDIDATE_ROOT}
    for arm, root in roots.items():
        head = git("rev-parse", "HEAD", cwd=root)
        if head != expected[arm]:
            raise RuntimeError(f"{arm} HEAD mismatch: {head} != {expected[arm]}")
        if git("status", "--porcelain", "--untracked-files=no", cwd=root):
            raise RuntimeError(f"{arm} tracked worktree is dirty")

    base_context, base_hashes = build_context(BASELINE_ROOT)
    cand_context, cand_hashes = build_context(CANDIDATE_ROOT)
    changed = [path for path in REFERENCE_PATHS if base_hashes[path] != cand_hashes[path]]
    if changed != ["references/anti-ai-patterns.md"]:
        raise RuntimeError(f"unexpected changed references: {changed}")
    return base_hashes, cand_hashes, build_prompt(base_context), build_prompt(cand_context)


def run_one(provider: str, model: str, replicate: int, arm: str, order: int, prompt: str) -> dict:
    slug = f"{provider}-r{replicate}-{arm}"
    final_path = OUT / f"{slug}.txt"
    stdout_path = OUT / f"{slug}.stdout.txt"
    stderr_path = OUT / f"{slug}.stderr.txt"
    command = [
        shutil.which("codex") or "codex",
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-C",
        str(RUNTIME),
        "-m",
        model,
        "-c",
        f'openai_base_url="{BASE_URL}"',
        "-c",
        f'model_catalog_json="{CATALOG}"',
        "-c",
        'model_reasoning_effort="max"',
        "-s",
        "read-only",
        "--ephemeral",
        "--output-last-message",
        str(final_path),
        "-",
    ]
    started = time.monotonic()
    error: str | None = None
    return_code: int | None = None
    try:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=900,
            check=False,
        )
        return_code = completed.returncode
        stdout_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
        stderr_path.write_text(completed.stderr, encoding="utf-8", newline="\n")
    except subprocess.TimeoutExpired as exc:
        error = "timeout after 900 seconds"
        stdout_path.write_text(exc.stdout or "", encoding="utf-8", newline="\n")
        stderr_path.write_text(exc.stderr or "", encoding="utf-8", newline="\n")

    duration = round(time.monotonic() - started, 3)
    final = final_path.read_text(encoding="utf-8") if final_path.exists() else ""
    headings = [f"## {name}" for name in ("T1", "T2", "T3", "C1", "C2", "C3")]
    heading_positions = [final.find(heading) for heading in headings]
    headings_complete = all(final.count(heading) == 1 for heading in headings)
    headings_complete = headings_complete and heading_positions == sorted(heading_positions)
    return {
        "provider": provider,
        "model": model,
        "replicate": replicate,
        "arm": arm,
        "order": order,
        "return_code": return_code,
        "error": error,
        "duration_seconds": duration,
        "prompt_chars": len(prompt),
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "final_file": final_path.name,
        "final_sha256": sha256_bytes(final.encode("utf-8")) if final else None,
        "final_chars": len(final),
        "heading_positions": heading_positions,
        "headings_complete": headings_complete,
    }


def create_blind_packet(records: list[dict]) -> tuple[str, dict]:
    by_key = {(record["provider"], record["replicate"], record["arm"]): record for record in records}
    rng = secrets.SystemRandom()
    mapping: dict[str, dict] = {}
    sections = ["# 连续否定全位置减载匿名 A/B", "", JUDGE_FACTS, ""]
    pair_number = 0
    for provider in MODELS:
        replicates = sorted(
            replicate for pair_provider, replicate in PAIR_ORDER if pair_provider == provider
        )
        for replicate in replicates:
            pair_number += 1
            pair_id = f"P{pair_number}"
            arms = ["baseline", "candidate"]
            rng.shuffle(arms)
            mapping[pair_id] = {"provider": provider, "replicate": replicate, "A": arms[0], "B": arms[1]}
            sections.extend([f"## {pair_id}", ""])
            for label, arm in zip(("A", "B"), arms):
                record = by_key[(provider, replicate, arm)]
                body = (OUT / record["final_file"]).read_text(encoding="utf-8").strip()
                sections.extend([f"### {label}", "", body, ""])
    return "\n".join(sections).rstrip() + "\n", mapping


def main() -> int:
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError(f"output directory is not empty: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if not CATALOG.is_file():
        raise RuntimeError(f"catalog missing: {CATALOG}")

    base_hashes, cand_hashes, base_prompt, cand_prompt = validate_roots()
    (OUT / "baseline-prompt.txt").write_text(base_prompt, encoding="utf-8", newline="\n")
    (OUT / "candidate-prompt.txt").write_text(cand_prompt, encoding="utf-8", newline="\n")

    jobs: list[tuple] = []
    for (provider, replicate), arms in PAIR_ORDER.items():
        for order, arm in enumerate(arms, start=1):
            prompt = base_prompt if arm == "baseline" else cand_prompt
            jobs.append((provider, MODELS[provider], replicate, arm, order, prompt))

    records: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_one, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda item: (item["provider"], item["replicate"], item["order"]))

    invalid = [
        record
        for record in records
        if record["return_code"] != 0
        or record["error"] is not None
        or record["final_chars"] == 0
        or not record["headings_complete"]
    ]

    manifest = {
        "baseline_root": str(BASELINE_ROOT),
        "candidate_root": str(CANDIDATE_ROOT),
        "baseline_commit": BASELINE_COMMIT,
        "candidate_commit": CANDIDATE_COMMIT,
        "reference_paths": REFERENCE_PATHS,
        "changed_refs": ["references/anti-ai-patterns.md"],
        "reference_sha256": {"baseline": base_hashes, "candidate": cand_hashes},
        "catalog_sha256": sha256_bytes(CATALOG.read_bytes()),
        "model_reasoning_effort": "max",
        "retry_count": 0,
        "pair_order": {f"{provider}-r{replicate}": arms for (provider, replicate), arms in PAIR_ORDER.items()},
        "records": records,
        "invalid_count": len(invalid),
    }

    if invalid:
        (OUT / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(json.dumps(invalid, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    packet, mapping = create_blind_packet(records)
    packet_bytes = packet.encode("utf-8")
    mapping_text = json.dumps(mapping, ensure_ascii=False, indent=2) + "\n"
    mapping_bytes = mapping_text.encode("utf-8")
    (OUT / "blind-packet.md").write_bytes(packet_bytes)
    (OUT / "blind-mapping.json").write_bytes(mapping_bytes)
    manifest["blind_packet_sha256"] = sha256_bytes(packet_bytes)
    manifest["blind_mapping_sha256"] = sha256_bytes(mapping_bytes)
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    print(f"valid={len(records)}/{len(records)}")
    print(f"baseline_prompt_sha256={sha256_bytes(base_prompt.encode('utf-8'))}")
    print(f"candidate_prompt_sha256={sha256_bytes(cand_prompt.encode('utf-8'))}")
    print(f"blind_packet_sha256={manifest['blind_packet_sha256']}")
    print(f"blind_mapping_sha256={manifest['blind_mapping_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
