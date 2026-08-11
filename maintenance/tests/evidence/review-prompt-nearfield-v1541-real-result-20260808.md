# Review 近场重复减负真实结果（2026-08-08）

## 结论

保留产品原子。候选只从 `review-checklist.md` 全文复核段删除第二次“免责话术”枚举，前段高风险检测、两处“提示词”、两处重复标题检查、正文外审稿意见和用户明确标识例外均保留。三家写手真实只审复放未见召回回退；SOL 匿名裁决三组均为“难分”，结论为“行为等价，可进入组合验证”。该证据只支持等义去重，不宣称写作质量提升。

产品原提交为 `1599dba12575f34b1a256818dc257c8869c73622`，挑入本地 `main` 后为 `85fb5420`。规范化文本净减 5 个字符，不改变路由、加载条件、复核顺序、输出模式、脚本或回退链。

## 固定题目

- R1：正文末行含免责话术，必须定位并建议删除或移出正文。
- R2：同一句含“用户提示词”“内部推理”“校验门禁/可以直接报送”，三类核心风险必须全部识别。
- R3：必须识别第二个重复标题；用户明确保密标识不得误删；正文外审稿意见不得误判为正文泄露；`9+3=12` 与“尚未形成最终验收结论”必须保留。

每个写手只读取 `AGENTS.md`、`chinese-official-writing/SKILL.md` 和命中分支的 `review-checklist.md`，只审不改，首个最终消息即为样本，不补稿、不重采样。

## 写手与来源

| Provider / 模型 | Baseline 任务 | Candidate 任务 |
| --- | --- | --- |
| Alibaba Token Plan / DeepSeek V4 Flash 0731，max | `019fe1e4-f18f-75d1-b393-3e50cf962282` | `019fe1e4-f293-7152-a999-28065fdc9925` |
| Ollama Cloud / DeepSeek V4 Flash 0731，max | `019fe1e4-f18f-75d1-b393-3e301fc58252` | `019fe1e4-f25c-7f92-8cf8-dec107839280` |
| GPT-5.6 Luna，max | `019fe1e4-f18f-75d1-b393-3e11b9f048d1` | `019fe1e4-f25c-7f92-8cf8-dea0b5d24021` |

六个样本均命中 R1、R2、R3 核心召回，均保留保密标识与未决状态，未把正文外意见当成正文泄露。额外的年份、量词和正式报送结构建议只作次要差异，不参与核心召回胜负。

## SOL 匿名裁决

匿名裁决任务：`019fe1e9-5153-77f1-9043-a5a767565479`，模型 `gpt-5.6-sol`，`max`。

三组匿名配对的 X、Y 在 R1—R3 均为 PASS；三组均“难分”，均为“无独有硬回退”。决定性证据是：免责话术仍被召回，提示词/隐藏推理/门禁三类风险均被召回，重复标题仍被召回，保密标识和正文外意见例外均处理正确。SOL 总结为“行为等价，可进入组合验证”。

## 工程与组合门禁

- 候选分支既有门禁：定向测试 70/70；全量 454/454；Promptfoo smoke 20/20；固定消融 baseline/current 111/111；quick validate、镜像同步、`git diff --check` 通过。
- 挑入本地 `main` 后：`python -m unittest discover -s tests` 为 454/454；`OFFICIAL_WRITING_EVAL_STUB=1 npm run eval:official-writing:smoke` 为 20/20，0 failed、0 errors；quick validate 输出 `Skill is valid!`；`git diff --check` 通过，工作树清洁。
- `python -m unittest` 在本仓库自动发现 0 项，未作为有效测试结果；实际全量命令使用显式 `discover -s tests`。

## 边界

该原子可与后续已验证减负组合，但不能单独宣称质量提升。未推送、未发布。
