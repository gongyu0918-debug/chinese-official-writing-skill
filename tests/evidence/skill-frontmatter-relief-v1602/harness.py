#!/usr/bin/env python3
"""Frozen real A/B harness for the v1.6.2 SKILL frontmatter relief atom.

The default preflight is local-only. Real calls require both ``--execute`` and
the explicit environment latch below. The harness never retries a call and it
writes a sealed mapping without printing or reading it after creation.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import time
from typing import Any, Iterable


EVIDENCE_DIR = Path(__file__).resolve().parent
DEFAULT_BASELINE_ROOT = Path(r"F:\Workspaces\chinese-official-writing-skill\output\research-worktrees\v1602-integration")
DEFAULT_CANDIDATE_ROOT = Path(r"F:\Workspaces\chinese-official-writing-skill\output\research-worktrees\skill-frontmatter-relief-v1602")
DEFAULT_OUT = Path(r"C:\Users\admin\Documents\Codex\runtime-evidence\skill-frontmatter-relief-v1602\run-20260811")
CATALOG = Path(r"C:\Users\admin\.codex\opencodex-catalog.json")
BASE_URL = "http://127.0.0.1:10100/v1"
BASELINE_COMMIT = "d17cb8853274ba6dec4d686171daf4f8972a0ec8"
CANDIDATE_PRODUCT_COMMIT = "83afc6d250f55733fbc08f12f71792fa038367b1"
AUTH_ENV = "SKILL_FRONTMATTER_RELIEF_EVAL_AUTH"
AUTH_VALUE = "APPROVED_BY_ROOT"
TIMEOUT_SECONDS = 1200
SOURCE_FILE = "SKILL.md"
PACKAGE_PREFIXES = (
    "chinese-official-writing",
    "skills/chinese-official-writing",
    ".agents/skills/chinese-official-writing",
    ".qwen/skills/chinese-official-writing",
    "hermes/skills/chinese-official-writing",
    "openclaw/skills/chinese_official_writing",
)
MODELS = {
    "alibaba": "alibaba-token-plan/deepseek-v4-flash-0731",
    "ollama": "ollama-cloud/deepseek-v4-flash:0731",
    "minimax": "minimax-cn/MiniMax-M3",
}


@dataclass(frozen=True)
class Task:
    id: str
    topic: str
    prompt: str
    required: tuple[str, ...]
    forbidden: tuple[str, ...]
    min_chars: int = 0
    max_chars: int = 0
    review_only: bool = False


TASKS = (
    Task(
        id="N1",
        topic="短事务通知",
        prompt="""根据材料起草一则会议通知，只输出正文。材料：8月18日14时在三楼会议室召开档案整理协调会，参会人员为办公室、档案室和信息中心负责人，议题为核对整理进度和抽检记录。材料未提供任务分工、会议决定、联系人、反馈期限或其他安排。边界：准确保留时间、地点、参会范围和两个议题；不得补写未给事项。""",
        required=("8月18日14时", "三楼会议室", "办公室", "档案室", "信息中心", "整理进度", "抽检记录"),
        forbidden=("联系人", "反馈期限", "会议决定", "任务分工"),
        max_chars=500,
    ),
    Task(
        id="R1",
        topic="长篇事实受限报告",
        prompt="""根据材料起草一篇700至900字的工作情况报告，只输出正文。材料：7月1日至31日完成档案数字化整理1260卷，扫描图像312000页；抽检发现6卷目录页码与原件不一致，已登记复核；7月28日完成数据备份。材料未提供整改结果、经费、责任分工、验收结论或下一步安排。边界：准确保留全部日期、数量和已登记复核状态；不得补写未给事实。""",
        required=("7月1日至31日", "1260卷", "312000页", "6卷", "目录页码与原件不一致", "已登记复核", "7月28日", "数据备份"),
        forbidden=("整改已完成", "验收通过", "责任分工", "下一步将"),
        min_chars=600,
        max_chars=1050,
    ),
    Task(
        id="V1",
        topic="只审不改",
        prompt="""请只审不改下列通知，输出问题位置、风险层级和修改建议，不重写全文，不输出改后正文。原文：\n\n关于报送档案整理情况的通知\n\n各有关单位：\n8月18日14时在三楼会议室召开档案整理协调会，请办公室、档案室和信息中心负责人参加，会议核对整理进度和抽检记录。\n\n档案室\n2026年8月15日\n\n审查边界：材料没有联系人、反馈期限、任务分工或会议决定，不得把它们补入建议或改写稿。""",
        required=("问题位置", "风险层级", "修改建议"),
        forbidden=("联系人", "反馈期限", "任务分工", "会议决定"),
        max_chars=900,
        review_only=True,
    ),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def normalized(value: str) -> str:
    return re.sub(r"[\\\\/]+", "/", value).replace("\r\n", "\n").replace("\r", "\n")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {root}: {result.stderr.strip()}")
    return result.stdout.strip()


def source_path(root: Path) -> Path:
    return root / "chinese-official-writing" / SOURCE_FILE


def skill_body(root: Path) -> bytes:
    parts = source_path(root).read_bytes().split(b"---", 2)
    if len(parts) != 3:
        raise RuntimeError(f"malformed SKILL.md: {source_path(root)}")
    # The product atom changes YAML only. The frozen baseline retains CRLF
    # while the candidate's synchronized copies use LF, so compare body
    # content rather than transport line endings.
    return parts[2].replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def read_command(path: Path) -> str:
    return f"Get-Content -Raw -LiteralPath '{path}' | Out-Null"


def prompt_for(task: Task, root: Path) -> str:
    path = source_path(root)
    return f"""你是中文公文写作代理。当前任务只允许使用下列固定 Skill 文件。开始处理前，必须在终端执行这一条精确 PowerShell 读取命令；不得改写其中的绝对路径，不得读取其他 Skill、reference、历史证据或 AGENTS.md，也不得修改文件。\n\n`{read_command(path)}`\n\n读取后完成下面唯一题目。最终只输出题目要求的直接可用文本，不要输出读取过程、Skill 说明、许可证、Agent 兼容名单、安装路径、仓库或平台元数据、代码块、Markdown 标记或 JSON。\n\n题目（{task.id}，{task.topic}）：\n{task.prompt}\n"""


def walk_objects(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_objects(child)


def tool_commands(trace: str) -> list[str]:
    commands: list[str] = []
    for line in trace.splitlines():
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        for item in walk_objects(parsed):
            if item.get("type") == "command_execution" and isinstance(item.get("command"), str):
                commands.append(item["command"])
                continue
            name = str(item.get("name", "")).lower()
            if "command" not in name and "shell" not in name and "powershell" not in name:
                continue
            arguments: Any = item.get("arguments", item.get("input", item.get("args", {})))
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {"command": arguments}
            if isinstance(arguments, dict):
                for key in ("command", "cmd", "script"):
                    if isinstance(arguments.get(key), str):
                        commands.append(arguments[key])
    return commands


def trace_read_binding(trace: str, path: Path) -> list[int]:
    target = normalized(str(path)).lower()
    return [
        index for index, command in enumerate(tool_commands(trace))
        if "get-content" in command.lower() and target in normalized(command).lower()
    ]


def build_plan() -> list[dict[str, Any]]:
    # Nine pairs cannot split AB/BA exactly; 5/4 is the smallest possible gap.
    orders = {
        "alibaba": ("AB", "BA", "AB"),
        "ollama": ("BA", "AB", "BA"),
        "minimax": ("AB", "BA", "AB"),
    }
    rows: list[dict[str, Any]] = []
    number = 0
    for provider, model in MODELS.items():
        for task, order in zip(TASKS, orders[provider], strict=True):
            number += 1
            arms = ("baseline", "candidate") if order == "AB" else ("candidate", "baseline")
            rows.append({
                "pair_id": f"P{number:03d}", "provider": provider, "model": model,
                "task_id": task.id, "topic": task.topic, "order": order, "arms": list(arms),
            })
    return rows


def preflight(baseline_root: Path, candidate_root: Path) -> dict[str, Any]:
    if not CATALOG.is_file():
        raise RuntimeError(f"model catalog missing: {CATALOG}")
    if git(baseline_root, "rev-parse", "HEAD") != BASELINE_COMMIT:
        raise RuntimeError("baseline HEAD drifted")
    if git(baseline_root, "status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("baseline worktree is dirty")
    if git(candidate_root, "status", "--porcelain", "--untracked-files=all"):
        raise RuntimeError("candidate worktree is dirty")
    if git(candidate_root, "merge-base", CANDIDATE_PRODUCT_COMMIT, "HEAD") != CANDIDATE_PRODUCT_COMMIT:
        raise RuntimeError("candidate product commit is not an ancestor of evaluation worktree")
    candidate_changed = git(candidate_root, "diff", "--name-only", CANDIDATE_PRODUCT_COMMIT, "HEAD").splitlines()
    if any(path.startswith(prefix + "/") for path in candidate_changed for prefix in PACKAGE_PREFIXES):
        raise RuntimeError(f"candidate product changed after frozen commit: {candidate_changed}")
    changed_products = {
        path for path in git(candidate_root, "diff", "--name-only", BASELINE_COMMIT, CANDIDATE_PRODUCT_COMMIT).splitlines()
        if any(path == f"{prefix}/{SOURCE_FILE}" for prefix in PACKAGE_PREFIXES)
    }
    expected_products = {f"{prefix}/{SOURCE_FILE}" for prefix in PACKAGE_PREFIXES}
    if changed_products != expected_products:
        raise RuntimeError(f"unexpected product SKILL diff: {sorted(changed_products)}")
    if skill_body(baseline_root) != skill_body(candidate_root):
        raise RuntimeError("SKILL body changed; this is not frontmatter-only")
    return {
        "baseline_commit": BASELINE_COMMIT,
        "candidate_product_commit": CANDIDATE_PRODUCT_COMMIT,
        "candidate_evaluation_commit": git(candidate_root, "rev-parse", "HEAD"),
        "baseline_root": str(baseline_root), "candidate_root": str(candidate_root),
        "skill_sha256": {
            "baseline": sha256_bytes(source_path(baseline_root).read_bytes()),
            "candidate": sha256_bytes(source_path(candidate_root).read_bytes()),
        },
        "skill_body_sha256": sha256_bytes(skill_body(baseline_root)),
        "changed_product_skill_paths": sorted(changed_products),
        "first_final_only": True, "retry_count": 0, "reasoning_effort": "max", "plan": build_plan(),
    }


def evaluate_hard(task: Task, final: str) -> list[str]:
    text = compact(final)
    failures: list[str] = []
    if not text:
        return ["empty_final"]
    if re.search(r"(?m)^\s*(#|```|读取过程|Skill说明|JSON)", final):
        failures.append("non_requested_format")
    for required in task.required:
        if compact(required) not in text:
            failures.append(f"missing:{required}")
    for forbidden in task.forbidden:
        if compact(forbidden) in text:
            failures.append(f"forbidden:{forbidden}")
    for marker in ("MIT-0", "compatible_agents", "qwen_code", "安装路径", "GitHub", "仓库地址", "openclaw", "hermes"):
        if marker.lower() in final.lower():
            failures.append(f"metadata_leak:{marker}")
    length = len(text)
    if task.min_chars and length < task.min_chars:
        failures.append("length_under")
    if task.max_chars and length > task.max_chars:
        failures.append("length_over")
    if task.review_only and ("改后正文" in text or text.count("关于报送档案整理情况的通知") > 0):
        failures.append("review_rewrites_full_text")
    return failures


def run_call(pair: dict[str, Any], arm: str, task: Task, roots: dict[str, Path], out: Path) -> dict[str, Any]:
    source = roots[arm]
    prompt = prompt_for(task, source)
    stem = f"{pair['pair_id']}-{arm}"
    raw = out / "raw"
    final_path, trace_path, stderr_path = raw / f"{stem}.final.txt", raw / f"{stem}.trace.jsonl", raw / f"{stem}.stderr.txt"
    command = [
        shutil.which("codex") or "codex", "exec", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
        "-C", str(source), "-m", pair["model"], "-c", f'openai_base_url="{BASE_URL}"',
        "-c", f'model_catalog_json="{CATALOG}"', "-c", 'model_reasoning_effort="max"',
        "-s", "read-only", "--ephemeral", "--json", "--output-last-message", str(final_path), "-",
    ]
    started, error = time.monotonic(), None
    try:
        result = subprocess.run(command, input=prompt, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=TIMEOUT_SECONDS, check=False)
        return_code = result.returncode
        trace_path.write_text(result.stdout, encoding="utf-8", newline="\n")
        stderr_path.write_text(result.stderr, encoding="utf-8", newline="\n")
    except subprocess.TimeoutExpired as exc:
        return_code, error = None, f"timeout after {TIMEOUT_SECONDS} seconds"
        trace_path.write_text(str(exc.stdout or ""), encoding="utf-8", newline="\n")
        stderr_path.write_text(str(exc.stderr or ""), encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
    binding = trace_read_binding(trace_path.read_text(encoding="utf-8", errors="replace"), source_path(source))
    technical = []
    if return_code != 0:
        technical.append("nonzero_exit")
    if error:
        technical.append("timeout")
    if not final.strip():
        technical.append("missing_final")
    if not binding:
        technical.append("missing_exact_trace_read")
    return {
        "pair_id": pair["pair_id"], "provider": pair["provider"], "model": pair["model"], "order": pair["order"],
        "task_id": task.id, "topic": task.topic, "arm": arm, "source_root": str(source), "return_code": return_code,
        "error": error, "seconds": round(time.monotonic() - started, 3), "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "final_file": str(final_path.relative_to(out)), "trace_file": str(trace_path.relative_to(out)), "stderr_file": str(stderr_path.relative_to(out)),
        "final_sha256": sha256_bytes(final.encode("utf-8")) if final else None, "final_chars": len(compact(final)),
        "trace_read_bindings": {str(source_path(source)): binding}, "technical_failures": technical,
        "hard_failures": evaluate_hard(task, final) if not technical else [],
    }


def assess(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        grouped[record["pair_id"]][record["arm"]] = record
    pairs = []
    for pair in build_plan():
        arms = grouped[pair["pair_id"]]
        baseline, candidate = arms.get("baseline"), arms.get("candidate")
        valid = bool(baseline and candidate and not baseline["technical_failures"] and not candidate["technical_failures"])
        pairs.append({
            **{key: pair[key] for key in ("pair_id", "provider", "model", "task_id", "topic", "order")}, "valid": valid,
            "candidate_only_hard": candidate["hard_failures"] if valid and candidate["hard_failures"] and not baseline["hard_failures"] else [],
        })
    return pairs


def build_blind_packet(records: list[dict[str, Any]], pairs: list[dict[str, Any]], out: Path) -> tuple[str, dict[str, Any]]:
    by_pair: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        by_pair[record["pair_id"]][record["arm"]] = record
    task_by_id = {task.id: task for task in TASKS}
    randomizer, mapping, lines = random.SystemRandom(), {}, ["# SKILL frontmatter 减载匿名盲审包", "", "逐对比较 A/B，只依据题面判定硬边界、只审不改要求和直接可用性；不得猜测来源。", ""]
    public_number = 0
    for pair in pairs:
        if not pair["valid"]:
            continue
        public_number += 1
        labels = ["baseline", "candidate"]
        randomizer.shuffle(labels)
        public_id, task = f"B{public_number:03d}", task_by_id[pair["task_id"]]
        mapping[public_id] = {"pair_id": pair["pair_id"], "A": labels[0], "B": labels[1]}
        arms = by_pair[pair["pair_id"]]
        lines.extend([
            f"## {public_id}", "", f"题目：{task.id}（{task.topic}）", "", task.prompt, "", "硬边界：",
            *[f"- 必须保留：{item}" for item in task.required], *[f"- 不得补写：{item}" for item in task.forbidden],
            "- 不得泄露许可证、兼容名单、安装路径、仓库或平台元数据。", "", "### A", "",
            (out / arms[labels[0]]["final_file"]).read_text(encoding="utf-8", errors="replace").strip(), "", "### B", "",
            (out / arms[labels[1]]["final_file"]).read_text(encoding="utf-8", errors="replace").strip(), "",
        ])
    return "\n".join(lines).rstrip() + "\n", mapping


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def execute(baseline_root: Path, candidate_root: Path, out: Path) -> int:
    if out.exists():
        raise RuntimeError(f"refuse to overwrite output: {out}")
    context = preflight(baseline_root, candidate_root)
    out.mkdir(parents=True)
    (out / "raw").mkdir()
    write_json(out / "preflight.json", context)
    records, roots, task_by_id = [], {"baseline": baseline_root, "candidate": candidate_root}, {task.id: task for task in TASKS}
    for pair in build_plan():
        for arm in pair["arms"]:
            records.append(run_call(pair, arm, task_by_id[pair["task_id"]], roots, out))
    pairs = assess(records)
    manifest = {"context": context, "records": records, "assessment": {"pairs": pairs}, "retry_count": 0, "first_final_only": True}
    write_json(out / "manifest.json", manifest)
    blind, mapping = build_blind_packet(records, pairs, out)
    (out / "blind-packet.md").write_text(blind, encoding="utf-8", newline="\n")
    write_json(out / "blind-mapping.json", mapping)
    print(json.dumps({"status": "BLIND_PACKET_READY", "valid_pairs": sum(pair["valid"] for pair in pairs), "blind_packet_sha256": sha256_bytes(blind.encode("utf-8"))}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_BASELINE_ROOT)
    parser.add_argument("--candidate-root", type=Path, default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.preflight == args.execute:
        parser.error("choose exactly one of --preflight or --execute")
    if args.preflight:
        print(json.dumps(preflight(args.baseline_root, args.candidate_root), ensure_ascii=False, indent=2))
        return 0
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"real execution blocked: set {AUTH_ENV}={AUTH_VALUE}")
    return execute(args.baseline_root, args.candidate_root, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
