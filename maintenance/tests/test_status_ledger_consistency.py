from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def table_row(text: str, item_id: str) -> str:
    match = re.search(rf"^\| `{re.escape(item_id)}` .*?$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing coverage row: {item_id}")
    return match.group(0)


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"missing roadmap section: {heading}")
    end = text.find("\n## ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


class StatusLedgerConsistencyTests(unittest.TestCase):
    def test_current_release_record_is_v1620(self) -> None:
        public_readme = read("README.md")
        todo = read("maintenance/docs/待办.md")
        roadmap = read("maintenance/specs/roadmap.md")

        self.assertIn("当前产品 tag 为 `v1.6.20^{commit}=2fc9d1d4", todo)
        self.assertIn("`release-1.6.20.md`", todo)
        self.assertIn("## v1.6.14 起已发布状态与后续研究", todo)
        self.assertNotIn("候选均保持 HOLD", public_readme)
        self.assertIn("`v1.6.20` 小版本已发布", roadmap)
        self.assertNotIn("当前产品 tag 为 `v1.6.19", todo)

    def test_oc003_is_closed_on_every_active_status_surface(self) -> None:
        for relative in (
            "maintenance/specs/requirements.md",
            "maintenance/specs/coverage.md",
            "maintenance/specs/roadmap.md",
            "maintenance/docs/待办.md",
            "maintenance/docs/evidence/README.md",
        ):
            with self.subTest(relative=relative):
                self.assertIn("OC-003", read(relative))

        requirements = read("maintenance/specs/requirements.md")
        coverage_row = table_row(read("maintenance/specs/coverage.md"), "OC-003")
        self.assertIn("条件性研究或风险控制建议", requirements)
        self.assertIn("反向条件结论", requirements)
        self.assertIn("DONE_V1.6.16", coverage_row)
        self.assertIn("已随 v1.6.16 发布", coverage_row)
        self.assertIn("合成材料状态", coverage_row)
        self.assertNotIn("MINIMAL_SCOPE_REPAIR_REQUIRED", coverage_row)
        self.assertNotIn("公开 main 尚未包含候选规则", coverage_row)
        self.assertIn(
            "oc003-r2-state-layering/result.md",
            read("maintenance/docs/evidence/README.md"),
        )
        roadmap = read("maintenance/specs/roadmap.md")
        self.assertIn("`OC-003` 算力可研状态与程序边界已完成", section(roadmap, "DONE"))
        self.assertNotIn("OC-003", section(roadmap, "IN_PROGRESS"))
        self.assertRegex(
            read("maintenance/docs/待办.md"),
            r"(?m)^- \[x\] `OC-003`.*DONE_V1\.6\.16",
        )

    def test_rejected_prompt_atoms_are_not_left_as_active_hold(self) -> None:
        coverage = read("maintenance/specs/coverage.md")
        roadmap = read("maintenance/specs/roadmap.md")
        todo = read("maintenance/docs/待办.md")

        self.assertIn("REJECTED_CANDIDATE / WAIT_NEW_COUNTEREXAMPLE", table_row(coverage, "WR-012"))
        self.assertIn("## REJECTED", roadmap)
        self.assertIn("## TERMINATED", roadmap)
        self.assertIn("## WAIT_NEW_COUNTEREXAMPLE", roadmap)
        self.assertNotIn("## HOLD", roadmap)
        in_progress = section(roadmap, "IN_PROGRESS")
        for item_id in ("WR-012", "MT-005b2", "MT-005b3", "MT-005b4"):
            with self.subTest(item_id=item_id):
                self.assertRegex(todo, rf"(?m)^- \[x\] `{re.escape(item_id)}`")
                self.assertNotRegex(todo, rf"(?m)^- \[ \] `{re.escape(item_id)}`.*HOLD")
                self.assertNotIn(item_id, in_progress)

    def test_reference_slimming_atoms_are_terminal(self) -> None:
        roadmap = read("maintenance/specs/roadmap.md")
        todo = read("maintenance/docs/待办.md")
        evidence_index = read("maintenance/docs/evidence/README.md")
        result = read("maintenance/tests/evidence/reference-slimming-r1/result.md")
        rejected = section(roadmap, "REJECTED")
        in_progress = section(roadmap, "IN_PROGRESS")

        for item_id in (
            "MINUTES-CHECKLIST-LEAF-R1",
            "NOTICE-LEAF-CURRENT-R1",
            "PROCUREMENT-ANNOUNCEMENT-LEAF-R1/R2",
            "REVIEW-LAYER-SPLIT-R1",
        ):
            with self.subTest(item_id=item_id):
                self.assertIn(item_id, rejected)
                self.assertIn(item_id, todo)
                self.assertIn(item_id, result)
                self.assertNotIn(item_id, in_progress)

        self.assertIn("reference-slimming-r1/result.md", evidence_index)
        self.assertIn("累计190次真实任务输出", result)
        self.assertNotIn("`HOLD`", rejected)

    def test_ah002_is_a_local_release_candidate_and_prompt_atom_stays_terminated(self) -> None:
        requirements = read("maintenance/specs/requirements.md")
        coverage_row = table_row(read("maintenance/specs/coverage.md"), "AH-002")
        roadmap = read("maintenance/specs/roadmap.md")
        todo = read("maintenance/docs/待办.md")
        evidence_index = read("maintenance/docs/evidence/README.md")

        self.assertIn("### AH-002 新闻完整日期来源绑定修复", requirements)
        self.assertIn("请求中只有一个唯一完整日期", requirements)
        self.assertIn("DONE_V1.6.20", coverage_row)
        self.assertIn("三 provider 九次执行", coverage_row)
        self.assertNotIn("AH-002", section(roadmap, "IN_PROGRESS"))
        self.assertIn("AH-002", section(roadmap, "DONE"))
        self.assertRegex(
            todo,
            r"(?m)^- \[x\] `AH-002`.*DONE_V1\.6\.20",
        )
        self.assertIn(
            "ah002-news-date-completeness-r1/live-result.md",
            evidence_index,
        )
        self.assertNotIn(
            "完整年份遗漏仍是真实风险；重复日期提示方向已经终止，等待新素材",
            section(roadmap, "WAIT_NEW_COUNTEREXAMPLE"),
        )

    def test_wr020_first_draft_rejected_but_existing_draft_atoms_are_closed(self) -> None:
        coverage_row = table_row(read("maintenance/specs/coverage.md"), "WR-020")
        roadmap = read("maintenance/specs/roadmap.md")

        self.assertIn("B1_REJECTED / B2_DONE / WAIT_NEW_COUNTEREXAMPLE", coverage_row)
        self.assertIn("Ollama包装风险保留", coverage_row)
        self.assertIn("`WR-020b1` 讲话首次起草任务卡", section(roadmap, "REJECTED"))
        self.assertIn("`WR-020` 当前长稿基线有写作价值", section(roadmap, "WAIT_NEW_COUNTEREXAMPLE"))

    def test_host_adapters_keep_released_limits_and_record_current_cli_revalidation(self) -> None:
        row = table_row(read("maintenance/specs/coverage.md"), "HK-004")

        self.assertIn("国产 CLI 复核", row)
        self.assertIn(
            "OPENCODE_DONE_V1.6.18 / HERMES_R2_DONE_V1.6.19 / DSH_R1_DONE_V1.6.19 / CURRENT_CLI_R1_REVALIDATED",
            row,
        )
        self.assertIn("CodeBuddy 2.141.0", row)
        self.assertIn("QWEN_0.22.3_HOOK_INCOMPATIBLE", row)
        self.assertIn("KIMI_0.39.1_HOOK_UNSAFE", row)
        self.assertIn("OPENCODE_1.18.25_LIFECYCLE_INCOMPATIBLE", row)
        self.assertIn("产品0差异", row)
        self.assertNotIn("LOCAL_CANDIDATE", row)
        self.assertIn("无 `HOLD`", row)

        roadmap = read("maintenance/specs/roadmap.md")
        todo = read("maintenance/docs/待办.md")
        evidence = read("maintenance/docs/evidence/README.md")
        self.assertIn("`SHORT-CURRENT-CLI-R1`", section(roadmap, "WAIT_NEW_COUNTEREXAMPLE"))
        self.assertNotIn("SHORT-CURRENT-CLI-R1", section(roadmap, "IN_PROGRESS"))
        self.assertIn("HK-004-CLI-REVALIDATION-R1", todo)
        self.assertIn("host-cli-revalidation-r1/result.md", evidence)

        coverage = read("maintenance/specs/coverage.md")
        for item_id, marker in (
            ("WR-014", "已随v1.6.15发布"),
            ("WR-019", "已随v1.6.15发布"),
            ("HK-008", "HK-008b已随v1.6.15发布"),
            ("MT-005", "b6b已随v1.6.15发布"),
        ):
            with self.subTest(item_id=item_id):
                self.assertIn(marker, table_row(coverage, item_id))

    def test_paid_placeholders_follow_the_canonical_local_candidate(self) -> None:
        coverage = read("maintenance/specs/coverage.md")
        todo = read("maintenance/docs/待办.md")
        roadmap = read("maintenance/specs/roadmap.md")

        self.assertIn("DONE_LOCAL_PAID_NO_RELEASE", table_row(coverage, "OT-001"))
        self.assertIn("DONE_CODEBUDDY_ONE_SAMPLE", table_row(coverage, "OT-001-composite"))
        self.assertIn("CLOSED_BY_EXISTING_PLANNER", table_row(coverage, "OT-002"))
        self.assertIn("PAID_PRODUCT_PASS_FONT_FALLBACK", table_row(coverage, "RF-001"))
        for item_id in ("OT-002", "OT-001-composite", "OT-001", "RF-001"):
            with self.subTest(item_id=item_id):
                self.assertRegex(todo, rf"(?m)^- \[x\] `{re.escape(item_id)}`")
        self.assertIn("`codex/paid-outline-review`", roadmap)
        self.assertNotRegex(roadmap, r"codex/paid-outline-review@[0-9a-f]{8,40}")
        self.assertIn("DONE_LOCAL_PAID_NO_RELEASE", roadmap)
        self.assertNotIn("尚未实现的是结构化组合 coordinator 及其真实 Stop 生命周期", roadmap)


if __name__ == "__main__":
    unittest.main()
