# 1.5.33 发布证据

## 范围

1.5.33 以 `v1.5.32=dbaa5b19ed403cbcf1e133ad6c8b91d9900425b9` 为固定发布
基线，发布以下已独立验证并完成组合回归的改动：

- 方案、实施方案和建设方案从聚合 playbook 迁入专用起草叶；
- 入口七项重复或低频细则下沉，审稿模式进一步收束为专项 reference 指针；
- 可研只审不改进入专用检查叶，复核项目主张本身及相互之间的一致性；
- `prose_lint.py --mode draft-body` 识别带中文、阿拉伯数字、括号及章节目次前缀的文后提示标题。

本版不增加自由扩写公式、自动改稿循环、新的强制 Hook 或默认联网行为；事实
边界、用户模板、文种功能、输出模式、修改次数和回退方式保持现有口径。

## 已有真实写稿与单变量证据

- 方案专叶目标题中，Candidate 非空白字符为 998，固定基线为 781；匿名盲审判
  Candidate 明显胜出。目标路径由 13909 字符降至 11358 字符，减少 2551 字符、
  约 18.34%。控制题用于确认非目标能力无回退，不计入严格因果收益。
- 入口七项组合由 10678 个规范化字符降至 10145 个，净减 533 个、约 4.99%；
  两题匿名 A/B 为 Candidate 1 胜、1 难分。审稿模式继续净减 121 个字符，两题
  均难分，四稿硬边界通过。
- 可研只审不改三题为 Candidate 1 胜、2 难分；六份输出均保持只审不改，没有
  恢复完整估算、技术条件、资金安排、评估主体或验收体系等外围清单。
- 文后提示 OS01—OS04 四模式符合输出范围；当前主线未复现“文后提示误入正文”。
  脚本定向测试覆盖四种编号标题及三类正文反例。
- 三项末轮组合回归未发现事实、文种、输出模式、只审不改、文后提示或镜像一致性
  回退。

既有部分写稿记录无法核验精确模型和 thinking，因此只作单变量行为证据，不包装
成严格同条件总体质量胜率。

## 发布前验证

- `python -m unittest discover -s tests`：417/417，`OK`；
- `npm run eval:official-writing:smoke`：20/20，0 failed，0 errors，judge
  consistency 1.0，eval id `eval-hbQ-2026-08-02T05:49:04`；
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.32> --baseline-label
  v1.5.32 --current-root . --out output/release-1.5.33-ablation`：固定 1.5.32 为
  110/111，Candidate 为 111/111；基线唯一失败是没有本版新增的方案专叶；
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：
  `Skill is valid!`；
- `python tools/sync_adapters.py`：canonical 与五个 Agent 镜像完成同步；
- `git diff --check`：通过。

ClawHub dry-run 为 32 个文件，fingerprint
`cf8dcab0e9d3b2d0939ffa502f3f4e69af3f9fbb293904d6c6091618ae3b3a35`；
skillhub.cn dry-run 精确返回 `chinese-official-writing@1.5.33`。skillhub.cn 清洁包
为 31 个文件，排除 `agents/openai.yaml`、Codex 门禁说明和两项门禁脚本；其余
29 个内容文件逐文件哈希与 canonical 一致，`SKILL.md` 正文一致。ClawHub 包不含
门禁脚本、缓存或 `.pyc`。

## 发行包与平台状态

GitHub、ClawHub 和 skillhub.cn 的正式提交回执、公开 latest、审核与扫描状态在
发布后分别补入。小红书 Red SkillHub 不在本次发布范围。

## 剩余风险

- 文后提示是否应出现仍由 Agent 按输出模式和材料语义判断；lint 是可选定位器，
  不是所有宿主的强制交付出口，也不会自动删除或改写正文。
- 用户确实把“待确认事项”等名称用作正文业务章节时，脚本可能要求人工复核；
  已用“待确认事项办理情况”等反例压低误报，但语义边界不交给正则一刀切。
- 本版没有新增 true No-Skill 或跨模型矩阵；发布判断限定在既有真实 A/B、组合
  sanity、固定版本消融和工程回归。
