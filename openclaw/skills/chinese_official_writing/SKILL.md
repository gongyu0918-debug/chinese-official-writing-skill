---
name: chinese_official_writing
description: 主要用于中文公文、机关企事业单位、学校正式事务材料的起草、改写、压缩、复核；用户要求写申请、请示、报告、通知、通告、意见、决定、决议、议案、公报、命令、函、复函、批复、说明、方案、纪要、公告、公示、通报、征求意见函、工作要点、总结、调研、讲话、采购公告、可研、审查材料或降 AI 味时使用。中文本科、硕士学位论文、课程论文及其开题报告或独立文献综述任务按独立论文叶子处理；不用于英文、文学、营销、社媒、个人求职、代码说明、通用翻译、闲聊、模型训练、批量语料和未知来源文本改写、规避人工审核或 AIGC/查重检测，不替代法律/财务/采购/审计/政策/学术判断。
license: MIT-0
category: writing
tags:
  - chinese
  - official-document
  - writing
  - gongwen
  - ai-compute
metadata:
  version: "1.5.8"
  compatible_agents:
    - codex
    - claude-code
    - openclaw
    - hermes
    - qwen-code
    - minimax-skills
    - glm-skills
    - autoclaw
    - kimi-code-cli
    - trae
    - baidu-comate-ai-ide
    - generic-agent-skills
  qwen_code:
    install_personal: "~/.qwen/skills/chinese-official-writing"
    install_project: ".qwen/skills/chinese-official-writing"
    entry: "SKILL.md"
  openclaw:
    version: "1.5.8"
    emoji: "📝"
    tags:
      - chinese
      - official-document
      - writing
      - gongwen
      - ai-compute
---

# 中文公文写作

主入口是中文公文和正式工作材料；论文仅作按需专项叶。

## 入口路由

按最终交付物选一个叶子：

- 公文路线只读取 `references/official-writing.md`；“本科毕业论文抽检通知”和“报送开题报告的通知”仍按通知处理。
- 论文路线只读取一个专项：普通本科、硕士或课程论文读取 `references/academic-writing.md`；开题报告读取 `references/academic-proposal.md`；独立文献综述读取 `references/academic-literature-review.md`。“研究公文语言的课程论文”仍走论文叶。

英文论文、投稿全流程、实验设计、统计分析、答辩、排版和查重/AIGC 规避不在范围内。

## 共用硬边界

- 正文事实只来自用户材料和已核验检索结果；材料不足时宁可短写，不补造主体、数据、案例、政策、日期、金额、联系人、方法、文献、结果或结论。
- 证据状态必须保真：“未提供、未披露、尚未完成”不得改成“未开展、不存在、没有”，“反映、认为、拟、建议”不得改成客观结论、既定决定或已完成事实。
- 用户模板、最新版底稿和本轮要求优先；旧稿、样文和检索材料不自动成为事实。默认不联网，无法核验的内容不入正文。
- 严格服从只输出正文、只输出改后稿或只审不改；不输出 AI 身份、推理、加载过程、规则自述或占位。保密审查、正式签发和专业判断须人工复核；不承诺规避检测，不补造签发信息。

选定后结束路由；不得合并不同叶子的 references。
