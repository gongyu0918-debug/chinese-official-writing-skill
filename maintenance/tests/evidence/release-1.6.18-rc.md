# v1.6.18 本地候选基线

日期：2026-08-27。

状态：`PUBLISHED / SEE release-1.6.18.md`。本文件保留发布前候选门；正式外部回执见同目录 `release-1.6.18.md`。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.17^{commit}=7b4577843d6d98e5583aa6615d813c1c82a56db3`。
- 本轮内容基线：`main@0fa243ba0740ca3aff3a8d879ef7b73d98013601`；`origin/main@98b018483db938769a20fd5125ba83770566a49b` 是 v1.6.17 发布回执提交，且为本轮内容基线祖先。
- 本地发行分支：`codex/release-v1.6.18`；目标版本：`1.6.18`。
- 本版只发行已经合入本地 `main` 的 OpenCode 1.18.23 常驻交互 adapter、共享 core 的精确 `HostAbort` 支持、组装/测试和工程记录。没有修改 description、公开写作规则、references 或真实写稿判定标准。
- Hermes Agent 0.20.0 的同步变换位置虽已验证，但三份当前 Skill 真稿没有出现可机械删除的共同包装目标；材料外语义外扩不能由同步 transform 安全修复，因此终态为 `BASELINE_NOT_REPRODUCED`，本版没有 Hermes adapter。
- `codex/paid-outline-review` 的提纲与红头 DOCX 能力不反向进入公开版。ClawHub 继续使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 普通包。

## 真实写稿与生命周期依据

- OpenCode 同稿原型的三份有效稿都作出目标修正：稀疏采购申请和未决情况说明解决目标；活动新闻恢复完整年份并收紧待核范围，但仍有 Markdown 包装和材料外交流表述，按部分改善记录。
- 当前 companion 使用 `opencodex/alibaba-token-plan-2/deepseek-v4-flash-0731` 在线复核320字符无字数限制采购申请，保留92%、18个排队、拟采购2台、预算/供应商未定及一层原因和时效影响；D0与最终逐字相同，终态完成原文脱敏。
- 延迟期间新用户任务、未终态模块重载、派发窗口并发实例、同名外部 Skill 冲突均有对抗 smoke；OpenCode 无头 `run` 明确旁路，不把常驻交互证据外推到其他宿主路径。
- 本轮只更新发行坐标，不重复消耗付费真实写稿；真实结果、生命周期和两轮冷审的完整记录见 `hk004-opencode-hermes-r1/result.md`。

## 发布坐标与边界

- GitHub：`gongyu0918-debug/chinese-official-writing-skill`，tag 与 Release 名均为 `v1.6.18`。
- SkillHub.cn：现有 `skillId=70149`、坐标 `@user_f3d82da7/chinese-official-writing`、slug `chinese-official-writing`、展示名“中文公文写作”；清洁包允许包含默认关闭的可选 Hook，不含 `agents/openai.yaml` 和付费实现。
- ClawHub：owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`；发布包必须为33文件且 Hook、`agents/openai.yaml`、付费提纲和红头实现命中均为0。
- 小红书 Red SkillHub、付费包及其他平台不在本轮范围。

## 发布门结果

- 固定基线复核确认 `v1.6.17^{commit}=7b4577843d6d98e5583aa6615d813c1c82a56db3`，`origin/main@98b01848` 为本轮内容基线 `0fa243ba` 的祖先；v1.6.17 后差异只含 OpenCode/Hermes R1、共享 core/组装、测试、规格和发行坐标，没有付费提纲或红头实现路径。
- 全量单元测试：`py -3 -B -m unittest discover -s maintenance/tests -p "test_*.py"`，701/701通过，耗时100.269秒。
- 发布定向回归：最终174/174通过，耗时33.141秒。首次运行时173/174通过，唯一失败是状态台账测试仍要求 `HK-004` 行保留已被 OpenCode 终态取代的 `DONE_V1.6.15` 字样；测试改为同时核对国产 CLI 历史链接、Kimi 首次 Stop 限制与当前 `DONE_LOCAL_MAIN / HERMES_BASELINE_NOT_REPRODUCED` 后通过，产品规则和 adapter 未因该失败修改。
- Promptfoo 本地 stub smoke：20/20通过，Skill 10胜、baseline 0胜、平票0、无效0、judge consistency 1.0；该项不冒充真实模型写稿。
- 固定上一 tag 的确定性消融：v1.6.17 与当前候选均为111/111，新增 create/revise failure 均为0。
- canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；138个 tracked Python 文件内存编译、142个 tracked JSON 文件解析通过。
- `sync_adapters.py` 复跑前后 diff hash 均为 `3a17b581c6822b24918fb99ff7be76219531238285b217475de423023fe3f30e`，镜像同步幂等。
- SkillHub.cn 清洁包73文件，本地文件树指纹 `4ff2cb68beff03a09a9372d8c26eb2d0d0c9aabbde6aa56e5ae615b478f16c61`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。dry-run 返回 `slug=chinese-official-writing`、`version=1.6.18`。
- ClawHub 包33文件，本地文件树指纹 `b09972521d52871e4345c40074683db58374d5bd12fca8413cc6dae332de6f53`；Hook路径和Hook内容命中均为0，`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。ClawHub 0.23.3 结构 dry-run 与绑定最终产品提交 `67a68257f8a79220a38e961ced932bcb022cf86b` 的 source-bound dry-run 均返回 `would-publish`、展示名“中文公文写作”、版本1.6.18、33文件、平台 fingerprint `f71bf08951ea28860d14602950aab7ee43d7bd482a2ccc71e40d909f363a765d`。
- 本地指纹按相对 POSIX 路径排序，对每个文件依次写入 `path + NUL + bytes + NUL` 后计算 SHA-256；平台回执指纹单列，不与本地 Windows 检出字节混用。
- `git diff --check`、候选终审和最终清洁状态在产品提交前复核；所有正式外部写入均尚未发生。

正式发布结果、最终产品提交绑定和平台回读另写发布回执，不由本地候选证据预断。
