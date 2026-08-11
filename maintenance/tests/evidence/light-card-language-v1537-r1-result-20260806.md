# 轻量卡路由术语自然化候选结果

## 结论

PASS / MERGE-READY。将“在轻量卡早停”改为“由卡片完成，不再读取长 reference”，没有改变触发条件、转读条件或成稿后复核。

## 固定对象

- 基线：v1.5.37 产品提交 5d166a8d671fcb0bd96e66aec8e944ccbdf3c0d4。
- 预注册：24aac284。
- 产品提交：3dbfe3ab。
- 测试契约提交：33a0c367。

## 工程验证

- python -m unittest discover -s tests：442/442 通过。
- npm run eval:official-writing:smoke：20/20 通过。
- 固定 1.5.37 确定性消融：Candidate 111/111，Baseline 111/111。
- quick_validate.py chinese-official-writing：通过。
- canonical 与五个发行镜像核对：通过；Hermes/OpenClaw 既有宿主适配差异未扩大。
- git diff --check：通过。

最初两项 unittest 逐字要求旧术语“在轻量卡早停”。测试改为同时核验“卡片能够覆盖任务”和“由卡片完成，不再读取长 reference”；产品路由未改变。

## 真实 A/B

两名隔离 writer 按 gpt-5.6-terra / high 派发，逐字使用同一份 180—220 字简短情况说明任务，各取首个输出，不补抽、不二次修订。

两臂实际读取集合完全一致：

1. SKILL.md
2. information-selection.md
3. task-route-cards.md

Candidate 没有读取 workflow.md、长文种 playbook 或整套复核资料，说明新措辞仍保持轻量路由。

独立匿名盲审：

- Candidate：PASS，约 203 字。
- Baseline：其余硬项通过，约 223 字，超过题面上限。

篇幅和句式差异属于单次采样，不作为术语修改带来的质量收益。可归因结论仅为：Candidate 没有扩大 reference 集合，且未出现事实、状态、文种、输出范围或正文质量回退。

## 剩余风险

本轮因额度收紧未新增长任务 writer 对照；应转读长 reference 的控制由未改变的触发文本、既有回归与 111/111 确定性消融守住。后续若修改触发集合，必须重新做短稿/长稿双向真实轨迹。
