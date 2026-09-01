# WR-005b 短稿语义路由去魔法数字结果

## 结论

状态：`R3_SELECTED_ENGINEERING_VERIFIED / READY_FOR_INTEGRATION / NOT_MERGED`。

固定 main 基线为 `69515dbc216e6e057e497fbaa0c1cebb9dac6547`。R3 产品提交为 `c5d0d59bac946705a2d94748a4d2cab8d948db3e`，只修改 canonical `SKILL.md` 与 `references/short-draft-naturalness.md`；随后机械同步五套公开兼容镜像。未改 Hook、description、版本、发行说明或平台包元数据。

原入口中的“不超过300字”“200字左右”来自 v1.6.7 前四个260/280字上限样本的集成启发，并非公开公文规范给出的通用分界。Git 追溯起点为 `8ee9c908 feat(writing): add max-only short-draft naturalness route`。本轮不再用另一组数字替代，而改为：

- 用户明确要求简短正文时直达短稿页；
- 只有篇幅上限时，结合文种、材料密度和交付形态判断；
- 用户明确不要求短稿，或给出明确下限/区间时，先按原任务成稿；
- 压缩不把相对、可能或条件判断收紧为绝对结论。

这套实验按“每次只改一组指令、使用代表性真实任务”的方式递进；方法参考 OpenAI 官方关于精简提示和代表性评测的建议，但官方文档不为任何中文字符阈值背书：<https://developers.openai.com/api/docs/guides/latest-model>。

## 真实写稿

五家均使用 Codex Desktop 可用的低成本 provider，思考强度 `max`：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `alibaba-token-plan/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

总计实际调用100份：固定基线30份、R1 30份、R2 25份、R3 15份；97份技术有效。OpenCode的800—1000字硬区间在基线/R1各一次超时，MiniMax的R2采购申请一次未形成最终稿，均保留为技术失败，不计质量票。

| 轮次 | 单原子 | 真实结果 | 终态 |
| --- | --- | --- | --- |
| R1 | 同时移除固定数字并把“简洁、精炼、紧凑”全部直达短稿页 | 路由读取明显增加，但多家输出Skill过程说明；Alibaba2采购稿另补“部门年度预算”来源 | `REJECTED` |
| R2 | 撤销新增同义词直达，只保留原“简短正文”直达；仅上限按语境判断 | 25份中24份有效，R1过程说明共性回退消失；但Ollama把“接近新机价格”写成“已无维修价值”，且Ollama、MiniMax在明确不要求短稿的长讲话中仍读取短稿页 | `SUPERSEDED_BY_R3` |
| R3 | 只补“不要求短稿”覆盖规则和判断强度保护 | 15/15有效；采购5份均保留相对判断，情况说明5份完整保留事实与未决状态，完整讲话短稿页读取从R2的2/5降为0/5 | `SELECTED` |

R3 实际读取：

| 病例 | 有效稿 | 短稿页读取 | 人工结论 |
| --- | ---: | ---: | --- |
| 简洁采购申请 | 5/5 | 2/5 | 5份均保留8台、3台、7年、6200元、18600元、用途和请批状态；“不经济/经济性较差/不宜继续维修”是由维修费用接近新机价格直接支持的一层合理判断，不按过严标准判失败 |
| 480字上限情况说明 | 5/5 | 3/5 | 5份均保留日期、6/4/2接口、3200/17记录、无数据丢失、切换未决和技术协调组责任 |
| 1500字上限且明确不要求短稿的讲话 | 5/5 | 0/5 | 短稿误路由目标闭环；个别provider仍有正文包装或材料外管理细节，因未读取短稿页且旧基线已有同类波动，保留为`CL-001/WR-020`模型风险，不冒充本原子收益 |

“正文短于提示词”与“稿件功能不足”没有机械等同。本组三个目标分别按申请理由—事项—请批、情况—状态—责任、讲话成绩—问题—下一步判断；合理原因、直接作用、总结和条件性推断均不作失败。失败只认与候选差异直接相关的事实/状态升级、程序责任外扩、文种功能缺失、正文包装或误路由。

## 工程门

直接工程门在真实写稿通过后才启动：

```text
python -m unittest maintenance.tests.test_short_draft_naturalness maintenance.tests.test_skill_boundary maintenance.tests.test_skill_frontmatter_relief_harness
python maintenance/tools/sync_adapters.py
python -m py_compile maintenance/tools/sync_adapters.py maintenance/tests/evidence/short-route-semantic-r1/run_eval.py
python -m json.tool maintenance/tests/evidence/short-route-semantic-r1/config.json
git diff --check
```

首次定向门准确报出五套镜像仍是旧字节；运行既有同步器后85项定向测试通过。完整全量门和最终提交状态见本分支后续提交，不把首次预期镜像失败写成通过。

## 剩余风险

- 语义判断仍由模型完成，不宣称所有“简洁/紧凑”表达都确定读取或不读取短稿页；本轮只证明选定真实任务没有跨provider共同硬回退。
- Alibaba2长讲话连续两轮出现Skill过程引导语；MiniMax讲话仍容易补管理动作。两者未由短稿页触发，分别归入既有`CL-001-NOHK-R2`与长稿模型方差，不在本原子继续堆字。
- 本候选尚未合入 `main`，不属于已发布v1.6.23，也没有发布授权。
