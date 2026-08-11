# 1.5.36 发布证据

## 范围

1.5.36 以 `v1.5.35=d357c9fb340120c067c1e9efb8d4404c0a9d70e6` 为固定发布基线，只发布一项写作规则减负：将 `workflow.md`“素材映射与事实边界”中的重复否定清单归并为一条正向事实源规则，并继续转读 `information-selection.md` 和已命中的轻量任务卡。相对 1.5.35，canonical `workflow.md` 净减少 363 个规范化字符。

本版不改变文种路由、reference 加载条件、篇幅规则、输出模式、复核顺序、修改次数、回退方式和发布链。产品提交为 `b25d704d3da8e12b37f5c9a6939f44fabc2b2415`；版本面提交为 `16442205796492414da321f4140b145bb1c62c06`。

本地 `main` 原先还包含一组只达到 `KEEP ISOLATED` 的 lint/anti-AI 研究改动。发布范围收口提交 `a3a20f8e` 已把这些产品和测试改动恢复为 1.5.35 行为；研究记录仍保留在 Git 历史和 `tests/evidence/`，不随本版产品生效。

## 真实写稿证据

历史正确路由的同机制 A/B 为 Candidate 5 胜、Baseline 1 胜。唯一负项为一次篇幅下偏，未形成三个正常场景重复的共性风险；完整历史与当前主线复验见 `workflow-info-dedup-v1536-r2-result-20260804.md`。

发布前另用“校园维修工单办理情况报告”对固定 1.5.35 和版本面提交 `16442205` 做一次清洁复验。两臂使用同一原始任务哈希 `67f3c4f8d08bbafe074c7ee64bf08b97be6aab901acbae7c15fc46fea3573cfb`，均为一次首稿、零次修订，正文分别为 470 和 545 个非空白字符；事实、数字、日期、主体、状态、报告文种、四个指定小节、输出范围和 450—550 字要求全部成立，匿名评审均判 G1，未见功能性硬回退。

该复验不计比较胜负：1.5.35 写手实际读取 6 个文件，未读取 `workflow.md`、`handling-elements.md` 和 `argument-chains.md`；1.5.36 写手读取 9 个文件。匿名评审虽然判 1.5.35 稿小胜，但运行条件不能支持因果归因。本轮按预注册纪律不补抽、不换题，不把无效比较包装为 Candidate 失败或通过。

## 发布前门禁

- `python -m unittest discover -s tests`：442/442，`OK`；
- `$env:OFFICIAL_WRITING_EVAL_STUB='1'; npm run eval:official-writing:smoke`：20/20，0 failed，0 errors，judge consistency 1.0，eval id `eval-QlK-2026-08-05T02:29:10`；
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.35> --baseline-label v1.5.35 --current-root . --out output/release-1.5.36-ablation`：固定 1.5.35 为 111/111，Candidate 为 111/111；
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`；
- `python tools/sync_adapters.py`：canonical 与五套发行镜像同步，重复运行后工作树无新增差异；
- `python -m py_compile chinese-official-writing\scripts\prose_lint.py`：通过；
- `git diff --check`：通过。

## 发行包

### ClawHub

- 发行目录：`openclaw/skills/chinese_official_writing/`；
- 文件数：32；
- dry-run：`status=would-publish`，公开基线 1.5.35，目标版本 1.5.36；
- fingerprint：`52c36b80d263087515c13c72bb0f460e795ea0b6bb0324daba3cab64553f430c`。

### skillhub.cn

- 清洁包：`output/skillhub-release-1.5.36/publish-package/`；
- 文件数：31，禁入文件 0，共享内容哈希不一致 0；
- 排除 `agents/openai.yaml`、`delivery-review-gate.md`、`gate_stop_hook.py`、`review_gate.py`，加入平台 `_meta.json` 和 SkillHub 专用 frontmatter；
- 排序清单 SHA-256：`7e7935dc6399b073cba42fd8b9c1012cbac80138f1ffdd1860a775afd079dc69`；
- dry-run：精确返回 `chinese-official-writing@1.5.36`。

## 剩余风险

- workflow 去重的历史样本有一次篇幅下偏，继续作为观察项，不在本版追加展开规则；
- 发布前清洁复验因实际读取文件不对称，只能证明两臂均无硬回退，不能提供严格因果胜负；
- 被撤出的 lint/anti-AI 组合仍在研究记录中，后续须以对称运行条件重新验证后才能发布；
- 本版没有重新生成 true No-Skill 稿，质量结论限于相对 1.5.35 的规则减负和既有历史 A/B。

## 实际发布与回执

- GitHub：`origin/main`、annotated tag `v1.5.36` 的解引用提交和正式 Release 均为 `8bd4eb8c8b4f233445e07ebf4d3f54ceb5777aa2`；tag object 为 `b0655f0c163eff92f58e69670b1725b63a232eee`。Release 已公开：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.36`。
- ClawHub：正式提交只执行一次，回执为 `status=published`、`versionId=k97emf7mhg4adgdbastvnnj3y58bwhak`、32 个文件、fingerprint `52c36b80d263087515c13c72bb0f460e795ea0b6bb0324daba3cab64553f430c`。随后只读查询已显示公开 `latestVersion=1.5.36`，moderation 为 `clean`；本次字段展开没有稳定返回 tags 和统计对象，不作推断。
- skillhub.cn：正式提交只执行一次，回执为 `ok=true`、`skillId=70149`、`versionId=197616`、31 个文件、fingerprint `2dd2505f454335ee85d3934e8f8fd820f4b552102feca9b3edbbe6b3a67096c1`、`tags.latest=1.5.36`；提交回执中的 review、security scan 和 content audit 均为 `pending`。随后只读查询仍显示 `latestVersion=1.5.35`，属于公开详情传播延迟，不重复提交。
- 小红书 Red SkillHub 未调用。
