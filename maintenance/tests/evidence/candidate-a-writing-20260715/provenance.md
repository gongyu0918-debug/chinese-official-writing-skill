# 候选 A 自然触发真实写稿来源记录

## 候选与安装边界

- 产品提交：`f184f28fd10cf652d4784de66ad71304c9321525`。
- 候选全局安装 `SKILL.md` SHA-256：`B5AE6B40ECC1298D4357E919DD2EBDFC6ADC80F75BA924FA1BE6F0F76295D7AF`，版本仍为 1.5.14。
- 测试前全局 Skill 为 1.2.18，`SKILL.md` SHA-256：`44BDCF85399E0FEBA87A90A82611B9F336A4580075F91919E0DDE7063DEF6E83`。
- 8 个 writer 完成后，候选副本移入忽略目录 `output/strict-candidate-a-global-installed-20260715-1633`，原 1.2.18 原位恢复；恢复哈希仍为 `44BDCF85399E0FEBA87A90A82611B9F336A4580075F91919E0DDE7063DEF6E83`。

每个 writer 均为 projectless 独立线程，thinking 为 medium。`<input>` 只含 `tests/evidence/no-skill-risk-ablation-20260715/prompts.md` 中对应任务正文；按 LF 统一换行后，8/8 与固定 T01—T04 逐字一致。任务中没有 Skill、基线、测试、A/B、盲审、读取路径或输出标记等控制语。App 自动加入的 `<codex_delegation>` 仅为传输外壳。

候选、原 1.5.14 与无 Skill 三组都运行在同一 Codex 基础指令和宿主 `AGENTS.md` 外壳中。完整外壳文本 SHA-256 为 `47C370389D2FC51701BCEAC240FF93E933B0ACD484E44D4176395471BF95055F`。

## 线程与实际读取

| 模型 | 任务 | thinking | thread | Prompt | 入口 SKILL | reference |
| --- | --- | --- | --- | --- | --- | --- |
| `gpt-5.6-luna` | T01 | medium | `019f64e7-811b-75c0-be00-ef2fcd004f42` | 逐字一致 | 完整读取 1 次 | 0 |
| `gpt-5.6-luna` | T02 | medium | `019f64e7-9d11-7fa0-b97c-26040cc3a273` | 逐字一致 | 完整读取 1 次 | 0 |
| `gpt-5.6-luna` | T03 | medium | `019f64e7-b7d0-79b0-a76b-26e26817b619` | 逐字一致 | 完整读取 1 次 | 0 |
| `gpt-5.6-luna` | T04 | medium | `019f64e7-cb63-7100-b369-98cddb458050` | 逐字一致 | 完整读取 1 次 | 0 |
| `gpt-5.6-terra` | T01 | medium | `019f64e7-e4ed-7b53-a700-129f68ddfa03` | 逐字一致 | 完整读取 1 次 | `workflow`、`genre-playbooks`、`final-review-layers`、`proofreading-checklist` |
| `gpt-5.6-terra` | T02 | medium | `019f64e8-017c-7e72-9f67-42ce3cb52694` | 逐字一致 | 完整读取 1 次 | 0 |
| `gpt-5.6-terra` | T03 | medium | `019f64e8-147c-7db0-9d36-cb439a9170a2` | 逐字一致 | 完整读取 1 次 | 0 |
| `gpt-5.6-terra` | T04 | medium | `019f64e8-1d1d-7041-a346-de88a0fd21fe` | 逐字一致 | 完整读取 1 次 | `task-route-cards`、`genre-playbooks` |

本机 rollout 的 `turn_context` 逐项确认了上述模型和 medium effort。8/8 均读取候选入口，2/8 自然继续读取 reference；因此本轮称为“候选 A 自然入口执行”，不称为 8/8 完整渐进路由。候选 A 的常驻入口规则对 8/8 writer 可见，reference 中的同向修改只对实际加载对应文件的线程可见。

## 原始输出

同目录 8 个 `luna/terra-t01—t04.md` 文件逐字保存各线程的单个 `final_answer`，未把 commentary、测试标签或主上下文改写混入成稿。
