# Word Markdown 清理句原子减载结果

## 结论

`PASS`。产品提交 `2770f3402398fc86f868fc9d89942d1795037a60` 只从通用
`review-checklist.md` 删除一处已经由同文件通用交付检查和
`format-gbt9704.md` 近场规则重复承担的 Markdown 清理半句；文号、密级、
签发人和印章防编造检查保持不变。

两组真实 A/B 均自然读取 `review-checklist.md` 和 `format-gbt9704.md`。
匿名盲审两题均由 Candidate 小胜，四稿未出现 Candidate 独有的事实、主体、
状态、文种、格式、输出模式、Markdown 遗漏或 P0 回退，满足预注册验收门。
本结果只支持合并这一处原子减载，不支持继续删除同条其余 Word 复核规则。

## 提交与范围

- 固定基线：`cde03cca2a36bc124d0c5b4420c8f89ebcfad5de`。
- 预注册：`816df39`。
- 产品提交：`2770f34`。
- 确定性真值调整：`7330686`。
- 修改范围：canonical 与五套发行镜像的 `review-checklist.md`，以及只验证
  既存双重锚点的确定性断言；未修改入口、路由、reference 加载条件、
  复核顺序、输出模式、脚本、Hook、FSM、修改次数、回退或发布链。

## 工程验证

- Word 定向边界：1/1 通过。
- `python -m unittest discover -s tests`：390/390 通过。
- `npm run eval:official-writing:smoke`：系统 Python 环境复跑 20/20 通过。
  沙箱内 Node 首轮误选 Hermes Python 后产生 20 个环境错误，记为宿主噪声。
- 固定基线确定性消融：Baseline 110/110，Candidate 110/110。
- Skill Creator `quick_validate.py`：通过。
- canonical 与发行镜像一致；`git diff --check` 通过。

全量测试首轮有一项 P025 失败，原因是确定性测试仍把已迁走的逐字短语固定在
`review-checklist.md`。提交 `7330686` 把真值改为分别核验通用 Markdown 清理、
Word 模式和防编造锚点，没有降低检查能力；定向与全量回归随后全部通过。

## 真实 A/B

两臂逐题使用同一原始任务，各取首个技术有效输出，不补抽、不二次修订。
请求模型为 `gpt-5.6-sol`，请求 reasoning 为 `high`；宿主没有向 writer 暴露
实际模型和 reasoning 字段，记为 `unavailable`。四个 writer 均记录实际读取
reference，Candidate 与 Baseline 两题都自然命中两个目标文件。

匿名映射：

- WM01：A=Candidate，B=Baseline。
- WM02：A=Baseline，B=Candidate。

| 任务 | 匿名结果 | 映射后结果 | 独有硬回退 |
| --- | --- | --- | --- |
| WM01 请示 Word 只审不改 | A 小胜；A PASS、B WARN | Candidate 小胜 | 无 |
| WM02 纪要 Word 只审不改 | B 小胜；A WARN、B PASS | Candidate 小胜 | 无 |

WM01 的相对差异是 Baseline 把已经能够识别的购置请批事项扩大为审批范围缺口；
WM02 的相对差异是 Baseline 重复列示正式发文缺项，并扩展提交对象、报送对象等
材料外核验项。Candidate 均识别 Markdown 标记，保持数字、责任单位、期限和
“未形成决定”状态，也没有编造文号、签发人或版记。

## 共同残余风险

独立 hard verifier 对四稿均判 `FAIL`：两臂都把稿内无法验证的事实真实性、
主送或审批权限、办理要素完整性和发文程序确认扩大为中高风险或正式 Word
定稿门槛。该问题在 Candidate 与 Baseline 中共同存在，不是本次删除重复半句
造成的 Candidate 独有回退，因此不改变本原子候选的相对 `PASS` 结论。

这项共同 P0 风险应单独登记，后续只能按正常场景共性证据另建单变量研究；
不得在本候选中追加 Prompt，也不得把本次合并表述为已经解决 Word 审查外扩。
