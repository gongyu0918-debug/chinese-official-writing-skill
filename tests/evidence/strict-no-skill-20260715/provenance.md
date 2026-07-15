# 严格无 Skill 裸基线来源记录

## 创建边界

2026-07-15 创建线程前，临时把以下两个可发现目录原位改名：

- `C:\Users\admin\.codex\skills\chinese-official-writing`
- `F:\Workspaces\chinese-official-writing-skill\.agents\skills\chinese-official-writing`

8 个线程创建完成后立即恢复，两处 `SKILL.md` 均核对为存在。线程一题一个，任务 `<input>` 只包含原始用户任务；没有加入“无 Skill、基线、测试、不得读取、不要看其他输出、只凭模型能力”等控制语，也没有加入输出分隔标记。App 自动生成的 `<codex_delegation>` 为传输外壳。线程仍运行在 Codex 基础指令和宿主 `AGENTS.md` 外壳中；严格带 Skill 对照使用同一宿主文本。16 个 writer rollout 的宿主 `AGENTS.md` 文本 SHA-256 均为 `47C370389D2FC51701BCEAC240FF93E933B0ACD484E44D4176395471BF95055F`。

逐线程程序比较确认 `<input>` 与 `prompts.md` 对应任务正文 8/8 完全一致；可见 agent message 中 8/8 未出现 `skill/SKILL/技能`。这里的无 Skill 指未加载或发现本项目公文 Skill，不排除模型预训练中已有的通用公文知识。

## 线程

| 模型 | 任务 | thinking | thread | 输入逐字一致 | Skill 提及 |
| --- | --- | --- | --- | --- | --- |
| `gpt-5.6-luna` | T01 | medium | `019f64a9-b723-7421-9baa-800397a9e96b` | 是 | 无 |
| `gpt-5.6-luna` | T02 | medium | `019f64a9-d363-7551-a025-329de1dea07e` | 是 | 无 |
| `gpt-5.6-luna` | T03 | medium | `019f64a9-e689-7ad3-b308-c0f945990ad0` | 是 | 无 |
| `gpt-5.6-luna` | T04 | medium | `019f64a9-f9bb-73f3-8073-145581725c49` | 是 | 无 |
| `gpt-5.6-terra` | T01 | medium | `019f64aa-1416-70c2-9129-70314b0c4edd` | 是 | 无 |
| `gpt-5.6-terra` | T02 | medium | `019f64aa-262f-76a2-8318-989bc347065b` | 是 | 无 |
| `gpt-5.6-terra` | T03 | medium | `019f64aa-412b-79f2-9fdd-65e40aca5896` | 是 | 无 |
| `gpt-5.6-terra` | T04 | medium | `019f64aa-4d16-7bf1-b875-36b85e3f003e` | 是 | 无 |
