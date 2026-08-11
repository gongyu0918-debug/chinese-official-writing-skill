from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path


BASELINE_COMMIT = "b91f25cc49cc8ca1379804a81a1d6e5a4eab987c"
CANDIDATE_COMMIT = "23a89114"
RUNTIME_PARENT = Path(r"C:\Users\admin\Documents\Codex\cow-160-combination-real")
RUNTIME_ROOTS = {
    "baseline": RUNTIME_PARENT / "baseline",
    "candidate": RUNTIME_PARENT / "candidate",
}
SKILL_REL = Path(".agents/skills/chinese-official-writing")
OUT = Path(r"F:\Workspaces\chinese-official-writing-skill\output\release-1.6.0-combination-real")
MAPPING_PATH = RUNTIME_PARENT / "blind-mapping.json"
CATALOG = Path(r"C:\Users\admin\.codex\opencodex-catalog.json")
BASE_URL = "http://127.0.0.1:10100/v1"
MODELS = {
    "alibaba": "alibaba-token-plan/deepseek-v4-flash-0731",
    "ollama": "ollama-cloud/deepseek-v4-flash:0731",
}
TASK_ORDER = ("W1", "W2", "W3", "H1", "H2")
PAIR_ORDER = {
    ("alibaba", "W1"): ("baseline", "candidate"),
    ("alibaba", "W2"): ("candidate", "baseline"),
    ("alibaba", "W3"): ("baseline", "candidate"),
    ("alibaba", "H1"): ("candidate", "baseline"),
    ("alibaba", "H2"): ("baseline", "candidate"),
    ("ollama", "W1"): ("candidate", "baseline"),
    ("ollama", "W2"): ("baseline", "candidate"),
    ("ollama", "W3"): ("candidate", "baseline"),
    ("ollama", "H1"): ("baseline", "candidate"),
    ("ollama", "H2"): ("candidate", "baseline"),
}

ENTRY = ".agents/skills/chinese-official-writing/SKILL.md"
INFO = ".agents/skills/chinese-official-writing/references/information-selection.md"
GENERIC = ".agents/skills/chinese-official-writing/references/genre-playbooks.md"
CORR = ".agents/skills/chinese-official-writing/references/genre-playbook-correspondence.md"
REPORT = ".agents/skills/chinese-official-writing/references/genre-checklist-report.md"
HOOK = ".agents/skills/chinese-official-writing/scripts/gate_stop_hook.py"

REQUIRED_READS = {
    "W1": (ENTRY, INFO, GENERIC),
    "W2": (ENTRY, INFO, GENERIC, CORR),
    "W3": (ENTRY, INFO, REPORT),
    "H1": (ENTRY, HOOK),
    "H2": (ENTRY, HOOK),
}

TASK_TEXT = {
    "W1": """根据下列材料起草 220—300 字会议通知，只输出正文。保留标题、称谓和以下顺序：会议时间、会议地点、参会人员、会议事项、联系人；末尾保留信息管理处与 2026 年 8 月 11 日。材料：各部门；会议时间为 2026 年 8 月 18 日 14:30；第二会议室；各部门业务联络员参加；事项为核对第三季度数据目录更新情况；联系人周宁，电话 010-66778899。不得补回执、请假、附件、主持人、会期、责任、台账或后续安排；短稿不得拆成一二级标题或制造无谓空行。""",
    "W2": """按用户既有格式起草复函，只输出正文，依次保留：标题《市文化馆关于数据接口联调事项的复函》、主送“市图书馆：”、办理意见、附件、反馈期限、联系人、落款和日期。材料：同意 8 月 20 日 9:00—11:00 开展接口联调；附件为《联调字段清单》；请于 8 月 15 日前将确认意见发送至 data@example.org；联系人陈宁，010-66881234；落款市文化馆；日期 2026 年 8 月 11 日。不得新增依据、责任分工、审批、台账、验收、成效或后续机制。""",
    "W3": """按用户固定四栏“基本情况—核查结果—当前状态—落款”起草情况报告，只输出正文，栏目名称和顺序逐字保留。材料：8 月 10 日核查 36 个账号，31 个配置一致，5 个需继续核对；5 项尚未形成核对结论；不得改写为正在核查、正在研究或已安排处理；落款信息管理处，日期 2026 年 8 月 11 日。不得补原因、责任、期限、整改、台账、制度或下一步动作。""",
    "H1": """材料与 D0：2026年8月11日10时统一查询接口延迟，10时08分恢复；延迟原因尚未查明。finding 为 unresolved-conclusion-tail，命中“尚未查明”；材料没有调查、排查、核查或处理动作。请严格依照当前 gate_stop_hook.py 的 repair instruction 和 semantic verdict instruction 完成一次语义判断。最终只输出两行：第一行 H1；第二行最终拟交付正文。不得输出 JSON、读取过程、判决过程或说明。""",
    "H2": """材料与 D0：统一认证接口延迟原因正在核查。finding 为 protective-negative-inference 的人工复核控制；材料明确给出“正在核查”。请严格依照当前 gate_stop_hook.py 的 repair instruction 和 semantic verdict instruction 完成一次语义判断。最终只输出两行：第一行 H2；第二行最终拟交付正文。不得输出 JSON、读取过程、判决过程或说明。""",
}

JUDGE_GUIDE = """你是 1.6.0 组合回归的匿名裁判。每组 A/B 来自同一任务。不得猜测身份。先判事实、数字、日期、状态、标题、字段顺序、主送、附件、落款和输出范围，再判直接采用成本。逐组给 A、B 的 PASS/WARN/FAIL，并给 A优、B优或难分。

W1：标题、称谓、会议时间、地点、人员、事项、联系人、信息管理处和日期齐全；顺序正确；不得补材料外事项；短稿不应拆成一二级标题或大量空行。
W2：固定标题、主送、同意联调、完整时段、附件、反馈期限和邮箱、联系人电话、落款日期齐全且顺序不乱；不得新增依据、责任、审批、台账、验收、成效或后续机制。
W3：四个栏目名称和顺序逐字保留；36=31+5，5项尚未形成结论；不得升级为正在核查、研究、安排处理或补后续动作。
H1：必须保持“尚未查明”，不得加入“正在核查”等材料外进行态。H2：必须保留材料明确的“正在核查”，不得误删或改成其他未决状态。

任何 Candidate 独有硬错误都要单列；两臂共有问题、语言偏好和无法关联题面硬边界的波动分别说明。"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def tree_manifest(root: Path) -> dict[str, str]:
    skill = root / SKILL_REL
    return {
        path.relative_to(skill).as_posix(): sha256_file(path)
        for path in sorted(skill.rglob("*"), key=lambda p: p.as_posix().lower())
        if path.is_file()
    }


def validate_roots() -> tuple[dict[str, str], dict[str, str]]:
    manifests = {arm: tree_manifest(root) for arm, root in RUNTIME_ROOTS.items()}
    if set(manifests["baseline"]) != set(manifests["candidate"]):
        raise RuntimeError("runtime file sets differ")
    changed = {
        path
        for path in manifests["baseline"]
        if manifests["baseline"][path] != manifests["candidate"][path]
    }
    expected = {
        "SKILL.md",
        "references/genre-playbooks.md",
        "references/genre-checklist-report.md",
        "references/genre-playbook-correspondence.md",
        "references/genre-playbook-minutes.md",
        "references/genre-playbook-plan-construction.md",
        "scripts/gate_stop_hook.py",
    }
    if changed != expected:
        raise RuntimeError(f"unexpected runtime diff: {sorted(changed)}")
    for root in RUNTIME_ROOTS.values():
        if (root / "AGENTS.md").exists():
            raise RuntimeError(f"runtime must not contain AGENTS.md: {root}")
    return manifests["baseline"], manifests["candidate"]


def read_command(paths: tuple[str, ...]) -> str:
    joined = ",".join(f"'{path.replace('/', chr(92))}'" for path in paths)
    return f"Get-Content -LiteralPath {joined}"


def build_prompt(task: str) -> str:
    paths = REQUIRED_READS[task]
    route_note = ""
    if task == "W3":
        route_note = "不得读取 .agents\\skills\\chinese-official-writing\\references\\genre-playbooks.md。"
    return (
        "这是中文公文 Skill 的只读真实任务。只使用当前工作目录中的本地 "
        ".agents\\skills\\chinese-official-writing，不得读取 C:\\Users\\admin\\.agents、"
        "其他 Skill、副本、tests/evidence、历史结果、git diff/log 或其他 worktree；不得修改文件。"
        "第一步必须调用 shell_command 实际执行：\n"
        + read_command(paths)
        + "\n完整读取这些文件后再完成任务。"
        + route_note
        + "若读取失败，最终只输出 ENV_INVALID。最终不得回显读取过程、规则、命令或自评。\n\n"
        + TASK_TEXT[task]
    )


def command_paths(trace_path: Path) -> list[str]:
    commands: list[str] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line).get("item") or {}
        except json.JSONDecodeError:
            continue
        if item.get("type") == "command_execution" and item.get("status") == "completed":
            commands.append(str(item.get("command") or ""))
    return commands


def normalized_command_blob(commands: list[str]) -> str:
    return "\n".join(commands).replace("\\\\", "/").replace("\\", "/").lower()


def load_valid(task: str, trace_path: Path) -> tuple[bool, list[str]]:
    commands = command_paths(trace_path)
    blob = normalized_command_blob(commands)
    issues: list[str] = []
    for path in REQUIRED_READS[task]:
        if path.lower() not in blob:
            issues.append(f"missing_read:{path}")
    if task == "W3" and GENERIC.lower() in blob:
        issues.append("forbidden_generic_playbook_read")
    for forbidden in ("tests/evidence", "git diff", "git log", "c:/users/admin/.agents"):
        if forbidden in blob:
            issues.append(f"forbidden_trace:{forbidden}")
    return not issues, issues


def final_shape_valid(task: str, final: str) -> bool:
    if not final.strip() or "ENV_INVALID" in final:
        return False
    if task.startswith("H"):
        lines = [line.strip() for line in final.splitlines() if line.strip()]
        return len(lines) == 2 and lines[0] == task
    return not any(token in final for token in ("读取过程", "SHA-256", "自评：", "```"))


def run_one(provider: str, task: str, arm: str, order: int) -> dict[str, object]:
    slug = f"{provider}-{task.lower()}-{arm}"
    final_path = OUT / f"{slug}.final.txt"
    trace_path = OUT / f"{slug}.trace.jsonl"
    stderr_path = OUT / f"{slug}.stderr.txt"
    prompt = build_prompt(task)
    command = [
        shutil.which("codex") or "codex",
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-C",
        str(RUNTIME_ROOTS[arm]),
        "-m",
        MODELS[provider],
        "-c",
        f'openai_base_url="{BASE_URL}"',
        "-c",
        f'model_catalog_json="{CATALOG}"',
        "-c",
        'model_reasoning_effort="max"',
        "-s",
        "read-only",
        "--ephemeral",
        "--json",
        "-o",
        str(final_path),
        prompt,
    ]
    started = time.monotonic()
    timeout = False
    try:
        completed = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=900,
            check=False,
        )
        return_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timeout = True
        return_code = None
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
    trace_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    final = final_path.read_text(encoding="utf-8") if final_path.exists() else ""
    trace_ok, trace_issues = load_valid(task, trace_path)
    shape_ok = final_shape_valid(task, final)
    return {
        "provider": provider,
        "model": MODELS[provider],
        "thinking": "max",
        "task": task,
        "arm": arm,
        "order": order,
        "return_code": return_code,
        "timeout": timeout,
        "duration_seconds": round(time.monotonic() - started, 3),
        "retry_count": 0,
        "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "final_file": final_path.name,
        "final_sha256": sha256_bytes(final.encode("utf-8")) if final else None,
        "final_chars": len(final),
        "trace_file": trace_path.name,
        "trace_sha256": sha256_file(trace_path),
        "trace_load_valid": trace_ok,
        "trace_issues": trace_issues,
        "final_shape_valid": shape_ok,
        "valid": return_code == 0 and not timeout and trace_ok and shape_ok,
    }


def write_packet(records: list[dict[str, object]]) -> tuple[str, dict[str, object]]:
    indexed = {(r["provider"], r["task"], r["arm"]): r for r in records}
    rng = random.Random(20260811)
    mapping: dict[str, object] = {}
    lines = ["# 1.6.0 组合真实回归匿名包", "", JUDGE_GUIDE, ""]
    pair_index = 0
    for task in TASK_ORDER:
        for provider in MODELS:
            pair_index += 1
            pair_id = f"P{pair_index:02d}"
            arms = ["baseline", "candidate"]
            rng.shuffle(arms)
            mapping[pair_id] = {"provider": provider, "task": task, "A": arms[0], "B": arms[1]}
            lines.extend([f"## {pair_id} / {task}", ""])
            for label, arm in zip(("A", "B"), arms):
                record = indexed[(provider, task, arm)]
                body = (OUT / str(record["final_file"])).read_text(encoding="utf-8").strip()
                lines.extend([f"### {label}", "", body, ""])
    return "\n".join(lines).rstrip() + "\n", mapping


def preflight() -> int:
    baseline, candidate = validate_roots()
    changed = sorted(path for path in baseline if baseline[path] != candidate[path])
    payload = {
        "baseline_commit": BASELINE_COMMIT,
        "candidate_commit": CANDIDATE_COMMIT,
        "runtime_file_count": len(baseline),
        "changed_runtime_files": changed,
        "baseline_fingerprint": sha256_bytes(json.dumps(baseline, sort_keys=True).encode("utf-8")),
        "candidate_fingerprint": sha256_bytes(json.dumps(candidate, sort_keys=True).encode("utf-8")),
        "calls_planned": len(PAIR_ORDER) * 2,
        "models": MODELS,
        "thinking": "max",
        "retry_count": 0,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def execute() -> int:
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError(f"output directory is not empty: {OUT}")
    if not CATALOG.is_file():
        raise RuntimeError(f"catalog missing: {CATALOG}")
    baseline, candidate = validate_roots()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, str, str, int]] = []
    for (provider, task), arms in PAIR_ORDER.items():
        jobs.extend((provider, task, arm, order) for order, arm in enumerate(arms, start=1))
    records: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(run_one, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            records.append(record)
            print(json.dumps({key: record[key] for key in ("provider", "task", "arm", "valid", "duration_seconds")}, ensure_ascii=False), flush=True)
    records.sort(key=lambda r: (TASK_ORDER.index(str(r["task"])), str(r["provider"]), str(r["arm"])))
    manifest: dict[str, object] = {
        "baseline_commit": BASELINE_COMMIT,
        "candidate_commit": CANDIDATE_COMMIT,
        "runtime_sha256": {"baseline": baseline, "candidate": candidate},
        "records": records,
        "retry_count": 0,
    }
    valid_pairs = []
    indexed = {(r["provider"], r["task"], r["arm"]): r for r in records}
    for provider, task in PAIR_ORDER:
        if all(indexed[(provider, task, arm)]["valid"] for arm in ("baseline", "candidate")):
            valid_pairs.append(f"{provider}-{task}")
    manifest["valid_pairs"] = valid_pairs
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if len(valid_pairs) != len(PAIR_ORDER):
        print(json.dumps({"status": "invalid", "valid_pairs": len(valid_pairs), "expected": len(PAIR_ORDER)}, ensure_ascii=False), file=sys.stderr)
        return 2
    packet, mapping = write_packet(records)
    packet_bytes = packet.encode("utf-8")
    mapping_bytes = (json.dumps(mapping, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (OUT / "blind-packet.md").write_bytes(packet_bytes)
    MAPPING_PATH.write_bytes(mapping_bytes)
    manifest.update({
        "blind_packet_sha256": sha256_bytes(packet_bytes),
        "blind_packet_chars": len(packet),
        "blind_mapping_sha256": sha256_bytes(mapping_bytes),
    })
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "ready-for-blind-review", "valid_pairs": len(valid_pairs), "packet_sha256": manifest["blind_packet_sha256"]}, ensure_ascii=False))
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
