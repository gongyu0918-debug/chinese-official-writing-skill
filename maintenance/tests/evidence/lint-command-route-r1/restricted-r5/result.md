# R5：入口提示曝光后仍没有两路线源码减载

读取量口径补充：本报告原有字节表是MCP服务端返回的文档原文字节。R6归档时只读核对完整trace发现，Claude把源码响应持久化并只传回约3.3KB预览；这些请求不能称为58KB源码完整进入上下文。下文“源码请求”仅计请求整份文件的动作，宿主可见响应量另列；原始fixture、raw和SHA未改。[12稿读取面复核](../reading-surface-audit.json)

结论：新增句在两路线候选的首次SKILL读取中均已曝光，但**四份仍全部请求完整脚本源码（服务端每次返回58290 bytes）**。总读取在Alibaba2减少、MiniMax增加，未得到两路线可归因省读。两候选无观察到独有正文硬回退；控制稿发生一次独立限制状态遗漏，不能把所有正文都记PASS。按授权仅再尝试R6的最小读取条件，之后收口。

这是受限MCP接口A/B，控制固定 `5cb696fe`，实验/宿主代码固定 `4cd78c01205c44c8dd8ee63642aa630bb7863def`。产品只有SKILL脚本段新增同一句100 UTF-8 bytes（27267→27367）；final-review与控制逐字相同9029 bytes。没有强制预读该叶或删除源码工具。R4原稿没有迁入本轮质量分母。[预登记](preregister.md)

两臂38项真实stdio检查及8项初始化合成流反控PASS、模型调用0；新模型批次4份均技术有效，init先行、只有2个MCP工具、skills/plugins均空，init/assistant/modelUsage精确绑定登记模型。[无模型反控](real-ab/contract.json) / [fixture](real-ab/fixture.json)

实际运行共4次，顺序Alibaba2实验、MiniMax控制、Alibaba2控制、MiniMax实验，没有重试：

```text
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r5 --provider alibaba2 --arm experiment
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r5 --provider minimax --arm control
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r5 --provider alibaba2 --arm control
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r5 --provider minimax --arm experiment
```

## 观察分列

| 路线/臂 | 服务端文档bytes | 可见响应bytes | 源码请求 | 参数拒绝 | 成功help | 有效终稿复扫 | 秒 | 正文实质错误 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Alibaba2控制 | 110033 | 55485 | 1 | 0 | 1 | 1 | 80.750 | 1 |
| Alibaba2实验 | 101392 | 46837 | 1 | 0 | 1 | 1 | 71.156 | 0 |
| MiniMax控制 | 86295 | 31470 | 1 | 1 | 1 | 1 | 27.859 | 0 |
| MiniMax实验 | 103264 | 48730 | 1 | 0 | 0 | 1 | 25.703 | 0 |

成功读取计入D0和源码，均无重复文档ID。Alibaba2读取差−8641 bytes、MiniMax+16969 bytes，来自不同reference选择加候选100-byte入口句，不能当源码省读。Alibaba2控制已自然用help及正确终稿复扫；MiniMax候选少一次漏 `-` 拒绝，但没有少读源码或减少复扫步骤。四份均成功扫过与最终正文相同的stdin且带format/structure，因此本轮有效复扫不是候选独有能力。

Alibaba2控制将“交流主题、发言顺序尚待确定”挪至首段，同时删除了“报名不等于已列入发言名单”。原稿的“不作正式参加确认”针对参加确认，不能完整替代发言名单限制；用户要求保留未决状态，作者复核按独立限制状态遗漏计1个实质错误，未重复计为新增事实错误。该限制遗漏仍存在于最终复扫的正文中，说明lint扫描通过不能替代语义保真。其余3稿保留全部实质事实和状态；MiniMax两臂仅另删重复的报送结语。此处为作者逐稿复核，不冒充外部盲审。[量化与逐稿判读](real-ab/metrics.json)

| 完整正文 | 实际argv | 完整模型trace | 工具输入输出 |
| --- | --- | --- | --- |
| [Alibaba2控制](real-ab/raw/alibaba2/control/final.txt) | [argv](real-ab/raw/alibaba2/control/invocation.json) | [trace](real-ab/raw/alibaba2/control/stream.jsonl) | [calls](real-ab/raw/alibaba2/control/tool-calls.jsonl) |
| [Alibaba2实验](real-ab/raw/alibaba2/experiment/final.txt) | [argv](real-ab/raw/alibaba2/experiment/invocation.json) | [trace](real-ab/raw/alibaba2/experiment/stream.jsonl) | [calls](real-ab/raw/alibaba2/experiment/tool-calls.jsonl) |
| [MiniMax控制](real-ab/raw/minimax/control/final.txt) | [argv](real-ab/raw/minimax/control/invocation.json) | [trace](real-ab/raw/minimax/control/stream.jsonl) | [calls](real-ab/raw/minimax/control/tool-calls.jsonl) |
| [MiniMax实验](real-ab/raw/minimax/experiment/final.txt) | [argv](real-ab/raw/minimax/experiment/invocation.json) | [trace](real-ab/raw/minimax/experiment/stream.jsonl) | [calls](real-ab/raw/minimax/experiment/tool-calls.jsonl) |

fixture SHA-256：`2f1ed0301ebecdc5c278dad0fea02851e1b32d6ed1bdc1fa4317614275767789`；[38文件SHA清单](real-ab/SHA256.json)同时用于本地/暂存blob复核。各receipt保留原始usage，CLI费用估计分别$0.254306、$0.229703、$0.1637885、$0.219101，合计$0.8668985；不是供应商实付账单。

原始prompt、D0、两路线max配置、工具ID和能力范围与R4一致；只补了已记录的初始化异常守卫，普通写稿行为没有额外引导。没有临时文件写入工具，因此也没有资格声称改善普通宿主临时文件行为。四份同题稿不推导一般无错率、多版修改稳定性或普遍token收益；不合并、不镜像、不发布。
