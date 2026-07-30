# 1.5.30 发布证据

## 范围

1.5.30 以 `v1.5.29=426911ac76538a582f5d7c1a8c9ef63ea12a9833` 为固定发布
基线，只发布 D2 中文占位盲区修复：

- 识别 `XX类`、`XX系统`、`XX项` 等紧接中文的 X 类占位；
- 保留 `XX发〔2026〕1号` 等合法文号；
- 不扩大到小写 `xx`、混写 `Xx` 或全角 `ＸＸ`；
- 不改变正文生成、任务路由、reference 加载、复核顺序、输出模式、修改次数、
  Hook、FSM 或回退方式。

桌面外部候选只作为线索。外部记录所称的 C903 原始稿不在归档中，因此不采信
其个案结论；本仓库从固定 1.5.29 独立复现漏检后，采用更窄的通用规则并重新
验证。独立审计见 `d2-placeholder-archive-audit-v1529-result-20260730.md`。

## 发布前验证

- `python -m unittest discover -s tests`：394/394，`OK`。沙箱内首次运行因
  Windows ACL 拒绝临时目录二级写入而产生 149 个环境错误；切换到系统权限环境
  后按同一测试入口完整通过。
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.29> --baseline-label v1.5.29 --current-root . --out output/release-1.5.30-ablation`：
  固定 1.5.29 为 110/110，Candidate 为 110/110。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：
  20/20，0 failure，0 error；Skill 10、baseline 0、tie 0，judge
  consistency 1.0，eval id `eval-J8l-2026-07-30T09:27:31`。
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：
  `Skill is valid!`。
- `python tools/sync_adapters.py`：canonical、Claude、Agent、Qwen、Hermes
  与 OpenClaw 镜像同步完成。六份 `scripts/prose_lint.py` SHA-256 均为
  `0E4A7B1BEE42D66125F531CDB1EB4E1FF2AF2A8C94D23DA02E72A4407D32359B`。
- `git diff --check v1.5.29..HEAD` 与工作树 `git diff --check`：通过。

本版只改变确定性检测器及其测试，不改变写稿 Prompt 或 reference，因此不新增
真实写稿样本，也不把历史 MIXED 候选的稿件质量结果计入本版收益。

## 发行包与平台状态

- GitHub：发布前只读核验 `origin/main=ce2035948457da1ba4ddda06ce68d4dbeb3ef573`；
  `v1.5.29` 解引用为固定基线提交，正式提交、tag object 和 Release 待发布后记录。
- ClawHub：dry-run 为 27 个文件、fingerprint
  `589214d353391f1d8bf382d4015f0821a3ecd14caa15157383a0ca86ee894f63`，
  发布前公开 latest 为 1.5.29，moderation 为 clean；正式回执待记录。
- skillhub.cn：26 文件清洁包排除 `agents/openai.yaml`、Codex 门禁说明和两项
  门禁脚本；dry-run 返回 1.5.30。正式回执和公开传播状态待记录。
- 小红书 Red SkillHub 不在本次发布范围。

## 剩余风险

- 小写、混写和全角 X 占位没有三次以上正常场景证据，本版不扩大规则。
- 检测器只定位问题，不自动改稿；中文占位是否为真实业务缩写仍由 Agent 结合
  上下文判断。
- 平台提交、公开 latest、审核、扫描和 provenance 分别核验，异步传播不触发
  重复发布。
