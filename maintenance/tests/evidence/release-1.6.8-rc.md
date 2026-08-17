# v1.6.8 本地发行候选

日期：2026-08-17

状态：`READY_LOCAL_CANDIDATE`。本地候选已完成发布前必要验证，不代表外部平台已经发布。

## 固定对象与范围

- 上一正式 tag：`v1.6.7^{commit}=44347003aa7af12b7b205621e255f5e9c1f2166b`。
- 候选起点：`main@d60f4d1ed9bc4e5393028a3cc0b2243f031b88b8`。
- 候选分支：`codex/v168-overlength-shortdraft-readme`。
- 写入本记录前的候选 HEAD：`93c2034ce5c17f850d0fd8a27a185a02712dbc2b`。
- 版本：`1.6.8`。
- 本版只包含短稿局部去重、README 制度示例替换、可选超长收束 Hook，以及冷审发现的规格解析、语义核验、异常回退和机械门修复。

## 真实结果与冷审

- Ollama 与 Alibaba DeepSeek V4 Flash 0731 max 完成短稿、超长压缩和制度示例的真实原型；失败稿继续收束后形成当前候选。
- Claude Code + Alibaba DeepSeek V4 Flash 0731 max 将同一 D0 从498字收束为285字，选择 D1，终稿回显与 SHA-256 闭合。
- 独立 SOL max 对该 D1 的篇幅、事实、状态、职责关系、结构和非重复六项均判 `PASS`。
- Grok 4.6 ultra 两轮只读冷审发现的可执行 P1/P2 已修复，最终增量复核为 `PASS`；最终机械门重放同一真实 D1 返回无拒绝理由。

## 发布前验证

- [x] 最终全量测试为616/616通过。此前一轮可读取回执为616项、3项发布元数据/README契约失败；同步 OpenClaw 说明版本并删除测试中的旧栏目断言后，3项聚焦复测和最终全量均通过。更早一次全量进程因桌面包装器未返回可续读句柄而未计入通过结果。
- [x] 超长 Hook、路由和复杂度20/20通过；真实 R6 的498→285稿件按最终机械门重放通过，候选 SHA-256 与在线事务凭证一致。
- [x] canonical、Agent Skills、Qwen Code、Hermes 四个通用包 quick validation 通过；`sync_adapters.py` 重跑幂等，`git diff --check`通过。
- [x] 三宿主 `over_length` companion 从最终 `main` 静态组装成功，均为 `installed=false`、`enabled=false`、`network_used=false`：Codex 54文件、fingerprint `cd92de257917f633eb8e106f2d8911759deb3d74e12be4e3f82713a38cb0593f`；CodeBuddy 53文件、`c93a9db30bc7c5e6a7adef847923625a959adba2c20e9dbf2468563e64d8e719`；Claude Code 53文件、`d636d4859c226c9309c8f853f1f7c9764b59b7d9dbccedd264c7fa7092e83d6a`。
- [x] 从最终 `main` 构建的 SkillHub 清洁包共60文件，根 MIT 全文一致，逐文件本地清单 SHA-256 为 `e36ee0e1e684223197d81c3bff6a8c231721c9034c05dcc6f9346eb62d5c475d`；dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.8`。
- [x] 最终 `main` 的 OpenClaw 无 Hook 包共33文件，Hook、插件、`agents/openai.yaml`、`delivery-review-gate.md` 和 `review_gate.py` 检出为0；本地逐文件清单 SHA-256 为 `0af125cb00b470dcd156a5743f84ba2cd869a0806e90af3401c869d2496aa1fd`。ClawHub 有效 dry-run 返回 `would-publish`、33文件、fingerprint `8957fe37581e4095bc0daf1588c08044aa6cc8205f620830447787424c609381`。
- [x] 用户已明确授权本轮发布 GitHub、SkillHub.cn 与 ClawHub `1.6.8`；Red SkillHub 未获授权且不在范围内。

ClawHub 第一次 dry-run 同时传入 `--source-repo` 但尚无最终 `--source-commit`，CLI 在任何发布动作前拒绝并返回非零；移除未闭合的来源参数后，使用同一包重跑有效 dry-run。正式发布将绑定最终 tag commit，并重新带齐来源参数。

建议的公开更新说明：

> 优化短稿局部去重和制度示例；新增可选超长收束 Hook，在明确超限时合并重复、有限压缩并复核事实和状态；修复字数规格解析、语义核验旁路和异常回退循环。

## 已知边界

- 本轮真实在线 D1 来自 Claude Code；Codex、CodeBuddy 已有静态兼容层和组装验证，但本轮未重跑在线超长生命周期。
- `over_length_continuation_limit` 是能力说明字段，不是宿主可执行配置；当前成功样本实际完成5次 Stop，不能据此推断其他宿主的在线延续预算。
- 普通 Skill 与 OpenClaw 包不含 Hook；ClawHub 只同步无 Hook 语义规则和版本。
