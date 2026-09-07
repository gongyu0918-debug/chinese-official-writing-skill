"""Narrow the source-check paragraph after preserving the first four attempts."""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("factual_fixed_d0_base", HERE / "run_factual.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
R2 = HERE / "candidate-r2"
ADDITION = """补充原稿事实来源核对：D0 自身不能作事实依据。局部核对具体主办者、介绍者和已经实施的程序，原始材料若没有支持，只删除该无据成分，不改同句其余事实，不顺带润色其他内容。材料明确的职责及对应完成事实可以合并表达；同一已给职责事项的进行态、一般目的、直接支持的一层问题分析和明示的下一步建议应保留，不能仅因材料未逐字列出而删除。一次活动不足以确定整个系统当前阶段，只删除这类无据整体阶段判断，不把它与同事项正在办理混同。不要按“组织”“审核”“正在”等词机械删改。"""


def prepare():
    if R2.exists():
        raise RuntimeError("R2 exists; preserve all attempts")
    R2.mkdir()
    fixture = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
    shutil.copytree(HERE / "frozen-product", R2 / "frozen-product")
    baseline = (HERE / "baseline-system.txt").read_text(encoding="utf-8")
    candidate = baseline.replace("返回唯一、严格的 JSON 对象", ADDITION + "\n\n返回唯一、严格的 JSON 对象")
    for arm, system in (("baseline", baseline), ("candidate", candidate)):
        (R2 / f"{arm}-system.txt").write_text(system, encoding="utf-8", newline="\n")
    fixture.update({"expected_real_calls": 2, "expected_independent_sessions": 2,
        "arms_to_run": ["candidate"], "stage": "candidate-r2",
        "previous_fixture_sha256": base.digest((HERE / "fixture.json").read_bytes()),
        "narrowing_reason": "R1 M5 candidate removed supported same-matter ongoing wording and kept unsupported whole-system stage; restrict local source correction and explicitly distinguish the two.",
        "driver_sha256": base.digest(Path(__file__).read_bytes()),
        "system_sha256": {arm: base.digest((R2 / f"{arm}-system.txt").read_bytes()) for arm in ("baseline", "candidate")}})
    base.save(R2 / "fixture.json", fixture)
    print(json.dumps({"prepared": True, "stage": "candidate-r2", "calls": 2}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--case", choices=("M5", "P6"))
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.case:
        fixture = json.loads((R2 / "fixture.json").read_text(encoding="utf-8"))
        assert fixture["driver_sha256"] == base.digest(Path(__file__).read_bytes())
        base.HERE = R2
        base.run(args.case, "candidate")
    else:
        parser.error("use --prepare or --case")
