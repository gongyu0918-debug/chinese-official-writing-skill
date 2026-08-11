# 关键名词例子下沉候选结果

## 结论

PASS / MERGE-READY。入口保留“关键名词和结构标签一般保留原词”的抽象契约，五个具体例子继续由按需 reference 承载。未观察到标签保留、局部改稿、事实或输出范围回退。

## 固定对象

- 基线：v1.5.37 产品提交 5d166a8d671fcb0bd96e66aec8e944ccbdf3c0d4。
- 预注册：0b8ad960。
- 产品提交：a7ad6f54。
- 测试契约提交：4ec0bb6d。

## 工程验证

- python -m unittest discover -s tests：442/442 通过。
- 固定 1.5.37 确定性消融：Candidate 111/111，Baseline 111/111。
- quick_validate.py chinese-official-writing：通过。
- canonical 与五个发行镜像核对：通过；宿主既有适配差异未扩大。
- git diff --check：通过。
- Candidate 单独的 Promptfoo smoke 因外部发送审批门未获准，记为未运行；合并候选仍需在主线组合回归中补一次 smoke。

最初全量 unittest 的唯一失败是旧断言逐字要求入口出现示例“原因分析”。测试改为入口核验抽象契约、reference 继续核验具体示例；产品规则未为通过测试而追加。

## 真实 A/B

两名隔离 writer 按 gpt-5.6-terra / high 派发，逐字使用同一自然任务，各取首个输出，不补抽、不二次修订。两臂均只读取：

1. SKILL.md
2. information-selection.md
3. task-route-cards.md

任务要求只改第二段，并逐字保留“受理渠道”“牵头科室”“复核节点”三个新标签、字段顺序、字段值、两段结构和全部数字事实。

独立匿名盲审结果：

- Baseline：PASS。
- Candidate：PASS。
- 排序：Candidate 小胜；两稿均可直接使用。

因果判定只采用硬项：Candidate 三个新标签逐字保留，只改指定段落，无事实、数字、状态或正文外残留。普通句式差异不作为本候选收益。

## 剩余风险

本轮只证明具体例子可从入口下沉，未证明可以删除“关键名词和结构标签保留原词”的抽象契约；该句继续保留。
