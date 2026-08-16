# v1.6.6 发布记录

日期：2026-08-16

## 发布范围与提交

- 发布产品提交：`b49da7f2a5a8ac2327252d29efd66f1d54ccbc35`。
- 上一正式产品 tag：`v1.6.5^{commit}=81061bd78c0dbf5604fb2927ba275169fc93f5ed`。
- 本版发布 GitHub `main`、annotated tag `v1.6.6`、GitHub Release 和 SkillHub.cn `1.6.6`。
- ClawHub、Red SkillHub 及其他平台未上传；没有执行其上传、同步、删除、撤回或版本覆盖命令。

## 主要变化

- 完善约20类事务文体的功能、结构与常用语路由，按文种选择开端、承启、综合和结尾表达。
- 增强跨文种责任主体与合理推断约束：新增进展、承诺和预期须由材料主体、写作主体或近邻语篇主体承载。
- 补充编者按功能标识与相对时间锚保护；材料只给月份、月日或时间段时不自行补年份。
- 本版没有修改可选 Hook 的启用方式或运行行为；WR-005 普通短稿自然度继续 HOLD。

## 真实写稿与发布前验证

- 三条指定 DeepSeek V4 Flash 路线完成20份真实写稿；原型文种功能19/20，编者按标识修复后目标功能20/20。
- 编者按、演讲词和责任书完成候选直连复测；最终样本经独立 SOL max 复核，事实、状态、时间锚、责任主体、文种、篇幅和直接使用全部 PASS。
- 发布级全量回归：`python -B -m unittest discover -s maintenance/tests -p "test_*.py" -q`，603/603 PASS。
- 版本、README、镜像、OpenClaw 与 SkillHub builder 聚焦测试8/8 PASS；README 可达性4/4 PASS；canonical 与三套普通镜像 quick validation 全部 PASS。
- `sync_adapters.py` 重跑零 diff；`git diff --check`通过。

## GitHub 回执

- 远端 `main`：`b49da7f2a5a8ac2327252d29efd66f1d54ccbc35`。
- annotated tag object：`4331aab43160f6840f112a66ccb8c1803adb13c1`；`v1.6.6^{commit}`：`b49da7f2a5a8ac2327252d29efd66f1d54ccbc35`。
- GitHub Release：[`v1.6.6`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.6)，`id=371271831`、`draft=false`、`prerelease=false`、`published_at=2026-08-16T08:26:27Z`。

## SkillHub.cn 回执与传播状态

- 最终清洁包路径：`output/release-candidates/v1.6.6-release-final/skillhub-package/`；共57文件，排除 `agents/openai.yaml` 和无扩展名 `LICENSE`，另带根 MIT 全文的 `LICENSE.md`。
- 本地逐文件清单 SHA-256：`c827e0bc0d1049d679f99b818146e06856d64b47a686d3db75d0d230068ba3bc`。
- GitHub 本地源码归档 SHA-256：`57d70ab779aabc3f287473827be812bb1453853783ec8c9e7fd9f89a6cc9b6f5`，绑定发布产品提交。
- dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.6`。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=239977`、`fileCount=57`、平台 fingerprint `47f8ae885e3dda438fd96d6b153066f0ecc859c31fa88c478d2633493a94b59f`。
- 原始正式回执 SHA-256：`e43feeb1a3b61641f74c17aa9fb35870f9cf8af070a3c7b7e4881a2cbd3a9c2b`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.6`。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。
- 上传后即时只读查询时，公开 `tags.latest=1.6.6`、版本数69，但 `latestVersion` 仍为 `1.6.5`，1.6.6 签名端点返回404。该状态属于平台异步传播，不重复上传。

## 剩余事项

- 等待 SkillHub 公开 `latestVersion`、精确版本签名及审核、安全、内容状态异步更新；只读复核，不重复提交。
- WR-005 普通短稿篇幅、Markdown 洁净输出与重复/拖沓继续按独立原子处理，不借本版发布改称已解决。
