#!/usr/bin/env python3
"""Generate deterministic synthetic ablation evidence for the skill repository.

The script does not call an LLM. It creates compact baseline-vs-skill proxies
that exercise the lint checks and genre coverage used in release validation.
Human/agent review can then inspect the generated packet.
"""

from __future__ import annotations

import argparse
from pathlib import Path


GENRES = [
    "通知",
    "请示",
    "报告",
    "说明",
    "方案",
    "申请",
    "函",
    "复函",
    "批复",
    "意见",
    "决定",
    "公告",
    "公示",
    "通报",
    "会议纪要",
    "工作要点",
    "工作总结",
    "调研报告",
    "可研报告",
    "实施方案",
    "建设方案",
    "审查材料",
]

AI_COMPUTE = [
    "算力服务可研报告",
    "算力资源采购方案",
    "GPU/服务器租赁技术需求",
    "云端部署成本对比说明",
    "技术服务审查材料",
]

TASK_VARIANTS = [
    ("短文", "基础办理"),
    ("短文", "补充事项"),
    ("中篇", "专项推进"),
    ("中篇", "跨部门协同"),
    ("长文", "年度安排"),
    ("长文", "整改复核"),
    ("短文", "征求意见"),
    ("中篇", "结果通报"),
    ("长文", "验收归档"),
    ("中篇", "持续优化"),
]


BASELINE_FILLERS = [
    "本方案重点说明三个问题",
    "不是单一事项，而是系统工作",
    "不仅要提升效率，还要保障安全",
    "为了便于理解，以下直接列出",
    "租赁方式更稳，也更省",
]

GENRE_PATTERNS = {
    "通知": "现就报送范围、材料要求、完成时限和联系人等事项明确如下。",
    "请示": "拟申请启动相关工作，请予审查批复。",
    "报告": "现将阶段性进展、存在问题和下一步安排报告如下。",
    "说明": "有关进度偏慢原因、整改安排和责任落实情况说明如下。",
    "方案": "项目按照目标牵引、分步实施、责任到项的原则推进。",
    "申请": "申请事项、使用计划、资金或资源需求和真实性承诺应一并列明。",
    "函": "商请贵单位配合提供联调条件，并于规定时间反馈联系人和接口安排。",
    "复函": "来函收悉，经研究，现就有关事项函复如下。",
    "批复": "原则同意实施，并按批复范围、投资控制和管理要求组织推进。",
    "意见": "围绕目标要求、重点任务、管理措施和组织保障提出实施意见。",
    "决定": "经研究，决定成立专项工作机制，明确职责分工和运行规则。",
    "公告": "现将服务时间、办理方式、注意事项和咨询渠道公告如下。",
    "公示": "公示期内可通过指定渠道反映情况，并提供必要证明材料。",
    "通报": "现将检查情况、主要问题和整改要求予以通报。",
    "会议纪要": "会议明确了责任分工、完成时限和后续协调事项。",
    "工作要点": "年度工作围绕基础管理、重点项目、风险防控和能力提升展开。",
    "工作总结": "全年工作取得阶段性成效，同时仍需解决协同、数据和机制问题。",
    "调研报告": "调研显示，基层单位应用基础有所改善，但数据贯通和人员能力仍需加强。",
    "可研报告": "项目具备建设必要性和实施基础，费用测算、风险控制和收益安排较为清晰。",
    "实施方案": "实施工作分准备、部署、试运行、验收四个阶段推进。",
    "建设方案": "项目建设围绕需求来源、建设内容、成本安排、运行管理和建设成效展开。",
    "审查材料": "审查意见应区分已确认事项、需补充材料和后续整改要求。",
}

SCENARIO_PATTERNS = {
    "基础办理": "主办部门按既定流程组织办理，明确材料清单、反馈时限和联系人。",
    "补充事项": "对前期材料缺项和口径不一致的事项，由责任部门补齐依据并统一报送。",
    "专项推进": "专项工作实行节点管理，重要事项形成台账，完成情况纳入后续复核。",
    "跨部门协同": "涉及多部门配合的事项，由牵头部门统一协调接口、数据和反馈安排。",
    "年度安排": "年度任务按照季度分解、过程跟踪和结果验收推进，确保责任落实到岗到项。",
    "整改复核": "整改事项逐项明确责任人、完成时限和复核方式，逾期未完成的及时说明原因。",
    "征求意见": "征求意见事项明确反馈范围、反馈方式和采纳规则，逾期未反馈的按无意见处理。",
    "结果通报": "结果通报突出检查范围、主要情况、典型问题和整改要求，便于责任单位对照落实。",
    "验收归档": "验收归档阶段同步整理过程记录、成果文件和问题清单，作为后续复盘依据。",
    "持续优化": "后续优化围绕流程压缩、数据校准、责任协同和运行监测持续推进。",
}


def baseline_block(title: str, length: str, scenario: str, index: int) -> str:
    filler = BASELINE_FILLERS[index % len(BASELINE_FILLERS)]
    extra = (
        "一方面要强化统筹，另一方面要提升能力。"
        if length != "短文"
        else "要全面提升工作质效。"
    )
    if length == "长文":
        extra += "同时持续推进机制创新、流程再造和数字化赋能，打造可复制可推广经验。"
    return (
        f"### Baseline-{length}-{title}-{scenario}\n"
        f"{filler}。相关工作需要持续推进，全面赋能业务发展，满足未来发展需要。"
        f"各单位要高度重视，形成一批成果，并不断提升管理水平。{extra}\n"
    )


def skill_block(title: str, length: str, scenario: str) -> str:
    scenario_sentence = SCENARIO_PATTERNS[scenario]
    if "算力" in title or "GPU" in title or "云端" in title or "技术服务" in title:
        text = (
            f"### Skill-{length}-{title}-{scenario}\n"
            "项目需求主要来自长文处理、批量任务、多轮问答和知识库检索。"
            "年度调用量按业务系统、使用人数、任务频次和单次 Token 消耗测算，"
            "再换算为云端部署费用和租赁服务费用。租赁服务方式将服务器资源、"
            "模型部署、训推调度、网络带宽、运维响应、SLA 和安全审计纳入统一合同管理，"
            f"有利于稳定三年成本并明确交付验收责任。{scenario_sentence}\n"
        )
    else:
        genre_sentence = GENRE_PATTERNS.get(title, "办理事项应有事实依据、责任安排和时限要求。")
        text = (
            f"### Skill-{length}-{title}-{scenario}\n"
            f"{genre_sentence}"
            f"{scenario_sentence}"
            "涉及资金、数据、期限和附件的，同步明确来源、范围、提交方式和后续管理要求。\n"
        )
    if length == "长文":
        text += (
            "后续工作按照准备、实施、检查、整改四个环节推进。"
            "准备阶段完成资料核验和责任分工，实施阶段形成过程记录，"
            "检查阶段对照目标逐项复核，整改阶段明确时限和反馈要求。\n"
        )
    return text


def write_outputs(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    baseline = ["# Baseline Synthetic Outputs\n"]
    skilled = ["# Skill Synthetic Outputs\n"]
    for title in GENRES + AI_COMPUTE:
        for index, (length, scenario) in enumerate(TASK_VARIANTS):
            baseline.append(baseline_block(title, length, scenario, index))
            skilled.append(skill_block(title, length, scenario))
    (out_dir / "baseline.md").write_text("\n".join(baseline), encoding="utf-8")
    (out_dir / "skill.md").write_text("\n".join(skilled), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "# Expanded Ablation Artifacts\n\n"
        "Synthetic outputs for release validation. These files are generated and are not raw user documents.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="output/expanded-ablation")
    args = parser.parse_args()
    write_outputs(Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
