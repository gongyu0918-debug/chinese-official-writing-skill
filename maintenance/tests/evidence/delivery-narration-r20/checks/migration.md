# 交付叙述 R20 工程测试迁移

仅修改 `maintenance/tests/test_skill_boundary.py` 与 `maintenance/tests/test_reference_rewrite_contract.py`。开发分支为 `codex/reference-rewrite-20260912`，开始时HEAD为 `b511274ddd5b46a4481a10b44f5f9a4805a41a4d`。产品两页及五份镜像已由父任务同步；本代理未修改产品、镜像或其他测试，未commit，交父任务复核提交。

## 迁移责任

| 旧断言所在测试 | 迁移后仍检查的责任 |
| --- | --- |
| canonical_skill_declares_positive_trigger_boundary | description覆盖中文公文、事务性材料、新闻稿件及起草/改写/压缩/润色/审校/文种核对/去口语化/降AI味/Word能力；保留代表文种与事务触发，不再强求“正式文本”旧词；选路后进入共性四步 |
| delivery_scope_rule_is_naturalized_across_current_skill_copies | 将旧单句拆为四组禁止内容，逐一核验；检查整条交付消息的过程说明边界，保留各镜像一致性、业务适用声明及文后提示例外 |
| drafting_rules_are_split_for_prompt_following | 保留任务/用途/材料/形式与六类任务，分节提取不依赖已不存在的“路由主线”；主叶选定后按任务加读，后接共性四步 |
| second_revision_fact_mapping_has_one_complete_entry_rule | 最新材料/旧稿溯源/改动范围和未解决事项继续保留；旧“路由、工具过程与自评”整句改为共性交付段的语义检查 |
| reference_loading_table_keeps_progressive_disclosure | 每份独立稿件选一个主叶、共性能力按需加读、再进入共性写作与交付步骤 |
| light_route_is_terminal_until_an_explicit_escalation_condition | 更名为 common_workflow_keeps_local_scope_and_rechecks；仍检查局部/关联范围、实质修改复扫、篇幅变动复测及审后完整改稿；不复活单独短长入口 |
| revision_workflow_forbids_new_unprovided_facts | 有据分析与具体事实边界不变；整条交付消息的过程内留责任转向当前交付段检查 |

reference_rewrite_contract 中不再以 writing-rules 链接第一次出现的位置代表流程；改为明确提取选文种段、写作步骤段。首页四步须与共性页四标题一致，顺序为材料与分析→成稿与篇幅→复核→交付，冲突选路必须在主叶前处理。首页的字数脚本、文稿脚本及用法页必须实际可达；共性复核段须对所有成稿、改后稿和审核任务要求读取抗AI页，且在文稿扫描前。

新增一项当前交付责任检查：两个过程说明反例保留在 references/writing-rules.md、不移到首页；整条消息从成果开始；开头、提示和结尾同受过程说明清理要求；原句问题/依据/改法属于审核交付；业务版本、流转、保密、适用范围声明保留；影响使用的缺项、风险、未完成检查和遗留错误仍按规则提示。既有普通短稿与通常稿共用路径的动态检查未删除。

## 实际验证

运行命令：

```text
C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe -X utf8 -B -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_reference_rewrite_contract -v
```

Python 3.13.13；两个模块仅运行一次，共114项，全部通过，0失败、0错误，1.420秒。无失败项，无定向复跑，也未扩跑整仓。完整输出在 `python313-two-modules.log`，命令与退出码在 `test-run.json`。

`git diff --check -- maintenance/tests/test_skill_boundary.py maintenance/tests/test_reference_rewrite_contract.py` 通过；Git仅提示现有CRLF策略下LF将转换为CRLF，没有空白错误。diff为两个测试文件95行新增、15行删除；测试共新增1项，未删除有效责任。

canonical加5镜像的两页共12个文件在测试前后SHA-256一致，清单见 `product-pages-before-tests.json`。静态复核确认没有恢复旧产品句、没有通过删责任求绿。

## 限制

这只证明当前开发内容的相关工程契约与脚本检查通过，不是新的真实模型验证，也不代表对1.x基线过关。既有实测中的状态含糊、过程旁白和漏读抗AI等问题不由本次测试通过消除；保留父任务原始结果和分歧。没有commit，等待父任务复核提交。
