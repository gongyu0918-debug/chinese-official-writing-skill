# 1.5.38 发布证据

## 当前状态

1.5.38 已完成 GitHub、ClawHub 和 skillhub.cn 各一次正式提交。GitHub `main`、annotated tag `v1.5.38` 和正式 Release 的产品提交均为 `c3fa2128ef9426b4ebb135986a7e19feccf08421`；发布回执记录作为后续文档提交推进 `main`，不移动发布 tag。ClawHub 公开详情已切换到 1.5.38；skillhub.cn 的 `tags.latest` 已切换到 1.5.38、正文详情仍在异步传播，不重复提交。

## 本轮改动

- 删除入口中的五个关键名词示例（“反馈渠道”“联系人”“原因分析”“问题清单”“每周反馈”），保留“用户给出的关键名词和结构标签一般保留原词，不能只用泛化近义词带过”承重规则；示例在 `references/workflow.md` 与复核清单中仍有承载。
- 将“命中 `references/task-route-cards.md` 且卡片能够覆盖任务时，在轻量卡早停”改为“由卡片完成，不再读取长 reference”，路由条件不变。
- canonical、Codex、Claude Code、Qwen、Hermes、OpenClaw 镜像及展示元数据统一到 1.5.38。
- 不改变文种路由、reference 加载条件、篇幅规则、输出模式、复核顺序、脚本、Hook 或回退方式。

## 基线与提交

- 固定 1.5.37 产品基线：`5d166a8d671fcb0bd96e66aec8e944ccbdf3c0d4`（GitHub annotated tag `v1.5.37` 解引用提交）。
- 已合并入口清晰化两项原子：`370a2bfd`（关键名词示例压缩）、`84292368`（轻量卡加载边界显式化）；整合证据：`317fdff0`。
- 版本面同步：`a2e8ac050035dc6be5315b7ad5ca6ce65ae5ea6c`。
- 产品提交（本地候选记录）：`c3fa2128ef9426b4ebb135986a7e19feccf08421`。

## 合并后验证（2026-08-07，opencode 工作区实跑）

| 验证 | 实际结果 |
| --- | --- |
| `python -m unittest discover -s tests` | 442/442，通过 |
| `npm run eval:official-writing:smoke`（OFFICIAL_WRITING_EVAL_STUB=1） | 20/20，通过；0 failed、0 errors |
| 固定 1.5.37 确定性消融（`tools/run_real_prompt_ablation.py`，基线 worktree 为 `v1.5.37` detached） | v1.5.37 111/111；current 111/111 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py` 通过 |
| `python tools/sync_adapters.py` | 重复执行后无语义差异，镜像同步幂等 |
| `git diff --check` | 通过 |

## 真实写稿 + 独立盲审（对固定 1.5.37）

口径（用户 2026-08-07 定义）：不劣于已发布基线即可发布；“不劣于”= 不存在由本轮 diff 改动造成的质量回退，写作本身波动不算。

三题覆盖本轮 diff 直接交互边界与旧能力回归：T1 稀疏材料轻量卡情况说明（200 字内、禁补固定章节）；T2 关键名词保留改稿（五个指定名词原词保留 + 第三部分后加自然段、不加小标题）；T3 请示起草回归（缺主送/单位/金额/日期不得编造）。writer 为独立子代理，分别加载固定 1.5.37 基线与 1.5.38 候选；独立 verifier 只看“原 prompt + 匿名稿”，不知版本映射。

| 任务 | 基线 1.5.37 | 候选 1.5.38 | 盲审结论 |
| --- | --- | --- | --- |
| T1 轻量卡 | WARN（缺标题） | PASS | 候选略优；两臂均只读轻量卡与信息选择规则，未加载长 reference |
| T2 关键名词 | PASS（首轮有“特此通知”） | WARN（首轮缺结尾语） | 五个关键名词两臂两轮均 2/2 原词保留；结尾语有无在两轮间双向抖动，判波动 |
| T3 请示回归 | PASS | WARN（首轮补写“设备老化、性能下降”等未给背景） | 同题两次定向复现候选均未再编造（0/2 复现），基线 3/3 干净；该任务不命中本轮任一改动子句，判写作波动 |

结论：未见由本轮 diff 造成的质量回退，满足“不劣于”发布口径。writer/verifier 均由 opencode 子代理执行（模型 qwen3.8-max），本轮未使用其他模型档位。

## 发行包

### ClawHub

- 发行目录：`openclaw/skills/chinese_official_writing/`；
- 文件数：32；
- dry-run：`status=would-publish`，公开基线 1.5.37，目标版本 1.5.38；
- fingerprint：`7873fb4683b8aa6edcdda719540d7568cc23f0d8ce24af68b43017fc80b985c5`。

### skillhub.cn

- 清洁包：`output/skillhub-release-1.5.38-20260807/publish-package/`；
- 文件数：31，禁入文件 0，共享内容哈希不一致 0；
- 自 1.5.37 清洁包复制后，除 `_meta.json` 与 `SKILL.md` 外逐文件用 canonical 覆盖；`SKILL.md` 保留 SkillHub 专用 frontmatter，正文与 canonical 逐字一致（本轮入口有两处原子改动，不能只替换版本号）；
- 排除 `agents/openai.yaml`、`delivery-review-gate.md`、`gate_stop_hook.py`、`review_gate.py`，加入平台 `_meta.json` 和 SkillHub 专用 frontmatter；
- 排序清单 SHA-256：`b8e72432919ed43db0d222e09d4b651344695883e06eda46c632a46f3ddb13cb`；
- dry-run：精确返回 `chinese-official-writing@1.5.38`。

## 剩余风险

1. 真实写稿 A/B 为三题、writer/verifier 为同一模型档位的子代理，能够核验本轮两处入口改动的直接交互，不能据此宣称所有文种的统计性提升。
2. T3 首轮候选稿出现一次未给背景补写，两次复现未再现；事实边界规则本轮未改动，仍按写作波动记录，后续版本继续观察请示类起草的事实克制。
3. skillhub.cn 的 review、security scan 和 content audit 仍为 pending，公开正文详情仍显示 1.5.37，属于异步传播；公开 keen/sanbu benign 对应已传播的 1.5.37，不写成 1.5.38 审核结论。

## 实际发布与回执

- GitHub：`origin/main` 已包含产品提交；annotated tag `v1.5.38` 的 tag object 为 `1903357615346ec129a08ad7692c1c434a5d0547`，解引用提交为 `c3fa2128ef9426b4ebb135986a7e19feccf08421`。正式 Release 已公开（`isDraft=false`、`isPrerelease=false`、`publishedAt=2026-08-07T05:29:39Z`）：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.38`。
- ClawHub：正式提交只执行一次，回执为 `status=published`、`versionId=k97czm04ca0vfxxq7pk0qmnn0s8c0qk6`、32 个文件、fingerprint `7873fb4683b8aa6edcdda719540d7568cc23f0d8ce24af68b43017fc80b985c5`。首次只读检查已显示公开 `latestVersion=1.5.38`、`tags.latest=1.5.38`，精确查询 1.5.38 返回版本级 security `clean`（llm benign、confidence high）；moderation `clean` 对应当前已传播的 1.5.38。
- skillhub.cn：正式提交只执行一次，回执为 `ok=true`、`skillId=70149`、`versionId=204235`、31 个文件、fingerprint `d1416a66018bd122eede9b684c688a9b27411db84ccea848b4cf904beb18495d`、`tags.latest=1.5.38`；提交回执中的 review、security scan 和 content audit 均为 `pending`。首次公开查询已显示 `tags.latest=1.5.38`，正文详情仍为 `latestVersion=1.5.37`；公开 keen/sanbu benign 报告对应已传播的 1.5.37，不写成 1.5.38 审核结论。
- 小红书 Red SkillHub 未调用。
