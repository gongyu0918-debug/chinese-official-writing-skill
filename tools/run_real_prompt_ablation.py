#!/usr/bin/env python3
"""Compare real-user prompt coverage between two skill package roots.

This is a deterministic release check. It does not call an LLM. The cases use
realistic user-style prompts and verify whether each skill package contains the
trigger, routing, checklist, handling-element, and lint behavior needed to
support the prompt without relying on ad hoc reviewer judgment.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PromptCase:
    id: str
    kind: str
    prompt: str
    checks: dict[str, Any] = field(default_factory=dict)


CASES: list[PromptCase] = [
    PromptCase(
        id="P001",
        kind="create",
        prompt="帮我起草一份向各区征求意见的函，附件是管理办法征求意见稿，要求写清反馈期限、邮箱和联系人。",
        checks={
            "description_terms": ["征求意见函"],
            "routing_terms": ["征求意见函", "反馈期限", "反馈方式"],
            "checklist_sections": ["征求意见函"],
            "handling_rows": ["征求意见函"],
        },
    ),
    PromptCase(
        id="P002",
        kind="create",
        prompt="写一份采购公告，项目是办公软件会员服务采购，预算上限 2 万元，要有响应文件提交方式和联系人。",
        checks={
            "description_terms": ["采购公告"],
            "routing_terms": ["采购公告", "预算", "联系方式"],
            "checklist_sections": ["采购公告"],
            "handling_rows": ["采购公告"],
        },
    ),
    PromptCase(
        id="P003",
        kind="create",
        prompt="请起草拟聘用人员公示，公示 5 个工作日，要求写明异议渠道、联系电话和处理规则。",
        checks={
            "description_terms": ["公示"],
            "routing_terms": ["公示", "期限", "异议渠道"],
            "checklist_sections": ["公示"],
            "handling_rows": ["公示"],
        },
    ),
    PromptCase(
        id="P004",
        kind="create",
        prompt="给我写一份年度信息化工作要点，按重点任务、责任机制、时间节点和评价方式组织。",
        checks={
            "description_terms": ["工作要点"],
            "routing_terms": ["工作要点", "时间节点", "评价方式"],
            "checklist_sections": ["工作要点"],
            "handling_rows": ["工作要点"],
        },
    ),
    PromptCase(
        id="P005",
        kind="create",
        prompt="起草一份项目初步设计审查材料，区分审查依据、主要发现、风险、整改要求和审查结论。",
        checks={
            "description_terms": ["审查材料"],
            "routing_terms": ["审查材料", "整改要求", "结论"],
            "checklist_sections": ["审查材料"],
            "handling_rows": ["审查材料"],
        },
    ),
    PromptCase(
        id="P006",
        kind="revise",
        prompt="请把这段顺成正式报告：根据领导要求，项目组已完成风险排查。领导关心的交付节点已纳入每周调度。",
        checks={
            "lint_text": "根据领导要求，项目组已完成风险排查。领导关心的交付节点已纳入每周调度。",
            "lint_absent_labels": ["viewpoint-risk", "casual"],
        },
    ),
    PromptCase(
        id="P007",
        kind="revise",
        prompt="审一下这段能不能进正文：本材料由 AI 起草。根据用户要求修改如下：这版文章将压缩为三段。",
        checks={
            "lint_text": "本材料由 AI 起草。根据用户要求修改如下：这版文章将压缩为三段。",
            "lint_present_labels": ["thought-leak", "viewpoint-risk"],
        },
    ),
    PromptCase(
        id="P008",
        kind="revise",
        prompt="请把纪要里的这句保留成正式表达：会议要求如下，各责任单位每周反馈整改进展。",
        checks={
            "lint_text": "会议要求如下，各责任单位每周反馈整改进展。",
            "lint_absent_labels": ["viewpoint-risk"],
        },
    ),
    PromptCase(
        id="P009",
        kind="revise",
        prompt="在第三部分后增加一个说明数据口径影响的自然段，不要新增小标题，原四个小标题必须保持不变。",
        checks={
            "review_checklist_terms": ["改稿前小标题清单", "改稿后小标题清单", "小标题数量"],
            "heading_lock": {
                "before": """一、整改进展
二、存在问题
三、原因分析
四、下一步安排""",
                "after": """一、整改进展
二、存在问题
三、原因分析
四、下一步安排""",
            },
        },
    ),
    PromptCase(
        id="P010",
        kind="create",
        prompt="写一份情况说明，说明系统维护期间部分数据同步延迟、已恢复、后续加强监测；不要写成请示，也不要加接收方。",
        checks={
            "description_terms": ["说明"],
            "routing_terms": ["说明", "不写成请示"],
            "checklist_sections": ["说明"],
            "handling_rows": ["说明"],
            "file_terms": {
                "chinese-official-writing/references/format-gbt9704.md": ["最终以用户模板和材料属性为准"],
            },
        },
    ),
    PromptCase(
        id="P011",
        kind="create",
        prompt="帮我起草一份内部 WPS 会员采购申请，保留“尊敬的领导：”称呼和两行标题，不要强行改成法定公文格式。",
        checks={
            "description_terms": ["申请"],
            "routing_terms": ["申请", "不因使用请批语就自动改成请示"],
            "checklist_sections": ["申请"],
            "handling_rows": ["申请"],
            "file_terms": {
                "chinese-official-writing/references/genre-checklist.md": ["两行标题", "尊敬的领导"],
                "chinese-official-writing/references/formal-addressing.md": ["不作无依据硬删"],
            },
        },
    ),
    PromptCase(
        id="P012",
        kind="revise",
        prompt="把这份报告改得正式一点，但我明确要求不写主送机关，不要补接收方，也不要加“妥否，请批示”。",
        checks={
            "routing_terms": ["报告", "不以“妥否，请批示”收尾"],
            "review_checklist_terms": ["只有明确要求时才作硬性位置断言"],
            "file_terms": {
                "chinese-official-writing/references/final-review-layers.md": ["用户明确要求是否遗漏", "只有在用户或文种明确要求时"],
                "chinese-official-writing/references/format-gbt9704.md": ["最终以用户模板和材料属性为准"],
            },
        },
    ),
    PromptCase(
        id="P013",
        kind="revise",
        prompt="把这份申请顺一下，保留“尊敬的领导：”、右下落款和“妥否，请批示”结尾，不要改成请示。",
        checks={
            "routing_terms": ["不因使用请批语就自动改成请示"],
            "checklist_sections": ["申请"],
            "file_terms": {
                "chinese-official-writing/references/genre-checklist.md": ["不要只因出现 `妥否，请批示` 就判定为请示"],
                "chinese-official-writing/references/formal-addressing.md": ["申请向上级或领导班子请求批准时", "不要违背用户指定结尾"],
            },
        },
    ),
    PromptCase(
        id="P014",
        kind="revise",
        prompt="审一下这段能不能直接作为正文交付，模型把全文包在代码块里，里面还有项目名称和日期占位。",
        checks={
            "lint_text": "```text\n项目名称为[具体项目名称]，计划于YYYY年MM月DD日完成。\n```",
            "lint_present_labels": ["markdown-code-fence", "unfinished-placeholder"],
        },
    ),
    PromptCase(
        id="P015",
        kind="revise",
        prompt="审一下这段是否还留着未完成占位：维护期限为XXXX年，设备XXXX张，支持XXXX并发请求。",
        checks={
            "lint_text": "维护期限为XXXX年，设备XXXX张，支持XXXX并发请求。",
            "lint_present_labels": ["unfinished-placeholder"],
        },
    ),
    PromptCase(
        id="P016",
        kind="revise",
        prompt="审一下这段 AI 算力采购说明是否会被误判为模型自述：本平台面向AI生成内容业务，支撑AI辅助生成内容的并发推理。",
        checks={
            "lint_text": "本平台面向AI生成内容业务，支撑AI辅助生成内容的并发推理。",
            "lint_absent_labels": ["thought-leak"],
        },
    ),
    PromptCase(
        id="P017",
        kind="revise",
        prompt="审一下这段报告和方案正文能不能交付：本报告系AI辅助生成，仅供参考。该方案为AI生成初稿。",
        checks={
            "lint_text": "本报告系AI辅助生成，仅供参考。该方案为AI生成初稿。",
            "lint_present_labels": ["thought-leak"],
        },
    ),
    PromptCase(
        id="P018",
        kind="revise",
        prompt="审一下这段方案正文格式是否合适：### 业务需求与服务保障。",
        checks={
            "lint_text": "### 业务需求与服务保障\n正文内容。",
            "lint_present_labels": ["markdown-heading"],
        },
    ),
    PromptCase(
        id="P019",
        kind="revise",
        prompt="把这段去口语化，但不要补原文没有的事实活动、依据、数据或成效。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["未新增原文外事实"],
                "chinese-official-writing/references/workflow.md": [
                    "不新增原文没有交代的活动、依据、数据、成效或责任安排",
                    "未新增原文外事实",
                ],
                "chinese-official-writing/references/review-checklist.md": ["未新增原文外事实"],
            },
        },
    ),
    PromptCase(
        id="P020",
        kind="revise",
        prompt="给 prose_lint 增加新规则前，先确认真实合格公文 clean corpus 不会被 medium/high 误报。",
        checks={
            "file_terms": {
                "tests/fixtures/clean_prose_corpus.json": ["notice-submit-materials", "ai-compute-plan"],
                "tests/test_review_regressions.py": ["test_clean_corpus_has_no_medium_or_high_findings"],
            },
        },
    ),
    PromptCase(
        id="P021",
        kind="create",
        prompt="我要用真实模型跑一小组公文评测，不要沿用 stub 发布门槛误杀，请给出可复现入口和阈值覆盖方式。",
        checks={
            "file_terms": {
                "README.md": [
                    "真实模型小样本评测",
                    "OFFICIAL_WRITING_SKILL_PLACEHOLDER_RISK_RATE_MAX",
                ],
                "evals/official-writing/run_eval.py": ["THRESHOLD_ENV_VARS"],
            },
        },
    ),
    PromptCase(
        id="P022",
        kind="revise",
        prompt="检查 OpenClaw 展示卡片和镜像目录是否会漂移：skill-card 链接要能在网页打开，镜像不能静默分叉。",
        checks={
            "file_terms": {
                "openclaw/skill-card.md": ["https://github.com/gongyu0918-debug/chinese-official-writing-skill"],
                "tests/test_skill_boundary.py": [
                    "test_primary_adapter_mirrors_match_canonical_bytes",
                    "test_packaged_resource_mirrors_match_canonical_bytes",
                ],
            },
        },
    ),
    PromptCase(
        id="P023",
        kind="create",
        prompt="写一份食品安全专项检查情况报告，有发现问题和下一步计划，不要写成请示，也不要加“妥否，请批示”。",
        checks={
            "description_terms": ["报告"],
            "routing_terms": ["报告", "不夹带审批请求"],
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["任务模式路由", "起草、改稿、复核、排版交付"],
                "chinese-official-writing/references/workflow.md": ["起草模式", "复核模式"],
            },
        },
    ),
    PromptCase(
        id="P024",
        kind="revise",
        prompt="把三个人写的年度总结材料合成一稿，严格保留我给的提纲顺序，原文事实要保留，新增事实请放到待确认事项。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["多材料合稿", "原文事实", "待确认补充"],
                "chinese-official-writing/references/workflow.md": [
                    "原文已有事实",
                    "压实合并表达",
                    "待确认补充",
                    "提纲顺序",
                ],
                "chinese-official-writing/references/review-checklist.md": ["原文已有事实", "压实合并表达", "待确认补充"],
            },
        },
    ),
    PromptCase(
        id="P025",
        kind="revise",
        prompt="我已经写好正文了，请按 GB/T 9704 排成 Word，带红头、发文字号和版记；没有给签发人就不要编，正文里的 markdown 标记也别带进 Word。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["Word、docx、GB/T 9704", "不得残留 Markdown"],
                "chinese-official-writing/references/format-gbt9704.md": [
                    "Word/排版交付衔接",
                    "DOCX/document 技能",
                    "不得编造文号",
                    "Markdown `**加粗**`",
                ],
                "chinese-official-writing/references/review-checklist.md": ["Word、docx、GB/T 9704", "代码块和 `###`"],
            },
        },
    ),
    PromptCase(
        id="P026",
        kind="revise",
        prompt="审一下这段是否 AI 味太重：意义重大、亮点纷呈、有关方面认为、未来可期、首先其次最后。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "公文表达结构风险",
                    "夸大意义",
                    "宣传腔",
                    "模糊归因",
                    "公式化未来展望",
                    "同义词循环",
                    "机械三段式",
                    "过度抽象词互相解释",
                    "不新增硬清洗",
                ],
            },
        },
    ),
    PromptCase(
        id="P027",
        kind="revise",
        prompt="两版材料里营业收入增速一个写 10%，一个写 12%，请合稿，不要默认就高，也不要自己选最优口径。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/workflow.md": [
                    "数据冲突不得默认就高",
                    "自选最优",
                    "区间口径",
                ],
                "chinese-official-writing/references/review-checklist.md": ["未默认就高或自选最优"],
            },
        },
    ),
    PromptCase(
        id="P028",
        kind="revise",
        prompt="请把这份材料处理成正式 Word 红头文件，要有发文字号、签发人和版记；这些要素我还没给，不要编，先列缺项清单。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["正式交付前要素核对", "不得编造文号"],
                "chinese-official-writing/references/format-gbt9704.md": [
                    "正式交付前要素核对",
                    "缺项清单",
                    "签发人",
                    "版记",
                    "印章",
                    "不得用 `[依据/背景]`",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "正式交付前要素核对",
                    "缺项清单",
                    "未编造文号、签发人、印章或版记",
                ],
            },
        },
    ),
    PromptCase(
        id="P029",
        kind="revise",
        prompt="只审一下这段格式和语气，不要重写全文：关于推进巡检工作的通知，大家要马上搞起来，然后月底前报结果。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "格式核验或语气检查",
                    "不默认重写全文",
                    "0-100 分式伪精确评分",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "位置、风险层级、修改建议",
                    "未默认重写全文",
                    "不做 0-100 分评分",
                    "用户可读格式复核项",
                ],
            },
        },
    ),
    PromptCase(
        id="P030",
        kind="revise",
        prompt="把这段去口语化但保留事实，不要新增依据和成效：我觉得这个事差不多可以马上搞一下，然后月底前报领导。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["轻量语气替换", "不新增硬清洗"],
                "chinese-official-writing/references/official-style.md": [
                    "轻量语气替换建议",
                    "我觉得",
                    "搞",
                    "差不多",
                    "马上",
                    "然后",
                    "保留原文事实",
                    "不新增硬清洗",
                ],
            },
        },
    ),
    PromptCase(
        id="P031",
        kind="create",
        prompt="起草一份政务数据共享通知，政策依据我没给，也不要外搜；不能编政策依据，缺项放待确认事项。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["默认不外搜", "搜索结果只作为来源参考", "待确认事项"],
                "chinese-official-writing/references/workflow.md": [
                    "联网搜索使用边界",
                    "默认按用户给定材料写稿",
                    "不把联网搜索作为起草、改稿或复核的默认步骤",
                ],
                "chinese-official-writing/references/handling-elements.md": [
                    "默认不外搜补缺项",
                    "不写成已确认事实",
                ],
            },
        },
    ),
    PromptCase(
        id="P032",
        kind="create",
        prompt="请核验现行政策依据后起草通知，要说明来源日期，不要把单一网络来源直接写成确定结论。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["现行政策", "联网核验", "来源、日期或检索口径"],
                "chinese-official-writing/references/workflow.md": [
                    "最新",
                    "当前",
                    "今日",
                    "现行政策",
                    "近期数据",
                    "发布日期、访问日期或检索口径",
                    "来源冲突、无法核验或工具不可用",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "搜索结果",
                    "正文外说明来源、日期或检索口径",
                ],
            },
        },
    ),
    PromptCase(
        id="P033",
        kind="create",
        prompt="帮市数据资源管理局写一份通知；我只给了单位名称，没让你查官网或样文，不要自动搜索单位风格。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["不因出现单位名称就搜索单位公开样文、固定格式或写作风格"],
                "chinese-official-writing/references/workflow.md": [
                    "只出现单位名称",
                    "不触发搜索单位公开样文、固定格式或写作风格",
                ],
                "chinese-official-writing/references/handling-elements.md": [
                    "不因出现单位名称就搜索单位公开样文、固定格式或写作风格",
                    "使用中性称谓和通用文种格式",
                ],
                "chinese-official-writing/references/review-checklist.md": ["未因单位名称自动搜索单位公开样文"],
            },
        },
    ),
    PromptCase(
        id="P034",
        kind="revise",
        prompt="我从政府网站复制了一篇关于印发《实施方案》的通知，里面有来源、字号、打印、责任编辑。请先清理网页元信息，再只改被印发方案第二部分，不要改通知壳和附件标题。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["网页元信息", "通知壳", "被印发文件正文", "附件关系"],
                "chinese-official-writing/references/workflow.md": [
                    "网页复制稿",
                    "通知壳",
                    "被印发文件正文",
                    "附件标题",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "网页元信息",
                    "通知壳",
                    "被印发文件正文",
                    "附件关系",
                ],
            },
        },
    ),
    PromptCase(
        id="P035",
        kind="revise",
        prompt="把一份很长的通知压缩到500字以内，但原文里的责任单位、办理期限、附件、联系人、反馈渠道和具体数字不能丢；多个责任主体不要压成笼统的有关单位。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": ["压缩长文", "主体、对象、数字、期限、责任、附件、联系人和反馈渠道"],
                "chinese-official-writing/references/workflow.md": [
                    "长文缩写",
                    "不可丢要素",
                    "责任单位",
                    "反馈渠道",
                    "不把明确分工压成",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "长文缩写",
                    "责任单位",
                    "反馈渠道",
                    "多主体分工",
                ],
            },
        },
    ),
    PromptCase(
        id="P036",
        kind="create",
        prompt="起草推进政务数据共享通知，政策依据、截止时间、联系人和反馈渠道都没给；不要外搜，也不要写成“指定渠道”“截止时间前”，缺项放正文外待确认。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "截止时间",
                    "反馈渠道",
                    "泛占位",
                    "指定渠道",
                    "联系人沟通",
                    "缺项说明",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "缺失事实处理提示",
                    "指定渠道",
                    "截止时间前",
                    "联系人沟通",
                    "缺项说明写进正文",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "缺项边界",
                    "正文泛占位",
                    "缺项说明位置",
                ],
            },
        },
    ),
    PromptCase(
        id="P037",
        kind="revise",
        prompt="顺一下字段式培训费用申请，只新增“报销凭证”字段但我没给字段值；不要推断发票、票据、邮箱或日期，原字段顺序不动。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "新增字段只有字段名",
                    "字段顺序",
                    "不推断",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "新增字段没有用户提供值",
                    "只写字段名",
                    "不推断发票、票据、邮箱、截止日期",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "字段值未知",
                    "未推断发票、票据、邮箱、截止日期",
                ],
            },
        },
    ),
    PromptCase(
        id="P038",
        kind="revise",
        prompt="把通知压缩到260字以内，责任单位、办理期限、附件、联系人、反馈渠道和具体数字不能丢；如果做不到要说明取舍风险。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "字数或篇幅上限",
                    "字数自检",
                    "5%-10% 余量",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "260 字",
                    "去空行后的正文计数",
                    "5%-10% 余量",
                    "取舍风险",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "去空行后的正文计数",
                    "避免静默超字数或贴线上限",
                ],
            },
        },
    ),
    PromptCase(
        id="P039",
        kind="revise",
        prompt="审一下这段是否空泛：相关问题已基本完成整改，形成长效机制，显著提升治理能力，未影响核心业务。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "抽象词和评价强度要落到证据",
                    "显著",
                    "长效",
                ],
                "chinese-official-writing/references/official-style.md": [
                    "评价强度",
                    "相关问题已基本完成整改",
                    "未影响核心业务",
                ],
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "评价强度超过证据",
                    "基本完成整改",
                    "形成长效机制",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "证据强度",
                    "显著、长效、全面、基本完成、未影响",
                ],
            },
        },
    ),
    PromptCase(
        id="P040",
        kind="create",
        prompt="用户明确要求核验现行政策后起草通知；请把来源名称、发布机关、文号或链接、发布日期、访问日期和用于哪一段放正文外。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/workflow.md": [
                    "来源名称",
                    "发布机关或发布主体",
                    "文号或链接",
                    "用于哪一处",
                    "是否已核验",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "搜索来源清单",
                    "发布机关或主体",
                    "单一网络来源",
                ],
            },
        },
    ),
    PromptCase(
        id="P041",
        kind="revise",
        prompt="用户要求正式 Word/docx 交付，但正文还没确认，文号、签发人、印章也没给；只做要素核对和另存，不借排版补写事实。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/format-gbt9704.md": [
                    "正文内容已经定稿",
                    "不要写成“已确认可作为 Word 稿基础”",
                    "默认另存新版本",
                    "不借排版补写政策依据、联系人、截止时间、签发人、文号、印章或版记",
                    "避免把缺项改写成正文泛占位",
                ],
            },
        },
    ),
    PromptCase(
        id="P042",
        kind="create",
        prompt="写一份1500字以内的专项调研报告，要求有背景现状、问题原因、措施安排和结尾落点；不要为了限字只写开头，后半篇不能草草结束。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "长篇限字稿件",
                    "篇幅预算",
                    "避免头重脚轻",
                    "草草收尾",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "长篇限字稿件先做篇幅预算",
                    "背景现状",
                    "问题原因",
                    "措施安排",
                    "结尾落点",
                    "后文草草收尾",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "长篇限字稿件",
                    "开头、主体、措施和结尾",
                    "头重脚轻",
                    "压掉措施安排",
                ],
            },
        },
    ),
    PromptCase(
        id="P043",
        kind="create",
        prompt="请先写一版资金申请请示，申请事项、金额和审批对象还没完全给；不要先问我一串问题，正文后只列关键缺口。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "事实不足不作为默认中断理由",
                    "先完成可用正文",
                    "补充以下信息后，文章会更完整",
                    "不要做调查问卷式问题清单",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "不在正文前中断成稿",
                    "不连续追问",
                    "申请事项",
                    "审批对象",
                    "关键缺口",
                    "不做调查问卷",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "未在正文前中断成稿或连续追问",
                    "补充以下信息后，文章会更完整",
                    "未做调查问卷式问题清单",
                ],
            },
        },
    ),
    PromptCase(
        id="P044",
        kind="create",
        prompt="材料不足但要写完整工作报告，底部提示可补充事实；不要把增删论点、扩写细节列成我的义务，也不要做调查问卷。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "先完整输出正式正文",
                    "事实补足建议只列影响文种功能或执行落地的关键缺口",
                    "不要把增删论点、扩写细节等写稿人可自行安排的事项转嫁给用户",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "先按用户已给材料完成正文",
                    "影响文种功能或执行落地",
                    "增加论点",
                    "删除论点",
                    "扩写细节",
                    "写稿人可安排事项",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "仍先完成正文",
                    "影响文种功能或执行落地",
                    "增删论点",
                    "扩写细节",
                    "转嫁给用户",
                ],
            },
        },
    ),
    PromptCase(
        id="P045",
        kind="revise",
        prompt="上一轮底部列了金额和联系人待确认，但我这轮还是没补；请继续把稿子压缩到500字内并调整标题顺序，不要因为我没补信息就追问或停止修改。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "后续轮次用户未补齐这些事实",
                    "继续完成本轮修改",
                    "不把上一轮待确认事项升级为阻断条件",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "后续轮次用户未补齐上一轮列出的关键缺口",
                    "仍先执行本轮修改请求",
                    "不把待确认事项变成连续追问或修改阻断",
                    "第二轮或后续修改",
                    "待确认事项仍是软提示",
                    "只在正文外保留或更新关键缺口",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "后续轮次用户未补齐事实",
                    "仍执行本轮修改",
                    "不把待确认事项升级成阻断链路",
                ],
            },
        },
    ),
    PromptCase(
        id="P046",
        kind="create",
        prompt="材料只说发现台账更新不及时和标识不清，请写检查报告；不要因为要成稿就自行写“未发现重大隐患”或“无异常”。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "材料未给风险结论",
                    "未发现重大隐患",
                    "无异常",
                    "强判断",
                    "材料只给问题清单",
                    "总体较好",
                    "能够正常开展",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "风险结论",
                    "整改结论",
                    "检查结论",
                    "影响范围",
                    "从已给材料看，问题集中于",
                    "结论口径列入正文外待确认",
                    "概括性正向判断",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "事实强判断",
                    "未发现重大隐患",
                    "无异常",
                    "已完成整改",
                    "未影响核心业务",
                    "总体较好",
                    "能够正常开展",
                ],
            },
        },
    ),
    PromptCase(
        id="P047",
        kind="create",
        prompt="先帮我写正文，后续再补文号、签发人和版记；不要因为正式 Word 要素没齐就停下追问，正文后给一个核对卡即可。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "正式交付前要素核对卡",
                    "事实不足不作为默认中断理由",
                    "核对卡优先只列这些点名要素",
                ],
                "chinese-official-writing/references/format-gbt9704.md": [
                    "正式交付前要素核对卡",
                    "不因缺这些正式要素阻断成稿",
                    "发文机关",
                    "印章或签署信息",
                    "内部模板、企业模板或用户指定格式",
                    "优先只列用户点名缺项",
                    "其他正式要素按单位模板另行核对",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "正式交付前要素核对卡",
                    "发文机关",
                    "印章或签署信息",
                    "未变成正文占位",
                    "未扩展成长清单",
                ],
            },
        },
    ),
    PromptCase(
        id="P048",
        kind="revise",
        prompt="这是最新版申请，另附旧版申请和一篇参考样文；请只按最新版改写，旧版金额、旧主送和旧政策口号不要回流。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "修改模式只以用户最新版底稿",
                    "不自动回流为正文事实",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "旧稿、参考样文、过往材料和公开网页材料",
                    "不把旧金额、旧主送、旧落款、旧政策口号或旧结论带回最新版正文",
                    "参考材料只可影响结构检查、语气尺度或缺项提示",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "修改模式是否以最新版底稿为主线",
                    "旧金额、旧主送、旧落款、旧政策口号或旧结论",
                ],
            },
        },
    ),
    PromptCase(
        id="P049",
        kind="revise",
        prompt="只审空话套话，不重写全文：各单位高度重视，扎实推进整改，持续完善机制；请给位置、风险层级和建议。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "成簇问题",
                    "不因单个正式词、单个转折或一次排比就硬清洗",
                ],
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "审稿时看成簇问题",
                    "单独出现 `高度重视`",
                    "不足以判为 AI 味或套话",
                    "位置、风险层级和修改建议",
                    "不默认重写全文",
                    "保留公文必要的正式语气",
                ],
                "chinese-official-writing/references/official-style.md": [
                    "去 AI 味或语气审稿应匹配文体",
                    "不为了显得像人写而加入第一人称",
                    "检查时看成簇问题",
                    "单个正式词或单个转折不作为硬清洗理由",
                ],
            },
        },
    ),
    PromptCase(
        id="P050",
        kind="revise",
        prompt="把这段顺成正式报告，但不要新增事实：我们检查了系统，发现日志备份不及时，后面继续盯；不要补责任部门、督办安排或处理进展。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "不得为显得完整而补造未提供的牵头部门、责任部门、管理动作、整改动作、成果总结或跟踪督办安排",
                ],
                "chinese-official-writing/references/workflow.md": [
                    "不为显得完整而补造牵头部门、责任部门、管理动作、整改动作、成果总结、跟踪督办、后续处理进展",
                    "原文未给事实",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "正式化新增事实",
                    "牵头部门、责任部门、管理动作、整改动作、成果总结、跟踪督办、后续处理进展",
                ],
                "chinese-official-writing/references/official-style.md": [
                    "正式化改写只压实原文已有事实",
                    "不要为了让句子更正式而补入原文没有的组织名称",
                ],
            },
        },
    ),
    PromptCase(
        id="P051",
        kind="revise",
        prompt="只审空话套话，不重写全文；必须标明每处具体位置，不要只给整段整体评价。",
        checks={
            "file_terms": {
                "chinese-official-writing/SKILL.md": [
                    "用户要求“位置”时，优先逐项引用原文短语或句子",
                ],
                "chinese-official-writing/references/review-checklist.md": [
                    "优先逐项引用原文短语或句子",
                    "未只给笼统段落评价",
                ],
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "先逐项引用原文短语或句子",
                    "整体归纳可放在逐项意见之后",
                ],
            },
        },
    ),
    PromptCase(
        id="P052",
        kind="revise",
        prompt="只审 AI 味，不重写全文：首先要高度重视，其次要持续推进，最后要形成闭环。请看句式是不是太模板化。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "句群节奏和模板化痕迹",
                    "句首重复",
                    "连接词链",
                    "用户只要求审稿时，仍输出位置、风险层级和修改建议",
                ],
            },
        },
    ),
    PromptCase(
        id="P053",
        kind="revise",
        prompt="帮我把这段去模板化，但仍然是正式报告语气；不要改成公众号口吻，不要加“我觉得”“说白了”或反问。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "公文去 AI 味不是聊天化",
                    "不得为了显得“像人写”而加入第一人称、反问、口语插入",
                    "保留公文骨架和用户模板",
                ],
                "chinese-official-writing/references/official-style.md": [
                    "不为了显得像人写而加入第一人称",
                    "正式化改写只压实原文已有事实",
                ],
            },
        },
    ),
    PromptCase(
        id="P054",
        kind="revise",
        prompt="审一下这段结尾是不是空：为工作开展提供有力支撑，为后续推进奠定坚实基础，推动工作再上新台阶。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "口号式收束",
                    "提供有力支撑",
                    "推动再上新台阶",
                    "将口号式收束改为具体办理动作、责任时限、反馈渠道或审慎结论",
                ],
            },
        },
    ),
    PromptCase(
        id="P055",
        kind="revise",
        prompt="借鉴社区公文 skill 的检查层，但不要新增脚本或硬门禁。把“老板关心、钱花得值、马上要搞”顺成正式表达时，不要升级事实，也不要覆盖用户模板。",
        checks={
            "file_terms": {
                "chinese-official-writing/references/review-checklist.md": [
                    "定稿前高风险先查",
                    "其余按文种/风险面",
                    "不把它改成新的阻断流程",
                ],
                "chinese-official-writing/references/official-style.md": [
                    "口语来源不等于事实授权",
                    "老板关心",
                    "领导高度关注",
                    "不得自动升级",
                    "审批态度留给用户确认",
                ],
                "chinese-official-writing/references/anti-ai-patterns.md": [
                    "需说明资金使用必要性和预期效果",
                    "相关负责人关注该事项",
                    "不要无依据升级为 `领导高度关注`",
                ],
                "chinese-official-writing/references/genre-checklist.md": [
                    "可参考顺序",
                    "不写成正文标签",
                    "不覆盖用户模板",
                    "## 函\n",
                ],
            },
        },
    ),
]


def read_text(root: Path, relative: str) -> str:
    path = root / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_description(skill_text: str) -> str:
    match = re.search(r"^description:\s*(.+)$", skill_text, re.M)
    return match.group(1) if match else ""


def has_table_row(text: str, row_name: str) -> bool:
    return re.search(rf"^\| {re.escape(row_name)} \|", text, re.M) is not None


HEADING_RE = re.compile(
    r"^\s*(?:#{1,6}\s+)?"
    r"((?:[一二三四五六七八九十]+、|[（(][一二三四五六七八九十]+[）)]|[0-9]+[.、])\s*[^\n#]+?)"
    r"\s*(?:#+\s*)?$",
    re.M,
)


def numbered_headings(text: str) -> list[str]:
    return [match.group(1).strip() for match in HEADING_RE.finditer(text)]


def load_prose_lint(root: Path, label: str):
    path = root / "chinese-official-writing" / "scripts" / "prose_lint.py"
    spec = importlib.util.spec_from_file_location(f"real_prompt_prose_lint_{label}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def evaluate_case(case: PromptCase, root: Path, prose_lint) -> dict[str, Any]:
    skill_text = read_text(root, "chinese-official-writing/SKILL.md")
    description = extract_description(skill_text)
    routing = read_text(root, "chinese-official-writing/references/genre-routing.md")
    checklist = read_text(root, "chinese-official-writing/references/genre-checklist.md")
    elements = read_text(root, "chinese-official-writing/references/handling-elements.md")
    review_checklist = read_text(root, "chinese-official-writing/references/review-checklist.md")

    failures: list[str] = []
    checks = case.checks

    for term in checks.get("description_terms", []):
        if term not in description:
            failures.append(f"description missing {term}")
    for term in checks.get("routing_terms", []):
        if term not in routing:
            failures.append(f"routing missing {term}")
    for section in checks.get("checklist_sections", []):
        if f"## {section}" not in checklist:
            failures.append(f"checklist missing {section}")
    for row in checks.get("handling_rows", []):
        if not has_table_row(elements, row):
            failures.append(f"handling-elements missing {row}")
    for term in checks.get("review_checklist_terms", []):
        if term not in review_checklist:
            failures.append(f"review-checklist missing {term}")
    for relative, terms in checks.get("file_terms", {}).items():
        file_text = read_text(root, relative)
        for term in terms:
            if term not in file_text:
                failures.append(f"{relative} missing {term}")

    heading_lock = checks.get("heading_lock")
    if heading_lock:
        before = numbered_headings(heading_lock["before"])
        after = numbered_headings(heading_lock["after"])
        if before != after:
            failures.append(f"heading list changed: before={before}; after={after}")

    lint_text = checks.get("lint_text")
    lint_labels: list[str] = []
    if lint_text:
        findings = prose_lint.scan(f"{case.id}:{case.kind}", lint_text, include_format=True, include_structure=True)
        lint_labels = sorted({item.label for item in findings})
        for label in checks.get("lint_present_labels", []):
            if label not in lint_labels:
                failures.append(f"lint missing {label}")
        for label in checks.get("lint_absent_labels", []):
            if label in lint_labels:
                failures.append(f"lint false-positive {label}")

    return {
        "id": case.id,
        "kind": case.kind,
        "prompt": case.prompt,
        "passed": not failures,
        "failures": failures,
        "lint_labels": lint_labels,
    }


def evaluate_root(root: Path, label: str) -> list[dict[str, Any]]:
    prose_lint = load_prose_lint(root, re.sub(r"\W+", "_", label))
    return [evaluate_case(case, root, prose_lint) for case in CASES]


def root_validation_error(root: Path, label: str) -> str | None:
    required = [
        "chinese-official-writing/SKILL.md",
        "chinese-official-writing/scripts/prose_lint.py",
    ]
    if not root.exists():
        return (
            f"{label} 目录不存在：{root}。请先用 git worktree add --detach <基线目录> <tag或commit> "
            "或 checkout 对应发行版本准备基线目录。"
        )
    missing = [relative for relative in required if not (root / relative).exists()]
    if missing:
        return (
            f"{label} 目录不完整：{root}，缺少 {', '.join(missing)}。请确认传入的是仓库根目录，"
            "或用 git worktree add --detach 准备完整基线目录。"
        )
    return None


def write_summary(out_dir: Path, results: dict[str, list[dict[str, Any]]]) -> None:
    lines = [
        "# 真实用户 Prompt 消融测试摘要",
        "",
        "本测试不调用 LLM，而是用真实用户式起草/改稿 prompt 检查 Skill 包是否具备触发、文种路由、办理要素、清单和 lint 行为支撑。",
        "",
        "| 基线 | 用例数 | 通过 | 失败 | 起草失败 | 改稿失败 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, rows in results.items():
        failures = [row for row in rows if not row["passed"]]
        create_failures = [row for row in failures if row["kind"] == "create"]
        revise_failures = [row for row in failures if row["kind"] == "revise"]
        lines.append(
            f"| {label} | {len(rows)} | {len(rows) - len(failures)} | {len(failures)} | "
            f"{len(create_failures)} | {len(revise_failures)} |"
        )
    lines.extend(
        [
            "",
            "## 用例结果",
            "",
            "| 基线 | 用例 | 类型 | 结果 | 失败原因 | Prompt |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for label, rows in results.items():
        for row in rows:
            failures = "; ".join(row["failures"]) if row["failures"] else "无"
            prompt = row["prompt"].replace("|", "｜")
            result = "通过" if row["passed"] else "失败"
            lines.append(f"| {label} | {row['id']} | {row['kind']} | {result} | {failures} | {prompt} |")
    lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def exit_code_for_results(results: dict[str, list[dict[str, Any]]], _baseline_label: str) -> int:
    """Fail the release gate only when the current package fails."""
    current_failures = sum(1 for row in results["current"] if not row["passed"])
    return 1 if current_failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--current-root", default=".")
    parser.add_argument("--out", default="output/real-prompt-ablation")
    args = parser.parse_args()

    baseline_root = Path(args.baseline_root).resolve()
    current_root = Path(args.current_root).resolve()
    baseline_label = args.baseline_label
    for label, root in [(baseline_label, baseline_root), ("current", current_root)]:
        error = root_validation_error(root, label)
        if error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 2

    results = {
        baseline_label: evaluate_root(baseline_root, baseline_label),
        "current": evaluate_root(current_root, "current"),
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary(out_dir, results)
    print((out_dir / "summary.md").as_posix())
    return exit_code_for_results(results, baseline_label)


if __name__ == "__main__":
    raise SystemExit(main())
