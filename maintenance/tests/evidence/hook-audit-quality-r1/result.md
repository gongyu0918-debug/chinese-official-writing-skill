# 六稿同 D0 默认 Hook 真实复放结果

固定 core 为 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f`，运行后确认该审计树干净。选稿和边界见 [preregister.md](preregister.md)。本实验使用已生成的真实 D0，不重新生成或人工改造初稿。

## 实际结果

六稿均完成 core 子进程事件重放和真实 CLI 续写。9 次模型调用全部通过 init、assistant、usage 三处模型名绑定；alibaba1 和 minimax 的原路线也可用，未使用替代 provider。六稿最终可见输出都与各自 D0 相同，`delivery_verified=true`；改稿 0，Hook 新增错误 0。这里的新增错误为与同一 D0 比较的增量，不表示初稿没有错误。

| 原稿 | finding | 真实续写次数 | 终态原因 | 终稿 |
| --- | ---: | ---: | --- | --- |
| alibaba2 / SHORT / baseline | 1 | 2 | replacement_retains_protective_pattern | 与 D0 相同 |
| alibaba1 / SHORT / candidate | 1 | 2 | empty_or_unchanged_candidate | 与 D0 相同 |
| ollama / EDUCATION / baseline | 1 | 2 | replacement_changes_sensitive_fact_object | 与 D0 相同 |
| opencode / EDUCATION / baseline | 0 | 1 | no_review_candidate | 与 D0 相同 |
| minimax / SHORT / baseline | 0 | 1 | no_review_candidate | 与 D0 相同 |
| minimax / EDUCATION / candidate | 0 | 1 | no_review_candidate | 与 D0 相同 |

三处命中均为 `multi-object-pending-tail`。alibaba1 判断 KEEP；alibaba2 将原因句改写后仍命中相同模式，机械门回退；ollama 将“尚未形成可执行的修订结果”改成“尚处于论证报批阶段”，机械门以敏感事实对象变化回退。没有一稿进入语义 verdict 阶段，因此本组不能证明最终语义核验有效。

CLI 报告的 usage 合计：input 39,092，cache-read input 291，output 40,110；`total_cost_usd` 合计 1.3245095。这是 CLI 报告字段，不是账户实际扣费证明。alibaba2 的首个修订响应耗时 162.687 秒，接近 core 默认 180 秒修订截止时间；本次没有超时。

## 原文人工复核

本组至少暴露以下未被默认 Hook 消除的问题；完整 D0 和终稿相同，可直接逐字核对，不把原稿问题计为 Hook 新增错误。

- opencode / EDUCATION 的第五项写“效果评价环节尚未启动”。原材料仅说数据尚未统一报送、效果尚待复核，不能据此断言评价未启动。第四项还把“正在修订”具体写成“目前处于论证和报批阶段”。这些新增现状没有产生 finding。
- minimax / EDUCATION 遗漏原材料的完整反馈日期 `2026年6月30日`，这也是冻结 fixture 的必保项。另给质量监测中心增加“意见系统管理”职责，而材料未提供该系统。默认 Hook 没有产生 finding。
- alibaba1 / SHORT 写“申请人按网站公开清单准备”，材料只给版本不一致及二次补件，未给申请人实际依照哪个清单。该具体行为宜作为待复核事实扩写处理；本次 locator 指向另一处原因分析句，没有检查这句。

不把合理未来措施、直接算出的 35%、或“整改尚未启动”对“整改工作尚未开始”的同义表达判为错误。正式总体错误率仍须由根代理按完整 20 稿和统一口径裁定。本组结论仅为：默认 Hook 在这六稿中保持了输出稳定，但未展示正文质量改善；无新错与能修正 D0 原有错误是两个不同结果。

## 复核入口

- [运行脚本](replay_real_d0.py)
- [持久化六稿和九次调用记录](frozen-evidence.json)：只存一次完整 D0 正文（与终稿相同）、两道原始请求、来源及终稿 hash、九次模型绑定与 usage。它保留完整正文用于核查，省去重复终稿和庞大的 stream。
- [未准入的日期原型说明](prototype.md) 与 [补丁](prototype.patch)。
- 完整 raw 仅保留在未提交的 `output/hook-audit-quality-r1/r1/`。其中 `summary.json`、`fixture.json` 以及逐稿 `source.json`、`d0.txt`、`events.json`、`final-visible.txt` 和各次 prompt、stream、stderr、reply、receipt 的对应指纹保存在持久化记录中。

原收据中的 `d0_sha256`、`final_visible_sha256`、模型回复 `final_sha256` 使用 UTF-8 正文和 LF 换行计算。Windows 输出文件写成 CRLF；持久化记录另加 `*_file_sha256` 保存原文件字节 hash。六稿既通过正文相等核验，导出的 D0 与可见终稿文件也逐字节相等。

当时运行的命令结构如下，机器绝对路径已去标识。`SOURCE_OUTPUT` 对应 `reference-route-audit-r1/r1` 的冻结输出，`BASELINE_TREE` 对应上述固定 commit，`NEW_OUTPUT` 对应本组全新输出目录；真实调用退出码 0，输入预检通过。

```text
python -B maintenance/tests/evidence/hook-audit-quality-r1/replay_real_d0.py --source-root <SOURCE_OUTPUT> --core-root <BASELINE_TREE> --output <NEW_OUTPUT> --run
```

归档校验：`replay_real_d0.py --help`、Python AST 语法解析、文档本地直链核验、六稿正文和九次调用收据 hash/绑定核验、`git diff --check` 均通过。未重跑模型、未运行全量测试。归档 wrapper 保持真实运行时的原字节，未将后续隔离参数修正混入本组。

这是真实模型回应参与的 core 事件重放，不能作为原生宿主插件安装、启用或同一原生会话运行的证明；也不是同稿七版修订链的证据。日期候选没有参与本组 core 运行。本轮只归档证据，产品文件已恢复固定基线，日期原型状态为 `NOT_ADMITTED`。
