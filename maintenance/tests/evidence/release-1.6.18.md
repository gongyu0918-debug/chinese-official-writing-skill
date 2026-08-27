# v1.6.18 发布记录

日期：2026-08-27。

## 发布范围与提交

- 发布产品提交：`67a68257f8a79220a38e961ced932bcb022cf86b`；上一正式产品 tag：`v1.6.17^{commit}=7b4577843d6d98e5583aa6615d813c1c82a56db3`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.18`；小红书 Red SkillHub、付费分支及其他平台未操作。
- GitHub 与 SkillHub.cn 新增已验证的 OpenCode 1.18.23 常驻交互 adapter、共享 core 的精确 `HostAbort`、组装/测试及工程记录；公开写作规则、description 和 references 相对 v1.6.17 不变。
- Hermes 真实稿未复现适合同步 transform 安全处理的共同目标，因此没有 adapter。ClawHub 只同步版本坐标，继续使用33文件无 Hook 普通包，正文规则与v1.6.17逐字相同。

## 发布门与候选包

- 全量 unittest 701/701通过；发布定向回归最终174/174通过；固定 v1.6.17/current 确定性消融分别111/111、111/111，无新增 create/revise failure。
- Promptfoo 本地 stub smoke 20/20通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；138个 tracked Python 文件内存编译、142个 tracked JSON 文件解析通过；镜像同步复跑 diff hash 不变。
- SkillHub.cn 正式上传包73文件，本地文件树指纹 `4ff2cb68beff03a09a9372d8c26eb2d0d0c9aabbde6aa56e5ae615b478f16c61`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。
- ClawHub 正式上传目录33文件，本地文件树指纹 `b09972521d52871e4345c40074683db58374d5bd12fca8413cc6dae332de6f53`；Hook路径和Hook内容为0，`agents/openai.yaml`、付费提纲和红头实现路径为0。最终 source-bound dry-run 绑定产品提交，返回平台 fingerprint `f71bf08951ea28860d14602950aab7ee43d7bd482a2ccc71e40d909f363a765d`。

## GitHub 回执

- 远端 `main` 与 `v1.6.18^{commit}` 在产品发布时均为 `67a68257f8a79220a38e961ced932bcb022cf86b`；annotated tag object 为 `f94752dc49da1568b0820b427d73f05dd8dfc32f`。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.18>，`databaseId=377599589`、`draft=false`、`prerelease=false`、`publishedAt=2026-08-27T06:14:10Z`。
- `main` 与 annotated tag 原子推送；GitHub Release 创建一次成功。

## SkillHub.cn 回执

- slug `chinese-official-writing`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=272847`、`fileCount=73`、平台 fingerprint `b5f1085c6caead9f8bffcf17adafd45613c425f9a3a91dde6db7e0c7fc21b110`；八个既有 tags 含 `latest` 均指向1.6.18。
- 首次只读搜索仍显示1.6.17且精确签名未就绪；未重复提交。后续公开搜索已显示精确坐标、正确展示名和1.6.18；本地正式 zip 对平台签名验证 `content_hash_match=true`，content hash 为 `3a02eb4a680851ecf04c5bb3090fc4e5f2436726405b007585362b8c54457f55`。
- 上传回执中的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 仍为 `pending`，不改写为审核完成。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变。
- ClawHub 0.23.3 正式提交一次获受理：`status=pending-publication`、`versionId=k9745n8v3wgavpdb736s7v5a0n8d9rda`、`attemptId=zx704wzg5ccn1r7xnyvfn08vjx8d9p81`、`fileCount=33`、平台 fingerprint `f71bf08951ea28860d14602950aab7ee43d7bd482a2ccc71e40d909f363a765d`。首次回读仍为旧 latest，期间未重复提交。
- 后续 `latestVersion`、`tags.latest` 与精确版本均为1.6.18。精确远端33文件与本地比较：缺失0、额外0、SHA-256不一致0、Hook路径0；安全状态为 `clean`。首次精确回读的 `hasWarnings=false` 随异步扫描传播变为 `true`，不把早期瞬时值写成终态，也不把总体clean外推为该布尔字段已消失。

## 剩余边界

- GitHub、SkillHub.cn 与 ClawHub 公开版本均已到1.6.18；ClawHub 精确33文件、哈希和安全状态已闭环。
- SkillHub.cn 三项异步审核/扫描仍为pending，不重复上传；平台后续状态不能由本回执预判。
- OpenCode adapter 只支持1.18.23常驻交互 CLI，中间响应可见；无头 `run` 旁路。Hermes 没有 adapter，ClawHub 包完全不含 Hook。
- 付费提纲和红头 DOCX 能力继续只在独立分支管理，未发布、未反向合入公开 `main`。
