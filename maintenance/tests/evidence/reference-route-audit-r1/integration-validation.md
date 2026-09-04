# 本轮集成验证与提交前复核

独立分支 `codex/reference-route-audit-r1`，固定基线 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f`。最终产品只采用 `5cb696fe` 的命令路径说明，完整命令试验取自 `codex/lint-command-route-r1@c7b9ff607fda54ce22e3f5cb304e707d050360f0`。

## 产品准入与精确范围

[两份真实稿件的四次原生命令](../command-cwd-real-draft-r1/result.md)先证明相对路径失败、绝对路径执行成功，正文逐字不变，再同步 canonical 和五套普通包。每套只改 SKILL 脚本段与 final-review 工具段各一行，分别增加120、152 UTF-8/LF bytes。产品脚本、Hook、description、其他写稿路由、红头/付费实现与 red-skillhub 发布包均无增量。

[精确范围与轻量消融](../command-cwd-real-draft-r1/integration-check.json)核对12个运行时文件：各自撤去这一行路径增量后逐字等于固定基线；canonical 两文件逐字等于获选路径原型。全局五行路由、stdin/help提示和源码读取条件均未进入最终产品。真实原命令/新命令使用同一稿件，另保留20稿与R4—R6各自原型开关的真实结果；不以静态还原替代真实准入。

## 实际命令与结果

在本工作树执行：

```text
python -B -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_core_lint_pointer_relocation maintenance.tests.test_hook_layer_contract
```

89项通过，2.316秒。首次运行有1个失败：旧测试硬编码压缩前AGENTS的六处原句；改为压缩后的相同纪律、历史归档链接与唯一活动指令断言后重跑通过。没有移除纪律检查。路径测试原来的相对命令断言也更新为带引号的绝对路径及已读SKILL目录来源。

```text
python -B -m unittest maintenance.tests.test_repository_reachability maintenance.tests.test_status_ledger_consistency
```

23项通过，0.586秒。两组共112项直接回归。基线早先159项审核结果另记[冷审](audit-findings.md)，不与本次相加成独立测试覆盖量。

quick_validate 实际由以下本机解释器分别执行5次：

```text
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py packages/agent-skills/skills/chinese-official-writing
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py packages/qwen-code/skills/chinese-official-writing
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py packages/qwenwork/skills/chinese-official-writing
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py packages/hermes/skills/chinese-official-writing
```

5次均exit0、`Skill is valid!`。默认Hermes Python及Codex bundled Python各一次先因 `ModuleNotFoundError: No module named 'yaml'` 失败；改用已安装PyYAML的Python313，未安装依赖或改系统配置。OpenClaw的特定frontmatter与无Hook普通包边界由上述仓库专项契约检查，不冒充通用validator验证。

## 证据复核

[导入收据](../command-cwd-real-draft-r1/import-receipt.json)列出193份证据的源commit和逐文件SHA；[主代理复核](../command-cwd-real-draft-r1/root-verification.json)再次核验全部原字节，并从12份原始stream独立核对init/assistant/usage三层模型、实际两项工具、空skills/plugins、正文hash，以及每条可见读取响应的字节和SHA。9次完整源码请求都对应宿主持久化预览；服务端返回量不替代可见量。

主代理直接阅读R6全部四份正文并与原通知核对：MiniMax控制遗漏独立的发言名单限制；两候选没有独有实质错误；Alibaba候选复扫与最终回显的空白差异单列，不误判为事实错误。R6没有两路线一致减载，按原门收口，不继续增加模型尝试。193份导入文件的令牌、Authorization值和私网IPv4模式扫描零命中；这不是对通用Shell安全的认证，R3原始越界尝试仍保留。

首次暂存blob检查在旧失败fixture处发现字节不一致：`git archive`按checkout换行设置把96份源Git的LF文本导出为CRLF。最终改用 `git cat-file --batch` 读取源commit原始blob，逐份核对源Git、本地文件和暂存blob，193份全部一致；导入收据保留原导出hash及修正记录。受保护的R4—R6原始stream未变化，未回写任何源commit、原实验manifest或模型结果。

第10次提交前按范围扩大做独立review与主代理复核；AGENTS关键纪律、51项原需求/59条覆盖基数和本轮5个子项均核对。review指出specs/README仍称命令“未准入”、消融字段缺少解释；已统一终态并说明逆向复原的含义。[最终链接/结构收据](final-checks.json)记录24份活动及新增报告的本地链接与表格检查，零缺失/列宽错误；`git diff --check` 返回0。原始证据按各自.gitattributes保留字节并另核对Git blob，换行问题不靠改实验hash清单消除。

## 未完成与边界

本轮没有可准入的Skill整体减载；AGENTS减15.12%只计开发纪律。四项Hook冷审缺陷和默认定位器事实漏检尚未修复；日期真实D0本批未复现，不应用候选。没有运行新的原生多宿主Hook生命周期、合并/发布全量门，也没有合并main、推送、移动tag、修改安装或操作付费版。
