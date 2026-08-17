# v1.6.7 本地发行候选

日期：2026-08-17

状态：`PREPARING_LOCAL_CANDIDATE`。当前只准备本地候选，不代表任何外部平台已经发布。

## 固定对象与范围

- 上一正式 tag：`v1.6.6^{commit}=b49da7f2a5a8ac2327252d29efd66f1d54ccbc35`。
- 候选起点：`main@9a090c7cd3bb1aae12312307bfd87a2f5a315503`。
- 候选分支：`codex/v167-release-candidate`。
- 候选版本：`1.6.7`；上一正式版本仍为 `1.6.6`。
- 本版产品增量只包含短稿自然收束和 Hook/review gate 行为等价拆分。常用语机械化 R1—R6 均为 HOLD，原型只保存在 maintenance evidence，不进入 canonical 或发布包。

## 主要变化

- 对只有上限或没有硬下限的简短正文增加独立自然收束规则，避免套用长报告骨架、同义复述、口号式结尾和正文外包装。
- 明确短稿规则不负责补足硬下限；存在明确字数下限或区间时仍由原写稿流程和可选 under-length 能力分别处理。
- 按行为不变原则拆分 Hook core 与 `review_gate.py` 的历史超长函数，保留原有协议字段、状态、reason、顺序、D0/D1 选择和异常回退。
- 不修改20类事务文体的常用语总表，不引入固定开头、固定结尾或统一三段式。

## 真实写稿依据

- 短稿自然度 R3 共8/8技术有效；独立 SOL max 判候选3胜、基线0胜、难分1，候选四稿事实、状态、篇幅、文种和直接使用成本全部通过。
- 最小接入后，Ollama 报告和 Alibaba 新闻两份真实稿均读取新增短稿页并保持可用。
- Hook 重构后使用 Claude Code 2.1.195、Alibaba DeepSeek V4 Flash 0731 max 完成1次真实 D0 生命周期；插件注册、Skill读取、三类事件、事务、选择和终稿 hash 均闭合。
- 常用语机械化 R1—R6 的真实写稿反复出现事实、篇幅或文种回退，因此明确不进入本版产品。

## 待完成的候选门

- [ ] 版本、README、镜像、OpenClaw 与 SkillHub builder 聚焦测试。
- [ ] canonical 与普通镜像 quick validation、同步幂等和 diff check。
- [ ] GitHub 源码归档与 SkillHub 清洁包的文件集合、版本、许可证、禁入项和 hash 核验。
- [ ] SkillHub 本地 dry-run；不得把 dry-run 当作正式提交。
- [ ] 正式发布前确认本轮获授权的平台表面。

建议的 SkillHub 更新说明：

> 优化短稿自然收束，减少短篇套用长稿骨架、同义复述和正文外包装；重构可选交付 Hook 内部流程，保持原有启用方式与失败回退。

## 未授权动作

当前未推送、未打 tag、未创建 GitHub Release、未上传 SkillHub.cn，也未对 ClawHub、Red SkillHub 或其他平台执行上传、同步、删除、撤回或版本覆盖操作。
