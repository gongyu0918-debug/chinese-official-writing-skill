# 1.5.28 发布证据

## 范围

1.5.28 以 `v1.5.27=cfd7bd039e5655ba3e9fe7680206b520d7582072` 为固定
发布基线，只发布两项已经独立验证并合入本地 `main` 的净收益：

1. `prose_lint.py` 职责拆分。原 `scan()` 与 `main()` 的多项职责分别交给
   文本视图、规则编译、正文及正文外扫描、全文聚合、稳定去重、参数解析、
   批量扫描、结果输出和退出码计算等函数；流程阈值改为具名常量，维护注释和
   解释型 docstring 使用中文。规则 ID、正则、CLI 参数、JSON 字段、finding
   内容及顺序、退出码和默认行为不变。
2. Word 复核原子减负。通用 `review-checklist.md` 删除一处与同文件通用交付
   检查及 `format-gbt9704.md` 近场规则重复的 Markdown 清理半句；文号、密级、
   签发人、印章防编造检查保持不变。

培训/信息传达会议纪要轻量路由已在独立分支完成工程验证和四份首稿，但用户在
匿名盲审前要求暂停，故顺延下一轮；可研只审专用叶的定向复验同样顺延。两者
均不进入本版。

## 已有可复核证据

### `prose_lint.py` 职责拆分

- 3536 组固定样本行为等价复放：Candidate 与 1.5.27 finding 完整序列
  0 差异。
- 独立只读审查另取 222 个字符串、复放 3552 组：完整 finding 序列 0 差异。
- 定向回归 65/65、合并态全量回归 390/390。
- 六份发行脚本 Git 内容与运行行为一致。

该项不改变模型写稿 Prompt 或检测结果，因此真实写稿 A/B 不能增加因果证据，
不为形式补生成。

### Word 复核原子减负

- 两组真实 A/B 均实际读取 `review-checklist.md` 和
  `format-gbt9704.md`。
- WM01、WM02 均为 Candidate 小胜；四稿未出现 Candidate 独有的事实、主体、
  状态、文种、格式、输出模式、Markdown 遗漏或 P0 回退。
- 固定基线确定性消融：Baseline 110/110，Candidate 110/110。
- 原子候选全量回归 390/390，Promptfoo 20/20，quick validate 通过。

共同残余风险是两臂都可能把无法验证的事实真实性、主送或审批权限、办理要素
完整性和发文程序确认扩大为 Word 定稿门槛。该问题不是本次删除重复半句造成，
本版不追加 Prompt。

## 1.5.28 发布级验证

版本同步后实际完成：

- `python -m unittest discover -s tests`：390/390 通过；
- `evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：
  Promptfoo 20/20 通过，0 error；
- 固定 1.5.27 确定性消融：Baseline 110/110，Candidate 110/110；
- Skill Creator quick validate：`Skill is valid!`；
- canonical 与 Codex、Agent、Qwen 发行镜像的 28 个共享文件逐文件
  SHA-256 一致；Hermes 仅 `SKILL.md` 存在预期的适配 frontmatter 差异；
- `git diff --check` 通过。

沙箱内首次全量 unittest 受 Python 临时目录 ACL 拒绝，首次 Promptfoo 受
Node 子进程未继承 `PROMPTFOO_PYTHON` 影响，均作为宿主环境噪声记录；在沙箱外
按原测试口径复跑后分别为 390/390 和 20/20，不把首次环境错误记为产品失败或
测试通过。

## 四平台发布边界

- GitHub、ClawHub、skillhub.cn 沿用现有仓库、slug 和 Skill ID。
- 小红书 Red SkillHub 本轮经用户明确恢复更新；沿用既有
  `skill_identifier=chinese-official-writing`，按官方 CLI 的同 identifier
  新版本路径提交 1.5.28，不更换 identifier，不创建第二个 Skill。
- Red 最后可验证成功版本为 1.5.7，平台回执为 `skill_id=8494`、
  `version_id=100041`。1.5.8 至 1.5.10 的提交曾在服务端以
  “Skill ID 已被占用”拒绝，均没有 `submitted` 回执；本轮先做当前账号、
  live 标签和 dry-run 校验，服务端再次拒绝时如实记为未发布，不盲目重传。
- 四个平台分别记录提交、公开 latest、审核或扫描和安装/包哈希；一个平台成功
  不替代另一个平台的回执。

Red SkillHub 更新说明合并 1.5.7 至 1.5.26 的主要演进：事实与信息选择边界、
保护性外扩压制、篇幅与降 AI 味、创作/修改/只审不改输出模式、渐进式路由、
报告/纪要/请示申请/制度办法/实施细则/AI 算力/公开来源核验专项能力，以及
Word、GB/T 9704 和占位符复核。1.5.27 补入普通函轻量路径和括号占位误报
修复；1.5.28 补入少量缺陷修复、Python 检查函数职责拆分和 Word 复核减负。
曾在 1.5.8—1.5.9 出现、后于 1.5.10 迁出的论文入口不写入当前累计能力。

## 发布状态

- 产品发布提交：待生成；
- annotated tag：待创建；
- GitHub Release：待创建；
- ClawHub：待提交；
- skillhub.cn：待提交；
- 小红书 Red SkillHub：待 dry-run 与更新提交。
