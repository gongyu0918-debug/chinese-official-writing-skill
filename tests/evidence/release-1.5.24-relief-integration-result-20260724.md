# 1.5.24 减负集成验证结果（2026-07-24）

## 结论

固定 1.5.23 基线 `e97567724dbac00aa7bc77ad2758a2698c433702` 上，会议纪要叶与报告叶组合验证为 **PASS**，可作为明日小版本候选继续做发布准备。

集成提交：

- `da576f4`：会议纪要规则物理拆分至 `genre-playbook-minutes.md`；
- `d2d2960`：报告规则物理归并至既有 `genre-checklist-report.md`；
- `6887645`：纪要与报告同题 A/B 预注册。

两项产品变量都已在独立 worktree 完成真实 A/B。会议纪要为 1 胜 1 平，报告为 2 平，均无 Candidate 独有硬回退。本轮再用一项同时交付纪要与报告的自然任务检查组合影响，硬检查双侧通过，匿名盲审平局。

## 集成冲突与处置

两个产品提交都修改了入口路由、provider 和路由测试，直接 cherry-pick 出现预期的文本冲突。集成只合并两项既有语义：

- 会议纪要使用 `genre-playbook-minutes.md`；
- 报告、情况报告、情况说明使用 `genre-checklist-report.md`；
- 同一任务同时要求纪要和报告时，两叶同时加载；
- 其他普通文种仍使用 `genre-playbooks.md`；
- AI 专项仍按 1.5.23 的 `ai-compute-docs.md` 路由叠加。

第一次全量单测为 367/368，唯一失败是会议纪要候选留下的组合测试仍预期“纪要叶 + 通用 playbook”。报告叶合入后，正确组合已变为“纪要叶 + 报告叶”。该断言按组合后的预注册路由更新，未修改产品逻辑、没有放宽检查条件。更新后全量 368/368 通过。

## 工程验证

实际运行结果：

- `python -m unittest discover -s tests`：368/368 通过；
- 系统 Python 运行 Promptfoo smoke：20/20 通过，0 error，judge consistency 1.0；
- 固定 1.5.23 确定性消融：Candidate 108/108，Baseline 101/108；
- Baseline 7 项失败均为本轮新增的会议纪要叶、报告叶定位断言，不是 1.5.23 既有用例回退；
- `quick_validate.py chinese-official-writing`：`Skill is valid!`；
- canonical、五套发行镜像、reference 图和组合路由断言随全量测试通过；
- `git diff --check`：通过；
- tracked worktree：干净。

Promptfoo 在沙箱内首次使用 Hermes Python、第二次使用系统 Python 时，均因 Node 无权启动 Python 而产生 20 项进程错误。获批在沙箱外使用同一系统 Python 复跑后 20/20 通过。前两次仅记为 Windows 进程权限环境噪声，不计产品失败或通过。

## 实际路径减载

统计口径为移除空白后的 `SKILL.md + information-selection.md + 该任务起草阶段文种 reference`：

| 起草路径 | 1.5.23 | 集成 Candidate | 减少 | 降幅 |
| --- | ---: | ---: | ---: | ---: |
| 完整会议纪要 | 14054 | 11351 | 2703 | 19.23% |
| 完整报告 | 14054 | 11569 | 2485 | 17.68% |
| 同题纪要 + 报告 | 14054 | 12552 | 1502 | 10.69% |

该统计不把成稿后按需读取的终检 reference 混入起草阶段，也不把字符减少直接等同为语言质量提升。

## 组合真实 A/B

### 运行条件

- 原始任务：同一份完整材料分别形成专题会议纪要和试运行情况报告；
- 模型与档位：`gpt-5.6-sol / ultra`；
- Candidate 起草包：`SKILL.md`、`information-selection.md`、`genre-playbook-minutes.md`、`genre-checklist-report.md`；
- Baseline 起草包：`SKILL.md`、`information-selection.md`、`genre-playbooks.md`；
- 两侧 D0 后均读取 `final-review-layers.md` 与 `proofreading-checklist.md`；
- 每侧只生成一组正文，内含两份文稿；无补抽、无二次改写、无启动或读取错误。

### 硬检查

Candidate 与 Baseline 均完整保留：

- 2026年7月23日14时30分至15时30分；
- 明川市行政服务中心、办公室、信息中心、6个试用科室；
- 6月1日至30日、86名工作人员、430项、397项、33项；
- 统一查看任务进度、减少线下汇总次数；
- 移动端加载较慢、3名工作人员反馈附件上传失败；
- 2次版本更新及第二次更新后未再收到反映；
- 信息中心8月5日前完成优化方案；
- 办公室8月8日组织培训；
- 其余单位推广安排结合8月运行情况继续研究。

两侧文稿数量、文种、输出范围和状态强度均符合，无事实、数字、主体、期限、格式、空稿、保护性外扩或材料外程序硬回退。

### 匿名盲审

匿名映射在裁决后解封：A=`Candidate`，B=`Baseline`。

裁决为平局，直接修改成本相同。Baseline 的会议明确事项分列更利于扫读；Candidate 的报告更贴近“试运行”“试用科室”原始口径，优势相抵。两稿均可直接使用。

## 未进入集成的方向

两项 AI 通用规则迁移候选均已判 `FAIL` 并撤回：

- `handling-elements.md` 的 AI 小节迁入 AI 叶，会让纯 AI 路径增加 197 字，并形成目标文件自引用；
- `argument-chains.md` 的 AI 小节迁入 AI 叶，会让纯 AI 路径增加 282 字，并形成同类自引用。

两项失败候选均无产品提交，不能进入本集成分支。

## 剩余风险

- 真实 A/B 覆盖会议纪要、报告及两者组合，没有新增通知、请示、长文、多附件或跨模型矩阵；
- 两项拆分不改变规则内容，但入口路由同时列出两个专项叶，仍需独立 diff 审计确认没有漏掉混合文种和 AI 叠加；
- 本分支尚未改版本号、README、发布记录或平台包，也没有合并、推送或发布；
- 进入发布准备前，应再做一次独立只读集成审计，并以最终发布提交复跑最小门。
