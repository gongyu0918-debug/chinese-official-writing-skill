# Workflow 事实边界去重当前主线复验结果（2026-08-04）

## 结论

`PASS / MERGE ELIGIBLE / 1 VALID CANDIDATE WIN / 2 TECHNICALLY INVALID PAIRS`

本轮固定 Baseline 为 `9b2de9f1af68b47751f7404ebbf75f731d68eb7b`，Candidate 产品提交为 `b25d704d`，测试契约提交后运行 HEAD 为 `751223349488cea89ed80b6f05fe98b462c4d7fb`。产品只把 `workflow.md`“素材映射与事实边界”的重复否定清单收成一条正向事实源规则，并指向 `information-selection.md` 和轻量任务卡；未修改入口、文种路由、篇幅规则、复核顺序、脚本行为、输出模式或发布链。

当前主线严格有效的 WID04 匿名盲审为 Candidate 胜，且胜点能够映射到本次改动：Candidate 没有 Baseline 的“按现有工单记录统计”“仍按当前状态办理”等保护性重复，也没有新增“已按咨询情况予以记录”“持续做好工单办理和回访记录”等材料外表述。两稿事实、数字、主体、状态、文种、四个指定小节、输出范围和 450—550 字要求均合格。该结果满足用户明确设定的“当前主线至少一胜”门槛。

WID05、WID06 的代理清单没有保存逐字一致的原始输入，均判技术无效，不进入胜负统计，也未补抽或重跑。结合历史正确文种路由 A/B 的 Candidate 5 胜 1 负、唯一负项为一次篇幅下偏，本候选可合并；历史已知篇幅风险继续保留，不在本次去重句中追加展开规则。

## 工程验证

- `python -m unittest discover -s tests`：442/442 通过。
- `npm run eval:official-writing:smoke`：20/20 通过；该结果是 stub/smoke，不作真实写作质量证据。
- `python tools/run_real_prompt_ablation.py ...`：Baseline 111/111，Candidate 111/111。
- 定向规则测试：75/75 通过。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 发行镜像与 canonical 一致；`git diff --check` 通过。
- 六份既有成稿运行 `prose_lint.py --json --format --structure --delivery-mode draft-body`：`[]`。该项只作辅助硬检查，不替代盲审。

初次确定性消融曾出现 Candidate 106/111，原因是旧测试只接受被去重的逐字句子，不接受同一行为由 `information-selection.md`、任务卡与正向指针共同承载。测试契约提交 `75122334` 将断言改为同时接受发布基线的重复布局和候选的单一规则源布局；没有放宽事实、状态、旧稿回流或输出模式要求。修正后两臂均为 111/111。

## 真实 A/B 运行有效性

| 任务 | Baseline | Candidate | 对称性 | 处理 |
| --- | --- | --- | --- | --- |
| WID04 校园维修工单办理情况报告 | 543 字，`329241bf...` | 457 字，`e0ef319f...` | 输入 SHA-256 相同；两臂 7 个 reference 相同；attempt=1、revision=0 | 有效，匿名 A=Candidate，A胜 |
| WID05 新员工培训实施情况总结 | 452 字 | 491 字 | Baseline 清单漏记“旧版和参考材料只用于理解修改要求”，输入哈希不一致 | 技术无效，不计分、不重跑 |
| WID06 档案库房设施巡检整改阶段情况报告 | 461 字 | 465 字 | Baseline 清单把测试控制语写入 raw input，并改变标题引号，输入哈希不一致 | 技术无效，不计分、不重跑 |

四个有效 WID04/WID06 文件哈希均与各自 manifest 一致；两组技术无效来自证据链不对称，不解释为产品失败或通过。

## WID04 匿名盲审

- Candidate：事实、数字、日期、主体、状态、标题、四个小节和篇幅均合格。首段仍有“渠道合计936件”“绝大多数”“本报告围绕……”等可压缩内容，评为 G0。
- Baseline：算术比例均正确、篇幅合格；“已按咨询情况予以记录”不是材料明示事实，“持续做好工单办理和回访记录”扩展了既定 7 月安排；另有保护性重复，评为 G1。
- 结论：Candidate 胜。评审认为差异不只是随机措辞波动，Candidate 的事实边界和直接修改成本更稳。

## 历史交叉证据与剩余风险

历史产品原型 `3138b055` 在正确文种路由的 WID04—WID06 中为 2 胜 1 负；加上早期三题方向信号，累计 5 胜 1 负。WID05 的历史负项是 Candidate 410 字，低于 450—550 字区间；它没有形成跨三个正常场景的共性事实或文种回退，但说明去重后仍需监测既有篇幅下偏。

本轮不把篇幅校准、段落展开、材料充分度或其他候选机制拼入该提交。后续若在三个正常场景复现 Candidate 独有的欠写，再作为独立篇幅候选处理。
