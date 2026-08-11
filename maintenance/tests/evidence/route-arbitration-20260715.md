# 渐进式路由最小仲裁修复证据

日期：2026-07-15
固定上一发行基线：`v1.5.13` / `cd2d46c58a5f56b9009c5da08626a88640f2e5b3`

## 修改边界

用户明确同意按最小方案处理，并要求出现任何事实、文种、格式或输出模式回退即撤回。本轮只处理轻量任务卡与文种 playbook 的主叶仲裁，不改事实边界、文种规则、三级复核顺序、输出模式定义、修改轮次、默认联网和发布链；不提升版本，不发布。

修改前可稳定复现：

- `SKILL.md` 和任务卡声明卡片覆盖时可结束 reference 路由；
- `task-route-cards.md` 又把所有会议纪要列入必须转读长 reference；
- 评测 provider 因此对未形成决定、责任和期限的纪要同时加载任务卡与 `genre-playbooks.md`。

## 最小修复

1. `SKILL.md` 先定创作、修改、只审不改等输出模式，再做主叶仲裁；四类轻量卡完整覆盖时终止，已知文种需要常规或完整骨架时直接进入对应 playbook 叶子。
2. `task-route-cards.md` 将纪要升级条件收束为：已经形成决定、议定事项、结论或一致意见、责任分工或期限，或者用户要求完整正式会议纪要。未决建议、待评估、听取结果和下次再议仍由轻量卡处理。
3. provider 删除未决纪要的临时双加载，使用纪要专用仲裁。首个候选因使用裸关键词，实测把五类未决表述误进 playbook、把“简短但完整正式会议纪要”误停轻量卡，未予保留；后续候选又在独立对抗复核中暴露 high：整段清除否定/未决分句会吞掉同句后半的“但已明确责任单位”或完整正式请求，导致已决纪要误停轻量卡，该候选同样未予保留。最终规则只屏蔽明确的未决短语，不删除整个分句；完整正式请求和屏蔽后仍存在的决定、议定、结论、共识、责任、期限证据优先升级。仅写“简短”“不新增事实”、只说明材料未提供某字段，或词序无法确定时，默认进入 playbook。
4. canonical 变更通过 `tools/sync_adapters.py` 同步到 `skills/`、`.agents/`、`.qwen/`、Hermes 和 OpenClaw 镜像；未修改 `genre-playbooks.md` 或 Red 历史归档。

## 确定性验证

- `python -B -m unittest discover -s tests -v`：174/174 通过。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.13-cold-audit --baseline-label baseline-1.5.13 --current-root . --out output/route-arbitration-vs-1.5.13`：baseline 108/108，current 108/108。
- `npm run eval:official-writing:smoke`：最终在允许 Node 启动 Python 子进程后 20/20 通过，0 error；前两次沙箱内运行均因 Promptfoo 无法启动本机 Python 而得到 20 error，样例没有执行，未计为产品结果。
- `python -B tools/run_real_article_eval.py --out output/route-arbitration-real-article`：退出码 0；该工具为确定性样文回归，不替代真实写稿。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check`：通过。

新增 provider 边界用例覆盖：

- 未决轻卡：`议定事项尚未形成`、`责任单位待明确`、`无议定事项`、`不要写会议决定`、`已形成初步建议，仍待评估`、`目前只有建议，事项待评估`、`会议明确提出建议，待进一步评估`、`会议确定下次再议`；
- 完整 playbook：`简短但完整正式会议纪要`、`完整、正式的会议纪要`、已决定/无异议通过事项、已明确责任单位/责任分工/完成期限，以及“会上形成决定”“经研究决定”“明确由某单位负责”等常见词序；
- 混合状态优先升级：同句含“未形成决定/建议继续研究”，但后续已经明确责任、期限、决定，或者明确要求完整正式纪要时，均进入 playbook；已形成结论、达成一致意见或共识而其余要素待定时也进入 playbook；
- 保守回退：只有“简短会议纪要”、材料“未说明是否形成决定”或“未提供责任单位和期限”时进入 playbook，不把信息缺失误判成事项未决；
- 断言均精确区分 `[SKILL.md, task-route-cards.md]` 与 `[SKILL.md, genre-playbooks.md]`。

## 真实写稿 A/B

原始提示、成稿、路由自报和盲审分别见：

- `route-arbitration-20260715/prompts.md`
- `route-arbitration-20260715/writer-c.md`
- `route-arbitration-20260715/writer-d.md`
- `route-arbitration-20260715/verifier-blind.md`
- `route-arbitration-20260715/mapping.md`

四个任务覆盖未决纪要、已决完整纪要、材料稀疏情况说明和二次局部改稿。两名 writer 分别按相反 A/B 映射生成，共 16 份成稿；独立 verifier 在不知道版本映射时判定：

- 内容 16/16 PASS，0 WARN，0 FAIL；
- 未发现任何一侧独有的事实、文种、格式或输出模式问题；
- 路由 14/16 适配，两份 over-read 均为未决纪要多读 playbook。

揭盲后，两份 over-read 均属于固定 `v1.5.13` 基线；current 8 份成稿内容全部 PASS，current 的 R1 均只读任务卡，R2 均只读 playbook，R3/R4 均只读任务卡。未触发撤回条件。

## 结论与限制

本轮接受最小修复：已消除可复现的未决纪要双加载，且最终独立对抗复核为 0 blocker、0 high；中途发现的同句否定范围 high 已在提交前关闭。未观察到事实、文种、格式或输出模式回退。仍保留 low 级保守 over-read：`仅作初步讨论、尚需进一步论证`、`暂不作决定`，以及带量词和顿号的`不需要一份完整、正式的会议纪要`等表达会进入 playbook。该 over-read 不改变正文边界，`genre-playbooks.md` 仍要求未给结论时保持待确认，不构成本轮撤回条件；为避免继续按单句扩张正则，本轮记录而不追补。

真实写稿属于四个短任务、两名 writer 的针对性 sanity，不等同发布级长文、多附件、多轮或全 29 文种矩阵；ROUTE 为 agent 自报，不是操作系统级文件访问日志。后续只有同类 over-read 在真实链路中形成三次以上共性问题，或出现事实、文种、格式、输出模式回退时，才按同一仲裁原则继续处理，不做一例一修。
