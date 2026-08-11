# 三原子当前 main 组合验证结果（2026-08-01）

## 结论

`PASS / MERGEABLE / NO RELEASE IN THIS TURN`。

固定基线为 `6bd6c6762a6ccf6b42c378a3990c093db43804ab`。组合只包含新闻评论 R3、工作总结逐字物理拆叶和入口固定余量删除三个已冻结原子；三项来源补丁均无冲突机械移植，工程回归全部通过。预注册的一题组合 sanity 也已完成：两稿硬边界均 PASS，组合稿满足篇幅且无 P0，匿名盲审判固定 Baseline 小胜。该软负项集中在一次相邻事实复述，没有达到三场景共性门槛，也没有可追溯到新增语义规则的机制，不为单篇追加 Prompt。

本分支具备合入本地 main 的条件；本轮不改版本号、不发布、不推送。

## 提交与差异追溯

- 组合预注册：`5a9c2734`。
- 新闻评论组合产品：`3036618f`，来源 `ba59011f`。
- 工作总结组合产品：`4a8a2f6d`，来源 `755177b6`。
- 固定余量删除组合产品：`46897a62`，来源 `2d006905`。

stable patch-id 核验：

| 原子 | 来源 / 组合 patch-id | 结果 |
| --- | --- | --- |
| 新闻评论 R3 | `ffcc9452e83e98df0e3664fc6e0aa118798691ce` / 同值 | PASS |
| 工作总结逐字拆叶 | `6ac1f23eb79b6d235ffac01d56232925aa0c3a4d` / 同值 | PASS |
| 删除入口固定余量 | `8c7533c6798738b7f7619d1e48acc44e01868f67` / 同值 | PASS |

独立只读 diff 审计进一步确认：三个来源补丁文件并集与组合产品提交的文件集合相同，双方集合差异为 0；未混入第四项产品规则。

## 三项组合不变量

### 1. 新闻评论 R3

- canonical 新闻评论叶 Git blob 为 `662104ea0ba040911d0815a8db5c02e2c3247e1f`，与来源 `ba59011f` 相同。
- canonical 与五个发行镜像的工作区 SHA-256 均为 `44e4055b1d2a3b85c034d262c631e1fb23b8eb400d9ded77074c7f05b1e8c89f`。
- 只在既有“一次局部复核”句中增加评论推演的事实依据、适用范围和判断强度核对；新闻评论路由、骨架和复核次数未变。

### 2. 工作总结逐字物理拆叶

- 新叶 Git blob 为 `d952abb4dcf38b9b03295077d3a488c41dc2dcea`，删段后的通用 playbook blob 为 `1762062a90a96a0f7351829bea86da33a5d7544f`，均与来源 `755177b6` 相同。
- 独立审计将固定基线原段与新叶正文按 Ordinal 比较：均为 340 字符、7 行，结果为相同，无逐行差异。
- canonical 与五个发行镜像的新叶 SHA-256 均为 `8a52a0c31edda8a2c3ab94769b2f5c9d867cd5ed1f80cd20ccb0a79c3a10226d`；通用 playbook 均为 `4e9ddd112a7eb540b3cb68cd1de98bc4970a68e3cce85dcbccd413b269817d8f`。
- 真实 provider 加载集合由 `SKILL.md + genre-playbooks.md` 改为 `SKILL.md + genre-playbook-work-summary.md`；包含加载标题包装的上下文由 14,192 字符降至 11,005 字符，减少 3,187 字符，减载 22.46%。

### 3. 删除入口固定 5%—10% 余量

- 六个 `SKILL.md` 各减少 13 个字符，短语计数均由 1 降为 0；仍保留“字数自检”和“尽量压到限制内”。
- 六个 `references/workflow.md` 的 `5%-10% 余量` 均仍保留 1 次，明确硬上限场景的安全规则未被删除。
- 未新增达到下限、展开、补写或二次修订规则。

## 实际工程验证

| 验证 | 结果 |
| --- | --- |
| 三原子 focused unittest | 9/9 PASS |
| `python -m unittest discover -s tests` | 407/407 PASS |
| `npm run eval:official-writing:smoke` | 20/20 PASS，0 error |
| 固定 `6bd6c676` 确定性消融 | current 110/110；baseline 109/110。baseline 仅在新增的 P075 工作总结专叶路径断言失败，属于产品新增覆盖，不是 current 回退 |
| `quick_validate.py chinese-official-writing` | PASS，`Skill is valid!` |
| `python tools/sync_adapters.py` | 完成同步；重新暂存行尾归一化后无实际内容 diff |
| 镜像字节一致性专项 | 2/2 PASS |
| reference graph | PASS，缺失引用 0 |
| 三项关键 reference 六包 SHA-256 | 各文件六包完全一致 |
| `git diff --check` | PASS |

Promptfoo 提示本机 `promptfoo 0.121.11` 低于可用的 `0.121.20`，但本轮 20 项均实际完成并通过；未在组合候选中升级依赖。

确定性消融输出位于忽略目录 `output/final-three-atom-ablation-20260801/`。该消融不调用 LLM，只证明包、路由、引用和评测入口无回退。

## 来源证据复制核验

最终提交原样带入四份来源结果证据；复制后 Git blob 与来源分支逐一相同：

| 证据 | Git blob |
| --- | --- |
| `news-commentary-r3-main-integration-result-20260801.md` | `15f0744c79a0f0fc5a9c57fbeb8e270206d993ed` |
| `work-summary-current-main-integration-result-20260801.md` | `81dbbc7e8aabcc723b93fe55148815f6ad889ee9` |
| `candidate-length-headroom-delete-only-current-main-v1531-engineering-result-20260801.md` | `717d1aa16f3c96247f0633d9d448752ac15f160c` |
| `candidate-length-headroom-delete-only-current-main-v1531-real-ab-result-20260801.md` | `8718fb05eb1fc1583583eb99924c28d761e36bb8` |

这些原始结果分别记录：新闻评论 R3 的三对匿名收益与证据限制；工作总结逐字拆叶的真实证据继承和减载；固定余量删除的工程门及三题真实 A/B。组合结果不改写其中结论。

## 一题组合真实 sanity

### 对象与运行

- 任务：LH03 工作总结改稿，保留标题、三部分结构、全部数字、时间、进展和三项下半年安排，要求 1000—1100 字。
- 组合 Candidate：本分支 `7d735321`，按 `SKILL.md -> information-selection.md -> workflow.md -> genre-playbook-work-summary.md -> argument-chains.md -> final-review-layers.md -> proofreading-checklist.md` 读取。
- 固定 Baseline：复用 `6bd6c676` 在 deletion-only A/B 中已经生成的一次首稿，不重新生成。
- Candidate writer 由编排层指定 `gpt-5.6-terra/high`，generation=1、revision=0、resample=0；输入和输出 SHA-256、实际读序有回执。
- 匿名 judge 只读取 task/A/B，未读取 mapping、hard verifier、receipt、git 或候选说明。

统一按去除全部空白字符计数：Candidate 1015，Baseline 1059，两稿都在 1000—1100 范围内。匿名包装阶段的 hard verifier 曾同时列出“仅去末尾换行”的 1035/1083 口径；该口径不用于最终判定，结论不受影响。

### 结果

| 稿件 | 硬核验 | 匿名语言结论 |
| --- | --- | --- |
| Candidate | PASS；事实、数字、日期、主体、状态、标题、三部分结构和三项安排完整；无 P0 | 小负；若干工作事项后紧跟一句同义概括，机械复述略多 |
| Baseline | PASS；同上；无 P0 | 小胜；也有段末概括和套语，但重复主要集中于收束处 |

匿名映射为 A=Baseline、B=Candidate。两稿差异属于直接使用成本上的轻微波动：Candidate 的“依次完成接口梳理、分批改造和联调”“各类流程均纳入本次升级范围”等句子重复相邻事实，但没有新增事实、责任、程序或承诺，删除后正文仍完整。

### 因果与判定

1. 组合稿没有出现事实、数字、状态、文种、格式、篇幅、输出范围或 P0 回退，三原子交互的硬边界通过。
2. 工作总结新叶与固定基线原段逐字相同，只改变物理加载范围；本题的一次机械复述没有对应新增 Prompt，也没有在三个正常场景形成同一 Candidate 独有机制。
3. 旧工作总结 A/B 的软差异机制并不一致；本题不能把单次 Baseline 小胜升级为 22.46% 减载的因果失败。
4. 按“只有与 diff 相关的回退才计负、同机制三场景才升级共性风险”的既定口径，本题记为软观察项，组合保持 `PASS`。不补抽、不一例一修。

## 剩余风险与停止边界

1. 新闻评论既有 A/B 的精确模型和 thinking 未由 writer 回执独立回显，仍属二级运行证据；组合工程通过不消除这一证据限制。
2. 工作总结拆叶证明加载减负且未发现共性可归因回退，不代表它稳定提升语言质量；组合 sanity 的相邻事实复述作为软观察保留。
3. 固定余量删除的三题 A/B 支持篇幅服从改善，但篇幅合规不等于语言质量稳定；本组合不继续调整 `workflow.md` 或增加扩写规则。
4. 当前没有 true No-Skill 或跨模型组合胜率；本轮结论是相对固定 main 的非负合并资格。
5. 任何后续修改新闻评论叶正文、工作总结叶正文/加载集合、篇幅复核顺序或 `workflow.md` 余量规则，都会超出本次证据继承范围，需要重新验证。

综合判定：三原子组合的产品差异、镜像、引用、工程入口和一题真实交互均达到合入本地 main 的条件；不在本分支继续扩规则。
