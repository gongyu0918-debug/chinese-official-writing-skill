# Hook 质量构建 R1

基于已发行 main `b77f6381438c8fa01f8576c205d13af4b8a987fd`，在 `codex/hook-quality-build-r1` 独立 worktree 构建。保留连续改稿参与与默认正文清理；自然字数解析和原稿事实纠错候选暂不准入。未合并、推送或发布；版本仍为1.6.28，未改 Skill、references、示例或付费包。

## 四项结果

| 要求 | 本轮结果 | 不能据此声称 |
| --- | --- | --- |
| 连续改稿参与 | Claude原型五版后四版全部进入；正式报告旧窄措辞在第七版漏入，修复后同一会话第八版恢复；正式纪要后四版均进入。恢复材料按时间仅取用户请求，更正/删除优先，终态只保留hash及计数 | 参与不等于原稿事实正确；其他宿主、分支历史及更长会话未验证 |
| 正文外说明 | P6 755→589、M6 579→447，正文逐字保全。修复完整单JSON围栏误拒；默认清理核验/回显后继续原审查，两个集成链最终delivery_verified | 不是全稿事实核验，也未覆盖所有自然措辞和包装 |
| 自然字数上限 | 原型识别700/500，但两条真实链被原回复硬锚拦回；分离出447字正文、改为400字的新请求中，唯一压缩调用超时。两轮原型均撤回，10%容差未改 | 解析正确不等于最终合限；超时不算质量胜负 |
| 原稿已有事实错误 | 7次尝试、6次有效。收窄后M5能仅删两处材料外主体，其他文字逐字保全；仍因关系未独立核验选回D0。保留原合同，不放宽硬锚 | 最终纠错交付仍为0；不宣称新增完整事实核验能力 |

## 实际写稿与宿主

- 使用已有便宜路线 `alibaba-token-plan-2/deepseek-v4-flash-0731`、`minimax-cn/MiniMax-M3`。同稿修稿/核验/回显使用隔离CLI会话与原始真实D0，保留模型绑定、原始prompt/reply及哈希。
- 连续写稿使用原生Claude CLI，同一session真实resume，自然请求不点名Skill或强迫读取。首次Read-only工具配置的R1五版因启动路径转义错误导致Hook全部失效，完整保留为无效Hook实验；未算产品失败。R2恢复原生Skill工具后，成功读取本Skill的references，原型完成五版链。
- R3正式报告前七版使用冻结窄解析器，第七版“改得”未参与；第八版换入已登记的措辞修正后继续同一session，绑定8回合。R4正式纪要使用独立MiniMax五版链。两条正式链共44次Stop、31次内部续写；内部续写不是31个独立质量样本。
- 原生CLI允许Read/Skill，有宿主内置Skill描述；不能声称所有内置Skill已禁用。核对实际工具使用，未将其他写作Skill作为本轮材料。隔离配置仅存在output测试目录，未修改用户安装/启用状态。
- 最后收窄同稿指向、Read路径及取消竞态后，以真实会话前缀复放：13个请求中11个后续请求可恢复，10个已有原生source hash逐字一致；R3第七版原生漏入仍保留，第八版是单独实测。不是重写旧结果。

原生稿件仍有明确问题：R4第五版整回复626字、正文含标题556字，均超过500字，前言的合限自证也不实。R3第五版Hook有13字符局部减冗且保留上线未批准状态；其他稿件的材料外程序、外围研究安排或前导说明不能由“门禁已运行”抵销。详见[独立质量报告](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/continuity/production-quality-review/report.json)与原始稿。

## 正文清理组合

[原清理实证](cleanliness/README.md)包含18次独立调用、基线M6围栏失败、精确正文结果及3个明确格式反控。随后用两份真实洁净稿先跑既有默认门禁，新调用3次，正文均未变化；再接默认预处理，用原始完整D0复放前3条逐字一致的真实清理回应，后续默认门禁新调用3次，两个最终正文仍逐字一致并完成清理。

此组合遵循先真实结果、后胶水。默认入口不会用清理终态替代原审查；预处理已启动后，模块不可用或回显重试耗尽会明确停止。核验包只接受整个回应为单JSON/单JSON围栏，仍拒绝旁白、多对象、错误hash和错误删除项。来源见[顺序原型](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness-after-review/preregister.json)、[完整集成](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness-integrated/preregister.json)。组合是实际模型驱动的core Harness，未冒称新增原生宿主组合覆盖。

## 审查与验证

[独立core复核](core-review.md)保留并修复：独立新稿混入旧材料、Read路径越界、取消窗口及并发失败终态被交接吞掉。最终取消/终态反控通过，终态不会恢复source_text。全量首次817项中2项失败：Stop决策分支超限及共享模块缺入口链接；拆出准备函数并补链接后，全量817项通过，123.005秒。未放宽复杂度门槛。

实际命令：

```powershell
python -B -X utf8 -m unittest discover -s maintenance/tests -p "test_*.py"
python -B -X utf8 maintenance/tests/evidence/hook-quality-build-r1/core_review_probe.py
python -B -X utf8 maintenance/tests/evidence/hook-quality-build-r1/replay_continuity.py
python -B -X utf8 maintenance/tests/evidence/hook-quality-build-r1/cleanliness/replay_saved.py
```

执行使用Python313的明确绝对路径，未借用环境中其他python。最终文件/链接/包体及quick validate结果见[验证记录](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/validation.json)。最终Claude companion组装60文件，fingerprint `a1cde757ac69f0d6dcb7e3551a59e9dbe293872e8d33eedc320a500f17491bcf`；canonical quick validate和`claude plugin validate --strict`均通过。组装校验不等于把最终文件在全部宿主重新在线运行；原生冻结包与最后收窄的差异、真实材料复放边界已在上文列明。

## 未完成与下一原子

1. 自然字数解析仍为HOLD；下一步从无包装真实D0完成压缩、关系验收和逐字交付，再单独评估启动容差。
2. 新前言“以下正文约500字以内……”的[最小清理试验](cleanliness-new-prefix/result.md)中，D1已精确删掉70字包装，但核验模型输出了DSML伪工具调用文本，未返回合格JSON；没有执行该文本。运行时保留626字D0，入口未扩展，记录为HOLD。
3. D0事实纠错仍为HOLD；下一步先验证独立的来源关系核验，不能因模型局部改对就放开关系保护。
4. 同稿参与目前只实现Claude的宿主原始会话路径，最多8回合、4MB、4万字符用户要求；缺读凭据、显式任务切换、管理清理请求或不明确同稿关系时不恢复。其他宿主没有迁移新接续能力的在线证据。
5. 本轮证明特定路径改善，不能据小样本给出98%或其他总体可靠性指标。

所有失败、中间候选和旧审查结果保留原文。归档仅保存需要的正文/调用/协议摘录及原stream hash，剔除HOME、登录目录和thinking；完整原始流留在output，不进入产品包。
