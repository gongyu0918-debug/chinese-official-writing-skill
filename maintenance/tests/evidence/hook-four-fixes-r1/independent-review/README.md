# 终态与锁行为：独立窄复验

最终 R3 三项通过，冻结 core SHA-256 为 `969235f48c8a7f8592b84742257b08315e823326c76d4198e7e12b7cc5eb32ea`。只验证锁超时与迟到终态写入，不代表完整生命周期或原生宿主验证。独立审查未修改产品；以下修复由主代理实施。

| 阶段 | 结果 | 证据 |
| --- | --- | --- |
| R1，修复前 | prototype 锁超时后错误回显被 main 放行；基线同条件返回 block。另一个启动/HostAbort 窗口在两臂均重建两份原文输入，是继承问题，保留登记、不计本轮新回退 | [原始结果](result-r1-before-fix.json) |
| R2，部分修复后、最终修复前 | 锁超时已明确停止；失败终态拒写与调用方刷新通过；成功终态仍返回缺少正文的回显 block，整体 `pass:false` | [保留的失败结果](result-r2.json) |
| R3，最终窄修复后 | 锁超时 2.016 秒后 `continue:false`，释放锁后恢复正常 block；失败终态保持明确停止；成功终态直接 allow。两种终态的记录 hash 不变、无 raw 键，调用方均刷新 | [最终结果](result-r3-after-fix.json) |

[复验脚本](probe.py)仅用标准库，加载指定 core，使用真实操作系统文件锁和受控迟到写入次序。其它 capability handler 被旁路；未调用模型或 gate 子进程。复用既有短 D0，SHA-256 为 `353db1634bb8796131c8b92857aa9d49f4f1401c73dd736efa218a9c8dfee2e5`。结果不包含凭据或私有配置。

实际 R3 命令如下，工作目录为本轮独立 worktree；进程退出 0，结果中的三项及整体 `pass` 均为 true。R2 使用相同脚本和参数结构，输出目录为 `independent-state-review-r2`；该诊断脚本退出 0 只代表完成记录，R2 的 `pass:false` 保持原样。

```text
python -X utf8 -B maintenance/tests/evidence/hook-four-fixes-r1/independent-review/probe.py --core chinese-official-writing/hooks/core/gate_stop_hook.py --output output/hook-four-fixes-r1/independent-state-review-r3
```

重复执行须使用新的输出目录，脚本拒绝覆盖旧目录。原始 R1/R2/R3 输出均保留；归档 JSON 按原字节复制。旧 bootstrap/HostAbort 窗口未在 R2/R3 扩测或修改，最终原生生命周期由主代理另行举证。
