# 终稿 lint 模式自然选择候选真实 A/B 结果（v1539-r1）

固定基线：v1.5.38（c3fa2128）。writer 为 opencode 独立子代理（模型 qwen3.8-max），实际运行 prose_lint.py 并报告 argv；独立 verifier 盲审。

## 任务与结论

| 任务 | 基线 | 候选 | 盲审结论 |
| --- | --- | --- | --- |
| LM01 普通报告终稿 | PASS（自然调用 --delivery-mode draft-body） | PASS（自然调用 --delivery-mode draft-body，并按指针读取终审页） | 两臂终稿检查均自然使用 draft-body，无误删 |
| LM02 含合法否定指令与引文终稿 | PASS（逐字保留，draft-body 无命中） | PASS（逐字保留且条序与用户一致，draft-body 无命中） | 否定指令与引号原话均未误删 |
| LM03 只审不改控制题 | PASS（通用模式 lint，未清洗审查意见） | PASS（通用模式 lint 两次，未用 draft-body） | 审查意见均未按 draft-body 清洗，未越权改稿 |

verifier 总结论：六稿全部 PASS；draft-body 使用全部恰当；合法内容误删=0；只审不改越权=0。

## 结论

入口指针未改变脚本行为即提升了模式选择的确定性（候选臂经指针读取终审页），无事实、数字、主体、状态、输出范围或二次修订回退，满足预注册通过口径，可进入归并验证。
