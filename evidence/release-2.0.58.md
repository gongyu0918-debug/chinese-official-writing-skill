# 2.0.58 发布证据

日期：2026-11-12。固定上一发行基线：`b2fb1682f1f7a968f2e9c5a806acd29a475d333d`（2.0.57）。发布分支：`codex/cold-review-2.0.57-long-validation`。发布范围为 GitHub、ClawHub 和 skillhub.cn，不包括小红书 Red SkillHub。

## 产品修正

- 指定替换拆分不落盘与敏感材料路径，敏感材料不创建中间原稿、计划或临时新稿；用户明确要求的最终文件仅通过获准的宿主工具生成。
- Python 命令统一 `-B`，避免在技能目录产生字节码缓存。
- 严格国标与用户模板冲突时按页首优先级处理；补充双面印刷、左侧装订和对称页边距规则，条款分别指向 6.2、6.3。
- 一次补搜限制仅约束代理自主检索，用户指定来源数量、交叉核验或深度时按用户范围执行。
- 长文不得以同义复述、定义式解释、重复否定或反复回扣同一数字凑字。
- 年度总结的比较结论必须有前期基线，无基线时不得用扩大、延伸、拓展描述覆盖范围增加。
- 调研报告的不同问卷题目、统计对象和选项分别解释，不把协助需求误写为预约能力。
- 清理 `host lifecycle`、`review-gate` 两处非可执行维护术语。

## 真实写稿与复核

本轮使用 12 类场景、34 份输出及 L11 两份消息交付。L1/L2/L4/L9 四个长文场景均实测达到 3000 字以上；另覆盖采购请示、会议纪要、年度总结、讲话稿、复函、只审不改、指定替换和多来源新闻综述。原始 prompt、映射、计数和 verdict 见 `evidence/long-writing-2.0.58/`。

复测后的 candidate 没有 FAIL。L6 的无基线扩围已解除，L9 的数据含义误读已消除，L5 的分类和语言改善后胜出。L2/L3/L4 候选表现更好；L1、L8、L12 仍有局部重复、材料外细节或来源披露提示。L11 两版指定替换逐字一致。L12 两版均实际打开三个公开来源，candidate 定点修订消除季度归属和过强归因，剩余同源披露轻微 WARN。

这些结果支持发布小修复版本，不表示全部 PASS 或跨模型质量稳定。剩余 WARN 主要为长文局部重复、轻度材料外推和来源披露不完整。

## 确定性验证

- `verify_fix.py`：5 个计数样本全部相等，review-only 与默认模式范围差异得到确认；4 个脚本 AST 通过，引用无缺失，维护术语无残留。
- `count_outputs.py`：独立计算各稿字数、范围和 SHA-256；原始输出与复测输出均保留。
- `git diff --check`、JSON 解析和 canonical 94 文件核对通过。
- 发行包、dry-run、平台回执和本机安装核验在对应步骤完成后追加，未执行的项目不提前记为通过。

## 发布回执

### GitHub

- 发布提交：`bb1260c94cd622bf89db33883d938d8295743792`；annotated tag object：`a09f1f274735d75e3231d7151d4a96601042c953`。
- `main` 已从 `b2fb168` 快进至 `bb1260c`，annotated tag `2.0.58` 已推送；Release 为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.58`，`draft=false`、`prerelease=false`。
- 通用 ZIP 94 文件，SHA-256 `4f70bd6d083b0a7fc0945d7c234682b4539b794f767eb62cd341cefe96891e6e`；ClawHub ZIP 93 文件，`0de2e6b6c5d923f6f3b903dba3071290b1acf7262723b4617198eff6c47409e5`；SkillHub ZIP 94 文件，`23b060daab172593b4b5b71f6576f76264447b9d4e8894997c583dc434490e85`。四个远程附件均实际下载复核，字节哈希与本地一致，`SHA256SUMS.txt` 内容一致。

### ClawHub

- 正式提交一次，返回 `Published chinese-official-writing@2.0.58`，`versionId=k9729jc768ywftygh7byjk2ckh8j2f5y`。
- 首次只读查询公开 latest 仍为 2.0.57，精确 2.0.58 返回 `Version not found`，按异步传播处理，未重复提交。
- 后续公开 latest 与精确版本均已切换为 2.0.58；文件清单 93 个，与 Release 的 ClawHub ZIP 逐文件 SHA-256 一致。`security.status=clean`、`hasWarnings=false`，版本级 `security.sha256hash=facb983add6221636824c3d102e2f3586937673ae4ab5f7df9bbba0aea46bf05`，moderation 为 clean。

### skillhub.cn

- 正式提交一次，返回 `skillId=70149`、`versionId=509410`、94 文件、fingerprint `29c1b9aa7c2afc1e90b34785d05b6332244d5383a791d643e3099fba1fa2d041`、`tags.latest=2.0.58`。
- 提交时 `reviewStatus=pending`、`securityScanStatus=pending`、`contentAuditStatus=pending`。公开搜索首次仍显示 2.0.57，未重复提交。
- 后续公开搜索已切换为 2.0.58。隔离安装共 94 个文件；排除平台补入的 `_meta.json` 后，其余 93 个文件与 Release 的 SkillHub ZIP 逐文件 SHA-256 一致。内部 review、security scan 和 content audit 状态不因公开切换而推定为通过。

### 本机 Codex 安装

- 本地插件源提交：`2b746505c080e58852d1273470dde78b71029b64`。
- `chinese-official-writing@personal` 已重装为 2.0.58，`installed=true`、`enabled=true`。安装缓存 94/94 个 Git blob 和 SHA-256 均与发布提交 `bb1260c` 一致。
- 下一轮对话可使用更新后的 Skill；未向小红书 Red SkillHub 提交。
