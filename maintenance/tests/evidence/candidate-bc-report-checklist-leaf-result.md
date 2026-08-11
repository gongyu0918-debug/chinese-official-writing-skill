# Candidate BC：报告检查项原子拆叶结果

结论：`PASS`。固定底座为 Candidate BB 产品提交 `ed803c4`，Candidate BC 产品提交为 `522cb2fbde3b0fbf475e297728c80554bf736ea7`。

## 实际改动与减载

Candidate BC 只把 `genre-checklist.md` 中 4 条报告检查规则原文移入同级叶子 `genre-checklist-report.md`，并从 `SKILL.md` 和报告 playbook 建立直达路径。报告叶子为 156 字符，Candidate BB 全量文种清单为 3705 字符；报告细查路径减少 3549 字符。通知、纪要、请示等其他文种路由未改。

六套发行镜像中的新叶子 SHA256 一致。Candidate 三题均实际读取 `genre-checklist-report.md`，Baseline 三题均实际读取原 `genre-checklist.md`；其余主要写稿与复核 reference 对称。

## 工程验证

- 全量 unittest：Candidate 新增路由测试和同步后的旧覆盖测试均通过；共运行 352 项，仅继承 1.5.19 的 README 旧数字断言失败。该断言仍期待 `349/349`，而 1.5.19 README 已写 `350/350`，与本次拆叶无关，发布分支更新当前工程统计时修复。
- Promptfoo smoke：首次由 npm 包装器运行时错误继承 Hermes Python 路径，产生 20 个 provider 启动错误；改用已核验的系统 Python 3.13 直接运行后 20/20 通过，0 failed，0 errors，Skill 10/10，judge consistency 1.0。
- 固定 Candidate BB 确定性消融：Baseline 108/108，Candidate 108/108。
- quick validate、镜像同步、镜像哈希一致性和 `git diff --check`：通过。

首次工程门还暴露旧测试固定要求“报告”必须位于全量清单。该测试同步为在“通用清单 + 报告叶子”的覆盖集合中核验，产品规则未改；调整后相关两项测试通过。

## 真实写稿 A/B

三题均为正常自然语言报告任务，不含 P0 风险词或目标答案：公共停车场暑期运行报告、馆藏档案数字化进展报告、暑期课程预约试运行报告。Candidate BC 与 Candidate BB 均使用 `gpt-5.6-sol / ultra`、逐字一致输入和首个技术有效输出，不补抽。

匿名映射由任务编号和两稿 SHA256 确定：T01 Candidate=B，T02 Candidate=B，T03 Candidate=A。独立 judge 仅读原任务和匿名稿，结论为：

| 任务 | 匿名结论 | 解盲结果 |
| --- | --- | --- |
| T01 | B 胜（小胜） | Candidate BC 胜 |
| T02 | B 胜（微弱） | Candidate BC 胜 |
| T03 | A 胜 | Candidate BC 胜 |

三题六稿的事实、数字、日期、主体、状态、文种、格式、篇幅和只输出正文均通过；没有 P0 保护性外扩，也没有单篇同一机制达到 3 处。盲审发现的边缘材料外概括与重复复盘均为单例，不升级为共性风险。

## 判定边界

Candidate BC 达到“至少 2/3 持平或胜出且无硬回退”的预注册门槛，保留进入 1.5.20 发布候选。3/3 的语言结果受生成噪声影响，不宣称全部来自 3549 字符减载；可确认的是路由减载成立，真实写稿未观察到质量回退。

原始稿、匿名包、映射和盲审留在忽略目录 `output/candidate-bc-real-ab/`，不进入发行包。
