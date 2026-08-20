# v1.6.11 本地发行候选

日期：2026-08-20

状态：`READY_LOCAL_CANDIDATE`。本文件绑定本地发行分支；发布完成前不代表 GitHub、SkillHub.cn 或 ClawHub 已存在1.6.11。

## 固定对象与范围

- 上一正式 tag：`v1.6.10^{commit}=af12b771e376e815c44d53b08d26c635805586b3`。
- 公开候选起点：`main@f07eae5b`。
- 候选分支：`codex/release-v1.6.11`。
- 版本准备提交：`156da3b4`。
- 校验契约修正提交：`92cfa85c`。
- 目标版本：`1.6.11`。
- 公开包不包含本地付费提纲能力 `outline_assist`。
- SkillHub 使用 canonical 清洁包并保留可选 Hook；ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 无 Hook 包。

## 主要变化

- 完善进行态与责任主体边界，避免把未决状态机械改成无主体动作。
- 允许同数中文数量的透明归纳进入语义核验，不直接越过事实和归属检查。
- 修复相对期限、序号和修辞性“一方面/另一方面”的共享硬锚误判。

## 已有真实证据

- 状态、进行态与责任主体5个真实小样本通过独立 SOL 复核。
- WorkBuddy/CodeBuddy 对同一106字 D0 完成中文数量透明归纳在线事务；含新增对象和错归属的候选被语义层选择 D0。
- Claude Code 在线压缩修辞性方面并选择 D1；相对期限变化在当前产品生命周期复放中以中文数量原因选择 D0并逐字交付原稿。

## 实际验证

- 发行定向测试88/88通过。
- 全量测试首次为639/640，唯一失败是测试仍锁定旧进行态措辞；只更新断言后单项1/1通过，最终全量640/640通过。产品和包字节未因该修正变化。
- 固定 v1.6.10 与当前候选的确定性消融均为111/111。
- canonical、Agent Skills、Qwen Code、Hermes 四个普通入口均通过 quick validation。
- `sync_adapters.py` 二次执行无差异；`git diff --check`通过。

## 候选包

- SkillHub 清洁包61文件，文件清单+逐文件 SHA-256 指纹为 `0a4e89b63dd8aaf62dccbb670faf8506248d62df8e40b0cfecacb50b3093563f`。
- ClawHub 无 Hook 包33文件，同口径指纹为 `ce9f4b55846d25d7ef2966a7564920454fda1943b0e403371ce498d48ee04886`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数为0。
- 两包许可证 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`，与根 MIT `LICENSE` 一致。
- SkillHub dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.11`。
- ClawHub dry-run 返回 `status=would-publish`、latestVersion `1.6.10`、fileCount `33`、平台 fingerprint `5663d0a04affe3bb9dea812c143e55514e24b8a0b711a190f4a84aeb50b88655`；展示名为“中文公文写作”。

## 未执行与剩余边界

- 尚未推送、创建 tag 或 GitHub Release，尚未正式上传 SkillHub.cn 与 ClawHub。
- `UL-005`、付费提纲组合和提纲修正继续 HOLD，不进入本版。
- 远端 main/tag 漂移复核通过后，才执行当次明确授权的三平台发布。
