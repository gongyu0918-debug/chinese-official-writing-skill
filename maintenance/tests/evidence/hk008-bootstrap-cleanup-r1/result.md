# HK-008b 启动清理与并发恢复集成结果

日期：2026-08-23。固定基线：`main@408db010870bb336d0d1f6dbc7019a519e55b2a4`。集成分支：`codex/v1615-hk008b-integration`。

## 结论

`PASS_MERGE_CANDIDATE_NOT_RELEASED`。本候选只集成 HK-008b 的 Hook 核心与直接测试，不包含 WR-010 sidecar、OC-002 新闻语料或其他研究文件。

普通 Stop 自动启动门禁时，Hook 会先登记当前 turn 的 provisional txn，再写入 request/D0。detect 非零、detect OSError、成功但缺 state、进程中断后的下一次 Stop，以及锁文件永久 I/O 故障，都会删除该 turn 的原始输入和事务后安全放行；并发 Stop 只有一个 bootstrap owner。

OS 文件互斥由进程退出自动释放。只有锁 API 的真实 `EACCES/EAGAIN` 竞争记为 busy；文件打开、sentinel 初始化和其他锁 I/O 错误不再造成无限阻断。Windows 正常终态删除锁文件，清理 I/O 故障时可残留1字节无敏感 sentinel；POSIX 固定保留 sentinel，避免 `flock` inode 分裂。

## 精确集成范围

前五个提交逐项移植原候选产品原子：

- `b3c48174`：失败 bootstrap 原始快照清理；
- `15956563`：不修改文件的起草请求不误判审稿；
- `e2b4d584`：bootstrap owner 与起草/审稿分类竞态；
- `2d4a65d2`：进程级 OS 互斥；
- `2e32d96e`：POSIX sentinel；
- `0375f516`：fatal lock I/O 与真实竞争分流。

在第五提交暂停点，Hook 与测试的 blob 分别与原研究候选 `22ac4a19` 完全一致；最后一项仅移植 `fac85210` 的两个产品/测试文件，目标 blob 也逐字一致。研究文档未随提交整体 cherry-pick。

## 固定基线消融与回归

- 同6个反例装载发布基线：6个 method 中5个 failure、5个 subtest error；会残留 request/D0、重复 detect、并发重复 owner，并把5个起草变体误旁路。
- 当前候选：同6个 method 为6/6通过、0 failure、0 error。
- `py -3.13 maintenance/tests/test_gate_stop_hook.py -q`：38/38通过。
- `py -3.13 -m unittest discover -s maintenance/tests -p "test_*.py" -q`：673/673通过。

## CodeBuddy 实际生命周期与最终包

fatal-lock I/O 分流前的直接前序候选已在 CodeBuddy CLI 2.115.0、`deepseek-v4-flash/max` 完成一份采购申请：Skill/Read 后2次 Stop，终稿保持数字、未定采购状态和低强度预期；终态 core 只留 hash/阶段/交付回执，transaction 为0项、锁为0、原始敏感文本为0命中。该次54文件 companion fingerprint 为 `2a1c6962e9687ff9852328ed16d11e400f86cc730f58b6544b4df25e93282255`。

最终集成候选只在锁错误分流及其反控上不同，普通 Stop 协议、CodeBuddy adapter 和组装胶水未变；没有把前序在线样本冒充为最终 blob 重跑。最终候选重新组装为54文件，fingerprint `84f8179688250dea172b9c0bd3f71655cdc47ff3513172a2f7ab9641de66dea7`，CodeBuddy `plugin validate` 通过，`installed=false`、`network_used=false`。

该在线证据只证明 Windows CodeBuddy 当前路径。CLI init 仍列出完整工具表，不能把实际只调用 Skill/Read 写成宿主强制裁剪。

## 剩余边界

- Linux/macOS 只有分支单测，没有真实宿主多进程生命周期。
- fatal-lock I/O 最终补丁只有直接反控和最终包校验，没有再次运行普通 CodeBuddy 在线写稿；迁移的是协议未变化的前序生命周期。
- 宿主硬退出且之后没有同 turn Stop 时，pending 原始输入仍需人工清理；本候选不增加后台 TTL 或全局扫描。
- CodeBuddy 自身会话、debug、trace 和通用日志不在 companion 清理权限内。
- 当前只是本地合并候选，未推送、未打 tag、未发布；Hook 默认关闭和窄启用边界不变。
