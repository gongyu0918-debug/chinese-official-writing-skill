# 1.5.35 发布前证据

## 范围

1.5.35 以 `v1.5.34=e85dc6a66fa300e8136eedf26af4534d2715d2fb` 为固定发布
基线，只纳入已经完成隔离真实写稿验证和组合回归的两项修改：

- 方案、实施方案、建设方案叶以目标、主要任务和实施路径为主线，责任、进度、
  保障、验收和风险控制按材料及用户模板落位；
- 权威文种路由补齐新闻消息、新闻评论定义，评测 provider 的只审新闻任务加载
  既有命中叶。

功能准备提交为 `5d343c5c080b0cf14ad6fe5698bcfee793721fb6`，发布元数据收口后的
最终发布提交为 `d357c9fb340120c067c1e9efb8d4404c0a9d70e6`。本版没有修改
事实边界、篇幅规则、复核顺序、脚本检测规则、自动改稿次数、回退方式或发布链；
没有恢复述职专叶、叶内说明压缩或 Candidate H。

## 被排除的实现

- 方案 R1 固定七要素顺序在两题中均出现任务、进度、保障或验收复述，盲审两题
  均由 1.5.34 胜出，产品提交 `330f723c` 未合入；
- 新闻 R1 将“起草／成稿复核”段放入起草可见上下文，有效样本出现整组事实
  复述，产品提交 `bf825083` 未合入。

## 真实写稿与盲审

方案 R2 使用两道自然任务，复用逐字一致原始任务和固定 1.5.34 基线稿，Candidate
各取首个技术有效输出，writer 与匿名盲审分离：

- 窗口服务实施方案：Candidate 胜，990 字，减少步骤、任务和验收三次复述；
- 统一认证建设方案：Candidate 小胜，1044 字；保留两处轻微阶段衔接套话观察项。

新闻 R2 使用未直接点名文种的门户会议公开稿任务。Candidate 判为新闻消息，明确
事项作为已发生事实报道，未转成纪要责任清单或通知办理要求；Candidate 586 个
非空白字符，固定 1.5.34 为 420 个，匿名盲审判 Candidate 胜。Candidate 距“约
600—800 字”下限 14 字，并有轻度任务链重复，继续作为观察项。

上述稿件未见事实、数字、日期、主体、状态、文种或输出范围硬回退。完整记录见
`tests/evidence/plan-news-routing-integration-20260803.md`；本轮没有重新生成 true
No-Skill 稿，结论限于相对固定 1.5.34 的冲突修正和功能覆盖。

## 发布前门禁

- `python -m unittest discover -s tests`：442/442，`OK`；
- `$env:OFFICIAL_WRITING_EVAL_STUB='1'; npm run eval:official-writing:smoke`：
  20/20，0 failed，0 errors，judge consistency 1.0，eval id
  `eval-f7V-2026-08-03T12:20:08`；
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.34> --baseline-label
  v1.5.34 --current-root . --out output/release-1.5.35-ablation`：固定 v1.5.34
  111/111、Candidate 111/111；
- Hermes Python 运行 `quick_validate.py chinese-official-writing`：
  `Skill is valid!`；
- `python tools/sync_adapters.py`：canonical 与五套 Agent 镜像完成同步；
- `git diff --check`：通过。

首次全量 unittest 发现 README 已更新为 442/442，但断言仍锁定旧的 440/440，
同时 README 版本徽章仍为 1.5.34。两处均属于发布元数据，修正后全量 442/442
通过；没有借此修改写作规则或测试口径。

## 发行包

### ClawHub

- 发行目录：`openclaw/skills/chinese_official_writing/`；
- 文件数：32；
- 禁入文件、缓存和 `.pyc`：0；
- dry-run：`status=would-publish`、公开基线 1.5.34、目标版本 1.5.35；
- fingerprint：`f7aace001f59308fa0f2db737b4449a81a1e22a63350513d6fda645985194a25`。

正式发布必须使用冻结发布提交作为 `source-commit`，并将 tags 参数作为单个 token
传入。dry-run 未上传任何文件。

### skillhub.cn

- 清洁包：`output/skillhub-release-1.5.35/publish-package/`；
- 文件数：31；
- 排除 `agents/openai.yaml`、`delivery-review-gate.md`、`gate_stop_hook.py`、
  `review_gate.py`，加入平台 `_meta.json`；
- 29 个共享内容文件与 canonical 逐文件 SHA-256 一致，平台 `SKILL.md` 正文与
  canonical 一致；
- 排序清单 SHA-256：
  `56859cebb153adef3379bd23a552266e55c694c19c42d3cfd6d38b520bc78655`；
- dry-run 精确返回 `chinese-official-writing@1.5.35`。

首次复制当前 references 时把 `delivery-review-gate.md` 带入临时包。清洁包审计在
任何 dry-run 或上传前检出并移除；复核后缺失 0、额外 0、哈希不一致 0、禁入文件
0。失败包没有进入发布证据或平台调用。

## 一次性定时发布边界

本地发布提交和 annotated tag `v1.5.35` 在全部门禁通过后冻结。一次性任务安排在
2026-08-04 09:00（Asia/Shanghai），只执行以下发布动作：

1. 核验本地 `main`、tag 解引用提交、版本面、两个冻结包的文件数和哈希均与任务
   中登记值一致；
2. 推送固定 `main` 与既有本地 tag，创建 GitHub Release；
3. ClawHub 正式提交一次；
4. skillhub.cn 正式提交一次；
5. 记录各平台接受回执与首次公开状态，区分提交成功、公开 latest 和审核状态。

定时任务不修改产品、不重新生成稿件、不重建或移动 tag、不在失败后换包补投。
只有明确的建连前环境错误可在清空失效代理后按相同命令重试一次；平台已返回接受
回执后，即使索引、moderation 或审核滞后，也不重复提交。小红书 Red SkillHub 不在
范围内。

## 剩余风险

- 方案 P02 仍有轻微阶段衔接套话，未在三个正常场景形成共性，不追加规则；
- 新闻歧义样稿略低于约定下限且有轻度任务链复述，后续新闻样本继续观察；
- 新闻只审覆盖的确定性 provider 路由已经验证，本轮没有扩成跨模型只审语言矩阵；
- 述职专叶、叶内说明压缩和 Candidate H 只在独立研究 worktree 继续验证，不进入
  1.5.35。

## 实际发布与回执

2026-08-04 09:01（Asia/Shanghai），一次性定时任务按计划启动，但在发布前不变量
核验处停止。失败原因不是 tag 错误，而是 PowerShell 对未加引号的
`v1.5.35^{commit}` 发生了错误解析，误把 tag 解引用结果判为父提交
`5d343c5c080b0cf14ad6fe5698bcfee793721fb6`。随后使用带引号的
`git rev-parse 'v1.5.35^{commit}'` 和 tag object 交叉核验，确认 annotated tag object
为 `08318703a2a4d74461384c1123f65c900f5692c5`，解引用提交始终为冻结发布提交
`d357c9fb340120c067c1e9efb8d4404c0a9d70e6`。定时任务停止前没有执行任何平台提交。

修正核验方式后，按冻结包和既有 tag 完成一次正式发布：

- GitHub：`origin/main`、远端 `v1.5.35` 解引用提交均为
  `d357c9fb340120c067c1e9efb8d4404c0a9d70e6`；Release 为非草稿、非预发布，
  `publishedAt=2026-08-04T01:22:47Z`，地址为
  `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.35`。
- ClawHub：正式回执 `status=published`、`version=1.5.35`、
  `versionId=k976rg5tady45fbwd965z7gwjx8bt2wf`、32 个文件、fingerprint
  `f7aace001f59308fa0f2db737b4449a81a1e22a63350513d6fda645985194a25`。
  随后的公开查询已显示 `latestVersion=1.5.35`、`tags.latest=1.5.35`，moderation
  为 `clean`。
- skillhub.cn：正式回执 `ok=true`、`skillId=70149`、`versionId=192938`、31 个
  文件、fingerprint
  `faad8e3d353e8f42f1a1f8d028b658f4d42a38fbc8c61789062ceab026d89825`，
  `tags.latest=1.5.35`；首次回执的 review、security scan 和 content audit 均为
  `pending`。首次公开详情查询仍显示 `latestVersion=1.5.34`，但 skill 级
  `tags.latest=1.5.35`，属于审核与详情页传播尚未收敛，不重复提交。

小红书 Red SkillHub 继续不在本次发布范围内，未调用其上传或更新工具。
