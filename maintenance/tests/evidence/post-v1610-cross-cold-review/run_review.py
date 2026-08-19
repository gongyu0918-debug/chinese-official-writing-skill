#!/usr/bin/env python3
"""Run three read-only cold reviews against one frozen multi-range diff packet."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/post-v1610-cross-cold-review/formal-r1"
RUNTIME = ROOT / "output/post-v1610-cross-cold-review/runtime-r1"
BASE_URL = "http://127.0.0.1:10100/v1"
CATALOG = Path.home() / ".codex/opencodex-catalog.json"
TIMEOUT_SECONDS = 1200
RANGES = {
    "A": ("v1.6.10", "3084ee567eefb80b47e1cd40aea1a13399734282"),
    "B": ("3084ee567eefb80b47e1cd40aea1a13399734282", "b0e72a263c87bf19d3eaa36b2600caee61880669"),
    "C": ("b0e72a263c87bf19d3eaa36b2600caee61880669", "c3477de3cb29251a8df13b4ff1ccb7b60ed2bb58"),
    "D": ("3084ee567eefb80b47e1cd40aea1a13399734282", "740154b3c847114b4ac7473eab20a342e141fbc5"),
}
MODELS = {
    "qwen": "alibaba-token-plan-2/qwen3.8-max",
    "grok": "xai/grok-4.6",
    "kimi": "ollama-cloud/kimi-k3",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True,
    )
    return completed.stdout


def build_packet() -> str:
    chunks = [
        "# v1.6.10 后多范围冻结 DIFF 冷审包",
        "",
        "范围 A 为公开 main 的近期增量；B 为公开 main 到付费提纲叠加；",
        "C 为付费叠加到 Claude 提纲+篇幅组合实验；D 为本轮风险台账。",
    ]
    for label, (start, end) in RANGES.items():
        chunks.extend([
            "",
            f"## RANGE {label}: {start}..{end}",
            "",
            "### COMMITS",
            "```text",
            git("log", "--oneline", f"{start}..{end}").rstrip(),
            "```",
            "",
            "### DIFF",
            "```diff",
            git("diff", "--no-ext-diff", "--unified=40", f"{start}..{end}").rstrip(),
            "```",
        ])
    return "\n".join(chunks) + "\n"


def build_prompt(packet: str, packet_sha256: str) -> str:
    return (
        "你是独立代码与产品冷审员。禁止调用工具、读取文件、联网或修改任何内容；"
        "只能使用下方冻结 packet。重点核查最近几次 diff：写作语义是否造成事实、状态或责任主体回退；"
        "中文数量透明归纳与共享硬锚是否有可复现漏洞；付费提纲 companion 与 Claude 有序组合的生命周期、"
        "回退、hash、路由和 allowlist 是否正确；篇幅不足 verifier 是否存在自审误放、证据夸大或待办遗漏；"
        "文档、规格、测试、实现是否互相矛盾；是否有孤儿路由、只有测试可达的代码或过时状态。"
        "只报告可从 packet 复现的 P0/P1/P2。不要泛泛要求更多测试，不要把已明确 HOLD 的能力说成已发布缺陷，"
        "不要用总体文采胜负否决新增兜底功能。区分确认缺陷、HOLD/证据缺口、已正确处理。"
        "只输出一个 JSON 对象，不要 Markdown。结构为："
        '{"reviewer_model":"实际模型ID","effort":"ultra","packet_sha256":"哈希",'
        '"scope":["A","B","C","D"],"overall":"PASS|HOLD|FAIL",'
        '"findings":[{"priority":"P0|P1|P2","range":"A|B|C|D","path":"路径",'
        '"line_or_symbol":"行或符号","title":"标题","evidence":"可复现证据",'
        '"impact":"影响","minimal_fix":"最小修复"}],"confirmed_safe":["已核实事项"],'
        '"remaining_holds":["非缺陷但未闭环事项"]}。'
        f"冻结 packet SHA-256={packet_sha256}。\n\n{packet}"
    )


def run_one(label: str, model: str, prompt: str, packet_sha256: str) -> dict[str, object]:
    model_out = OUT / label
    runtime = RUNTIME / label
    model_out.mkdir(parents=True)
    runtime.mkdir(parents=True)
    final_path = model_out / "final.json"
    command = [
        shutil.which("codex") or "codex", "exec", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--ephemeral", "-s", "read-only", "-C", str(runtime),
        "-m", model, "-c", f'openai_base_url="{BASE_URL}"',
        "-c", f'model_catalog_json="{CATALOG}"', "-c", 'model_reasoning_effort="ultra"',
        "-o", str(final_path), "-",
    ]
    started = time.monotonic()
    timeout = False
    try:
        result = subprocess.run(
            command, input=prompt, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=TIMEOUT_SECONDS, check=False,
            env=os.environ.copy(),
        )
        return_code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        timeout, return_code = True, -9
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
    duration = round(time.monotonic() - started, 3)
    final = final_path.read_text(encoding="utf-8") if final_path.exists() else ""
    parsed = None
    parse_error = None
    if final:
        try:
            parsed = json.loads(final)
        except json.JSONDecodeError as exc:
            parse_error = f"json:{exc.pos}"
    write_text(model_out / "stdout.txt", stdout)
    write_text(model_out / "stderr.txt", stderr)
    receipt = {
        "label": label,
        "commanded_model": model,
        "effort": "ultra",
        "packet_sha256": packet_sha256,
        "return_code": return_code,
        "timeout": timeout,
        "duration_seconds": duration,
        "retry_count": 0,
        "final_sha256": sha256_text(final) if final else None,
        "json_valid": isinstance(parsed, dict),
        "parse_error": parse_error,
    }
    write_text(model_out / "receipt.json", json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return receipt


def main() -> int:
    if OUT.exists() or RUNTIME.exists():
        raise SystemExit("formal output/runtime already exists")
    packet = build_packet()
    packet_sha256 = sha256_text(packet)
    OUT.mkdir(parents=True)
    write_text(OUT / "packet.md", packet)
    write_text(OUT / "freeze.json", json.dumps({
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ranges": RANGES,
        "packet_sha256": packet_sha256,
    }, ensure_ascii=False, indent=2) + "\n")
    prompt = build_prompt(packet, packet_sha256)
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_one, label, model, prompt, packet_sha256): label for label, model in MODELS.items()}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: str(item["label"]))
    write_text(OUT / "manifest.json", json.dumps({
        "packet_sha256": packet_sha256,
        "results": results,
    }, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"packet_sha256": packet_sha256, "results": results}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
