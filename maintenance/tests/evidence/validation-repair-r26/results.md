# 最小修复：技术检查与规则审阅分开

按用户最新要求，写作规则以可读性、语义完整性、路由通达及真实写稿A/B判断，停止用关键词、整句、中文标题或步骤数量作Python语义门禁。本轮只修技术检查、一个评测程序的实际路径遗漏和文档漂移；没有修改产品SKILL.md、references或普通脚本，没有重跑模型写稿。

R25产品指纹仍为`03b11fbbfca3409b3b7ae6853f4e9174448746378fee0b3d04cf9fb46ff97d2d`。此前实稿结果保留；“115项通过”仅覆盖三个模块，其工程范围声明不足，不能解释成全分支门禁通过，也不能因历史词句测试红灯推翻全部实稿证据。

## 复现与处置

| 项目 | 复现及最小处置 |
| --- | --- |
| 全量Python测试 | 在0aa38587复现411项、109 failures及7 errors。保留原日志；结果混有历史措辞锁，不将其总通过率用于写作质量判定 |
| 首页路线脊假失败 | 去掉固定路线句、中文标题、三步/四步数量断言。工具改查显式文件链接、断链、不可达参考及工程命令残留，支持`--root`。换标题和链接表现形式不再误报 |
| description与文后提示原句锁 | description只检查frontmatter有效、非空及镜像一致；移除缺项清理等整句要求，保留普通脚本文件、路径和Hook边界检查 |
| promptfoo旧文件路径 | 保留34个原测试方法和输入，将引用集合对齐现有文件；移除本轮中途新增的中文词句和页内步骤断言。它检验的是评测程序选择文件的行为，不是判断规则语义 |
| 真实字段路径遗漏 | 现有“请按字段整理工作总结”被错误断言为不读字段页。纠正该期望后保留1个失败，评测provider统一收尾处仅加3行，明确字段动作才加入字段页，普通总结不加入 |
| 常设治理边界 | 恢复main不含付费提纲Hook、胶水、测试和详细规格的边界；Pro专属内容不反流。没有恢复已退役的旧Hook运行链 |
| 文档指纹 | 页映射摘要此前实际停在R23，更新为R25。R20冻结目录73文件逐一核对无漂移；与当前包有5文件差异属于后续改动，不是冻结证据被改坏 |
| 许可及旧平台快照 | 修正根README仍残留的v1.6.34截止表述，明确1.x既有Hook继续MIT；将red-skillhub标为历史快照、非当前发布来源，未批量更新或发布旧平台包 |

`run_real_prompt_ablation.py`的111项只做历史静态覆盖：指定main111/111、候选28/111，共83个用例发生523条字面未命中；未见其中的lint行为检查失败。这不是111次模型写稿，也不是路由图检查。按用户指令停止迁移这些词句，不为全绿加回旧规则。[只读核查](../../../../output/validation-repair-r26/ablation-review.md)保留原结果与取样范围。

## 相关验证

```text
python -m unittest maintenance.tests.test_product_surface_audit maintenance.tests.test_description_news_trigger maintenance.tests.test_mit_script_boundary maintenance.tests.test_promptfoo_eval maintenance.tests.test_draft_length
python maintenance/tools/audit_product_surface.py --root chinese-official-writing
python maintenance/tools/validate_reference_manifest.py
```

56项相关技术测试通过，包含计数、输入读写、文后提示分隔、评测文件选择、frontmatter、路径和镜像检查。随后给路径解析增加Markdown链接支持，只重跑受影响的4项工具测试，通过。当前133个显式文件指针目标存在，67参考页可由入口链接到达；manifest检查通过。静态可达不等于模型每次实际读取，具体执行仍看原生写稿轨迹。

没有为旧词句断言重跑全部discover或补齐到全绿；初次全量失败记录没有删除，不声称整库测试通过。该类测试保留作历史参考，当前检查口径已写入开发细则与Spec。修复过程中的中间结果和最终结果分别保留，见[原始记录](../../../../output/validation-repair-r26)及[核对摘要](checks.json)。

## 本轮没有据此扩改的项目

- 额外要素兜底层和anti-AI例库：审计提出了值得关注的架构风险，现有摘录不能单独证明语义损失；不据静态字数恢复大段规则。
- 字数退出码：已确认未达标时退出0，但JSON明确返回`below/above`及差额，读取失败为2。保留现有报告式行为，本轮不增加严格门禁或更改CLI契约。
- 成本和速度：减少的是规则字符及部分读取量，R24/R25未证明费用或速度普遍改善，原始用量与慢调用记录继续保留。
- 评测provider的审后改稿、结构动作还有待验证建议，本轮只修现有原题暴露的字段路径遗漏，不据模块通过声明所有自然语言选路已完整。

本轮是维护层最小修复，产品包保持原字节；没有合main、安装、推送或发布。
