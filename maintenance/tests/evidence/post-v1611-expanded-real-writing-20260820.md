# v1.6.11 后扩大真实写稿与竞品原子复核

日期：2026-08-20。基线：本地 `main@aeccc49e`。范围：description 既有 HOLD 的扩大 A/B、会议纪要争议来源原子、联网来源用途分型与有限补搜原子，以及公开变更同步付费候选。未推送、未移动 tag、未上传或发布。

## 已准入内容的合并与付费同步

- `codex/v1612-research-closeout` 的三个已验证提交已以 `aeccc49e` 合入本地 main；description 为204字，较280字原始入口减少76字（27.1%）。合并后定向测试108/108、canonical quick validate 和 `git diff --check` 通过。
- main 的普通 Skill 语义随后按 `public-paid-sync.md` 合入 `codex/paid-outline-review@8274d2c4`。main 已成为付费分支祖先；公开 main 的 `outline_assist` 文件数为0，付费分支保留10个提纲能力文件及批准的说明、规格、测试和组装器差异。付费定向测试94/94、quick validate 和 diff check 通过。没有发布付费包。

## MT-005b2/b3/b4 扩大真实 A/B

环境：WorkBuddy 5.3.13 内置 CodeBuddy CLI 2.115.0、`deepseek-v4-flash`、max、`bypassPermissions`。每个候选只改一个 description 原子；每个原子2个正式正向题、1个相邻边界题，基线/候选各1次，共18次有效写稿。首次新 cwd 的信任提示为技术无效，不计入矩阵。

| 原子 | 扩大题目 | 结果 | 停止原因 |
| --- | --- | --- | --- |
| `MT-005b2` 只删“规定” | 两个制度正向题＋相邻边界 | HOLD | 候选新增“规范实验室工作人员的安全行为”，并把“本校实验室工作人员”扩大为“本校实验室及其工作人员” |
| `MT-005b3` “函、复函→函件” | 商请函、复函、私人回信 | HOLD | 两个正式正向题均可直接使用；私人回信两边均未调用 Skill，但候选独有地补入用户未给的“2026年8月20日” |
| `MT-005b4` “讲话、致辞→讲话致辞” | 防汛讲话、签约致辞、私人边界 | HOLD | 防汛稿新增关键时期、人员在岗、责任到人和生命财产安全等责任/效果；签约致辞停在追问，未交付正文 |

原始结果与全部 terminal hash：`F:\Workspaces\chinese-official-writing-skill\output\current-verification\v1.6.12-mt005-expanded\result.md`、`F:\Workspaces\chinese-official-writing-skill\output\current-verification\v1.6.12-mt005-expanded\all-terminal-sha256.json`。函件六份 terminal SHA-256：商请函基线/候选 `6bb17fe1…` / `31687fca…`，复函 `3facb582…` / `475f134c…`，私人边界 `b63b3d6c…` / `b542c385…`。

结论：扩大范围没有推翻既有 HOLD。不得用两个函件正向题的局部通过覆盖相邻边界硬回退，也不为随机成功重跑相同题。

## 会议纪要：竞品方法有价值，但当前 main 已自然覆盖

`meeting-minutes-drafter` 提供“分歧时保留选项及来源”的抽象方法。本地下载包 `_skillhub_meta.json`/`_meta.json` 标为1.0.3，而本轮 API 可见元数据曾显示1.6.0；两者只记为不同时间/表面，不合并成同一确定版本。包内未发现独立 LICENSE，只借鉴方法，不复制文字、结构标记、模板或代码。

候选只增加同一语义规则：材料明确给出不同主体的互斥主张且未表决时，保持主体—主张绑定和未决状态，不合并为共识、折中方案、议定事项或决定。WorkBuddy / CodeBuddy 完成三组 A/B：

1. 轻量未决纪要：办公室一次切换、信息中心2个系统试运行、档案室先做历史映射；基线和候选均完整保留三方来源及未决状态。
2. 已决＋未决混合纪要：两项责任期限和两种扫描主张；基线和候选均完整、未折中、未选边。
3. 无分歧边界：两边均保留既定责任与期限，未反向生成争议结构。

六份 terminal SHA-256：`0b35b6fe…` / `9fd4d4db…`、`b4f92ef7…` / `b913d4da…`、`9a5e6d92…` / `2c2b739a…`。

结论：基线3/3已经实现目标，候选没有可复现的目标改善；不向 `task-route-cards.md` 或 `genre-playbook-minutes.md` 叠加重复规则。竞品原子状态由“待原型”改为“已被当前结果覆盖”。

## 联网来源分型与停止：方向成立，当前候选 HOLD

竞品 `dknowc-official-doc-writer` 相对当前 Skill 的可借鉴点是：联网获准后区分来源用途、把来源单独登记、冲突保留并设置停止条件。历史 SkillHub 快照为3.4.2/60文件，公开 GitHub/skills.sh 表面曾显示3.3.1；不混写版本，不复制其实现、模板或外部服务配置。

候选只在 `external-research.md` 增加四类用途：规范依据、地方执行口径、事件/新闻事实、数据/统计数字；并规定每类一项主来源、一项交叉来源，只有直接冲突再补搜一次。真实题联网核验国家《政务数据共享条例》、上海地方制度、浙江比较制度和上海“一网通办”进展。

首个交互 PTY 基线把工具回执误当最终回答，记为无效样本；修为 CodeBuddy `--print --output-format json` 后得到完整 A/B：

| 指标 | main 基线 | 候选 |
| --- | ---: | ---: |
| CodeBuddy `num_turns` | 84 | 46 |
| `WebSearch` | 12 | 11 |
| `WebFetch` | 2 | 3 |
| 完整终稿 | 有 | 有 |

两稿都区分国家、本市、外地比较和新闻进展，也都保留不同时点数字。候选没有证明稳定停止：仍有11次搜索，仅比基线少1次；来源清单把 `zjwx.gov.cn` 写成浙江省政府门户，但独立检索找到的官方原文位于浙江省商务厅/政府域和省级政务云附件，未支持该来源身份；候选还在完整交付前增加“核验完成。以下为完整交付文本。”和 Markdown 横线，构成直接使用范围回退。

基线/候选 JSON SHA-256：`ead6d5e7…` / `e6e3b398…`。原始流位于 `F:\Workspaces\chinese-official-writing-skill\output\current-verification\v1.6.12-source-typing\`。

结论：来源用途分型值得继续，优先级高于 Hook；当前“分型＋停止”组合候选 HOLD，不改产品。下一轮应再拆：先只验证来源用途和原始权威页身份，后单独验证查询停止，避免把两个变化混在一起。

## 实际命令与来源

```powershell
git merge --no-ff codex/v1612-research-closeout ...
python -B -m unittest maintenance.tests.test_description_news_trigger maintenance.tests.test_skill_boundary maintenance.tests.test_repository_reachability maintenance.tests.test_hook_layer_contract maintenance.tests.test_complexity_contract maintenance.tests.test_skillhub_package_builder maintenance.tests.test_claude_gate_adapter
python -B maintenance/tools/assemble_hook_companion.py --host codebuddy --output <ignored-output>
python -B output/current-verification/v1.6.11-description-load/run_codebuddy_once.py ...
node <WorkBuddy CodeBuddy CLI> --plugin-dir <candidate> --print --output-format json ...
git merge --no-ff main ...  # 在 paid worktree
python -B -m unittest maintenance.tests.test_description_news_trigger maintenance.tests.test_skill_boundary maintenance.tests.test_hook_layer_contract maintenance.tests.test_outline_hook_companion
git merge-base --is-ancestor main HEAD
git diff --name-only main...HEAD
```

外部方法与宿主规范：dknowc 官方仓库、Claude Code Hooks、Codex Hooks、CodeBuddy Hooks、WorkBuddy 插件系统。浙江制度原文以浙江省政府部门页和省级政务云附件交叉核验；搜索结果页或未打开转载不冒充有效原文。
