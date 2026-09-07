# “以下正文”前言清理：HOLD

本次没有修改产品。唯一输入来自本轮原生纪要链 `continuity/native-r4-minutes/round-5`：完整 D0 取 stream result，请求逐字取 invocation；与该流的 assistant 文本及 final.txt 文本一致。原生来源和本次离线 runtime 调度真实续写分开记录，不能将本次清理称为原生 Hook 已运行。

原回复 626 个非空白字符，首段以“以下正文约 500 字以内”开头，其后是一条横线。期望仅删首段和横线的 70 字符，556 字正文完全保留。正文仍超原 500 字要求，原有事实问题也保留，不是本次清理目标。

当前 `delivery_cleanliness` runtime SHA-256 `9b2988d00ba341a708a04f661f3fae1afd6a5e1510e1a017304ea10da783824c`。Alibaba2 DeepSeek V4 Flash 0731、max、180 秒/次、0 retry；实际只调用 revision、verdict、echo 共 3 次，未触及 4 次上限。

| 环节 | 实际结果 |
|---|---|
| 修稿 | 21.766 秒；只删前言和横线，与冻结正文逐字一致 |
| 核验 | 115.937 秒；返回 DSML 伪工具调用文本，不是规定的 JSON |
| 选稿与回显 | 正确回退 D0；5.625 秒精确回显，`delivery_verified:true` |

三个调用的 CLI 传输、模型绑定和空工具清单均有效。核验回复的 Python 文本没有执行；没有补算 hash 或人为注入 PASS。runtime 的 `semantic_rejected` 在这里对应**核验协议失败**，不代表模型作出了“删除前言有错”的语义判断。最终仍是带前言的 626 字原稿，目标清理未闭合，`functional_pass:false`；入口“以下正文”暂不准入扩展，也不追加调用。

复现当时执行的命令：

```text
python -B output/hook-quality-build-r1/cleanliness-new-prefix/run.py --prepare
python -B output/hook-quality-build-r1/cleanliness-new-prefix/run.py
```

两条命令 exit 0；runner exit 0 仅表示执行收口，不等于清理目标通过。完整 prompt、reply、receipt、流摘录、原生来源及冻结 runtime 见[清单](manifest.json)；私有 runtime/HOME 不归档，归档驱动保留原 output 工作坐标。

- fixture：`33c0e981ec857e298d68fd8b89d41462849c41d859c1c851e09c3f4bdd8782fd`
- 原 D0（stream result 的 UTF-8 文本）：`17ad73b7212d42078beae4a3ebf11e131eb4de9d6cd0ebcd3c6e4e510a0f20ea`
- 期望正文与真实修稿：`b0444fbb499f0717c9fddec1d6a3187cd7f954634c93727a03b3ea969a863740`
- 最终回显与 D0 相同：`17ad73b7212d42078beae4a3ebf11e131eb4de9d6cd0ebcd3c6e4e510a0f20ea`
