# MT-005c 合并前全量门与“学校”最小回补结果

## 结论

`REJECTED_NOT_INTEGRATED`。

193字受众合并候选未通过合并前全量门；196字最小回补虽恢复“学校”并保持正负触发方向，但两份正向真实通知出现材料外安排或状态升级。最终产品恢复 v1.6.13 已发布的204字 description，MT-005c 不进入本地 `main`。

## 全量门暴露的问题

在 `codex/v1614-next-atomic` 上第一次运行：

```text
python -B -m unittest discover -s maintenance/tests -q
```

实际结果为660项、1项失败：`P058` 的 prompt 是“帮我写一份学校奖学金申请……”，193字候选 description 已删除显式“学校”，因此 `description missing 学校`。此前学校系统通知的真实样本能够触发，不能抵消已登记低频正向关键词的确定性回退。

## 196字单一修正

只把开头改为“用于机关企事业、学校等组织……”，其他枚举和正文规则不动。同步 canonical 与四套镜像后：

```text
python -B -m unittest maintenance.tests.test_description_news_trigger maintenance.tests.test_real_prompt_ablation maintenance.tests.test_skill_boundary -q
```

结果88/88通过；Skill Creator quick validate 通过。

## Codex CLI 真实写稿

- `codex-cli 0.144.6`
- `gpt-5.6-terra` / medium
- 隔离仓库 `.agents/skills/chinese-official-writing`，禁用两条用户级同名公文 Skill；read-only、ephemeral、无 Hook。
- 第一次曾把任意路径写进 `skills.config`，模型没有读取指定 Skill，记 `TECHNICAL_INVALID`，不计质量；随后改用官方仓库级发现目录。

| 题目 | 公文 Skill | 触发结论 | 稿件结论 |
| --- | --- | --- | --- |
| 学校系统通知 | 精确读取 | 正向触发 | `FAIL`：新增“请各学院结合实际做好试用安排”；把并行时间“尚待评估”扩成“待评估后另行通知” |
| 行业协会通知 | 精确读取 | 正向触发 | `FAIL`：把“每家会员单位可报1名代表”升级为“请各会员单位安排1名代表参会”；新增“后续如有安排另行通知” |
| 小红书社团招新 | 未读取公文 Skill；读取小红书写作 Skill | 负向不误触发 | 只作路由观察，不归因给公文 Skill |

两份正向稿均保留主要数字和日期，但触犯预先登记的状态与材料外安排边界，不能因触发成功而放行。

## 有效正向原稿

### 学校系统通知

```text
关于启用新实验室预约系统的通知

各学院：

新实验室预约系统将于2026年9月1日起正式启用。为做好系统切换工作，现将有关事项通知如下：

一、新系统于8月27日至28日开放试用，请各学院结合实际做好试用安排。

二、请各学院于8月26日17时前报送1名系统管理员的姓名和联系电话。

三、旧实验室预约系统保留使用至9月5日。新旧系统并行运行时间是否延长，待评估后另行通知。
```

### 行业协会通知

```text
关于举办算力资源使用交流会的通知

各会员单位：

定于2026年8月28日14时在市创新中心三楼会议室举办算力资源使用交流会。请各会员单位安排1名代表参会，并于8月26日17时前将参会代表姓名、单位和联系电话发送至service@example.org。

线上直播安排尚未确定，后续如有安排另行通知。
```

## 决定

1. 恢复204字 description 及四套镜像，不修改 P058 验收来迁就候选。
2. 保留初轮 CLI 结果作为为什么继续做全量门的证据，不把阶段性 `PASS_CANDIDATE_ELIGIBLE` 冒充最终接入状态。
3. 不再换一个近义受众短语重复抽样；只有新的真实加载成本、漏触发或误触发证据出现时，才设计新的 description 原子。
