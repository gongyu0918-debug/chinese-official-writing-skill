#!/usr/bin/env python3
"""Promptfoo Python providers for official-writing ablation evals.

The provider has two modes:
- baseline: draft from the task only.
- skill: load the installed Skill entrypoint plus genre-specific references.

By default the provider uses deterministic local drafts so tests can run in
any agent without a model-specific CLI. Set OFFICIAL_WRITING_AGENT_COMMAND to
use the current agent or any model command; include {prompt} in the command
template or the prompt will be appended as the final argument.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import textwrap
import time
from typing import Any


GENRE_REFERENCES: dict[str, list[str]] = {
    "routing": [
        "references/genre-routing.md",
    ],
    "review": [
        "references/review-checklist.md",
    ],
    "review_direct": [
        "references/review-checklist.md",
    ],
    "genre_review": [
        "references/genre-checklist.md",
    ],
    "anti_ai": [
        "references/anti-ai-patterns.md",
    ],
    "body_delivery": [
        "references/writing-rules.md",
    ],
    "style": [
        "references/official-style.md",
    ],
    "argument": [
        "references/argument-chains.md",
    ],
    "unknown_genre": [
        "references/genre-routing.md",
        "references/genre-checklist.md",
    ],
    "minutes_playbook": [
        "references/genre-playbook-minutes.md",
    ],
    "report_playbook": [
        "references/genre-playbook-report.md",
    ],
    "correspondence_playbook": [
        "references/genre-playbook-correspondence.md",
    ],
    "work_summary_playbook": [
        "references/genre-playbook-work-summary.md",
    ],
    "work_priorities_playbook": [
        "references/genre-playbook-work-priorities.md",
    ],
    "field_editing": [
        "references/field-editing.md",
    ],
    "plan_construction_playbook": [
        "references/genre-playbook-plan-construction.md",
    ],
    "notice_playbook": [
        "references/genre-playbook-notice.md",
    ],
    "publication_playbook": [
        "references/genre-playbook-publication.md",
    ],
    "institution_playbook": [
        "references/genre-playbook-institution-rules.md",
    ],
    "speech_playbook": [
        "references/genre-playbook-speech-address.md",
    ],
    "meeting_host_playbook": [
        "references/genre-playbook-meeting-host.md",
    ],
    "duty_report_playbook": [
        "references/genre-playbook-duty-report.md",
    ],
    "speech_person_order": [
        "references/speech-person-order.md",
    ],
    "research_playbook": [
        "references/genre-playbook-research.md",
    ],
    "feasibility_playbook": [
        "references/genre-playbook-feasibility.md",
    ],
    "procurement_overlay": [
        "references/genre-playbook-procurement-review.md",
    ],
    "review_opinion_playbook": ["references/genre-playbook-review-opinion.md"],
    "technical_requirements_playbook": ["references/genre-playbook-technical-requirements.md"],
    "responsibility_letter_playbook": ["references/genre-playbook-responsibility-letter.md"],
    "initiative_playbook": ["references/genre-playbook-initiative.md"],
    "open_letter_playbook": ["references/genre-playbook-open-letter.md"],
    "narration_playbook": ["references/genre-playbook-narration.md"],
    "information_materials_playbook": ["references/genre-playbook-information-materials.md"],
    "procurement_announcement_playbook": [
        "references/genre-playbook-procurement-announcement.md",
    ],
    "decision_playbook": ["references/genre-playbook-decision.md"],
    "resolution_playbook": ["references/genre-playbook-resolution.md"],
    "motion_playbook": ["references/genre-playbook-motion.md"],
    "communique_playbook": ["references/genre-playbook-communique.md"],
    "order_playbook": ["references/genre-playbook-order.md"],
    "deployment_playbook": [
        "references/genre-playbook-deployment.md",
    ],
    "advisory_playbook": [
        "references/genre-playbook-advisory-feedback.md",
    ],
    "complaint_playbook": [
        "references/genre-playbook-complaint-reflection.md",
    ],
    "remediation_playbook": [
        "references/genre-playbook-remediation-plan.md",
    ],
    "project_application_playbook": [
        "references/genre-playbook-project-application.md",
    ],
    "reply_playbook": [
        "references/genre-playbook-reply.md",
    ],
    "opinion_playbook": [
        "references/genre-playbook-opinion.md",
    ],
    "explanation_playbook": [
        "references/genre-playbook-explanation.md",
    ],
    "remediation_report_overlay": [
        "references/transaction-remediation-report.md",
    ],
    "feedback_report_overlay": [
        "references/transaction-feedback-report.md",
    ],
    "request_review": [
        "references/genre-checklist-request.md",
    ],
    "request_playbook": [
        "references/genre-playbook-request.md",
    ],
    "feasibility_review": [
        "references/genre-checklist-feasibility-review.md",
    ],
    "ai_compute": [
        "references/ai-compute-docs.md",
    ],
    "complex": [
        "references/handling-elements.md",
        "references/argument-chains.md",
    ],
    "external_research": [
        "references/external-research.md",
    ],
    "format": [
        "references/format-gbt9704.md",
    ],
    "news_message": [
        "references/genre-playbook-news-message.md",
    ],
    "news_commentary": [
        "references/genre-playbook-news-commentary.md",
    ],
}

MAX_SKILL_CONTEXT_CHARS = 50_000
DEFAULT_TIMEOUT_SECONDS = 720

CHAIN_GENRES = {
    "请示",
    "报告",
    "通知",
    "函",
    "复函",
    "征求意见函",
    "采购公告",
    "公示",
    "批复",
    "会议纪要",
    "方案",
    "意见",
    "工作要点",
    "工作总结",
    "调研报告",
    "可研报告",
    "实施方案",
    "建设方案",
    "审查材料",
    "说明",
    "情况说明",
    "申请",
    "周报",
    "月报",
}

MEETING_HOST_PLAYBOOK_GENRES = {
    "会议主持词",
    "主持词",
    "主持串词",
}

DUTY_REPORT_PLAYBOOK_GENRES = {
    "书面述职",
    "述职报告",
    "履职情况报告",
    "现场述职发言",
}

PLAYBOOK_GENRES = (
    CHAIN_GENRES
    | MEETING_HOST_PLAYBOOK_GENRES
    | DUTY_REPORT_PLAYBOOK_GENRES
    | {
        "通告",
        "公告",
        "通报",
        "决定",
        "决议",
        "议案",
        "公报",
        "命令",
        "命令（令）",
        "讲话稿",
        "致辞",
        "研究报告",
        "制度",
        "规定",
        "办法",
        "细则",
        "操作规程",
        "采购审查",
        "评审材料",
        "采购方案",
    }
)

NEWS_MESSAGE_GENRES = {
    "新闻稿",
    "新闻消息",
    "快讯",
    "活动报道",
    "活动新闻稿",
    "新闻通稿",
}

NEWS_COMMENTARY_GENRES = {
    "新闻评论",
    "时评",
    "评论员文章",
}

PERIODIC_REPORT_GENRES = {
    "周报",
    "月报",
}

REPORT_PLAYBOOK_GENRES = PERIODIC_REPORT_GENRES | {
    "报告",
    "情况报告",
    "情况说明",
    "情况综合",
    "整改报告",
    "整改进展报告",
    "整改情况报告",
    "整改工作报告",
    "反馈报告",
    "反馈情况报告",
    "意见反馈报告",
}

ORDINARY_LETTER_PLAYBOOK_GENRES = {
    "函",
}

WORK_SUMMARY_PLAYBOOK_GENRES = {
    "工作总结",
}

WORK_PRIORITIES_PLAYBOOK_GENRES = {"工作要点"}

PERIODIC_REPORT_FIELD_MARKERS = (
    "字段式",
    "按字段",
    "字段名",
    "字段顺序",
    "字段换行",
)

NOTICE_PLAYBOOK_GENRES = {"通知"}
PUBLICATION_PLAYBOOK_GENRES = {"公告", "公示", "通告", "通报"}
PROCUREMENT_ANNOUNCEMENT_GENRES = {"采购公告"}

INSTITUTION_PLAYBOOK_MARKERS = (
    "制度",
    "规定",
    "办法",
    "细则",
    "操作规程",
)

SPEECH_PLAYBOOK_GENRES = {
    "讲话稿",
    "讲话",
    "致辞",
    "演讲",
}
SPEECH_PERSON_ORDER_MARKERS = (
    "人物排序",
    "职务排序",
    "开场顺序",
    "称谓排序",
    "按职务",
)

RESEARCH_PLAYBOOK_GENRES = {"调研报告", "研究报告"}
FEASIBILITY_PLAYBOOK_GENRES = {"可研报告"}

PURPOSE_PLAYBOOK_GENRES = {
    "采购审查": "review_opinion_playbook",
    "采购审查意见": "review_opinion_playbook",
    "审查意见": "review_opinion_playbook",
    "评审意见": "review_opinion_playbook",
    "审查材料": "review_opinion_playbook",
    "评审材料": "review_opinion_playbook",
    "技术需求": "technical_requirements_playbook",
    "技术需求书": "technical_requirements_playbook",
    "软件需求说明": "technical_requirements_playbook",
    "接口需求": "technical_requirements_playbook",
    "技术需求附件": "technical_requirements_playbook",
    "责任书": "responsibility_letter_playbook",
    "倡议书": "initiative_playbook",
    "公开信": "open_letter_playbook",
    "讲解稿": "narration_playbook",
    "解说词": "narration_playbook",
    "宣传手册": "information_materials_playbook",
    "宣传材料": "information_materials_playbook",
}

DELIBERATION_PLAYBOOK_GENRES = {
    "决定",
    "决议",
    "议案",
    "公报",
    "命令",
    "命令（令）",
}
DEPLOYMENT_PLAYBOOK_GENRES = {"部署", "部署安排"}
ADVISORY_GENRES = {"意见建议", "建议反馈", "优化建议", "合作性意见建议", "建议信"}
COMPLAINT_GENRES = {"投诉", "问题反映", "情况反映"}
REMEDIATION_GENRES = {"整改方案", "专项整改方案", "整改工作方案"}
PROJECT_APPLICATION_GENRES = {"项目申请", "增项申请", "项目增项申请"}
REPLY_GENRES = {"批复"}
OPINION_GENRES = {"意见"}
EXPLANATION_GENRES = {"说明"}
REMEDIATION_REPORT_MARKERS = (
    "整改报告",
    "整改进展报告",
    "整改情况报告",
    "整改工作报告",
    "专项整改进展",
)
FEEDBACK_REPORT_MARKERS = (
    "反馈报告",
    "反馈情况报告",
    "意见反馈报告",
    "办理反馈报告",
)

PLAN_CONSTRUCTION_GENRE_MARKER = "方案"

REQUEST_REVIEW_GENRES = {
    "请示",
    "申请",
    "采购申请",
    "采购申购",
    "采购请示",
}

ROUTED_PRIMARY_GENRES = (
    REPORT_PLAYBOOK_GENRES
    | REQUEST_REVIEW_GENRES
    | ORDINARY_LETTER_PLAYBOOK_GENRES
    | WORK_SUMMARY_PLAYBOOK_GENRES
    | WORK_PRIORITIES_PLAYBOOK_GENRES
    | NOTICE_PLAYBOOK_GENRES
    | SPEECH_PLAYBOOK_GENRES
    | MEETING_HOST_PLAYBOOK_GENRES
    | DUTY_REPORT_PLAYBOOK_GENRES
    | RESEARCH_PLAYBOOK_GENRES
    | PURPOSE_PLAYBOOK_GENRES.keys()
)

REQUEST_PROCUREMENT_MARKERS = (
    "采购",
    "购置",
    "购买",
    "申购",
)
REQUEST_PROCUREMENT_COMPLEXITY_RE = re.compile(
    r"(?:多(?:个)?品类|不同品类|多项(?:物资|设备|采购)?|"
    r"不同规格|规格(?:不同|不一|各异)|不同价格|价格(?:不同|不一|各异)|"
    r"分项(?:核算|列示|报价|计价)|逐项核算|报价(?:单|文件|清单)?|询价|比价|"
    r"验收(?:标准|要求|指标|方案|条款)?|技术(?:附件|参数附件|需求附件|规格书))"
)
REQUEST_PROCUREMENT_NEGATED_CLAUSE_RE = re.compile(
    r"(?:材料未给|材料未提供|未给|未提供|未涉及|不涉及|不含|无需|无须|不需要|"
    r"不要求|没有|并非|不是|不采用)"
    r"[^。；;\n]*?(?=(?:，?(?:但|不过|然而|可是|而是|却|仍需|仍要|同时|另需|"
    r"仅需|只需|本次|只(?:申请|采购|购置|购买|申购)))|[。；;\n]|$)"
)

FEASIBILITY_REVIEW_GENRES = {
    "可研报告",
}

COMPLEX_TASK_MARKERS = (
    "完整文种骨架",
    "完整结构",
    "复杂改稿",
    "多材料",
    "多附件",
    "合稿",
    "长文",
)
FORMAT_TASK_MARKERS = ("Word", "word", "DOCX", "docx", "GB/T 9704", "红头", "版记")
LONG_FORM_RE = re.compile(r"(?<!\d)(\d{3,5})\s*字")

AI_COMPUTE_MARKERS = (
    "算力",
    "GPU",
    "模型服务",
    "智算中心",
    "AI平台",
    "AI 平台",
    "大模型",
    "Token",
    "模型推理",
    "推理服务",
    "模型训练",
    "训练服务",
)

AI_COMPUTE_EXACT_GENRES = {
    "算力服务可研报告",
    "算力资源采购方案",
    "GPU/服务器租赁技术需求",
}

AI_ORDINARY_GENRE_MARKERS = (
    "请示",
    "申请",
    "采购",
    "可研",
    "可行性研究",
    "报告",
    "说明",
    "审查",
    "公告",
    "通知",
    "函",
    "建设方案",
    "实施方案",
    "方案",
)
AI_ORDINARY_TASK_RE = re.compile(
    r"(?:起草|撰写|形成|编制|写)(?:一份)?[^。；;\n]{0,32}?"
    r"(?:请示|申请|采购公告|采购方案|可研报告|可行性研究报告|情况报告|报告|说明|审查材料|公告|通知|函|建设方案|实施方案|保障方案|方案)"
)

AI_NEGATION_MARKERS = (
    "不涉及AI",
    "不涉及 AI",
    "非AI",
    "非 AI",
    "与AI无关",
    "与 AI 无关",
    "不用于AI",
    "不用于 AI",
)

MINUTES_FULL_REQUEST_MARKERS = (
    "完整会议纪要",
    "完整的会议纪要",
    "完整正式会议纪要",
    "完整的正式会议纪要",
    "正式完整会议纪要",
)
MINUTES_UNRESOLVED_MARKERS = (
    "下次再议",
    "未决",
    "待定",
    "待议",
    "只记录建议",
    "仅记录建议",
    "不写会议决定",
    "不要写会议决定",
)
MINUTES_UNRESOLVED_RE = re.compile(
    r"(?:未|尚未|没有)(?:形成|作出|作|明确|确定|达成)[^，。；;\n]{0,10}?"
    r"(?:决定|决议|议定事项|结论|一致意见|共识|责任单位|责任部门|责任人|责任分工|完成期限|办理期限|期限|时限)"
    r"|(?:决定|决议|议定事项|结论|一致意见|共识|责任单位|责任部门|责任人|责任分工|完成期限|办理期限|期限|时限)"
    r"[^，。；;\n]{0,12}?(?:未|尚未|没有)(?:形成|作出|作|明确|确定|达成)"
    r"|(?:尚无|无)(?:决定|决议|议定事项|结论|一致意见|共识|责任单位|责任部门|责任人|责任分工|完成期限|办理期限|期限|时限)"
    r"|(?:仍待|尚待|待)[^，。；;\n]{0,10}?(?:评估|研究|确认|明确|议定|决定)"
    r"|(?:材料只有|只有|仅有)[^，。；;\n]{0,12}?(?:建议|讨论|汇报|听取结果)"
    r"|(?:只|仅)(?:记录|保留)[^，。；;\n]{0,12}?(?:建议|讨论|汇报|听取结果)"
    r"|(?:下次|后续|再次)[^，。；;\n]{0,6}?(?:再议|评估|研究|确认)"
    r"|(?:拟|建议)[^，。；;\n]{0,16}?(?:采购|试点|测试|评估|研究|再议|观察|安排|实施)"
    r"|(?:只|仅)?(?:听取|汇报)[^，。；;\n]{0,12}?(?:结果|情况)"
)
MINUTES_FULL_REQUEST_RE = re.compile(
    r"(?:完整[、，,\s]*(?:且|并)?正式|正式[、，,\s]*(?:且|并)?完整)(?:的)?会议纪要"
)
MINUTES_NEGATED_FULL_REQUEST_RE = re.compile(
    r"(?:不需要|不要求|不是|不要|不用|无需|不必|不按)"
    r"\s*(?:按|写|起草|一份)?\s*"
    r"(?:完整(?:的)?会议纪要|完整正式(?:的)?会议纪要|完整(?:的)?正式会议纪要|正式完整(?:的)?会议纪要)"
)
MINUTES_RESOLVED_RE = re.compile(
    r"(?:会议)?(?:已|已经|现已)(?:作出|形成|通过|议定|明确|确定|达成)"
    r"(?:了)?(?:如下|[一二三四五六七八九十\d]+项)?[^，。；;\n]{0,16}"
    r"(?:决定|决议|议定事项|结论|一致意见|共识|责任(?:单位|部门|人|分工)?|完成期限|办理期限|期限|时限|截止时间|安排|负责|牵头)"
    r"|会议(?:作出|形成|通过|议定|达成)(?:了)?"
    r"(?:如下|[一二三四五六七八九十\d]+项)?[^，。；;\n]{0,16}"
    r"(?:决定|决议|议定事项|结论|一致意见|共识|事项|方案|议案|申请|责任(?:单位|部门|人|分工)?|完成期限|办理期限|期限|时限|截止时间|安排)"
    r"|(?:会议)?(?:已|已经|现已)(?:决定|议定)(?:了|如下|：|:|，)?"
    r"|会议(?:决定|议定)(?:了|如下|：|:|，)?"
    r"|(?:会议)?(?:无异议|一致|审议)(?:通过|同意)"
    r"|(?:责任单位|责任部门|责任人|责任分工|完成期限|办理期限|期限|时限|截止时间)"
    r"\s*(?:(?:已|已经|现已)?(?:明确|确定)|为|是|如下|：|:)"
    r"|会议(?:已|已经|现已)?(?:明确|确定)[^，。；;\n]{0,16}"
    r"(?:责任单位|责任部门|责任人|责任分工|完成期限|办理期限|期限|时限|截止时间)"
    r"|(?:作出|形成|通过|议定|明确|确定|达成)(?:了)?"
    r"[^，。；;\n]{0,16}"
    r"(?:决定|决议|议定事项|结论|一致意见|共识|责任单位|责任部门|责任人|责任分工|完成期限|办理期限|期限|时限|截止时间)"
    r"|(?:明确|确定)(?:由)?[^，。；;\n]{0,16}(?:负责|牵头)"
    r"|(?:决定|议定)(?:由|将|先|如下|：|:)[^，。；;\n]{0,20}"
)
REVIEW_TASK_MARKERS = (
    "只审",
    "审一下",
    "只检查",
    "检查这段",
    "检查这份",
    "格式核验",
    "语气检查",
    "复核这段",
    "复核这份",
    "审核一下",
    "审核这份",
    "审核稿件",
    "审校一下",
    "审校这份",
    "审校稿件",
    "复核一下",
    "复核稿件",
    "检查一下",
    "检查稿件",
    "帮我审核",
    "帮我复核",
    "帮我审校",
    "帮我看看这份",
    "把关这份",
    "把关稿件",
    "看看有没有问题",
    "审阅这份",
)
REVIEW_REWRITE_MARKERS = (
    "再按建议重写",
    "再重写",
    "然后重写",
    "并重写",
    "同时重写",
    "审后重写",
    "输出改后稿",
    "修改并输出",
    "改写成",
    "修改全文",
    "修改正文",
    "直接改",
    "代改",
    "输出修改稿",
    "输出改稿",
    "给出改后稿",
)
REVIEW_REWRITE_ACTION_RE = re.compile(
    r"(?:"
    r"改写(?:成|为|全文|正文|一版)|"
    r"重写(?:全文|正文|一版)|"
    r"改一版|改成|改好|修改全文|修改正文|代改|"
    r"(?:请|并|再|然后|同时|直接|帮我|代为|给我|后帮我)[^，。；;\n]{0,6}(?:重写|改写)"
    r")"
)
REVIEW_REWRITE_NEGATIONS = (
    "不重写",
    "不要重写",
    "不改写",
    "不要改写",
    "不修改",
    "不要修改",
    "不代改",
    "不要代改",
    "不输出修改稿",
    "不要输出修改稿",
    "不输出改后稿",
    "不要输出改后稿",
    "只给修改建议",
    "仅给修改建议",
    "修改建议",
)
LOCAL_REVISION_SCOPE_MARKERS = (
    "只改",
    "仅改",
    "只修改",
    "仅修改",
    "只调整",
    "仅调整",
    "只更正",
    "仅更正",
    "只替换",
    "仅替换",
    "其余不变",
    "其他不变",
    "其余内容不变",
    "其他内容不变",
)
LOCAL_REVISION_TARGET_MARKERS = (
    "错别字",
    "标点",
    "格式",
    "日期",
    "数字",
    "称谓",
    "落款",
    "标题",
    "一处",
    "一句",
    "局部措辞",
)
SUBSTANTIVE_ORDINARY_LETTER_TARGET_MARKERS = (
    "事务动作",
    "办理动作",
    "事项",
    "状态",
    "条件",
    "范围",
    "结构",
    "职责",
    "责任",
    "时限",
)
ORDINARY_LETTER_DRAFT_SOURCE_RE = re.compile(
    r"(?:以下|下面|下列)[^。；;\n]{0,8}?(?:事实|材料|情况|要点|信息|内容)"
    r"|根据[^。；;\n]{0,16}?(?:事实|材料|情况|要点|信息|内容)"
)
ORDINARY_LETTER_DRAFT_OUTPUT_RE = re.compile(
    r"(?:起草|拟写|撰写)[^。；;\n]{0,20}?(?:新的?)?(?:一份)?(?:正式)?函(?:件)?"
    r"|(?:整理|完善|修改)(?:成|为)[^。；;\n]{0,12}?(?:一份)?(?:新的?)?(?:正式)?函(?:件)?"
)
ORDINARY_LETTER_NEW_DRAFT_RE = re.compile(
    r"参考[^。；;\n]{0,20}?函[^。；;\n]{0,8}?格式"
    r"[^。；;\n]{0,28}?(?:起草|拟写|撰写|形成|整理)"
    r"[^。；;\n]{0,12}?(?:新的?)?(?:一份)?函(?:件)?"
)
ORDINARY_LETTER_UNCHANGED_CLAUSE_RE = re.compile(
    r"(?:不|不要|无需)(?:调整|修改|重组|重排|变更)[^，。；;\n]{0,24}"
    r"|[^，。；;\n]{0,24}(?:不用改|无需改动|不作调整|(?:均)?保持不变|维持不变|保持原样)"
)
EXISTING_ORDINARY_LETTER_RE = re.compile(
    r"(?:这份|这封|该份|该|下列|以下|下面(?:这份)?)"
    r"(?!(?:事实|材料|情况|要点|信息|内容))"
    r"[^。；;\n]{0,12}?(?:函|函件|函稿)"
    r"|(?:原函|原稿|底稿|函稿|既有普通函|现有普通函)"
    r"|(?:修改|改写|重写|调整|重组|重排)正文"
)
ORDINARY_LETTER_REVISION_ACTION_MARKERS = (
    "修改",
    "改写",
    "重写",
    "整理",
    "完善",
    "调整",
    "重组",
    "重排",
)
ORDINARY_LETTER_STRUCTURAL_REVISION_RE = re.compile(
    r"(?:重新组织|梳理|整体优化|优化)"
    r"[^。；;\n]{0,28}?(?:段落|逻辑|层次|顺序)"
)
ORDINARY_LETTER_REVISION_NEGATIONS = (
    "不调整",
    "不要调整",
    "无需调整",
    "不重组",
    "不要重组",
    "无需重组",
    "不重排",
    "不要重排",
    "无需重排",
    "不整理",
    "不要整理",
    "无需整理",
    "不完善",
    "不要完善",
    "无需完善",
)
ANTI_AI_TASK_MARKERS = ("AI 味", "AI味", "降 AI 味", "降AI味", "模板化", "空话套话")
BODY_ONLY_TASK_MARKERS = (
    "只输出正文",
    "只输出完整正文",
    "给我正文",
    "直接给正文",
    "仅给正文",
    "只看正文",
    "直接交付正文",
    "只输出改后全文",
    "只交正文",
    "直接交付正文",
)
BODY_DELIVERY_MARKERS = (
    "只输出正文",
    "只输出完整正文",
    "只要文章",
    "只要稿件",
    "只要正文",
    "不需要解释",
    "不需要提示",
    "不要解释",
    "不要提示",
    "不需要文后提示",
    "只看稿件",
    "只交稿件",
)
COMPREHENSIVE_REVIEW_MARKERS = (
    "格式",
    "语气",
    "通篇",
    "全面审稿",
    "全面复核",
    "全面检查",
    "综合审稿",
    "综合复核",
    "综合检查",
    "段落、小节",
    "段落、小节、全文",
    "段落、小节和全文",
    "全文审稿",
    "全文复核",
    "全文检查",
    "全面审核",
    "全面审校",
    "全面把关",
)
DIRECT_REVIEW_SCOPE_MARKERS = (
    "事实",
    "状态",
    "保真",
    "主体",
    "对象",
    "事项",
    "金额",
    "数量",
    "单位",
    "日期",
    "时限",
    "渠道",
    "落款",
    "结尾",
    "文种功能",
    "请批",
    "办理要素",
    "数据",
    "估算依据",
    "步骤",
    "责任分工",
    "标题",
    "导语",
    "体裁",
    "观点",
    "判断强度",
    "承诺强度",
)
STYLE_TASK_MARKERS = ("去口语化", "降 AI 味", "降AI味", "润色", "正式一点", "统一语气", "顺稿")
ROUTING_TASK_MARKERS = ("文种不清", "判断文种", "选择文种", "请示还是报告", "函还是通知")
ARGUMENT_TASK_MARKERS = ("论证", "可行性", "必要性", "方案比较", "成本比较")
EXTERNAL_RESEARCH_TASK_MARKERS = (
    "搜索",
    "联网搜索",
    "联网核验",
    "搜索公开来源",
    "核验公开来源",
    "最新",
    "当前政策",
    "当前规定",
    "今日",
    "现行政策",
    "近期数据",
    "最新政策",
    "最新数据",
    "今日数据",
)

_BATCH_CACHE: dict[str, dict[str, str]] = {}


class ProviderError(RuntimeError):
    pass


def _options_config(options: dict[str, Any]) -> dict[str, Any]:
    config = options.get("config") or {}
    if not isinstance(config, dict):
        return {}
    return config


def _base_path(config: dict[str, Any]) -> Path:
    base_path = config.get("basePath")
    if base_path:
        return Path(str(base_path)).resolve()
    return Path(__file__).resolve().parents[1]


def _repo_root(config: dict[str, Any]) -> Path:
    configured = config.get("repoRoot")
    if configured:
        return (_base_path(config) / str(configured)).resolve()
    return _base_path(config).parents[1]


def _dataset_path(config: dict[str, Any]) -> Path:
    configured = config.get("datasetPath", "datasets/cases.jsonl")
    return (_base_path(config) / str(configured)).resolve()


def _cache_dir(config: dict[str, Any]) -> Path:
    repo_root = _repo_root(config)
    return repo_root / "output" / "promptfoo" / "cache"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _load_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for line in _dataset_path(config).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        vars_ = item.get("vars") or {}
        metadata = item.get("metadata") or {}
        case = {
            "description": item.get("description", vars_.get("case_id", "")),
            "vars": vars_,
            "metadata": metadata,
        }
        cases.append(case)

    limit_text = os.environ.get("OFFICIAL_WRITING_EVAL_LIMIT", "").strip()
    if limit_text:
        try:
            limit = int(limit_text)
        except ValueError as exc:
            raise ProviderError(f"OFFICIAL_WRITING_EVAL_LIMIT must be an integer: {limit_text}") from exc
        cases = cases[:limit]
    return cases


def _current_case(context: dict[str, Any]) -> dict[str, Any]:
    vars_ = context.get("vars") or {}
    test = context.get("test") or {}
    return {
        "description": test.get("description", vars_.get("case_id", "")),
        "vars": vars_,
        "metadata": test.get("metadata") or {},
    }


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _is_ai_compute(genre: str, tasks: list[str] | None = None) -> bool:
    if genre in AI_COMPUTE_EXACT_GENRES:
        return True
    text = "\n".join([genre, *(tasks or [])])
    original_folded = text.casefold()
    negative_clause = re.compile(
        r"(?:不涉及|不用于)[^。；;\n]*?(?=(?:，?(?:但|不过|然而|可是|而是|却|仍需|同时|另需|仅涉及))|[。；;\n]|$)",
        re.I,
    )
    text = negative_clause.sub("", text)
    text = re.sub(r"非\s*AI[^，。；;\n]*", "", text, flags=re.I)
    for marker in AI_NEGATION_MARKERS:
        text = text.replace(marker, "")
    folded = text.casefold()
    if any(marker.casefold() in folded for marker in AI_COMPUTE_MARKERS):
        return True
    if any(marker.casefold() in original_folded for marker in AI_NEGATION_MARKERS):
        return False
    return all(marker in text for marker in ("云端", "本地", "部署"))


def _ai_requires_ordinary_playbook(genres: list[str], tasks: list[str]) -> bool:
    if genres and all(genre in AI_COMPUTE_EXACT_GENRES for genre in genres):
        return False
    if any(genre in PLAYBOOK_GENRES and genre != "会议纪要" for genre in genres):
        return True
    if any(_contains_marker(genre, AI_ORDINARY_GENRE_MARKERS) for genre in genres):
        return True
    return any(AI_ORDINARY_TASK_RE.search(task) for task in tasks)


def _skill_root(repo_root: Path) -> Path:
    installed = repo_root / "packages" / "agent-skills" / "skills" / "chinese-official-writing"
    if installed.exists():
        return installed
    return repo_root / "chinese-official-writing"


def _task_requires_complex_route(tasks: list[str]) -> bool:
    if any(marker in task for task in tasks for marker in COMPLEX_TASK_MARKERS):
        return True
    return any(int(match.group(1)) >= 800 for task in tasks for match in LONG_FORM_RE.finditer(task))


def _request_procurement_requires_complex_route(genres: list[str], tasks: list[str]) -> bool:
    if not any(genre in REQUEST_REVIEW_GENRES for genre in genres):
        return False
    text = "\n".join(tasks)
    normalized = REQUEST_PROCUREMENT_NEGATED_CLAUSE_RE.sub("", text)
    normalized = re.sub(
        r"非\s*(?:多品类|多项采购|分项核算|比价|报价|验收|技术附件)[^，。；;\n]*",
        "",
        normalized,
    )
    return _contains_marker(normalized, REQUEST_PROCUREMENT_MARKERS) and bool(
        REQUEST_PROCUREMENT_COMPLEXITY_RE.search(normalized)
    )


def _task_requires_external_research(tasks: list[str]) -> bool:
    return any(_contains_marker(task, EXTERNAL_RESEARCH_TASK_MARKERS) for task in tasks)


def _task_requests_rewrite(task: str) -> bool:
    normalized = task
    for marker in REVIEW_REWRITE_NEGATIONS:
        normalized = normalized.replace(marker, "")
    return (
        _contains_marker(normalized, REVIEW_REWRITE_MARKERS)
        or bool(REVIEW_REWRITE_ACTION_RE.search(normalized))
    )


def _task_is_explicit_local_revision(task: str) -> bool:
    instruction = ORDINARY_LETTER_UNCHANGED_CLAUSE_RE.sub(
        "",
        task.split("\n\n", 1)[0],
    )
    has_local_target = _contains_marker(instruction, LOCAL_REVISION_TARGET_MARKERS)
    has_substantive_target = _contains_marker(
        instruction,
        SUBSTANTIVE_ORDINARY_LETTER_TARGET_MARKERS,
    )
    return (
        has_local_target
        and _contains_marker(instruction, LOCAL_REVISION_SCOPE_MARKERS)
        and not has_substantive_target
    )


def _task_is_ordinary_letter_drafting(task: str) -> bool:
    instruction = task.split("\n\n", 1)[0]
    if ORDINARY_LETTER_NEW_DRAFT_RE.search(instruction):
        return True
    if (
        ORDINARY_LETTER_DRAFT_OUTPUT_RE.search(instruction)
        and not EXISTING_ORDINARY_LETTER_RE.search(instruction)
    ):
        return True
    return bool(
        ORDINARY_LETTER_DRAFT_SOURCE_RE.search(instruction)
        and ORDINARY_LETTER_DRAFT_OUTPUT_RE.search(instruction)
    )


def _ordinary_letter_requires_full_playbook(tasks: list[str]) -> bool:
    for task in tasks:
        normalized = ORDINARY_LETTER_UNCHANGED_CLAUSE_RE.sub("", task)
        for marker in (*REVIEW_REWRITE_NEGATIONS, *ORDINARY_LETTER_REVISION_NEGATIONS):
            normalized = normalized.replace(marker, "")
        if _task_is_ordinary_letter_drafting(normalized):
            continue
        instruction = normalized.split("\n\n", 1)[0]
        if (
            EXISTING_ORDINARY_LETTER_RE.search(instruction)
            and ORDINARY_LETTER_STRUCTURAL_REVISION_RE.search(instruction)
        ):
            return True
        has_revision_action = _contains_marker(
            instruction,
            ORDINARY_LETTER_REVISION_ACTION_MARKERS,
        )
        if has_revision_action and _contains_marker(
            instruction,
            SUBSTANTIVE_ORDINARY_LETTER_TARGET_MARKERS,
        ):
            return True
        if (
            EXISTING_ORDINARY_LETTER_RE.search(normalized)
            and has_revision_action
            and not _task_is_explicit_local_revision(task)
        ):
            return True
    return False


def _is_plan_construction_genre(genre: str) -> bool:
    return PLAN_CONSTRUCTION_GENRE_MARKER in genre


def _ai_task_requests_plan_construction(tasks: list[str]) -> bool:
    for task in tasks:
        match = AI_ORDINARY_TASK_RE.search(task)
        if match is not None and PLAN_CONSTRUCTION_GENRE_MARKER in match.group(0):
            return True
    return False


def _tasks_are_review_only(tasks: list[str]) -> bool:
    return bool(tasks) and all(
        (
            _contains_marker(task, REVIEW_TASK_MARKERS)
            or re.search(r"(?:审核|审校|复核|审阅|把关)(?:一下|这份|一份)?[^。；;\n]{0,12}(?:方案|技术需求|需求书|审查意见|评审意见)", task)
        )
        and (
            not _task_requests_rewrite(task)
            or any(
                marker in task
                for marker in (
                    "不要直接改全文",
                    "不直接改全文",
                    "不要改全文",
                    "不改全文",
                    "只给建议",
                    "只指出问题",
                    "指出问题和修改建议",
                )
            )
        )
        for task in tasks
    )


def _tasks_require_comprehensive_review(tasks: list[str]) -> bool:
    return any(
        _contains_marker(task, COMPREHENSIVE_REVIEW_MARKERS)
        or _contains_marker(task, ANTI_AI_TASK_MARKERS)
        for task in tasks
    )


def _tasks_name_direct_review_scope(tasks: list[str]) -> bool:
    return bool(tasks) and all(
        _contains_marker(task, DIRECT_REVIEW_SCOPE_MARKERS) for task in tasks
    )


def _minutes_require_playbook(tasks: list[str]) -> bool:
    minutes_text = "\n".join(tasks)
    full_request_text = MINUTES_NEGATED_FULL_REQUEST_RE.sub("", minutes_text)
    if _contains_marker(full_request_text, MINUTES_FULL_REQUEST_MARKERS) or MINUTES_FULL_REQUEST_RE.search(
        full_request_text
    ):
        return True

    resolved_text = minutes_text
    for marker in MINUTES_UNRESOLVED_MARKERS:
        resolved_text = resolved_text.replace(marker, "")
    resolved_text = MINUTES_UNRESOLVED_RE.sub("", resolved_text)
    return bool(MINUTES_RESOLVED_RE.search(resolved_text))


def _minutes_are_explicitly_unresolved(task: str) -> bool:
    return _contains_marker(task, MINUTES_UNRESOLVED_MARKERS) or bool(
        MINUTES_UNRESOLVED_RE.search(task)
    )


def _deliberation_primary_paths(genres: list[str]) -> list[str]:
    names = {"决定": "decision", "决议": "resolution", "议案": "motion", "公报": "communique", "命令": "order", "命令（令）": "order", "令": "order"}
    return list(dict.fromkeys(path for genre in genres if genre in names for path in GENRE_REFERENCES[names[genre] + "_playbook"]))


def _genres_for_delivery_purpose(genres: list[str], tasks: list[str]) -> list[str]:
    """Normalize ambiguous fixture labels by the requested deliverable."""
    joined = "\n".join(tasks)
    result = []
    for genre in genres:
        if genre in {"采购审查", "审查材料", "评审材料", "采购材料", "采购方案"}:
            if re.search(r"(?:起草|撰写|形成|整理|编制)[^。；;\n]{0,24}(?:审查意见|评审意见)", joined):
                genre = "采购审查意见" if "采购" in genre or "采购" in joined else "审查意见"
            elif re.search(r"(?:审核|审校|复核|审阅|把关|修改|改写)[^。；;\n]{0,12}采购方案", joined):
                genre = "采购方案"
        if genre not in AI_COMPUTE_EXACT_GENRES and "技术需求" in genre:
            genre = "技术需求"
        if genre == "情况说明" and re.search(r"解释[^。；;\n]{0,12}(?:事实|原因)|回应[^。；;\n]{0,12}疑问", joined):
            genre = "说明"
        result.append(genre)
    return list(dict.fromkeys(result))


def _purpose_primary_paths(genres: list[str]) -> list[str]:
    return list(dict.fromkeys(
        path for genre in genres if genre in PURPOSE_PLAYBOOK_GENRES
        for path in GENRE_REFERENCES[PURPOSE_PLAYBOOK_GENRES[genre]]
    ))


def _procurement_overlay_paths(genres: list[str], tasks: list[str]) -> list[str]:
    joined = "\n".join(genres + tasks)
    if any(genre in {"采购审查", "采购审查意见"} for genre in genres):
        return GENRE_REFERENCES["procurement_overlay"]
    if "采购" in joined and re.search(r"核对[^。；;\n]{0,20}(?:规格|报价|响应规则|履约条件|采购需求)", joined):
        return GENRE_REFERENCES["procurement_overlay"]
    return []


def _compute_primary_paths(genres: list[str], tasks: list[str]) -> list[str]:
    named = " ".join(genres)
    if "技术需求" in named:
        return GENRE_REFERENCES["technical_requirements_playbook"]
    if "可研" in named or "可行性" in named:
        return GENRE_REFERENCES["feasibility_playbook"]
    if "报告" in named:
        return GENRE_REFERENCES["report_playbook"]
    if "采购" in named or "租赁" in named:
        return GENRE_REFERENCES["plan_construction_playbook"]
    if "方案" in named:
        return GENRE_REFERENCES["plan_construction_playbook"]
    return GENRE_REFERENCES["unknown_genre"]


def _primary_reference_paths(genres: list[str], tasks: list[str]) -> list[str]:
    """Return the smallest primary-genre set for drafting or review."""
    if any(genre in NEWS_COMMENTARY_GENRES for genre in genres):
        return GENRE_REFERENCES["news_commentary"]
    if any(genre in NEWS_MESSAGE_GENRES for genre in genres):
        return GENRE_REFERENCES["news_message"]
    if genres and all(genre in AI_COMPUTE_EXACT_GENRES for genre in genres):
        return _compute_primary_paths(genres, tasks)
    if any("通报" in genre for genre in genres):
        return ["references/genre-playbook-bulletin.md"]
    paths: list[str] = []
    if "会议纪要" in genres:
        paths.extend(GENRE_REFERENCES["minutes_playbook"])
    if any(genre in REPORT_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["report_playbook"])
    if any(genre in REQUEST_REVIEW_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["request_playbook"])
    if any(genre in ORDINARY_LETTER_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["correspondence_playbook"])
    if any(genre in WORK_SUMMARY_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["work_summary_playbook"])
    if any(genre in WORK_PRIORITIES_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["work_priorities_playbook"])
    if any(_is_plan_construction_genre(genre) for genre in genres):
        paths.extend(GENRE_REFERENCES["plan_construction_playbook"])
    if any(genre in NOTICE_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["notice_playbook"])
    if any(genre in PUBLICATION_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["publication_playbook"])
    if any(genre in PROCUREMENT_ANNOUNCEMENT_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["procurement_announcement_playbook"])
    if any(any(marker in genre for marker in INSTITUTION_PLAYBOOK_MARKERS) for genre in genres):
        paths.extend(GENRE_REFERENCES["institution_playbook"])
    if any(genre in SPEECH_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["speech_playbook"])
    if any(genre in MEETING_HOST_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["meeting_host_playbook"])
    if any(genre in DUTY_REPORT_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["duty_report_playbook"])
    if any(genre in RESEARCH_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["research_playbook"])
    if any(genre in FEASIBILITY_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["feasibility_playbook"])
    if any(genre in PURPOSE_PLAYBOOK_GENRES for genre in genres):
        paths.extend(_purpose_primary_paths(genres))
    if any(genre in DELIBERATION_PLAYBOOK_GENRES for genre in genres):
        paths.extend(_deliberation_primary_paths(genres))
    if any(genre in DEPLOYMENT_PLAYBOOK_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["deployment_playbook"])
    if any(genre in ADVISORY_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["advisory_playbook"])
    if any(genre in COMPLAINT_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["complaint_playbook"])
    if any(genre in REMEDIATION_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["remediation_playbook"])
    if any(genre in PROJECT_APPLICATION_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["project_application_playbook"])
    if any(genre in REPLY_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["reply_playbook"])
    if any(genre in OPINION_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["opinion_playbook"])
    if any(genre in EXPLANATION_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["explanation_playbook"])
    return list(dict.fromkeys(paths or GENRE_REFERENCES["unknown_genre"]))


def _report_transaction_overlay_paths(genres: list[str], tasks: list[str]) -> list[str]:
    """Add at most one report transaction overlay when the scene is explicit."""
    if not any(genre in REPORT_PLAYBOOK_GENRES for genre in genres):
        return []
    joined = "\n".join(tasks + genres)
    paths: list[str] = []
    if any(marker in joined for marker in REMEDIATION_REPORT_MARKERS):
        paths.extend(GENRE_REFERENCES["remediation_report_overlay"])
    if any(marker in joined for marker in FEEDBACK_REPORT_MARKERS):
        paths.extend(GENRE_REFERENCES["feedback_report_overlay"])
    return list(dict.fromkeys(paths))


def _periodic_report_field_paths(genres: list[str], tasks: list[str]) -> list[str]:
    if not any(genre in PERIODIC_REPORT_GENRES for genre in genres):
        return []
    if not any(_contains_marker(task, PERIODIC_REPORT_FIELD_MARKERS) for task in tasks):
        return []
    return GENRE_REFERENCES["field_editing"]


def _finish_reference_paths(paths: list[str], tasks: list[str]) -> list[str]:
    # This deterministic fixture mirrors the shared flow; native route tests
    # observe the model's own file reads instead of this preselected context.
    common = [
        "references/writing-rules.md",
        "references/anti-ai-patterns.md",
        "references/prose-lint-usage.md",
    ]
    selected = [path for path in paths if path not in common]
    # Ordinary limits, including 80 characters, are handled in writing-rules.
    if any(marker in task for task in tasks for marker in ("压缩", "超限", "篇幅分配", "计数口径")):
        selected.append("references/compression-details.md")
    return list(dict.fromkeys(selected + common))


def _reference_paths_for_genres(genres: list[str], tasks: list[str] | None = None) -> list[str]:
    tasks = tasks or []
    ai_compute = any(_is_ai_compute(genre, tasks) for genre in genres)
    genres = _genres_for_delivery_purpose(genres, tasks)
    paths = ["SKILL.md"]
    report_playbook = any(genre in REPORT_PLAYBOOK_GENRES for genre in genres)
    request_playbook = any(genre in REQUEST_REVIEW_GENRES for genre in genres)
    ordinary_letter_playbook = any(genre in ORDINARY_LETTER_PLAYBOOK_GENRES for genre in genres)
    work_summary_playbook = any(genre in WORK_SUMMARY_PLAYBOOK_GENRES for genre in genres)
    work_priorities_playbook = any(
        genre in WORK_PRIORITIES_PLAYBOOK_GENRES for genre in genres
    )
    notice_playbook = any(genre in NOTICE_PLAYBOOK_GENRES for genre in genres)
    publication_playbook = any(genre in PUBLICATION_PLAYBOOK_GENRES for genre in genres)
    procurement_announcement_playbook = any(
        genre in PROCUREMENT_ANNOUNCEMENT_GENRES for genre in genres
    )
    institution_playbook = any(
        any(marker in genre for marker in INSTITUTION_PLAYBOOK_MARKERS)
        for genre in genres
    )
    speech_playbook = any(genre in SPEECH_PLAYBOOK_GENRES for genre in genres)
    meeting_host_playbook = any(
        genre in MEETING_HOST_PLAYBOOK_GENRES for genre in genres
    )
    duty_report_playbook = any(
        genre in DUTY_REPORT_PLAYBOOK_GENRES for genre in genres
    )
    research_playbook = any(genre in RESEARCH_PLAYBOOK_GENRES for genre in genres)
    feasibility_playbook = any(genre in FEASIBILITY_PLAYBOOK_GENRES for genre in genres)
    purpose_playbook = any(genre in PURPOSE_PLAYBOOK_GENRES for genre in genres)
    deliberation_playbook = any(genre in DELIBERATION_PLAYBOOK_GENRES for genre in genres)
    deployment_playbook = any(genre in DEPLOYMENT_PLAYBOOK_GENRES for genre in genres)
    advisory_playbook = any(genre in ADVISORY_GENRES for genre in genres)
    complaint_playbook = any(genre in COMPLAINT_GENRES for genre in genres)
    remediation_playbook = any(genre in REMEDIATION_GENRES for genre in genres)
    project_application_playbook = any(genre in PROJECT_APPLICATION_GENRES for genre in genres)
    reply_playbook = any(genre in REPLY_GENRES for genre in genres)
    opinion_playbook = any(genre in OPINION_GENRES for genre in genres)
    explanation_playbook = any(genre in EXPLANATION_GENRES for genre in genres)
    plan_construction_playbook = any(
        _is_plan_construction_genre(genre) for genre in genres
    ) or (ai_compute and _ai_task_requests_plan_construction(tasks))
    ordinary_letter_full_playbook = (
        ordinary_letter_playbook and _ordinary_letter_requires_full_playbook(tasks)
    )

    if _tasks_are_review_only(tasks):
        paths.extend(_primary_reference_paths(genres, tasks))
        paths.extend(_procurement_overlay_paths(genres, tasks))
        paths.extend(_report_transaction_overlay_paths(genres, tasks))
        paths.extend(_periodic_report_field_paths(genres, tasks))
        if ai_compute:
            paths.extend(GENRE_REFERENCES["ai_compute"])
        paths.extend(GENRE_REFERENCES["review"])
        return _finish_reference_paths(paths, tasks)

    if any(genre in NEWS_COMMENTARY_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["news_commentary"])
        return _finish_reference_paths(paths, tasks)

    if any(genre in NEWS_MESSAGE_GENRES for genre in genres):
        paths.extend(GENRE_REFERENCES["news_message"])
        return _finish_reference_paths(paths, tasks)

    if genres and all(genre in AI_COMPUTE_EXACT_GENRES for genre in genres):
        paths.extend(_compute_primary_paths(genres, tasks))
        paths.extend(_procurement_overlay_paths(genres, tasks))
        paths.extend(GENRE_REFERENCES["ai_compute"])
        return _finish_reference_paths(paths, tasks)

    if any("通报" in genre for genre in genres):
        paths.append("references/genre-playbook-bulletin.md")
        return _finish_reference_paths(paths, tasks)

    if "会议纪要" in genres:
        paths.extend(GENRE_REFERENCES["minutes_playbook"])
    if report_playbook:
        paths.extend(GENRE_REFERENCES["report_playbook"])
        paths.extend(_report_transaction_overlay_paths(genres, tasks))
        paths.extend(_periodic_report_field_paths(genres, tasks))
    if request_playbook:
        paths.extend(GENRE_REFERENCES["request_playbook"])
    if ordinary_letter_playbook and not ordinary_letter_full_playbook:
        paths.extend(GENRE_REFERENCES["correspondence_playbook"])
    if work_summary_playbook:
        paths.extend(GENRE_REFERENCES["work_summary_playbook"])
    if work_priorities_playbook:
        paths.extend(GENRE_REFERENCES["work_priorities_playbook"])
    if plan_construction_playbook:
        paths.extend(GENRE_REFERENCES["plan_construction_playbook"])
    if notice_playbook:
        paths.extend(GENRE_REFERENCES["notice_playbook"])
    if publication_playbook:
        paths.extend(GENRE_REFERENCES["publication_playbook"])
    if procurement_announcement_playbook:
        paths.extend(GENRE_REFERENCES["procurement_announcement_playbook"])
    if institution_playbook:
        paths.extend(GENRE_REFERENCES["institution_playbook"])
    if speech_playbook:
        paths.extend(GENRE_REFERENCES["speech_playbook"])
    if meeting_host_playbook:
        paths.extend(GENRE_REFERENCES["meeting_host_playbook"])
    if duty_report_playbook:
        paths.extend(GENRE_REFERENCES["duty_report_playbook"])
    if research_playbook:
        paths.extend(GENRE_REFERENCES["research_playbook"])
    if feasibility_playbook:
        paths.extend(GENRE_REFERENCES["feasibility_playbook"])
    if purpose_playbook:
        paths.extend(_purpose_primary_paths(genres))
    if deliberation_playbook:
        paths.extend(_deliberation_primary_paths(genres))
    if deployment_playbook:
        paths.extend(GENRE_REFERENCES["deployment_playbook"])
    if advisory_playbook:
        paths.extend(GENRE_REFERENCES["advisory_playbook"])
    if complaint_playbook:
        paths.extend(GENRE_REFERENCES["complaint_playbook"])
    if remediation_playbook:
        paths.extend(GENRE_REFERENCES["remediation_playbook"])
    if project_application_playbook:
        paths.extend(GENRE_REFERENCES["project_application_playbook"])
    if reply_playbook:
        paths.extend(GENRE_REFERENCES["reply_playbook"])
    if opinion_playbook:
        paths.extend(GENRE_REFERENCES["opinion_playbook"])
    if explanation_playbook:
        paths.extend(GENRE_REFERENCES["explanation_playbook"])
    if not any(
        (
            report_playbook,
            request_playbook,
            ordinary_letter_playbook,
            work_summary_playbook,
            work_priorities_playbook,
            plan_construction_playbook,
            notice_playbook,
            publication_playbook,
            procurement_announcement_playbook,
            institution_playbook,
            speech_playbook,
            meeting_host_playbook,
            duty_report_playbook,
            research_playbook,
            feasibility_playbook,
            purpose_playbook,
            deliberation_playbook,
            deployment_playbook,
            advisory_playbook,
            complaint_playbook,
            remediation_playbook,
            project_application_playbook,
            reply_playbook,
            opinion_playbook,
            explanation_playbook,
            "会议纪要" in genres,
        )
    ):
        paths.extend(GENRE_REFERENCES["unknown_genre"])
    if any(
        genre in PLAYBOOK_GENRES
        and genre != "会议纪要"
        and genre not in REPORT_PLAYBOOK_GENRES
        and genre not in REQUEST_REVIEW_GENRES
        and genre not in ORDINARY_LETTER_PLAYBOOK_GENRES
        and genre not in WORK_SUMMARY_PLAYBOOK_GENRES
        and genre not in WORK_PRIORITIES_PLAYBOOK_GENRES
        and genre not in NOTICE_PLAYBOOK_GENRES
        and genre not in PUBLICATION_PLAYBOOK_GENRES
        and genre not in PROCUREMENT_ANNOUNCEMENT_GENRES
        and genre not in SPEECH_PLAYBOOK_GENRES
        and genre not in MEETING_HOST_PLAYBOOK_GENRES
        and genre not in DUTY_REPORT_PLAYBOOK_GENRES
        and genre not in RESEARCH_PLAYBOOK_GENRES
        and genre not in FEASIBILITY_PLAYBOOK_GENRES
        and genre not in PURPOSE_PLAYBOOK_GENRES
        and genre not in DELIBERATION_PLAYBOOK_GENRES
        and genre not in DEPLOYMENT_PLAYBOOK_GENRES
        and genre not in ADVISORY_GENRES
        and genre not in COMPLAINT_GENRES
        and genre not in REMEDIATION_GENRES
        and genre not in PROJECT_APPLICATION_GENRES
        and genre not in REPLY_GENRES
        and genre not in OPINION_GENRES
        and genre not in EXPLANATION_GENRES
        and not any(marker in genre for marker in INSTITUTION_PLAYBOOK_MARKERS)
        and not _is_plan_construction_genre(genre)
        for genre in genres
    ) or (
        ai_compute
        and _ai_requires_ordinary_playbook(genres, tasks)
        and not report_playbook
        and not request_playbook
        and not ordinary_letter_playbook
        and not work_summary_playbook
        and not work_priorities_playbook
        and not plan_construction_playbook
        and not notice_playbook
        and not institution_playbook
        and not speech_playbook
        and not meeting_host_playbook
        and not duty_report_playbook
        and not research_playbook
        and not purpose_playbook
        and not deliberation_playbook
    ) or ordinary_letter_full_playbook:
        paths.extend(GENRE_REFERENCES["unknown_genre"])
    if any(_contains_marker(task, ROUTING_TASK_MARKERS) for task in tasks):
        paths.extend(GENRE_REFERENCES["routing"])
    complex_route = _task_requires_complex_route(tasks) or _request_procurement_requires_complex_route(
        genres,
        tasks,
    )
    argument_requested = any(_contains_marker(task, ARGUMENT_TASK_MARKERS) for task in tasks)
    if complex_route:
        paths.extend(GENRE_REFERENCES["complex"])
        if any(genre in CHAIN_GENRES for genre in genres) or ai_compute or argument_requested:
            paths.extend(GENRE_REFERENCES["argument"])
    elif argument_requested:
        paths.extend(GENRE_REFERENCES["argument"])

    if any(_contains_marker(task, STYLE_TASK_MARKERS) for task in tasks):
        paths.extend(GENRE_REFERENCES["style"])
    if (speech_playbook or meeting_host_playbook) and any(
        _contains_marker(task, SPEECH_PERSON_ORDER_MARKERS) for task in tasks
    ):
        paths.extend(GENRE_REFERENCES["speech_person_order"])
    if ai_compute:
        paths.extend(GENRE_REFERENCES["ai_compute"])
    paths.extend(_procurement_overlay_paths(genres, tasks))
    if any(marker in task for task in tasks for marker in FORMAT_TASK_MARKERS):
        paths.extend(GENRE_REFERENCES["format"])
    if _task_requires_external_research(tasks):
        paths.extend(GENRE_REFERENCES["external_research"])

    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            ordered.append(path)
    return _finish_reference_paths(ordered, tasks)


def _load_skill_context_from_paths(repo_root: Path, reference_paths: list[str]) -> str:
    root = _skill_root(repo_root)
    parts: list[str] = []
    for relative in reference_paths:
        path = root / relative
        if not path.exists():
            raise ProviderError(f"selected skill reference does not exist: {path}")
        parts.append(f"## {relative}\n{_read_text(path)}")
    context = "\n\n".join(parts)
    if len(context) > MAX_SKILL_CONTEXT_CHARS:
        raise ProviderError(
            f"selected skill context exceeds {MAX_SKILL_CONTEXT_CHARS} characters: {len(context)}"
        )
    return context


def _load_skill_context(repo_root: Path, genres: list[str], tasks: list[str] | None = None) -> str:
    return _load_skill_context_from_paths(repo_root, _reference_paths_for_genres(genres, tasks))


def _case_id(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("case_id", "")).strip()


def _case_genre(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("genre", "")).strip()


def _case_task(case: dict[str, Any]) -> str:
    return str((case.get("vars") or {}).get("task", "")).strip()


def _case_reference_paths(case: dict[str, Any]) -> list[str]:
    genre = _case_genre(case)
    task = _case_task(case)
    return _reference_paths_for_genres([genre] if genre else [], [task] if task else [])


def _reference_paths_for_cases(cases: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    for case in cases:
        paths.extend(_case_reference_paths(case))
    return list(dict.fromkeys(paths))


def _skill_batch_reference_paths(cases: list[dict[str, Any]]) -> list[str]:
    signatures = {tuple(_case_reference_paths(case)) for case in cases}
    if not signatures:
        raise ProviderError("cannot build a skill prompt without cases")
    if len(signatures) != 1:
        raise ProviderError("skill batch contains mixed reference routes")
    return list(next(iter(signatures)))


def _render_tasks(cases: list[dict[str, Any]]) -> str:
    return "\n".join(f"{_case_id(case)}: {_case_task(case)}" for case in cases)


def _baseline_prompt(cases: list[dict[str, Any]]) -> str:
    return textwrap.dedent(
        f"""
        你是中文正式材料写作助手。请不要读取或使用任何仓库文件、Skill、清单或模板，只依据下面任务写作。

        对每个任务输出一段中文正式材料初稿，控制在 160-260 个汉字。不要编造真实单位、真实政策、真实金额、
        人名、电话、邮箱或内部项目事实。可使用“有关单位”“相关部门”等泛称，但不要把“发文机关、
        发文字号、主送单位”等占位标签写进正文。

        输出必须严格按如下格式，不要解释：
        ### <case_id>
        <正文>

        任务：
        {_render_tasks(cases)}
        """
    ).strip()


def _skill_prompt(cases: list[dict[str, Any]], config: dict[str, Any]) -> str:
    repo_root = _repo_root(config)
    tasks = [_case_task(case) for case in cases if _case_task(case)]
    reference_paths = _skill_batch_reference_paths(cases)
    skill_context = _load_skill_context_from_paths(repo_root, reference_paths)
    delivery_instruction = "按用户指定的任务、范围和所读 Skill 交付。"
    return textwrap.dedent(
        f"""
        你是中文公文 Skill 写作代理。仓库已安装 Skill：
        `packages/agent-skills/skills/chinese-official-writing/SKILL.md`。

        只使用下列 Skill 入口和本批任务已选中的 references；不要加载整包上下文，不要复制参考资料原文，
        也不要自行扩展到未选中的 reference 路线。{delivery_instruction}

        不要编造真实单位、真实政策、真实金额、
        人名、电话、邮箱或内部项目事实。可使用“有关单位”“相关部门”等泛称，但不要把“发文机关、
        发文字号、主送单位”等占位标签写进正文。

        输出必须严格按如下格式，不要解释：
        ### <case_id>
        <正文或审稿结果>

        Skill context:
        ```text
        {skill_context}
        ```

        任务：
        {_render_tasks(cases)}
        """
    ).strip()


def _single_prompt(mode: str, case: dict[str, Any], config: dict[str, Any]) -> str:
    if mode == "skill":
        return _skill_prompt([case], config)
    return _baseline_prompt([case])


def _agent_command_template(config: dict[str, Any] | None = None) -> str:
    config = config or {}
    return str(
        config.get("commandTemplate")
        or os.environ.get("OFFICIAL_WRITING_AGENT_COMMAND")
        or os.environ.get("OFFICIAL_WRITING_EVAL_COMMAND")
        or ""
    ).strip()


def _truthy_env(name: str) -> bool | None:
    value = os.environ.get(name)
    if value is None:
        return None
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _use_stub(config: dict[str, Any] | None = None) -> bool:
    explicit = _truthy_env("OFFICIAL_WRITING_EVAL_STUB")
    if explicit is not None:
        return explicit
    return not _agent_command_template(config)


def use_stub(config: dict[str, Any] | None = None) -> bool:
    return _use_stub(config)


def _agent_cmd(prompt: str, config: dict[str, Any] | None = None) -> list[str]:
    template = _agent_command_template(config)
    if not template:
        raise ProviderError("agent eval command is not configured")
    tokens = shlex.split(template, posix=os.name != "nt")
    replacements = {
        "{prompt}": prompt,
        "{prompt_json}": json.dumps(prompt, ensure_ascii=False),
    }
    has_placeholder = any(marker in token for token in tokens for marker in replacements)
    if has_placeholder:
        return [
            token.replace("{prompt}", replacements["{prompt}"]).replace("{prompt_json}", replacements["{prompt_json}"])
            for token in tokens
        ]
    return [*tokens, prompt]


def call_model_prompt(
    prompt: str,
    cwd: Path,
    timeout_seconds: int,
    config: dict[str, Any] | None = None,
    retries: int = 1,
) -> tuple[str, int, int]:
    output = ""
    return_code = 1
    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                _agent_cmd(prompt, config),
                cwd=str(cwd),
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + "\n" + (exc.stderr or "")
            return_code = 124
        else:
            output = result.stdout
            # Keep model stdout as the only draft channel.  CLI diagnostics
            # belong to the harness log; appending them would turn warnings
            # into apparent正文/旁白 and contaminate the writing comparison.
            if not output.strip() and result.stderr:
                output = result.stderr
            return_code = result.returncode
        if output.strip() or return_code != 0:
            break
        time.sleep(2 + attempt)
    return output, return_code, len(prompt)


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[A-Za-z0-9_-]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _normalize_draft(text: str, case_id: str) -> str:
    text = _strip_code_fences(text)
    text = re.sub(rf"^\s*(?:#{1,6}\s*)?(?:[AB]-)?{re.escape(case_id)}[：:\s-]*", "", text).strip()
    text = re.sub(r"^\s*(以下为|下面是|正文如下)[^。\n]*[。:\n]", "", text).strip()
    return text.strip()


def _parse_sections(raw: str, case_ids: set[str]) -> dict[str, str]:
    lines = raw.splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    header_re = re.compile(r"^\s*(?:#{1,6}\s*)?(?:[AB]-)?(C\d{3})\b[：:\s-]*(.*)$", re.I)
    for line in lines:
        match = header_re.match(line)
        if match and match.group(1) in case_ids:
            current = match.group(1)
            sections.setdefault(current, [])
            if match.group(2).strip():
                sections[current].append(match.group(2).strip())
            continue
        if current:
            sections[current].append(line)

    parsed: dict[str, str] = {}
    for case_id, body_lines in sections.items():
        body = _normalize_draft("\n".join(body_lines), case_id)
        if body:
            parsed[case_id] = body
    return parsed


def _stub_draft(mode: str, case: dict[str, Any]) -> str:
    genre = _case_genre(case)
    scenario = str((case.get("vars") or {}).get("scenario", "")).strip()
    if mode == "baseline":
        return (
            f"围绕{scenario}事项，相关工作要全面赋能、不断提升，形成一批阶段性成果。"
            "各单位应高度重视，加强统筹协调，确保任务顺利推进。下一步将结合实际持续优化流程，"
            "进一步提升管理水平和服务能力，满足未来发展需要。"
        )
    if _is_ai_compute(genre):
        return (
            f"本{genre}围绕{scenario}需求，先按业务系统、使用人数、任务频次和单次 Token 消耗测算年度调用量，"
            "再折算 GPU、并发和云端费用。拟通过租赁服务明确部署边界、SLA、运维响应、安全审计和验收责任，"
            "以稳定周期成本并降低一次性建设风险。"
        )
    if genre == "请示":
        return (
            f"为推进{scenario}事项，拟由牵头部门组织相关单位开展资料核验、责任分工和节点管理，"
            "同步明确经费来源、实施范围和风险控制要求。现提请审定该事项启动安排及后续办理路径，"
            "妥否，请批示。"
        )
    if genre == "报告":
        return (
            f"现将{scenario}有关情况报告如下：前期已完成任务梳理、资料核验和责任分工，"
            "主要问题集中在数据口径、协同流程和归档标准不够统一。下一步将完善台账管理，"
            "按节点推进整改复核和成果归档。"
        )
    if genre == "复函":
        return (
            f"关于{scenario}事项的来函收悉。经研究，现函复如下：请按既定程序明确材料范围、"
            "办理条件、责任分工和反馈时限，同步说明联系人、附件依据和后续管理要求；"
            "涉及数据口径和结果报送的，请留存核验记录，便于后续沟通。"
        )
    return (
        f"现就{scenario}有关事项作出安排。请相关单位对照{genre}办理要求，明确责任分工、材料清单、"
        "反馈时限和联系人，按程序完成资料核验、过程记录和结果报送。涉及附件、数据和后续管理的，"
        "同步说明来源、范围和复核方式。"
    )


def _cache_key(mode: str, cases: list[dict[str, Any]], config: dict[str, Any]) -> str:
    routes = {
        _case_id(case): _case_reference_paths(case)
        for case in cases
    } if mode == "skill" else {}
    refs = _reference_paths_for_cases(cases) if mode == "skill" else []
    ref_hashes: dict[str, str] = {}
    if mode == "skill":
        root = _skill_root(_repo_root(config))
        for relative in refs:
            path = root / relative
            if path.exists():
                ref_hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    payload = {
        "mode": mode,
        "cases": [case.get("vars", {}) for case in cases],
        "routes": routes,
        "refs": refs,
        "ref_hashes": ref_hashes,
        "provider_version": 9,
        "stub": _use_stub(config),
        "command_configured": bool(_agent_command_template(config)),
        "command_template_hash": hashlib.sha256(
            _agent_command_template(config).encode("utf-8")
        ).hexdigest(),
        "batch_size": config.get("batchSize", 10),
        "timeout_seconds": config.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS),
        "retries": config.get("retries", 1),
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:20]


def _write_cache(path: Path, data: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_cache(path: Path) -> dict[str, str] | None:
    if not path.exists() or os.environ.get("OFFICIAL_WRITING_EVAL_REFRESH"):
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _run_batch(mode: str, cases: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, str]:
    if _use_stub(config):
        return {_case_id(case): _stub_draft(mode, case) for case in cases}

    repo_root = _repo_root(config)
    timeout = int(config.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS))
    retries = int(config.get("retries", 1))
    prompt = _skill_prompt(cases, config) if mode == "skill" else _baseline_prompt(cases)
    raw, code, _prompt_chars = call_model_prompt(prompt, repo_root, timeout, config=config, retries=retries)
    if code != 0 and not raw.strip():
        raise ProviderError(f"agent eval command returned code {code} with empty output")
    case_ids = {_case_id(case) for case in cases}
    parsed = _parse_sections(raw, case_ids)
    return parsed


def _run_single(mode: str, case: dict[str, Any], config: dict[str, Any]) -> str:
    if _use_stub(config):
        return _stub_draft(mode, case)

    repo_root = _repo_root(config)
    timeout = int(config.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS))
    retries = int(config.get("retries", 1))
    prompt = _single_prompt(mode, case, config)
    raw, code, _prompt_chars = call_model_prompt(prompt, repo_root, timeout, config=config, retries=retries)
    if code != 0 and not raw.strip():
        raise ProviderError(f"agent eval command returned code {code} for {_case_id(case)} with empty output")
    parsed = _parse_sections(raw, {_case_id(case)})
    if parsed.get(_case_id(case)):
        return parsed[_case_id(case)]
    return _normalize_draft(raw, _case_id(case))


def _batch_cases(mode: str, cases: list[dict[str, Any]], batch_size: int) -> list[list[dict[str, Any]]]:
    if mode != "skill":
        return [cases[index : index + batch_size] for index in range(0, len(cases), batch_size)]

    route_groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for case in cases:
        route_groups.setdefault(tuple(_case_reference_paths(case)), []).append(case)

    batches: list[list[dict[str, Any]]] = []
    for group in route_groups.values():
        batches.extend(group[index : index + batch_size] for index in range(0, len(group), batch_size))
    return batches


def _ensure_batch_cache(mode: str, config: dict[str, Any]) -> dict[str, str]:
    memory_key = f"{mode}:{_cache_key(mode, _load_cases(config), config)}"
    if memory_key in _BATCH_CACHE:
        return _BATCH_CACHE[memory_key]

    cases = _load_cases(config)
    cache_path = _cache_dir(config) / f"writer-{memory_key.replace(':', '-')}.json"
    cached = _load_cache(cache_path)
    if cached is not None:
        _BATCH_CACHE[memory_key] = cached
        return cached

    batch_size = max(1, int(config.get("batchSize", 10)))
    outputs: dict[str, str] = {}
    for chunk in _batch_cases(mode, cases, batch_size):
        outputs.update(_run_batch(mode, chunk, config))
        _write_cache(cache_path, outputs)

    _BATCH_CACHE[memory_key] = outputs
    return outputs


def _estimate_usage(prompt: str, output: str, config: dict[str, Any]) -> tuple[dict[str, int], float]:
    prompt_tokens = max(1, len(prompt) // 2)
    completion_tokens = max(1, len(output) // 2)
    total = prompt_tokens + completion_tokens
    cost_per_1k_chars = float(config.get("estimatedCostPer1kChars", 0.00002))
    cost = ((len(prompt) + len(output)) / 1000.0) * cost_per_1k_chars
    return {"prompt": prompt_tokens, "completion": completion_tokens, "total": total, "numRequests": 1}, cost


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    config = _options_config(options)
    mode = str(config.get("mode", "baseline")).strip().lower()
    if mode not in {"baseline", "skill"}:
        return {"output": "", "error": f"unsupported provider mode: {mode}"}

    case = _current_case(context)
    case_id = _case_id(case)
    started = time.time()
    try:
        outputs = _ensure_batch_cache(mode, config) if config.get("prebatch", True) else {}
        output = outputs.get(case_id)
        if not output:
            output = _run_single(mode, case, config)
    except Exception as exc:
        return {"output": "", "error": str(exc)}

    output = _normalize_draft(output, case_id)
    if not output:
        return {"output": "", "error": f"empty output for {case_id} in {mode} mode"}

    token_usage, cost = _estimate_usage(prompt, output, config)
    return {
        "output": output,
        "tokenUsage": token_usage,
        "cost": cost,
        "latencyMs": int((time.time() - started) * 1000),
        "metadata": {
            "case_id": case_id,
            "genre": _case_genre(case),
            "mode": mode,
            "selected_references": _case_reference_paths(case) if mode == "skill" else [],
            "provider": str(
                config.get("providerLabel")
                or os.environ.get("OFFICIAL_WRITING_EVAL_PROVIDER_LABEL")
                or ("deterministic-local" if _use_stub(config) else "agent-eval-command")
            ),
            "estimated_cost_note": "character-count proxy; agent command billing is not read here",
        },
    }
