# WR-001-DATE-R2 结果

日期：2026-08-24。

## 结论

`TERMINATED_DUPLICATE_PROMPT_DIRECTION`。R2 把日期要求合并进既有时间事实条目并缩短，Ollama 与 Alibaba Candidate 都读取精确隔离 Skill，均保留“2026年8月20日”和48/45/3/46、单人原话、意见卡汇总状态，且无 Markdown 包装或后续安排。

Ollama 仍把题面只给名称的导读具体化为“了解本次分享书目和阅读要点”，并补写各环节的具体过程；这是预登记禁止的材料外活动过程。Alibaba 没有该硬回退，但把同一三个环节先总述、再逐项重复展开，284字正文信息增量有限。R2 未解决 R1 的关键副作用，按预登记停止继续换位置、换措辞或追加日期/活动枚举。

## 结果

| 路线 | 字符 | 日期与硬事实 | 材料外/自然度 | 判定 |
| --- | ---: | --- | --- | --- |
| Ollama DeepSeek V4 Flash 0731 | 217 | 完整 | 补“本次分享书目和阅读要点”及环节具体过程 | `TARGET_PASS / HARD_FAIL` |
| Alibaba Token Plan 2 DeepSeek V4 Flash 0731 | 284 | 完整 | 三环节总述后再次逐项展开，重复偏长 | `TARGET_PASS / WARN` |

R1 已证明 v1.6.15 Baseline 在 Ollama、Alibaba 继续省略年份；R2 按预登记只跑 Candidate，不重复消耗 Baseline。原始输出、trace 和 stderr 保存在忽略目录 `output/wr001-date-r2/candidate-only/`。

## 收口

- 日期完整性仍由现有 `information-selection.md` 的日期保留总则承担；本轮证明在新闻叶重复同义规则虽能提高目标命中，却没有形成稳定净收益。
- 不增加“正文必须更长”、固定段数、活动过程模板或更多枚举禁令。
- 本分支恢复产品到 v1.6.15 字节，只保留研究证据；后续若再研究，必须换成不同机制和新的真实反例，不能沿本提示词方向抽样。

实际命令为同一 runner 的 R2 `--prepare`，随后对 Ollama、Alibaba 各调用一次 Candidate 单臂。固定候选产品提交为 `e13d602b`，fixture 绑定运行 HEAD `25627f7f`。本轮未修改 main、版本、tag 或平台内容。
