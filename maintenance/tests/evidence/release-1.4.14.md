# 1.4.14 发布证据

## 修改摘要

- 将 `description` 调整为更明确的触发边界：覆盖中文公文、机关企事业单位和学校等正式事务材料，保留“写申请/请示/报告/通知/函”等短 prompt 的可触发性。
- 将 `降 AI 味` 收束为“对这类材料”适用，明确排除英文、文学、营销、社媒、论文、个人求职、批量语料和法律/财务/采购/审计替代判断，降低误触发风险。
- OpenClaw 市场页说明改为“市场页只展示摘要；安装包内入口规则和 references 为准”，避免把 canonical 硬边界路径写成包内不可达依赖。
- `run_real_prompt_ablation.py` 新增 P056-P064 description 专项用例，覆盖短 prompt 正触发、学校正式事务材料、工作要点/征求意见函遗漏防护，以及论文/营销/个人求职排除边界。

## 消融测试

命令：

```powershell
python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.4.13-publish-1.4.14 --baseline-label baseline-1.4.13 --current-root . --out output\real-prompt-vs-1.4.13-release-1.4.14-description
```

结果：

- `baseline-1.4.13`: 64 例，61 通过，3 失败。
- `current`: 64 例，64 通过，0 失败。
- 1.4.13 仅在新增 description 专项上失败：
  - P058: `description missing 学校`
  - P061: `description exclusion missing 论文`
  - P063: `description exclusion missing 个人求职`

前置发现：

- 初版 description 与 1.4.13 基线跑 P001-P055 时，current 曾失败 2 项：`征求意见函`、`工作要点` 未写入 description。
- 本轮已补入 description，并用 P059/P060 固化为回归用例。

## 真实写稿测试

writer subagent 覆盖 4 个真实用户式 prompt：

- W1：200 字以内硬盘采购申请，2T 固态硬盘，数量 1，金额 2000 元，申请人龚昱，日期 2026 年 6 月 22 日。
- W2：办公电脑采购请示，3 台，预算 15000 元，用于财务、行政、资料归档岗位。
- W3：征求意见函，附件为《数据共享管理办法（征求意见稿）》，2026 年 7 月 10 日前反馈至 `data@example.com`，联系人张工。
- W4：350 字以内年度信息化工作要点，包含重点任务、责任机制、时间节点、评价方式，避免头重脚轻。

独立 verifier 结论：

- W1: PASS。关键要素完整，200 字以内，未中断、未编造。
- W2: WARN。请示文种和事项正确，缺主送机关、落款和日期；prompt 未提供这些信息，不构成事实编造或发布阻断。
- W3: WARN。征求意见函方向正确，截止日期、邮箱、联系人和附件均覆盖；缺发函单位和成文日期，属于正式完整性不足，不构成文种错乱。
- W4: PASS。350 字以内，四类要求均覆盖，未头重脚轻。

总体：未发现影响发布的功能性回退风险。

## 发布前验证

已运行：

```powershell
python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary -v
```

结果：39 项通过。

```powershell
python -m unittest discover -s tests -v
```

结果：95 项通过。

```powershell
npm run eval:official-writing:smoke
```

结果：授权联网后通过，20/20 passed，`skill_win_rate=1.0`，`judge_consistency_rate=1.0`。

说明：首次在受限沙箱下运行 smoke 时，npm 访问 registry 报 `connect EACCES`，未作为产品测试失败；授权联网重跑后通过。

```powershell
python .\tools\run_real_article_eval.py --out output\real-article-release-1.4.14
```

结果：生成 `output\real-article-release-1.4.14\summary.md`；skill 模式 10 组关键要素 61/61 覆盖，平均差异率 0.00%。

```powershell
python .\tools\sync_adapters.py
```

结果：同步 canonical、OpenClaw、Qwen、Hermes、generic agent skills、Claude plugin manifest。`.agents` 镜像写入需授权后完成。

```powershell
python C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
```

结果：`Skill is valid!`

```powershell
git diff --check
```

结果：退出码 0；仅有 Windows 换行提示。

## 剩余风险

- description 无法真实替代 Codex 运行时的触发统计。本轮未找到可靠结构化 skill 使用计数，只用 description 专项消融和真实写稿验证控制误触发/漏触发风险。
- W2/W3 的正式要素偏简来自用户未提供主送、发函单位、成文日期；不构成本轮 description 改动引入的回归。
