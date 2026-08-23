# WR-019c-R3 必要英文与标准译名结果

## 结论

`PASS_CANDIDATE_ELIGIBLE`。产品候选只增加：

1. 通用英文边界：必要英文、产品名、型号和缩写不是 AI 味；未知内部代号不展开；英文口号只有无名称/指标/引用功能且没有事实增量时才按材料压实。
2. AI 算力叶的四个已核准常见映射：GPU、API、SLA、PUE；不扩建通用术语词典。

canonical 与四套普通镜像同步；不改 description、lint、Hook 或默认联网。

## 原子迭代

R2 只给原则、不提供核准译名。Luna baseline 与 candidate 都能：

- 保留 `ZQX-7` 和 `DeepSeek-R1` 大小写；
- 保持两轮测试、3字段待确认和上线未决；
- 删除 `internal users、end-to-end、one-stop、quick win、best practice` 空壳，只写已给三个线上环节；
- 保留必要的 AI、API、Token。

因此通用原则没有目标增益。真实缺口是两臂都把 `Power Usage Effectiveness` 写成“电能使用效率”，而工信部正式文本使用“数据中心电能利用效率”；API 也没有采用国家标准/行业材料常见的“应用编程接口”。R3 只补核准映射，不增加更多抽象规则。

## 官方依据

- [工信部等《算力基础设施高质量发展行动计划》](https://www.gov.cn/zhengce/zhengceku/202310/P020231009520949915888.pdf)：`数据中心电能利用效率（Power Usage Effectiveness，PUE）`。
- [国家标准项目《信息技术 中文Linux应用编程接口（API）》](https://std.samr.gov.cn/gb/search/gbDetailed?id=04C21BD6C38DA346E06397BE0A0A30A4)：使用“应用编程接口（API）”。
- [民航行业《机场数据基础设施技术指南》](https://www.caac.gov.cn/PHONE/XXGK_17/XXGK/BZGF/HYBZ/202112/P020211201360485870262.pdf)：列出 `API 应用程序接口` 与 `SLA 服务级别协议`，说明具体标准可有正式变体，用户指定标准优先。
- [国家标准计划《半导体集成电路 图形处理器（GPU）》](https://std.samr.gov.cn/gb/search/gbDetailed?id=14CAA43B48255CA1E06397BE0A0A2477)：使用“图形处理器（GPU）”。

产品采用更贴近本题 AI 算力/云服务语境的 `应用编程接口`、`服务级别协议`；用户材料或适用标准采用其他正式译名时仍以其为准。

## 两模型真实写稿

| 模型 | Baseline Y1 | Candidate Y1 | Y2 未知代号控制 |
| --- | --- | --- | --- |
| Luna high | PUE=`电能使用效率`，API=`应用程序接口` | 四项全部使用核准映射 | `ZQX-7` 未展开，DeepSeek-R1/API、两轮、3字段和上线未决完整 |
| Terra high | PUE=`电能使用效率`，API=`应用程序编程接口` | 四项全部使用核准映射 | 同上，无状态或大小写回退 |

两条 candidate 都把 `API并发数、SLA具体数值、PUE目标值、Token总量` 保持为未决，没有补阈值、性能成效或采购决定。Terra 把“尚未确定”改为“待确认”，仍为同强度未决状态；不计升级。

## 产品位置

- `anti-ai-patterns.md`：只写通用保留/省略边界，并把 AI 算力少量译名路由到专项叶。
- `ai-compute-docs.md`：四项映射放在“写作定位”之后，只有明确 AI 算力、云服务、GPU/服务器等任务才读取。

## 验证

- `python -m unittest maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_ai_compute_detail_is_loaded_from_specialty_reference maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_v148_anti_ai_borrowing_stays_soft_and_official maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_packaged_resource_mirrors_match_canonical_bytes`：3项通过。
- `python -m unittest maintenance.tests.test_repository_reachability`：7项通过。
- canonical 与四套普通镜像的 `anti-ai-patterns.md`、`ai-compute-docs.md` 各自 SHA-256 唯一值均为1。
- `git diff --check`：通过。

## 剩余风险

不同国家标准、行业标准和单位规范可能采用“服务等级协议/服务级别协议”“应用程序接口/应用编程接口”等正式变体。本规则明确用户材料和适用标准优先，不能用四项默认映射覆盖用户指定标准；未列术语不凭类推生成译名，必要时按用户允许的联网边界核验。
