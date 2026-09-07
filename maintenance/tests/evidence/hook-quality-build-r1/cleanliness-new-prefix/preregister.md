# “以下正文”新前言：一次同稿真实清理

唯一来源为本轮 `continuity/native-r4-minutes/round-5` 原生真实会话的 stream result，须与 assistant 正文及 final.txt 一致；请求逐字取该轮 invocation。原稿首段以“以下正文约”开头，未含“是／为”。期望仅删除第一段及横线，后续正文全字节保全。

只使用当前 `delivery_cleanliness` runtime，冻结副本及来源哈希，不改产品。Alibaba Token Plan 2 DeepSeek V4 Flash 0731，max，既有空工具 restricted_reply，每次 180 秒、0 retry，最多 4 次真实调用。按现有 revision／verdict／echo 原文执行，不注入人工候选或 PASS。

成功条件是选择 D1、真实语义核验通过、最终回显哈希等于冻结正文，`delivery_verified:true`。本次仅验证清理能力，不代表当前默认入口已匹配此前言，也不是新一轮原生 Hook 生命周期。正文超 500 字和原有事实错误均不算本清理目标；失败就停，不扩模型或测试矩阵。只有成功后根代理才考虑入口新增“以下正文”匹配。
