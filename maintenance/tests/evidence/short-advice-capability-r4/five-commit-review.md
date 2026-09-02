# WR-026-R4 五提交合并前复核

日期：2026-09-02。

固定主线：`main@821364abfd7df2fa0af04f5e3ab7277897110ff0`。五提交检查点：`eab2f3c2`。用户在本检查点后明确授权：候选真实写稿无问题且可合并时合入 `main`。

## 结论

`PASS_FOR_MAIN_MERGE`

R4 的产品差异只有意见建议专叶一行及五套逐字镜像：把原有“短反馈可以同节”扩为紧凑连续正文中的实际情形或依据、直接支持的影响或判断、有权对象建议和载体形式关系。`SKILL.md`、通用短稿页、description、Hook、版本文件及其他文种叶差异为零。

四家有效 provider 分别完成五道 Baseline 与 Candidate，共20份基线和20份候选；候选12份短意见正向稿均可直接使用，正式长意见和已决定通知控制没有跨provider候选相关硬回退。MiniMax 的材料外具体化在基线已存在且未被其他provider复现，记模型残余风险，不把合理的一层影响或判断误判为失败。Ollama DeepSeek、同provider的GLM回退以及随后两个全新任务初始化均未形成正文，只记技术无效。

## 范围、消融与结构门

- `git log --oneline main..HEAD`：五个提交依次为预登记、基线证据、canonical原型、五镜像同步、结果与规格收口。
- `git merge-base --is-ancestor main HEAD`：通过。
- `git diff --name-status main...HEAD`：产品面只含 canonical 专叶及 Agent Skills、Qwen Code、QwenWork、Hermes、OpenClaw 五套镜像；其余均为本原子预登记、题面、官方样本索引、结果、测试和状态记录。
- 同题消融：Baseline与Candidate使用相同五题；Alibaba两路和OpenCode保持已有可用能力，MiniMax两道短载体稿由编号式问题段改为紧凑连续正文。候选无需逐项文采胜过基线，但必须守住事实、权限、未决状态、文种与载体形态；上述硬边界通过。
- `python maintenance/tools/sync_adapters.py`：五套持久镜像同步，复跑后产品工作树无新增差异。
- 合并前 SkillHub 结构包：84文件，slug `chinese-official-writing`、展示名“中文公文写作”、结构版本仍为当前基线 `1.6.24`，fingerprint `e1e3a664810aff534c037d26730eca01ef9ddba7d79481af4b4179fcfd5a5bfa`；含46个公开Hook文件，付费提纲、红头实现、`agents/openai.yaml`和扩展名为空的根`LICENSE`命中0。该包只作结构检查，未保存、未上传。
- OpenClaw 包：35文件，fingerprint `bae1e5067b77dd60a763b10cb2e3a6e1a64b6f5ee144084365c4313dbb0375b1`；Hook、付费提纲、红头实现和`agents/openai.yaml`命中0。

## 实际回归

- `python -m unittest maintenance.tests.test_advisory_feedback_leaf maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability`：108项通过。
- `python -m unittest discover -s maintenance/tests -p "test_*.py"`：766项通过，耗时120.723秒。
- Skill Creator `quick_validate.py`：canonical、Agent Skills、Qwen Code、QwenWork、Hermes五处通过；OpenClaw因其既有合法扩展字段`category`不在通用校验器白名单而退出1，仓库宿主专项与镜像断言已通过，不冒充通用校验通过。
- `git diff --check main...HEAD` 首次发现预登记文件尾部多一空行；本检查点已删除该空行，复查必须通过后才允许合并。

## 冻结与剩余风险

- 本轮未修改本地冻结 `v1.6.25^{commit}=cf8e181591ea01ba81138352c12b5b93a8acf098` 或 `codex/release-v1.6.25@ead595b7aeda655104297e56600885e3117c9694`，也不发布、不推送、不移动tag。
- Ollama尚无本轮有效稿；用户提供的OpenCodex 2.39.0同`call_id`诊断因新会话未跑通，只留实验记录，不提升为通用规则。后续provider恢复时再用新会话复测。
- MiniMax的材料外具体措施倾向不是本候选新引入；只有出现与本行规则可重复归因的新反例时，才另拆原子，不在本轮添加泛化禁令。
