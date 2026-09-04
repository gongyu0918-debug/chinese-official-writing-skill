# v1.6.27 候选与验证记录

日期：2026-09-05。状态：`PUBLISHED / SEE release-1.6.27.md`。本记录首次冻结时已合入本地main、尚未正式上传；后续发布与异步传播事实见[发布记录](release-1.6.27.md)，不改变本候选产品字节。

## 固定产品与范围

- 产品提交 `0a83ecbf3be21815e72a80593f612eb858613be5`，annotated tag `v1.6.27`，tag object `8a45b6af8c835f7ad70caf1df532873717f6f84f`。本记录在产品tag之后提交，不改变产品字节。
- 上一发布 `v1.6.26^{commit}=41a477b852062ad9fb66c80a791633cb29ab71f6` 是祖先。发行开发使用独立 `codex/release-v1.6.27` worktree，基于本轮开始时main `5fbb2d26`，经已准入审计分支 `92142f64` 和新叶选择 `b4afd7e8` 整合；最终全量通过后才将main快进到产品提交。
- 对上一tag共374个变更路径：整改方案专叶与路由、带引号的校对绝对路径、投诉页68-byte删例、八个adapter及兼容包版本，以及开发纪律/规格/验证证据。八个adapter仅版本变化，其余38个Hook blob及core/shared/capabilities子树完全一致；两个canonical脚本未变。付费提纲、红头、Pro和示例未改。
- 两次独立范围审查经主代理复核均无阻断；新增证据未发现明显令牌、JWT、私钥、凭据URL或私网IP。失败原型仅作为维护证据，不进入运行时包。

## 真实结果与工程验证

- 整改方案复用已合入当前main的[WR-028 R2真稿](remediation-plan-r1/candidate-r2-result.md)；命令路径使用[两份真实通知、四次原生执行](command-cwd-real-draft-r1/result.md)的证据，不冒充模型自主Shell A/B。
- 新叶清理用两条原有低价路线完成8次独立真实调用，技术有效8/8；只选择投诉页68-byte删例，定向审稿36-byte删除出现候选独有处理过程，已恢复原文。共同误报与热线联系方向歧义照实保留。[逐稿结果](recent-leaf-cleanup-r1/result.md)
- 新叶5项直接测试、canonical quick validate、60个原始文件及Git blob hash、490个本地链接通过；发行前canonical、Agent Skills、Qwen Code、QwenWork、Hermes五套quick validate通过。OpenClaw的category扩展由仓库契约覆盖，不声称通用validator通过。
- 首轮全量实际运行774项，105.059秒，两处旧措辞断言失败：AGENTS控制面测试仍绑定压缩前原句，P098仍要求已替换的相对命令。仅把断言对应到相同纪律、引号绝对路径及“exit 0只表示扫描完成”，未放松实际约束；两目标项通过（0.143秒）。最终全量 **774/774通过，102.473秒**。首跑日志和最终日志均保留。

```text
python -X utf8 -B -m unittest discover -s maintenance/tests -p "test_*.py"
python -X utf8 -B -m unittest maintenance.tests.test_agents_control_plane.AgentsControlPlaneTests.test_root_agents_is_small_engineering_only_control_plane maintenance.tests.test_real_prompt_ablation.RealPromptAblationTests.test_current_skill_passes_real_prompt_cases
python -X utf8 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py <上述各Skill目录>
python -X utf8 -B maintenance/tools/sync_adapters.py
git diff --check
```

实际解释器为本机Python313（含现有PyYAML）。同步前逐项核准五个绝对目标均在发行树packages内且无外来文件或符号链接，复跑幂等；同步通过调用既有模块main完成，与所列CLI使用同一入口。排除evidence/archive/output/platform-snapshots后的93个受控Python和19个JSON解析通过，`git diff --check`通过。首次复用SkillHub CLI的ZIP函数因未加入其目录而缺少skills_upgrade模块；补齐CLI目录后成功打包，未涉及平台提交。

## 冻结包与平台预检

- SkillHub.cn为86文件含Hook包，使用LICENSE.md、排除agents/openai.yaml及无扩展名LICENSE。ClawHub为37文件无Hook包；两者相对上一版均新增整改方案页。
- 本地逐文件原始与LF规范化hash及明确算法见[包manifest](release-v1627/package-manifest.json)。SkillHub原始树fingerprint `51a4f7ae46b579930ae75e21fb67f40f488cbf04b751f204f08353213fcff29a`，LF树 `4953fc49a962bb4138147c8ef00daa26b77c054806417af06a87304c65ae73e8`；ClawHub原始树 `b0c7bf00c2e9b792c2d6cbf3cbd775ce25459d77ac7042e2bf9d9d3fce6aad61`，LF树 `aee0518fee8dee84e693540e561d6ed8f5aa4ea48d5e5a3bdfbda4f85e7297d8`。本地算法与平台fingerprint分别记录，不互相冒充。
- SkillHub ZIP SHA-256 `94cec25e2042a347cd017fcccc93091667696b192b5568a4da3ef462b3ac1c3f`，CLI content hash（排除_meta）`cea9f4c16594b277d2a9b019a5eaab1f243b3e45244b86dce97001e20a6e17ab`。86个ZIP成员逐项等于冻结目录字节。
- SkillHub dry-run返回 `dryRun=true`、1.6.27；ClawHub返回 `would-publish`、37文件、展示名“中文公文写作”、1.6.27，平台dry-run fingerprint为 `6ed68c7cb787ecca3085349af0b2225bcf7e398b4af17b156358345cc16f30fe`。这只是预检，不是上传或审核证明。
- [冻结调用参数](release-v1627/publish-commands.json)绑定产品SHA/tag，正式提交只移除dry-run。SkillHub坐标维持 `@user_f3d82da7/chinese-official-writing`；ClawHub owner维持gongyu0918-debug，四个topics保留，只移动latest，不提供已过时的categories覆盖。

## 发布及剩余边界

用户已授权GitHub、SkillHub.cn和ClawHub发行。每个平台只正式提交一次，成功回执后仅只读核验传播与审核，不因pending或平台生成文件重复提交。正式回执另记。

本版未修复此前登记的Hook日期示例错绑、错回显耗尽放行、终态重放、晚到事件覆盖，也未证明所有写稿/多版修改普遍可靠。保留[质量审计与后续问题](reference-route-audit-r1/result.md)，不把774项确定性测试当成稿件可靠率。
