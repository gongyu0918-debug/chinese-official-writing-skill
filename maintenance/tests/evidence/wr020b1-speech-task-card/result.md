# WR-020b1 讲话输入任务卡真实写稿结果

## 结论

`REJECTED_NO_MERGE`。讲话输入任务卡连续做了三次最小收窄，均未稳定阻止材料外职责、流程和任务扩张；R3 还把保护性自证写进正文。canonical 产品已恢复固定基线，不增加任务卡、节奏模板、段长规则或 Hook。

这不是等待补票的 HOLD。后续若继续 WR-020，只研究已有讲话稿中任务段的精确复核、搬移或删除，不再沿“首次起草前追加任务卡”重试。

## 固定环境

- 基线：`main@e3ed9bb374fd13234ea0eff9ea61c9e0f3cc7e69`。
- 宿主：Codex CLI 0.144.6；OpenCodex `opencode-go/deepseek-v4-flash`，`low`，无 fallback。
- 权限：read-only、ephemeral；两臂只读取相同的 canonical `SKILL.md`、`information-selection.md`、`genre-playbooks.md` 和固定 `longform-fact-pack.md`。
- 不联网检索、不启用 Hook、不修改真实写稿输出。

## 同题结果

| 臂 | 非空白字符 | SHA-256 | Token | 主要结果 |
| --- | ---: | --- | --- | --- |
| 基线 | 1016 | `489add894c4117a71fb24706a02047d44795cc822b7dc61cd6f008c650bdbbae` | input 67021，cache read 46592，output 1981 | 事实、三项结构和未决保障方式完整；但把13项退回材料扩成跟进任务，并出现“恢复不等于一辈子的隐患消除”等不自然表述 |
| R1 `2c34aee1` | 976 | `9d9caa8b3a1025dbab34014dde507ef622588aeb6c7a34b3e799d3549f322a3f` | input 82888，cache read 69888，output 3881 | 仍把13项写成当前重点；把未绑定主体的报价与风险材料交给“相关处室”；把“字段确认后再测试”扩大为相应工作不能推进；新增“工单要逐项见成效” |
| R2 `1d8b7720` | 851 | `d295ff0300f4ba9992a744c016ba8b149810b8fa01245f3412be3da9b763bafd` | input 168309，cache read 144640，output 2069 | 不再把13项单列为第四项，也没有明确指定报价材料责任主体；但新增“缺什么、谁负责对应”和“正式接入才能往前推进”，并产生病句 |
| R3 `304dcdf7` | 909 | `51d96aca0a2ae244de7e2007af40c7d64c46d25f0ff6efa6d904c18840be6ec5` | input 73365，cache read 65792，output 2052 | 新增会前准备、联络人为接口、对接部门和对外统计安排；再次把13项带入第一项任务，并把“不额外追加责任分摊”写进正文 |

三版候选都保持486=421+52+13、38分钟已恢复且原因在复核、3名联络人、两轮测试与3字段、三项工作和保障方式未定；拒绝依据不是机械逐字判据，而是候选独有的职责、流程、任务范围或直接可用性回退。

## 无效启动

两次基线启动在模型请求前失败，不计样本和费用：一次 PowerShell 管道未提供 stdin prompt；一次 `--ignore-user-config` 未同时注入 OpenCodex base URL/catalog，namespaced 模型被错误发往 ChatGPT 账户并返回400。另一次尝试加载本机用户配置时，旧 `agents` 项与 Codex 0.144.6 不兼容，同样在模型请求前退出。有效调用均显式使用进程内 `openai_base_url` 和 `model_catalog_json`，没有修改全局配置。

## 实际命令形态

```powershell
codex exec --ignore-user-config --ignore-rules --skip-git-repo-check `
  -C <baseline-or-candidate-root> -m opencode-go/deepseek-v4-flash `
  -c 'openai_base_url="http://127.0.0.1:10100/v1"' `
  -c 'model_catalog_json="C:/Users/admin/.codex/opencodex-catalog.json"' `
  -c 'model_reasoning_effort="low"' -s read-only --ephemeral --json `
  --output-last-message <ignored-output> <same-prompt>
```
