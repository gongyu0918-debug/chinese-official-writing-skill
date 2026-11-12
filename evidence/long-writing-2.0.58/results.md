# 长文与多文种真实写稿结果

日期：2026-11-12。基线为 `b2fb1682f1f7a968f2e9c5a806acd29a475d333d`，首轮候选为 `b86e45a1df1dd69a703cfa1bd51bf3eda6656ef0`，优化后候选为 `7016f35`。原始输出保存在 scratch `C:\Users\2\Documents\chinese-official-writing\output\long-writing-2.0.58`，原始 prompt 与映射见 `cases/`、`plan.md`。verifier 不接收映射，以下在评审结束后解盲。

## 首轮 2.0.57 对 b86e45a

| case | candidate 侧 | baseline 侧 | 独立盲审结论 |
|---|---|---|---|
| L1 运行报告 | A，3214 字，WARN | B，3736 字，WARN | baseline 小胜；候选有局部重复，baseline 有材料外“尚未”判断 |
| L2 项目申请 | B，3528 字，PASS | A，3926 字，PASS（轻微提示） | candidate 明显胜，结构和请批措辞更完整 |
| L3 采购请示 | A，1574 字，PASS | B，1818 字，WARN | candidate 略优；baseline 有材料外具体化 |
| L4 制度正文 | A，3088 字，PASS | B，3073 字，PASS | candidate 略优；排版仅检查基本可用 |
| L5 会议纪要 | A，1822 字，WARN | B，1876 字，WARN | baseline 优；候选存在明显同义重复和定义式凑字 |
| L6 年度总结 | B，2493 字，FAIL | A，2241 字，WARN | baseline 胜；候选把覆盖 6 个社区写成范围扩大/延伸，构成独有事实硬回退 |
| L7 讲话稿 | A，2455 字，PASS | B，2633 字，PASS | 两版均可用，baseline 小胜 |
| L8 办理复函 | B，1536 字，WARN | A，1553 字，PASS | baseline 略胜；候选有材料外指南栏目和后续承诺 |
| L9 调研报告 | A，3962 字，WARN | B，3398 字，PASS | baseline 略优；候选将协助需求误收窄为预约环节且有重复 |
| L10 只审不改 | B，WARN | A，WARN | candidate 略胜但不干净，候选审核建议存在“一文一事”与同一请示分项并用的矛盾 |
| L11 指定替换 | A，PASS | B，PASS | 两版逐字一致，三处替换外无变化，程序比对均为 EXACT |
| L12 新闻综述 | B，正文实测通过 | A，首次检索未成稿后重试 | candidate 实际打开 3 个来源；baseline 首次持续检索未成稿后改用限定入口 |

篇幅数字来自 `count_outputs.py` 的独立复核；个别 verifier 自报计数因是否含标题、日期或方案边界不同而略有差异，均另保留原始输出和 SHA-256。L11 非空白字符数为 643，文本比对不依赖该数字。

## 首轮发现与优化

1. L6 的“覆盖范围扩大/延伸到社区”没有前期基线，是 candidate 独有事实硬回退，阻断发布。
2. L1、L5、L6 出现不同程度的重复解释和定义式凑字，说明达到字数不等于长文质量合格。
3. L9 将“需要电话或现场协助”误限定为“预约环节”，需要把不同问卷题目和统计对象分开解释。
4. L8、L10 的材料外细节和审核建议矛盾按单样本 WARN 登记，不扩写为全局规则。
5. 格式仅有限参考，普通版继续聚焦写稿能力；双面印刷与左侧装订的条款编号只作文字修正。

据此在 `7016f35` 中作四处小范围调整：`writing-rules.md` 防止长文凑字，`genre-playbook-work-summary.md` 要求比较结论有前期基线，`genre-playbook-research.md` 分开不同问卷题目，`format-gbt9704.md` 修正 6.2/6.3 条款编号。L1、L5、L6、L9 用新候选和新 baseline 重写，其他 case 保留原结果。

## 优化后复测

### L1/L5

- L1：candidate A2=3186 字、baseline B2=3309 字，双方均 WARN，baseline 窄胜。候选仍有总述预演和局部重复，未出现新的事实硬回退。
- L5：candidate A2=1815 字、baseline B2=1819 字，双方均 WARN，candidate 胜。候选正确区分权限试用与正式清单；baseline 将权限试用错置到继续研究事项，属于其侧状态归类风险。

### L6/L9

- L6：candidate B3=2233 字、baseline A2=2319 字，candidate=WARN、baseline=FAIL，candidate 胜。B3 未再出现扩大、延伸、拓展等无基线覆盖表述；A2 将 6 个社区写成延伸，构成 baseline 侧事实硬回退。B3 仍有软性评价和重复提示，不能写成全 PASS。
- L9：candidate A2=3817 字、baseline B2=3823 字，双方均 PASS（有 WARN），baseline 微弱领先。两版均未把协助需求误写成不能线上预约，candidate 的数据含义误读已消除；baseline 的题目分层略好，candidate 的 81 人边界更干净。

## 当前结论

1. 复测后的 candidate 没有 FAIL。L6 首轮硬回退已解除，L1/L5/L9 的复测没有新增事实、文种、结构、篇幅或输出模式硬回退。
2. 12 类场景均已完成真实写稿，长文场景 L1/L2/L4/L9 均实测达到 3000 字以上；其他中等篇幅和专项任务也按各自范围交付。原始与复测合计 34 份输出，L11 另有 2 份仅经消息传递的指定替换文本。
3. 当前候选仍有 WARN：长文局部重复、材料外细节、软性评价和来源披露不完整。不能把结果写成“全部 PASS”或“没有写作风险”。
4. 本轮结果支持进入 2.0.58 发布准备，不支持未经版本推进、发行包复核和用户批准直接发布。当前本机安装仍为 2.0.57，未 push、未发布、未同步插件。

补充证据卫生：L5 baseline 复测 writer 将文件写为 `L5-B.md`，经核对后复制为 `L5-B2.md` 供盲审；首轮 L5 的独立 verdict 已保留。部分测试命令在 baseline 审计树产生未跟踪 `__pycache__`，不属于 tracked 产品文件，结论只依据固定提交树和交付文本。

### L12 新闻定点修订

- 首轮 baseline A=PASS，candidate B=WARN，baseline 略胜。candidate 的季度归属和直接归因存在软偏差。
- candidate B2 已完成定点修订，季度归属和过强归因均已消除，正文 848 字（不含标题），没有新增事实错误。
- 独立复核：baseline A=PASS，candidate B2=WARN（轻微），baseline 略胜。B2 的剩余问题是工信部行未明确同源统计披露；两侧均无独有硬回退。三个唯一链接均由 verifier 实际打开，原始 PDF 第 10 页、人民日报和工信部页面内容对应。
