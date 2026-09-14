# MIT 普通脚本、内部规则与原生写稿审计

状态：重构候选，尚未达到合并标准。基线 `main@1ce7112303172478faa2392667a2de1098eb912c`；产品仍在独立分支，未合并、推送或发布。

## 改动与依据

1. 保全 Hook 到 `codex/pro-hooks-preserved-20260912@3b6f273b6ee4ea583e7c0ade8311ad1f262d7159`，再从 MIT 产品、镜像、活动工具与专属测试移出。保留全部普通写作能力和两种普通脚本；历史 MIT 副本许可不追溯撤销。详见[接续便条](../../../docs/pro-hooks-next.md)。
2. `draft_length.py` 独立统计正文篇幅；`prose_lint.py` 继续做文稿复核。修复业务标题截断正文、含提示模式漏扫正文，以及 Markdown 文后提示标题不能正确分区；连续未决谓语只给低风险线索，保护材料明确的未定状态。
3. 删除重复的旧 workflow；共性信息选择、论证、办理要素与复核各自收束。决定、决议、议案、公报、命令分为五个主叶，通报独立；算力页移除文种骨架和回到总路由的指针。
4. 改写/压缩/合稿统一进入信息选择；原稿与审稿意见采用对应脚本模式。脚本引起修改后核对受影响事实与文种，再复扫。专项页接回编号检查，避免提前交付。
5. 根据真实失败区分材料缺项、业务未定状态与模板空位，清理日期占位歧义；申请主送按用户提供的名称或职务称谓使用，文后提示逐项回看材料。

两份规则冷审见[共性页](common-leaf-audit-r3.md)、[旧主叶](remaining-leaf-audit-r1.md)。这些修复并不证明所有旧叶的语义已经等价，仍有主持/述职、申请场景及全套旧测试契约待处理。

## 原生写稿证据

[逐轮索引](native-evidence-index.json)按需读取每轮的参数、模型、候选文件指纹、执行命令、技术失败及原始稿件。`drafts/` 保留原始交付，未为评审清理旁白或修正错误。总计 19 轮、78 次调用、62 次具备终稿及 Skill 读取轨迹的技术输出；这个数字不是质量通过数。

- 五个客户端通道：`alibaba-token-plan/qwen3.8-flash`、`alibaba-token-plan-2/qwen3.8-flash`、`command-code/deepseek-deepseek-v4.1-flash`、`minimax-cn/MiniMax-M3`、`ollama-cloud/glm-5.3-flash`。
- 使用原生 Codex CLI 自主读叶和执行脚本；主线从 Git 导出，候选从文件系统冻结，两臂提示相同。不是把整套 reference 拼成一次无工具 API 请求。
- R1 使用旧 CLI 时不接受 max；R2 读取受限；R3 超时。这些不算有效写稿。R4—R5 在仓库下继承维护说明，只作诊断。R6—R11 移到临时工作区但仍使用主机 profile，保留全局代码指令干扰说明。
- R12 起使用临时 profile，保留相同执行政策、现有本地代理与精确模型通道；未复制账户凭据，也未修改全局设置。关闭自动 AGENTS 文档不能代替产品自身的交付约束。官方配置依据见 [AGENTS.md 指令发现](https://learn.chatgpt.com/docs/agent-configuration/agents-md) 和 [配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)。
- 隔离 profile 后完成 15 个成对 A/B 样本；另有一个主线单臂结果，对应候选 max 超时。Qwen 两通道下调为 medium 后分别完成采购改稿成对输出，MiniMax 使用 high，DeepSeek 用通道默认思考配置。每次失败保留，没有用重试覆盖首轮。
- Qwen 的超时不是脚本函数卡住：尾部轨迹中多版稿件已经计数完成、lint 正常返回，模型仍继续改稿或调用工具。R11 还出现工具参数和权限错误。应记为执行未收束并继续观察，不直接判模型故障或规则死锁。

首组 [8 对匿名冷审](mit-blind-review-r3-result.md) 与 [后续 9 对冷审](mit-blind-review-r4-result.md)均保留原句证据。配对身份分别在映射 JSON 中，评审时未读取映射。

## 真实质量结论

已看到采购公告直达专页、编号复核和两个脚本实际执行的收益。金额与未定状态在不少稿件中保留正确，部分缺项入正文的问题复测改善。仍不能判定整体不回退：

- 纪要曾把“会议地点尚未提供”写进正文；另一次改为正文外，但又靠重复未决事项补篇幅。
- 复杂申请两次漏掉已给主送，修订后又出现改成泛称；两臂都出现过未经许可加日期、虚构形成动作或稿后误报。
- 采购公告曾保留日期占位、误报已给的采购主体；后续正文日期占位消失，提示仍有过度补项。
- 审核有误读、过度修改与无据的审批前置条件。普通“给修改建议”偶尔被扩成整稿替换；不能因为建议包含“修改”就视作用户要求全文改写。
- 过程旁白在两臂及临时 profile 中均出现，尚未稳定压住。扫描的是稿件文件时，模型随后生成的消息包装仍可能未经扫描。
- 用户指出稿件偏短、申请原因不足。后续必须单列原因/必要性/申请事项的功能完整性，补普通篇幅和材料支持的原因展开样本，不能以短稿字数合格替代写完整。

单次独有问题、重复问题、规则诱因、两臂共同问题、环境失败分别记录。冷审中的“硬问题”仍需结合具体请求和复现情况复核；不按否定词或提示数量机械裁决。

## 工程验证

```powershell
python -B -m unittest maintenance.tests.test_reference_rewrite_contract maintenance.tests.test_promptfoo_eval maintenance.tests.test_draft_length maintenance.tests.test_review_regressions maintenance.tests.test_reference_uniqueness maintenance.tests.test_mit_script_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_product_surface_audit maintenance.tests.test_repository_reachability
```

171 项通过。覆盖图无环、真实链接、manifest 一致性、脚本分区和 CLI、镜像、最小包及产品表面标记。约 8.8 万字符压力输入中，计数和文稿扫描均在 1 秒内返回，见[记录](mit-script-stress-r1.json)。这不是原生 Hook 生命周期测试，也不证明模型不会重复调用。

全量 `python -B -m unittest discover -s maintenance/tests -p 'test_*.py'` 跑了 386 项，116 失败、25 错误；[失败清单](full-suite-triage.json)保留旧路径、旧标题、旧固定文本及模式预期的逐项名称。需要迁移和复核语义，未以删除或跳过来掩盖。聚焦通过不等于全量通过。

SKILL.md 比 main 减少约 48.1%，reference Markdown 减少约 39.7%，详见[字符统计](mit-rewrite-metrics-r1.json)。统计排除 Hook 运行代码、脚本、维护 manifest 和镜像；减字不作为质量证据。

## 复核者分歧与后续核对

R4 冷审 Q01 把 A 自报的 187 字视为正文计数；原交付明确把正文外提示也算入，根代理按标题至文后提示前的实际正文重新计算为 171 个非空白字符，低于 180 下限。保留冷审原报告并单列此纠正，不采纳错误计数。稿件事实、篇幅和交付分别评估。

旧 protective-negative-tail 测试已单独迁移：15 个旧失败来自新旧模式及复核文案预期差异，保留正负例后 10 项通过；产品脚本未因此修改。全量测试未再次跑绿，剩余迁移继续单列。
