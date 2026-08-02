from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prose_lint = load_module(
    "scene_filler_prose_lint",
    ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py",
)


def scene_findings(text: str):
    return [item for item in prose_lint.scan("<scene>", text) if item.label == "scene-filler-cluster"]


class SceneFillerClusterTests(unittest.TestCase):
    def test_clustered_scene_fillers_are_located_as_low_risk_hints(self) -> None:
        samples = [
            "活动期间，负责人亲切会见参会代表，并与大家合影留念。",
            "交流结束后，与会人员合影留念，现场气氛十分热烈。",
            "现场气氛热烈，活动圆满结束。",
            "在融洽的气氛中，本次交流取得圆满成功。",
            "互动环节现场气氛活跃，掌声不断。",
        ]

        for sample in samples:
            with self.subTest(sample=sample):
                findings = scene_findings(sample)
                self.assertTrue(findings)
                self.assertTrue(all(item.severity == "low" for item in findings))

    def test_single_facts_and_normal_official_prose_are_not_flagged(self) -> None:
        samples = [
            "在工作人员指导下，35名参训人员完成终端操作练习。",
            "办公室负责人会见企业代表，逐项核对申请材料和办理时限。",
            "活动结束后，与会人员合影留念。",
            "接待人员亲切会见来访代表。",
            "巡检覆盖18个综合窗口，发现的2项设备问题已于当日恢复。",
            "信息技术科负责设备检查和技术处置，大厅管理科负责现场协调。",
            "项目建设期为2026年8月至10月，验收范围以批复的建设内容为准。",
            "可研报告已列明投资估算、建设周期和系统边界，本次只复核三项数据的一致性。",
        ]

        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(scene_findings(sample), [])

    def test_clean_corpus_has_no_scene_filler_cluster_findings(self) -> None:
        corpus = json.loads(
            (ROOT / "tests" / "fixtures" / "clean_prose_corpus.json").read_text(encoding="utf-8")
        )

        for item in corpus["items"]:
            with self.subTest(item=item["id"]):
                self.assertEqual(scene_findings(item["text"]), [])

    def test_archived_real_drafts_have_no_scene_filler_cluster_findings(self) -> None:
        drafts = [
            "tests/evidence/candidate-b-writing-20260715/terra-t01.md",
            "tests/evidence/candidate-b-writing-20260715/terra-t02.md",
            "tests/evidence/candidate-b-writing-20260715/terra-t03.md",
            "tests/evidence/candidate-b-writing-20260715/terra-t04.md",
            "tests/evidence/candidate-b-writing-20260715/luna-t01.md",
            "tests/evidence/candidate-b-writing-20260715/luna-t03.md",
            "tests/evidence/candidate-b-writing-20260715/luna-t04.md",
        ]

        for relative_path in drafts:
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertEqual(scene_findings(text), [])

    def test_low_scene_hint_does_not_fail_medium_gate(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "scene.txt"
            draft.write_text("现场气氛热烈，活动圆满结束。", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(draft),
                    "--strict",
                    "--fail-on",
                    "medium",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("scene-filler-cluster", result.stdout)


if __name__ == "__main__":
    unittest.main()
