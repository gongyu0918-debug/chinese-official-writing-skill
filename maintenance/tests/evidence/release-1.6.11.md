# v1.6.11 发布记录

日期：2026-08-20

## 发布范围与提交

- 发布产品提交：`15af538adfb5ec6a711770d67ec265498ec7127d`。
- 上一正式产品 tag：`v1.6.10^{commit}=af12b771e376e815c44d53b08d26c635805586b3`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.11`；Red SkillHub 及其他平台未操作。
- 三个平台均使用公开非付费版；付费提纲能力 `outline_assist` 未进入源码 tag、SkillHub 包或 ClawHub 包。
- ClawHub 使用33文件无 Hook 包；可选 Hook 只进入 GitHub canonical 与 SkillHub 清洁包。

## 主要变化

- 完善进行态与责任主体边界，避免把未决状态机械改成无主体动作。
- 允许同数中文数量的透明归纳进入语义核验，不直接越过事实和归属检查。
- 修复相对期限、序号和修辞性“一方面/另一方面”的共享硬锚误判。

## 发布前验证

- 发行定向测试88/88通过。
- 全量测试首次为639/640，唯一失败是测试仍锁定旧进行态措辞；只更新断言后单项1/1通过，最终全量640/640通过，产品和包字节未变化。
- 固定 v1.6.10 与当前候选的确定性消融均为111/111。
- canonical、Agent Skills、Qwen Code、Hermes 通过 quick validation；`sync_adapters.py` 二次执行无差异，`git diff --check`通过。
- SkillHub 清洁包61文件，文件清单+逐文件 SHA-256 指纹为 `0a4e89b63dd8aaf62dccbb670faf8506248d62df8e40b0cfecacb50b3093563f`。
- ClawHub 无 Hook 包33文件，同口径指纹为 `ce9f4b55846d25d7ef2966a7564920454fda1943b0e403371ce498d48ee04886`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数均为0。
- 两包许可证 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`，与根 MIT `LICENSE` 一致。

## GitHub 回执

- 远端 `main`：`15af538adfb5ec6a711770d67ec265498ec7127d`。
- annotated tag object：`9ad0cecf936eb3c54b0f79619fb0162bb368d34f`；`v1.6.11^{commit}`：`15af538adfb5ec6a711770d67ec265498ec7127d`。
- GitHub Release：[`v1.6.11`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.11)，`id=RE_kwDOSXovUM4WQxm4`、`draft=false`、`prerelease=false`、`published_at=2026-08-20T04:52:17Z`。
- 本发布证据在 tag 之后单独推进 `main`，不移动已发布 tag。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=249279`、`fileCount=61`、平台 fingerprint `3d08c64a23d4233116cfa082720ca8f9b2132cd6c2be042a9e064e98a6b53e2b`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.11`；公开版本计数由73增至74。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。提交后的首次只读复核中，公开 `latestVersion` 仍为1.6.10，1.6.11精确版本签名返回404；未重复上传。

## ClawHub 回执与传播状态

- 正式提交一次：`ok=true`、`status=published`、`versionId=k978xhang829wcxy68tmwbqxz18cv6js`、`fileCount=33`、fingerprint `5663d0a04affe3bb9dea812c143e55514e24b8a0b711a190f4a84aeb50b88655`。
- 展示名为“中文公文写作”；分类提交为 `productivity,knowledge`，话题为 `chinese-writing,official-writing,office-productivity,content-creation`。
- 提交后的首次只读复核中，精确版本仍返回 `Version not found`；未重复上传。后续复核时公开 `latestVersion` 与精确版本均为1.6.11，moderation 为 `clean`。
- 远端33个文件逐项与本地发布包比较：缺失0、哈希不一致0、多余0；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数为0。
- ClawHub 页面按平台统一规则显示 MIT-0；GitHub 仓库和上传包内 `LICENSE` 使用根 MIT 许可证。

## 剩余边界

- `UL-005` 篇幅语义验收来源绑定、付费提纲组合和提纲修正继续 HOLD，未进入本版本。
- ClawHub 精确版本与无 Hook 文件清单已闭环；SkillHub 精确签名仍继续只读复核，不因索引滞后重复发布。
