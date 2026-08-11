# 当前 1.5.14 Skill 直接 Prompt 对照来源记录

## 创建边界

2026-07-15 创建线程前，将全局可发现的 1.2.18 Skill 原位备份，并把仓库 canonical `chinese-official-writing/` 复制到全局发现目录。安装后 `SKILL.md` SHA-256 为 `85545D10FB503E3DA013B0292BB0310596A279F9FA99A81124528631C2A0811F`，对应版本 1.5.14。

8 个线程均为 projectless、一题一个，`<input>` 只包含与严格无 Skill 组逐字一致的原始任务，不包含 Skill、基线、测试、A/B、盲审或输出标记等控制语。App 自动生成的 `<codex_delegation>` 为传输外壳。两组都运行在共同的 Codex 基础指令和宿主 `AGENTS.md` 外壳中；16 个 writer rollout 的宿主 `AGENTS.md` 文本 SHA-256 均为 `47C370389D2FC51701BCEAC240FF93E933B0ACD484E44D4176395471BF95055F`，组间变量仅为本公文 Skill 是否可发现并被读取。

线程完成后，临时 1.5.14 副本移至忽略目录 `output/strict-current-skill-install-20260715-1540` 留存；原全局 1.2.18 已恢复，恢复后 `SKILL.md` SHA-256 为 `44BDCF85399E0FEBA87A90A82611B9F336A4580075F91919E0DDE7063DEF6E83`。

## 运行日志核验

| 模型 | 任务 | thinking | thread | Prompt 逐字一致 | 当前 Skill 完整读取 |
| --- | --- | --- | --- | --- | --- |
| `gpt-5.6-luna` | T01 | medium | `019f64b6-218f-7de3-a5d1-646aa694d116` | 是 | 1 次 |
| `gpt-5.6-luna` | T02 | medium | `019f64b6-3d7f-7e52-be2d-82a1b24d7455` | 是 | 1 次 |
| `gpt-5.6-luna` | T03 | medium | `019f64b6-55f5-7dc1-9e53-f55e3c694b4d` | 是 | 1 次 |
| `gpt-5.6-luna` | T04 | medium | `019f64b6-719b-71d3-a781-4f490e010cfc` | 是 | 1 次 |
| `gpt-5.6-terra` | T01 | medium | `019f64b6-7a78-7201-90f1-8a1691304bd5` | 是 | 1 次 |
| `gpt-5.6-terra` | T02 | medium | `019f64b6-8b33-7813-b35b-216200f722d1` | 是 | 1 次 |
| `gpt-5.6-terra` | T03 | medium | `019f64b6-a4cc-7b63-bf24-1a8e956222ee` | 是 | 1 次 |
| `gpt-5.6-terra` | T04 | medium | `019f64b6-bf91-7022-805e-11cd78b2b220` | 是 | 1 次 |

每个线程的本机 rollout `turn_context` 均记录对应 model 和 medium effort；每个 rollout 均包含一次 `Get-Content -Raw 'C:\\Users\\admin\\.codex\\skills\\chinese-official-writing\\SKILL.md'`。该路径在 8 个线程运行期间只放置上述哈希的 1.5.14 副本。
