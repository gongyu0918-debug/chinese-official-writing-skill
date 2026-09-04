# WR-028 五次提交后复核

## 基线与范围

- 分支：`codex/wr028-remediation-plan-r1`
- 固定上一发布基线：`5869234bcfee5aeb7f70762035a8ee593569fbc3`
- 复核时 HEAD：`9045e659`
- 五次提交依次完成预登记与官方语料、当前 main 基线、最小产品原型、候选预登记和候选 runner 恢复。
- 产品差异仍只有 canonical `SKILL.md` 的 3 行路由/表项和一页 20 行整改方案 reference；其余 829 行是规格、证据、题目和可复跑工具，不进入 Skill 包。

## Baseline diff 与轻量消融

- `git diff --check 5869234b..9045e659` 无空白错误。
- 真实 A/B 已承担轻量消融：基线使用普通方案路由，候选只新增整改专叶。三类正向题中候选分别有 4、4、5 家读取专叶；两个控制题各 5 家均未读取专叶，说明直达入口依赖明确“制定整改方案”意图，没有因正文出现“整改”串入报告，也没有误伤普通实施方案。
- 有效短稿的未启动状态从基线 1/5 提升到候选 3/4；正文包装从基线 2/5 降到有效候选 0/4。中长稿保持实际措施和合理归因，没有因事实保护塌缩成问题复述。
- R1 仍有一处可归因硬回退：Alibaba2 中等审计候选遗漏基线已保留的“均尚未启动整改”。因此本次复核不把 R1 直接送入镜像或全量工程门。

## 回归与风险

- 路由控制通过：整改进展报告 5/5、普通实施方案 5/5 未读专叶。
- 仍存在但不归因于候选的风险：普通方案偶发过程旁白和过度扩写；整改稿偶发固定台账、培训、月报、考核或过细节点；机器检查对等义状态和否定句有子串误报。
- 下一步只做状态落位 R2；若定向真稿消除硬回退，再补直接路由断言、镜像同步和合并前一次全量门。

## 实际复核命令

```powershell
git status --short --branch
git log --oneline 5869234bcfee5aeb7f70762035a8ee593569fbc3..HEAD
git diff --stat 5869234bcfee5aeb7f70762035a8ee593569fbc3..HEAD
git diff --check 5869234bcfee5aeb7f70762035a8ee593569fbc3..HEAD
git diff 5869234bcfee5aeb7f70762035a8ee593569fbc3..HEAD -- chinese-official-writing/SKILL.md chinese-official-writing/references/genre-playbook-remediation-plan.md
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --summarize
```
