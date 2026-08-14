# 交付洁净度真实优先预注册

固定基线：`ea34866008dad0cb6bf45bc01e926f4e8fc9905c`

本轮不实现 Hook、不修改产品。先把最小洁净指令直接作用于 5 份完整 D0：1 份真实出现的过程旁白稿、1 份 Markdown 围栏包装稿、1 份协议 JSON 泄漏稿、1 份干净正文、1 份用户明确要求 Markdown 的正文。

## 固定模型与执行

- `opencode-go/deepseek-v4-flash`，max：C1、C4；
- `ollama-cloud/deepseek-v4-flash:0731`，max：C2、C5；
- `alibaba-token-plan-2/deepseek-v4-flash-0731`，max：C3；
- provider 内串行，provider 间最多 3 路并行；1200 秒；0 retry；只取首个 final。

## 唯一指令

只允许删除用户未要求的正文外过程旁白、协议或 JSON 泄漏、代码围栏和包装语。正文内容、顺序、标点、数字、状态和换行逐字不改。用户明确要求 Markdown 或稿件已经干净时逐字返回 D0。只输出完整终稿。

## 功能门

每个 case 都冻结唯一 expected 文本。有效调用必须 exit 0、无超时、首个且唯一 final 非空。功能 PASS 只看 final 是否与 expected 逐字相同：3 个脏稿精确清除目标包装，2 个反控逐字不变。任一 case 改写正文、遗漏内容、保留目标污染或误删用户要求格式，都记 FAIL；不追加样本救结果。

本轮通过后才设计 `CL-001` capability、span contract 和 coordinator 胶水；未通过则只按真实失败收窄提示。
