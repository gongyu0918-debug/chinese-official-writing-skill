# 新闻声明级核验 R3 原子结果

日期：2026-08-22。固定基线为本地 `main@4da2423b45f8485f2da2b0017952cc0225c76851`，候选分支为 `codex/v1612-wr011-source-identity-r3`。本轮只改新闻消息叶中的一个来源边界，不增加 Hook、独立矩阵叶或路由胶水；未推送、未发布。

## 原子边界

目标是修复上一轮的三个硬回退：

1. 来源名称与发布载体照录材料，不凭名称判定行政机关、事业单位、主管单位、技术支撑单位或自建机构序位；
2. 来源身份与数据、文件的原始出处分开，原始出处待核不等于已知媒体或机构的身份待核；
3. 材料限定核验范围时，结论只写到“所给来源未提供”，不外推成“截至发稿未见”或有关单位尚未发布。

不同截止日、统计范围、接入/覆盖口径和开放数量的既有边界保持不变。

## 真实写稿方法

全部样本在 Codex Desktop 独立任务中完成，不使用自建 harness、不启用 Hook、不用电脑控制。五条实际模型路线均按最大推理档运行：

- `gpt-5.6-luna`
- `opencode-go/deepseek-v4-flash`
- `ollama-cloud/deepseek-v4-flash:0731`
- `minimax-cn/MiniMax-M3`
- `alibaba-token-plan-2/deepseek-v4-flash-0731`

评价只看稿件质量；系统错误、截断或只输出检索进度单列为技术无效，不算质量通过。

## R3a：先拆来源身份与原始出处

五路基线、五路候选各写一题三冲突来源矩阵与安全正文。任务 ID：

| 路线 | 基线 | 候选 |
| --- | --- | --- |
| Luna | `01a02606-c186-76f3-bfbb-5fa5e55a6c1c` | `01a02606-e424-74a1-b923-550a1a560850` |
| OpenCode Go | `01a02606-c8ee-7f61-baf2-b65e565537d1` | `01a02606-e972-7d93-a431-a9d1898e231d` |
| Ollama Cloud | `01a02606-d0c8-7043-a9f7-011895833477` | `01a02606-f834-7ca3-8088-791a25c91e06` |
| MiniMax | `01a02606-dac8-7693-a1d5-74085f626d25` | `01a02607-036f-7e10-8a52-68714cfaf678` |
| Alibaba Token Plan 2 | `01a02606-e937-70a2-acd9-113fbac92f39` | `01a02607-0f33-7930-9bc4-b4f113aaa996` |

候选已能分开来源身份与数据出处，但部分稿件仍凭机构名称补写性质；OpenCode 一稿截断，MiniMax 一稿增加正文前旁白。没有以局部改善判通过，而是把候选继续收窄为“名称＋载体事实”。

## R3b：只照录名称和载体

改用养老服务平台三冲突来源题，再做五路基线、五路候选 A/B。任务 ID：

| 路线 | 基线 | 候选 |
| --- | --- | --- |
| Luna | `01a02616-65fc-7d23-a7e9-c66bd5fabd48` | `01a02616-8544-7171-85f1-f3fea397ae7a` |
| OpenCode Go | `01a02616-6de8-7fd0-8265-3474928a36fb` | `01a02616-8de9-7d00-aa85-399438fb8697` |
| Ollama Cloud | `01a02616-752f-79e3-81d8-12e8f6acbc36` | `01a02616-9459-7712-a234-d1a64ab9a569` |
| MiniMax | `01a02616-7cba-7492-b0c9-f0c75fec0718` | `01a02616-9fd0-7870-a589-58ad39de0dc7` |
| Alibaba Token Plan 2 | `01a02616-85a1-78e2-8bc7-460dbb2ff1ef` | `01a02616-ab44-7701-ad41-dfe9c4e98036` |

五份候选均未再凭名称补机构性质，目标边界成立。Ollama 基线把冲突数字写成标题中的既成成效，并补写材料外时段和流程，候选没有这些问题。候选 OpenCode 另出现“截至发稿未见正式书面材料”等限定来源外推，因此继续拆出第三个原子，不把 R3b 直接合入。

## R3c：限定来源结论闭合

停车服务平台题固定三条来源：官网通报称截至2026年5月接入248个，电视采访称超过300个但无截止日，媒体报道写300个和缩短22%但原始出处不明。只跑修正后的五路候选：

| 路线 | 任务 ID | 目标结果 |
| --- | --- | --- |
| Luna | `01a0261b-7e8f-74a3-9e96-e7bfce134b03` | PASS |
| OpenCode Go | `01a0261b-7ea8-77f1-8570-0e3c77c6e27c` | PASS |
| Ollama Cloud | `01a0261b-7ebe-7493-b763-c80883f22904` | PASS，正文有一处“有关单位的单位”重复，记文面 WARN |
| MiniMax | `01a0261b-7e79-7b71-9b4f-481226284ff9` | PASS |
| Alibaba Token Plan 2 | `01a0261b-7eae-7b80-95f2-1079b7565848` | PASS |

五份稿件均完成矩阵和安全正文，均只照录来源名称及“官网发布、接受电视采访、媒体报道”等载体事实；没有补机构性质、没有把原始出处待核写成来源身份待核、没有按来源数量选边，也没有写“截至发稿未见”或把300个、22%升级为已核实事实。Ollama 的单处词语重复不改变来源、数字、状态或交付范围，作为自然度风险保留。

## 确定性验证

- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 第一次运行 `python -B -m unittest maintenance.tests.test_promptfoo_eval.PromptfooProviderTests maintenance.tests.test_skill_boundary`：151项中148项通过，3项因普通兼容包镜像仍是旧新闻叶失败；未写成通过。
- 运行 `python -B maintenance/tools/sync_adapters.py --help` 时，该脚本不解析参数而执行了既有同步流程；实际 diff 仅同步四套普通兼容包中的同一新闻叶，没有引入其他文件变化。
- 镜像同步后重跑同一 unittest：151/151通过。
- 累计5个提交后的轻量 review：固定 `main@4da2423b` 比较，产品 diff 只有 canonical 新闻叶新增1条及四套逐字镜像；R3a、R3b 的真实失败与 R3c 的逐项收窄构成直接消融，没有夹带独立叶、路由或 Hook。
- 合并前 `python -B -m unittest discover -s maintenance/tests`：640/640通过。
- `git diff --check`：通过。

## 结论

`WR-011` 的目标风险已经经过“失败—拆分—再写稿”闭合。最小产品改动为新闻消息叶的一条复合边界及四套普通镜像；不新增 Hook、矩阵模板、来源等级表或工程门。候选可合入本地 `main`，但本轮不推送、不发布。
