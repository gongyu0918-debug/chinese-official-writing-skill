# 1.5.19 发布证据

日期：2026-07-20

## 变更边界

1.5.19 以 `v1.5.18=9822aaee30df89c479a4e8c94c478424f6d426e3` 为固定发行基线，纳入三项独立验证后的最小修改：

- ClawHub/OpenClaw 普通 Skill 包不再携带 `delivery-review-gate.md`、`gate_stop_hook.py` 和 `review_gate.py`。这三个文件属于 Codex 生命周期 Hook 与有限状态事务运行时，曾使普通 Skill 包出现 `subprocess module call` 审查提示；canonical、Codex 插件和既有 1.5.18 能力不因本项改动而删除。普通包继续保留只定位、不自动改稿的 `prose_lint.py`。
- `review-checklist.md` 删除一处重复的信息选择去向提示，canonical 与五个发行镜像合计减少 38 个字符。信息选择规则、文种路由、事实锚、用户模板、篇幅预算、输出模式和复核顺序保持不变。
- `final-review-layers.md` 增加一条原子化结论限定复核：事实已经完整，材料、用户和当前文种均未提出某个结论对象时，不在句后追加对该结论的限定；材料明确记载的结论状态保持原义。该项不按词删除，不同时引入缓和语、免责声明、范围限定、进行态改写或段内公式调整。

跨宿主共享检测内核、JSON 协议和各宿主薄适配器仍在隔离研究分支。现有原型存在显式标记自动删除时损失必要事实、非公文任务误触发和部分宿主缺少真实生命周期证明等风险，不进入 1.5.19 发行包。

## 真实写稿

38 字符微减负使用三条正常自然任务做 1.5.18/Candidate A/B，两组实际读取同一复核清单。独立匿名盲审结果为：账号清理内部通知 baseline 小胜；备份任务运行报告 Candidate 优胜；应用系统运维会议纪要 Candidate 小胜。三题没有复现同一 Candidate 独有回退。

该组证据只支持“删除重复指针后未观察到共性写作回退”，不把 2/3 小胜归因为 38 个字符，也不宣称微减负形成稳定语言增益。ClawHub 清洁包只改变发行文件边界，不改变写稿 Prompt，因此不重复生成正文。

最初把公式化否定、保护性限定、进行态承载和必要否定例外合并加载时，三组正常成稿盲审为 Candidate 一胜、一负、一难分，不能归因，组合规则已撤回。随后将外部“命题来源”思路拆成单一结论限定复核。规则首次放在 `anti-ai-patterns.md` 时，三份 Candidate 均未实际读取该文件，按技术无效处理，不计入质量样本；规则移至成稿后必读的 `final-review-layers.md` 后，三份输出均有实际读取记录。

有效原子 A/B 复用固定 1.5.18 的首个技术有效基线稿，只新增 Candidate：一项人工标注旧稿局部改写、一份设备巡检整改报告、一份食堂供餐异常通报。独立匿名盲审判 Candidate 三题均胜：局部改写明显胜，保留了材料原有结论状态；巡检报告小胜，事实与篇幅通过；食堂通报小胜，事实与篇幅通过。三题没有 Candidate 独有的事实、数字、主体、状态、文种或输出模式回退。两份完整稿仍有逐项复述和测算说明腔，属于既有可读性风险；本轮不叠加第二条语言规则。

## 工程验证

- `py -3.13 -m unittest discover -s tests`：350/350 通过。沙箱内首次运行因 Python 临时目录 ACL 出现 149 个 `PermissionError`；在沙箱外按原命令复跑后全部通过，该次失败记为环境噪声。
- `py -3.13 tools/run_real_prompt_ablation.py --baseline-root <1.5.18> --baseline-label 1.5.18 --current-root . --out <out>`：1.5.18 为 108/108，current 为 108/108。
- `py -3.13 evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，Skill 10/10，judge consistency 1.0。沙箱内首次运行因 Node 无法启动系统 Python 产生 20 个环境错误；沙箱外按原命令复跑后无错误。
- `py -3.13 <skill-creator>/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py`、镜像一致性测试与 `git diff --check`：通过。

## 已知边界

- 1.5.19 不宣称普通 ClawHub Skill 自动执行生命周期 Hook；它的修复目标是让普通包保持纯 Skill 边界，消除与该分发面无关的子进程运行时。
- “尚未、未形成、不能”等词在事故调查、行政裁决和明确未决状态中仍可能承担必要事实，不能由脚本按词整体删除。1.5.19 只处理材料、用户和文种均未提出的结论对象；材料原句、法定论证和必要未决状态保留。
- 当前 38 字符减负的语言差异小于单次生成噪声，只把确定性上下文减少和无共性回退作为发布依据。
- 原子结论限定规则不处理一般缓和语、免责声明或范围限定，也不自动把未决状态改成进行态。两份完整稿仍可见重复解释；本轮没有加入“事实只写一次”等新的段落级限制。

## 发布回执

- GitHub：`origin/main=e22b0150666974f38c4ce9c3b75cf6757091e646`；annotated tag object 为 `9ec7b5f2b9f030b680d4f05a9cdb7127518697e7`，解引用提交为 `e22b0150666974f38c4ce9c3b75cf6757091e646`；[v1.5.19 Release](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.19) 已公开，非 draft、非 prerelease。
- ClawHub：dry-run 与正式提交均为 20 个文件，fingerprint `08d9f0ce40fe63e229a5851b9b7ab670b794b23b849e5c724a7ee1f4540c7f17`；正式提交返回 `status=published`、`versionId=k9771r8n90n85g2x6yd4g3gj1x8ax9fs`。首次发布后只读查询仍显示公开 1.5.18，属于索引传播；1.5.18 的 moderation 为 clean，不能写成 1.5.19 已完成审核，也不重复提交。
- skillhub.cn：精确目标 `skillId=70149`；dry-run 返回 `chinese-official-writing@1.5.19`。正式提交返回 `ok=true`、`versionId=147664`、20 个文件、fingerprint `777381b76fdcde18c0e6f4c33c1487245ac6cb55dd6e18959c3a19e5eb48fd7a`、`tags.latest=1.5.19`；review、security scan、content audit 均为 pending。首次公开搜索仍显示 1.5.18，按异步传播处理，不重复提交。

小红书 Red SkillHub 继续排除。提交成功、公开 latest、审核和安全扫描分别记录，不互相推断。
