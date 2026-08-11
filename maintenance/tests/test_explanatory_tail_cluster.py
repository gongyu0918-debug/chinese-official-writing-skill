from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prose_lint = load_module(
    "explanatory_tail_prose_lint",
    ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py",
)


def tail_findings(text: str, *, include_structure: bool = True):
    return [
        item
        for item in prose_lint.scan("<tail>", text, include_structure=include_structure)
        if item.label == "explanatory-tail-cluster"
    ]


class ExplanatoryTailClusterTests(unittest.TestCase):
    def test_historical_normal_draft_clusters_are_located_once(self) -> None:
        samples = [
            """一、重点工作完成情况

（一）完成数据中台一期建设。项目于年初立项，9月完成建设并正式上线，接入业务系统6个，归集数据表120张，同步制定数据标准3项。通过一期建设，主要业务数据实现统一归集和共享查询，为后续扩大数据共享利用范围提供了基础。

（二）通过网络安全等级保护二级测评。3月启动测评工作，围绕测评发现的问题逐项组织整改，12月通过网络安全等级保护二级测评。测评和整改工作同步推进，进一步明确了网络安全管理中的相关要求。

（三）完成OA系统二期升级。二期升级重点优化流程审批模块并完成移动端适配，11月完成切换上线，审批事项可通过移动端办理。系统上线后，流程审批模块和移动端应用衔接更加顺畅，为日常审批办理提供了支撑。

（四）加强网络安全教育培训。全年组织网络安全培训4次，累计300人次参加，培训对象覆盖各部门。通过开展培训，持续强化各部门人员的网络安全意识，为网络安全管理工作提供了必要保障。""",
            """四、主要任务

（一）开展字段梳理。围绕合同档案电子归集需要，结合现有档案系统字段设置和业务实际，对合同名称、签订日期等关键字段进行梳理，明确字段口径、填写要求和对应关系，为后续归集和核对提供统一依据。

（二）组织存量抽样。结合2025年至2026年新形成合同情况，选取具有代表性的合同样本，对合同电子资料归集情况、字段填写情况和目录对应情况进行抽样检查，了解现有基础，发现归集过程中的具体问题，为优化试点操作提供依据。

（三）推进增量归集。对试点期间涉及的合同电子资料，按照既定范围及时纳入现有档案系统，做到合同形成后同步归集、同步核对，逐步形成增量合同电子归集的常态化操作流程。

（四）做好目录检查和归档接收。围绕合同档案目录项目设置和资料对应关系，对归集后的目录完整性进行检查，对符合要求的电子资料及时接收归档，保证试点资料收得进、查得到、对得上。

（五）汇总试点数据。对试点期间合同归集数量、归集完整情况、关键字段核对情况及目录检查情况进行汇总，形成试点工作数据，为评估试点效果和研究后续安排提供依据。""",
        ]

        for sample in samples:
            with self.subTest(sample=sample[:20]):
                findings = tail_findings(sample)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].severity, "low")

    def test_structure_scan_is_required(self) -> None:
        text = self._three_hit_text()

        self.assertEqual(tail_findings(text, include_structure=False), [])
        self.assertEqual(len(tail_findings(text)), 1)

    def test_two_matching_tails_do_not_form_a_cluster(self) -> None:
        text = """一、事项安排

第一项工作已完成需求核对和接口检查，相关问题均已逐项登记，为后续联调提供了基础。

第二项工作已完成数据校验和权限配置，现有功能已进入试运行阶段，为日常办理提供了支撑。

第三项工作已完成设备巡检和台账更新，巡检发现的问题已按原状态记录并移交处理。"""

        self.assertEqual(tail_findings(text), [])

    def test_section_headings_break_the_cluster(self) -> None:
        text = """一、建设情况

第一项工作已完成需求核对和接口检查，相关问题均已逐项登记，为后续联调提供了基础。

二、运行情况

第二项工作已完成数据校验和权限配置，现有功能已进入试运行阶段，为日常办理提供了支撑。

三、保障情况

第三项工作已完成设备巡检和台账更新，巡检发现的问题已按原状态记录，为日常运行提供了保障。"""

        self.assertEqual(tail_findings(text), [])

    def test_repeated_words_without_complete_tail_structure_are_not_flagged(self) -> None:
        text = """一、工作安排

第一项工作仍需持续推进，现有记录已经移交业务部门按职责办理，相关状态保持不变。

第二项工作仍需持续推进，接口联调按照原定范围开展，测试结果由技术部门汇总。

第三项工作仍需持续推进，设备巡检覆盖既定点位，发现的问题按现有流程处理。"""

        self.assertEqual(tail_findings(text), [])

    def test_clean_corpus_has_no_explanatory_tail_cluster(self) -> None:
        corpus = json.loads(
            (ROOT / "maintenance" / "tests" / "fixtures" / "clean_prose_corpus.json").read_text(encoding="utf-8")
        )

        for item in corpus["items"]:
            with self.subTest(item=item["id"]):
                self.assertEqual(tail_findings(item["text"]), [])

    def test_archived_clean_drafts_have_no_explanatory_tail_cluster(self) -> None:
        drafts = [
            "maintenance/tests/evidence/candidate-b-writing-20260715/terra-t01.md",
            "maintenance/tests/evidence/candidate-b-writing-20260715/terra-t02.md",
            "maintenance/tests/evidence/candidate-b-writing-20260715/terra-t03.md",
            "maintenance/tests/evidence/candidate-b-writing-20260715/terra-t04.md",
            "maintenance/tests/evidence/candidate-b-writing-20260715/luna-t01.md",
            "maintenance/tests/evidence/candidate-b-writing-20260715/luna-t03.md",
            "maintenance/tests/evidence/candidate-b-writing-20260715/luna-t04.md",
        ]

        for relative_path in drafts:
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertEqual(tail_findings(text), [])

    def test_low_hint_does_not_fail_medium_gate_or_modify_input(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        original = self._three_hit_text()
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "draft.txt"
            draft.write_text(original, encoding="utf-8")
            before = draft.read_bytes()
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(draft),
                    "--structure",
                    "--strict",
                    "--fail-on",
                    "medium",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            after = draft.read_bytes()

        self.assertEqual(result.returncode, 0)
        self.assertIn("explanatory-tail-cluster", result.stdout)
        self.assertEqual(before, after)

    @staticmethod
    def _three_hit_text() -> str:
        return """一、工作情况

第一项工作已完成需求核对、接口检查和问题登记，相关记录已经按业务系统分类整理，为后续联调提供了基础。

第二项工作已完成数据校验、权限配置和功能验证，现有功能已经按照既定范围进入试运行阶段，为日常办理提供了支撑。

第三项工作已完成设备巡检、台账更新和状态复核，巡检发现的问题已经按原状态登记并移交处理，为日常运行提供了保障。"""


if __name__ == "__main__":
    unittest.main()
