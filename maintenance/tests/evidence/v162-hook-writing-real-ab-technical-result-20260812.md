# v1.6.2 Hook 真实写稿 A/B 技术结果

## 绑定与执行

- 产品根：`0d53b3656e351020600b3754d1fe06ff2fc26ddd`
- 正式矩阵：`run-20260812-r2`
- OpenCode Go：`opencode-go/deepseek-v4-flash`，max
- Ollama：`ollama-cloud/deepseek-v4-flash:0731`，max
- Alibaba Token Plan 2：`alibaba-token-plan-2/deepseek-v4-flash-0731`，max
- 三条 provider lane 并行；每家内部 T1→T2→T3 严格串行；9 对、18 次、零重试、first final、单臂上限 1200 秒。
- 通过本机第三方 gateway 使用 Claude Code，不登录 Claude；每臂使用独立配置、临时目录和插件数据目录。

## 技术结果

- 18/18 arms 技术有效，9/9 pairs 技术有效，0 timeout，0 retry。
- provider 覆盖：OpenCode Go 3/3、Ollama 3/3、Alibaba Token Plan 2 3/3。
- case 覆盖：情况说明 3/3、制度正文 3/3、活动新闻稿 3/3。
- 9 个 Hook on 臂均有 UserPromptSubmit、PostToolUse、Stop 事件闭环，均保存 adapter turn 和 gate transaction。
- 9 个 Hook on 臂终态全部为 `TERMINAL_D0`，D1=0。该结果证明事件链和安全回退实际运行，不能据此宣称 Hook 改善稿件。
- 9 个 Hook off 臂均无 companion 注册、无 Hook event、无门禁数据。
- enabled 耗时为 27.703—216.953 秒；disabled 为 14.266—174.422 秒。独立采样不能把两组差值直接归为 Hook 固有开销，盲审后只作描述。

## 机械观察

- 18 稿均保留预注册的数字/日期核心 token；制度稿对“尚未确定”出现同义表达，新闻稿对“320人”出现空格或量词变体，故精确字符串检查显示缺词但不直接判事实缺失。
- 13/18 稿进入题面篇幅区间。Ollama T1 两臂和 Alibaba T1 off 均偏短；Ollama T2 on 偏短。该分布既有两臂共有，也有单臂差异，不能在解盲前归因。
- 机械结果不替代语义裁判；一般性的衔接或基于已给在办状态继续办理，不因措辞本身判外扩。只有新增具体主体、数字、期限、程序、结果、职责或改变已给状态时才计硬失败。

## 冻结哈希

- `manifest.json`: `b1640ac5769c1f1afdc56676666053b95dcb42ee169349067a218a3e927c9b36`
- `blind-packet.md`: `2171a88fda22e81c9523a075d733bdf3ddd158451f956aa43dcf7d1872196dbc`
- `mapping.json`: `303cd6a9e7f690a9a75600041ab49091220875de9d81b2b41d016f70ab754a14`
- `blind-verdict-template.json`: `68fe673257e5f2c04fd0598753011fcfd5a27885f8ea7c3cdd497a592571c8e7`

本线程生成此技术摘要时未读取 `mapping.json` 或正文；mapping 只以文件哈希封存。三名独立裁判完成并冻结原始结果前不得解盲。

## 无效 R1

R1 因 OpenCode Go 与 Ollama 的模型路径规格写错被整批判 `MODEL_ROUTE_SPEC_INVALID`。终止时 8/18 arms、4 pairs，未生成终态盲包；所有进程已终止，正文未读取、未评分、未并入 R2。R2 从全新目录按修正后的精确路径完整执行。
