# WR-028 当前 main 基线结果

## 运行范围

- 产品基线：`main@5869234bcfee5aeb7f70762035a8ee593569fbc3`
- 导出文件：85 个
- 产品树 fingerprint：`c1d4d2f3ab558e8dad214c86b0702d1e26c55110df17f6c9759da69020ef728f`
- 模型：`alibaba-token-plan-2/deepseek-v4-flash-0731`、`alibaba-token-plan/deepseek-v4-flash-0731`、`ollama-cloud/deepseek-v4-flash:0731`、`opencode-go/deepseek-v4-flash`、`minimax-cn/MiniMax-M3`
- 每家运行短整改、审计整改、长教育整改、整改进展报告控制、普通实施方案控制各一题，思考强度均为 `max`。
- 共落盘 25 份真稿，其中 22 份隔离轨迹有效。Alibaba 1 审计题、MiniMax 长教育题和整改进展控制题出现用户 Skill 路径污染，按技术失效剔除，不计质量。

## 基线观察

| 原子 | 有效稿 | 当前表现 | 共同缺口 |
| --- | ---: | --- | --- |
| 短整改方案 | 5/5 | 五家都形成原因和实际措施，篇幅均未塌缩 | 4/5 漏掉材料明示的“整改工作尚未开始”；2/5 附带过程说明或横线；多稿补出书面告知书、系统记录、固定考核等材料未给的具体载体 |
| 中等审计整改 | 4/5 | 四类问题均能绑定措施和给定牵头部门，期限大体保留 | 有效稿中仍有精确子节点、第一责任人、定期报送等过细既定安排；MiniMax 虽成稿但漏“尚未启动整改” |
| 长教育整改 | 4/5 | 有效稿均覆盖五类问题、分工和两个阶段，篇幅与结构基本成立 | 多稿把“可设计的措施”继续扩成材料未授权的固定模板、专班/委员会、六个月预警、月报、考核挂钩或精确分段日期；当前状态虽多能保留，但依赖模型自行把握 |
| 整改进展报告控制 | 4/5 | 有效稿均保持报告文种及 2/1/1 状态，没有另拟整改方案 | 未见候选目标问题；应作为专项叶误路由反控 |
| 普通实施方案控制 | 5/5 | 五稿均保持普通系统上线方案，没有制造审计、督察或整改叙事 | MiniMax 大幅补造回退、旧系统并行、咨询点和培训等安排，是既有通用方案风险，不应冒充整改专叶候选回退 |

## 机器标记校准

自动检查共标出 7 份稿。人工复核后，其中两类不能作为失败：

- Ollama 审计稿写的是“虽未造成资金损失”，命中 `造成资金损失` 只是简单子串误报。
- OpenCode 普通实施方案写的是“历史预约记录以只读方式保留”，与必保事实等义，只因未逐字匹配而误报。

其余短整改四家遗漏“整改工作尚未开始”、MiniMax 审计稿遗漏“尚未启动整改”均为真实状态遗漏。后续门只阻断候选直接相关的遗漏、升级、错误责任关系、文种误路由和正文包装，不用固定套语或全文长于提示词代替质量判断。

## 基线结论

当前通用方案叶能够生成基本可用的整改措施，但缺少整改方案自身的状态、措施授权和粒度边界。共同问题已达到预登记的候选启动条件：一是短稿跨四家遗漏明示未启动状态；二是中长稿容易在“不能编造”与“必须制定未来措施”之间自行摆动，生成材料未给的固定组织和精确流程。进入仅包含一条直达路由和一页整改方案专叶的最小候选。

## 实际命令

```powershell
python maintenance/tests/evidence/remediation-plan-r1/run_baseline.py --prepare
python maintenance/tests/evidence/remediation-plan-r1/run_baseline.py --provider alibaba2
python maintenance/tests/evidence/remediation-plan-r1/run_baseline.py --provider alibaba1
python maintenance/tests/evidence/remediation-plan-r1/run_baseline.py --provider ollama
python maintenance/tests/evidence/remediation-plan-r1/run_baseline.py --provider opencode
python maintenance/tests/evidence/remediation-plan-r1/run_baseline.py --provider minimax
python maintenance/tests/evidence/remediation-plan-r1/run_baseline.py --summarize
```

MiniMax 首次在三题后被中断；runner 已改为按已有 `case_id` 断点续跑，第二次只补两个缺失控制题，没有重复消耗前三题。
