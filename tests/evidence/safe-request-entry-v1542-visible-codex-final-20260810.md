# 请示采购候选最终可见 Codex 质量证据

## 结论与口径

本轮只评价候选自身的成稿质量、事实要素和路由形态，不按 A/B 票数作判断。最终裁决为：

- `SHORT REQUEST + MULTI-ITEM ROUTE QUALITY PASS`；
- `RICH LONG ROUTE PASS WITH WARN`；
- `NO P0 LOSS`；
- `ELIGIBLE FOR LOCAL MAIN`。

候选产品固定为 `69b1508722715dddbe25bddcc57c0bb6e97bc036`。Alibaba Token Plan 使用 `alibaba-token-plan/deepseek-v4-flash-0731`，Ollama Cloud 使用 `ollama-cloud/deepseek-v4-flash:0731`，均请求 `reasoning=max`。下列结果按各 Codex 任务的首个可见 final 记录，不把后续改写混入首稿结论。正文 SHA-256 未随用户回传，不作推测；以完整 task ID、用户回传的非空白字符数和逐题检查作为定位与量化依据。

## 修复后 direct visible

| 场景 | provider | Codex task ID | 非空白字符 | 首稿逐题检查 | 证据等级 |
| --- | --- | --- | ---: | --- | --- |
| R2 短软件订阅申请 | Alibaba Token Plan | `019feb6e-ef2d-72a1-9195-4bc227372e98` | 未回传 | 紧凑；12 个月、9,600 元、用途和办公经费全部准确；未补询价、验收或供应商 | 补充证据：无文件工具轨迹 |
| R2 短软件订阅申请 | Ollama Cloud | `019feb6e-ef2d-72a1-9195-4bed35da56de` | 未回传 | 紧凑；全部已给要素准确；未补材料外采购状态 | 补充证据：无文件工具轨迹 |
| R4 多品类采购请示 | Alibaba Token Plan | `019feb6e-ef2d-72a1-9195-4ba08e6d5c29` | 未回传 | 最终正文无读取或交付旁白；显示器、投屏器、安装服务三品项，数量、单价、14,000 元合计、三家报价、供应商尚未确定和到货后验收全部准确 | 主证据：有 HEAD、selector 和 6 条 selected paths 的完整读取过程 |
| R4 多品类采购请示 | Ollama Cloud | `019feb6e-f834-7d41-b5c8-f05a874ce137` | 未回传 | 正文同样通过；三品项、金额、报价、供应商状态和后续验收保留准确 | 补充证据：无文件读取轨迹 |
| R6 稀疏长题包 | Alibaba Token Plan | `019feb6e-f829-7571-80da-5e2a52d90e8a` | 395 | 未达到“约 800 字”；增加泛化合规句，不能据此判长篇路线闭环 | 可见负例 |
| R6 稀疏长题包 | Ollama Cloud | `019feb6e-f829-7571-80da-5e0004210cb4` | 849 | 达到篇幅；已给事实和算术基本正确 | 可见正例 |

R2 两稿共同证明短单项形态没有因近场转读规则而膨胀。R4 两稿共同证明多品类题能产出要素完整正文，其中 Alibaba 的完整读取过程直接确认实际路径为 `SKILL.md`、`information-selection.md`、`genre-playbook-request.md`、`workflow.md`、`handling-elements.md`、`argument-chains.md`，没有读取 `task-route-cards.md`。R6 两稿分化明显，说明该稀疏长题包不适合作为长篇能力的唯一门。

## 冻结候选上下文复放

本轮同样固定候选 `69b1508722715dddbe25bddcc57c0bb6e97bc036`，但上下文前含 shell wrapper 元信息，原样降为次级证据。

| 场景 | provider | Codex task ID | 非空白字符 | 首稿逐题检查 |
| --- | --- | --- | ---: | --- |
| R2 短软件订阅申请 | Alibaba Token Plan | `019feb75-b16a-73c0-a464-bda95c5d6edd` | 未回传 | PASS；紧凑且要素准确 |
| R2 短软件订阅申请 | Ollama Cloud | `019feb75-b3f2-7f21-9024-a4d19b93e37e` | 未回传 | PASS；紧凑且要素准确 |
| R6 稀疏长题包 | Alibaba Token Plan | `019feb75-b7cf-7e91-9c6b-81aa559e86cb` | 716 | 接近 800 字并保留要素；稀疏材料引出推算或泛化，记 WARN |
| R6 稀疏长题包 | Ollama Cloud | `019feb75-b7f5-7740-bfb7-3b9e619af8de` | 723 | 接近 800 字并保留要素；稀疏材料引出推算或泛化，记 WARN |

## clean frozen rich-long control

最终长篇控制使用事实更丰富的任务和干净冻结上下文，作为长篇路线的主要质量门。

| provider | Codex task ID | 非空白字符 | 首稿逐题检查 | 结论 |
| --- | --- | ---: | --- | --- |
| Alibaba Token Plan | `019feb7a-bc7f-7810-8cd5-caba78a08e88` | 766 | 所有分类、进度、预算、余额、责任和节点均保留；没有补造品牌、供应商或报价；把未分类剩余页概括为 A4 | PASS WITH WARN |
| Ollama Cloud | `019feb7a-bcb2-7843-a927-708785bf242d` | 736 | 所有分类、进度、预算、余额、责任和节点均保留；没有补造品牌、供应商或报价；使用“报告如下” | PASS WITH WARN |

两稿均无 P0 事实、算术、状态或输出范围损失。A4 概括和“报告如下”分别保留为轻微表达 WARN，不用模型间票数覆盖候选自身的要素通过结论。

## 证据保留与边界

- 首次外部 CLI 的 `12/12 ENV_INVALID` 继续完整保留在 `safe-request-entry-v1542-single-arm-result-20260810.md`，对应提交 `f382bfaec707a417c7a3f48fa38d231ca108490d`；不把环境失败改写为模型结果，也不删除原始失败链。
- 最终产品范围仍为请求叶近场规则及其既有安全集成。description 未改；short notice 和 closing relocation 均未进入候选。
- 本文件只追加质量证据，不修改产品、评测 selector、路由实现或其他 reference。
- Codex 任务归档状态为 `PENDING_ROOT`，由 root 在证据提交后另行执行并核验；本提交不宣称已归档。
