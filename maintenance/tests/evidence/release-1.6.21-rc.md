# v1.6.21 本地待发布基线

日期：2026-08-30。

状态：`PUBLISHED / SEE release-1.6.21.md`。本文件保留发布前候选门；正式外部回执与本次复跑计数见同目录 `release-1.6.21.md`。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.20^{commit}=2fc9d1d4baf8b5b74009d6ac28cf92135881a5c8`。
- 本地公开内容基线：干净 `main@c60e3ffaa12af012bf2a3910081ae70244a87a21`；本地发行分支：`codex/release-v1.6.21`。
- 版本坐标提交：`c53bc3fb`。八套 Hook adapter、同步器、SkillHub 组包测试和 OpenClaw 无 Hook 包 metadata 使用 `1.6.21`；公开 README 与 OpenClaw README 继续显示已发布的 `1.6.20`，不把本地候选冒充线上版本。
- 相对 v1.6.20 的产品增量来自已进入干净 main 的 `UL-005-R10` 篇幅不足修订口径与 QwenWork 无 Hook 静态 Skill 包。canonical `SKILL.md` 和公开 references 相对 v1.6.20 没有本轮新增修改；QwenWork 不声明未被官方生命周期证明的 Hook。
- `UL-006` 动态近材料过短候选 `389b43f4` 不是本分支祖先；canonical Skill、references、scripts 和现有 `under_length/runtime.py` 与 `main@c60e3ffa` 逐路径一致。当前分支只恢复其预登记、真实结果、规格状态和复现脚本，不带入候选 runtime 或新增单测。
- ClawHub 仍以 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 包为基线；Hook 路径与 `agents/openai.yaml` 均为0。

## 已完成但推迟继续的真实验证

- 普通 reference 减载三轮没有形成跨 provider 稳定收益，产品已恢复；合理原因、即时作用、归纳、条件性结论和低强度预期没有因“材料未逐字写出”被直接判失败。
- `UL-006-R1` 五路20份提示原型只支持情况说明、事故通报和办理通知进入最小研究候选，会议纪要未进入。
- `UL-006-R2` 本轮只完成既已启动的 Alibaba Token Plan 2 四题 Codex Stop：U1 真实触发，96→147字 D1 因新增计算 `95.7%` 被机械门拒绝并安全回 D0；U2 事故稿自然充分而未触发；U3 通知未触发但普通 Skill 新增了落款、当前日期和动作；80字上限控制正确旁路。安全回退不记为目标成功。
- 其余四家低成本 provider 与 `UL-006-R3-ARITHMETIC`、`UL-006-R3-COMPLETENESS`、`WR-018-NOTICE-ISSUER-DATE` 三个原子均为 `DEFERRED_NEXT_SESSION / NOT_STARTED_THIS_CLOSEOUT`；本轮没有继续调用模型，也没有启动新题。

## 本地确定性门结果

- 发布定向回归：`python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_status_ledger_consistency maintenance.tests.test_under_length_capability maintenance.tests.test_hook_layer_contract -v`，122/122通过，耗时5.212秒。
- 全量回归首次运行736项，只有10项失败，均为选择性恢复规格时遗漏其引用的既有研究证据文件；没有产品、版本、Hook 或包体失败。补齐六份已有证据后，链接单测1/1通过；最终同一全量命令736/736通过，耗时119.309秒。
- 五提交检查点：`main@c60e3ffa` 是候选祖先；`389b43f4` 不是候选祖先；canonical 产品路径与 main 无差异。固定 v1.6.20/current 确定性真实用户式 Prompt 消融均为111/111，起草和改稿失败均为0；该工具不调用 LLM。
- `sync_adapters.py` 复跑前后 Git 状态一致。Skill Creator quick validate 对 canonical、Agent Skills、QwenWork、Qwen Code、Hermes 五套均通过；OpenClaw 包因宿主专用 `category` 字段不符合通用 validator schema 而不使用该项作准入，其33文件、MIT、无 Hook 与版本 metadata 由仓库边界测试通过。
- SkillHub 本地清洁包生成82文件，slug `chinese-official-writing`、展示名“中文公文写作”、版本 `1.6.21`，排除仓库 `LICENSE` 和 `agents/openai.yaml`，包内使用 `LICENSE.md`。ClawHub 本地基线33文件，Hook路径0、`agents/openai.yaml` 0。
- `git diff --check`、活动 Markdown 链接和本地组包结构均通过；生成目录位于忽略的 `output/release-v1.6.21/`，未提交模型输出或平台凭据。

## 待发布边界

- 本轮没有创建或移动 `v1.6.21` tag，没有 push，没有创建 GitHub Release，没有调用 SkillHub.cn 或 ClawHub 上传接口。
- 后续获得明确发布授权后，须以本分支最新干净提交重新绑定 source commit，复核三平台 slug、展示名和包体；ClawHub 继续只发布33文件无 Hook 包。
- 动态字数兜底不得随发布动作顺带进入本版；它必须在下一轮按已登记原子继续真实写稿和 Stop 生命周期验证。
