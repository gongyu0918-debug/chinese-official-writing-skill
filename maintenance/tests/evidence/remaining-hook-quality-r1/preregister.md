# 剩余 Hook 与写稿规则修复 R1

固定基线 `37f22146f64cf2dfcaea7a8a5afba40750215803`，独立分支 `codex/remaining-hook-quality-r1`。用户授权继续修复，涉及写作时使用现有低价模型真实测试，也允许修改有问题的 reference。main、平台版本和付费增量不在本次候选修改范围。

## 原子与准入

- HK-008：复用真实 D0，在独立进程中暂停 bootstrap、触发 HostAbort、再恢复；另外实占状态锁后取消，再恢复事件。先复现原文重建和取消丢失，再接必要的精确路径清理、取消标记和相邻反控。
- HK-005b：核对各宿主实际协议，不能假设 `continue:false` 意义相同。DSH先用本机SDK及无网络MockAdapter执行真实AgentLoop，检查aborted、保留排队用户请求及无自动第二请求；OpenCode分开记录插件停止、宿主完成和不可撤回的已显示正文。
- AH-002b / WR-020c：先做固定上下文、无工具的真实写稿和同稿修订原型。两家模型为 `alibaba-token-plan-2/deepseek-v4-flash-0731`、`minimax-cn/MiniMax-M3`，均max，无自动重试或模型回退。初稿新闻与旧真实D0的删除、插段各自计数；不把注入上下文称为模型自然读取。

`output/remaining-hook-quality-r1/writing-prototype-r1/fixture.json` 在12次调用前固定上下文和题面。R1的多轮规则出现候选独有漏删，拒绝。R2在6次调用前另存fixture，缩小修改范围及新增段落事实边界；新闻页消融掉泛化推断和动作核验新增句，只保留完整事实日期的规则。原稿、题面、receipt与失败记录均保留，不覆盖旧轮。

只有目标风险改善且无候选独有硬回退才接入产品；后续真实链失败时修候选或停止，不以增样和工程门覆盖失败。

## 七版真实会话

原子通过后，在清洁的独立测试worktree中运行[现有七轮驱动的薄封装](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/remaining-hook-quality-r1/run_chain.py)。两臂两路线，共4个独立session、28版正文；第2—7轮使用真实 `exec resume`，只发送原来的增量任务，不重拼历史。题面沿用[原七轮配置](../revision-stability-audit-r1/cases.json)，只更新两臂commit。原始初稿→更新统计→调序→删除→新增独立段→650字符压缩→只撤销调序。此阶段不启用Hook，不代表compaction或任意长度稳定性。

实际命令计划：

```text
python -X utf8 -B maintenance/tests/evidence/remaining-hook-quality-r1/run_chain.py --prepare --output-root output/remaining-hook-quality-r1/chain-r1
python -X utf8 -B maintenance/tests/evidence/remaining-hook-quality-r1/run_chain.py --provider <alibaba2|minimax> --arm <baseline|candidate> --output-root output/remaining-hook-quality-r1/chain-r1
python -X utf8 -B maintenance/tests/evidence/remaining-hook-quality-r1/run_chain.py --summarize --output-root output/remaining-hook-quality-r1/chain-r1
```

本文件首次提交时，七版链尚未执行。逐版分开判断事实、状态、篇幅、结构和指定修改；继承的旧稿问题与本版新增问题分开，R6未冻结段落边界，不把压缩合段判成硬错。技术失败保留并停止该链，不静默补样。统计相关版本轨迹，不推算百稿正确率。

## 查阅与复用

[新闻职业准则](https://www.xinhuanet.com/politics/2019-12/15/c_1125348618.htm)用于核对新闻事实与情节保真；[Anthropic文档编辑Skill](https://github.com/anthropics/skills/blob/main/skills/docx/SKILL.md)提供按位置做最小替换的现有方法；[其社区问题27137](https://github.com/anthropics/claude-code/issues/27137)仅作为全文覆盖导致遗漏的观察，不当作本仓库因果证明。具体宿主协议与源码查阅记录随宿主结果保存。
