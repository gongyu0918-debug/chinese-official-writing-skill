# 入口质量风险枚举去重：失败记录（2026-07-22）

## 变量

固定基线为提交 `39cd442`。候选只从 `SKILL.md` 的“其他口语化……”路由句中删除此前已经出现过的六个例项：标题漂移、重复事项、格式噪点、项目卡片式摘要、测算说明腔、必要性罗列；保留路由目标、专项 reference 和其余风险类型。各发行镜像同步同一变更，不修改 reference、路由条件、复核顺序或输出模式。

该原子变更可减少入口 35 个字符，约占变更前入口的 0.34%。

## 工程检查

- 边界单测：52/52 通过。
- 固定基线确定性消融：Candidate 108/108，Baseline 108/108。
- `git diff --check`：通过。

上述结果只说明静态结构和既有确定性用例没有退化，不作为写作质量通过依据。

## 真实 A/B

两题均使用逐字一致的自然语言原始任务，同题 Candidate 与固定基线各取首个技术有效输出；写稿上下文物理隔离。匿名盲审只读取原始任务和随机标记稿件。

### T01：工作总结段落精简

- Candidate SHA-256：`1F8D33FBBA6E9B5FDB97999AD13A6D2616AC7DDD82373234B657E8CBAAA54E12`
- Baseline SHA-256：`6662577D57AD2A1CDF3E35B88DB8219CCEFA6703711A81637F81CE623508C4CE`
- 盲审：难分。两稿事实、数字和输出范围均有效，只存在标点与语流差异。

### T02：排队叫号设备巡检情况报告

- Candidate SHA-256：`B82EBCA3119AA445A23876B5BA82ED02538FA435D3787C1B51ACD0C54459450C`
- Baseline SHA-256：`40135CAD44FAF75AB264FCC5D3CC165ABE4737B80389C0B2CE7206BB6B50972C`
- 匿名映射：稿件 A 为 Candidate，稿件 B 为 Baseline。
- 盲审：稿件 B 胜。Candidate 将材料中的问题设备复测结论扩大表述为全部 46 台（块、个）设备运行正常，并有更多重复统计；Baseline 对复测对象的范围控制更稳。

盲审同时指出 Baseline 也有可由材料计算但帮助有限的数字和轻微下一步外扩。这些问题不是本原子新增规则的目标，不据此增加提示或修改基线。

## 结论

**FAIL，产品变更完整撤回。**

本原子没有形成跨题一致的语言回退，但 T02 出现 Candidate 独有的事实范围扩大，违反“真实写稿不得新增事实、主体、状态或范围回退”的验收条件。该失败不升级为新的共性风险，也不作一例一修；它仅证明这组六项枚举当前不适合作为可安全删除的入口重复项。

保留本记录和忽略目录中的原始稿、匿名包与盲审结果；不补抽、不改题、不发布。

## 撤回后回归

- `python -m unittest discover -s tests`：354/354 通过。
- Promptfoo smoke：沙箱内三次均因 Node 无法启动目标 Python 而产生 20 个 provider 环境错误，没有进入产品断言；改用已核验的系统 Python 在沙箱外按同一 smoke 入口复跑，20/20 通过，0 failed，0 errors，judge consistency 1.0。
- `python tools/run_real_prompt_ablation.py ...`：固定 v1.5.21 与撤回后的 current 均为 108/108。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过，仅有 Windows 换行提示。
