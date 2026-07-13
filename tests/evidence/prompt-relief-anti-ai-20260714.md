# Prompt 减负与 ANTI-AI 结构优化证据（2026-07-14）

## 范围和回退原则

- 固定上一发行基线：`v1.5.11=59eed9e4a4873082edaaef0c241186583bd68206`。
- 本轮只做本地候选，不升版本、不推送、不发布。
- 任务路由、reference 加载条件、段落/小节/全文复核顺序、输出模式、修改次数、默认联网和发布链保持不变。
- 一次只改一类重复信息；当前候选只要出现基线没有的事实、引用、格式、文种或输出模式回退，就撤销该项修改并保留失败证据。
- 1.5.11 现有证据没有出现三次以上的新 ANTI-AI 共性失败，因此本轮不增加禁词、替换表、固定频次阈值或新的写作规则。ANTI-AI 只允许在不丢语义的前提下做结构去重。

## 外部取证与最小借鉴

- [Agent Skills specification](https://agentskills.io/specification) 明确入口文件会在激活时整体加载，详细资料可按需放入 references；据此优先删除入口中已被叶子 reference 完整承接的重复例子，不移动核心流程。
- [Agent Skills evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills) 建议使用真实 prompt、干净上下文和上一版本基线；本轮固定 1.5.11 做 A/B，不与 no-skill 混比。
- [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) 建议采用明确的分类、成对比较和具体标准；本轮 verifier 只看原 prompt 和匿名输出，按事实、格式、文种和输出模式逐项判定。
- 社区 humanizer 类实现只借鉴“按成簇问题判断、保留语义和正式语域”的维度；拒绝大段替换词表、固定次数门槛、口语化注入、检测规避和自动批量改写。

## 共性风险复核

历史证据中，制作旁白、过程自述、机械重复和事实遗漏曾多次出现，但 1.5.11 已有对应规则和通过复测。当前版本没有达到“三份输出、两个 prompt、两次独立 writer”的新失败项。无前文依据的否定和虚假对比目前是测试输入，不是 1.5.11 写稿中连续复现的新失败。因此本轮不新增行为边界，只消除规则内部的重复解释。

## 第一项：入口 Prompt 减负

### 修改

从 canonical `SKILL.md` 的“常见错误反例”删除两个完整重复例子：

- 旁白式写法例子；
- 教学式写法例子。

两类风险仍由入口中的非正文说明硬边界、视角错位/思考泄露检查，以及按需加载的 `references/anti-ai-patterns.md` 完整覆盖。六个发行镜像通过 `tools/sync_adapters.py` 同步。单句回退方式：恢复上述两个例子并重新同步镜像。

### 确定性验证

- 最大上下文：`24968 -> 24808`，减少 160 字符，仍低于仓库 `<25000` 门槛。
- `python -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation tests.test_promptfoo_eval`：首次和改用仓库 TEMP 的两次沙箱运行均在 Windows 临时目录清理时触发 `PermissionError`，没有断言失败；以允许系统临时目录正常清理的同命令复跑，`75/75 OK`。
- 固定 1.5.11 消融：baseline `108/108`，current `108/108`。
- `git diff --check`：通过；仅提示工作区 CRLF 转换告警。

### 真实 A/B

两名独立 writer 分别只加载当前候选和 detached 1.5.11，覆盖：

1. 稀疏事实的短情况报告；
2. 只审不改、严格四字段输出的旁白/虚假递进/机械重复检查；
3. 含真实否定、数字和服务抖动事实的算力使用说明。

第三名独立 verifier 只看原 prompt 和匿名 A/B：两版三组样本均为 `PASS`。当前候选在标题贴合度和无依据判断覆盖上略优；两版之间没有事实失真、编造、格式破坏、输出模式错误或过程旁白残留等功能性回退。第一项候选保留。

## 第二项：ANTI-AI 结构去重

### 首轮候选及回滚

首轮曾同时删除叶子文件中的总规则复述，并把三处“只审不改/按用户格式输出”合并到一处。文件由 5323 字符降到 4753，定向测试 `75/75`、固定基线消融 `108/108` 对 `108/108`。

真实 A/B 中，独立 verifier 判当前候选在一条审稿建议里把“持续推进”改成“推进”，而基线只建议合并重复，构成候选独有的论断强度回退；两版在另一条改稿中也共同出现同类 `WARN`。按预设回退条件，首轮候选完整撤销并同步六个镜像，没有以单样本追加新禁令或补丁。

### 缩窄候选

第二次只删除 `references/anti-ai-patterns.md` 开头与入口及专项 reference 重复的文种、行文关系、格式骨架、字段、事实、联网和占位符总清单，替换为一条范围分工说明。局部审稿、用户格式、真实否定与比较、事实保真和改写边界均保持原位；不增加新的行为规则。单句回退方式：恢复“网络和社区高频共性风险”清单并同步镜像。

- ANTI-AI 叶子资料：`5323 -> 4802` 字符，减少 521 字符，约 9.8%。
- 定向测试：`75/75 OK`。
- 固定 1.5.11 消融：baseline `108/108`，current `108/108`。
- 两次独立 current writer 和一次固定 baseline writer 覆盖真实比较、必要否定、虚假递进、机械重复、干净文本不动、字段式材料和稀疏报告。独立三方 verifier 判 15 组结果全部 `PASS`，两个 current 输出均无 baseline 独有风险。

缩窄候选保留。首轮暴露的“合并机械重复时可能连同持续性一起删掉”在没有明确材料强度提示的样本中是 current 与 1.5.11 共同风险；本轮没有达到当前候选新增的三次共性门槛，不追加产品规则，继续列为后续观察项。

## 最终验证

- `py -3 -B -m unittest discover -s tests`：`151/151 OK`；完整测试包含 canonical 与五个发行镜像的逐文件一致性检查。
- `npm run eval:official-writing:smoke`：沙箱内三次均在 Node 启动 Python 时失败，前两次分别命中失效 Hermes 路径和 runner 覆盖显式环境变量，第三次已指向真实 Python 3.13 但仍被沙箱拦截；在相同 PATH 和相同命令下允许子进程执行后复跑，`20/20 PASS`、`0 error`、judge consistency `1.0`。
- `py -3 -B tools/run_real_article_eval.py --out output/prompt-relief-anti-ai-20260714/final-real-article`：skill 10 个样本缺失要素 `0/61`、关键词命中率 `100%`、格式/重复/反 AI 风险均为 `0`；9 个匿名占位标签样本仍只作人工线索。
- `py -3 -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 27 批评测上下文最大值：`24808`，低于 `<25000` 门槛；相较固定 1.5.11 的 `24968` 减少 160 字符。ANTI-AI 文件按需加载，不影响这组最大批次统计。
- `git diff --check`：提交前复核通过，仅有工作区 CRLF 转换提示。
