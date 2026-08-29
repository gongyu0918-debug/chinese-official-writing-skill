# AH-002 阶段一自然写稿结果

日期：2026-08-29。

固定 `main@31dacd0805035521ad848bdc10e70c0a366d554c`，Ollama Cloud 与 MiniMax CN 按预登记完成三题共6份真实新闻稿。6份均有终稿，5份实际读取隔离 Skill；MiniMax 演练稿没有读取隔离 Skill，记为技术无效，不作准入票。

Ollama 三份有效稿均把完整日期缩为月日：

| 题面 | 材料日期 | D0日期 | D0 SHA-256 | 结果 |
| --- | --- | --- | --- | --- |
| `AH2-TRAINING` | `2026年9月2日` | `9月2日` | `17a3dcf945d316b7a95b22a1a60b67480c099fe9fcd71391aaa53f1033731f2a` | 自然漏年，可修复 |
| `AH2-OPEN-DAY` | `2026年9月6日` | `9月6日` | `02359dbe8936d3d60d6ddcd5a87f7f3dc5cd03790ad097d5299e5c59726eeed3` | 自然漏年，可修复 |
| `AH2-DRILL` | `2026年9月9日` | `9月9日` | `72113ddbfea808b77bff25c0444bd13a20194e9cdf8e0f3d24c1623401b69ad8` | 自然漏年，可修复 |

三稿分别为175、147、177个非空白字符，均保留单位、人数、完成范围和未决状态，并形成一层学习、了解或实践作用；短于提示词只作信号，不判功能失败。一般作用和从“29人完成全部环节、3人只缺设备检查”承接的前两环节参与情况不作材料外硬事实处理。

MiniMax 的培训稿与开放日稿完整保留年份；按预登记取第一份技术有效完整日期稿 `AH2-TRAINING` 作原样控制，SHA-256 为 `d630c877032be6d932a1fe0fdb31dd71701c40d7acf4f84819eb8bf03da35957`。该控制稿存在较具体的环节铺陈，但本轮只验证日期修订是否无故改动现有 D0，不用控制稿文采替代日期目标。

阶段一累计3份自然可修复 D0，已经超过至少2份的启动条件；不再运行 Alibaba Token Plan 2、Alibaba Token Plan 或 OpenCode Go 的自然基线。下一阶段冻结上述三稿和一份控制稿，由五家便宜 provider 做同稿精确修订。

实际命令：

```text
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_baseline.py --prepare
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_baseline.py --provider ollama
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_baseline.py --provider minimax
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_baseline.py --summarize
```

原始 final、trace、stderr、fixture 和 summary 位于忽略目录 `output/ah002-news-date-completeness-r1/baseline/`。

