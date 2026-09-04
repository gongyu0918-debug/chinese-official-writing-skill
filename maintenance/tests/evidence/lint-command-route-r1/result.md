# 命令路径与源码读取实验：最终交付状态

只集成绝对路径文档修正；R4/R5/R6的stdin/help及源码读取条件未准入，已全部撤回。最终两个产品文件与 `5cb696fe` 逐字节相同，保留路径解析、引号绝对路径示例、exit0仅表示扫描完成和提示性lint原有边界。主代理另以两份真实终稿执行原命令/绝对路径命令，路径可执行性收据由主代理单独整合，不混作模型省读证据。

## 集成范围

- `chinese-official-writing/SKILL.md`：相对固定主线 `5fbb2d26` 仅补120 bytes脚本路径解析说明；最终27267 bytes，SHA-256 `094e214bdd8e32d0ee69dfad2e3a796a08557e35a531e19ba18748365510ebc8`。
- `chinese-official-writing/references/final-review-layers.md`：相对主线仅补152 bytes，引号绝对路径及返回码语义；最终9029 bytes，SHA-256 `0204ee133951e5ca0839312e8c60524d2edc529161e9b2846a314e1e7232e546`。
- `maintenance/tests/evidence/lint-command-route-r1/` 整个证据目录，含原始失败、合成原稿、冻结产品/模型/脚本hash、受限stdio工具与runner、所有完整真实正文/trace/工具输入输出、usage和判读。无其它产品、Hook、镜像或规格文件变化。

中间产品原型只保留在历史commit及各轮fixture中，不从中间commit合并产品。没有修改主工作树、合并、推送、tag、平台发布、系统代理或注册表。

## 分轮结果

| 轮次 | 冻结产品/宿主 | 真实结果 | 最终处理 |
| --- | --- | --- | --- |
| R3原生命令 | 产品 `5cb696fe`；归档 `9d096085` | 4份完整稿未见正文实质错误；路径提示没有可重复的自然命令收益，Alibaba2候选出现已保留的工具越界尝试 | 原始失败与越界命令保留；不再运行任意Shell模型harness。路径文字的可执行性依主代理独立真实稿命令收据判断 |
| R4叶页提示 | `9e9f5575`，归档 `f1ce9db` | 4份正文无观察实质错误；4份均请求整份源码；MiniMax未读取新增句所在叶 | 未准入 |
| R5入口提示 | `4cd78c01`，归档 `7e9ca23d` | 4份均请求整份源码；Alibaba2控制遗漏发言名单限制，候选无独有硬回退 | 未准入 |
| R6条件提示 | `70d3c596` | Alibaba2源码请求1→0，MiniMax0→0；可见文档响应分别−10536/+67774 bytes，MiniMax控制也有同一限制遗漏 | REJECTED_NO_CONSISTENT_LOAD_GAIN；撤回提示，收口 |

R3使用原生命令接口，R4—R6使用固定ID读取与固定stdin lint两个MCP工具；不同接口不合并成同一A/B或一般无错率。完整判读：[R3](r3-result.md)、[R4](restricted-r4/result.md)、[R5](restricted-r5/result.md)、[R6](restricted-r6/result.md)。

读取量已纠偏：[12份受限稿读取面复核](reading-surface-audit.json)逐个对应真实tool_use/tool_result及trace SHA。服务端返回的文档bytes与宿主可见响应bytes分列；9次源码响应均被Claude持久化为约3.3KB预览，不能声称58290-byte源码完整进入上下文。R4/R5原始hash/fixture/raw没有回写。

## 实际验证命令

三个受限批次各先冻结后执行现成无模型门：

```text
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --prepare --output-root output/lint-command-route-r1/restricted-r4-r2
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/check_contract.py output/lint-command-route-r1/restricted-r4-r2
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --prepare --output-root output/lint-command-route-r1/restricted-r5
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/check_contract.py output/lint-command-route-r1/restricted-r5
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --prepare --output-root output/lint-command-route-r1/restricted-r6
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/check_contract.py output/lint-command-route-r1/restricted-r6
```

R4：两臂各19项MCP检查PASS、模型0。R5/R6：各同样38项MCP检查及8项初始化流反控PASS、模型0。三轮共12次真实模型命令逐条列在各轮结果中，各自的 `invocation.json` 保存实际Claude argv/cwd/prompt，`tool-calls.jsonl` 保存固定Python argv及stdin/stdout；所有完成调用技术违规为 `[]`，真实init及实际tool_use只有2项，无技能/插件加载。

最终对恢复后的产品实际运行：

```text
python -X utf8 C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing
git diff --check
```

quick validate输出 `Skill is valid!`。另以只读Python核对R3及三个受限批次共141个文件hash、全部报告直接链接/表格列宽、实际工具和模型绑定、两产品文件精确还原控制；提交前再核对暂存Git blob与证据原字节一致。未重跑主代理159项全量测试，不声称本分支运行了它们。

主代理已另行准入两处路径说明并窄同步五套普通包，报告其主树直接测试89项PASS及五份quick_validate PASS（OpenClaw专项契约）；这些是主代理的集成验证，不冒充本分支运行。当前本分支只交付最终路径产品与完整证据供主代理窄复制，没有剩余模型试验或本方向待推进原型。
