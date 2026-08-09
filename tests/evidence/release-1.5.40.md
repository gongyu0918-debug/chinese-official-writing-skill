# 1.5.40 发布证据

## 当前状态

1.5.40 发布候选已完成版本同步、真实证据复核、发布前工程回归及 ClawHub、skillhub.cn dry-run。正式提交和传播回执在 annotated tag 冻结后补记；小红书 Red SkillHub 不在本次授权范围内。

## 本轮产品改动

相对固定 `v1.5.39`，canonical Skill 的产品正文只有四处差异，共 4 行新增、5 行删除：

1. 将既有“检查终稿正文时使用 `draft-body` 模式”指针从末尾脚本说明纯前移到核心流程第 6 步。没有新增“必须执行”、命令、正则、Hook、FSM、复核次数或自动改稿。
2. `genre-checklist-report.md` 删除“使用事实性汇报语言”后重复的“报告不请求上级批准”半句，前部报告风险仍完整承载文种边界。
3. `genre-checklist-request.md` 删除请示小节第二次完整复述的参考顺序，逐项的请批事项、依据、现状、必要性、经费、安排和请批语仍保留。
4. `review-checklist.md` 删除后段第二个“免责话术”枚举，前段高风险检测以及提示词、隐藏推理、重复标题和明确标识例外均保留。

canonical、Claude Code、Qwen、Agents、Hermes 与 OpenClaw 镜像同步到 1.5.40。仓库在 1.5.39 后另增加外部确定性冻结、字符计数和简单金额关系核验工具及测试；这些是评测控制面，不进入 Skill 运行时 Prompt。

## 本版明确不包含

- 不包含独立成句“不直接代表/不等同于/不意味着”的检测候选 `59ea0def`。
- 不包含把脚本改成“必须执行”、固定命令或跨宿主 Hook 的候选。
- 不包含“材料足够时直接以正文结束交付”的无缺口收口候选。
- 不包含短通知链路减时、纪要单次状态落位、全局分阶段或其他尚在隔离 worktree 的研究项。

## 基线与产品提交

- 固定发行基线：annotated tag `v1.5.39`，解引用提交 `e1de44abefc3ec91f68be55be7abcc616aae105a`。
- 本轮四个产品原子：`3df03cac`、`7ee89106`、`a0c49840`、`85fb5420`。
- 版本准备与首轮发行证据提交：`221d8750ad5c1cc3a0cecfaa0bedb5339a62311b`。
- annotated tag object、tag 解引用提交及回执文档提交在正式发布后补记。

## 真实写稿、真实复核与独立裁决

| 原子 | 真实证据 | 判定 |
| --- | --- | --- |
| 终稿指针纯前移 | `core-lint-pointer-pure-relocation-v1548-result-20260809.md` | Alibaba DeepSeek V4 Flash 0731 与 Luna 固定题复放；Luna Candidate 实际读取终稿叶并删除无锚保护尾句，反向控制保留真实否定边界；`PASS / MERGE` |
| 报告审批边界半句去重 | `review-leaf-exact-dedup-v1546-result-20260809.md` | 两组固定 manifest 真实只审均保持报告功能召回，Candidate 分别小胜和更克制；`PASS / ELIGIBLE FOR CLEAN INTEGRATION` |
| 请示顺序重复去除 | `request-review-sequence-dedup-v1542-result-20260809.md` | 两家 provider、两道只审任务核心召回保持，SOL 四组 `direct_regression=NO`；`BEHAVIOR-EQUIVALENT` |
| 免责话术近场去重 | `review-prompt-nearfield-v1541-real-result-20260808.md` | 三家 provider 六个样本保持三题召回，SOL 三组均难分且无独有硬回退；`BEHAVIOR-EQUIVALENT` |

上述结论按 DIFF 归因：基线共有问题、同提示波动和未读取候选差异的样本不记为候选回退；只有能由差异或实际读取轨迹直接解释的变化才计入裁决。

## 发布前验证（2026-08-09 实跑）

| 验证 | 实际结果 |
| --- | --- |
| 四原子定向测试与镜像边界 | 70/70，通过 |
| `python -B -m unittest discover -s tests` | 457/457，通过 |
| `OFFICIAL_WRITING_EVAL_STUB=1` 的 Promptfoo smoke | 20/20，通过；0 failed、0 errors |
| 固定 1.5.39 确定性消融 | v1.5.39 111/111；current 111/111 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py`、`deterministic_capture.py` 通过 |
| 镜像同步与 `git diff --check` | 通过；另修复一处历史证据 Markdown 行尾空白 |

Promptfoo 使用本地 stub；111 项消融不调用 LLM。两者只证明评测入口、静态支撑和工程结构没有回退，不能替代上面的真实执行与独立质量裁决。

## 发行包

### ClawHub

- 发行目录：`openclaw/skills/chinese_official_writing/`；
- 文件数：32；
- dry-run：`ok=true`、`status=would-publish`，公开基线 1.5.39，目标版本 1.5.40；
- 首轮 dry-run fingerprint：`6a0801ea151a8622e40b2885b39669e23c6244e983b760df43e76f04f4df8300`；最终发布提交冻结后使用精确 SHA 重跑，fingerprint 必须保持一致。

### skillhub.cn

- 清洁包：`output/skillhub-release-1.5.40-20260809/publish-package/`；
- 文件数：31，禁入文件 0，共享内容哈希不一致 0；
- 排除 `agents/openai.yaml`、`references/delivery-review-gate.md`、`scripts/gate_stop_hook.py`、`scripts/review_gate.py`，加入平台 `_meta.json` 和 SkillHub 专用 frontmatter；
- `SKILL.md` 可执行正文与 canonical 逐字一致；
- 内容清单 SHA-256：`3a27babbeb04a493af802dd8d95174c3632626de38aed012b88d665dcc05c280`。算法为：相对路径按序排列，每行 `relative_path<TAB>file_sha256`，UTF-8、LF、末尾保留 LF 后取 SHA-256；
- dry-run：`dryRun=true`，精确返回 `chinese-official-writing@1.5.40`。

## 下一轮剩余项

1. 继续验证无缺口场景的直接正文收口，重点看格式遵循、文后提示过量和短通知链路时延；本版不提前写入规则。
2. 继续隔离验证 `59ea0def` 的精确结构召回及跨宿主真实执行；不得扩大成“尚未、未、不能”等词级禁令。
3. 保护性外扩仍是 P0 观察项；本版只前移已有语义复核入口，不宣称已彻底解决跨模型、跨 Harness 的外扩波动。

平台正式回执取得后，即使公开索引、审核或扫描异步滞后，也不重复提交。
