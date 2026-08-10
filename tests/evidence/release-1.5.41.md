# 1.5.41 发布证据

## 当前状态

1.5.41 发布候选以 `main=61ac47114402bbc9bd51e10e705b8b6ce575f46e` 为固定产品基线，已完成版本面同步。GitHub、ClawHub 与 skillhub.cn 的发布前回归、清洁包 dry-run、正式提交和传播回执按本文件逐项补记；小红书 Red SkillHub 不在本次授权范围内。

## 本轮产品改动

相对固定 `v1.5.40`，canonical Skill 的运行时产品正文只改动 `references/anti-ai-patterns.md` 两行：

1. 将“无前文依据的否定”改为位置无关的“连续否定”检查，覆盖同一句及相邻句中的多个否定分句。
2. 处理动作限定为保留材料明确且与主题直接相关的必要否定、合并同一事项的重复内容、省去主题外围的否定说明；不使用词级禁令，不自动批量替换，不改变事实、对象、否定范围、判断强度或办理含义。

最终 canonical 相对 1.5.40 为 2 行新增、2 行删除，规范化净减 9 个字符。canonical、Claude Code、Qwen、Agents、Hermes 与 OpenClaw 镜像同步到 1.5.41。仓库另增加真实 A/B harness、有效性修正、匿名裁决和确定性评测锚点；这些属于评测控制面，不进入 Skill 运行时 Prompt。

## 本版明确不包含

- 不包含独立成句“不直接代表/不等同于/不意味着”的检测候选 `59ea0def`。
- 不包含把脚本改成强制执行、自动替换、循环修订或跨宿主 Hook 的候选。
- 不包含“材料足够时直接以正文结束交付”的无缺口提示候选。
- 不包含固定二段式、短通知链路减时、纪要单次状态落位、全局分阶段或其他隔离研究项。

## 基线与产品提交

- 固定发行基线：annotated tag `v1.5.40`，解引用提交 `ca69eafb000fc21db69f5a18985683f550076885`。
- 连续否定正向状态承载集成：`dc8733c4`。
- 连续否定全位置减载产品提交：`fcc1d960`。
- 当前发布产品基线：`61ac47114402bbc9bd51e10e705b8b6ce575f46e`。
- 版本准备、发布提交、annotated tag object 和回执文档提交在各阶段冻结后补记。

## 真实写稿、真实复核与独立裁决

| 阶段 | 真实证据 | 判定 |
| --- | --- | --- |
| 连续否定状态承载 | `anti-ai-negative-close-v1541-r3-real-result-20260809.md` | Alibaba Token Plan 与 Ollama Cloud 的 DeepSeek V4 Flash 0731 `max` 同题复放；两家均以“馆务会仅听取相关情况”承载材料状态，保留设备数量、时间、次数及未作采购决定的办理含义，不追加采购、预算、责任或后续动作；独立裁判两组均判 Candidate `PASS`、对照 `WARN` |
| 全位置规则减载 | `anti-ai-continuous-negation-anywhere-v1543-result-20260810.md` | 修正无效样本后，DeepSeek、Luna、Qwen 共 8 个有效配对、16 份有效 final；两名裁判均确认三道目标题无材料外否定分句或连续否定，三个控制题的必要否定、禁令和固定引语均保留，无 Candidate 独有硬回退；`REAL NON-INFERIOR RELIEF` |

Qwen 两个留出配对的整体语言偏好均指向 Baseline，原因是 Candidate 单臂增加通知式引导语、使用“投入试用”和一句不自然停顿；这些变化没有改变事实或连续否定目标计数，也不在本轮差异的直接管辖范围内，按预注册保留为模型/provider 软负信号，不升级为 DIFF 硬回退。

## 发布前验证（2026-08-10）

| 验证 | 实际结果 |
| --- | --- |
| 连续否定聚焦测试与镜像边界 | 4/4，通过 |
| `python -B -m unittest discover -s tests -p 'test_*.py'` | 458/458，通过 |
| `OFFICIAL_WRITING_EVAL_STUB=1` 的 Promptfoo smoke | 20/20，通过；0 failed、0 errors |
| 固定 1.5.40 确定性消融 | v1.5.40 110/111；current 111/111；唯一差项为旧版没有 P109“连续否定”语义锚 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py`、`deterministic_capture.py` 通过 |
| 镜像同步与 `git diff --check` | 同步前后 diff object hash 一致；六份 anti-AI reference SHA-256 均为 `9D9E129919644819A995CD154672B24B9AC4E72158BA4CBCBDD60C28F71EE32B`；`git diff --check` 通过 |

Promptfoo 使用本地 stub；111 项消融不调用 LLM。两者只证明评测入口、静态支撑和工程结构没有回退，不能替代上面的真实执行与独立质量裁决。

## 发行包

### ClawHub

- 发行目录、文件数、dry-run fingerprint 和正式回执待发布提交冻结后补记。

### skillhub.cn

- 清洁包路径、文件数、排除项、内容清单 SHA-256、dry-run 和正式回执待发布提交冻结后补记。

## 下一轮剩余项

1. 继续隔离验证 `59ea0def` 的精确结构召回及跨宿主真实执行；没有真实执行证据前不合入。
2. 继续验证无缺口场景的直接正文交付、给定材料格式遵循、文后提示数量和短通知链路时延。
3. 固定二段式表达、纪要单次状态落位和分阶段加载继续保持原子隔离，不与本版连续否定规则捆绑。

平台正式回执取得后，即使公开索引、审核或扫描异步滞后，也不重复提交。
