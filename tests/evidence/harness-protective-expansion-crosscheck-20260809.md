# 保护性外扩跨 Harness 旁证

日期：2026-08-09  
Skill 基线：`main=424e262b6a512fcf2e7fd548fceacf8e7b116d5d`

## 目的与边界

本检查只估计 Harness 对保护性外扩的影响程度，不设计品牌专属 Prompt，也不以 Harness 配置修复代替 Skill 产品修复。未抓取请求包，未探查 Codex 私有系统提示词；公开侧只读取 OpenCode、Qwen Code 的官方文档与开源仓库。

两道固定任务分别为自助设备试用阶段报告和预约接口异常报告。模型统一为 DeepSeek V4 Flash 0731，provider 分别为 Alibaba Token Plan 与 Ollama Cloud；事实包、输出要求和当前 main Skill 相同。重点检查材料明确未决状态是否保留，以及是否新增“评估、扩大配置、研究处置、另行汇总、不能据此”等材料外结论或动作。

## Harness 与加载事实

- Codex：项目任务自动匹配 Skill；使用当前精简后的同一 `AGENTS.md`。
- OpenCode 1.18.15：官方 CLI 临时执行，走本机 OpenCodex 兼容端点。JSON 轨迹确认四个有效样本均调用项目 `.agents/skills/chinese-official-writing`。OpenCode 会按模型族选择公开 system prompt；DeepSeek 走 `default.txt`。
- Qwen Code 0.21.8：官方 CLI 临时执行，独立临时 `QWEN_HOME`，使用项目 `.qwen/skills/chinese-official-writing`。模型自主调用 Skill 在 Alibaba 路径出现权限/触发漂移，故同 Skill 对照采用 `/chinese-official-writing` 直接调用；Ollama 自主调用成功。

官方实现依据：

- OpenCode model-family prompt 选择：<https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/system.ts>
- OpenCode DeepSeek 使用的默认 prompt：<https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/prompt/default.txt>
- OpenCode 项目 `AGENTS.md` 与规则加载：<https://opencode.ai/docs/rules/>
- OpenCode Skill 发现：<https://opencode.ai/docs/skills>
- Qwen Code 公开 core prompt：<https://github.com/QwenLM/qwen-code/blob/main/packages/core/src/core/prompts.ts>
- Qwen Code 层级上下文与 system prompt 配置：<https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/>
- Qwen Code Skill 调用：<https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/>

## 有效样本

### Codex

- Alibaba 设备题 `019fe257-b207-79d1-87ce-bfd15cdb51e6`：新增“检验服务效能”“为后续评估提供依据”。
- Alibaba 接口题 `019fe257-cfb3-71e0-b910-4c3db6dde59b`：只保留材料明确的原因核查中、人数未统计完整和技术会商。
- Ollama 设备题 `019fe257-b638-7fb2-826d-281f33c03a56`、接口题 `019fe257-fb17-7522-aac9-7213119dd955`：均只保留材料明确状态和动作。
- 既有同 Prompt 复放中，Alibaba、Ollama 均曾在不同臂出现“进一步分析/研究处置”，说明 Codex 内部也有抽样波动。

### OpenCode

- Alibaba 设备题 `ses_01d9e966effeAJ3ApgvMg9xb44`、Ollama 设备题 `ses_01d9e5940ffe6KOX8Tg7pW1e3r`：均只保留材料明确的“共同原因尚未形成结论”和“未形成新增设备采购决定”。
- Alibaba 接口题 `ses_01d9e31cfffeU1n4OyUFVp7sd5`：新增“研究后续处理事项”。
- Ollama 接口题 `ses_01d9da74fffes97kfABBLHGY22`：只保留材料明确状态和会商。

### Qwen Code

- Alibaba 直接 Skill 设备题 `c7a52cba-3c4b-4aa1-a496-022f50e159a5`、接口题 `c38fdbe8-caca-4913-b516-157efbacab6d`：均只保留材料明确状态与动作。
- Ollama 自主 Skill 设备题 `60e8da38-7380-4b0a-873a-6aeb40561ffc`：新增“为评估使用效果”；接口题 `4d6216a2-17f1-4281-b778-a059ff14a16a`：新增“研究处置后续事项”。
- Alibaba 自主 Skill 调用未成功时，设备题 `897b7cd4-cf4e-4fb3-81c8-c7fdab0515bb` 在正文后附“故不推断、不提出……”保护性自证。该样本不能用于同 Skill 质量比较，但证明 Harness 的 Skill 触发和权限层会显著改变输出。

## 判断

1. Harness 有明显影响：同一模型在不同 Harness 中，Skill 是否实际调用、输出是否带 Markdown/过程说明、保护性尾句频率均会变化。
2. 保护性外扩不是 Codex 独有：OpenCode 与 Qwen Code 也出现“会商→研究处置”“试用→评估依据”。Codex 系统风格可能放大严谨否定，但不是唯一根因。
3. Provider/模型波动与 Harness 交互存在：Alibaba 和 Ollama 在同一 Harness 内也会分化，单样本不能归因系统提示词。
4. 产品层不应增加模型品牌或 Harness 专属规则。跨 Harness 旁证只用于识别噪声与加载条件；Skill 修复仍以共同事实边界、实际加载轨迹和原子 A/B 为准。
5. 两个终稿单行候选均已真实失败，说明 P0 触发源更靠前。当前 main 的 `SKILL.md` 在所有 Harness 中都是必读层，其中“判断归纳、事项落点”段落公式与多处否定式未给事项枚举，较 `final-review-layers.md` 单行更值得继续做最小消融。
