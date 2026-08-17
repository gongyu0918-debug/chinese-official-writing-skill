# v1.6.9 本地发行候选

日期：2026-08-18

状态：`READY_LOCAL_CANDIDATE`。本文件只记录本地候选，不代表 GitHub、SkillHub.cn、ClawHub 或其他平台已经发布。

## 固定对象与范围

- 上一正式 tag：`v1.6.8^{commit}=6b1dc2c507d2a7f240506a036c6859620dd0f43a`。
- 候选起点：`main@7e54e60b155c065ebc1c889ecf297f08f038b960`。
- 候选分支：`codex/release-v1.6.9`。
- 版本同步提交：`b85424689a00132416e8b5ea1dd4c7f65a9894ed`。
- 目标版本：`1.6.9`。
- 产品更新只包含超长 Hook 边界修复和自然审稿旁路完善。SkillHub `50k+` 徽章及维护台账属于仓库文档，不写入版本更新说明。

## 已有直接证据

- Qwen 3.8 max 冷审指出的软性字数表达、长引语、否定责任短语、无标点阿拉伯编号正文和同动词多拟办对象问题已复现并修复。
- v1.6.8 已通过 SOL max 的真实 D1 从498字收束为285字；该稿件按修复后的机械门重放，无拒绝理由，原稿和候选哈希均与在线事务一致。
- “只读审核、帮我审核、审稿模式、审一下稿、看看哪里有问题”等自然审稿表达，以及审后改写、审核并优化和材料引语反控，已完成代表性事件回放。

## 候选包

- 根目录：`F:\Workspaces\chinese-official-writing-skill\output\release-candidates\v1.6.9-local-r1`。
- SkillHub 清洁包：60 文件；路径、NUL 分隔和 LF 规范化内容的 SHA-256 为 `da3b0ced66e815df87c5eb22945bb38ded0047e5d0c805fe71afbb740b3dbbb3`。
- ClawHub 无 Hook 包：33 文件；同口径 SHA-256 为 `046aac1a88f1d962b424dd9a106b1a18d60ecf0df79e202898e7650f75adcfc0`。
- 两包许可证 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`，与根 MIT `LICENSE` 一致。
- SkillHub 包不含无扩展名 `LICENSE`、`agents/openai.yaml`、插件 manifest、嵌套 `skills/` 或 `plugins/`；ClawHub 包不含 Hook、插件、`agents/openai.yaml`、交付门禁 reference 或 `review_gate.py`。

三宿主 `over_length` 静态 companion 仅组装、未安装、未启用、未联网：

- Codex：54 文件，fingerprint `4f92f097ebd5fc56ec07b67c6039f87178879b1b8578cbe69848b01c2e0d59b1`。
- CodeBuddy：53 文件，fingerprint `f0143b3c0c47c2b1c0a48b057d5ccee78397b1289c131d72d6e1bbffab6c0bf1`。
- Claude Code：53 文件，fingerprint `4c8a17702a4d2d91d69520ba3459d863a0e2c8c2e6dc04d718c98d800eb3dae1`。

## 实际验证

- `python -B -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_readme_badges maintenance.tests.test_over_length_capability maintenance.tests.test_gate_stop_hook maintenance.tests.test_hook_layer_contract -q`：120/120 通过。
- `python -B -m unittest maintenance.tests.test_host_gate_adapter maintenance.tests.test_claude_gate_adapter maintenance.tests.test_hook_layer_contract maintenance.tests.test_over_length_capability -q`：41/41 通过。
- `python -B -m unittest discover -s maintenance/tests -p "test_*.py" -q`：617/617 通过。第一次执行在桌面执行器转后台后遗失最终回执，不计入通过结果；随后只补跑一次并取得 `Ran 617 tests in 62.595s / OK` 的有效回执。
- canonical、Agent Skills、Qwen Code、Hermes 四个普通 Skill 均通过 `quick_validate.py`。
- `sync_adapters.py` 再运行后工作树仍干净，证明同步幂等。
- 相关 Python 文件编译检查、`git diff --check` 和终态工作树检查通过。编译检查第一次误写了不存在的模块文件名，未执行产品文件；改为实际 `hooks/capabilities/over_length/runtime.py` 后通过。
- SkillHub CLI 本地 dry-run 返回 `{"dryRun": true, "slug": "chinese-official-writing", "version": "1.6.9"}`，没有发起 HTTP 请求。
- 上一 tag 是当前候选祖先；`v1.6.8^{commit}..b8542468` 共 8 个提交、20 个文件、`+274/-56`。其中发布回执、维护记录和 README 下载徽章不是 1.6.9 产品更新说明内容。

组包时首次使用 `Copy-Item -LiteralPath` 携带通配符，导致 ClawHub 目标保持空目录；确认目标为空后改用固定源目录逐项复制，最终33文件边界和哈希均重新核验。三宿主组装首次循环误用了 PowerShell 内置只读变量名，未生成输出；更名后重新组装并取得上述回执。这两项均为本地命令层更正，不是产品或宿主适配失败。

## 未执行的外部动作与剩余边界

- 未推送分支，未创建或移动 tag，未创建 GitHub Release，未上传 SkillHub.cn 或 ClawHub。
- 本候选没有新增三宿主在线生命周期样本；超长收束沿用 v1.6.8 的 Claude Code 在线 D1，并已按本轮机械门重放通过。Codex、CodeBuddy 的当前静态 companion 只证明可组装，不冒充本版本在线成功。
- `AH-001` 共享硬锚抽取仍是后续研究项，不属于 1.6.9。

建议的公开更新说明：

> 修复可选超长收束 Hook 对“约、左右、上下”等软性字数表达的误触发，并加强长引语、编号正文、责任主体和多拟办对象保护；完善自然审稿识别，“帮我审核、审一下稿、审稿模式、看看哪里有问题”等表达可保持只审不改，审后改写和材料引语仍按成稿任务处理。
