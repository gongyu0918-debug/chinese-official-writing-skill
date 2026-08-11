# Hook 纯审稿放行原子预注册

## 固定对象与问题

- 固定输入提交：`6a3745421b77c651a1d0a9ffc51654beec7bd368`。
- 仅修改共享 Hook 桥及其 Codex、Claude adapter 测试；不改 `review_gate.py`、`prose_lint.py`、references、Skill 正文或包构建器。
- 已在固定提交复现：请求“只审查这份采购申请，不要代改，不重写全文”，模型已读取本 Skill，并交付非空审稿意见；当前 Stop 仍创建 transaction，进入 `AWAITING_REPAIR`，返回 `decision=block`。

## 单一候选

在共享 Hook 桥中增加窄域 review-only 判定。`只审查`、`只复核`等自身已明确限定交付模式；普通审查、检查或复核请求还须同时明确限定不代改或不重写全文。命中时 Stop 直接放行，不创建 transaction。Codex 桥与 Claude adapter 共用这一判断。

以下请求必须继续进入原门禁：

- 起草、撰写正文；
- 修改、改写、润色正文；
- 审后改写、复核后修改等同时要求交付新正文的任务。

## 固定验证

1. focused：`tests.test_gate_stop_hook`、`tests.test_claude_gate_adapter`。
2. full unittest、stub smoke、固定 deterministic ablation、quick validate、镜像同步幂等和 `git diff --check`。
3. 接受条件：四组纯审稿表述均放行且无 transaction；起草、改稿和审后改写控制仍触发；Claude adapter 行为与共享桥一致。

本原子只修复 Hook 对交付模式的误判，不评价写稿质量，不运行模型。
