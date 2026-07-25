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

## 包与平台回执

发布前两家商店分别完成 dry-run：

- ClawHub：`status=would-publish`、24 文件、fingerprint `cf1c54b4699aee45b81540042c8350c1d17b2e0f4df0ab925dcf1b04ea0b51b3`；
- skillhub.cn：`dryRun=true`、`slug=chinese-official-writing`、`version=1.5.24`；
- 两个发行面均未带入 `delivery-review-gate.md`、`review_gate.py`、`gate_stop_hook.py`、tests、output、tmp、缓存或 `.pyc`。

正式发布结果：

- GitHub `main=f9d38c9755cf6188df2767dcfbf5bdaf659f1d1c`；annotated tag `v1.5.24` 的 tag object 为 `387f2a006ad6fdffa6a3d0b54a24512342abe708`，解引用同一发布提交；GitHub Release `中文公文写作 1.5.24` 已公开，`draft=false`、`prerelease=false`；
- ClawHub 只正式提交一次，返回 `status=published`、`versionId=k9701pszcev3r776wsjtkqpnwh8b7ssc`、24 文件和 fingerprint `cf1c54b4699aee45b81540042c8350c1d17b2e0f4df0ab925dcf1b04ea0b51b3`。提交回执中的公开 latest 仍为 1.5.23；随后只读查询出现 `No matching routes found`，精确 1.5.24 查询返回传播期 `Version not found`，未重复提交；
- skillhub.cn 只正式提交一次，返回 `ok=true`、`skillId=70149`、`versionId=167050`、24 文件、fingerprint `72b785a16770b8c31255bd810c6456c603566374df905cddd8165a2d084c48de`，`tags.latest=1.5.24`，review、security scan 和 content audit 均为 pending。首次公开 GET 的 `latestVersion` 和版本列表仍停留在 1.5.23，按异步传播记录，不重复提交。

GitHub Release：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.24`。两家商店的提交回执、公开传播和审核状态分别记录，不互相推断。
