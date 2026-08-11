# 1.5.27 发布证据

## 范围

1.5.27 以
`v1.5.26=50afb5ffd9be88327ad1b4dd25d87c1377d39de9`
为固定产品基线，只发布三项可独立复核的改动：

- 普通函起草，以及错字、标点、格式和明确局部措辞修改，读取
  `genre-playbook-correspondence.md`；
- 涉及事务动作、状态、条件、范围或结构的实质改稿，继续读取完整
  `genre-playbooks.md`；
- `prose_lint.py` 的圆括号占位检测只识别“待确认、待补充、待填写、
  待签发”等完整占位表达，正常办理要求不再因“确认、补充”等词误报。

`tools/check_ab_provenance.py` 及配套测试只用于区分严格可比与探索性 A/B，
不改变写稿行为。失败的调研/可研叶、未验证的社区借鉴和其他研究 worktree
均未合入本版。信息选择、事实边界、文种功能、用户模板、篇幅预算、输出模式、
复核顺序、Hook、FSM、修改次数和回退链保持不变。

候选产品提交为
`875786168187242bd9a57a451df3765efea4e8e7`。版本面使用
`tools/sync_adapters.py` 同步到 canonical、五套发行镜像、OpenClaw 展示面和
Claude 插件。

## 可复核净收益

| 普通函起草路径 | 1.5.26 | 1.5.27 | 变化 |
| --- | ---: | ---: | ---: |
| 命中文种 reference | 3529 字符 | 852 字符 | -2677，约 -75.86% |

普通函专用叶只保留适用条件、正文骨架、平行商洽语气、反馈要素和文种风险。
复函、征求意见函及实质改稿继续走原完整 playbook，没有被一并减载。

括号占位修复中，三个正常办理指令不再误报；八类真实占位仍全部命中。该修复
只改变检测结果，不自动改写正文。

## 真实 A/B

### 历史扩展验证

普通函叶的扩展自然任务曾得到 5 胜 1 负；唯一负项为实质改稿中核心事务动作
弱化。该题同机制复放为持平；随后按任务性质把实质改稿恢复到完整 playbook，
三题结果为 1 胜 2 平。集成回归同时覆盖普通函起草与实质改稿，两题均通过
事实、文种和路由检查。

早期运行没有可直接核验的实际模型和 reasoning，因此这些结果只作为探索性
证据，不单独承担发布结论。

### 发布前严格复验

发布前追加 F04 普通函起草、F06 实质改稿两题。Candidate 与固定 1.5.26
使用逐字一致输入，各取首个技术有效输出，不补抽、不二次修订。

- 原始 rollout 复核确认两组均使用 `gpt-5.6-sol`、`high`；
- 两组宿主指令各由 9 个同序部分组成，SHA-256 均为
  `5e6a3e3ab3a06933ce78db71e4d1fc39c15c8d1c756fa885d301fe8008453304`；
- F04 任务哈希均为
  `d380e8ffae59136bc0d19f5b88801b7159325cbf59c5d672d9785e6777099e5a`；
- F06 任务哈希均为
  `e07e86a45046637b6857484fad31811034afdbfa95bad903ab0e573efa7e4d8c`；
- Candidate 实际读取普通函专用叶；Baseline 读取完整 playbook；F06 两组均
  读取完整 playbook；
- 四稿经 `prose_lint.py --json --format --structure --delivery-mode
  draft-body` 扫描，结果均为空。

匿名映射为 F04 A=Candidate、B=Baseline，F06 A=Baseline、B=Candidate。
独立盲审结论：

- F04：Baseline 小胜，两稿硬边界均通过；
- F06：Candidate 小胜，两稿硬边界均通过；
- 汇总为 Candidate 1 胜 1 负；四稿的事实、数字、日期、主体、状态、文种、
  格式、输出范围和保护性外扩检查全部通过，没有发布阻断项。

一胜一负集中在标题和分段等轻微直接使用成本，没有稳定指向同一规则机制。
本轮结论是普通函起草路径减少 75.86% 文种 reference 后，严格小样本写作质量
与固定 1.5.26 持平；不外推为全部文种胜出。本轮没有重新生成 true
No-Skill。

## 发布级工程验证

- `python -m unittest discover -s tests`
  - 结果：390/390，`OK`。
- `python tools/run_real_prompt_ablation.py --baseline-root
  <1.5.26-product> --baseline-label v1.5.26 --current-root .
  --out output\release-1.5.27-ablation`
  - 结果：固定 1.5.26 为 108/110，Candidate 为 110/110；固定基线只缺本版
    新增的 P110、P111 普通函路由断言。
- `python <skill-creator>\scripts\quick_validate.py chinese-official-writing`
  - 结果：`Skill is valid!`。
- `PROMPTFOO_PYTHON=<bundled-python> npm run eval:official-writing:smoke`
  - 结果：20/20，0 failure，0 error；skill 10、baseline 0、tie 0，
    judge consistency 1.0。
- `python tools/sync_adapters.py` 与 `git diff --check`
  - 结果：镜像同步，diff 检查通过。

第一次全量单测发现 README 的发布计数断言仍固定为上一版 372/372 和 108/108，
同步为本版实际计数后全量通过。Promptfoo 在沙箱内首先尝试了失效的 Hermes
Python 路径，20 项均未进入产品逻辑；改用工作区提供的 bundled Python 后同一
命令通过。两者分别记为维护断言和运行环境问题，不改写成产品失败或通过。

## 发行包预检

- ClawHub dry-run：`status=would-publish`、27 个文件、fingerprint
  `fc858580413bbb293f5c1cc9043c1b554e731e954accc5e8b62402c420260257`；
- skillhub.cn dry-run：`dryRun=true`、`slug=chinese-official-writing`、
  `version=1.5.27`，临时包 26 个文件；
- 两个发行面均不携带 `delivery-review-gate.md`、`review_gate.py`、
  `gate_stop_hook.py`、tests、output、缓存或 `.pyc`。

skillhub.cn 的第一次临时包包含了本版不应发布的门禁文件，未进入 dry-run 或
上传；核对后按白名单重新构建。清洁包首次 dry-run 只因缺少平台必需的 `slug`
被拒绝，随后仅在临时包 frontmatter 中补齐 `slug` 和 `displayName` 后通过，
canonical 没有因此增加平台专有字段。

## 剩余风险

- 新增严格 A/B 只覆盖普通函起草与实质改稿，不能外推为全部文种或长稿；
- 普通函历史扩展验证缺少可直接核验的实际模型字段，只作探索性补充；
- 本轮没有新增 true No-Skill，对无 Skill 的质量比较继续使用既有公开证据；
- 正常括号指令与待办占位的边界由完整词形区分，新的低频表达仍可能需要后续
  真实样本校准；
- 平台发布、公开传播、审核和扫描状态在正式提交后分别补录，不以一个字段代替
  其他字段。

## 发布状态

- 产品发布提交：
  `cfd7bd039e5655ba3e9fe7680206b520d7582072`；
- annotated tag object：
  `16157ecd43ffa0243ec0a98d14c807fcf839d60e`，解引用到产品发布提交；
- GitHub `main`、`v1.5.27` 和正式 Release 已公开，Release 为非 draft、
  非 prerelease：
  <https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.27>；
- ClawHub 只正式提交一次，回执为 `status=published`、
  `versionId=k975tks2z718b0fe459ngk72gh8bdtbe`、27 个文件、fingerprint
  `fc858580413bbb293f5c1cc9043c1b554e731e954accc5e8b62402c420260257`。
  随后的公开查询已显示 `latestVersion.version=1.5.27`、
  `tags.latest=1.5.27`、版本总数 74，moderation 为 `clean`；
- skillhub.cn 只正式提交一次，回执为 `skillId=70149`、
  `versionId=175859`、26 个文件、fingerprint
  `c1c7c31952c09a0098ab7cdd757af9076d095a3f1444708373ed6950b0a93b33`、
  `tags.latest=1.5.27`；review、security scan 和 content audit 均为
  `pending`。首次公开搜索和精确项目 API 的 `latestVersion` 仍显示
  1.5.26，但精确项目的 `tags.latest` 已为 1.5.27；
- 两家商店均未重复发布。skillhub.cn 的异步索引传播与审核状态只记录现状，
  不把 1.5.26 的安全报告推断为 1.5.27 的审核结果。
