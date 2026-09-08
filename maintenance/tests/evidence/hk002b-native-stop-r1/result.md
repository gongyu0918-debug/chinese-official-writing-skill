# HK-002b Codex 原生 Stop 最小验证 R1

冻结产品 4fd63ce344fec440bbbbc664a7ebd7934751e04e 的本轮原生生命周期通过：一份明确状态错误得到局部纠正，一份正常对照逐字保留。两例都完成最终回显哈希核对和运行材料脱敏。此结论只覆盖本轮两个冻结输入。

运行使用本机已缓存的 Codex CLI 0.151.0、精确 ollama-cloud/glm-5.3-flash / max。两例宿主 turn_context 均实际记录该 model/effort，每例独立 CODEX_HOME、profile 和工作目录。冻结 Git 正常组装完整 64 文件 companion，原生 marketplace add、plugin add 成功，安装缓存文件集合与组装包唯一对应。--dangerously-bypass-hook-trust 只作为本次调用的 Hook 信任依据，不代表永久信任。原始安装回执、清单与调用记录分别保留。

| 样本 | 原生运行 | 实际结果 |
| --- | --- | --- |
| 明确状态错误 | 44.409 秒，exit 0 | 冻结 D0 → repair JSON → PASS 关系核验 JSON → 最终 D1。把“业务科尚未开展18份附件核对”改为“业务科正在核对18份附件”，保留9月4日、18/10/8、反馈日期未定及有据分析。 |
| 正常对照 | 31.117 秒，exit 0 | 门禁采用 D0，未调用修订或语义核验；最终正文与冻结 D0 完全相同。 |

错误例D0按UTF-8、LF正文计算的SHA-256为 f5d73b3a9416559c4e7dfbd01f0994bed29c096da5a4e430bd6b4f8dcff7f82f。原始Windows初稿文件使用CRLF，原文件SHA另列于summary和归档清单，不能把这两个口径混称逐字节相同。门禁实际D0与预先冻结的LF正文一致。两例最终文件均为 d0152a7d8d400a7a980dcf5d33e43cd08a135f44599a1767fbeba1b693c6ae47；最终文件字节SHA与各自 emitted_sha256 一致。两个终态均为 complete，delivery_verified=true，data_retention_state=raw_turn_data_redacted，raw_artifact_delete_failures=0。

错误例保留 request-bound、skill_seen、awaiting_repair、awaiting_verdict、awaiting_final_output、complete 的实际状态快照，事务经过一次修订和一次核验。修订与核验响应绑定请求、D0、D1 和来源关系包，独立列出原稿确错、修订解决及其余事实保持的判断。调用中的工具命令只读取已安装首页和冻结 D0，未手工调用 gate 或 Hook。正常对照也实际成功读到首页和初稿。

保留的运行噪声与限制：

- 对照样本在取得文件内容过程中出现六条可见进度说明，之后才提交冻结正文及最终回显。因此不能把本轮称作两次完全无噪声、只含正文的首稿试验；实际输入门禁的 D0 哈希与冻结文本一致。
- CLI 的 error item 包含调用级 hook-trust 提示；出现的 WebSocket 426 日志一并保留。进程最终成功，未将这些记录删除或另起批次覆盖。
- CLI trace 没有单独暴露原生 Hook 事件封包。本轮以原生插件调用、绑定请求的状态快照、成功读页、Stop 启动标记、事务转移及模型续行共同举证，不虚报原生 Stop 事件条数。stop_attempts 是核心续行计数字段，不能直接当宿主事件总数。
- 两次 CLI 任务、12条可见 assistant 消息均不等于上游调用数。正常对照的六条进度说明也不等于六次 Stop。未观察到上游返回模型身份，只能确认宿主 model/effort。
- 初稿是显式冻结注入，不能称作模型自然成稿产生的错误；原生修订和核验在同一会话、同一路线完成，不能称作跨 provider 独立核验。未验证全文事实完整性，full_draft_fact_verified 保持 false。

归档只包含本轮合成材料的提示、冻结稿、最终稿、可见 trace、修订/核验响应、回执、必要状态快照和脱敏终态；不包含完整会话、home、config、catalog 内容、缓存或登录态。入库前对选定文件运行凭据模式扫描，结果及精确文件 SHA 见 summary.json 和 archive-manifest.json。原始隔离运行目录继续留在 output 供追溯。

运行入口为 runner.py 的 prepare、setup --case error、run --case error、setup --case control、run --case control。该子任务没有发布、推送、Pro 更新或定时发布动作。后续845项工程回归及30+20项行为等价回放，由主任务另行关联；不把它们混记为本轮原生在线调用。
