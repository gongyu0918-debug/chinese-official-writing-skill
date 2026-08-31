# v1.6.22 发布记录

日期：2026-08-31。

## 发布范围与提交

- 发布产品提交：`4b135c506b4b4d61f49115298bc78564b5ec8f50`；上一正式产品 tag：`v1.6.21^{commit}=8086ff255f04df8b080ef1a0488236295bf2cb8d`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.22`。产品增量为 `UL-006` 阶段性事故通报的无显式下限近转写兜底、短通知主体/日期关系边界、`WR-023` 申请原因与材料缺口边界、`WR-024` 请示缘由与材料缺口边界。
- 付费提纲、Pro Hook、红头 DOCX、Red SkillHub 和下一版本研究均未操作。ClawHub 继续使用33文件无 Hook 普通包。

## 发布门与候选包

- 冻结发行 worktree 为 `codex/release-v1.6.22@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe`；远端发布前 `main@eba4d36f96986c7ee5c749bc30cae864508437a3` 是该提交祖先。产品 tag 固定在版本坐标提交 `4b135c50`，候选记录和状态测试不进入产品 tag。
- 本次复跑聚焦回归100/100通过；全量 unittest 747/747通过，耗时113.862秒。Promptfoo本地stub smoke为20/20，Skill 10胜、baseline 0胜、平票0、无效0、需人工复核0，judge consistency为1.0；该门不调用真实写稿模型。
- 固定 `v1.6.21` 与 current 的确定性真实用户式Prompt消融均为111/111，双方起草失败和改稿失败均为0；该门不调用LLM。`sync_adapters.py` 复跑后tracked diff为空，`git diff --check`与冻结工作树清洁检查通过。
- 发布回执状态更新后，状态/边界/包体/Hook聚焦回归100/100与活动Markdown链接7/7通过，canonical、Agent Skills、QwenWork、Qwen Code、Hermes五套Skill Creator `quick_validate.py`均返回`Skill is valid!`。首次误把外部validator写成不存在的仓内`maintenance/tools/quick_validate.py`，五次调用均在读取产品前以路径不存在退出；随后用实际Skill Creator路径原样重跑通过，不把失效命令记为产品失败或通过。
- SkillHub.cn 正式包82文件，本地规范化文件树fingerprint为`6b97bb1ef28789360004b1a580ee724fef2c97f4758ebd2a9bf141a378457ed2`；包内slug `chinese-official-writing`、展示名“中文公文写作”、版本`1.6.22`，含`LICENSE.md`，排除根`LICENSE`与`agents/openai.yaml`。
- ClawHub 正式目录33文件，本地规范化文件树fingerprint为`0ce2f2e2b3929d65e9970b73d0c31d67f69ce36e09dedc59538cf434db754427`；Hook路径、Hook内容、`agents/openai.yaml`、付费提纲和红头实现命中均为0。dry-run返回`would-publish`、33文件和平台fingerprint `05fdf89bb00b22a49359edcfbdec47c1094bacfbf7ca9cdeeca469b56bebdfed`。

## GitHub 回执

- 远端 `main` 在产品发布时推进到冻结候选 `62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe`；annotated tag对象为`a145ffc66542c7acbb2e9c034693fcae01b4028a`，`v1.6.22^{commit}=4b135c506b4b4d61f49115298bc78564b5ec8f50`。主线和tag以一次atomic push成功，没有force push或tag移动。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.22>，`databaseId=379466459`、`draft=false`、`prerelease=false`、`publishedAt=2026-08-31T02:06:07Z`。
- 更新说明只陈述用户可见增量：短稿完整性，以及短通知、申请和请示的主体、日期、缘由与材料缺口处理；未混入内部排除项。

## SkillHub.cn 回执

- slug `chinese-official-writing`、`skillId=70149`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- dry-run先返回`dryRun=true`、slug和版本正确；正式提交一次成功：`ok=true`、`versionId=277452`、`fileCount=82`、平台fingerprint `5118a74e73b3a5d1ec2c0167cbef1f222856192225b2251e7847a66efa1f32ec`，八个既有tags含`latest`均在提交回执中指向1.6.22。
- 提交回执中的`reviewStatus`、`securityScanStatus`、`contentAuditStatus`均为`pending`。首次只读公开接口仍显示latestVersion 1.6.21，但tags已指向1.6.22；期间未重复提交，当前记为`ACCEPTED / REVIEW_PENDING / PUBLIC_LATEST_PENDING`。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类`productivity,knowledge`、话题`chinese-writing,official-writing,office-productivity,content-creation`保持不变。
- 正式提交一次成功：`status=published`、`versionId=k972jtvctk9hshdd0kqf149sks8dh3xf`、`fileCount=33`、平台fingerprint `05fdf89bb00b22a49359edcfbdec47c1094bacfbf7ca9cdeeca469b56bebdfed`。
- 提交回执中的`latestVersion`仍为1.6.21；首次精确1.6.22只读检查返回`Version not found`。后续只读复核确认公开latest与精确版本均为1.6.22，33个文件、Hook路径0，moderation与版本级security均为`clean`，平台许可证显示为既有`MIT-0`；期间未重复上传，当前记为`PUBLISHED_RECEIPT / PUBLIC_INDEX_CLOSED`。

## 剩余边界

- GitHub产品提交、annotated tag和Release已闭环；本发布记录只推进后续`main`，不得移动产品tag。
- SkillHub.cn与ClawHub均已各成功提交一次。ClawHub公开latest、精确33文件、零Hook路径与clean状态已闭环；SkillHub.cn仍等待审核和公开latest传播，成功回执不等于审核完成。后续只做只读复核，不重复上传。
- ClawHub包完全不含Hook。SkillHub.cn包包含公开仓库的普通Hook伴随能力，但不包含付费提纲、Pro Hook或红头实现。
