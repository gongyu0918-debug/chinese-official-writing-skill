# 真实稿件的命令路径验证

根代理取R5两路模型实际交付且已核对事实、日期、联系人与未决状态的两份完整通知，原字节复制到带空格的最小项目目录。两稿分别作为同一输入执行原reference命令与引号绝对路径命令，完整正文、来源hash、实际argv及stdout/stderr见 [execution-evidence.json](execution-evidence.json)。没有新模型调用，也没有改造原稿来制造命中。

脚本固定为 `5fbb2d26` 的 `prose_lint.py`，位于项目 `.agents/skills/chinese-official-writing/scripts/`；工作目录为项目根。这里只构建命令所需的最小文件布局，不声称已完成原生Skill安装或Hook启用。

| 实际输入 | 原命令 | 按已读Skill目录解析、脚本与稿件路径加引号 |
| --- | --- | --- |
| Alibaba2真实候选终稿 | exit 2，项目根不存在scripts/prose_lint.py | exit 0，No prose risks found |
| MiniMax真实候选终稿 | exit 2，同一相对路径问题 | exit 0，No prose risks found |

两稿扫描前后字节均未变化。执行由根代理调用本机Python原生进程，使用替换路径后的文档命令解析出的argv、`shell=False`；不是模型自己在原生Shell中选择命令的A/B。这里只证明路径说明可执行；exit 0表示扫描完成，不能替代事实、文种或正文质量判断。

绝对路径原型为 `5cb696fe`。stdout/stderr、四次退出码和正文原始hash均保留，不把这一命令正确性结果当成stdin提示或源码阅读路由的减载收益。

最终已同步canonical与五套普通镜像，每套仅改SKILL脚本段和final-review工具段。[集成检查](integration-check.json)的 `restores_baseline_exactly` 表示撤去各处路径说明增量后逐字恢复基线，不表示当前产品与基线相同；[主代理复核](root-verification.json)另核对12份受限真实稿的正文、三层模型绑定、实际工具与可见读取量，未把该静态检查当真实减载。
