#!/usr/bin/env python3
"""Run read-only multi-round revision-instruction checks.

This eval targets real usage failures that appear after a draft already exists:
removing or adding natural paragraphs, changing titles or subheadings, changing
outline shape, deleting or adding key points, reordering paragraphs, and changing
sender or recipient. The script records issues only; it never patches Skill
files or rewrites output.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
import textwrap
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "output" / "revision-instruction-eval"

INSTRUCTION_LEAK = re.compile(
    r"按(?:照)?你(?:的)?要求|根据你(?:的)?要求|已(?:删除|增加|调整|修改)|这版|上一版|修改如下|以下为|作为AI|我是AI"
)
APPROVAL_REQUEST = re.compile(
    r"妥否|请批示|请予(?:批复|审查|审定|批准)|申请批准|请求批准|提请批复|恳请(?:批准|审定)"
)
REPORT_OPENING = re.compile(r"现将[^。\n]{0,40}报告如下|有关情况报告如下|报告如下")
DATE_LINE = re.compile(r"^\s*\d{4}年\d{1,2}月\d{1,2}日\s*$", re.M)


@dataclass
class Turn:
    id: str
    operation: str
    instruction: str
    checks: dict[str, Any]


@dataclass
class Case:
    id: str
    genre: str
    title: str
    initial: str
    turns: list[Turn] = field(default_factory=list)


def _turn(id_: str, operation: str, instruction: str, **checks: Any) -> Turn:
    return Turn(id_, operation, instruction, checks)


CASES: list[Case] = [
    Case(
        id="R001",
        genre="通知",
        title="关于报送季度项目资料的通知",
        initial="""关于报送季度项目资料的通知

各有关单位：
为做好季度项目资料归集工作，请各单位按要求报送项目进展、资金使用、风险问题和佐证材料。

一、报送范围
本次报送范围包括在建项目、已完成待验收项目和需协调推进的重点项目。

二、材料要求
报送材料应包括项目台账、进展说明、问题清单和下一步安排，确保内容真实、口径一致。

三、工作要求
各单位要高度重视，指定专人负责材料核验和报送工作，逾期未报的应说明原因。

综合管理部
2026年6月1日""",
        turns=[
            _turn(
                "R001-T1",
                "remove_natural_paragraph",
                "删除第三段关于工作要求的自然段，不要改标题和主送对象。",
                title="关于报送季度项目资料的通知",
                recipient="各有关单位",
                absent=["三、工作要求", "高度重视", "逾期未报"],
                present=["报送范围", "材料要求"],
            ),
            _turn(
                "R001-T2",
                "add_natural_paragraph",
                "在材料要求后增加一个自然段，说明反馈渠道和联系人，不要新增小标题。",
                title="关于报送季度项目资料的通知",
                recipient="各有关单位",
                present=["反馈渠道", "联系人"],
                absent=["四、", "反馈渠道和联系人："],
                min_paragraphs=3,
            ),
            _turn(
                "R001-T3",
                "change_sender_receiver",
                "主送对象改为各项目单位，发送人改为综合协调处，其他结构保持不变。",
                title="关于报送季度项目资料的通知",
                recipient="各项目单位",
                sender="综合协调处",
                absent=["各有关单位", "综合管理部"],
            ),
        ],
    ),
    Case(
        id="R002",
        genre="请示",
        title="关于启动智能审校系统试点建设的请示",
        initial="""关于启动智能审校系统试点建设的请示

市发展改革委：
为提升长文审校和正式材料处理效率，拟启动智能审校系统试点建设。

一、项目背景
现有人工审校流程存在周期较长、标准不一和批量处理能力不足等问题。

二、建设内容
项目拟建设文本审校、知识库检索、多轮修改和归档管理等功能。

三、资金安排
项目资金拟按年度预算统筹安排，具体金额待测算后报审。

妥否，请批示。

信息化建设中心
2026年6月1日""",
        turns=[
            _turn(
                "R002-T1",
                "change_title",
                "标题改为“关于申请启动智能审校系统试点建设的请示”，正文请批语保留。",
                title="关于申请启动智能审校系统试点建设的请示",
                present=["妥否，请批示"],
                recipient="市发展改革委",
            ),
            _turn(
                "R002-T2",
                "delete_add_points",
                "删除资金安排要点，新增风险控制要点，不要把请示写成报告。",
                present=["风险控制", "妥否，请批示"],
                absent=["资金安排", "报告如下"],
                headings_in_order=["一、项目背景", "二、建设内容", "三、风险控制"],
            ),
            _turn(
                "R002-T3",
                "change_sender_receiver",
                "主送机关改为市政务服务和数据管理局，发文单位改为市信息化建设中心。",
                recipient="市政务服务和数据管理局",
                sender="市信息化建设中心",
                present=["妥否，请批示"],
                absent=["市发展改革委："],
            ),
        ],
    ),
    Case(
        id="R003",
        genre="报告",
        title="关于专项整改工作进展情况的报告",
        initial="""关于专项整改工作进展情况的报告

市政府办公室：
现将专项整改工作进展情况报告如下。

一、整改进展
已完成问题台账梳理、责任分工和阶段性复核，重点事项按计划推进。

二、存在问题
部分单位佐证材料不完整，个别事项整改口径还需进一步统一。

三、下一步工作
将继续完善台账管理，按节点组织复核，并及时报送整改结果。

专项整改工作专班
2026年6月1日""",
        turns=[
            _turn(
                "R003-T1",
                "reorder_paragraphs",
                "把“存在问题”调整到“整改进展”前面，“下一步工作”仍放最后。",
                title="关于专项整改工作进展情况的报告",
                headings_in_order=["一、存在问题", "二、整改进展", "三、下一步工作"],
                ordered=["存在问题", "整改进展", "下一步工作"],
                absent=["请批示", "请予批复"],
            ),
            _turn(
                "R003-T2",
                "add_natural_paragraph",
                "在存在问题后增加一个原因分析自然段，不要改标题。",
                title="关于专项整改工作进展情况的报告",
                present=["原因分析"],
                absent=["请批示", "请予批复"],
                min_paragraphs=5,
            ),
            _turn(
                "R003-T3",
                "change_title_receiver",
                "标题改为“关于专项整改工作进展情况的报告（修订稿）”，主送改为市政府督查室。",
                title="关于专项整改工作进展情况的报告（修订稿）",
                recipient="市政府督查室",
                absent=["市政府办公室：", "请批示", "请予批复"],
            ),
        ],
    ),
    Case(
        id="R004",
        genre="会议纪要",
        title="项目推进协调会议纪要",
        initial="""项目推进协调会议纪要

会议时间：2026年6月1日
会议地点：第三会议室
参会人员：有关部门负责同志

一、会议听取了项目进展情况
会议听取牵头部门关于系统联调、材料准备和风险事项的汇报。

二、会议议定了协同事项
会议明确由业务部门负责需求确认，由技术部门负责接口联调，由综合部门负责资料归档。

三、会议要求加强宣传推广
会议要求同步做好宣传推广，及时总结阶段性成果，形成示范经验。

会议强调，各责任单位应按节点落实任务，重要问题及时报牵头部门协调。
""",
        turns=[
            _turn(
                "R004-T1",
                "change_subheading_outline",
                "把三个小标题改为“一、关于任务分工”“二、关于节点安排”“三、关于后续督办”。",
                title="项目推进协调会议纪要",
                headings_in_order=["一、关于任务分工", "二、关于节点安排", "三、关于后续督办"],
                absent=["会议听取了项目进展情况", "会议议定了协同事项", "会议要求加强宣传推广"],
            ),
            _turn(
                "R004-T2",
                "remove_natural_paragraph",
                "删除关于宣传推广的自然段，会议议定事项和督办要求保留。",
                absent=["宣传推广", "示范经验"],
                present=["会议明确", "督办"],
            ),
            _turn(
                "R004-T3",
                "add_natural_paragraph",
                "增加一个自然段，明确由办公室牵头汇总问题清单并每周反馈。",
                present=["办公室", "问题清单", "每周反馈"],
            ),
        ],
    ),
    Case(
        id="R005",
        genre="实施方案",
        title="数据治理专项实施方案",
        initial="""数据治理专项实施方案

为提升数据治理能力，制定本实施方案。

一、总体要求
坚持问题导向、分步实施、闭环管理，提升数据质量和应用支撑能力。

二、重点任务
开展数据目录梳理、数据质量核验、宣传培训和共享应用评估。

三、实施步骤
准备阶段完成台账梳理，实施阶段推进整改，验收阶段形成成果报告。

四、保障措施
建立协调机制，明确责任分工，强化督办检查和结果运用。
""",
        turns=[
            _turn(
                "R005-T1",
                "outline_change",
                "提纲改为“一、目标任务”“二、阶段安排”“三、责任分工”“四、验收要求”。",
                title="数据治理专项实施方案",
                headings_in_order=["一、目标任务", "二、阶段安排", "三、责任分工", "四、验收要求"],
                absent=["总体要求", "重点任务", "实施步骤", "保障措施"],
            ),
            _turn(
                "R005-T2",
                "delete_add_points",
                "删除宣传培训要点，增加数据安全和验收归档两个要点。",
                present=["数据安全", "验收归档"],
                absent=["宣传培训"],
                headings_in_order=["一、目标任务", "二、阶段安排", "三、责任分工", "四、验收要求"],
            ),
            _turn(
                "R005-T3",
                "remove_natural_paragraph",
                "去掉开头说明性自然段，直接从第一个小标题开始。",
                starts_with="数据治理专项实施方案",
                absent=["为提升数据治理能力，制定本实施方案"],
                headings_in_order=["一、目标任务", "二、阶段安排", "三、责任分工", "四、验收要求"],
            ),
        ],
    ),
    Case(
        id="R006",
        genre="函",
        title="关于商请提供系统联调接口信息的函",
        initial="""关于商请提供系统联调接口信息的函

市大数据中心：
为推进政务服务系统联调工作，现商请贵单位协助提供系统联调接口信息。

一、协助事项
请提供接口清单、数据口径、联调联系人和测试环境开放安排。

二、反馈要求
请于近期反馈相关材料，便于我局统筹安排联调计划。

区行政审批局
2026年6月1日""",
        turns=[
            _turn(
                "R006-T1",
                "change_sender_receiver",
                "收文单位改为市信息中心，发文单位改为区数据资源管理局。",
                recipient="市信息中心",
                sender="区数据资源管理局",
                absent=["市大数据中心：", "区行政审批局"],
            ),
            _turn(
                "R006-T2",
                "change_title",
                "标题改为“关于商请协助开展政务服务系统联调的函”。",
                title="关于商请协助开展政务服务系统联调的函",
                recipient="市信息中心",
                sender="区数据资源管理局",
            ),
            _turn(
                "R006-T3",
                "delete_add_points",
                "删除“提供接口清单”这个要点，新增联调窗口期和安全责任两个要点。",
                present=["联调窗口期", "安全责任"],
                absent=["提供接口清单"],
                recipient="市信息中心",
                sender="区数据资源管理局",
            ),
        ],
    ),
    Case(
        id="R007",
        genre="请示",
        title="关于解决政务大厅设备更新经费的请示",
        initial="""关于解决政务大厅设备更新经费的请示

市政府：
为保障政务大厅窗口服务稳定运行，拟对老旧叫号屏、自助终端和网络配套设备进行更新。

一、基本情况
现有部分设备已连续使用多年，运行不稳定，影响群众取号、查询和材料打印等服务。

二、更新内容
拟更新叫号屏、自助终端和网络交换设备，并同步完成安装调试。

三、经费测算
经初步测算，设备更新和安装调试费用约80万元，拟按年度预算统筹安排。

四、请批事项
恳请同意启动设备更新工作，并按程序安排相关经费。

妥否，请批示。

区政务服务中心
2026年6月1日""",
        turns=[
            _turn(
                "R007-T1",
                "recipient_position",
                "主送机关改为市财政局。保持正式请示格式，标题必须仍在第一行。",
                title="关于解决政务大厅设备更新经费的请示",
                recipient="市财政局",
                absent=["市政府："],
                recipient_after_title=True,
                closing_before_signature=["妥否，请批示"],
                no_approval_after_signature=True,
            ),
            _turn(
                "R007-T2",
                "closing_position",
                "将请批语改为“以上请示，请予审定。”，该请批语必须作为正文最后一个自然段，落款和日期仍在其后。",
                title="关于解决政务大厅设备更新经费的请示",
                recipient="市财政局",
                present=["以上请示，请予审定"],
                absent=["妥否，请批示"],
                closing_before_signature=["以上请示，请予审定"],
                no_approval_after_signature=True,
            ),
            _turn(
                "R007-T3",
                "delete_add_points",
                "删除“四、请批事项”这个小标题，把请批事项并入正文最后一段，不改变请示文种。",
                title="关于解决政务大厅设备更新经费的请示",
                recipient="市财政局",
                present=["请予审定"],
                absent=["四、请批事项", "报告如下"],
                closing_before_signature=["请予审定"],
                no_approval_after_signature=True,
            ),
        ],
    ),
    Case(
        id="R008",
        genre="申请",
        title="办公设备购置经费申请",
        initial="""办公设备购置经费申请

尊敬的领导：
为保障综合服务窗口日常运行，拟申请购置打印机、扫描仪和配套耗材。

一、申请事项
申请安排办公设备购置经费18万元，用于补充综合服务窗口设备。

二、使用计划
经费主要用于购置打印机、扫描仪、耗材和设备安装调试服务。

三、工作承诺
资金到位后，将严格按采购程序实施，并做好资产登记和验收归档。

恳请予以支持。

综合服务中心
2026年6月1日""",
        turns=[
            _turn(
                "R008-T1",
                "recipient_position",
                "改成正式上报版，接收方为公司领导班子；标题仍放第一行，称呼按上报申请语境处理。",
                title="办公设备购置经费申请",
                recipient="公司领导班子",
                recipient_after_title=True,
                closing_before_signature_any=["恳请予以支持", "妥否，请批示"],
            ),
            _turn(
                "R008-T2",
                "closing_position",
                "将结尾改为“以上申请，恳请批准。”，结尾必须放在落款和日期之前。",
                title="办公设备购置经费申请",
                recipient="公司领导班子",
                present=["以上申请，恳请批准"],
                absent=["恳请予以支持"],
                closing_before_signature=["以上申请，恳请批准"],
            ),
            _turn(
                "R008-T3",
                "change_sender_receiver",
                "发文单位改为运营管理部，接收方改为总经理办公会，并增加一个资金用途自然段。",
                title="办公设备购置经费申请",
                recipient="总经理办公会",
                sender="运营管理部",
                present=["资金用途", "以上申请，恳请批准"],
                absent=["公司领导班子：", "综合服务中心"],
                closing_before_signature=["以上申请，恳请批准"],
            ),
        ],
    ),
    Case(
        id="R009",
        genre="报告",
        title="关于安全隐患排查整改情况的报告",
        initial="""关于安全隐患排查整改情况的报告

市应急管理局：
现将安全隐患排查整改情况报告如下。

一、排查情况
已完成重点场所、重点设备和重点岗位排查，形成问题台账并明确整改责任。

二、整改进展
一般隐患已完成整改，需持续跟踪的事项已纳入月度调度。

三、下一步工作
将继续开展复查复核，完善安全巡查机制，按要求报送整改结果。

特此报告。

新区建设管理局
2026年6月1日""",
        turns=[
            _turn(
                "R009-T1",
                "recipient_position",
                "主送机关改为市政府办公室。保持报告格式，不要增加请批语。",
                title="关于安全隐患排查整改情况的报告",
                recipient="市政府办公室",
                absent=["市应急管理局：", "妥否", "请批示"],
                recipient_after_title=True,
                closing_before_signature=["特此报告"],
                no_approval_after_signature=True,
            ),
            _turn(
                "R009-T2",
                "closing_position",
                "把结尾改为“以上情况，特此报告。”，必须放在落款和日期之前。",
                title="关于安全隐患排查整改情况的报告",
                recipient="市政府办公室",
                present=["以上情况，特此报告"],
                absent=["妥否", "请批示"],
                closing_before_signature=["以上情况，特此报告"],
                no_approval_after_signature=True,
            ),
            _turn(
                "R009-T3",
                "add_natural_paragraph",
                "在整改进展后增加一个原因分析自然段，标题改为“关于安全隐患排查整改情况的报告（修订稿）”。",
                title="关于安全隐患排查整改情况的报告（修订稿）",
                recipient="市政府办公室",
                present=["原因分析", "以上情况，特此报告"],
                absent=["妥否", "请批示"],
                closing_before_signature=["以上情况，特此报告"],
                min_paragraphs=5,
            ),
        ],
    ),
    Case(
        id="R010",
        genre="函",
        title="关于商请协助提供档案移交资料的函",
        initial="""关于商请协助提供档案移交资料的函

市档案馆：
为做好政务服务事项档案移交工作，现商请贵馆协助提供档案移交资料清单和办理要求。

一、协助事项
请协助提供资料清单、归档标准和移交流程说明。

二、反馈要求
请于近期反馈相关材料，便于我局组织窗口单位做好移交准备。

专此函达。

区行政审批局
2026年6月1日""",
        turns=[
            _turn(
                "R010-T1",
                "recipient_position",
                "收文单位改为市机关事务管理局。保持函的格式。",
                title="关于商请协助提供档案移交资料的函",
                recipient="市机关事务管理局",
                absent=["市档案馆："],
                recipient_after_title=True,
                closing_before_signature=["专此函达"],
            ),
            _turn(
                "R010-T2",
                "closing_position",
                "把结尾改为“请予支持为盼。”，该结尾应在落款和日期之前，不要写“妥否，请批示”。",
                title="关于商请协助提供档案移交资料的函",
                recipient="市机关事务管理局",
                present=["请予支持为盼"],
                absent=["专此函达", "妥否", "请批示"],
                closing_before_signature=["请予支持为盼"],
                no_approval_after_signature=True,
            ),
            _turn(
                "R010-T3",
                "add_natural_paragraph",
                "在反馈要求后增加一个自然段，写明联系人和反馈期限，不要新增小标题。",
                title="关于商请协助提供档案移交资料的函",
                recipient="市机关事务管理局",
                present=["联系人", "反馈期限", "请予支持为盼"],
                absent=["三、", "联系人和反馈期限：", "妥否", "请批示"],
                closing_before_signature=["请予支持为盼"],
            ),
        ],
    ),
    Case(
        id="R011",
        genre="申请",
        title="示例科技有限公司\n软件采购申请",
        initial="""示例科技有限公司
软件采购申请

尊敬的领导：
为进一步提升公司办公效率，保障文档编辑、排版及协同办公工作的顺利开展，现拟为相关岗位采购办公软件会员一年期授权。

本次采购具体情况如下：
办公软件会员一年期授权：6套
单价：198元/套
合计费用：1188元

上述费用为软件订阅费用，授权周期为一年。采购完成后将统一分配至相关岗位使用，以满足日常办公及文件处理需求。

妥否，请领导批示。

技术应用部
2026年3月13日""",
        turns=[
            _turn(
                "R011-T1",
                "preserve_real_application_template",
                "保留公司名称和“软件采购申请”两行标题，称呼仍为“尊敬的领导：”，在采购明细后新增一个自然段说明授权使用范围，结尾语和落款日期保持不变。",
                title="示例科技有限公司\n软件采购申请",
                present=["尊敬的领导", "授权使用范围", "妥否，请领导批示"],
                closing_before_signature=["妥否，请领导批示"],
            ),
            _turn(
                "R011-T2",
                "field_value_change",
                "把采购数量改为8套，合计费用改为1584元，保留明细字段式写法，不要改成表格或编号清单。",
                title="示例科技有限公司\n软件采购申请",
                present=["8套", "1584元", "单价", "合计费用", "妥否，请领导批示"],
                absent=["6套", "1188元", "一、", "1."],
                closing_before_signature=["妥否，请领导批示"],
            ),
            _turn(
                "R011-T3",
                "change_sender_date",
                "落款部门改为综合管理部，日期改为2026年3月18日；称呼、两行标题和请批结尾不变。",
                title="示例科技有限公司\n软件采购申请",
                sender="综合管理部",
                present=["尊敬的领导", "妥否，请领导批示", "2026年3月18日"],
                absent=["技术应用部", "2026年3月13日"],
                closing_before_signature=["妥否，请领导批示"],
            ),
        ],
    ),
]


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def title_block_lines(text: str) -> list[str]:
    lines = nonempty_lines(text)
    block: list[str] = []
    for index, line in enumerate(lines[:3]):
        if index > 0 and line.endswith(("：", ":")):
            break
        if index > 0 and re.match(r"^[一二三四五六七八九十]+、", line):
            break
        if index > 0 and re.search(r"[。；！？]$", line):
            break
        if index > 0 and re.match(r"^(会议时间|会议地点|参会人员)[:：]", line):
            break
        if index > 0 and len(line) > 40:
            break
        block.append(line)
    return block


def title_block_text(text: str) -> str:
    return "\n".join(title_block_lines(text))


def title_block_end_index(text: str) -> int:
    return max(0, len(title_block_lines(text)) - 1)


def body_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    for item in nonempty_lines(text):
        if not item:
            continue
        if item == first_nonempty_line(text):
            continue
        if re.match(r"^.{0,30}[:：]$", item):
            continue
        if re.match(r"^[一二三四五六七八九十]+、", item):
            continue
        if re.match(r"^（[一二三四五六七八九十]+）", item):
            continue
        if re.search(r"^\d{4}年\d{1,2}月\d{1,2}日$", item):
            continue
        if re.match(r"^(会议时间|会议地点|参会人员)[:：]", item):
            continue
        if len(item) <= 24 and not item.endswith(("。", "；", "！", "？")):
            continue
        paragraphs.append(item)
    return paragraphs


def nonempty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def semantic_term_present(term: str, text: str) -> bool:
    normalized = compact(text)
    compact_term = compact(term)
    if compact_term in normalized:
        return True
    if term == "反馈渠道":
        return bool(
            re.search(r"反馈[^。\n]{0,30}(渠道|接收|提交|报送|补充)", text)
            or re.search(r"(通过|经由)[^。\n]{0,30}渠道[^。\n]{0,30}反馈", text)
            or re.search(r"统一接收[^。\n]{0,30}反馈", text)
            or re.search(r"反馈[^。\n]{0,30}(联系人|对接|联系电话|电话)", text)
            or re.search(r"通过[^。\n]{0,30}(联系人|联系电话|电话)[^。\n]{0,30}(对接|反馈)", text)
        )
    if term == "原因分析":
        return bool(re.search(r"原因分析|经分析|主要原因|原因是|主要是|主要由于|主要源于|上述问题[^。\n]{0,20}由于|受[^。\n]{0,20}影响", text))
    if term == "每周反馈":
        return bool(re.search(r"每周[^。\n]{0,20}反馈|按周[^。\n]{0,20}反馈", text))
    if term == "反馈期限":
        return bool(re.search(r"(请于|于|在)[^。\n]{0,30}(前|内)[^。\n]{0,20}反馈|反馈[^。\n]{0,20}(期限|时间|时限)", text))
    if term == "授权使用范围":
        return bool(re.search(r"授权[^。\n]{0,30}(用于|使用|分配)|主要用于[^。\n]{0,60}(岗位|场景|工作|用途)", text))
    return False


def has_recipient_line(text: str) -> bool:
    lines = nonempty_lines(text)
    for line in lines[1:5]:
        if line.endswith(("：", ":")) and not re.match(r"^[一二三四五六七八九十]+、", line):
            return True
    return False


def has_sender_before_date(text: str) -> bool:
    lines = nonempty_lines(text)
    for index, line in enumerate(lines):
        if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", line):
            return index > 0 and bool(lines[index - 1]) and not lines[index - 1].endswith(("。", "：", ":"))
    return False


def numbered_heading_count(text: str) -> int:
    return sum(1 for line in nonempty_lines(text) if re.match(r"^[一二三四五六七八九十]+、", line))


def position_or_none(text: str, term: str) -> int | None:
    index = compact(text).find(compact(term))
    return index if index >= 0 else None


def line_index_containing(text: str, term: str) -> int | None:
    wanted = compact(term)
    for index, line in enumerate(nonempty_lines(text)):
        if wanted in compact(line):
            return index
    return None


def first_date_line_index(text: str) -> int | None:
    for index, line in enumerate(nonempty_lines(text)):
        if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", line):
            return index
    return None


def signature_line_index(text: str) -> int | None:
    lines = nonempty_lines(text)
    date_index = first_date_line_index(text)
    if date_index is None or date_index == 0:
        return None
    candidate = lines[date_index - 1]
    if candidate.endswith(("。", "；", "，", "：", ":", "！", "？")):
        return None
    return date_index - 1


def approval_after_signature(text: str) -> bool:
    lines = nonempty_lines(text)
    signature_index = signature_line_index(text)
    date_index = first_date_line_index(text)
    boundary = signature_index if signature_index is not None else date_index
    if boundary is None:
        return False
    for index, line in enumerate(lines):
        if index > boundary and APPROVAL_REQUEST.search(line):
            return True
    return False


def parse_sections(text: str, case_id: str) -> dict[str, str]:
    pattern = re.compile(rf"^\s*###\s*({re.escape(case_id)}-T\d+)\s*$", re.M)
    matches = list(pattern.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[start:end].strip()
    return sections


def genre_format_issues(output: str, case: Case) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    title = title_block_text(output)
    normalized = compact(output)

    def add(label: str, detail: str) -> None:
        issues.append({"label": label, "detail": detail})

    if case.genre == "通知":
        if "通知" not in title:
            add("genre_format_broken", "通知标题未保留通知文种。")
        if not has_recipient_line(output):
            add("genre_format_broken", "通知缺少主送对象行。")
        if APPROVAL_REQUEST.search(output) or "报告如下" in normalized:
            add("genre_function_mixed", "通知混入请批或报告功能。")
        if not DATE_LINE.search(output) or not has_sender_before_date(output):
            add("genre_format_broken", "通知落款或日期格式缺失。")
    elif case.genre == "请示":
        if "请示" not in title:
            add("genre_format_broken", "请示标题未保留请示文种。")
        if not has_recipient_line(output):
            add("genre_format_broken", "请示缺少主送机关行。")
        if not APPROVAL_REQUEST.search(output):
            add("genre_format_broken", "请示缺少请批语。")
        if REPORT_OPENING.search(output):
            add("genre_function_mixed", "请示被改成报告式开头。")
        if not DATE_LINE.search(output) or not has_sender_before_date(output):
            add("genre_format_broken", "请示落款或日期格式缺失。")
    elif case.genre == "报告":
        if "报告" not in title:
            add("genre_format_broken", "报告标题未保留报告文种。")
        if not has_recipient_line(output):
            add("genre_format_broken", "报告缺少主送机关行。")
        if not REPORT_OPENING.search(output):
            add("genre_format_broken", "报告缺少报告式开头。")
        if APPROVAL_REQUEST.search(output):
            add("genre_function_mixed", "报告混入请示请批语。")
        if not DATE_LINE.search(output) or not has_sender_before_date(output):
            add("genre_format_broken", "报告落款或日期格式缺失。")
    elif case.genre == "申请":
        if "申请" not in title:
            add("genre_format_broken", "申请标题未保留申请文种。")
        if not has_recipient_line(output):
            add("genre_format_broken", "申请缺少接收对象行。")
        if not re.search(r"申请|恳请|请予|支持|批准", output):
            add("genre_format_broken", "申请缺少申请事项或请求语。")
        if REPORT_OPENING.search(output):
            add("genre_function_mixed", "申请被改成报告式开头。")
        if not DATE_LINE.search(output) or not has_sender_before_date(output):
            add("genre_format_broken", "申请落款或日期格式缺失。")
    elif case.genre == "会议纪要":
        if "纪要" not in title:
            add("genre_format_broken", "会议纪要标题未保留纪要文种。")
        for term in ("会议时间", "会议地点", "参会人员"):
            if term not in normalized:
                add("genre_format_broken", f"会议纪要缺少固定要素：{term}")
        if numbered_heading_count(output) < 2:
            add("genre_format_broken", "会议纪要议定事项层级不足。")
        if APPROVAL_REQUEST.search(output):
            add("genre_function_mixed", "会议纪要混入请批语。")
    elif case.genre == "实施方案":
        if "方案" not in title:
            add("genre_format_broken", "实施方案标题未保留方案文种。")
        if numbered_heading_count(output) < 3:
            add("genre_format_broken", "实施方案小标题层级不足。")
        if APPROVAL_REQUEST.search(output):
            add("genre_function_mixed", "实施方案混入请批语。")
    elif case.genre == "函":
        if "函" not in title:
            add("genre_format_broken", "函标题未保留函件文种。")
        if not has_recipient_line(output):
            add("genre_format_broken", "函缺少收文单位行。")
        if not re.search(r"商请|函|协助|请予支持|请予协助", output):
            add("genre_format_broken", "函缺少平行商请或函复语气。")
        if APPROVAL_REQUEST.search(output):
            add("genre_function_mixed", "函混入上行请批语。")
        if not DATE_LINE.search(output) or not has_sender_before_date(output):
            add("genre_format_broken", "函落款或日期格式缺失。")
    return issues


def evaluate_turn(output: str, turn: Turn, case: Case) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    normalized = compact(output)

    def add(label: str, detail: str) -> None:
        issues.append({"label": label, "detail": detail})

    if not normalized:
        add("empty_output", "本轮没有可解析正文。")
        return issues
    if INSTRUCTION_LEAK.search(output):
        add("instruction_leak", "正文疑似残留修改过程或模型说明。")
    issues.extend(genre_format_issues(output, case))

    checks = turn.checks
    expected_title = checks.get("title")
    if expected_title and compact(title_block_text(output)) != compact(str(expected_title)):
        add("title_mismatch", f"标题未精确保持或变更为：{expected_title}")

    starts_with = checks.get("starts_with")
    if starts_with and not normalized.startswith(compact(str(starts_with))):
        add("start_mismatch", f"正文未按要求以指定内容开头：{starts_with}")

    recipient = checks.get("recipient")
    if recipient and compact(str(recipient) + "：") not in normalized and compact(str(recipient) + ":") not in normalized:
        add("recipient_mismatch", f"主送或接收方未变更为：{recipient}")
    if recipient and checks.get("recipient_after_title") and expected_title:
        title_index = title_block_end_index(output)
        recipient_index = line_index_containing(output, str(recipient))
        if title_index is not None and recipient_index is not None and recipient_index <= title_index:
            add("recipient_position_wrong", "主送或接收方出现在标题之前。")

    sender = checks.get("sender")
    if sender and compact(str(sender)) not in normalized:
        add("sender_mismatch", f"发送人或发文单位未变更为：{sender}")

    for term in checks.get("present", []):
        if not semantic_term_present(str(term), output):
            add("missing_required_content", f"缺少要求保留或新增的内容：{term}")

    for term in checks.get("closing_before_signature", []):
        closing_index = line_index_containing(output, str(term))
        signature_index = signature_line_index(output)
        if closing_index is None:
            add("missing_required_content", f"缺少要求的文种结尾语：{term}")
        elif signature_index is not None and closing_index >= signature_index:
            add("closing_position_wrong", f"文种结尾语应位于落款和成文日期之前：{term}")
    any_closings = checks.get("closing_before_signature_any")
    if any_closings:
        signature_index = signature_line_index(output)
        matched = False
        misplaced: list[str] = []
        for term in any_closings:
            closing_index = line_index_containing(output, str(term))
            if closing_index is None:
                continue
            if signature_index is not None and closing_index >= signature_index:
                misplaced.append(str(term))
                continue
            matched = True
        if not matched:
            add("missing_required_content", f"缺少可接受的文种结尾语：{' / '.join(map(str, any_closings))}")
        for term in misplaced:
            add("closing_position_wrong", f"文种结尾语应位于落款和成文日期之前：{term}")
    if checks.get("no_approval_after_signature") and approval_after_signature(output):
        add("closing_position_wrong", "请批语或审批请求出现在落款、成文日期之后。")

    for term in checks.get("absent", []):
        if compact(str(term)) in normalized:
            add("forbidden_content_retained", f"仍保留应删除或替换的内容：{term}")

    headings = checks.get("headings_in_order")
    if headings:
        positions: list[int] = []
        for heading in headings:
            pos = position_or_none(output, str(heading))
            if pos is None:
                add("heading_missing", f"缺少小标题：{heading}")
            else:
                positions.append(pos)
        if len(positions) == len(headings) and positions != sorted(positions):
            add("heading_order_wrong", f"小标题顺序不符合要求：{' -> '.join(headings)}")

    ordered = checks.get("ordered")
    if ordered:
        positions = []
        for term in ordered:
            pos = position_or_none(output, str(term))
            if pos is None:
                add("ordered_item_missing", f"排序检查项缺失：{term}")
            else:
                positions.append(pos)
        if len(positions) == len(ordered) and positions != sorted(positions):
            add("paragraph_order_wrong", f"段落或事项顺序不符合要求：{' -> '.join(ordered)}")

    paragraph_count = len(body_paragraphs(output))
    min_paragraphs = checks.get("min_paragraphs")
    if min_paragraphs is not None and paragraph_count < int(min_paragraphs):
        add("paragraph_count_low", f"自然段数量不足：{paragraph_count} < {min_paragraphs}")
    max_paragraphs = checks.get("max_paragraphs")
    if max_paragraphs is not None and paragraph_count > int(max_paragraphs):
        add("paragraph_count_high", f"自然段数量过多：{paragraph_count} > {max_paragraphs}")

    return issues


def skill_context(max_chars: int = 18000) -> str:
    paths = [
        ROOT / "chinese-official-writing" / "SKILL.md",
        ROOT / "chinese-official-writing" / "references" / "workflow.md",
        ROOT / "chinese-official-writing" / "references" / "final-review-layers.md",
        ROOT / "chinese-official-writing" / "references" / "review-checklist.md",
        ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md",
    ]
    parts: list[str] = []
    remaining = max_chars
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > remaining:
            text = text[:remaining] + "\n[truncated]\n"
        parts.append(f"## {path.relative_to(ROOT).as_posix()}\n{text}")
        remaining -= len(text)
        if remaining <= 0:
            break
    return "\n\n".join(parts)


def build_case_prompt(case: Case) -> str:
    turns = "\n".join(
        f"{turn.id} [{turn.operation}]: {turn.instruction}" for turn in case.turns
    )
    return textwrap.dedent(
        f"""
        这是中文公文写作 Skill 的只读评测。不要调用工具，不要读写文件，不要解释测试过程。
        你只需要基于给定底稿，按顺序执行多轮修改。每一轮必须以上一轮修改后的正文为基础，
        不得把“按你的要求”“已修改”等修改过程写进正文。

        使用下面 Skill 摘要作为写作规则；规则只用于指导，不要复制规则原文：
        ```text
        {skill_context()}
        ```

        文种：{case.genre}
        初始底稿：
        ```text
        {case.initial}
        ```

        修改轮次：
        {turns}

        输出格式必须严格如下。每个标题下只放该轮修改后的完整正文，不要写说明、差异列表、
        代码块、JSON 或额外标题。

        ### {case.turns[0].id}
        <第一轮完整正文>

        ### {case.turns[1].id}
        <第二轮完整正文>

        ### {case.turns[2].id}
        <第三轮完整正文>
        """
    ).strip()


def agent_command(prompt: str, template: str) -> list[str]:
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


def call_command(prompt: str, template: str, timeout: int) -> tuple[str, int, str]:
    result = subprocess.run(
        agent_command(prompt, template),
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )
    stderr = result.stderr.strip()
    return result.stdout, result.returncode, stderr


def call_codex(prompt: str, timeout: int) -> tuple[str, int, str]:
    out_file = Path(tempfile.gettempdir()) / f"revision-eval-codex-{os.getpid()}-{time.time_ns()}.md"
    codex_bin = shutil.which("codex.cmd") or shutil.which("codex.exe") or shutil.which("codex")
    if not codex_bin:
        return "", 127, "codex executable not found"
    codex_args = [
        "exec",
        "--cd",
        str(ROOT),
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--output-last-message",
        str(out_file),
        "-",
    ]
    if codex_bin.lower().endswith((".cmd", ".bat")):
        cmd = ["cmd.exe", "/d", "/c", codex_bin, *codex_args]
    else:
        cmd = [codex_bin, *codex_args]
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        input=prompt,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )
    output = ""
    if out_file.exists():
        output = out_file.read_text(encoding="utf-8", errors="replace")
        out_file.unlink(missing_ok=True)
    if not output.strip():
        output = result.stdout
    stderr = "\n".join(part for part in [result.stderr.strip(), result.stdout.strip()] if part)
    return output, result.returncode, stderr


def write_task_packet(cases: list[Case], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    packet = {
        "mode": "task-packet-only",
        "case_count": len(cases),
        "turn_count": sum(len(case.turns) for case in cases),
        "operations": sorted({turn.operation for case in cases for turn in case.turns}),
        "cases": [
            {
                "id": case.id,
                "genre": case.genre,
                "title": case.title,
                "initial": case.initial,
                "turns": [
                    {
                        "id": turn.id,
                        "operation": turn.operation,
                        "instruction": turn.instruction,
                        "checks": turn.checks,
                    }
                    for turn in case.turns
                ],
            }
            for case in cases
        ],
    }
    (out_dir / "tasks.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Revision Instruction Eval Task Packet",
        "",
        f"- Cases: {packet['case_count']}",
        f"- Turns: {packet['turn_count']}",
        f"- Operations: {', '.join(packet['operations'])}",
        "",
        "No agent was called in task-packet-only mode.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_eval(cases: list[Case], out_dir: Path, agent: str, command_template: str, timeout: int) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    issue_counter: Counter[str] = Counter()
    op_counter: Counter[str] = Counter()

    for case in cases:
        prompt = build_case_prompt(case)
        if agent == "codex":
            raw, code, stderr = call_codex(prompt, timeout)
        else:
            raw, code, stderr = call_command(prompt, command_template, timeout)
        (raw_dir / f"{case.id}.md").write_text(raw, encoding="utf-8")
        if stderr:
            (raw_dir / f"{case.id}.stderr.txt").write_text(stderr, encoding="utf-8")
        sections = parse_sections(raw, case.id)
        for turn in case.turns:
            output = sections.get(turn.id, "")
            issues = evaluate_turn(output, turn, case)
            for issue in issues:
                issue_counter[issue["label"]] += 1
            op_counter[turn.operation] += 1
            results.append(
                {
                    "case_id": case.id,
                    "genre": case.genre,
                    "turn_id": turn.id,
                    "operation": turn.operation,
                    "instruction": turn.instruction,
                    "return_code": code,
                    "output_chars": len(output),
                    "issues": issues,
                }
            )

    summary = {
        "mode": agent,
        "case_count": len(cases),
        "turn_count": len(results),
        "issue_count": sum(issue_counter.values()),
        "failed_turns": sum(1 for row in results if row["issues"]),
        "issue_counts": dict(sorted(issue_counter.items())),
        "operation_counts": dict(sorted(op_counter.items())),
        "results": results,
    }
    (out_dir / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary_markdown(summary, out_dir / "summary.md")
    return 0


def write_summary_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Multi-Round Revision Instruction Eval",
        "",
        "本测试只记录多轮结构修改指令遵循问题，不自动修复 Skill，也不对输出做脚本清洗。",
        "",
        "## 汇总",
        "",
        f"- 模式：{summary['mode']}",
        f"- 用例数：{summary['case_count']}",
        f"- 轮次数：{summary['turn_count']}",
        f"- 失败轮次：{summary['failed_turns']}",
        f"- 问题总数：{summary['issue_count']}",
        "",
        "## 问题类型",
        "",
    ]
    if summary["issue_counts"]:
        for label, count in summary["issue_counts"].items():
            lines.append(f"- {label}: {count}")
    else:
        lines.append("- 未发现断言问题。")
    lines.extend(["", "## 失败明细", ""])
    any_failure = False
    for row in summary["results"]:
        if not row["issues"]:
            continue
        any_failure = True
        lines.append(f"### {row['turn_id']} {row['genre']} {row['operation']}")
        lines.append("")
        lines.append(f"- 指令：{row['instruction']}")
        for issue in row["issues"]:
            lines.append(f"- {issue['label']}: {issue['detail']}")
        lines.append("")
    if not any_failure:
        lines.append("- 未发现失败轮次。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def selected_cases(limit_cases: int | None) -> list[Case]:
    if limit_cases is None:
        return CASES
    return CASES[: max(0, limit_cases)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--agent", choices=("none", "codex", "command"), default="none")
    parser.add_argument("--command-template", default=os.environ.get("OFFICIAL_WRITING_AGENT_COMMAND", ""))
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--limit-cases", type=int)
    args = parser.parse_args()

    cases = selected_cases(args.limit_cases)
    out_dir = Path(args.out)
    if args.agent == "none":
        write_task_packet(cases, out_dir)
        print((out_dir / "summary.md").as_posix())
        return 0
    if args.agent == "command" and not args.command_template.strip():
        print("ERROR: --command-template or OFFICIAL_WRITING_AGENT_COMMAND is required for command mode", file=sys.stderr)
        return 2
    code = run_eval(cases, out_dir, args.agent, args.command_template, args.timeout_seconds)
    print((out_dir / "summary.md").as_posix())
    return code


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
