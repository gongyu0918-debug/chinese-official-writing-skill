# SOL max 重复句功能裁决

逐项判断：

1. `redundancy_handled`：目标完全重复或同义零增量复述是否被删除；清洁反控是否没有误删；
2. `meaningful_content_preserved`：不同主体、时间、对象、事实、状态、结构、承接或结尾作用是否保留；
3. `deletion_only`：候选是否只删除 D0 字符，没有新增、改写或重排；
4. `direct_use`：候选是否可直接使用。

R4 删除任一重复位置均可，但须结合小标题和段落作用判断删后结构是否自然。不要因与预先指定位置不同自动失败。

严格输出 JSON，覆盖 R1—R5：

```json
{
  "schema_version": 1,
  "cases": [
    {
      "id": "R1",
      "redundancy_handled": "PASS|FAIL",
      "meaningful_content_preserved": "PASS|FAIL",
      "deletion_only": "PASS|FAIL",
      "direct_use": "PASS|WARN|FAIL",
      "reason": "简短理由"
    }
  ],
  "overall": "PASS|FAIL",
  "reason": "总体理由"
}
```

任一前三项 FAIL 或 direct_use=FAIL，则该 case FAIL；任一 case FAIL，则 overall FAIL。WARN 只允许轻微自然度问题。
