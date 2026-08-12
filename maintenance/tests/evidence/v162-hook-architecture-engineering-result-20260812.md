# v1.6.2 Hook 静态架构工程结果

## 绑定

- 固定 v1.6.1 产品基线：`2135fba6e05ee9a3d9c9f931237a9eb01b0cc107`
- 固定 v1.6.2 产品候选：`f40add66dfeb80a7f3e91a6a7b0738b6d41acf28`
- 分支：`codex/v162-package-architecture`
- 本文件只记录工程验证；没有上传、推送、移动 tag、安装或启用宿主插件。

## 结果

- canonical Skill 保留一份 Hook 核心和三套静态适配源；不再跟踪三份完整插件副本。
- 普通 Skill 不自动识别宿主、不生成文件、不安装插件、不修改配置、不联网。用户明确选择宿主并确认文件清单后，维护工具才可在新目录组装自包含 companion；组装结果仍为 `installed=false`、`enabled=false`。
- 当前任务明确说“本次关闭 Hook”“本次不要用 Hook”或“跳过交付门禁”时，门禁只做应用层旁路：不创建事务、不调用门禁、不阻断终稿。普通 Skill、Agent Skills、Qwen Code、Hermes 和 OpenClaw 包均不含 Hook 与 `review_gate.py`，仍可使用 references 和 `prose_lint.py` 独立完成闭环。
- canonical 下全部 reference、script、Hook 源、adapter 和说明均有上游入口或构建接引；`packages/`、`maintenance/` 分别有索引。组装包扫描父目录回指、symlink、单一 manifest 和 Markdown 本地链接。
- 未纳入篇幅补写 Hook。`host-capabilities.json` 与回归测试均锁定 `automatic_expansion=false`、`automatic_compression=false`、`status=not_shipped`。
- 新增代码未出现 80 行以上且决策节点超过 25 的新上帝函数。历史债务仍为 `review_gate.evaluate_candidate` 301 行/115 决策节点、`detect_transaction` 183/32、Hook `handle_stop` 115/48；本轮只登记，不在结构迁移中改写其语义。

## 实际验证

| 验证 | 结果 |
| --- | --- |
| `python -B -m unittest discover -s maintenance/tests -p "test_*.py" -q` | 536/536 通过；结构迁移初次全量运行曾有 8 个旧插件路径错误和 1 个旧 P022 oracle 错误，修复后完整复跑通过。 |
| 固定 v1.6.1/current 确定性消融 | 111/111 对 111/111；首次运行因新 P022 oracle 未给旧基线等价分支而得到 110/111，补充完整等价 oracle 后从空输出目录有效复跑。 |
| `OFFICIAL_WRITING_EVAL_STUB=1 npm.cmd --prefix maintenance run eval:official-writing:smoke` | 20/20 通过，0 failed、0 errors；eval `eval-on6-2026-08-12T07:19:11`。 |
| canonical quick validate | `Skill is valid!`。 |
| `sync_adapters.py` 连续两次 | 两次执行后 `git diff --exit-code` 均通过；普通镜像继续无 Hook。 |
| SkillHub 1.6.2 清洁包预构建 | 48 文件；包含静态 Hook 源和 `LICENSE.md`，不含 `agents/openai.yaml` 与无扩展名 `LICENSE`。未 dry-run、未上传。 |
| Codex companion | 41 文件，fingerprint `2b7fc42f1fa819d9d8f3781da110d3e81192b32f36369396186e8a4968d0052d`；OpenAI plugin validator 通过。 |
| WorkBuddy/CodeBuddy companion | 40 文件，fingerprint `60ec4d681a0dd69ff4c5d4506acb91ca55fd0452be6959cd451657a7d344a917`；本机 WorkBuddy 内置 CodeBuddy validator 返回 `valid: true`。 |
| Claude Code companion | 40 文件，fingerprint `f05a833f7f9d1942d11e523d6ca4774f69aa73f8bbf28ef529ce8e61c7c2345d`；`claude plugin validate --strict` 通过。 |
| `py_compile` | Hook core、两类 adapter、`prose_lint.py`、`review_gate.py`、assembler、builder、sync 共 8 文件通过；缓存定向写入忽略目录。 |
| `git diff --check`、终态 status | 通过；工作树清洁。 |

## 透明失败记录

- 第一次基线 diff 命令在 PowerShell 中把 `$base..$head` 解析错误，只打印 Git usage；后来改为两个独立 commit 参数重新核对。
- 第一次三宿主组装命令使用了 PowerShell 只读变量 `$Host`，在组装前终止；改用 `$hostName` 后三套结果有效。
- 初版 companion 复制的 `hooks/README.md` 含三个在组装包内不存在的 adapter 相对链接；组装器现会改写为插件根说明，并逐一验证全部本地 Markdown 链接。

这些命令层和迁移期错误均未被记作通过，也没有触发宿主安装或外部发布。

## 下一步门槛

工程结果只证明结构、边界和离线调用链。真实写稿非劣、Hook 实际事件使用和相对延迟另按冻结矩阵执行；写稿盲审与 v1.6.0 产品 DIFF 冷审完成前，不把本候选称为可发布版本。
