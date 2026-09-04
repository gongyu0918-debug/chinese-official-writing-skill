# MT-002a lint 命令路径 R1 预注册

状态：`PROTOTYPE_ONLY / REAL_AB_NOT_STARTED`。本记录在模型调用前提交；产品准入由主代理复核，尚不镜像、合并或发布。

## 单一机制与固定边界

基线为 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f`，候选仅修改 canonical `SKILL.md` 脚本段与 `references/final-review-layers.md` 工具示例：脚本基于本次已读 SKILL 的目录解析，示例使用加引号绝对脚本和草稿路径；保留提示性 lint 及语义判断，返回码 0 不代表没有风险。不增加 `--strict`、自动清洗、Hook 或镜像。

已复现的目标问题：普通项目 cwd 下执行 `python scripts/prose_lint.py` 找不到脚本；将脚本解析到实际 Skill 安装目录后同一草稿可完成扫描。这是命令正确性修复，候选可能增加说明字节，不宣称减载。两处文字均属于同一相对路径假设。Git UTF-8/LF字节：SKILL 27,147→27,267（+120），final-review 8,877→9,029（+152），合计+272 bytes。

## 题面与运行顺序

[cases.json](cases.json) 固定唯一完整通知及唯一 prompt：264字（不计空白，含4个Markdown星号），完整活动日期、报名期限、成文日期，方案未审定、仅征集意向、主题和发言顺序待定、报名不等于列入发言名单。标题含Markdown噪点。要求真实运行 Skill 的 lint 后作必要局部修订，只有原稿事实，最终只交完整正文。题面两臂逐字相同，明确本项目 Skill 相对入口，不给正确脚本命令或绝对路径答案。

一个题 × baseline/candidate两臂 × Alibaba2 DeepSeek/MiniMax M3两条既有低成本路线，共4份稿；均 `max`。Alibaba2先baseline后candidate，MiniMax先candidate后baseline；每份独立CLI会话，不自动补跑，技术失败保留。无需把本轮两路线或其他原子的五路线固化为后续统一门。

## 隔离及最薄运行器

[run_eval.py](run_eval.py) 复用既有 `complaint-reflection-r1/desktop_writer.py` 的 Desktop CLI 发现和上游导出/指纹/统计工具，独立覆盖调用，不改旧冻结writer。CLI当前为0.153.1。每臂安装在独立临时普通项目的 `.agents/skills/chinese-official-writing/`，项目路径包含空格，项目cwd不等于Skill目录。导出的canonical按五套普通包边界排除 `hooks/`、`scripts/review_gate.py`、`references/delivery-review-gate.md`，不组装或启用Hook。

`skills.config` 的启用与禁用路径均为 `SKILL.md` 文件，保留两处全局MIT安装及Pro安装不动；禁用两处全局同名 Skill，关闭plugins/apps/memories。路径依据[官方本地Skill启停示例](https://learn.chatgpt.com/docs/build-skills#enable-or-disable-local-codex-skills)。`workspace-write` 仅供本项目写临时校对稿，审批never；执行前后产品指纹必须一致。运行器冻结实际argv、cwd、提示词、模型、CLI版本、材料/Skill指纹与完整stdout/stderr。成功读取目标Skill须从真实成功命令解析到本运行的绝对文件，不用易命中全局的相对路径子串替代；另扫描全局路径及Hook污染。若解析不支持，保留trace转人工核验，不判已加载。

## 判定与交付

主要观察每稿实际lint命令、找不到脚本/路径错误次数、其他工具失败、扫描成功次数、命中是否得到语义处置，以及是否为正确安装版本的脚本。命令扫描完成与零命中分别记录；模型若自行修复baseline路径，属于基线自修能力。不得因候选命令成功便宣称稿件无错。

事实/数量/日期/未决状态、通知结构、必要信息完整性、正文交付及观感分别人工检查。文字等义保留不按简单子串误判；题面未给字数硬门，不把264字当必须长度。比较实际成功读取文件及输出体积，并保留每份trace；全文件字节只是读取上界，不能冒充截取/截断后的实际输入token。

CLI非零、无终稿、未成功读取本项目精确Skill、读取全局同名Skill、Hook污染或产品指纹变化列技术无效，不以质量失败替代。可恢复工具错误不会直接使整个样本技术无效。每条路线仅一对，可证明此题行为，不能估计普遍失败率。

真实结果后提交4份原始完整终稿、trace、hash、argv与逐稿评估。只跑本改动所需最小验证，不补镜像或全量门；未经主代理准入，不宣称候选通过。

提交前仅运行 `run_eval.py --help`（exit 0）与 `git diff --check`（exit 0）；真实写稿尚未开始，未用这些检查宣称候选准入。

## 调用前环境更正登记

第一次调用记录在 [attempt-01-invalid-model-route](attempt-01-invalid-model-route/fixture.json)：运行器误将路由写为 `opencodex/alibaba-token-plan-2/...` 与 `opencodex/minimax-cn/...`。4次CLI均在模型工具操作前退出1，提示未知模型并 `adapter_eof`，没有终稿、Skill读取或质量结果；CLI自身的流重试完整保留。这是本轮构建者的模型slug配置错误，不能归因于产品或provider写作质量。

改为本机catalog现有的 `alibaba-token-plan-2/deepseek-v4-flash-0731` 与 `minimax-cn/MiniMax-M3`，prepare检查精确slug及max支持，出现技术问题则暂停该路线后续臂供人工判断。题面、材料和产品字节不变，产品候选固定 `5cb696fe`；修正后的harness另行commit，再冻结新r2输出目录运行4份。原始失败包不覆盖，不把本次环境更正记为产品R2或抽掉质量失败。

## 最后一次环境修正

修正slug后的首两臂进入真实模型工具操作，但用户Temp路径被Windows沙箱拒绝访问，PowerShell cwd回落至运行时目录，Skill与原稿均未成功读取。已中止这两个测试CLI，后续两臂未启动；[attempt-02-temp-sandbox](attempt-02-temp-sandbox/fixture.json)完整保留。该批不得用于命令路径或正文质量比较。

按主代理2026-09-05收紧范围，唯一后续修正采用既有writer成功使用的 F 盘 `output/.../runtime` 普通Git项目与 `read-only` 沙箱，仍启用精确SKILL.md文件路径、禁用两处global同名文件。输出根目录名含空格；材料文件已预放入runtime，模型可直接lint原稿并在最终回复修订正文，不要求新增写文件行为。产品、题面、输入稿均不改。只允许这次环境修正的4份重跑；如再发生技术问题，保留现状交回主代理，不继续模型排障或补样本。
