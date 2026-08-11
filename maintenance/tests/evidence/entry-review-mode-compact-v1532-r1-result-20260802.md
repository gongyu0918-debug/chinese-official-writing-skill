# 入口审稿模式原子减载结果

## 结论

PASS，具备合并资格。入口只保留“只审不改、代改才出改后正文”两类输出边界，并把定位、分级、格式和去 AI 味分别指向既有专项叶。canonical `SKILL.md` 净减 121 个字符，审稿模式单条由 289 个字符降至 168 个字符；两题真实复验均难分，没有可归因的输出模式、事实或格式回退。

## 固定对象

- 固定基线：本地 `main=5ed38350c2ac10ac83ea81b5f6d3ec7c04462012`。
- 产品提交：`b78cf3f46ee53bc8f279d0a691e6c16b4df8db60`。
- 消融位置修正提交：`934fc65d`。该提交只把五个审稿用例从“入口必须逐字复述细则”改为“入口保留准确指针、专项叶保留完整细则”，没有修改 Skill 产品文件。
- 旧 current-main 首稿生成于 `6975c52a`；`git diff --quiet 6975c52a 5ed38350 -- chinese-official-writing skills .agents .qwen hermes openclaw` 返回 0，因此可复用为当前 main 产品首稿。

## 规则保存情况

- `SKILL.md`：保留只审不改、问题位置、风险层级、修改建议、代改触发和两份专项叶指针。
- `review-checklist.md`：继续承载逐项定位、风险层级、普通文本标签、不评分、事实不清审稿和格式检查。
- `anti-ai-patterns.md`：继续承载成簇判断、孤立词句不误杀和公文正式语气保护。

独立静态审计最初发现“去 AI 味检查”误指向 `review-checklist.md`；产品提交前已改为分别指向 `review-checklist.md` 和 `anti-ai-patterns.md`，定向测试同步核验两个指针。

## 真实 A/B

复用已冻结的 IR01、IR02 自然任务和当前 main 首稿，只新增产品提交的两份 Candidate 首稿。每题只取首个技术有效输出，不补抽；writer 未读取基线稿、旧稿或历史结果。精确模型标识和 thinking 档位由宿主记为 `unavailable`。

| 任务 | 匿名结果 | 硬项 | 结论 |
| --- | --- | --- | --- |
| IR01 只审不改 | 难分 | 两稿均 PASS | 均按位置、风险层级、修改建议输出，未重写、未评分；完整定位 Markdown、主送格式和联系人占位，保留引号原话。 |
| IR02 审后代改 | 难分 | 两稿均 PASS | 两稿逐字一致，只输出改后通知正文，保留对象、事项、日期、邮箱、联系人和电话。 |

独立 judge 判定两题均无可归因回退，直接使用成本均为 0。

稿件 SHA-256：

- Candidate IR01：`A5D784950D42832E82B078841DE007F3D2879D83701BDC40BD29FB769E563266`
- Current-main IR01：`BC47FAC59A2A6373AF56CD523E4DCC33670B717FC1F668ED58149EAE08BC24A5`
- IR02 两侧：`9E8DD393125C5C7C3BEB45089725F574D991EACF18117D7BF27A6FF1361764A6`

原始稿和 trace 保存在忽略目录 `output/entry-review-mode-compact-r1-real-ab-20260802/`。

## 工程验证

- `python -m unittest discover -s tests`：412/412 通过。
- `npm run eval:official-writing:smoke`：20/20 通过，0 failed，0 errors。
- `python tools/run_real_prompt_ablation.py ...`：固定 main 111/111，Candidate 111/111。
- `python .../skill-creator/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py`：canonical 已同步至五份发行镜像。
- `git diff --check`：通过。

全量单测首次失败的五项均为消融仍要求细则逐字出现在 `SKILL.md`，而不是规则实际丢失；检查改为“入口指针 + 专项叶完整细则”后，固定基线与 Candidate 均为 111/111，未删除能力断言。

## 剩余风险

- 真实复验只有两题，且精确模型和 thinking 不可核验；本结果证明本原子无回退，不外推为整体语言质量胜率。
- `review-checklist.md` 仍有一处兼容性写法“审一下”。历史证据只证明模型能理解该口语，不证明它必须常驻专项叶；应作为下一独立高熵原子验证，不与本次减载混合。
