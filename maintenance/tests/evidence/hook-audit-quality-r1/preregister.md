# 同一真实 D0 的默认 Hook 质量审计

基线 core 固定为 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f`，能力为 `delivery_review`。不改 core/adapter，不组装、安装或启用宿主插件。使用 `reference-route-audit-r1/r1` 已完成的真实稿，原请求从 fixture 取出，先核对稿件、请求及原 trace 的 hash 和实际 Skill 读取记录。

固定六稿：alibaba2/SHORT/baseline，alibaba1/SHORT/candidate，ollama/EDUCATION/baseline，opencode/EDUCATION/baseline，minimax/SHORT/baseline，minimax/EDUCATION/candidate。完整 case ID 为 `REMEDIATION-SHORT-SERVICE` 和 `REMEDIATION-EDUCATION-LONG`。本组用于检查实际修错、漏检和新增错误，不估计总体错误率。

薄 wrapper 重放原请求、已被源 trace 证实的 Skill 读取及 Stop 事件。每个 core 事件调用真实 Python 子进程；每个 block（含逐字回显）使用现有 Claude CLI、旧 harness 的环境构造和 stream 解析，读取实际模型回复再继续。最多四次续写；没有 finding 记为未发现，不强造修订包或语义判定。

优先保留 D0 的 provider/model 路线。若 alibaba1 或 minimax 在旧 CLI 中无法绑定，保留失败记录，显式改用 alibaba2 作续写者；不声称同模型。每次调用均保存 prompt、完整 stream、stderr、真实回复、模型绑定、usage 和 CLI 报告的费用。费用仅为宿主报告，不作实际账单保证。

所有完整数据写入新建的 `output/hook-audit-quality-r1` 子目录。逐稿保留 D0/可见终稿 hash、每次 core 输入输出和阶段快照。技术闭环成功与文章质量分开判断；原稿与终稿须按原请求复核事实、状态、必要内容、篇幅及自然度。该实验是 core 事件重放与独立 CLI 真实续写，不是原生宿主 Hook 在线运行证明。

运行 `replay_real_d0.py --source-root <真实稿目录> --core-root <固定基线工作树> --output <新输出目录>` 只核验输入；加 `--run` 才执行已授权的真实调用。不自动重跑已存在的输出目录。

运行后的记录见 [结果](result.md) 和 [持久化六稿证据](frozen-evidence.json)。它们补充实际结果，不改变上述选稿、模型回应真实性和宿主证明边界。
