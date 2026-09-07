"""One real M5 call isolating body factual corrections from wrapper anchors."""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("factual_fixed_d0_base_r3", HERE / "run_factual.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
R3 = HERE / "candidate-r3"
EXPERIMENT = """本轮为隔离正文事实修正与外围硬锚冲突的实验，以下范围约束优先于前述一般复核和交付要求：
1. 只修正 D0 中材料外的具体主办者、介绍者等主体归属，以及已经实施的具体程序；D0 自身不能作为事实来源。无据时仅删除该无据成分，保留同句其他文字和全部其他段落。不要扩展处理整体系统阶段或其他类别问题，不顺带润色。
2. 材料已有职责与对应完成事实可以合并表达；同一已给职责事项的进行态、一般目的、直接支持的一层分析、明确的下一步建议应保留，不因材料未逐字列出而删除，不按“组织”“审核”“正在”等词机械删改。
3. 本实验必须将 D0 全部正文外字数、过程介绍、修改附言、自检、分隔线及原有引号逐字保留；不检查或清理包装，不改正文标题、段落边界和其他文字。本条仅为分离硬锚冲突，不是正式文稿的最终交付要求。
4. 仍返回原合同的唯一 JSON 对象，字段和 action、issues 取值保持不变。若 REPLACE，final_text 必须包含保留原样的全部外围文本和局部修正后的完整正文；若无需本范围内修正则 KEEP。不要另加任何实验说明或手工裁决。"""


def prepare():
    if R3.exists():
        raise RuntimeError("R3 exists; preserve all attempts")
    R3.mkdir()
    fixture = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
    shutil.copytree(HERE / "frozen-product", R3 / "frozen-product")
    baseline = (HERE / "baseline-system.txt").read_text(encoding="utf-8")
    candidate = baseline + "\n\n" + EXPERIMENT
    for arm, system in (("baseline", baseline), ("candidate", candidate)):
        (R3 / f"{arm}-system.txt").write_text(system, encoding="utf-8", newline="\n")
    fixture.update({"expected_real_calls": 1, "expected_independent_sessions": 1,
        "cases_to_run": ["M5"], "arms_to_run": ["candidate"], "stage": "candidate-r3",
        "previous_fixture_sha256": base.digest((HERE / "fixture.json").read_bytes()),
        "r1_r2_result_sha256": base.digest((HERE / "result.json").read_bytes()),
        "experiment_boundary": "Preserve all real D0 wrapper bytes to isolate body fact/role anchor relation behavior; not a usable final-delivery experiment. One M5 call only; both original source/D0 cases remain frozen in fixture.",
        "driver_sha256": base.digest(Path(__file__).read_bytes()),
        "system_sha256": {arm: base.digest((R3 / f"{arm}-system.txt").read_bytes()) for arm in ("baseline", "candidate")}})
    base.save(R3 / "fixture.json", fixture)
    print(json.dumps({"prepared": True, "stage": "candidate-r3", "calls": 1}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.run:
        fixture = json.loads((R3 / "fixture.json").read_text(encoding="utf-8"))
        assert fixture["driver_sha256"] == base.digest(Path(__file__).read_bytes())
        base.HERE = R3
        base.run("M5", "candidate")
    else:
        parser.error("use --prepare or --run")
