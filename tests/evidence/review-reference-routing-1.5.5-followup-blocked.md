# 1.5.5 reference 路由复核与 1.5.6 发布阻断记录

日期：2026-07-10

## 范围与基线

- 仓库：`F:\Workspaces\chinese-official-writing-skill`
- 上一发行基线：tag `v1.5.5`，commit `dd4c6d66ce31d91e65c6e1d11de3e4e80885b4ba`
- 当前远端文档头：`origin/main=a777e3a75a964bdc3ee4daccbb1a6e708736623f`
- 固定 detached 基线：`output\release-baselines\github-1.5.5`
- 本轮使用 `gpt-5.6-luna` 做真实 writer/verifier，`gpt-5.6-sol` 只做代码与 prompt 冷审，不让 Sol 代替真实写稿。
- 版本号保持 `1.5.5`；未创建 `v1.5.6` tag，未推送 GitHub、ClawHub 或 SkillHub。

## 保留的最小修改

1. 只保留根目录 `AGENTS.md` 作为接手入口，删除过期 `agent.md`。
2. 区分普通口语正式化和明确字面引用：普通叙述可正式化；引号、原文、引语或逐字保留内容才按字面保护。
3. 轻量路由卡在能够覆盖任务时终止；完整骨架、长文、多材料、专项论证和 Word/GB/T 9704 请求再升级 reference。
4. playbook 改为可从入口直接到达的叶子资料，反 AI 和 review 资料不再反向启动整套总审链路。
5. Promptfoo provider 不再静默截断上下文；按文种和任务升级 playbook、workflow、办理要素或格式 reference；缺文件和超预算显式失败。
6. provider 缓存键纳入真实命令模板、批大小、超时、重试和任务触发的 reference，避免不同评测配置复用旧缓存。
7. 用户只要求正文且没有同时允许文后提示时，不附待确认、风险、核验或自证说明；用户只允许某一类提示时，只附该类内容。

对应本地提交：

- `e2702f7`：字面边界、交付命令和单一接手入口。
- `f0639df`：reference 渐进式路由和无环结构。
- `9891159`：评测 provider 完整载入与显式失败。

## 词语分歧取证规则

A/B 出现近义词、情态词或固定搭配分歧时，不按模型票数直接裁决，也不只比较搜索结果总数。先限定同一文种、同一语义和同一责任状态，再优先检索政府网站、公开政策文件和专业公文资料，记录真实上下文。

本轮检索显示：

- `将落实` 可用于已经决定、后续确定执行的动作，不应机械判错。国家体育总局公开材料可见“将落实政策责任”等用法：<https://www.sport.gov.cn/bgt/n4961/c644273/content.html>
- `拟落实` 多用于拟议、计划或尚未最终确定的状态。灌南县政府公开方案可见“拟落实新项目时间”：<https://xxgk.guannan.gov.cn/news/show-25786.html>
- `拟提请` 等表达也用于尚待审议的程序状态：<https://www.beijing.gov.cn/zhengce/gwywj/201905/t20190522_61370.html>

结论：优先依据原材料的决定状态选择“将、拟、尚未决定”，搜索频次只作方向性证据。本规则只用于 review/评测取证，不扩大 skill 默认联网范围。

## 真实 A/B

### 六任务直接 skill / provider 对照

任务覆盖：

- 请示只输出正文，缺主送、落款、日期，不得附待确认。
- 通知只允许正文后列“联系人待确认”。
- 已决定事项起草决定。
- 尚未决定事项改写，必须保留“拟、尚未决定”。
- 600—800 字多材料阶段报告。
- Word/GB/T 9704 最终用途下的流式纯文本通知。

writer：

- 直接 1.5.5 基线：`019f489d-1247-7b21-ba8f-09b7f75e9605`
- 直接当前候选：`019f489d-266e-78e3-8130-6c2b116e5f97`
- 旧 provider 上下文：`019f489d-3b19-7953-b34b-3382e3f5bd48`
- 新 provider 上下文：`019f489d-4f27-7330-b8f1-b77a4cccb1d8`

独立 verifier：

- `019f489f-542c-7502-ac2c-aef5a866e76f`
- `019f489f-6852-7c60-8c67-5658d1b3787d`

共同结论：

- 请示、通知、决定、未决事项和流式正文均通过；未把普通正式化误判为字面破坏，也未机械判定“将落实”错误。
- 直接 skill 的基线和候选都在 600—800 字稀疏合稿中明显不足 600 字；候选还出现“当前材料未进一步说明”等正文旁白，直接候选相对基线不占优。
- 新 provider 相对旧 provider 明显改善：旧 provider 漏掉 S6，且 S5 大量写入材料读取旁白；新 provider 完成 S6，S5 仅保留篇幅不足和轻度旁白风险。

### 900 字与 3000 字以上合稿

基线/当前 writer：

- 900 字基线 `019f48a1-1896-7e42-9bce-c1c85457e545`，当前 `019f48a1-2cb7-7992-845e-e7a9613467ce`。
- 3000 字以上基线 `019f48a1-4207-7462-8e39-73bdac30cf6f`，当前 `019f48a1-5604-7311-97ca-a3caf95957e7`。

基线和当前都可复现正文旁白，包括：

- “现有材料没有统计每件事项重复录入所需时间……”
- “现有材料未涉及云资源使用情况……”
- “材料没有供应商评分、采购方式或立项批复……”
- “本次调研涉及……五方面材料……”

这说明问题并非本轮候选单独引入，但按用户最新标准，思考链、材料读取状态、自证句或无关外语残片一次出现即可阻断发布。

## 失败且已回滚的 prompt 实验

先后尝试并真实复测四种 prompt-only 最小方案：

1. 明示禁止思考链、英文 process note 和“材料未说明”。
2. 要求将输入边界改写为“相关数据尚未统计”等业务对象状态。
3. 增加一次静默正文纯净检查。
4. 增加一次独立静默净稿，只删旁白和外语残片，不改事实结构。

测试覆盖稀疏 600—800 字、材料较充分 900—1100 字和 3000—3500 字多附件合稿。个别短稿或中等篇幅一度改善，但 3000 字稿仍多次出现“现有材料没有/未说明”等读取状态；一次稀疏稿末尾还出现无关外语残片。

最终独立 verifier `019f48b4-1433-79e3-b9a1-71a6c132770b` 对四个原句逐项判定 `FAIL`，结论为发布阻断。四种 prompt 实验及其确定性 P102 守卫已全部回滚，canonical 和镜像中无残留，不把未通过方案包装成修复。

## 工程验证

- `python -B -m unittest discover -s tests`：`121/121` 通过。
- `python -B .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.5 --baseline-label baseline-1.5.5 --current-root . --out output\real-prompt-vs-1.5.5-local-candidate-rerun`：baseline `95/101`，current `101/101`。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过。
- `npm run eval:official-writing:smoke`：沙箱内两次因 Promptfoo 无法启动外部 Python 而 20 errors；受控权限下以 Python 3.13 重跑后 `20/20` 通过，judge consistency `1.0`。
- `git diff --check`：通过，仅 Windows 换行提示。

Promptfoo smoke 使用 stub writer/judge，只证明确定性评测入口，不替代上面的真实 writer/verifier。

## 发布决定

`1.5.6` 不发布。没有改版本号，没有 tag，没有 push，没有调用 ClawHub 或 SkillHub 发布。

ClawHub 官方当前文档入口使用 `clawhub skill publish <path>`，本机 CLI 为 `0.23.1`，帮助文本也支持该命令：<https://docs.clawhub.ai/>。本轮由于产品级真实写作门槛失败，不进入发布命令验证和三平台实况核验。

下一轮不应继续向 `SKILL.md` 堆同义禁令。可行方向只剩两个：

1. 把“首稿 -> 独立净稿”做成真实二次 agent 交互，并证明它不是单次生成中的伪两遍提示。
2. 在用户允许改变边界后，增加可选 final-draft verifier；仍不得用脚本直接清洗正文，也不得把 verifier 伪装成默认首稿能力。
