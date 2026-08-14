# 交付洁净度真实优先结果

固定基线为 `ea34866008dad0cb6bf45bc01e926f4e8fc9905c`，产品原子在真实写稿通过后实现。没有运行独立采样的 Hook on/off 文采竞赛；功能门只看同一 D0 是否精确清除目标包装、正文是否保持、明确格式是否保留。

## 真实 D0 整理

- `opencode-go/deepseek-v4-flash`、`ollama-cloud/deepseek-v4-flash:0731`、`alibaba-token-plan-2/deepseek-v4-flash-0731`，均为 max、0 retry、1200 秒上限。
- 5/5 技术有效，5/5 与预期逐字一致。
- 三个脏稿分别清除了过程旁白、普通文本外的 Markdown 包装和协议 JSON；普通干净稿与用户明确要求的 Markdown 稿逐字不变。
- cases SHA-256：`811caedd87df08c34fb7dd69728f89373c7b619157f8ceec6dda26c38efc22ba`。

独立 `gpt-5.6-sol` max 对五组功能终审均为 PASS。`sol-verdict.json` SHA-256 为 `BFBA402199DC7E3C99DD637D136635BD2ADFBFDB392ABCD7CC65F96D929DA87A`；`sol-receipt.json` SHA-256 为 `565E3F0868AC6F9D8A539903F7FA5BF1772E67A013ED50BB888AE382DAE76532`。

## 在线生命周期

使用 Claude Code 2.1.195、OpenCode Go DeepSeek V4 Flash max 和静态 `delivery_cleanliness` companion。

1. R1：12 个 Hook 事件已发生，但 adapter 能力白名单漏掉新名称，配置静默回到 `delivery_review`，终稿保留脏前缀。该次失败促成 adapter 修复。
2. R2：能力正确进入，10 个 Hook 事件完成；测试 system 指令持续要求保留前缀，模型逐字返回 D0，能力安全选择 `D0/clean_or_requested_format_preserved`。这是测试污染下的安全回退，不计功能通过。
3. R3：把脏前缀要求限定为首稿后，12 个 Hook 事件完成。能力冻结并删除唯一前缀 span，`selection=D1`、`reason=semantic_pass`、`delivery_verified=true`。D0 SHA-256 为 `95dce24190729372fecf1d42a805edde3d91cc50384c3afd979b45165ab0d236`；最终稿与 D0 精确删除包装后的 SHA-256 均为 `8b27e4bf2663a67d604ebc1d5aa03df6e5bff3a67bde9600c3bf12b85f6393cb`。

## 当前结论

`CL-001` 功能门通过。实现是第四个静态互斥 capability：一次洁净稿、一次冻结删除项核验、一次哈希回显；候选含新增或改写、误删正文、删除用户要求格式、核验失败或运行异常时回退 D0。Codex/CodeBuddy 共用 adapter、Claude Code 独立 adapter 均接受该能力；三宿主静态包均完成组装。当前只完成 Claude Code 的真实在线生命周期，Codex 和 CodeBuddy 不冒充当次在线成功。
