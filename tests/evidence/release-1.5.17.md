# 1.5.17 发布证据

## 发布范围

1.5.17 以 `v1.5.16=172d1140905e38ce16ab6a16e89d9cb50248285e` 为固定底座，只增加一条跨宿主生效的事实关系锚：事实之间的时间、因果和归属关系以材料明确关系为准。产品提交为 `582c861`。

本版不包含 Candidate AI 脚本门禁。独立审计确认该门禁在 Hermes/Qwen 测试中可能完全跳过，因此不进入 1.5.17。reference 拆分、段内公式调整和其他失败候选同样排除。

## 正向差异与边界

- 日常完整报告中，Candidate 的机械复述略少，匿名盲审选择 Candidate。
- 决定状态确认题中，Candidate 保持一般会议意见与议定责任分离，固定 1.5.16 发生状态升级，匿名盲审选择 Candidate。
- 一项二次改稿中两版逐字一致，明确因果、主体、数字、状态和时序均保留。
- 两项定向关系题中两版均通过并难分，未因新规则丢失材料已明确的合法因果或归属。
- 一项会议纪要中 Candidate 出现一次决定状态升级，固定基线更优；同类确认题未复现。按仓库约定，普通场景同机制需在三个正常场景复现后才升级为共性发布阻断，本次作为已知单例风险保留。

因此，本版只声明存在可复核的局部正向收益和跨宿主事实关系边界，不宣称全面优于 1.5.16，也不宣称达到对无 Skill 80% 的完整统计门槛。

原始证据见：

- `tests/evidence/candidate-ac-explicit-relation-boundary-result-20260718.md`
- `tests/evidence/candidate-ac-second-stage-result-20260718.md`
- `tests/evidence/candidate-ac-release-writing-result-20260718.md`

## 发布前验证

版本同步后已完成：全量 unittest 177/177；固定 1.5.16/current 确定性消融 108/108 对 108/108；Promptfoo smoke 20/20，Skill 胜 10/10，judge consistency 1.0；真实样文关键要素 61/61；canonical quick validate、镜像同步和 `git diff --check` 均通过。

## 三平台状态

- GitHub：待发布。
- ClawHub：待发布。
- skillhub.cn（skillId 70149）：待发布。
- 小红书 Red SkillHub：按仓库纪律排除。
