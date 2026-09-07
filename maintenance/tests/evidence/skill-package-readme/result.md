# Skill 包内说明与能力路由集成结果

2026-09-07；分支 `codex/skill-package-readme`，基线 `08dea28b3dae4b9e86d5adb78c694e18eaec5174`。`DOC-001 / DONE / NOT_MERGED / NOT_RELEASED`：包内使用说明与有限问答路由已完成，尚未合入main或发布。

## 范围

- canonical新增46行README，按六个功能分组提供八条提示示例；保留用户指定的“整理一下”“我只想要正文”、免费Skill与Pro页面、MIT署名说明。
- SKILL正文与既有资料表增加能力、适用范围和一般用法的README路由；实际起草、改稿及具体文种写法继续走原任务，Hook问题继续使用原专用入口。description不变。
- Hook README只增加总说明回链。两页使用GitHub绝对链接，普通兼容包不含Hook、SkillHub清洁包改用LICENSE.md时仍能找到说明和许可证。
- 复用现有同步脚本更新五套Skill包；OpenClaw边界测试由禁止包内README改为要求其与canonical逐字节一致，Hook与agent排除保持。未修改任何写稿reference、Hook实现、同步脚本或包装器。

最终canonical在验证工作树中的原始字节SHA-256如下。README与SKILL为LF；Hook README沿用部分CRLF，其Git入库时LF规范化后的SHA-256为 `15d3197e902135d2e7d85d6e834eb6e67d103e57e73ca5542180434ebfa2f94e`。本机 `core.autocrlf=true`，合并后checkout字节可能不同；actual归档使用 `.gitattributes` 的 `-text` 保留原始字节。

| 文件 | SHA-256 |
| --- | --- |
| README.md | `69de332a0a8d128acebad1b2d6a138a29fd87ad8cabc10d6e446419cd8c01654` |
| SKILL.md | `64a414e5ee69eb6161658529e9807460c3c612eeb458bd81925cc2ad6b494e96` |
| hooks/README.md | `46c6ad19952a5aa4b3adfcb52ce34e321647a6a0eeb44295e309f60120b79ca0` |

## 真实任务与结论边界

按[预登记](preregister.md)，[run_real.py](run_real.py)复用main已有的低价模型Harness，使用独立Claude CLI会话，显式指定唯一Skill入口，由模型自主选择Read页面。题面不指定README路径，不运行Hook或联网。共20次调用，18次候选、2次main基线；API有效20次，仅说明调用技术完成，不能当作写稿质量或稳定率。[汇总](actual/summary.json)和[归档清单](actual/manifest.json)保留各轮正文、回执和冻结版本。

- 最终 `delivery` 两路能力问答均实际只读SKILL与总README，未再要求必填表或正文留白。
- `route-r2` 两路Hook问答只读SKILL与hooks/README；两路带“怎么写”的真实短申请仍读取写稿reference，没有误转能力介绍。四份证据实际读取的文件与最终版本逐字节hash相同，可以迁移；这不是重新运行Hook或宿主在线生命周期。
- 早期 `wording/capabilities-minimax-candidate` 未读README并增加必给项、留白建议，确属目标失败，原答复完整保留。R2补入统一资料表并明确适用范围问答后重新实测，未用旧成功覆盖失败。
- 最后两份问答之后，README仅增加用户指定的免费Skill页面链接；[汇总](actual/summary.json)单列这处说明文案差异。未把它冒充模型已读到的字节版本，未改变路由、功能或示例。

真实短申请的写稿质量没有整体通过：R2 DeepSeek仍带正文外说明，MiniMax仍补了白板属性或影响判断；同题main基线也有包装及无据影响句。独立成稿不足以确认这些问题由README路由直接造成，也不能用基线错误抵消候选错误。首稿论证与稿件事实质量继续归 `WR-023b / IN_PROGRESS`；R1—R10研究候选未进入本次产品，DOC-001完成不替代该主线。

## 工程验证

同步前已逐一核准 `sync_adapters.TARGETS` 的五个解析后绝对路径，全部位于本独立worktree的packages目录，排除项均为安全相对路径。真实路由验证完成后才同步新SKILL；此前只同步过README文档。

以下命令使用 `C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe`，cwd为本worktree；命令中的 `python` 指该解释器。

```text
python -B -X utf8 maintenance/tools/sync_adapters.py
python -B -X utf8 -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_skillhub_package_builder maintenance.tests.test_repository_reachability
python -B -X utf8 -m unittest discover -s maintenance/tests -p test_*.py
python -B -X utf8 C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py <Skill目录>
python -B -X utf8 maintenance/tools/build_skillhub_package.py --output F:/Workspaces/chinese-official-writing-skill-worktrees/skill-package-readme/output/skill-package-readme-engineering/skillhub --version 1.6.29
git diff --check
git -c core.whitespace=cr-at-eol diff --cached --check
```

- 相关minimal共107项通过，包含Skill边界、状态账本、清洁包构建及活动Markdown相对链接检查；登记完成后，状态与链接23项再次通过。按合并准入补跑一次仓库全量817项，120.026秒全部通过；所用测试为本地单元、stub或smoke，不新增在线模型调用。README文档早期状态另跑过100项，不作为最终路由证明。
- `git diff --check`通过。首次暂存检查将 `-text` 保护的原始CRLF归档快照标成尾空白；保留证据字节，使用 `git -c core.whitespace=cr-at-eol diff --cached --check` 识别CRLF后通过，不更改产品属性或清洗历史输出。
- quick_validate对canonical及agent-skills、qwen-code、qwenwork、hermes四套通用镜像共五处通过；OpenClaw名称和前置元数据由仓库专项边界测试覆盖。
- 五套镜像README均与canonical逐字节一致；能力路由保留，原Hook精确段落在canonical恰好出现一次、普通镜像已按原规则排除；Hook及OpenClaw的agents/openai.yaml禁入要求保持。
- SkillHub本地清洁包88文件，README逐字节一致，LICENSE.md与根MIT许可证一致；不含extensionless LICENSE、agents/openai.yaml、维护文件、缓存或原始流。此处使用1.6.29仅作现有包装器测试，未调整任何发行版本或上传。
- README标题结构及四个HTTPS链接格式有效；GitHub链接对应文件在当前checkout存在。链接检查不等于远端版本已发布或平台状态验证。
- actual归档清单66项字节数与SHA-256全部匹配，20份调用回执在案，没有原始stream或JSONL进入归档；旧冻结不回写。

本次没有合并main、推送、创建tag或发布。保留写稿质量、自动发现率及未测试宿主的限制，不增加新规则或新工程门补偿这些未完成项。
