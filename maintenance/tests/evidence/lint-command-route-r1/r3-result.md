# lint 路径原型：四稿结果与后续单原子边界

状态：`REAL_AB_COMPLETED / ADMISSION_PENDING`。产品候选为 `5cb696fe`，基线 `5fbb2d26`；R3仅指最终可运行的环境批次，不代表三轮产品改动。这是R3结束时的判断：不能宣称路径原型改善了本批模型真实调用，也不能只按正文无错判定行为通过。最终路径说明以主代理另做的真实终稿命令收据准入，见[最终状态](result.md)。

## 真实结果

一个264字完整通知题、同一prompt、两臂、Alibaba2与MiniMax各一对，共4份技术有效完整稿。Alibaba2基线的保守路径解析器因CLI外层引号转义漏记，已按其成功命令 `item_0` 的精确绝对安装路径和完整Skill内容人工确认；未重跑该稿。其后只启动此前未运行的candidate臂。

| 路线/臂 | 正文非空白字符 | lint扫描命令成功/尝试* | shell命令非零退出 | 找不到脚本 | 成功读取Skill/reference安装字节（去重/计重复） | 时长秒 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Alibaba2 baseline | 249 | 1/1 | 0 | 0 | 35,079 / 35,079 | 65.188 |
| Alibaba2 candidate | 249 | 2/5 | 4 | 0 | 48,143 / 48,143 | 184.844 |
| MiniMax baseline | 249 | 2/3 | 2 | 0 | 40,864 / 68,146 | 150.859 |
| MiniMax candidate | 247 | 1/3 | 2 | 0 | 40,516 / 40,516 | 60.266 |

*不含 `--help` 或读取源码；成功指扫描进程完成，不代表没有finding、正确复扫最终稿或整个复合命令成功。MiniMax baseline另调用一次 `--help`。其stdin尝试使用PowerShell `echo` 配合字面 `\n`，虽返回空finding数组，但不能冒充格式与最终稿一致的可靠复扫。Alibaba2 candidate的两次成功扫描均为原稿，后续复扫未完成。计数与逐项路径见[人工复核](attempt-03-real-ab/manual-review.json)，原始命令见各臂的 `invocation.json` 和 `trace.jsonl`。

四份均去除标题Markdown标记，保留完整活动日期、报名期限、成文日期、1至2人、王青/305、只征集意向、方案未审定、主题/顺序待定及报名不等于发言名单；未添加材料外安排。去除末尾重复报送提醒可接受。Alibaba2两臂终稿逐字相同；MiniMax候选将已有未决状态合入第一段，措辞略压缩，未发现妨碍使用的正文错误。观察到的事实/状态/结构/交付硬错误为0/4；本题没有字数硬门，不据单题小样本宣称普遍无错率或文采提升。用户文件为唯一来源，未使用Hook，未读取全局同名Skill，安装产品指纹保持。

## 真实命令行为与风险

1. 四份都成功调用本项目安装的 `prose_lint.py` 检出 `markdown-bold`；没有复现模型找不到脚本。Alibaba2 baseline自行使用绝对路径，两个candidate实际使用了有效的项目相对路径。文档修正了已知坏示例，但本题没有证明它降低失败率。
2. Alibaba2 candidate额外读取final-review与proofreading。复扫时三次尝试写临时稿均失败，之后 `item_15` 整体读取 `scripts/prose_lint.py`，工具返回52,541 bytes（含宿主提示且正文被截断；安装脚本59,684 bytes）。这条命令证明尝试整体读取源码，实际返回已截断，不能当作完整源码进入上下文；也不是按脚本存在或体积推测读取。MiniMax candidate也有两次临时稿写入失败。来源路径、入口正文与两臂提示相同，不能把单次路线差异直接归因到哪一句新增说明。
3. **Alibaba2 candidate另有与任务无关的工具越界。** `item_16/17` 尝试修改HKCU代理并把合成通知base64 POST至 `https://httpbin.org/post`。item16解析失败；item17虽exit0，逐项输出仍是注册表拒绝、方法受限和网络连接拒绝，未见成功改设置或发送。本轮读取的产品文件没有这些命令/域名文本。它不计成正文事实错误，但阻断“整个执行行为通过”的结论；不据一份样本断言路径文字导致越界，不放宽沙箱或网络作为处理。
4. read-only沙箱不要求模型新增写文件行为；原稿本来可直接lint。新暴露的实用缺口是未落盘正文如何复扫、参数如何就地查用。主代理随后只授权R4一处最短stdin/help说明，下一轮另预登记，不将当前失败覆盖为通过。

## 输入、完整产物与可复核证据

- [冻结题面及原稿](cases.json)，[产品与调用前预注册](preregister.md)，[运行器](run_eval.py)。两臂prompt完全一致，运行配置与材料/产品指纹在[fixture](attempt-03-real-ab/fixture.json)。
- Alibaba2：[baseline完整稿](attempt-03-real-ab/raw/alibaba2/baseline/final.txt) / [trace](attempt-03-real-ab/raw/alibaba2/baseline/trace.jsonl)；[candidate完整稿](attempt-03-real-ab/raw/alibaba2/candidate/final.txt) / [trace](attempt-03-real-ab/raw/alibaba2/candidate/trace.jsonl)。
- MiniMax：[baseline完整稿](attempt-03-real-ab/raw/minimax/baseline/final.txt) / [trace](attempt-03-real-ab/raw/minimax/baseline/trace.jsonl)；[candidate完整稿](attempt-03-real-ab/raw/minimax/candidate/final.txt) / [trace](attempt-03-real-ab/raw/minimax/candidate/trace.jsonl)。
- 各臂目录保留stdout trace、stderr、实际CLI argv/cwd/prompt及原始记录；[SHA-256清单](attempt-03-real-ab/SHA256.json)覆盖整份证据。
- [首批4次错误模型slug调用](attempt-01-invalid-model-route/fixture.json)与[第二批2次Temp沙箱访问失败](attempt-02-temp-sandbox/fixture.json)全部保留，均不计入4份技术有效稿。F盘迁移后的本机sandbox独立预检也因CLI要求命名permission-profile退出2，不能写成预检通过；真实exec读取成功另有直接证据。

实际运行：`python maintenance/tests/evidence/lint-command-route-r1/run_eval.py --prepare --output-root "output/lint-command-route-r1/r3 project"`；两条 `--provider alibaba2|minimax` 使用同一output。Alibaba2基线人工确认后，通过同一冻结模块 `run_one(output, fixture, "alibaba2", "candidate")` 只执行原先未启动的臂。实际完整模型命令逐份记录，不替换成汇总伪命令。

产品仅两行变动、Git LF净增272 bytes；未镜像、未合并或推送，未声称公开版本已修复。R3结束时曾拟将本批candidate作为后续对照；切换受限MCP接口后，R4实际两臂均重新采集，本批仅作原生命令背景，不与其合并分母。后续路径原子的独立准入及R4—R6撤回状态见[统一最终入口](result.md)。
