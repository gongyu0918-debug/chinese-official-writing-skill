# 普通自然任务与五版修改：R1/R2结果

状态：`REAL_WRITING_COMPLETE / BOTH_CANDIDATES_REJECTED / PRODUCT_RESTORED`。本轮在 `codex/natural-writing-stability-r1` 独立worktree完成两处reference原子的真实试验，最终产品与已合入main的 `a2a817d1` 相同，净减少0 bytes。需求、失败证据和验收口径进入维护区；没有接镜像或Hook胶水。

此前取消清理、DSH当前回合取消、OpenCode失败分类及新闻完整事实年份规则已随 `a2a817d1` 合入main，最终806项全量通过；见[合并记录](../remaining-hook-quality-merge-r1/result.md)。本报告不改写此前50次真实执行、被拒workflow候选或宿主边界，也不把旧全量门当作本轮候选真稿通过。

## 本轮任务与证据

[题面](cases.json)先于调用固定：报告900—1100字、纪要600—800字；每条链依次起草、更正数字/状态/期限、删除完整事项、单独插入新事实、压缩到700/500字。每次均为自然中文请求，不点名Skill、不写reference路径、不注入规则全文。Alibaba2 DeepSeek V4 Flash与MiniMax-M3均使用max，初稿建立独立CLI会话，后四版实际resume原ID。[薄封装](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/run.py)复用既有驱动，[预登记](preregister.md)保留候选选择顺序。

| 阶段 | 冻结产品 | 独立会话 | 相关版本 | 技术失败 |
| --- | --- | ---: | ---: | ---: |
| 基线 | a2a817d1 | 4 | 20 | 0 |
| R1报告页删条件 | d4859fb9 | 4 | 20 | 0 |
| R2信息选择句改写 | ecf9e361 | 4 | 20 | 0 |

合计60次真实写稿/修改、12条五版链。R2复用原基线，未补样或重新采样基线；正文、工具trace、调用参数、stderr、会话回执与盲审均保存于raw，逐文件hash见[清单](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw-manifest.json)。[R1汇总](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/summary.json)、[R2汇总](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r2/summary.json)和两轮[模型绑定](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/model-binding.json)、[模型绑定](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r2/model-binding.json)记录实际模型、max和5个turn context。

这是无Hook的普通Skill写稿试验；调用参数显式禁用两处同名个人Skill，插件、应用和记忆为false，实际trace未观察到其他Skill读取。原预登记及fixture的“其他个人Skill关闭”标签过宽，不能当作已证明所有个人Skill均关闭。宿主通用编码AGENTS偏好仍在12条会话中出现，两臂相同。不能称为无宿主指令环境，也不能由本轮普通稿推定Hook终稿质量。

12条初稿中11条成功读取Skill入口；R2四条都读取了被改的信息选择页。R1一条纪要链把 `.agents` 写成 `agents`，实际安装文件存在，尝试失败后继续交稿；此真实路由失败保留，未当作无效样本删除。[定位](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/route-observations.json)记录路径、宿主偏好和可核边界。读取统计依据成功工具输出；整文件字节上界与API token不用于宣称减载收益。

## 候选选择

| 原子 | 变化 | 真稿观察与决定 |
| --- | --- | --- |
| R1 报告事实限制条件 | 仅删条件前缀“用户写明“材料只有”或事实很少时，”，规范化UTF-8/LF −51 bytes | 实际读取修改页的Alibaba基线/候选均未确认硬错；MiniMax候选仍有事实问题且仅读入口，未读取改动页。其问题分组数变化不支持归因。拒绝，ecf9e361恢复报告页。 |
| R2 分析与事实经过 | 替换“合理推断必须有责任主体”为分析不得反推未给经过、范围、职责及既定安排，+111 bytes | 四条初稿均读修改页；Alibaba报告未确认硬错，MiniMax报告仍补出既成审核等事实。Alibaba纪要新增“信息部组织/介绍演示”及系统阶段判断，对应基线没有确认这两类事实硬错。拒绝，139e2f3f恢复信息选择页。 |

两次都是产品规则原型先于真实写稿；未因表面字数减少或某条链错误较少就补工程。两处变更均与原有合法分析、一般目的、进行态和合理建议规则分开测试，没有扩大为多页重写。最终SKILL.md、workflow、references、Hook和所有包体均与d8a942c3产品相同。

## 多版质量观察

报告的两轮Alibaba候选及原基线均未确认硬问题；这只是这些会话的审查结论。MiniMax报告中材料外既成审核、职责或活动归属在部分版本继承，部分随删除/压缩消失。R2末稿正文589字，但整个回复755字，原因是正文外的引导、自检和说明；不能把它写成正文自身超限。

纪要的数字/期限更正、整件演示删除、独立插段和末轮正文上限都完成；部分链在删除时又引入“已答复并办结”等新状态，或把已有错误一直带到末稿。六条纪要链均有正文外说明，部分另有未提供的地点、活动角色、审批链或预算约束。R2的两条纪要末稿正文分别431/447字，整个回复493/579字；最后一条正文长度合格仍不代表整个交付合格。

这些观察区分初稿新增、后续继承、合法删除和压缩消除。用户要求其他段落保留时，先核对正文的精确剩余文本；不把外围说明字数变化误算成正文越界改动。用户允许全文压缩后，不再强制沿用上一版插段边界。角色泛化、直接分析、自然目的与真实新增过程分别判读，未把每个新词或一般建议都算硬错。

[报告基线盲审](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/report-first-review.json)、[报告R1候选盲审](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/report-second-review.json)、[纪要R1四链盲审](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/minutes-review.json)、[R1根代理复核](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/root-adjudication.json)保留原结果；“系统操作要点”是否超出“仅介绍目录录入方法”保留[分歧补充](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r1/report-first-review-addendum.json)，不追加为一致认定的硬错。

R2分别见[报告P5](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r2/report-third-review.json)、[报告P6](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r2/report-fourth-review.json)、[纪要M5](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r2/minutes-second-review.json)、[纪要M6](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r2/minutes-third-review.json)与[根代理复核](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/r2/root-adjudication.json)。匿名包与映射分别存档，审稿者只读获准匿名包，根代理复核后才作准入决定。

## 验证与当前边界

实际命令及结果见[验证回执](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/validation.json)：

```text
python -X utf8 -B -m unittest maintenance.tests.test_status_ledger_consistency
  16/16 PASS，0.117s
python -X utf8 -B -m unittest maintenance.tests.test_repository_reachability
  7/7 PASS，1.899s，含活动Markdown本地链接与结构
python -X utf8 -B maintenance/tests/evidence/natural-writing-stability-r1/run.py --help
  exit 0
git diff --exit-code d8a942c3 -- chinese-official-writing packages
  exit 0，无产品差异
git diff --check
  exit 0
```

两处候选均在真实结果后恢复，当前最终差异只有维护文档和证据；产品与a2a817d1相同，迁移该产品的806项全量通过记录，本轮不重复全量。原始证据采用二进制Git属性，297项文件hash在暂存Git blob中逐项复核；[归档校验](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/integrity-check.json)记录数量与清单hash。

本轮累计五次提交为a2a817d1、d8a942c3、d4859fb9、ecf9e361、139e2f3f；当前实验相对d8只有后三次。第五次后停止新产品修改，做独立复核、baseline diff、以现有单原子真稿为轻量消融，以及相关回归，见[复核](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/natural-writing-stability-r1/raw/five-commit-review.json)。

本轮只覆盖两类正常任务、600—1100字初稿和五版修改，多个版本彼此相关；没有把60次换算总体稳定率。更长稿、更多材料密度和用户措辞仍须继续按真实风险扩展；本轮没有新增Hook on/off或原生宿主生命周期证据。剩余重点是已读规则仍补造具体事实、初稿错误跨版继承、正文外说明及自然资源路径失误。对应需求WR-020c保持IN_PROGRESS，两处候选REJECTED且不留HOLD。未推送、移动tag、发布平台或修改付费分支。
