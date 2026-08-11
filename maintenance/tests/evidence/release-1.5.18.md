# 1.5.18 发布证据

日期：2026-07-20

## 变更边界

1.5.18 以 `v1.5.17=ddb8dc8dc82255c4a71b02ce3ae1e0a0ec0825ce` 为固定功能基线，只纳入两项已经单独验证的改动：

- 删除 `SKILL.md` 入口内重复的文档清单和复核说明，字符数由 10759 降至 10191，减少 568 个字符，降幅 5.28%。文种路由、事实边界、用户模板、篇幅预算和输出模式保持不变。
- 为支持生命周期 Hook 的 Codex 插件提供一次有限交付复核。流程固定为 `detect → prepare → finalize → emit`，最多一次局部修订；异常、超时或事实不变量失败时选择非空 D0，不进入循环。

ClawHub 与 skillhub.cn 的技能包携带检测脚本和复核说明，但商店宿主不会自动注册仓库根 Hook。自动生命周期触发仅作为 GitHub/Codex 插件面能力发布。

## 真实写稿

入口减负使用三个自然日常任务，Candidate 与固定 1.5.17 使用相同模型、thinking 和逐字一致输入，分别覆盖运行报告、供餐通知和会议纪要。各题只取首个技术有效输出，独立匿名盲审结果为 Candidate 3/3 明确优于 1.5.17；三稿均未出现事实、数字、日期、主体、状态、文种、格式、篇幅或输出模式硬回退。

Hook 使用一篇既有 1600—1900 字试运行报告做真实 D1 闭环。事务 `d4f4bb93-1180-4b06-a8be-063e96f3d4f7` 各执行一次 detect、prepare、mechanical check、semantic verify 和 emit，最终状态为 `TERMINAL_D1`。D1 保留全部数字、日期、主体和未决状态，删除无材料依据的结果性否定，非空白字符 1719。未校准审稿把同一事项的“正在核查”判为新增动作；按统一事实口径复核后确认该句没有新增主体、方法、结果或承诺，属于进行态保留未决状态。两份意见均留档，发布采用统一口径裁决。

## 工程验证

- `python -m unittest discover -s tests`：349/349 通过。
- `python tools/run_real_prompt_ablation.py --baseline-root <1.5.17> --baseline-label 1.5.17 --current-root . --out <out>`：1.5.17 为 108/108，current 为 108/108。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，Skill 10/10，judge consistency 1.0。
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py`、`git diff --check`：通过。

## 已知边界

- 生命周期 Hook 的自动触发取决于宿主插件支持；普通 Skill 目录、ClawHub 和 skillhub.cn 仍按 Markdown 路由与随包脚本运行。
- 正则只处理已经证明安全的保护性外扩子集。混合事实、数字、责任或未决状态的句子由 Agent 语义裁决，脚本不做一刀切删除。
- 真实 D1 只覆盖一篇长报告，证明有限状态机能够完成一次有效修订，不代表所有宿主或所有文种都会进入 D1。

## 发布回执

- GitHub：`main` 已快进到 `9822aaee30df89c479a4e8c94c478424f6d426e3`；annotated tag `v1.5.18` 已推送，Release 为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.18`。
- ClawHub：正式提交返回 `status=published`、`versionId=k97865b6s05pt2g316qb0sqftd8axg46`、23 个文件、fingerprint `4ee56cff53aaf260255e07739efa6b962a44c0e366f59ab21e6d81f73ff4fe41`。首次公开查询仍显示 1.5.17，moderation 为 clean；该 clean 状态对应当前公开版本，不推断为 1.5.18 已完成扫描。
- skillhub.cn：向既有 `skillId=70149` 提交一次，返回 `ok=true`、`versionId=147406`、23 个文件、fingerprint `57d1e018e85e4bad3ecfb46d0a4b87348fa3fa4c2fee47d335ba84b33191c458`、`tags.latest=1.5.18`。review、content audit 和 security scan 均为 pending；首次公开搜索仍显示 1.5.17。

两家商店的公开索引处于异步传播，只继续只读核验，不重复提交。未返回的来源、扫描和审核字段按 `unavailable` 或平台实时状态记录。
