# SOL max 功能裁决规则

逐项判断：

1. `target_correct`：删除内容是否确属用户未要求的过程旁白、协议泄漏、围栏或包装；
2. `body_preserved`：正文事实、状态、标点、顺序和必要换行是否保留；
3. `requested_format_preserved`：用户明确要求的 Markdown 或干净普通文本是否未被误删；
4. `direct_use`：候选是否可直接交付。

输出严格 JSON：

```json
{
  "schema_version": 1,
  "cases": [
    {
      "id": "C1",
      "target_correct": "PASS|FAIL",
      "body_preserved": "PASS|FAIL",
      "requested_format_preserved": "PASS|FAIL",
      "direct_use": "PASS|FAIL",
      "reason": "简短理由"
    }
  ],
  "overall": "PASS|FAIL",
  "reason": "总体理由"
}
```

必须覆盖 C1—C5。任一检查 FAIL，则该 case FAIL；任一 case FAIL，则 overall FAIL。
