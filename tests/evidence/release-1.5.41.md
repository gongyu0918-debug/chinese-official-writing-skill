# 1.5.41 发布证据

## 当前状态

1.5.41 已完成 GitHub、ClawHub 和 skillhub.cn 各一次正式提交。GitHub `main`、annotated tag `v1.5.41` 和正式 Release 的产品提交均为 `b2bc25da6b31fb6d6057affc02e3e7b72d18d26c`；回执文档提交继续推进 `main`，不移动发布 tag。ClawHub 和 skillhub.cn 的公开正文索引仍显示 1.5.40，属于提交后的异步传播，不重复发布。小红书 Red SkillHub 不在本次授权范围内。

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
- 版本准备与首轮发行证据提交：`c01cfb2db7dc4bb863aa9bdbd3d626442afb2aad`。
- 1.5.41 产品与 tag 解引用提交：`b2bc25da6b31fb6d6057affc02e3e7b72d18d26c`。
- annotated tag `v1.5.41` 的 tag object：`13c611879f14ac739a7bff75d6b818c7e19f6fd8`。

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

- 发行目录：`openclaw/skills/chinese_official_writing/`；
- 文件数：32，禁入门禁文件、缓存和 `.pyc` 为 0；
- dry-run：`ok=true`、`status=would-publish`，公开基线 1.5.40，目标版本 1.5.41；
- 使用最终发布提交精确 `source-commit` 重跑 dry-run，fingerprint 仍为 `6d5851e7c589de5978303929e313b83fac843e18f4b03976c5f368795f33ed99`；
- 正式提交回执：`ok=true`、`status=published`、`versionId=k976j6z7tccr9zz2jb4tnz2phx8c77cz`、32 个文件，fingerprint 与 dry-run 一致。

### skillhub.cn

- 清洁包：`output/skillhub-release-1.5.41-20260810/publish-package/`；
- 文件数：31，缺失 0、额外 0、共享内容哈希不一致 0、禁入文件 0；
- 排除 `agents/openai.yaml`、`references/delivery-review-gate.md`、`scripts/gate_stop_hook.py`、`scripts/review_gate.py`，加入平台 `_meta.json` 和 SkillHub 专用 frontmatter；
- `SKILL.md` 可执行正文与 canonical 逐字一致；
- 内容清单 SHA-256：`6b24ba3e0f558fb06c6a5f6edf8dad2258d549dd9001fc3003141ef19bdff502`。算法为：相对路径按序排列，每行 `relative_path<TAB>file_sha256`，UTF-8、LF、末尾保留 LF 后取 SHA-256；
- dry-run：`dryRun=true`，精确返回 `chinese-official-writing@1.5.41`；
- 正式提交回执：`ok=true`、`skillId=70149`、`versionId=226574`、31 个文件、fingerprint `98dd5dc98d95f10ccf1e20b437fd4b4d586ca2aa8028255edf24dd21f3e24687`、`tags.latest=1.5.41`；review、security scan 和 content audit 均为 `pending`。

首次计算内容清单时，PowerShell 正则转义错误使 31 行均未加入清单，并得到空文本 SHA；该值已作废，未进入平台 dry-run 或发布证据。随后改用字面路径替换，启用错误即停并确认 31 行后重算，得到上列有效 SHA-256。

## 实际发布与首次传播核验

- GitHub：远端 `main` 为 `b2bc25da6b31fb6d6057affc02e3e7b72d18d26c`；远端 tag object 为 `13c611879f14ac739a7bff75d6b818c7e19f6fd8`，解引用提交为 `b2bc25da6b31fb6d6057affc02e3e7b72d18d26c`。正式 Release 为非草稿、非 prerelease，`publishedAt=2026-08-10T00:59:31Z`，地址为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.41`。
- ClawHub：正式回执已接受 1.5.41；首次只读查询仍显示 `latestVersion=1.5.40`、`tags.latest=1.5.40`，精确 1.5.41 查询返回传播中的 `Version not found`。当前显示的 moderation `clean` 属于已传播的 1.5.40，不能写成 1.5.41 已完成扫描。
- skillhub.cn：正式回执的 `tags.latest` 已为 1.5.41；首次公开详情的 `latestVersion` 仍显示 1.5.40。提交回执中的 review、security scan 和 content audit 均为 `pending`；公开安全报告仍对应此前已传播内容，不能推断 1.5.41 已完成扫描。
- 小红书 Red SkillHub 未调用。

## 下一轮剩余项

1. 继续隔离验证 `59ea0def` 的精确结构召回及跨宿主真实执行；没有真实执行证据前不合入。
2. 继续验证无缺口场景的直接正文交付、给定材料格式遵循、文后提示数量和短通知链路时延。
3. 固定二段式表达、纪要单次状态落位和分阶段加载继续保持原子隔离，不与本版连续否定规则捆绑。

平台正式回执取得后，即使公开索引、审核或扫描异步滞后，也不重复提交。
