# HK-002b 两类原稿事实纠正

当前候选在固定同稿测试中实际交付了8份纠正后的D1，另2份因响应格式问题保留D0并明确记为未解决。只覆盖两类局部问题：明确进行却写成未开展，以及把未定日期写成推进工作的前置条件。全部结果来自五条便宜路线的 Codex CLI/max 调用；未合入 main、安装、推送或发布。

工作基线 `f69534f05a2ae8c2da4f39d35a35497a90d0efff`，分支 `codex/hk002b-source-state-r1`。本次沿用已有材料绑定、单次局部修订、独立核验和唯一选稿/emit；增加共享来源关系接口。SKILL、README、references 和静态 adapters 与基线相同，完整冻结产品89→90文件，新增来源定位模块；没有压缩入口、改核心路由或删专叶。

## 路线与方法

| 路线 | 仓库登记模型 |
| --- | --- |
| OpenCode | `opencode-go/deepseek-v4-flash` |
| Ollama | `ollama-cloud/glm-5.3-flash` |
| Alibaba 1 | `alibaba-token-plan/qwen3.8-flash` |
| Alibaba 2 | `alibaba-token-plan-2/qwen3.8-flash` |
| MiniMax | `minimax-cn/MiniMax-M3` |

全部使用 max，无强度回退。42次CLI调用均完成且未用模型工具；CLI上下文与请求路由一致，未取得上游服务另行返回的模型身份字段。每轮同一材料和D0，五条路线并行；修订和核验使用不同路线。五条是服务路线，含两条同属Qwen系列的独立配置，不称五种独立模型。

初始原型5次调用，每次同样五题，共25个观察；[独立复核](prototype-review.md)区分命中、建议质量、技术形态及争议。核心R1有5次修订批调用和2次核验，R2有10次单稿修订、9次核验、10次最终回显，再加1次真实坏候选的反例核验。原稿来自既有真实报告及明确标注的诊断对照，不是本轮重新写首稿。

本轮是冻结canonical事务的 `detect/prepare/finalize/emit` 加真实CLI响应及新CLI最终回显。未安装新Hook，也未重跑宿主原生Stop生命周期；不能把此结果写成已安装Pro或全部宿主的在线验证。

## 第二轮结果

| 修订路线 | 无据日期前置条件 | 明确进行误写未开展 |
| --- | --- | --- |
| OpenCode | D1通过并精确回显 | D1通过并精确回显 |
| Ollama GLM | D1通过并精确回显 | D1通过并精确回显 |
| Alibaba 1 | D1通过并精确回显 | D1通过并精确回显 |
| Alibaba 2 | D1通过并精确回显 | D1通过并精确回显 |
| MiniMax | 修订响应遗漏target，D0/未解决 | 候选修对；OpenCode核验响应含未转义引号，D0/未解决 |

9份产生的D1经只读独立复核均修对目标错误，未确认新增错误或分析误杀。8份有合法的另一条路线核验PASS并实际交付；1份虽内容修对，但核验JSON不能解析，未获选。10份最终回复与实际选稿均完全一致，包含2份保留D0；精确回显不等于事实通过。

四份条件修订去掉无据等待关系；GLM还明确材料已有的安排已定与时间未定。五份进行态修订保留18/10/8份、反馈日期未定和“核对结果有助于厘清附件归属”。扫描/验收区别、3盒属于30盒、累计覆盖旧数、设备维护影响等分析没有误改。两个正常对照在R2定位时均未触发修订，原型的五路语义判断也均未误报；R2这部分只是确定性路由检查，不增加独立模型质量样本数。

反例直接复用原型Alibaba 1的原样replacement“抽检已按确定的安排先行开展”，仅按旧target机械应用，没有另写坏稿或人工改verdict。GLM核验给出FAIL并指出将安排升级成实际开展，核心保留D0。[原始反例核验](raw/core-r2/negative-real-proposal/calls/ollama/attempt-01/final.txt)的 `source_relation_supported/other_facts_preserved` 两个细字段仍为true，与新增状态错误的理由未完全对齐；总verdict、对应全局检查和 `d0_issue_resolved=false` 已拒收，不将这些true字段解释为纠错成功。

## 保留的失败和边界

- 核心R1中旧P整句与新S条件从句重叠，四份有效条件修订均被旧检查先拒；合并成同一个既有finding后保留旧标签和硬锚。R1两份进行态通过核验，但未做CLI最终回显，交付字段为null，不累计到本轮8份。
- R1 Alibaba 1批响应JSON不完整；GLM、MiniMax在进行态候选补入D0原无的材料日期，被原硬锚拒绝。日期有来源，不能记为编造。本轮未放宽硬锚来通过。
- 只读代码复核发现来源校验曾依赖可丢失的state字段，且普通旧D1恢复被增加依赖。前者改为从绑定输入/修订包重建，后者按receipt已绑定的来源verdict区分，保留普通恢复能力。冻结R1和原始失败都留存，R2才含最终修复。
- 新测试早期有导入路径错误、未命中旧检测的夹具及短夹具触发已有正文坍缩保护。改为已有普通报告夹具后通过，没有修改产品保护阈值。子代理的临时目录权限失败也不记作产品通过。
- “未完成抽检→尚未抽检”结合完整下一步安排仍有解释分歧，撤回早先单句确认，不当作五路漏检。“210盒图像均已保存”的范围疑点是D0既有问题，未作为这次候选新增硬错。
- 当前是窄模式定位，不保证同义改写、隐含集合、主体数量关系、全文事实和篇幅全面覆盖。`full_draft_fact_verified` 恒为false；有据分析不要求逐字出现或固定推理层数。
- 最后只对共享报告补充异常输入处理：模型返回null数组或非字符串ID时仍报告D0/未解决或未知。未改修订、核验和选稿逻辑，未追加模型调用；[30份既有报告重放](post-r2-report-check.json)与R2逐项一致，原R2冻结产品保留原字节。

## 验证和交付接口

`python -m unittest maintenance.tests.test_source_fact_review maintenance.tests.test_source_fact_recovery maintenance.tests.test_review_gate maintenance.tests.test_gate_stop_hook maintenance.tests.test_shared_hard_anchors maintenance.tests.test_review_gate_request_fact_safety maintenance.tests.test_host_gate_adapter -q`：最终代码**299项通过**，原始输出见 [unit.log](unit.log)。R2时的298项保留在[r2-unit.log](r2-unit.log)，新增报告异常边界的28项检查见[report-hardening-unit.log](report-hardening-unit.log)，三者有重叠，不相加。无合并/发布，本轮未重复全量发布门。

`python maintenance/tools/assemble_hook_companion.py --host codex --output output/hk002b-companion-r2`：64文件组装成功；新来源模块能由组装包实际导入、定位一处来源候选，[检查回执](companion-check.json)。fingerprint `244ae3b060693fbca388a982b3d26d1350ffd8d3421c31c8fffe819db70bbda4`；未安装、未启用。

报告异常输入处理后用同一组装命令输出到 `output/hk002b-companion-final`，仍为64文件，最终fingerprint `6391f91d2c570303673037bcb3431ff119dfac2c6a4bc8fe13a6e50d94a647e1`；组装代码和依赖路径未变。

`python C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing`：`Skill is valid!`。相关Python编译通过；维护文档本地链接、1284份原始文件hash与 `git diff --check` 均通过。

共享入口见 [接口规格](../../../specs/hook-source-facts-api.md)。[samples.json](samples.json)提供两个实际PASS并精确回显D1的样本，以及一个保留D0/未解决样本，逐份列出四输入的精确UTF-8路径和SHA-256、原verdict与实际回显；[summary.json](summary.json)从回执和共享报告生成统计。未知KEEP的语义由离线契约测试覆盖，不伪称本轮新增真实模型unknown样本。

`raw/`保留三阶段完整材料、提示、原始响应、回执、事务报告和两轮完整90文件冻结产品；排除CLI home、登录态与工作目录。`.gitattributes`禁用原始证据换行转换，逐文件SHA见 [archive-manifest.json](archive-manifest.json)。可分别运行同目录 `prototype.py`、`run_core.py`、`run_single_core.py` 的已有阶段命令复核；原输出目录受存在检查保护，不覆盖原调用。

Pro只能复用检测/关系包及只读报告，须按自己的四输入和最终选稿重新绑定；MIT的回显记录不能替代Pro交付证据。当前状态为 **两个局部原子有真实纠错交付、候选未合并**，HK-002b全文事实复核继续开放。
