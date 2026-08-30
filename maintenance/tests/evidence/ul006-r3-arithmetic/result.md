# `UL-006-R3-ARITHMETIC` 透明比例原子终态

日期：2026-08-30。

终态：`TERMINATED_NO_D1_DELIVERY / ARITHMETIC_INCREMENT_REVERTED / UL006_BASE_UNCHANGED / NOT_MAIN / NOT_V1.6.21`。

## 范围与判定

该原子只研究动态近转写 Hook 在 D1 新增百分比时，能否允许由材料同句、同单位、显式总量关系直接复算的透明比例，同时保留原分子、分母、剩余量和未决状态。它不把比例设为必写项，不允许错误分母、错误舍入、裸小数、丢原数或借比例新增评价。只有 D1 被最终选择并完成 hash 绑定交付才算目标闭环；单测通过、机械层放行或安全回退 D0 都不能冒充成功。

## 确定性原型

候选曾增加以下反控：同一候选分句必须同时有百分号和同单位计数；来源同句必须同时出现分子、分母，并以“中”或总量提示明确分母；分子不大于分母；按候选显示精度使用十进制四舍五入复算；原始数字仍由共享硬锚保护。相关定向测试、共享账本测试和35项 `test_under_length_capability` 均通过。

这些确定性结果只证明关系可以机械复核，不证明真实写稿会形成可交付 D1。

## 五次真实 Codex Stop

模型固定 `alibaba-token-plan-2/deepseek-v4-flash-0731`、推理强度 `max`，使用隔离 Codex CLI 0.144.6 与56文件 under-length companion。

| 轮次 | 真实结果 | 结论 |
| --- | --- | --- |
| R1 原 U1 | 初稿128字、材料104字，已经自然展开；未启动动态事务，且初稿漏“未附” | 未行使比例原子 |
| R2 同材料无标题单段 | 初稿96字但漏“未附”，既有普通 finding 先行，动态能力按设计旁路 | 证明事实完整性优先，不是算术结果 |
| R3 单一总量关系 | D0 71字触发，D1 95字只重复“已完成/仍在进行”，未写比例；语义层拒绝并 hash 绑定交付 D0 | 生命周期安全，比例未行使 |
| R4 增加透明比例提示 | D0 70字触发；D1 157字写出 `823/860≈95.7%`，机械关系接受并进入语义层；同时新增“绝大多数、数量较少、整体进展平稳”等评价和重复状态，verifier 判 FAIL，hash 绑定交付 D0 | 透明比例本身可通过机械层，但整稿无安全 D1 |
| R5 限定单增量 | 初稿自然扩展到87字，完整保留日期、两轮、860/823/37和进行态，动态能力正确不启动 | 安全未行使；题中“两轮联调已全部完成”是对已给“两轮联调已完成”的等义承载，不按状态升级失败 |

R4 的 verifier 把比例增量分类为 `transparent_derivation`，因此这次回退不能写成“95.7%被门禁误杀”；真正失败是同一 D1 叠加了不必要评价，导致整稿未通过。R5 又没有启动，最终仍缺少一次 D1 选择与交付闭环。

## 决定

- 撤回透明比例机械关系、修订提示及其定向单测，产品树恢复到进入本原子前的 `UL-006` 研究基线；普通公开 main 和 v1.6.21 从未包含这些字节。
- 本项不再标记 `HOLD`。终态为 `TERMINATED_NO_D1_DELIVERY`；没有新的自然 D1 反例或更换扩写策略前，不重复 R1—R5。
- `UL-006` 动态近材料过短主候选仍在独立研究分支，透明比例终止不等于动态篇幅整体终止；事实补回、文种功能和其他 provider 仍可按各自原子继续。
- 五轮原始 trace、终稿、fixture、Hook record 与 provider JSON 位于忽略目录 `output/ul006-r3-arithmetic-live*`，未提交模型正文或运行时凭据。

## 实际命令

- `python maintenance/tests/evidence/ul006-r3-arithmetic/run_live.py --prepare|--provider alibaba2|--summarize`
- `python maintenance/tests/evidence/ul006-r3-arithmetic/run_live_r2.py --prepare|--provider alibaba2|--summarize`
- `python maintenance/tests/evidence/ul006-r3-arithmetic/run_live_r3.py --prepare|--provider alibaba2|--summarize`
- `python maintenance/tests/evidence/ul006-r3-arithmetic/run_live_r4.py --prepare|--provider alibaba2|--summarize`
- `python maintenance/tests/evidence/ul006-r3-arithmetic/run_live_r5.py --prepare|--provider alibaba2|--summarize`
- `python -m unittest maintenance.tests.test_under_length_capability -v`（候选时35/35通过）
- `git diff --check 02eacf76..HEAD`
