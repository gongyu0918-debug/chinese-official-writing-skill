# 1.5.32 发布证据

## 范围

1.5.32 以 `v1.5.31=e8c077cb1d6c6fe02bec71634140793aeeba5a5b` 为固定
发布基线，发布以下已经在独立 worktree 验证并合入本地 `main` 的原子：

- 新闻消息和新闻评论进入专项叶，普通公文不会因正文偶然出现相关词语而改走新闻路由；
- 新闻评论推演逐句核对事实依据和适用范围，只修改判断强度超过材料支持的句子；
- 工作总结、工作要点和周报规则原文迁入专项叶，直接命中该叶；
- 归并入口原则、核心路由和稀疏工作流中的重复说明；
- 删除字数上限后的固定 5%-10% 余量要求，保留上限自检与硬要素完整性。

本版没有合入试验性的篇幅扩写公式、后置补写门禁或新增循环修改链。事实边界、
用户模板、文种功能、输出模式、Hook、FSM 和回退方式保持现有口径。

## 发布前验证

- `python -m unittest discover -s tests`：407/407，`OK`。首次运行只有一条
  README 历史计数断言仍要求 `395/395`；将断言同步到当前真实计数后完整通过，
  不涉及写作规则修改。
- `npm run eval:official-writing:smoke`：20/20，0 failure，0 error，judge
  consistency 1.0，eval id `eval-i0Q-2026-08-01T06:51:21`。
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.31> --baseline-label
  v1.5.31 --current-root . --out output/release-1.5.32-ablation`：固定 1.5.31 为
  109/110，Candidate 为 110/110；基线唯一失败是没有本版新增的工作总结专项叶，
  不属于旧能力回退。
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：
  `Skill is valid!`。
- `python tools/sync_adapters.py`：canonical 与五个 Agent 镜像完成同步；
  `git diff --check` 通过。

## 真实写稿与减载证据

- 新闻评论复核原子三组匿名 A/B 为 Candidate 3 胜 0 负，目标风险由 8 处降至
  4 处，两组均未发现 P0、事实或状态硬回退。见
  `tests/evidence/news-commentary-r3-main-integration-result-20260801.md`。
- 删除固定篇幅余量后三组严格同模型 A/B 为 Candidate 3 胜 0 负；Candidate
  去空白字符数为 322、804、1038，固定基线为 340、531、1059，三题均未发现
  P0、事实、状态、文种或格式回退。见
  `tests/evidence/candidate-length-headroom-delete-only-current-main-v1531-real-ab-result-20260801.md`。
- 工作总结规则文本保持逐字一致，命中上下文由 14192 字符降至 11005 字符，
  减少 3187 字符、约 22.46%。见
  `tests/evidence/work-summary-current-main-integration-result-20260801.md`。
- 三原子组合 sanity 中两稿硬边界均通过；固定基线因相邻事实复述较少获得一次
  语言小胜。该差异只出现于一个样本，未形成三场景共性机制，不做一例一修。
  见 `tests/evidence/final-three-atom-integration-v1531-result-20260801.md`。

## 发行包与平台状态

- GitHub：产品提交为 `dbaa5b19ed403cbcf1e133ad6c8b91d9900425b9`；annotated
  tag object 为 `8e1a3cf4e3406b0c993da7ce9ff433647811aac5`，tag 解引用提交与
  产品提交一致。正式 Release 已公开：
  `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.32`，
  `draft=false`、`prerelease=false`。
- ClawHub：30 文件发行镜像无额外文件；正式提交一次，返回
  `status=published`、`versionId=k9760bqzrrbnsqz0wccq5ws0s58bngds`、
  fingerprint
  `17019404b1a9cee9623960310f1b74e1de98088631f2035feab6f31865ce6160`。
  首次公开查询的 `latestVersion.version` 和 `tags.latest` 仍为 1.5.31，精确
  查询 1.5.32 返回传播中的 `Version not found`；公开旧版 moderation 为
  clean，不据此推断 1.5.32 的扫描状态，也不重复提交。
- skillhub.cn：29 文件清洁包排除 `agents/openai.yaml`、Codex 门禁说明和两项
  门禁脚本，并加入平台 `_meta.json`；其余 28 个内容文件逐文件哈希与 canonical
  一致，`SKILL.md` 正文一致。正式提交一次，返回 `skillId=70149`、
  `versionId=187025`、fingerprint
  `150378819d3e19a9ce86d4d1f273781c4225f4b599f3e340fe83143e31ee0768`，
  `tags.latest=1.5.32`；review、security scan 和 content audit 均为 pending。
  首次公开详情的 `latestVersion.version` 仍为 1.5.31，而 `tags.latest` 已为
  1.5.32，按异步传播处理，不重复提交。
- 小红书 Red SkillHub 不在本次发布范围。

平台提交、公开 latest、审核、扫描和 provenance 分别核验；公开索引传播延迟不
触发重复提交。

## 剩余风险

- 本轮没有重复生成 true No-Skill 或跨模型矩阵，真实结论限定在既有严格 A/B
  与发布级组合 sanity。
- `workflow.md` 内另一处固定余量/压缩表述仍是篇幅偏短的弱嫌疑项，未与入口
  原子同时修改；后续若继续，只能单变量验证。
- 新闻消息和新闻评论是新增专项能力，现有样本可以证明可用与无已见硬回退，
  不能替代全题材、全长度覆盖。
