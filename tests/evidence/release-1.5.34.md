# 1.5.34 发布证据

## 范围

1.5.34 以 `v1.5.33=1ea3f5b6ccccd5ef772803e264087adcf2fb5515` 为固定发布
基线，只纳入已经在独立 worktree 或隔离上下文中验证、并合入干净 `main` 的原子：

- Promptfoo 和真实成稿评估入口显式使用 `delivery_mode="draft-body"`，使终稿检测
  规则进入实际调用链；
- `prose_lint.py` 以 `medium` 线索定位高置信保护性否定收束，以 `low` 线索定位
  连续解释性句尾和成簇场景套话；
- `final-review-layers.md` 对保护性命中只做一次保留、进行态改写或删除的语义选择，
  复扫一次后停止；
- 入口“只输出正文／只输出改后稿”规则完成等义压缩，保留输出范围优先、允许一种
  提示不扩类和缺项不进正文三项语义。

本版不自动删除或改写正文，不增加自由扩写公式、自动修订循环、强制 Hook、默认
联网或新的发布链。欠写章节平衡候选真实 A/B 为基线 3 胜，已留在隔离研究分支，
没有进入本次发行。

## 真实写稿与定向证据

- 保护性否定收束完整稿 A/B 使用两份既有 P0 完整稿和一份 clean 通告；Candidate
  2 胜、1 平。两臂均无事实、数字、主体、责任、状态、文种、格式或输出范围硬
  回退，clean 通告与初稿字节一致。
- 保护性提示定向正例 11/11、明确豁免 8/8、clean corpus 12/12 通过；三类命中
  分别完成删除、进行态改写和保留的短链路复放，脚本扫描前后原稿字节一致。
- 场景化套话规则正例 5/5，8 条合法反例、12 条 clean fixture 和 7 篇历史稿合计
  0/27 误报；规则为 `low`，命中后允许依据材料保留。
- 连续解释性句尾在两份历史同机制稿中各命中一次；12 条 clean fixture 与 7 篇
  归档完整稿合计 0/19 误报。该规则只在 `--structure` 下提示，不自动清洗。
- 输出范围入口压缩两题真实行为核验通过：只输出正文时没有正文外说明；只允许
  联系人待确认时没有扩展到其他提示。
- 两题补充 true No-Skill 对照中，Skill 均胜出；该结果用于现实质量判断，因两侧
  宿主表面不同，不包装成总体胜率或完全同宿主因果实验。

## 发布前验证

- `python -m unittest discover -s tests`：440/440，`OK`；
- `npm run eval:official-writing:smoke`：20/20，0 failed，0 errors，judge
  consistency 1.0，eval id `eval-fkT-2026-08-03T05:34:03`；
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.33> --baseline-label
  v1.5.33 --current-root . --out output/release-1.5.34-ablation`：固定 1.5.33 为
  110/111，Candidate 为 111/111；基线唯一失败是没有本版新增的 P098 终稿检测
  调用证据；
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：
  `Skill is valid!`；
- 167 项版本面、镜像和本版功能专项回归通过；
- `python tools/sync_adapters.py`：canonical 与五个 Agent 镜像完成同步；
- `git diff --check`：通过。

ClawHub dry-run 为 32 个文件，目标版本 1.5.34，公开基线 1.5.33，fingerprint
`4f4c6347ca9f576d078863a1ca8886170aaec1cf5a708a6a07e88b924ebf0239`；包内没有
`review_gate.py`、`gate_stop_hook.py`、`delivery-review-gate.md`、缓存或 `.pyc`。

skillhub.cn dry-run 精确返回 `chinese-official-writing@1.5.34`。清洁包为 31 个
文件，排除 `agents/openai.yaml` 和三项 Codex 门禁文件；29 个共享内容文件逐文件
SHA-256 与 canonical 一致，平台专用 `SKILL.md` 正文与 canonical 一致。

## 发行包与平台状态

GitHub、ClawHub 和 skillhub.cn 的正式提交回执、公开 latest、审核与扫描状态在
发布后分别补入。小红书 Red SkillHub 不在本次发布范围。

## 剩余风险

- 保护性提示只定位完整高置信结构；一句话是否由材料明确支持，仍由 Agent 对照
  原材料和文种功能判断。为控制误报，本版没有扩成“尚未、不能、不”等宽词表。
- 完整稿 A/B 证明“脚本执行后”的局部复核有效，没有证明所有无 Hook 宿主都会
  自然调用脚本；未调用脚本时仍依赖成稿后语义复核。
- 场景套话和解释性句尾均为低等级线索；材料确有独立事实作用时应保留，不作为
  自动删除依据。
- 本版没有解决一般性的篇幅不足。欠写章节候选因三题均不优于 1.5.33 而未合并；
  该问题继续作为独立研究方向，不影响本次已验证小版本发布。
