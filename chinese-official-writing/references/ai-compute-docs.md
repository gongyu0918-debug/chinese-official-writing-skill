# AI Compute Technical Official Documents

Use this reference for AI companies, computing-power service providers, model platforms, GPU/server rental, intelligent computing centers, cloud-vs-local comparison, feasibility reports, procurement plans, leasing service plans, and technical service requirement documents.

## Writing Position

Write for the decision maker. The document should make the purchase or lease reason clear:

- Where computing demand comes from.
- How demand converts into Token, concurrency, storage, bandwidth, model, or GPU/server requirements.
- Why the selected service period, server scale, and service model are appropriate.
- What costs are reduced or stabilized.
- What operational risks are controlled.

Do not write as if explaining AI concepts to beginners. Define terms only when necessary for a nontechnical decision reader.

## Common Document Structures

### Computing power feasibility report

1. Project background and conclusion.
2. Business demand and annual Token/resource demand.
3. Existing use, constrained use, and future growth.
4. Technical route and construction or leasing model.
5. Cost calculation and cloud/external service comparison.
6. Service capability, SLA, concurrency, and operation guarantee.
7. Expected benefits.
8. Data security and compliance.
9. Implementation schedule and acceptance.

### Computing resource procurement or leasing plan

1. Procurement purpose.
2. Service scope.
3. Resource scale and performance requirement.
4. Service period and delivery location.
5. Deployment, scheduling, monitoring, operation, and upgrade service.
6. Price structure and payment arrangement.
7. Acceptance, SLA, fault response, and assessment.
8. Security, data ownership, confidentiality, and audit.

### GPU/server rental technical requirement

1. Required quantity, service period, and resource type.
2. GPU model or equivalent performance.
3. CPU, memory, disk, RAID, network, storage, and bandwidth.
4. Model training, inference, fine-tuning, and multi-tenant isolation needs.
5. Resource scheduling platform, quota management, monitoring, logs, billing, and alerts.
6. Onsite/remote delivery, installation, system environment, driver and dependency management.
7. 7x24 operation support, fault replacement, maintenance window, and SLA.
8. Acceptance tests and reporting materials.

## Demand-Writing Patterns

Use business-driven paragraphs:

`单位年度算力需求主要来自长文审校、内容生成、知识库问答、模型研发测试和多模态处理等场景。上述场景均以长文本处理、多轮交互、批量任务和知识库检索为主要特征，Token 调用量随使用范围扩大持续增加。项目通过集中租赁算力服务，为核心系统提供稳定承载能力，并为高峰并发和后续模型升级预留资源。`

Write demand by unit or scenario when data supports it:

- Current actual Token, calls, users, and peak concurrency.
- Restricted current use and reasons: quota, concurrency control, cost control, pilot scope, or manual review queue.
- Future use: wider users, daily workflow embedding, batch processing, agent workflow, knowledge-base linkage, multimodal tasks.
- Annual demand: measured data plus growth estimate.

Keep units consistent. If the document's logic uses Token, carry the calculation to cost at the end. Use TOPS/TFLOPS only for server carrying capacity, not as a competing cost line.

## Cost and Comparison Patterns

Cost comparison should not rely on model API unit price alone. Include:

- Model/API Token cost.
- Cloud server, database, storage, bandwidth, firewall, gateway, load balancing, logging, cache, and function computing.
- GPU leasing or server rental cost.
- Room, power, network, maintenance, operation, security, monitoring, and support cost.
- SLA and concurrency guarantee value.
- Data security and local deployment value.

Useful paragraph:

`继续采用云端部署的短期支出较轻，但费用随 Token 消耗、模型升级、并发释放和云厂商价格调整持续波动。现阶段账单反映的是受控调用状态，不能代表核心业务全面接入后的三年成本。租赁服务方式将服务器资源、模型部署、训推调度、机房托管、安全防护和运维保障纳入合同管理，有利于锁定服务能力和费用边界，增强三年成本可控性。`

When comparing paths, keep the conclusion readable:

- Cloud path: lower current cash spend, higher growth uncertainty, weaker SLA/concurrency/data control.
- Purchase/self-build path: high upfront investment, longer construction cycle, hardware depreciation, supply and maintenance burden.
- GPU/server rental path: faster resource access, contract-managed price and service, lower operation burden, stronger elasticity than self-build.
- Local service path: better data control, audit, continuity, and unified scheduling.

Do not write the conclusion as "rental is always cheaper." Write which scenario it is cheaper or more certain under.

## Technical Requirement Writing

Use measurable and checkable requirements:

- `单台服务器应提供不少于……张 GPU 或等效算力资源。`
- `应支持模型推理、微调训练、批量任务和多用户并发调用。`
- `应提供统一资源调度、配额管理、调用监控、日志审计和故障告警能力。`
- `应提供不少于……TB 可用存储和不少于……Gbps 网络带宽。`
- `服务期内应完成系统安装、驱动适配、模型环境部署、版本升级和故障处置。`
- `应提供 7x24 运维响应，重大故障应在合同约定时限内恢复或提供替代资源。`
- `验收内容包括资源规格、性能测试、模型服务可用性、并发压测、日志审计、安全配置和运维文档。`

Avoid vague terms such as `先进算力`, `强大平台`, `领先能力`, unless followed by measurable indicators.

## SLA and Operations

SLA is part of the business argument, not an appendix only. Mention:

- Availability.
- Fault response and recovery time.
- Peak concurrency and queue control.
- Resource isolation and priority guarantee.
- Monitoring, logs, monthly reports, and utilization analysis.
- Upgrade, migration, and model version switching.

Useful paragraph:

`项目服务能力不只体现为 Token 单价，还体现在峰值并发、响应时延、故障恢复和业务连续性。长文审校、知识库问答和智能体工作流均存在集中提交、批量处理和重点任务保障需求，若仅按平均调用量配置资源，关键时段容易形成排队和积压。租赁服务应将 SLA、资源优先级、监控报表和故障响应写入合同，保障核心业务稳定运行。`

## Security and Compliance

For publishing, media, education, healthcare, finance, government, and internal enterprise scenarios, state the specific data:

- Manuscripts, copyright materials, review records, internal knowledge bases, user feedback, business rules, training/evaluation data, logs, and prompts.
- Data should be processed in the controlled environment when required.
- Sensitive data should not leave the agreed region or environment.
- Permissions, keys, logs, calls, and model access should be manageable and auditable.

Useful paragraph:

`本地化或省内部署有利于将敏感业务数据控制在约定环境内处理，减少外部传输、留存、二次使用和跨区域流转风险。项目应对模型调用、知识库检索、日志记录、运维访问和数据导出实行统一权限管理，做到访问可控、日志可审、调用可追溯、责任可界定。`

## Review Checks

Before finalizing AI compute documents, check:

- Does every technical term support the purchase or lease decision?
- Are Token, TOPS/TFLOPS, GPU cards, server quantity, bandwidth, storage, and money not mixed without explanation?
- Is the cost comparison based on the same service period and demand assumption?
- Does the document explain current low use if existing usage is constrained?
- Does it show why redundancy is needed for peak load, model upgrades, and agent workflow?
- Are service period, delivery, acceptance, SLA, data ownership, confidentiality, and operation responsibilities stated?
- Are actual figures separated from estimates?
