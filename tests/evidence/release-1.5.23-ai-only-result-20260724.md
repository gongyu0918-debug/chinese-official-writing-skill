# 1.5.23 AI 专项独立分型结果（2026-07-24）

## 结论

`PASS`。保留产品提交 `4eacfcef72f4693c040c05913a28e8aa58a1a835`，停止扩大该变量。

本轮从 `v1.5.22=7628619da8e05cc03c86d27d5a95eb8cee8fde05` 独立重建 AI 专项分型：

- 纯 AI 算力、模型服务或 GPU/服务器租赁技术需求直达 `ai-compute-docs.md`；
- AI 与请示、申请、采购、可研、报告、说明、审查、公告、通知、函或方案叠加时，继续加载通用文种 playbook；
- 未带入通知叶、会议纪要叶、报告叶或组合通知兜底。

AI 写作规则只从 `genre-playbooks.md` 迁入既有 AI 专项叶，信息选择、P0、ANTI-AI、普通文种规则、轻量任务卡、复核顺序、输出模式、修改次数、脚本、Hook、FSM 和回退链均未改变。

纯 AI 路径的专项 reference 由 6,695 个规范化字符降至 3,332 个，减少 3,363 个，约 50.2%。把常驻 `SKILL.md` 一并计入，选读上下文由 17,824 个字符降至 13,591 个，减少 4,233 个，约 23.7%。

## 工程验证

- 目标 provider 与边界测试：92 项中首次 91 项通过、1 项因 Windows 临时目录 ACL 拒绝而未进入断言；改用工作树临时目录后仍被同一沙箱 ACL 阻断；获批在沙箱外原样复跑，92/92 通过。
- `python -m unittest discover -s tests`：358/358 通过。
- `npm run eval:official-writing:smoke`：20/20 通过，0 failed，0 errors。
- 固定 `v1.5.22` 确定性消融：baseline 107/108，current 108/108；基线唯一失败是本轮新增的 AI 小节单一来源断言。
- `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- canonical 与五套发行镜像一致，AI 小节只保留一份，reference 图与路由真值由全量测试覆盖。
- `git diff --check`：通过，仅有既有 CRLF 转换预警。

## 真实 A/B

固定对象：

- Candidate：`4eacfcef72f4693c040c05913a28e8aa58a1a835`
- Baseline：`7628619da8e05cc03c86d27d5a95eb8cee8fde05`
- writer 编排配置：`gpt-5.6-sol / ultra`
- 三题使用预注册的逐字一致自然任务，各侧由一个独立 writer 按 T1—T3 顺序生成首个技术有效输出，不补抽、不二次修订、不联网。

writer 子任务内部未暴露更细部署标识和 reasoning 字段，故其自存 provenance 将两项写为 unavailable；模型与档位以父级创建任务时的显式配置为准，不把 writer 自报改写成独立运行日志。

Candidate 实际读取：

- T1：`SKILL.md`、`information-selection.md`、`ai-compute-docs.md`、`final-review-layers.md`、`proofreading-checklist.md`；
- T2：在上项基础上读取采购公告 playbook、`handling-elements.md` 和采购公告检查叶；
- T3：在上项基础上读取可研 playbook 与可研、AI 算力论证链。

Baseline 三题均读入通用 `genre-playbooks.md`，并按任务继续读取 AI 专项和复核资料。两侧写稿目录物理分离，均未读取对方稿件、历史 evidence 或其他候选。

独立 hard verifier 结果：

| 任务 | Candidate | Baseline | Candidate 独有硬回退 |
| --- | --- | --- | --- |
| T1 模型推理服务技术需求 | PASS | PASS | 无 |
| T2 GPU 算力租赁服务采购公告 | PASS | PASS | 无 |
| T3 模型服务平台建设可行性研究报告 | PASS | WARN | 无 |

Baseline T3 的 WARN 来自“持续的模型调用需求”“为高峰时段提供统一承载”“建设期、投资估算和资金来源已经确定”等材料外强化。Candidate 三题均未发现事实、数字、日期、主体、责任、方案状态、文种、格式、输出模式、P0、材料外程序或承诺回退。

匿名映射在 judge 锁定结果后还原：

- T1：A=Candidate，B=Baseline，盲审难分；
- T2：A=Baseline，B=Candidate，盲审 B 胜，即 Candidate 胜；
- T3：A=Candidate，B=Baseline，盲审 A 胜，即 Candidate 胜。

最终为 Candidate 2 胜、1 平，满足三题均胜或难分的预注册门。

## 原件

写稿、provenance、硬检查和匿名锁定报告保存在忽略目录：

`output/release-1.5.23-ai-only-real-ab-20260724/`

SHA-256：

- T1 Candidate：`0E048075940571FBEA5AB8C1781E62695B044BCAF71C6C9413FAE3551E067F9A`
- T1 Baseline：`B1991D3E850BE227B5D10289C7683B16E045F2443779E5203CC2E320EC8929D3`
- T2 Candidate：`E1F84FD146DCC89B628E202F2DEF57BC31E4C1FC48338B91EA7E436D53CD18C9`
- T2 Baseline：`B413DCDBCCD8417E129B964914EB4A31052EED16B49E9DD17D0EB157F886950D`
- T3 Candidate：`2B1A94F564293FF0EE97AC48817E7887CA85698B8F9D14793646DE735AC1B836`
- T3 Baseline：`E163E61434A61983E02B1A019A52840AAE3433C0EFB5C05936138867FFCC7921`
- 匿名盲审锁定报告：`48878D3B76A54601AF0A381A43BEDA70E663830BB367282927D3AF25585EA620`

## 剩余风险

- 三题只覆盖纯技术需求、采购公告和可研报告，不证明全部 AI 文种、全部自然表达变体或跨模型结果。
- 普通文种叠加依赖有限标记集合；新增未覆盖表达时应先登记路由用例，不按单篇稿件追加写作禁令。
- 本轮证明正常样本中减载不劣并取得正向收益，不等于 P0 概率归零。
- 版本号、主线合并、tag、推送和平台发布尚未执行。
