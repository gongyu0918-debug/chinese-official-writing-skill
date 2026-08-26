# v1.6.17 发布记录

日期：2026-08-26。

## 发布范围与提交

- 发布产品提交：`7b4577843d6d98e5583aa6615d813c1c82a56db3`。
- 上一正式产品 tag：`v1.6.16^{commit}=f6293aaaa4095530b386b50e3a56c07e35206af5`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.17`；小红书 Red SkillHub、付费分支及其他平台未操作。
- 本版是维护补丁：公开写作规则和 Hook 协议相对 v1.6.16 不变；新增内容为 v1.6.16 后真实写稿研究、状态收口、发布元数据和证据。
- ClawHub 使用33文件无 Hook 普通包；GitHub canonical 与 SkillHub.cn 清洁包保留默认关闭的可选 Hook。付费提纲、阶段 Hook 和红头 DOCX 能力未进入公开 tag 或平台包。

## 真实写稿依据与发布门

- `WR-013c` 两路均保留事实边界并形成低强度原因/预期；`WR-014-R6` 原目标2/2未复现，R6b仅见Ollama 1/2单 provider 风险；`WR-020a2` OpenCode 2326字符五节长报告通过，Ollama两次技术失效。没有跨模型共同目标失败，因此不新增写作规则。
- 全量 unittest 693/693通过；发布定向回归94/94通过。定向回归曾与镜像同步并行而读到重建中间态，串行有效样本已通过。
- 固定 v1.6.16/current 的确定性消融分别111/111、111/111，无新增 create/revise failure。
- Promptfoo 本地 stub smoke 20/20通过，Skill 10胜、baseline 0胜、平票0、无效0、judge consistency 1.0；该项不冒充真实模型写稿。
- canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；136个 tracked Python 文件内存编译、142个 tracked JSON 文件解析通过；镜像同步复跑 diff hash 不变。

## 候选包

- SkillHub.cn 正式上传包71文件，本地文件树指纹 `2ef79003a0cd9d0343d30f94d9b95c1414d5ae9e71910449ca449b8383bf4a54`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。
- ClawHub 正式上传目录33文件，本地文件树指纹 `7c68fd98e77e9f9cb7f4abf6ff8e483b7eacc727eaaf4ce6b6475e9eb75cb50f`；Hook、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。
- 本地指纹按相对 POSIX 路径排序，对每个文件依次写入 `path + NUL + bytes + NUL` 后计算 SHA-256。Windows 检出换行会改变字节指纹，平台回执指纹另列，不混用。

## GitHub 回执

- 正式产品推送时的远端 `main` 与 `v1.6.17^{commit}` 均为 `7b4577843d6d98e5583aa6615d813c1c82a56db3`；annotated tag object 为 `48390199524f40facb2ab32087708ae461fb284a`。
- GitHub Release：[`v1.6.17`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.17)，`databaseId=376934881`、`draft=false`、`prerelease=false`、`publishedAt=2026-08-26T07:01:29Z`。
- `main` 与 annotated tag 已原子推送；GitHub Release 创建一次成功。

## SkillHub.cn 回执与传播状态

- slug `chinese-official-writing`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=270678`、`fileCount=71`、平台 fingerprint `81cb86fd88f0ecb37dfe44beadd39532dec5ffe284bccdce8f8ff35ae5dbeadc`。
- 上传回执中 `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均指向 `1.6.17`；`reviewStatus`、`securityScanStatus`、`contentAuditStatus` 为 `pending`。
- 首次提交后的公开搜索已显示现有精确坐标、正确展示名和 version `1.6.17`；没有重复上传。

## ClawHub 回执与传播状态

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变。
- 本机旧 CLI 0.23.1 的正式命令命中已下线 multipart 路由并返回 `No matching routes found`；随后的只读 history 与精确版本查询确认1.6.17未落库。官方最新 CLI 0.23.3 已改用逐文件预签名上传和 JSON 提交；其 source-bound dry-run 仍为33文件、同一 slug/展示名与 fingerprint。
- 0.23.3 正式提交一次获受理：`status=pending-publication`、`publicationStatus=pending`、`versionId=k97ehqyj43qb11255dkc20hx598d7smk`、`attemptId=zx7dbhs5vjvbb28qcmhx2dfbe18d609t`、`fileCount=33`、平台 fingerprint `811cd3dac093d8639adbfd9ad84a1844f4710730c695194ba65e64c1900d5a30`。首次只读精确版本查询仍为 `Version not found`，与先扫描后公开的 pending 回执一致；期间未重复提交。
- 后续 `latestVersion`、`tags.latest` 和精确版本均已传播为1.6.17。精确版本33文件与正式上传目录比较：缺失0、额外0、SHA-256不一致0、Hook路径0。
- aggregate moderation 与版本 security 均为 `clean`；VT为clean，Skillspector为clean/LOW，LLM为clean、`benign/high`。平台仍返回 `hasWarnings=true`，不把各扫描 clean 外推为该布尔字段已消失；安全包 SHA-256 为 `9a57ef863002f797f66a0af1bfb572dadcde9b9715754d857a92cd171f44cde4`。

## 剩余边界

- GitHub、SkillHub.cn 与 ClawHub 公开版本均已到1.6.17；ClawHub 精确33文件和扫描状态已闭环，期间未重复提交。
- SkillHub.cn 的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 仍为 `pending`；ClawHub 虽各扫描为clean，平台 `hasWarnings` 仍为true，二者都不改写为无条件审核完成。
- Hook 默认关闭并按单能力窄启用；ClawHub 包完全不含 Hook。
- 付费提纲和红头 DOCX 能力继续只在独立分支管理，不发布、不反向合入公开 `main`。
