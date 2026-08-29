# HK-004-QWENWORK-R1 结果

## 结论

状态：`STATIC_SKILL_PACKAGE_PASSED / ONLINE_LIFECYCLE_UNVERIFIED / NOT_MERGED`

QwenWork（Qwen 办公）无 Hook 静态 Skill 包已在独立分支形成候选。候选不修改 canonical `SKILL.md`、description、references、脚本或 Hook 核心，只增加机械镜像、安装说明、同步入口和包体反控。官方公开 Stop 事件没有说明完整最终正文或可绑定的当前回合记录，因此没有制作 QwenWork Hook adapter，也不把包路径写稿冒充 QwenWork 在线生命周期。

## 官方边界

- [QwenWork Skills](https://qwenwork.cn/docs/features/skills)：Skill 为含 `SKILL.md` 的目录，个人目录为 `~/.qwenworkcn/skills/`，支持自动、斜杠或手动调用。
- [组织 Skill 包](https://www.alibabacloud.com/help/en/qwenwork/skills-management)：ZIP 顶层目录名须与技术名称一致，可含 `scripts/`、`references/`，包体上限 10 MB。
- [QwenWork Hooks](https://www.alibabacloud.com/help/en/qwenwork/hooks)：公开事件包含 `UserPromptSubmit` 与 `Stop`，但 Stop 示例和字段说明没有给出完整终稿载荷或当前回合记录绑定方式。
- [专家套件](https://qwenwork.cn/docs/desktop/expert-kits)：可分发插件 ZIP；本轮按官方建议先使用更轻的 Skill 路径，不为无真实目标先建专家套件。

## 静态包

- 产品提交：`434eb8c1`；写稿固定提交：`b31f1389ee74be3bad73c4f8830a44b3e7975218`。
- 源：`packages/qwenwork/skills/chinese-official-writing/`。
- 文件数：34；tree fingerprint：`66d72e3d9179e03b3ef2541b8b0957a204cb69b37547e025348d6440751ddcee`。
- 两次 `git archive` 生成的 ZIP 均为116263字节，SHA-256 均为 `9d154ba6a9e71c2e1458084d78f24a19272bf047c797c81bcda1145f39b39b05`。
- ZIP 38个 entry，唯一顶层目录为 `chinese-official-writing/`；不安全路径0，Hook/门禁 entry 0，远低于10 MB。

## 包路径真实写稿

- 客户端：`codex-cli 0.144.6`，只读、ephemeral、无 Hook。
- 模型：`alibaba-token-plan-2/deepseek-v4-flash-0731`，reasoning effort `max`。
- 隔离路径：把 QwenWork 候选包复制为运行目录唯一项目级 `.agents/skills/chinese-official-writing/`；禁用用户级同名 Skill。
- trace：精确读取隔离包 `SKILL.md`，用户级同名 Skill 污染0；退出码0，技术失败0，硬失败0。
- 稿件：89个非空白字符的采购事实材料生成143个非空白字符正文。正文完整保留1台、现有3台、日均约1200页、2.8万元、3万元和办公设备购置经费；以“缓解扫描处理压力、提高工作效率”承接材料事实，属于预注册允许的一层合理原因和直接作用，不是材料外成效。没有新增用途、采购程序、责任人、日期或完成承诺。
- 143字短于含大量测试约束的208字提示词、长于89字事实材料。标题、主送、现状、原因、申请事项、资金和请批语均完整，因此不按提示词总字符机械判为过短。
- 用量回执：input 135753、cached input 108544、output 3471、reasoning output 2043 tokens。该数值含宿主指令和工具回显，不能直接等同于 reference 字节，但足以支持继续检查加载路径。

## 新 reference 风险原子

本页最初登记 `MT-004a-PROCUREMENT-REQUEST-ROUTE-R1`，没有修改产品 reference；后续已完成全新跨 provider 复现并收口为 `CURRENT_BASELINE_SUFFICIENT / WAIT_NEW_COUNTEREXAMPLE`，见 [`mt004a-procurement-request-route-r1/result.md`](../mt004a-procurement-request-route-r1/result.md)：

- 单份无字数限制采购申请实际读取入口与6个 references：`information-selection.md`、`genre-playbook-request.md`、`argument-chains.md`、`formal-addressing.md`、`proofreading-checklist.md`、`final-review-layers.md`，合计52029字节。
- 这是一份可用真稿中的单 trace 负载信号，不足以断言路由错误。后续 Alibaba Token Plan 1 全新题只读信息选择、轻量卡和申请叶，未复现4份额外通用页；预注册的候选启动门没有成立。
- 当前不增加停止条件，不运行五路候选 A/B。只有另一家低成本 provider 的新简单采购申请再次出现同类过读或真实质量回退才重开；准入仍须同时保护理由、申请事项、资金、请批功能和控制题路由。

## 实际命令与结果

```powershell
python maintenance/tools/sync_adapters.py
python -m py_compile maintenance/tools/sync_adapters.py
python maintenance/tests/evidence/hk004-qwenwork-r1/run_package_sanity.py --prepare
python maintenance/tests/evidence/hk004-qwenwork-r1/run_package_sanity.py --run
git archive --format=zip --prefix=chinese-official-writing/ -o output/hk004-qwenwork-r1/package/qwenwork-a.zip HEAD:packages/qwenwork/skills/chinese-official-writing
git archive --format=zip --prefix=chinese-official-writing/ -o output/hk004-qwenwork-r1/package/qwenwork-b.zip HEAD:packages/qwenwork/skills/chinese-official-writing
python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_hook_layer_contract maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability
python -m py_compile maintenance/tools/sync_adapters.py maintenance/tests/evidence/hk004-qwenwork-r1/run_package_sanity.py
python -m json.tool maintenance/tests/evidence/hk004-qwenwork-r1/package-sanity-case.json
git diff --check
```

直接相关镜像、边界、Hook 隔离、状态和链接共100项测试通过；两个 Python 文件编译、案例 JSON 解析和 `git diff --check` 通过。五提交范围与基线复核见 [`five-commit-review.md`](five-commit-review.md)。没有安装/启动 QwenWork，没有修改用户配置，没有控制 GUI，没有合并、推送或发布。
