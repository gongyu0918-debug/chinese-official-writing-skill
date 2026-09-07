"""Four fixed-D0 factual review calls; reuse the frozen no-tool CLI harness."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE_COMMIT = "b77f6381438c8fa01f8576c205d13af4b8a987fd"
MODEL = "alibaba-token-plan-2/deepseek-v4-flash-0731"
HARNESS = ROOT / "maintenance/tests/evidence/date-source-real-r1/run.py"
CONTRACT_REL = "chinese-official-writing/hooks/core/single_pass_final_review.py"
ANCHORS_REL = "chinese-official-writing/hooks/shared/hard_anchors.py"
PACKET_ROOT = ROOT / "maintenance/tests/evidence/natural-writing-stability-r1/raw/r2"
PACKETS = {
    "P6": ("report-fourth-packet.json", "3127a9501441b66a585be4f3ddcb811a61ea3de1f5f6357dd8baa813be4c4124"),
    "M5": ("minutes-second-packet.json", "b2c2089a68641d766f9fc973c540ac0046692f0c07eff422206befa13ae29104"),
}
ADDITION = """补充原稿事实来源核对：逐句对照原始材料核对 D0 的具体主体、动作、对象和状态；D0 自身不能作为事实来源。材料未给的组织者、介绍者、已经实施的审核程序或整个系统所处阶段，不得因部门职责或某次活动而补成既成事实。发现此类错误，只删除或纠正无据成分，保留有依据的事件、数字、主体、角色和状态。材料已有的职责与对应完成事实可以直接归纳；一般目的、材料直接支持的一层分析和明确作为下一步建议的措施，不能仅因材料未逐字列出而删除。不要按“组织”“审核”等词机械删改。"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_hash(value: str) -> str:
    return digest(value.encode("utf-8"))


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def prepare() -> None:
    if (HERE / "fixture.json").exists():
        raise RuntimeError("fixture exists; do not overwrite")
    actual_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if actual_head != BASE_COMMIT:
        raise RuntimeError("base changed")
    frozen = {}
    for rel in (CONTRACT_REL, ANCHORS_REL):
        content = subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{rel}"], cwd=ROOT)
        target = HERE / "frozen-product" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        frozen[str(target.relative_to(HERE))] = digest(content)
    contract = load_module("factual_frozen_contract_prepare", HERE / "frozen-product" / CONTRACT_REL)
    baseline = contract.REVIEW_INSTRUCTIONS
    marker = "返回唯一、严格的 JSON 对象"
    assert baseline.count(marker) == 1
    candidate = baseline.replace(marker, ADDITION + "\n\n" + marker)
    for arm, instructions in (("baseline", baseline), ("candidate", candidate)):
        (HERE / f"{arm}-system.txt").write_text(instructions, encoding="utf-8", newline="\n")
    cases = []
    for case_id, (name, expected_hash) in PACKETS.items():
        path = PACKET_ROOT / name
        assert digest(path.read_bytes()) == expected_hash
        packet = json.loads(path.read_text(encoding="utf-8"))
        chain, = [c for c in packet["chains"] if c["id"] == case_id]
        r1, = [r for r in chain["rounds"] if r["round"] == 1]
        assert text_hash(r1["text"]) == r1["sha256"]
        request, draft = r1["prompt"], r1["text"]
        cases.append({"id": case_id, "source_packet": str(path.relative_to(ROOT)),
                      "source_packet_sha256": expected_hash, "source_round": 1,
                      "request": request, "request_sha256": text_hash(request),
                      "d0": draft, "d0_sha256": r1["sha256"],
                      "user_message": contract.build_messages(request, draft)[1]["content"]})
    harness_paths = [HARNESS,
        ROOT / "maintenance/tests/evidence/hook-audit-quality-r1/replay_real_d0.py",
        ROOT / "maintenance/tests/evidence/v167-formulaic-mechanicality-real-first/harness.py"]
    fixture = {"schema_version": 1, "base_commit": BASE_COMMIT, "model": MODEL,
        "expected_real_calls": 4, "expected_independent_sessions": 4,
        "method": "same real complete R1 D0 and original full source; fixed single_pass system/user contract through existing no-tool CLI harness; one independent session per call",
        "not_measured": ["natural Skill routing", "native Hook lifecycle", "cross-turn persistence", "general writing reliability"],
        "automatic_retry": False, "automatic_fallback": False,
        "frozen_product_sha256": frozen,
        "harness_sha256": {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in harness_paths},
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "system_sha256": {arm: digest((HERE / f"{arm}-system.txt").read_bytes()) for arm in ("baseline", "candidate")},
        "cases": cases,
        "human_review_targets": {
          "P6": {"correction": ["材料未给的已完成合规性和可用性审核", "材料未给的市数据局组织专题交流"],
                 "preserve": ["市数据局统筹、市信息中心技术核验、业务主管部门授权范围复核", "3个场景完成技术核验且结论待复核，技术核验不代表上线批准", "目录及场景数字、尚未完成/未确定/未决定状态", "待核比例计算、材料直接支持的一层问题分析和明确下一步建议"]},
          "M5": {"correction": ["材料未给的信息部介绍和组织操作演示", "从一次演示外推整个系统当前阶段"],
                 "preserve": ["信息部提出预约系统试点建议但未决定", "业务部意见办理及9月12日责任期限", "综合部成本测算及9月15日责任期限，不作新增预算承诺", "9名馆员和8月26日演示，不是培训且未形成验收结论", "一般活动目的、已有责任期限的按期落实和直接支持的待研究承接"]}},
        "selection_rule": "store the real raw model proposal and run the unchanged frozen parse_selection; no hand-written D1 or verdict; rejected D1 is not successful final delivery"}
    save(HERE / "fixture.json", fixture)
    print(json.dumps({"prepared": True, "cases": [c["id"] for c in cases], "calls": 4}, ensure_ascii=False))


def run(case_id: str, arm: str) -> None:
    fixture = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
    assert fixture["runner_sha256"] == digest(Path(__file__).read_bytes())
    for rel, expected in fixture["frozen_product_sha256"].items():
        assert digest((HERE / rel).read_bytes()) == expected
    for rel, expected in fixture["harness_sha256"].items():
        assert digest((ROOT / rel).read_bytes()) == expected
    system = (HERE / f"{arm}-system.txt").read_text(encoding="utf-8")
    assert text_hash(system) == fixture["system_sha256"][arm]
    case, = [c for c in fixture["cases"] if c["id"] == case_id]
    assert text_hash(case["d0"]) == case["d0_sha256"]
    assert text_hash(case["request"]) == case["request_sha256"]
    real = load_module("factual_reused_real_cli", HARNESS)
    contract = load_module("factual_frozen_contract_run", HERE / "frozen-product" / CONTRACT_REL)
    cli = shutil.which("claude")
    if not cli:
        raise RuntimeError("existing CLI missing; no installation")
    lane = HERE / "calls" / case_id / arm
    original_command = real.command

    def fixed_system_command(claude, model):
        argv = original_command(claude, model) + ["--system-prompt", system]
        save(lane / "invocation.json", {"argv": argv, "prompt_sha256": text_hash(case["user_message"]),
             "system_sha256": text_hash(system), "request_sha256": case["request_sha256"],
             "d0_sha256": case["d0_sha256"], "source_base_commit": BASE_COMMIT})
        return argv

    real.command = fixed_system_command
    print("START", case_id, arm, MODEL, flush=True)
    raw, receipt = real.restricted_reply(MODEL, case["user_message"], lane, cli)
    selection = contract.parse_selection(raw, case["d0"], case["request"])
    selected_path = lane / "contract-selected.txt"
    selected_path.write_text(selection.text, encoding="utf-8", newline="\n")
    payload = None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        pass
    proposal = payload.get("final_text") if isinstance(payload, dict) else None
    if isinstance(proposal, str) and proposal:
        (lane / "model-proposal.txt").write_text(proposal, encoding="utf-8", newline="\n")
    comparison = None
    if isinstance(proposal, str) and proposal:
        anchors = contract._load_hard_anchors()
        comparison = anchors.compare(case["d0"], proposal, case["request"],
                      ignored_authority_values=contract._ignored_length_values(anchors, case["request"]))
    records = [json.loads(line) for line in (lane / "stream.jsonl").read_text(encoding="utf-8").splitlines()]
    session_ids = sorted({r["session_id"] for r in records if r.get("session_id")})
    result = {"case": case_id, "arm": arm, "model": MODEL, "technical_valid": receipt["technical_valid"],
              "session_ids": session_ids, "source_round": 1, "seconds": receipt["seconds"],
              "request_sha256": case["request_sha256"], "d0_sha256": case["d0_sha256"],
              "raw_model_payload": payload, "raw_reply_sha256": text_hash(raw),
              "contract_selection": asdict(selection), "contract_selected_sha256": text_hash(selection.text),
              "hard_anchor_comparison": comparison,
              "human_quality_review": "pending; model issues are model claims only",
              "raw_files_sha256": {p.name: digest(p.read_bytes()) for p in lane.iterdir() if p.is_file()}}
    save(lane / "result.json", result)
    print(json.dumps({"case": case_id, "arm": arm, "technical_valid": receipt["technical_valid"],
                      "session_ids": session_ids, "model_action": payload.get("action") if isinstance(payload, dict) else None,
                      "contract_action": selection.action, "contract_reason": selection.reason,
                      "seconds": receipt["seconds"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--case", choices=tuple(PACKETS))
    parser.add_argument("--arm", choices=("baseline", "candidate"))
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.case and args.arm:
        run(args.case, args.arm)
    else:
        parser.error("use --prepare or --case and --arm")
