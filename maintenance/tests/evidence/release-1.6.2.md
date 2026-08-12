# v1.6.2 发布记录

## 发布范围

- 本版发布 GitHub `main`、annotated tag `v1.6.2`、GitHub Release 和 SkillHub.cn `1.6.2`。
- 仓库及当前兼容包继续采用根 `LICENSE` 的 MIT 许可。
- ClawHub、小红书 Red SkillHub及其他平台不在本次授权范围内。
- 篇幅补写 Hook 未进入本版。

## 主要变化

- 将普通 Skill、共享 Hook 核心和 Codex、Claude Code、WorkBuddy/CodeBuddy 静态适配源分层组织；不再在 canonical 根混放宿主 manifest 和重复 Skill shim。
- 三套宿主 companion 由维护期组装器生成自包含包，运行时不动态识别宿主、不自动生成或安装文件、不修改配置、不联网。
- Hook 默认关闭。用户明确启用后才进入交付门禁；当前任务说“本次关闭 Hook”“本次不要用 Hook”或“跳过交付门禁”时，不创建门禁事务、不阻断终稿。
- 普通 Skill 和无 Hook 平台镜像继续依靠 SKILL、references 与可选 `prose_lint.py` 独立闭环。
- `hooks/README.md` 说明功能、启用与关闭、数据边界、优缺点和宿主差异，Agent 无需遍历实现代码即可解释。
- 修复显式删除来源中否定结论时的门禁识别边界；不改变“请保留”“不要删除”的只读保护。
- 新闻、新闻评论等写作能力继续保留在核心能力与路由中；GitHub OpenClaw 兼容包同步为 1.6.2、MIT、无 Hook。

## 发布前验证

- 全量 unittest：550/550 PASS。
- Promptfoo stub smoke：20/20 PASS，最终复跑为 `eval-0l0-2026-08-12T09:38:24`。
- 固定 v1.6.1 确定性消融：v1.6.1 为 111/111，v1.6.2 为 111/111。
- 真实写稿：3 个 provider、9 对、18 次全部技术有效，0 timeout、0 retry；9 个 Hook-on 臂均完成事件链并安全回退 D0，D1=0。
- canonical quick validate、Codex companion validator、Claude strict validator与无模型 preflight、WorkBuddy/CodeBuddy validator：PASS。
- 普通镜像同步两次幂等；SkillHub 清洁包、许可证、禁入文件、companion 自包含性、Markdown 链接、父目录回指、复杂度与孤儿文件契约均通过。
- `git diff --check` 与高置信凭据扫描：PASS。

## 已知边界

- SOL 匿名复核解盲后为 Hook enabled 3 胜、disabled 5 胜、难分 1，并在两个制度样本中重复判 enabled 独有状态硬失败，因此预注册质量结论仍为 `HOLD`。两处均来自未被 Hook 改写的 D0，不能证明由 Hook 造成。
- 本版只证明静态结构、显式开关、真实事件链与安全回退可用，不宣称 Hook 改善稿件质量、识别全部初稿问题或提供自动补字。
- 产品所有者在获知完整结果后明确授权发布；原始裁决与无效裁判记录不改写。

## 外部回执

- GitHub 产品发布提交：`7d794b10f7acd320c90c2d311af9466fca732cfe`。
- annotated tag object：`8fffac05d3f595884cf22b5e8269392a37e5fc4e`；`v1.6.2^{commit}` 与产品发布提交一致。
- GitHub 远端 `main` 与 tag 已回读；GitHub Release：[`v1.6.2`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.2)，`draft=false`、`prerelease=false`，发布时间 `2026-08-12T09:49:40Z`。
- SkillHub 正式上传只执行一次。回执：`ok=true`、skillId `70149`、versionId `231440`、48 文件、fingerprint `78ff1b8ad6a61b9d48f86f06c400fdbae78c8218115850902c2bd6700187ef68`，全部业务 tag 含 `latest` 均指向 `1.6.2`。
- SkillHub 更新说明逐字为：“重整 Hook 架构与静态兼容层，补充启用、关闭和任务级旁路说明，修复否定结论删除边界，完善新闻与新闻评论支持；普通 Skill 保持无 Hook 独立运行。”
- 正式回执中的 review、security scan 和 content audit 均为 `pending`。发布后公开详情的 tags 已为 `1.6.2`，但 `latestVersion.version` 仍为 `1.6.1`，精确版本签名端点返回 404；记录为平台异步传播 pending，不重复上传。
- ClawHub、小红书 Red SkillHub及其他平台未执行上传。

本节作为发布后证据提交推进 `main`，不移动 `v1.6.2` tag。
