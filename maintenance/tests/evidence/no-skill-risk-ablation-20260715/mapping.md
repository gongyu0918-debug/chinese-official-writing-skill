# 条件映射

本文件自述在匿名包和首轮盲审完成后补入，但匿名包、映射和结果位于同一 Git 提交，提交历史本身不能证明公开映射的先后顺序。LUNA verifier 保留了 thread 和原始报告；TERRA 组没有完整保留两份交叉判断的原始报告，具体限制见 `../historical-drift-20260715/five-commit-review.md`。

## LUNA

| 匿名稿 | 条件 | 模型 | thinking | thread |
| --- | --- | --- | --- | --- |
| A | 带 Skill，正常渐进路由 | `gpt-5.6-luna` | medium | `019f6460-021c-7f13-bcde-da75d567e335` |
| B | 无 Skill | `gpt-5.6-luna` | medium | `019f645f-dca7-7fc1-a696-1b1fb44c0743` |

盲审模型为 `gpt-5.6-terra` high，thread 为 `019f6463-6d9a-7a52-b084-539066269657`。

## TERRA

| 匿名稿 | 条件 | 模型 | thinking | thread |
| --- | --- | --- | --- | --- |
| A | 无 Skill | `gpt-5.6-terra` | medium | `019f6466-dc7b-7163-85d7-bc90873311cc` |
| B | 带 Skill，正常渐进路由 | `gpt-5.6-terra` | medium | `019f6466-fbe1-78b0-b7f1-f759f1693bb2` |

## 路由消融

LUNA 强制完整相关路由 thread 为 `019f6468-6ac1-7003-992c-aa0fdcd629d6`。该 writer 读取 canonical `SKILL.md`，不使用 `task-route-cards.md`，并强制读取与四题相关的完整工作流、文种、办理要素、论证、语言和复核 references。除路由外，任务正文与正常带 Skill 组一致。
