# Candidate BC：报告检查项原子拆叶预注册

固定底座：Candidate BB 产品提交 `ed803c4`；本研究分支同时保留其结果记录提交 `21c7e4a`。本候选不改版本号、不发布。

## 单变量与精确 diff 计划

本候选只把 `references/genre-checklist.md` 的“报告”小节原文移入同级叶子 `references/genre-checklist-report.md`。`SKILL.md` 增加报告专用直达入口，报告 playbook 的补充读取改为指向该叶子。其他文种仍读取原 `genre-checklist.md`，规则内容和顺序保持不变。

| 场景 | Candidate BB | Candidate BC |
| --- | --- | --- |
| 报告/情况说明起草与细查 | `SKILL.md` + 报告 playbook；需要细查时读取含全部文种的 `genre-checklist.md` | `SKILL.md` + 报告 playbook；需要细查时只读取 `genre-checklist-report.md` |
| 通知、纪要、请示等其他文种 | 按原路由读取对应 playbook 和 `genre-checklist.md` | 完全不变 |
| 文种不明或跨文种复核 | 按原条件读取通用路由和清单 | 完全不变 |
| 成稿后复核 | 按原条件读取复核材料 | 完全不变 |

同步调整只限 canonical、发行镜像、叶子存在性和路由锚点测试。预计报告细查路径减少约 3000 字符；默认不命中报告时不增加新叶子负担。

## 明确不改

- 不改报告 playbook 的适用范围、骨架、风险说明和事实约束。
- 不改信息选择、文种判定、用户模板、篇幅预算、段内写法和输出模式。
- 不改复核顺序、修改次数、脚本、正则、FSM、标记协议、回退逻辑和发布链。
- 不拆通知、纪要、请示或其他文种，不顺手压缩措辞，不加入 ANTI-AI 新规则。

## 验证计划

先运行全量 unittest、Promptfoo smoke、quick validate、镜像一致性、以 Candidate BB 为固定基线的确定性消融和 `git diff --check`。工程验证出现 Candidate 新失败即停止真实写稿。

工程门通过后最多做 3 组报告类自然 A/B。Candidate BC 与 Candidate BB 使用同模型、同推理档位和逐字一致原始输入，各取首个技术有效输出，不补抽。writer 与 blind judge 相互独立，judge 只看原任务和匿名稿。

验收要求：三题均无事实、数字、日期、主体、状态、文种、格式、篇幅或输出模式回退；至少 2/3 题 Candidate BC 与 Candidate BB 持平或更优，且没有 Candidate 独有的保护性外扩或直接修改成本上升。持平视为拆分通过，不以成稿字数长短单独判优。

结果为 `PASS`、`MIXED` 或 `FAIL`。通过才进入 1.5.20 发布候选；失败只撤回 Candidate BC，保留 Candidate BB 作为 1.5.20 底座。
