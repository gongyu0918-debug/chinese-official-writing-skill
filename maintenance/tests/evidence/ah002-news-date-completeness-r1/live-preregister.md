# AH-002 两家便宜模型真实 Hook 生命周期预登记

日期：2026-08-29。

固定产品树为 `ecacc543ba310ac2da1200303a0e5053b5af6ea7`。从当前候选组装一次 Claude Code companion，只启用默认 `delivery_review`；不安装插件、不修改用户配置。使用 Claude Code CLI 2.1.195、隔离配置目录和本机 OpenCodex 网关，思考强度 `max`。

初始 provider 为：

1. `ollama-cloud/deepseek-v4-flash:0731`；
2. `alibaba-token-plan-2/deepseek-v4-flash-0731`。

每家依次运行两份全新活动新闻和一份完整日期控制稿，只运行一次、无外层重试。若不足两家在任一目标题中自然形成“只含月日、不含年份”的完整 D0，则再运行 `opencode-go/deepseek-v4-flash`；达到两家后停止扩样。

目标题只有在同一真实会话中同时满足以下条件才通过：初始 D0 自然漏年；终态回执记录 `source_bound_date.selected=true`；最终正文逐字等于“只把唯一月日替换为原请求完整日期”的机械期望值。合理原因、即时作用和原稿其他表达全部冻结，不另作失败项。

控制题明确要求保留完整日期。控制通过要求初始 D0 已含完整日期、没有 `source_bound_date.selected=true`，且最终正文逐字等于初始 D0。技术有效还要求精确 Skill 已读、`UserPromptSubmit/PostToolUse/Stop` 均实际发生、终态原文已脱敏、模型与 provider 绑定正确。

只有至少两家 provider 各有一份目标题精确修复，且各自控制题逐字不变，才把产品候选记为可合并。技术失败不算稿件失败；目标未自然复现则扩到固定第三家，不无限追加模型或题面。
