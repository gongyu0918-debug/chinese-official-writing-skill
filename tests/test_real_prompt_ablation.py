from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


real_prompt_eval = load_module("real_prompt_ablation_under_test", ROOT / "tools" / "run_real_prompt_ablation.py")


class RealPromptAblationTests(unittest.TestCase):
    def test_cases_cover_create_and_revision_prompts(self) -> None:
        kinds = {case.kind for case in real_prompt_eval.CASES}
        prompts = "\n".join(case.prompt for case in real_prompt_eval.CASES)

        self.assertEqual(kinds, {"create", "revise"})
        self.assertIn("帮我起草", prompts)
        self.assertIn("写一份采购公告", prompts)
        self.assertIn("请把这段顺成正式报告", prompts)
        self.assertIn("审一下这段能不能进正文", prompts)
        self.assertIn("不要新增小标题", prompts)
        self.assertIn("不要加接收方", prompts)
        self.assertIn("内部 WPS 会员采购申请", prompts)
        self.assertIn("不写主送机关", prompts)
        self.assertIn("不要改成请示", prompts)
        self.assertIn("包在代码块", prompts)
        self.assertIn("维护期限为XXXX年", prompts)
        self.assertIn("AI生成内容业务", prompts)
        self.assertIn("本报告系AI辅助生成", prompts)
        self.assertIn("### 业务需求与服务保障", prompts)
        self.assertIn("不要补原文没有的事实", prompts)
        self.assertIn("clean corpus", prompts)
        self.assertIn("真实模型", prompts)
        self.assertIn("镜像不能静默分叉", prompts)
        self.assertIn("食品安全专项检查情况报告", prompts)
        self.assertIn("三个人写的年度总结材料", prompts)
        self.assertIn("GB/T 9704 排成 Word", prompts)
        self.assertIn("意义重大、亮点纷呈", prompts)
        self.assertIn("不要默认就高", prompts)
        self.assertIn("正式 Word 红头文件", prompts)
        self.assertIn("只审一下这段格式和语气", prompts)
        self.assertIn("我觉得这个事差不多", prompts)
        self.assertIn("政策依据我没给，也不要外搜", prompts)
        self.assertIn("请核验现行政策依据", prompts)
        self.assertIn("不要自动搜索单位风格", prompts)
        self.assertIn("清理网页元信息", prompts)
        self.assertIn("被印发方案第二部分", prompts)
        self.assertIn("压缩到500字以内", prompts)
        self.assertIn("多个责任主体不要压成笼统的有关单位", prompts)
        self.assertIn("不要写成“指定渠道”“截止时间前”", prompts)
        self.assertIn("只新增“报销凭证”字段", prompts)
        self.assertIn("压缩到260字以内", prompts)
        self.assertIn("形成长效机制，显著提升治理能力", prompts)
        self.assertIn("来源名称、发布机关、文号或链接", prompts)
        self.assertIn("正式 Word/docx 交付", prompts)
        self.assertIn("专项调研报告", prompts)
        self.assertIn("后半篇不能草草结束", prompts)
        self.assertIn("不要先问我一串问题", prompts)
        self.assertIn("不要把增删论点、扩写细节列成我的义务", prompts)
        self.assertIn("不要因为我没补信息就追问或停止修改", prompts)
        self.assertIn("不要因为要成稿就自行写", prompts)
        self.assertIn("正文后给一个核对卡", prompts)
        self.assertIn("旧版金额、旧主送和旧政策口号不要回流", prompts)
        self.assertIn("只审空话套话，不重写全文", prompts)
        self.assertIn("不要补责任部门、督办安排或处理进展", prompts)
        self.assertIn("必须标明每处具体位置", prompts)
        self.assertIn("句式是不是太模板化", prompts)
        self.assertIn("不要改成公众号口吻", prompts)
        self.assertIn("提供有力支撑", prompts)
        self.assertIn("老板关心、钱花得值、马上要搞", prompts)
        self.assertIn("不要升级事实", prompts)
        self.assertIn("写个申请，买一块 2T 固态硬盘", prompts)
        self.assertIn("写个请示，申请采购 3 台办公电脑", prompts)
        self.assertIn("学校奖学金申请", prompts)
        self.assertIn("起草征求意见函", prompts)
        self.assertIn("给论文降 AI 味", prompts)
        self.assertIn("小红书营销种草文案", prompts)
        self.assertIn("个人求职申请信", prompts)
        self.assertIn("App 增长营销方案", prompts)
        self.assertIn("会议记录整理成会议纪要", prompts)
        self.assertIn("普通采购，不涉及算力", prompts)
        self.assertIn("主送机关、申请单位、金额和成文日期都没给", prompts)
        self.assertIn("不要把落款截成简称", prompts)
        self.assertIn("不要用 --- 分隔正文和说明", prompts)
        self.assertIn("不要过拟合成调研报告", prompts)
        self.assertIn("不要把提醒写成第七章", prompts)
        self.assertIn("正文和附件表格的数字", prompts)
        self.assertIn("不要套模板补空项", prompts)
        self.assertIn("不要把采购需求推断成现有能力不足", prompts)

    def test_current_skill_passes_real_prompt_cases(self) -> None:
        rows = real_prompt_eval.evaluate_root(ROOT, "current_test")
        failures = {row["id"]: row["failures"] for row in rows if not row["passed"]}

        self.assertEqual(failures, {})

    def test_case_set_includes_recent_review_regressions(self) -> None:
        checks_by_id = {case.id: case.checks for case in real_prompt_eval.CASES}

        self.assertIn("采购公告", checks_by_id["P002"]["description_terms"])
        self.assertIn("征求意见函", checks_by_id["P001"]["checklist_sections"])
        self.assertIn("公示", checks_by_id["P003"]["handling_rows"])
        self.assertIn("thought-leak", checks_by_id["P007"]["lint_present_labels"])
        self.assertIn("viewpoint-risk", checks_by_id["P006"]["lint_absent_labels"])
        self.assertIn("改稿前小标题清单", checks_by_id["P009"]["review_checklist_terms"])
        self.assertIn("说明", checks_by_id["P010"]["description_terms"])
        self.assertIn("申请", checks_by_id["P011"]["description_terms"])
        self.assertIn("chinese-official-writing/references/final-review-layers.md", checks_by_id["P012"]["file_terms"])
        self.assertIn("chinese-official-writing/references/formal-addressing.md", checks_by_id["P013"]["file_terms"])
        self.assertIn("unfinished-placeholder", checks_by_id["P014"]["lint_present_labels"])
        self.assertIn("unfinished-placeholder", checks_by_id["P015"]["lint_present_labels"])
        self.assertIn("thought-leak", checks_by_id["P016"]["lint_absent_labels"])
        self.assertIn("thought-leak", checks_by_id["P017"]["lint_present_labels"])
        self.assertIn("markdown-heading", checks_by_id["P018"]["lint_present_labels"])
        self.assertIn(
            "不新增原文没有交代的活动、依据、数据、成效或责任安排",
            checks_by_id["P019"]["file_terms"]["chinese-official-writing/references/workflow.md"],
        )
        self.assertIn("未新增原文外事实", checks_by_id["P019"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn(
            "notice-submit-materials",
            checks_by_id["P020"]["file_terms"]["tests/fixtures/clean_prose_corpus.json"],
        )
        self.assertIn("真实模型小样本评测", checks_by_id["P021"]["file_terms"]["README.md"])
        self.assertIn("THRESHOLD_ENV_VARS", checks_by_id["P021"]["file_terms"]["evals/official-writing/run_eval.py"])
        self.assertIn(
            "test_primary_adapter_mirrors_match_canonical_bytes",
            checks_by_id["P022"]["file_terms"]["tests/test_skill_boundary.py"],
        )
        self.assertIn("任务模式路由", checks_by_id["P023"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("压实合并表达", checks_by_id["P024"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("Word/排版交付衔接", checks_by_id["P025"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("夸大意义", checks_by_id["P026"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("数据冲突不得默认就高", checks_by_id["P027"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("正式交付前要素核对", checks_by_id["P028"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("不默认重写全文", checks_by_id["P029"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("轻量语气替换建议", checks_by_id["P030"]["file_terms"]["chinese-official-writing/references/official-style.md"])
        self.assertIn("默认不外搜", checks_by_id["P031"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("现行政策", checks_by_id["P032"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("只出现单位名称", checks_by_id["P033"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("通知壳", checks_by_id["P034"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("被印发文件正文", checks_by_id["P034"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("不可丢要素", checks_by_id["P035"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("多主体分工", checks_by_id["P035"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("缺失事实处理提示", checks_by_id["P036"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("新增字段没有用户提供值", checks_by_id["P037"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("字数自检", checks_by_id["P038"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("评价强度超过证据", checks_by_id["P039"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("搜索来源清单", checks_by_id["P040"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("不要写成“已确认可作为 Word 稿基础”", checks_by_id["P041"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("长篇限字稿件", checks_by_id["P042"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("措施安排", checks_by_id["P042"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("压掉措施安排", checks_by_id["P042"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("事实不足不作为默认中断理由", checks_by_id["P043"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("不在正文前中断成稿", checks_by_id["P043"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("未做调查问卷式问题清单", checks_by_id["P043"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("补充以下信息后，文章会更完整", checks_by_id["P043"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn(
            "事实补足建议只列影响文种功能或执行落地的关键缺口",
            checks_by_id["P044"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn("写稿人可安排事项", checks_by_id["P044"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("转嫁给用户", checks_by_id["P044"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("不把上一轮待确认事项升级为阻断条件", checks_by_id["P045"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("待确认事项仍是软提示", checks_by_id["P045"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("不把待确认事项升级成阻断链路", checks_by_id["P045"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("强判断", checks_by_id["P046"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("能够正常开展", checks_by_id["P046"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("结论口径列入正文外待确认", checks_by_id["P046"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("事实强判断", checks_by_id["P046"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("正式交付前要素核对卡", checks_by_id["P047"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("不因缺这些正式要素阻断成稿", checks_by_id["P047"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("优先只列用户点名缺项", checks_by_id["P047"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("未扩展成长清单", checks_by_id["P047"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("不把旧金额、旧主送、旧落款、旧政策口号或旧结论带回最新版正文", checks_by_id["P048"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("修改模式是否以最新版底稿为主线", checks_by_id["P048"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("审稿时看成簇问题", checks_by_id["P049"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("单个正式词或单个转折不作为硬清洗理由", checks_by_id["P049"]["file_terms"]["chinese-official-writing/references/official-style.md"])
        self.assertIn(
            "不为显得完整而补造牵头部门、责任部门、管理动作、整改动作、成果总结、跟踪督办、后续处理进展",
            checks_by_id["P050"]["file_terms"]["chinese-official-writing/references/workflow.md"],
        )
        self.assertIn("正式化新增事实", checks_by_id["P050"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("优先逐项引用原文短语或句子", checks_by_id["P051"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("整体归纳可放在逐项意见之后", checks_by_id["P051"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("句群节奏和模板化痕迹", checks_by_id["P052"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("公文去 AI 味不是聊天化", checks_by_id["P053"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("口号式收束", checks_by_id["P054"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("定稿前高风险先查", checks_by_id["P055"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])
        self.assertIn("口语来源不等于事实授权", checks_by_id["P055"]["file_terms"]["chinese-official-writing/references/official-style.md"])
        self.assertIn("相关负责人关注该事项", checks_by_id["P055"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("不写成正文标签", checks_by_id["P055"]["file_terms"]["chinese-official-writing/references/genre-checklist.md"])
        self.assertIn("申请", checks_by_id["P056"]["description_terms"])
        self.assertIn("请示", checks_by_id["P057"]["description_terms"])
        self.assertIn("学校", checks_by_id["P058"]["description_terms"])
        self.assertIn("工作要点", checks_by_id["P059"]["description_terms"])
        self.assertIn("征求意见函", checks_by_id["P060"]["description_terms"])
        self.assertIn("论文", checks_by_id["P061"]["description_exclusion_terms"])
        self.assertIn("营销", checks_by_id["P062"]["description_exclusion_terms"])
        self.assertIn("个人求职", checks_by_id["P063"]["description_exclusion_terms"])
        self.assertIn("社媒", checks_by_id["P064"]["description_exclusion_terms"])
        for case_id, term in [
            ("P065", "通告"),
            ("P066", "意见"),
            ("P067", "决定"),
            ("P068", "决议"),
            ("P069", "议案"),
            ("P070", "公报"),
            ("P071", "命令"),
        ]:
            self.assertIn(term, checks_by_id[case_id]["description_terms"])
        self.assertIn(
            "## 会议纪要",
            checks_by_id["P072"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "普通采购公告不默认进入 AI 算力语境",
            checks_by_id["P077"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "专项结构和指标写法转读 `ai-compute-docs.md`",
            checks_by_id["P078"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"],
        )
        self.assertIn(
            "未给会议判断",
            checks_by_id["P080"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "未造成 `。；` 或行尾分号噪声",
            checks_by_id["P081"]["file_terms"]["chinese-official-writing/references/review-checklist.md"],
        )
        self.assertIn(
            "影响正式报送和文种完整性",
            checks_by_id["P082"]["file_terms"]["chinese-official-writing/references/handling-elements.md"],
        )
        self.assertIn(
            "不把落款单位截成泛称或为压字数删除成文日期",
            checks_by_id["P083"]["file_terms"]["chinese-official-writing/references/workflow.md"],
        )
        self.assertIn("markdown-horizontal-rule", checks_by_id["P084"]["lint_present_labels"])
        self.assertIn(
            "正文后的待确认、风险提醒或核验提示不属于正文章节",
            checks_by_id["P086"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "不自动改题为“调研报告”",
            checks_by_id["P086"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "文表和附件一致性",
            checks_by_id["P087"]["file_terms"]["chinese-official-writing/references/proofreading-checklist.md"],
        )
        self.assertIn(
            "未给的供应商、报价依据、验收安排或归档要求列正文外待补",
            checks_by_id["P088"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "不把有期限的事项拆成多个待明确字段",
            checks_by_id["P088"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "不把一个期限扩展到原文未绑定的其他任务",
            checks_by_id["P088"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "采购需求不等于现有能力不足、效率提升、业务范围不变或影响结论",
            checks_by_id["P088"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "不改写成已定实施方案、执行命令",
            checks_by_id["P089"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "不自动改题为“调研报告”“考核说明”或“实施方案”",
            checks_by_id["P089"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "不用 Markdown `**` 加粗包装标签",
            checks_by_id["P090"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "未用 Markdown 加粗或装饰性格式替代用户要求",
            checks_by_id["P090"]["file_terms"]["chinese-official-writing/references/review-checklist.md"],
        )
        self.assertIn(
            "标题后应短列 1-4 项",
            checks_by_id["P091"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "事实少于字数目标时宁可短写",
            checks_by_id["P091"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "材料稀疏型通报或情况说明按已给事实之间的关系简短成稿",
            checks_by_id["P091"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "事实映射式二次修改",
            checks_by_id["P091"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "材料未给执行要求、整改要求和后续处理时，不为了像通报而补写",
            checks_by_id["P091"]["file_terms"]["chinese-official-writing/references/genre-playbooks.md"],
        )
        self.assertIn(
            "不新增采购类别、资产属性、用途、入库流程",
            checks_by_id["P092"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "正式正文的标题、小标题、段落标签直接用普通文本承接",
            checks_by_id["P093"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "缺少某一环节时，不补齐固定章节",
            checks_by_id["P105"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn(
            "只有材料确有研究过程或事实依据时",
            checks_by_id["P106"]["file_terms"]["chinese-official-writing/references/official-style.md"],
        )
        self.assertIn(
            "字段式底稿默认保留字段名、顺序和单元边界",
            checks_by_id["P107"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"],
        )
        self.assertIn(
            "不保留字段标签或机械转述字段名",
            checks_by_id["P107"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"],
        )
        self.assertEqual(checks_by_id["P108"]["lint_delivery_mode"], "draft-body")
        self.assertIn("delivery-metadata", checks_by_id["P108"]["lint_present_labels"])
        self.assertIn(
            "制作版本、内部受众、操作方式、校验门禁或审核状态等交付元信息",
            checks_by_id["P108"]["file_terms"]["chinese-official-writing/SKILL.md"],
        )
        self.assertIn("delivery-boilerplate", checks_by_id["P108"]["lint_present_labels"])
        self.assertIn("duplicate-title", checks_by_id["P108"]["lint_present_labels"])
        self.assertIn(
            "本项由模型通读全文后判断，不按固定词表自动替换",
            checks_by_id["P109"]["file_terms"][
                "chinese-official-writing/references/anti-ai-patterns.md"
            ],
        )
        self.assertIn(
            "未确认有问题的句子、真实比较和必要否定保持原样",
            checks_by_id["P109"]["file_terms"][
                "chinese-official-writing/references/anti-ai-patterns.md"
            ],
        )
        self.assertIn(
            "事实、引用、术语、否定范围和论断强度不变",
            checks_by_id["P109"]["file_terms"][
                "chinese-official-writing/references/final-review-layers.md"
            ],
        )

    def test_heading_lock_detects_added_subheading(self) -> None:
        before = """一、整改进展
二、存在问题
三、原因分析
四、下一步安排"""
        after = """一、整改进展
二、存在问题
三、原因分析
四、数据口径影响
五、下一步安排"""

        self.assertNotEqual(real_prompt_eval.numbered_headings(before), real_prompt_eval.numbered_headings(after))

    def test_heading_lock_reads_markdown_numbered_headings(self) -> None:
        markdown = """### 一、整改进展
### 二、存在问题
### 三、原因分析
### 四、下一步安排"""

        self.assertEqual(
            real_prompt_eval.numbered_headings(markdown),
            ["一、整改进展", "二、存在问题", "三、原因分析", "四、下一步安排"],
        )

    def test_heading_lock_reads_bracketed_and_arabic_numbered_headings(self) -> None:
        text = """（一）整改进展
（二）存在问题
1. 原因分析
2、下一步安排
2026年6月30日前反馈材料。"""

        self.assertEqual(
            real_prompt_eval.numbered_headings(text),
            ["（一）整改进展", "（二）存在问题", "1. 原因分析", "2、下一步安排"],
        )

    def test_exit_code_fails_when_current_has_any_failure(self) -> None:
        results = {
            "old": [{"passed": False}, {"passed": False}],
            "current": [{"passed": True}, {"passed": False}],
        }

        self.assertEqual(real_prompt_eval.exit_code_for_results(results, "old"), 1)

    def test_missing_baseline_root_returns_clean_error(self) -> None:
        script = ROOT / "tools" / "run_real_prompt_ablation.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing-baseline"
            out_dir = Path(temp_dir) / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--baseline-root",
                    str(missing),
                    "--current-root",
                    str(ROOT),
                    "--out",
                    str(out_dir),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR:", result.stderr)
        self.assertIn("目录不存在", result.stderr)
        self.assertIn("git worktree add", result.stderr)
        self.assertNotIn("Traceback", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
