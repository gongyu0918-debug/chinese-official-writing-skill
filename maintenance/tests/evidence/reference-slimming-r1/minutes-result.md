# MINUTES-CHECKLIST-LEAF-R1 真实 A/B 结果

日期：2026-08-28。终态：`REJECTED_INSUFFICIENT_ATTRIBUTABLE_LOAD_BENEFIT`。

## 结论

把通用文种检查页的会议纪要小节合并到既有会议纪要叶，没有证明真实减载。五条低成本路线完成4题双臂40份真实正文；39份技术有效，MiniMax通知控制Candidate读取用户级同名Skill，按预登记记 `INVALID`。15个纪要目标配对均技术有效，但Baseline读取`genre-checklist.md`为0/15，因此0/15满足“Baseline读取通用检查页、Candidate停在纪要叶且总加载下降”的可归因条件。

静态上，通用检查页由7423降至7128字节，纪要叶由2044增至2374字节；真实调用中Baseline本来就自然停在入口、轻量卡或纪要叶。Candidate有时少读轻量卡，也有时把原本只读入口的路线引向纪要叶，字节变化在-24848至+9924之间，不能归因成删除通用检查页的稳定收益。

## 真实稿复核

- 噪声转写、整体未决和已议定责任期限共30份正文均实际生成。口头修正后的9月5日至9日、未回应建议未形成决定、备份参数待核验、A/B方案未表决、三项责任与期限总体保持。
- Candidate没有形成跨provider、可由本次搬移解释的事实、状态、责任绑定或文种硬回退。Ollama未决Candidate增加“证据缺口有待补齐”“再行研究”，MiniMax噪声Candidate增加未给的“同志/有关负责同志”，均未跨provider复现；MiniMax该题又没有读取改动叶，不能作为本原子阻断。
- 通知控制的有效Candidate没有读取纪要叶，也没有出现纪要语体污染。MiniMax Candidate因用户Skill污染作废，不补跑。
- 首版字符串检查把否定保留的“立即扩大到全部单位”、允许省略的“未明确完成期限”及“1名/1人”词形计为告警。独立复核后这些只作观察；结果不以这些机械告警判质量失败。

## 终态

- Candidate提交：`97a2dcbc4ec08fbc9927879a97da8582fed962de`。
- 目标路由：0/15通过；原因全部包含Baseline未读取通用检查页，非技术失败或裁判过严。
- 控制污染：有效配对0；技术无效1臂。
- 产品恢复固定Baseline，不同步镜像，不改Hook、包体、description、版本或发布坐标，不合入main。

## 命令与证据

```powershell
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment minutes --prepare e218d353f279eecb0761a58fcc59ad05e0fb5eb1 97a2dcbc4ec08fbc9927879a97da8582fed962de
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment minutes --provider <alibaba2|alibaba1|ollama|opencode|minimax>
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment minutes --summarize
```

- `output/reference-slimming-r1/minutes/fixture.json` SHA-256：`50E17A6E28D10965C0F53F91236328563C843CBE205A93556D04EDEE4718761B`
- `output/reference-slimming-r1/minutes/summary.json` SHA-256：`BD694F98B68166C23AA8A5CD5112453CE3C7CD3915907C89127C0633316EE434`
- 原始final、trace和stderr位于同一忽略目录；提交证据只保留预登记、runner和终态摘要。
