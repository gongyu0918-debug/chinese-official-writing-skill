# `official-writing-agent-community` harness 冷审记录

## 来源与可追溯范围

- 仓库：`https://github.com/gongyu0918-debug/official-writing-agent-community`
- 可见性：private。
- 当前主线：`d86eec238644ace6fc322ebbd45a1a95fe47b6fd`。
- Git 历史只有两个提交：`f43f218cd249efee0cf3da90af776500edd0f467` 导入私有社区版基线，`d86eec2` 增加斜杠命令。
- 第二个提交没有修改 `app/agent_lite/`、`app/skill/loader.py` 或内置 Skill；现存写作链可固定到导入基线审查。
- 内置 Skill 为 1.4.7，仓库没有 1.2.x tag、commit、配置或原始写稿证据。用户确认早期使用过该 harness，但当前 Git 只能做“现存 harness 快照 + 历史 Skill”的兼容性重建，不能冒充精确历史运行包。
- 根目录没有 LICENSE，GitHub `licenseInfo=null`。本轮只借鉴机制和测试分臂，不复制实现代码、整段 Prompt 或正则。

## 实际工作流

起草链见 `app/agent_lite/service.py`：

1. writer 生成提纲；
2. reviewer 只审文种、跑题和用户明确核心要求，失败时返修提纲一次；
3. writer 按提纲生成正文；
4. 超长 30% 时压缩；只有目标不少于 8000 字且正文低于目标 70% 时才触发续写；
5. final reviewer 做交稿阻断审校，失败后最多返修正文一次；
6. 仍未解决时标记 `needs_human_review`，保存正文、审校 JSON 和阶段轨迹。

修订任务不生成提纲，直接围绕当前稿修订后进入终审。provider 层可以分别传 writer、reviewer 配置，但当前 Web 入口把同一个模型配置传给两者；这是分开的模型调用，不是异模型独立验证。

## Skill 注入方式

`app/skill/loader.py` 不加载完整 Skill。它只抽取 `三层使用原则`、`核心流程`，删除含 `references/` 的行，再按 harness 自己的正则最多选择 4 个 reference。入口摘要上限 2200 字符，reference 摘要上限 5600 字符。

用同一内联报告任务和 `has_context=False` 实测：

| 外部 Skill | 入口摘要字符 | reference 摘要字符 | 实际加载 |
| --- | ---: | ---: | --- |
| 1.2.5 | 252 | 0 | 只有核心流程摘要 |
| 1.2.18 | 426 | 0 | 只有三层原则与核心流程摘要 |
| 1.2.29 | 533 | 1277 | 摘要 + `formal-addressing.md` |
| 1.5.14 | 1088 | 1277 | 摘要 + `formal-addressing.md` |

现存 `WRITER_SYSTEM` 为 3135 字符，`USER_TEMPLATE_OUTLINE` 为 783，`USER_TEMPLATE_DRAFT` 为 1306，`FINAL_REVIEWER_SYSTEM` 为 3039。`prompts.py` 源文件为 11912 字符，六类否定标记共 149 次；harness 的规则密度明显高于实际注入的历史 Skill 摘要。不拆 harness-only 时，无法把结果归因于历史 Skill。

## 已复现问题

### 1. 区间字数没有进入长度机制

`service.py::_target_words` 只识别单个数值。实际运行同一正则：

```text
起草一份1300—1600字的报告 -> []
起草一份1500字的报告 -> [1500]
控制在900—1100字 -> []
约1000字 -> [1000]
```

因此本轮 T02、T04 的区间要求不会触发 harness 的目标长度、压缩或续写逻辑。测试必须忠实记录，不能先修 harness 再称为历史组合结果。

### 2. 内联材料被当成无上下文

`_is_low_fact_report` 只看是否存在上传 context。材料全部写在用户 prompt 时，`has_context=False`；只要任务文本出现“报告”，就命中 low-fact 分支。T04 的材料句“信息中心报告”也会命中该正则，即使任务是会议纪要。

命中后 loader 先选择 `formal-addressing.md` 并立即返回。1.2.5、1.2.18 尚无该文件，结果是 0 reference，也不回退到当时已存在的其他 reference。该行为属于现存 harness 对旧 Skill 的重解释。

### 3. 跨版本同进程有缓存污染风险

`service.py::_skill_guidance` 使用 LRU 缓存，缓存键没有 Skill 路径或版本。切换 `OFFICIAL_WRITING_SKILL_ROOT` 后，同题可能复用上一版本指导。每个条件必须使用独立进程或独立 App 上下文，不能在同进程轮换版本。

### 4. harness reviewer 不评价整体观感

`FINAL_REVIEWER_SYSTEM` 明确采用“可用即可通过”“不做风格偏好审核”。它能拦事实、占位、禁写字段、文种和格式错误，不能回答首中尾是否均衡、行文是否自然、是否过度保护、主体宾语是否完整，以及是否优于无 Skill。

## 最小借鉴边界

接受用于测试设计：

- 用参数切换历史 Skill 根目录，每个版本独立上下文；
- 保存实际加载清单、模型、思考强度、阶段轨迹和原始输出；
- writer、reviewer 分开调用，返修次数有限；
- 先做提纲，再起草正文，最终由新的独立盲审评价整体质量。

暂不搬入产品 Skill：

- 整段 writer/reviewer Prompt 和固定禁写清单；
- 当前 low-fact 正则路由、自动日期删除和状态词门禁；
- 同模型自写自审充当独立质量证明；
- 默认 mock 场景矩阵充当真实写稿证据；
- 新增固定提纲调用、自动返修循环或 runtime harness。

最公平的首轮至少拆成无 Skill、harness-only、harness + 历史 Skill、原生当前 Skill 四臂。否则无 Skill 组和 Skill 组的 Prompt 负担不同，无法区分 harness 贡献、Skill 增益和过度工程风险。

## 实际验证

- `python -m unittest tests.test_skill_copy -v`：8/8 通过。
- `python -m unittest tests.agent_lite.test_orchestrator tests.test_skill_copy tests.test_prompt_scenario_matrix`：11 项中 8 项通过，3 项因当前临时 Python 环境缺少 `python-docx` 导入失败；未把这次运行记为 harness 全量测试通过。
- 区间字数正则与会议纪要中“报告”误命中均已用独立命令实际复现。
