# R6：未达到两路线减载，撤回stdin与源码读取提示

最终状态：`REJECTED_NO_CONSISTENT_LOAD_GAIN / RESTORED_TO_CONTROL`。四份真实稿收齐后，主代理确认按预登记收口：**本方向R4/R5/R6新增提示全部撤回，产品恢复到5cb696fe的绝对路径文档原子**。保留所有失败原型、完整稿与原始trace，不再新增模型调用。路径说明的可执行性由主代理另一份真实终稿命令证据单独准入，不能充作本轮源码减载证明。

实验产品冻结 `70d3c596`，对照 `5cb696fe`；唯一产品增量是SKILL脚本段194 UTF-8 bytes（27267→27461），工具/提示/模型绑定与R5相同，源码ID仍可用。现成38项MCP边界及8项init反控PASS、模型调用0；4份真实调用均技术有效，实际init与所有tool_use都只有两个登记MCP工具，skills/plugins空，三层模型绑定正确。[预登记](preregister.md) / [fixture](real-ab/fixture.json) / [无模型反控](real-ab/contract.json)

## 两种读取口径

| 路线/臂 | 服务端文档bytes | 宿主可见响应bytes | 完整源码请求 | 参数拒绝 | 精确终稿复扫 | 秒 | 正文实质错误 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Alibaba2控制 | 114114 | 59705 | 1 | 0 | 1 | 75.219 | 0 |
| Alibaba2实验 | 48766 | 49169 | 0 | 0 | 0* | 89.156 | 0 |
| MiniMax控制 | 28005 | 28178 | 0 | 2 | 0 | 26.000 | 1 |
| MiniMax实验 | 94829 | 95952 | 0 | 0 | 1 | 56.297 | 0 |

服务端字节是冻结文档原文，包括D0；宿主可见字节是完整stream中相应 `tool_result.content` 的UTF-8长度，包含可见包装和预览，不是API token或实付上下文。所有样本均无重复文档ID。

Alibaba2源码请求1→0，可见读取减少10536 bytes；但MiniMax控制本来就不请求源码，候选另读9份references，可见读取增加67774 bytes。两个候选合计可见响应145121 bytes，对照87883 bytes，增加57238 bytes。缺少两路线一致的省读，不能因为一条路线或参数使用有改善就更换准入指标。

R6归档时额外只读核对R4/R5/R6全部12份原始trace，发现共9次完整源码请求全部被Claude写成持久化输出，并只向当前消息给约3.3KB预览。此前服务端每次58290 bytes不能称为“58KB源码完整进入模型上下文”。原始raw/fixture/hash不改，R4/R5报告已补双口径并将“整读”更正为“完整源码请求”。[逐工具读取面与trace SHA](../reading-surface-audit.json)

## 正文与复扫

两候选保留全部事实、日期、数量、联系人、活动未审定状态、参加确认限制和发言名单限制，没有候选独有实质错误。Alibaba2实验将“报名信息包括”局部改为“报送内容包括”，并在署名与日期间增加空行；MiniMax实验只去Markdown加粗并删重复报送结语，均属正文范围内变化。

MiniMax控制删除“报名不等于已列入发言名单”，按与R5一致的口径计1项独立限制状态遗漏；另一句“不作正式参加确认”不能替代它。它只对原稿运行了有效format/structure扫描，没有对这个缺句终稿有效复扫。不能把两个不同状态合并，亦不能把原稿扫描成功当终稿保真。

表中0*：Alibaba2实验确实复扫了完成语义修订的正文，但最终回显又在署名/日期之间增加空行，故不满足预登记的“只忽略首尾空白”的精确终稿相等条件。去除全部空白后与所扫正文相同；这单列为回显空白差异，不据此虚构一个事实或结构硬错。[逐稿指标与作者复核](real-ab/metrics.json)

## 完整证据和实际命令

四次调用顺序为MiniMax实验、Alibaba2控制、MiniMax控制、Alibaba2实验，没有重试：

```text
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r6 --provider minimax --arm experiment
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r6 --provider alibaba2 --arm control
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r6 --provider minimax --arm control
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r6 --provider alibaba2 --arm experiment
```

| 完整正文 | 实际argv | 完整模型trace | 工具输入输出 |
| --- | --- | --- | --- |
| [Alibaba2控制](real-ab/raw/alibaba2/control/final.txt) | [argv](real-ab/raw/alibaba2/control/invocation.json) | [trace](real-ab/raw/alibaba2/control/stream.jsonl) | [calls](real-ab/raw/alibaba2/control/tool-calls.jsonl) |
| [Alibaba2实验](real-ab/raw/alibaba2/experiment/final.txt) | [argv](real-ab/raw/alibaba2/experiment/invocation.json) | [trace](real-ab/raw/alibaba2/experiment/stream.jsonl) | [calls](real-ab/raw/alibaba2/experiment/tool-calls.jsonl) |
| [MiniMax控制](real-ab/raw/minimax/control/final.txt) | [argv](real-ab/raw/minimax/control/invocation.json) | [trace](real-ab/raw/minimax/control/stream.jsonl) | [calls](real-ab/raw/minimax/control/tool-calls.jsonl) |
| [MiniMax实验](real-ab/raw/minimax/experiment/final.txt) | [argv](real-ab/raw/minimax/experiment/invocation.json) | [trace](real-ab/raw/minimax/experiment/stream.jsonl) | [calls](real-ab/raw/minimax/experiment/tool-calls.jsonl) |

fixture SHA-256：`db473078e5e2d01c27dd62ff9e39c19bc8418c9a75d6f6dd173902a5edadd426`；[38文件SHA清单](real-ab/SHA256.json)覆盖归档证据。四份CLI费用估计按表顺序为$0.248990、$0.265864、$0.1664165、$0.4514075，合计$1.132678；完整usage在各receipt中，费用不冒充供应商实付账单。

本轮是受限工具接口实验，无任意Shell/网络/注册表/通用文件工具；它不证明原生Shell安全，也不估计批量稿无错率或4—7版修改稳定性。没有系统代理修改、镜像、合并、推送、tag或发布。最终交付只保留绝对路径说明，失败的stdin/源码条件不会进入最终产品。
