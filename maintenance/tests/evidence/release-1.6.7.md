# v1.6.7 发布记录

日期：2026-08-17

## 发布范围与提交

- 发布产品提交：`44347003aa7af12b7b205621e255f5e9c1f2166b`。
- 上一正式产品 tag：`v1.6.6^{commit}=b49da7f2a5a8ac2327252d29efd66f1d54ccbc35`。
- 首次发行时发布 GitHub `main`、annotated tag `v1.6.7`、GitHub Release 和 SkillHub.cn `1.6.7`；ClawHub 当时未操作。
- 2026-08-17 取得用户后续明确授权后，将仓内无 Hook OpenClaw 兼容包单独同步到 ClawHub `1.6.7`；Red SkillHub 及其他平台仍未操作。

## 主要变化

- 对只有上限或没有硬下限的简短正文增加独立自然收束规则，减少短篇套用长报告骨架、同义复述、口号式结尾和正文外包装。
- 明确短稿规则不承担硬下限补字；明确下限或区间仍由普通写稿流程和可选 under-length 能力分别处理。
- 按行为不变原则拆分 Hook core 与 `review_gate.py` 的历史超长函数，保留原有协议字段、状态、reason、门禁顺序、D0/D1选择和异常回退。
- 常用语机械化 R1—R6 因真实写稿仍有事实、篇幅或文种回退而保持 HOLD；本版没有修改常用语总表。

## 真实写稿与发布前验证

- 短稿自然度 R3 共8/8技术有效；独立 SOL max 判候选3胜、基线0胜、难分1，候选四稿事实、状态、篇幅、文种和直接使用成本全部通过。
- 最小接入后，Ollama 报告和 Alibaba 新闻两份真实稿均读取新增短稿页并保持可用。
- Hook 重构后使用 Claude Code 2.1.195、Alibaba DeepSeek V4 Flash 0731 max 完成1次真实 D0 生命周期；插件注册、Skill读取、三类事件、事务、选择和终稿 hash 均闭合。
- 版本、包边界、README、可达性、短稿、review gate、Hook core、复杂度与组装合同共282项直接相关测试通过；最终版本边界80/80通过。
- canonical、Agent Skills、Qwen Code、Hermes 通用 quick validation 通过；OpenClaw 由专用包边界2/2验证。三宿主 companion 静态组装成功，`sync_adapters.py` 幂等，`git diff --check`通过。

## GitHub 回执

- 远端 `main`：`44347003aa7af12b7b205621e255f5e9c1f2166b`。
- annotated tag object：`7ebaf2cc4c4520fa765233291cf85e4489b20aad`；`v1.6.7^{commit}`：`44347003aa7af12b7b205621e255f5e9c1f2166b`。
- GitHub Release：[`v1.6.7`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.7)，`id=371479432`、`draft=false`、`prerelease=false`、`published_at=2026-08-17T01:07:35Z`。

## SkillHub.cn 回执与传播状态

- 最终清洁包路径：`output/release-candidates/v1.6.7-release-final/skillhub-package/`；共58文件，排除 `agents/openai.yaml` 和无扩展名 `LICENSE`，另带根 MIT 全文的 `LICENSE.md`。
- 本地逐文件清单 SHA-256：`9b41b78c5d93a44a9c027a4c548d0c4d2424601780b0e85a2ecd8440733103a1`。
- GitHub 本地源码归档 SHA-256：`217a70fcdd6f7f8164706171c45f05340e4819f9dc74895e991cd03a80261c18`，绑定发布产品提交。
- dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.7`。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=240948`、`fileCount=58`、平台 fingerprint `9bd49c6570ad2262c73d814032a251454e1f826571b2146d23c6bba4d374d7da`。
- 原始正式回执 JSON 字节 SHA-256：`03d001bbc8fc5fc2028c62ecf9ff92d0c1d20e116b948aff45288888d37f5ba8`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.7`；公开版本计数为70。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。
- 上传后即时只读查询时，公开 `latestVersion` 仍为 `1.6.6`，1.6.7 精确版本签名端点返回404。公开页显示的 benign 报告仍属于既有可见版本，不能替代1.6.7回执中的 pending 状态；该状态属于平台异步传播，不重复上传。

## ClawHub 后续同步回执与传播状态

- 发布源为 `packages/openclaw/skills/chinese_official_writing/`，绑定 `v1.6.7^{commit}=44347003aa7af12b7b205621e255f5e9c1f2166b`；包内 `SKILL.md` 版本为 `1.6.7`。
- 包共33文件；Hook、宿主插件、`agents/openai.yaml`、`references/delivery-review-gate.md` 和 `scripts/review_gate.py` 均未进入发布包。
- ClawHub CLI `0.23.1` dry-run 返回 `would-publish`，文件数33、fingerprint `fbbef734bf01d2ff0bef97ebdf9c0c99d42c5479971b61e0f28fa9b46b04bad1`。
- 正式提交一次返回 `ok=true`、`status=published`、version `1.6.7`、`versionId=k975vyhpk6092rv7yjbjszw8fs8cnfxh`；文件数和 fingerprint 与 dry-run 一致。
- ClawHub 平台按其统一规则显示 MIT-0；仓库与仓内兼容包仍由根 MIT 许可证覆盖，两者未通过本次同步相互改写。
- 提交后两次精确版本只读查询均返回 `Version not found`，公开 latest 仍为 `1.6.4`；强制安装未取得1.6.7内容。该状态记录为平台扫描/索引尚未完成，不重复上传。

## 剩余事项

- 等待 SkillHub 公开 `latestVersion`、精确版本签名及1.6.7审核、安全、内容状态异步更新；只读复核，不重复提交。
- 等待 ClawHub 公开列出1.6.7后，再核对33文件清单和下载内容 fingerprint；只读复核，不重复提交。
- 短稿明确下限仍由 under-length 处理；常用语机械化候选继续 HOLD，不因本次发布改称已解决。
- Hook 重构后的真实在线 smoke 走 D0 路径；D1 repair/verdict 的既有确定性覆盖保持不变，本次不把该样本扩张为新的质量宣称。
