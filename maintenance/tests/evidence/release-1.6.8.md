# v1.6.8 发布记录

日期：2026-08-17

## 发布范围与提交

- 发布产品提交：`6b1dc2c507d2a7f240506a036c6859620dd0f43a`。
- 上一正式产品 tag：`v1.6.7^{commit}=44347003aa7af12b7b205621e255f5e9c1f2166b`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.8`；Red SkillHub 及其他平台未操作。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 包，只同步语义规则和版本；可选 Hook 仅进入 GitHub canonical 与 SkillHub 清洁包。

## 主要变化

- 短稿按局部事项收束，同一原因、理由、目的、事实、动作和状态不在邻近句组重复展开。
- GitHub README 将旧制度示例替换为事实与职责关系明确的八条制度正文。
- 新增可选超长收束 Hook：只在明确上限或区间且完整稿超出上限10%以上时启用；先观察语义重复，再最多两次压缩，并用哈希绑定的语义 verdict 检查事实、状态、责任关系、结构和自然度。
- 修复重复清理达到上限后绕过语义核验、多条字数规格取值、runtime 丢失后的 D0 回显循环、终态重入、明确状态升级和责任主体误判。

## 真实写稿、冷审与验证

- Ollama 与 Alibaba DeepSeek V4 Flash 0731 max 先完成短稿、超长压缩和制度示例原型；失败稿驱动规则收束。
- Claude Code + Alibaba DeepSeek V4 Flash 0731 max 将同一 D0 从498字收束为285字，选择 D1，终稿回显与 SHA-256 闭合；独立 SOL max 对篇幅、事实、状态、职责关系、结构和非重复六项均判 `PASS`。
- Grok 4.6 ultra 两轮只读冷审发现的可执行 P1/P2 已修复，最终增量复核为 `PASS`；最终机械门重放同一真实 D1 返回无拒绝理由。
- 最终全量测试616/616通过，发布边界与 SkillHub builder 79/79通过；四个通用包 quick validation、同步幂等、三宿主静态组装与 diff check 通过。一次可读取的前置全量回执曾有3项发布元数据/README契约失败，修复后才形成上述最终通过结果；另一次桌面包装器未返回句柄的运行不计作通过。

## GitHub 回执

- 远端 `main`：`6b1dc2c507d2a7f240506a036c6859620dd0f43a`。
- annotated tag object：`d4af7f79c9bbbb8959339bc3e51289cd2b4f6da9`；`v1.6.8^{commit}`：`6b1dc2c507d2a7f240506a036c6859620dd0f43a`。
- GitHub 源码归档 SHA-256：`ce38663c74cc71d7e4c675ab332a162be29379bf4acc0a63c1c542ce6a0b735d`。
- GitHub Release：[`v1.6.8`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.8)，`id=371686942`、`draft=false`、`prerelease=false`、`published_at=2026-08-17T10:48:32Z`。

## SkillHub.cn 回执与传播状态

- 发布包路径：`output/release-candidates/v1.6.8-release-final/skillhub-package/`；60文件，排除 `agents/openai.yaml` 和无扩展名 `LICENSE`，另带根 MIT 全文的 `LICENSE.md`。
- 本地逐文件清单 SHA-256：`e36ee0e1e684223197d81c3bff6a8c231721c9034c05dcc6f9346eb62d5c475d`。
- dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.8`。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=242369`、`fileCount=60`、平台 fingerprint `5138cdf44ad41d720371f646e74246057447847a028332edf0b1209eb45e8877`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.8`；公开版本计数为71。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。上传后即时查询时 `latestVersion` 仍为1.6.7，1.6.8精确版本签名返回404；属于平台异步传播，不重复上传。

## ClawHub 回执与传播状态

- 发布源为 `packages/openclaw/skills/chinese_official_writing/`，绑定 `v1.6.8^{commit}=6b1dc2c507d2a7f240506a036c6859620dd0f43a`；包内版本为1.6.8。
- 包共33文件；Hook、宿主插件、`agents/openai.yaml`、`references/delivery-review-gate.md` 和 `scripts/review_gate.py` 均未进入发布包。本地逐文件清单 SHA-256 为 `0af125cb00b470dcd156a5743f84ba2cd869a0806e90af3401c869d2496aa1fd`。
- dry-run 与正式提交的 fingerprint 均为 `8957fe37581e4095bc0daf1588c08044aa6cc8205f620830447787424c609381`；正式提交返回 `ok=true`、`status=published`、`fileCount=33`、`versionId=k979cmymj5sdd1f9mw3t0789b58cnmvm`。
- 第一次 dry-run 因只给 `--source-repo`、未同时给最终 `--source-commit` 而在发布前被 CLI 拒绝；补齐边界后有效 dry-run 和正式提交均成功，没有重复正式发布。
- 提交后即时查询时公开 latest 仍为1.6.7，1.6.8精确版本暂不可见；只读等待传播，不重复上传。ClawHub 平台按统一规则显示 MIT-0，仓库和仓内包仍由根 MIT 许可证覆盖。

## 发布后冷审发现与下一补丁

Qwen 3.8 Max 独立只读冷审在发布动作进行期间完成。其对固定候选 `a7f82af2` 报出的 README 旧断言、OpenClaw 版本说明和 RC 断链均已在发布前修复，并由最终测试覆盖；同时新增以下后续修复项：

- `控制在500字左右`、`至多500字左右` 目前可能被 over-length 解析为硬上限，存在可选 Hook 误触发风险；下一补丁应把尾随近似词纳入软目标判断。
- 超过160字的引语仍主要依赖语义 verdict；`不得由某主体负责` 可能造成安全方向的 D0 回退；无标点编号正文行可能被当作标题；同一动词对应多个拟办对象时，机械状态保护仍需按对象收窄。
- 数字值必须至少保留一次，但不恢复“重复出现次数完全相等”的旧门；数值去重继续交语义 verdict 判断归属关系。

这些风险仅存在于用户明确启用的可选超长 Hook；失败默认保留 D0，普通 Skill 和 ClawHub 无 Hook 包不受影响。已发布 tag 不移动、不覆盖同版本，后续以新补丁版本修复。

