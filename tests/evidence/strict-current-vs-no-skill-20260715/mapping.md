# 严格同模型 A/B 映射

匿名包提交：`86b0f9e`。盲审原文提交：`e74d4d3`。本文件在两者之后首次公开条件映射。

| writer model | 任务 | A | B |
| --- | --- | --- | --- |
| `gpt-5.6-luna` | T01 | skill-1.5.14 | no-skill |
| `gpt-5.6-luna` | T02 | no-skill | skill-1.5.14 |
| `gpt-5.6-luna` | T03 | no-skill | skill-1.5.14 |
| `gpt-5.6-luna` | T04 | skill-1.5.14 | no-skill |
| `gpt-5.6-terra` | T01 | no-skill | skill-1.5.14 |
| `gpt-5.6-terra` | T02 | skill-1.5.14 | no-skill |
| `gpt-5.6-terra` | T03 | skill-1.5.14 | no-skill |
| `gpt-5.6-terra` | T04 | no-skill | skill-1.5.14 |

分配在创建 verifier 前保存在主线程工具状态中；匿名包采用每个模型 2 题 Skill=A、2 题 Skill=B 的平衡位置。4 个 verifier 的输入中没有本映射，也没有 Skill、no-Skill、baseline 或版本条件标签。
