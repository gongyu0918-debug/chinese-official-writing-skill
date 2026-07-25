# 1.5.24 发布证据

## 范围

1.5.24 以 `v1.5.23=1bf33384cc3d2ff9a17da16fcd8f1936b43c253b` 为固定产品基线，只合入已经独立验证通过的纪要与报告叶子减负：

- 完整会议纪要从通用文种合集中直达 `references/genre-playbook-minutes.md`；
- 完整报告直达精简后的 `references/genre-checklist-report.md`；
- 同题要求同时形成纪要和报告时，按需组合上述两条叶子；
- 信息选择、事实边界、文种功能、用户模板、篇幅预算、复核顺序、脚本、Hook、FSM、输出模式和回退链保持不变。

产品提交为 `da576f4`、`d2d2960`，整合与风险收口证据提交为 `6887645` 至 `9d6f451`。原始预注册、运行映射、匿名稿件、独立盲审与剩余风险见：

- `release-1.5.24-relief-integration-real-ab-preregister-20260724.md`
- `release-1.5.24-relief-integration-result-20260724.md`
- `release-1.5.24-relief-risk-closeout-20260724.md`

## 可复核净收益

按既有路由实际选择的入口与 reference 统计：

| 路径 | 1.5.23 | 1.5.24 | 减少 |
| --- | ---: | ---: | ---: |
| 完整纪要 | 14054 | 11351 | 2703（19.23%） |
| 完整报告 | 14054 | 11569 | 2485（17.68%） |
| 同题纪要与报告 | 14054 | 12552 | 1502（10.69%） |

这项收益来自把命中文种已经需要的规则迁入专用叶子，不通过删除事实、缩短正文或降低复核要求换取。

## 真实写稿

Candidate 与固定 1.5.23 使用相同模型、thinking 和逐字一致原始任务，各取首个技术有效输出；writer、硬核验和匿名盲审相互独立，不补抽、不二次修订。

- 纪要叶子：两组真实 A/B 为 Candidate 1 胜、1 难分；
- 报告叶子：两组真实 A/B 均为难分；
- 纪要与报告同题双成果：一组真实 A/B 为难分。

所有 Candidate 均通过事实、数字、日期、主体、状态、文种、格式、输出模式与 P0 检查，未出现 Candidate 独有硬回退。这里的语言胜负只说明有限样本中的直接使用成本；发布依据是确定性减载、规则保真和未观察到功能回退的组合证据。

## 工程验证

发布候选已完成：

- 全量 unittest：368/368；
- Promptfoo smoke：20/20，0 failure，0 error；
- 固定 1.5.23 确定性消融：Candidate 108/108，Baseline 101/108；Baseline 仅未满足本版新增的纪要、报告叶子路由断言；
- canonical quick validate：通过；
- canonical 与五套发行镜像一致性、reference 图和清洁包检查：通过；
- `git diff --check`：通过；
- 清洁发行内容的可移植清单哈希：`197f4eccfe35e26664e75611aa17a791414c4ccbb794e4cb7da4240ddb72f753`。

版本面更新后已按同一入口复跑。沙箱内首次运行时，149 项测试因 Windows 用户临时目录 ACL 报错，Promptfoo 也因 Node 无权启动系统 Python 产生 20 项 error；在获批系统权限下保持同一代码、同一测试入口原样复跑后，分别为 368/368 和 20/20。两次初始失败只记作运行环境噪声，不改写成产品失败或通过。

## 平台状态

发布前只读核验：

- GitHub `origin/main=e97567724dbac00aa7bc77ad2758a2698c433702`，远端尚无 `v1.5.24`；
- ClawHub 公开 latest 和 tags 均为 `1.5.23`，moderation 为 `clean`；
- skillhub.cn 公开状态和当前授权仍需在正式提交前由平台 CLI 重新核验。

本节将在正式发布后补录 GitHub tag/Release、ClawHub 与 skillhub.cn 的独立提交回执。平台公开传播和审核状态分别记录，不用发布回执推断异步字段。
