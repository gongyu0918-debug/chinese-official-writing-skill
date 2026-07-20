# 1.5.19 发布证据

日期：2026-07-20

## 变更边界

1.5.19 以 `v1.5.18=9822aaee30df89c479a4e8c94c478424f6d426e3` 为固定发行基线，纳入三项独立验证后的最小修改：

- ClawHub/OpenClaw 普通 Skill 包不再携带 `delivery-review-gate.md`、`gate_stop_hook.py` 和 `review_gate.py`。这三个文件属于 Codex 生命周期 Hook 与有限状态事务运行时，曾使普通 Skill 包出现 `subprocess module call` 审查提示；canonical、Codex 插件和既有 1.5.18 能力不因本项改动而删除。普通包继续保留只定位、不自动改稿的 `prose_lint.py`。
- `review-checklist.md` 删除一处重复的信息选择去向提示，canonical 与五个发行镜像合计减少 38 个字符。信息选择规则、文种路由、事实锚、用户模板、篇幅预算、输出模式和复核顺序保持不变。
- `anti-ai-patterns.md`、报告/通报文种叶子和材料稀疏轻量任务卡增加“结论式否定尾巴”复核：逐句检查否定命题来源和动词强度；材料已有的调查、核查等进行状态沿用原主体、动作、对象和状态，写到状态即止；材料外围补充句省略。`收口` 同时列入工程化高频词，正式正文按实际事项写成完成、明确、办结或汇总。

跨宿主共享检测内核、JSON 协议和各宿主薄适配器仍在隔离研究分支。现有原型存在显式标记自动删除时损失必要事实、非公文任务误触发和部分宿主缺少真实生命周期证明等风险，不进入 1.5.19 发行包。

## 真实写稿

38 字符微减负使用三条正常自然任务做 1.5.18/Candidate A/B，两组实际读取同一复核清单。独立匿名盲审结果为：账号清理内部通知 baseline 小胜；备份任务运行报告 Candidate 优胜；应用系统运维会议纪要 Candidate 小胜。三题没有复现同一 Candidate 独有回退。

该组证据只支持“删除重复指针后未观察到共性写作回退”，不把 2/3 小胜归因为 38 个字符，也不宣称微减负形成稳定语言增益。ClawHub 清洁包只改变发行文件边界，不改变写稿 Prompt，因此不重复生成正文。

结论式否定尾巴使用一篇系统异常报告和一篇备份任务通报做固定 1.5.18/Candidate A/B。首次 Candidate 只读取轻量任务卡，未触达长 reference，按路由缺口修正后复跑同题。报告题中，1.5.18 出现“原因调查尚未完成，调查结果待后续通报”；最终 Candidate 改为“具体原因正在调查中”，材料外调查程序由中间稿的 3 处降为 0，无锚定否定为 0。最终 Candidate 因重复较多且约低于 700 字下限 29 字，整体盲审仍判 1.5.18 小胜。通报题 Candidate 胜出，没有无锚定否定；一处“抽查结果未出现执行失败”有材料锚点但与“全部成功”重复。该组支持 P0 定向改善，不支持整体语言全面领先；重复解释和轻微篇幅偏差作为已知 P2 保留。

## 工程验证

- `py -3.13 -m unittest discover -s tests`：350/350 通过。沙箱内首次运行因 Python 临时目录 ACL 出现 149 个 `PermissionError`；在沙箱外按原命令复跑后全部通过，该次失败记为环境噪声。
- `py -3.13 tools/run_real_prompt_ablation.py --baseline-root <1.5.18> --baseline-label 1.5.18 --current-root . --out <out>`：1.5.18 为 108/108，current 为 108/108。
- `py -3.13 evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，Skill 10/10，judge consistency 1.0。
- `py -3.13 <skill-creator>/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py`、镜像一致性测试与 `git diff --check`：通过。

## 已知边界

- 1.5.19 不宣称普通 ClawHub Skill 自动执行生命周期 Hook；它的修复目标是让普通包保持纯 Skill 边界，消除与该分发面无关的子进程运行时。
- “尚未、未形成、不能”等词在事故调查、行政裁决和明确未决状态中仍可能承担必要事实，不能由脚本按词整体删除。后续 Prompt 候选将优先压制无材料锚点的结论式否定句群，并对材料原句、法定论证和必要未决状态保留例外。
- 当前 38 字符减负的语言差异小于单次生成噪声，只把确定性上下文减少和无共性回退作为发布依据。
- 结论式否定尾巴规则不按 `尚未`、`未形成`、`不能` 等词整体删除。材料原有否定、法定边界和必要未决状态继续保留；本轮没有加入“事实只写一次”等新的段落级限制。

## 发布回执

- GitHub：待发布。
- ClawHub：待发布。
- skillhub.cn：待发布，精确目标仍为 `skillId=70149`。

小红书 Red SkillHub 继续排除。本节在三平台操作后只按实际回执补录；提交成功、公开 latest、审核和安全扫描分别记录，不互相推断。
