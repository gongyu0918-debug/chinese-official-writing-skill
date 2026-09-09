# 四项 Hook 修复合入 main

用户授权“如果合理合并就进行合并”后，已将本地 main 从 `3532afd6619ac6256558e9552b92d03da5ae9c0f` 快进到 `3ce9241eab6bc26d45e1b9b63371da119d0cb123`。该提交包含原四项修复及合并前发现的显式关闭回退修正。[合并回执](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/merge-receipt.json)确认 main 清洁；未推送、未发布，`v1.6.27` tag 不变。本文及规格更新属于之后的文档提交，不改变产品。

## 合并依据

- `ee8ef489` 相对 main 的产品差异仅五个 Hook 文件，Skill、references、兼容镜像和版本文件不变。上一发布 tag 是祖先，85份冻结证据的Git blob哈希全部一致，公开产品没有付费提纲、红头、维护证据或缓存文件。[范围检查](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/scope-check.json)
- 先前[四项结果](../hook-four-fixes-r1/result.md)的真实同稿收益与未完成边界继续有效；没有改写源稿质量失败或旧审查失败。
- 第一次合并前全量 **787/787通过**，但主代理随后用真实D0复用、明确关闭请求和受控锁竞争发现新的关闭指令回退。该新反例优先于旧测试通过，故没有直接合并旧候选。[首轮全量](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/full-tests.json) [反例](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/optout-probe.json)
- 最小修复仅将显式关闭、无事务的分支前移到迟到Skill标记同步前，并允许该分支清理锁不可用时交付。活动门禁锁失败仍明确停止。独立复核指出了标记先写入的遗漏，最终补丁与测试通过复核。
- 同一真实D0的关闭请求变体中，基线允许、修复前候选阻断、最小候选允许；原文因清理锁不可用而暂存的限制未隐藏。[原型对照](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/optout-prototype-result.json)
- 三项定向测试覆盖显式关闭的锁竞争/I/O异常/迟到标记，以及活动门禁的相邻反控。之后对最终提交重新运行全量，**788/788通过，110.402秒**。重复全量由新发现与代码修改触发。[最终命令与输出](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/full-tests-final.json)
- 最终产品仍只改上述五个Hook文件；85份旧证据blob、18份新增原始文件、86个包文件逐一核对，323个本地文档链接与349条JSON记录通过结构检查。[最终范围与文档检查](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/final-scope-and-doc-check.json)；新增原始文件及该检查回执的字节hash见[清单](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw-manifest.json)。

```text
python -X utf8 -B -m unittest discover -s maintenance/tests -p "test_*.py"
git merge --ff-only 3ce9241eab6bc26d45e1b9b63371da119d0cb123
git diff --check
```

实际全量使用Python313，精确解释器路径见回执；合并使用 `--quiet` 抑制文件清单。

## 最终原生与包检查

以现有Claude Code 2.1.195、Alibaba2 DeepSeek V4 Flash、max和隔离profile完成一条最终原生关闭Hook链。模型实际只读当前Skill及新闻叶，输出正确完整年份的正文；在清理调用点明确注入 `RecordLockUnavailable`，唯一Stop仍返回 `continue:true`，没有自动续写。原生事件、模型绑定、完整正文与源码hash均保留在 [native-optout](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/native-optout/result.json)。这里的锁失败是故障注入，不是自然发生率；也未声称该路径已完成脱敏。

该运行复用已提交的 `run_native_claude.py`；[补充驱动](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/run_native_optout.py)冻结为当时在 `output/hook-four-fixes-r1/merge-check-r1` 执行的原始文件。它通过模块内配置添加明确关闭请求并注入清理失败，不修改canonical。复跑应按原相对目录放置驱动，并使用新的输出目录，不能覆盖旧证据。

五套quick validate通过；86文件干净SkillHub验证包无禁入文件。最终包相对补充修复前仅core文件不同，原始字节树fingerprint为 `621e98ed3fa5c082bd4355c3ab2fc946767e1a3d24c57059c23e0781d5960f50`，算法和逐文件hash以[最终包回执](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-merge-r1/raw/package-check-final.json)为准。包用于本地合并验证，不是平台提交，不代表同号版本更新。

## 后续修复顺序

1. **原文清理闭环（HK-008）**：启动中的Stop在HostAbort之后重建输入文件；锁不可用时留下待处理记录。先用同一真实D0和实际取消生命周期验证清理，不扩大为泛化协调器。
2. **失败状态传递（HK-005b）**：CodeBuddy、Kimi、OpenCode、DeepSeek Harness仍可能把core硬停当allow；Codex、ZCode、Qwen还需当前原生验证。CLI成功、停止续写和正文已通过核验必须分开；已显示文本不能被Stop撤回。
3. **真实成稿事实与日期（AH-002b / WR-020c）**：自然D0会漏年，也会新增未提供的“交流读书心得”。下一步应在明确事实来源的前提下补全年份，并定位活动内容外扩，不能继续以“保持D0”代替质量通过。
4. **4—7版修改稳定性（WR-020c）**：继续处理旧稿事实回流、指定删除不完整、插段和调序破坏硬锚等已登记问题；逐项用真实连续修订验证，不能用确定性测试数换算成稿可靠率。

付费候选的共享修复同步继续由其专属任务负责，公开 main 不引入付费增量。本次合并不改变这些未完成状态，也没有新的百稿可靠率结论。
