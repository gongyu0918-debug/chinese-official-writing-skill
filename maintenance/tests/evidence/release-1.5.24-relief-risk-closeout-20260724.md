# 1.5.24 减负集成剩余风险补测（2026-07-24）

## 对象与结论

- 固定 1.5.23 基线：`e97567724dbac00aa7bc77ad2758a2698c433702`
- 补测前 Candidate：`feb779f1f7c5c2e325b70a63a4e61ea0e317124f`
- 产品变量：纪要规则拆入 `genre-playbook-minutes.md`，报告精确路由进入 `genre-checklist-report.md`
- 本轮没有修改产品 Prompt、路由、reference、脚本或版本号，也没有生成新稿。

剩余风险补测通过。报告兼容副本、组合路由、发行镜像和清洁打包均未发现新增阻断；组合真实 A/B 已恢复原始任务、两侧最终稿、匿名裁决及哈希，可独立重判语言质量。完整运行对称性仍有两个不可补字段：writer 实际接收的加密委托载荷、运行瞬间的 `git rev-parse` 回执。

## 报告兼容副本与路由

`genre-playbooks.md` 的“报告/情况说明”兼容段，与 `genre-checklist-report.md` 对应段排除各自不同的补充读取说明后逐行相等。现有 `test_report_checklist_is_routed_as_an_atomic_leaf` 使用整段 `assertEqual` 锁定，不是关键词近似检查。

报告任务运行时只加载报告叶，不会同时加载通用 playbook。只读路由审计确认：

| 任务 | 起草阶段文种 reference |
| --- | --- |
| 纪要 | `genre-playbook-minutes.md` |
| 报告 | `genre-checklist-report.md` |
| 纪要+报告 | 纪要叶+报告叶 |
| 纯 AI | `ai-compute-docs.md` |
| AI+纪要 | 纪要叶+AI 叶 |
| AI+报告 | 报告叶+AI 叶 |
| 其他普通文种 | `genre-playbooks.md` |
| 稀疏报告、明确未决纪要 | `task-route-cards.md` |

返回顺序稳定且末端有序去重，未发现双载、漏载或顺序漂移。若上游只把“AI 模型服务报告”标成技术文种而未标成报告，provider 会沿用 1.5.23 的兼容回退，加载通用 playbook+AI 叶；该边界由既有测试锁定，不是本轮新增。

实际验证：

- 报告整段等值、纪要叶、报告/纪要/混合/AI 组合路由：`8/8` 通过。
- canonical、发行镜像和引用无环图：`3/3` 通过。
- 独立审计覆盖定向路由、兼容副本和镜像：`19/19` 通过。
- 独立审计运行 `test_skill_boundary + test_promptfoo_eval + test_real_prompt_ablation`：`120/120` 通过；沙箱内两项 `TemporaryDirectory` ACL 错误在沙箱外按原命令复跑通过，记为 Windows 环境噪声。
- `git diff --check`：通过。

## 最终 smoke 原始回执

命令：

```text
C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2
```

沙箱内 Node 无权启动系统 Python，首次运行产生 `20 errors`。在获批权限下按同一命令复跑：

- Promptfoo：`20/20` 通过，`0` failed，`0` errors。
- 10 个 smoke case 的确定性本地 provider/stub judge 裁决：Skill `10`，Baseline `0`，平局 `0`。该结果只证明 smoke 规则和评测入口，不作为真实模型写稿 10:0 结论。
- invalid `0`，needs manual review `0`，judge consistency `1.0`。
- Skill hard rule pass rate `1.0`，missing output `0`。

原始回执保存在忽略目录：

- `output/release-1.5.24-relief-risk-closeout/smoke/official-writing-smoke-results.json`
  - SHA256：`8d2025871f7daf48564ff9312d01325c09f0fe94321d2daa3690c33a1b15e70f`
- `output/release-1.5.24-relief-risk-closeout/smoke/official-writing-smoke-promptfoo.json`
  - SHA256：`b7045e7ec911eaba31c3d718bab8a956e2ed668990f1d3bc8e4d1f8db888aeff`

## 清洁发行预览

使用 `git ls-files chinese-official-writing` 白名单构造未改版本号的内容预览，并排除不进入商店最小包的：

- `references/delivery-review-gate.md`
- `scripts/gate_stop_hook.py`
- `scripts/review_gate.py`

结果：

- 内容文件：`23`；SkillHub 临时 `_meta.json` 尚未生成，ClawHub 的 OpenClaw 发行面另含 README。
- `__pycache__`、`.pyc`、`output/`、`tmp/`：`0`。
- 三个门禁/FSM 专用文件：`0`。
- 预览清单 SHA256：`197f4eccfe35e26664e75611aa17a791414c4ccbb794e4cb7da4240ddb72f753`。计算方法为：相对路径统一使用 `/`，按 Unicode Ordinal 升序排列；每行写成 `<相对路径>\t<小写文件 SHA256>\n`，再对完整 UTF-8 字节串计算 SHA256。

canonical 目录存在测试运行产生的 ignored `__pycache__`/`.pyc`；其数量会随测试变化，不作为发行证据。白名单预览、OpenClaw 镜像和同步脚本均未携带这些缓存。发布时继续使用白名单，不从工作目录递归打包。

## 组合真实 A/B 原始证据

哈希口径：UTF-8、LF、无 BOM、末尾无换行。

### 运行索引

| 角色 | task path | thread id | turn id | 模型 / thinking | 耗时 |
| --- | --- | --- | --- | --- | ---: |
| Candidate writer | `/root/genre_tail_t1_candidate_retry` | `019f919f-372e-7a50-bef0-712bfe535463` | `019f93b3-2a2c-7222-a277-fe36629db24e` | `gpt-5.6-sol / ultra` | 124074 ms |
| Baseline writer | `/root/genre_tail_t1_baseline_retry` | `019f919f-5b1c-76b2-acc9-a36ab6f7d7b4` | `019f93b3-5360-7a13-bd69-03b1c03072a6` | `gpt-5.6-sol / ultra` | 90126 ms |
| Anonymous judge | `/root/ci_relief_blind_judge` | `019f913d-cadc-7e22-a809-992bdc66f81a` | `019f93b5-88aa-7c83-9d7d-1f4b517266e9` | `gpt-5.6-terra / ultra` | 51096 ms |

### 原始任务

- 字符数：319
- UTF-8 字节数：883
- SHA256：`77a60f721f144a7f7a98111b9212ef628b2096455ab2e9474f185d150cc94ab2`

```text
请根据以下材料分别起草一份专题会议纪要和一份试运行情况报告，只输出两份正文，并用空行分隔。2026年7月23日14时30分至15时30分，明川市行政服务中心召开协同办公平台试运行专题会，办公室、信息中心和6个试用科室有关人员参加。会议听取了6月1日至30日试运行情况：86名工作人员共发起任务430项，其中按期完成397项、延期33项；平台可统一查看任务进度，减少线下汇总次数；部分移动端页面加载较慢，3名工作人员反映附件上传失败。试运行期间技术人员完成2次版本更新，附件上传问题在第二次更新后未再收到反映。会议明确，信息中心于8月5日前完成移动端加载优化方案，办公室于8月8日组织一次使用培训。其余单位推广安排结合8月运行情况继续研究。
```

两个 writer rollout 中委托载荷为加密字段，无法从原始 rollout 独立确认实际收到的逐字输入；原始任务来自预注册证据。

### Candidate

实际读取：

- `chinese-official-writing/SKILL.md`
- `references/information-selection.md`
- `references/genre-playbook-minutes.md`
- `references/genre-checklist-report.md`
- `references/final-review-layers.md`
- `references/proofreading-checklist.md`

工作树：`output/release-worktrees/release-1.5.24-relief-integration`。启动、编码、读取、工具错误均为无；输出一组正文，含纪要、报告各一份。

- 字符数：713
- UTF-8 字节数：1907
- SHA256：`9125e2468ff49c7b2900cd18b97bc99af2d41c49e9ded4f6aa63711c9af0a8b7`

```text
协同办公平台试运行专题会议纪要

2026年7月23日14时30分至15时30分，明川市行政服务中心召开协同办公平台试运行专题会，办公室、信息中心和6个试用科室有关人员参加。会议听取了2026年6月1日至30日试运行情况，明确了有关事项。现纪要如下：

一、试运行情况

试运行期间，86名工作人员共发起任务430项，其中按期完成397项、延期33项。平台可统一查看任务进度，减少线下汇总次数。部分移动端页面加载较慢，3名工作人员反映附件上传失败。技术人员完成2次版本更新，附件上传问题在第二次更新后未再收到反映。

二、会议明确事项

信息中心于8月5日前完成移动端加载优化方案。办公室于8月8日组织一次使用培训。

三、未决事项

其余单位推广安排结合8月运行情况继续研究。


协同办公平台试运行情况报告

一、基本情况

2026年6月1日至30日，明川市行政服务中心开展协同办公平台试运行，涉及6个试用科室、86名工作人员，共发起任务430项，其中按期完成397项、延期33项。

二、运行成效

平台可统一查看任务进度，减少了线下汇总次数。

三、存在问题及处理情况

部分移动端页面加载较慢，3名工作人员反映附件上传失败。试运行期间，技术人员完成2次版本更新，附件上传问题在第二次更新后未再收到反映。

四、下一步安排

2026年7月23日14时30分至15时30分，明川市行政服务中心召开协同办公平台试运行专题会，办公室、信息中心和6个试用科室有关人员参加。会议听取了试运行情况，明确由信息中心于8月5日前完成移动端加载优化方案，由办公室于8月8日组织一次使用培训。其余单位推广安排结合8月运行情况继续研究。
```

### Baseline

实际读取：

- `chinese-official-writing/SKILL.md`
- `references/information-selection.md`
- `references/genre-playbooks.md`
- `references/final-review-layers.md`
- `references/proofreading-checklist.md`

工作树：`output/release-worktrees/release-1.5.23-main`。无启动、编码、读取或工具错误；输出一组正文，含纪要、报告各一份。

- 字符数：708
- UTF-8 字节数：1888
- SHA256：`30f9cf8c463014ad46b494fdef995e43931b38e906495b0ae07daf8012299cf7`

```text
明川市行政服务中心协同办公平台试运行专题会议纪要

2026年7月23日14时30分至15时30分，明川市行政服务中心召开协同办公平台试运行专题会，办公室、信息中心和6个试用科室有关人员参加。

一、试运行情况

会议听取了2026年6月1日至30日协同办公平台试运行情况。试运行期间，86名工作人员共发起任务430项，其中按期完成397项、延期33项。平台可统一查看任务进度，减少了线下汇总次数。部分移动端页面加载较慢，3名工作人员反映附件上传失败。技术人员完成2次版本更新，附件上传问题在第二次更新后未再收到反映。

二、会议明确事项

（一）信息中心于8月5日前完成移动端加载优化方案。

（二）办公室于8月8日组织一次使用培训。

三、未决事项

其余单位推广安排结合8月运行情况继续研究。


协同办公平台试运行情况报告

一、基本情况

2026年6月1日至30日，明川市行政服务中心组织6个科室、86名工作人员试用协同办公平台，共发起任务430项，其中按期完成397项、延期33项。

二、试运行成效

平台可统一查看任务进度，减少了线下汇总次数。

三、存在问题及处理情况

部分移动端页面加载较慢，3名工作人员反映附件上传失败。试运行期间，技术人员完成2次版本更新，附件上传问题在第二次更新后未再收到反映。

四、下一步安排

2026年7月23日14时30分至15时30分，明川市行政服务中心召开协同办公平台试运行专题会，办公室、信息中心和6个试用科室有关人员参加。会议明确，信息中心于8月5日前完成移动端加载优化方案，办公室于8月8日组织一次使用培训。其余单位推广安排结合8月运行情况继续研究。
```

### 匿名裁决

映射在裁决后解封：A=`Candidate`，B=`Baseline`。judge 实际接收的匿名委托载荷为加密字段，无法从原始 rollout 独立复原逐字输入；judge 工具错误字段未显式提供，记为 `unavailable`。

- 字符数：403
- UTF-8 字节数：1147
- SHA256：`19f88a2c964eeeecc162e14ee799a043b9751b7e2c0e55b952ffcb3407216b60`

```text
A硬检查：两份正文均齐全并以空行分隔。会议纪要和报告均保留会议时间、主体、办公室、信息中心及6个试用科室参会范围，86人、430/397/33项、平台作用、移动端问题、3人反馈、2次更新及“未再收到反映”的状态；8月5日、8月8日安排和其余单位推广“继续研究”的未决口径均准确。无硬回退。

B硬检查：两份正文均齐全并以空行分隔。上述时间、主体、参会范围、数量、问题、处理状态、两项明确安排及未决推广安排均完整保留；未把优化方案、培训或附件上传问题写成已完成、已解决或已全面推广。无硬回退。

比较结论：平局。两稿均清晰区分会议纪要的会议情况、明确事项和未决事项，与报告的基本情况、成效、问题和下一步安排；均无保护性外扩、重复解释或机械化问题。B的会议明确事项分列更利于扫读，A的报告表述更贴近“试运行”“试用科室”原始口径，优势相抵。

直接修改成本：A＝B。两稿均可直接使用，不存在更难直接使用的一稿。
```

## 剩余边界

现有证据足以独立重判事实、状态、文种区分、语言观感和直接修改成本。以下字段仍为 `unavailable`，不作推断：

- writer 实际接收的逐字委托载荷；
- judge 实际接收的逐字匿名包；
- 三个运行瞬间的完整提交；
- judge 的显式工具错误字段。

任务名含 `retry`，此前尝试的失败原因不能由本组有效 rollout 确认。本证据只引用三个最终有效运行，不引用此前失败尝试。
