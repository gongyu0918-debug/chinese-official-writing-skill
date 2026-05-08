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


def baseline_block(title: str, length: str) -> str:
    repeat = 2 if length == "长文" else 1
    body = []
    for idx in range(repeat):
        filler = BASELINE_FILLERS[idx % len(BASELINE_FILLERS)]
        body.append(
            f"### Baseline-{length}-{title}-{idx + 1}\n"
            f"{filler}。相关工作需要持续推进，全面赋能业务发展，满足未来发展需要。"
            f"各单位要高度重视，形成一批成果，并不断提升管理水平。\n"
        )
    return "\n".join(body)


def skill_block(title: str, length: str) -> str:
    if "算力" in title or "GPU" in title or "云端" in title or "技术服务" in title:
        text = (
            f"### Skill-{length}-{title}\n"
            "项目需求主要来自长文处理、批量任务、多轮问答和知识库检索。"
            "年度调用量按业务系统、使用人数、任务频次和单次 Token 消耗测算，"
            "再换算为云端部署费用和租赁服务费用。租赁服务方式将服务器资源、"
            "模型部署、训推调度、网络带宽、运维响应、SLA 和安全审计纳入统一合同管理，"
            "有利于稳定三年成本并明确交付验收责任。\n"
        )
    else:
        genre_sentence = GENRE_PATTERNS.get(title, "正文应围绕办理事项、事实依据和责任要求展开。")
        text = (
            f"### Skill-{length}-{title}\n"
            f"{genre_sentence}"
            "为保障相关工作有序推进，拟由主办单位牵头组织实施。"
            "正文应围绕办理事项、事实依据、责任分工、时间安排和验收要求展开，"
            "确保事项清楚、责任明确、流程可执行。涉及资金、数据、期限和附件的，"
            "应列明来源、范围、提交方式和后续管理要求。\n"
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
        for length in ("短文", "长文"):
            baseline.append(baseline_block(title, length))
            skilled.append(skill_block(title, length))
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
