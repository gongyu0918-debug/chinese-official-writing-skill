# v1.6.19 本地候选基线

日期：2026-08-28。

状态：`PUBLISHED / SEE release-1.6.19.md`。本文件保留发布前候选门；正式外部回执见同目录 `release-1.6.19.md`。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.18^{commit}=67a68257f8a79220a38e961ced932bcb022cf86b`。
- 本轮内容基线：`main@ee4465dedee6e24d95feb656e19f5d0a88f79574`；`origin/main@c784e3721db8f170015e1220ea92c815f747a89a` 是 v1.6.18 发布回执提交，且为本轮内容基线祖先。
- 本地发行分支：`codex/release-v1.6.19`；目标版本：`1.6.19`。
- 本版只发行已合入本地 `main` 的 Hermes Agent 0.20.5—0.20.6 新建不可恢复单题 adapter、DeepSeek Harness 0.1.1-rc.2 headless 原生 Profile Bundle，以及对应共享 core、组装、测试和工程记录。description、公开写作规则和 references 相对 v1.6.18 不变。
- `codex/paid-outline-review` 的提纲与红头 DOCX 能力不反向进入公开版。ClawHub 继续使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 普通包。

## 真实写稿与生命周期依据

- Hermes Agent 使用 Alibaba Token Plan 2 与 Ollama Cloud 的当前 Skill 采购、情况说明真稿完成安全 KEEP；固定失败稿完成223→182字最小修订，inline、`--query-file`、0.20.6复跑和最终128字采购稿均闭合 task、turn、可见终稿 hash 与脱敏。宿主在 transform 前持久化 D0，因此只支持新建且不可恢复的单题；交互、resume/continue、`--oneshot` 和 gateway 明确旁路。
- DeepSeek Harness 使用 Alibaba provider-default 与 OpenCode Go max 各完成一份当前 Skill 真稿，分别以3次、2次 Stop 绑定同一 D0、最终稿 hash 和终态脱敏；仅验证 Windows headless Profile Bundle 的 `delivery_review`，不外推 TUI/Web、POSIX、其他 capability 或后续版本。
- 本轮只更新发行坐标，不重复消耗真实写稿；完整原始结果见 `hk004-hermes-r2/result.md` 与 `hk004-deepseek-harness-r1/result.md`。

## 发布坐标与边界

- GitHub：`gongyu0918-debug/chinese-official-writing-skill`，tag 与 Release 名均为 `v1.6.19`。
- SkillHub.cn：现有 `skillId=70149`、坐标 `@user_f3d82da7/chinese-official-writing`、slug `chinese-official-writing`、展示名“中文公文写作”；清洁包允许包含默认关闭的可选 Hook，不含 `agents/openai.yaml` 和付费实现。
- ClawHub：owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`；发布包必须为33文件且 Hook、`agents/openai.yaml`、付费提纲和红头实现命中均为0。
- 小红书 Red SkillHub、付费包及其他平台不在本轮范围。

## 发布门结果

- 固定基线复核确认 `v1.6.18^{commit}=67a68257f8a79220a38e961ced932bcb022cf86b`，`origin/main@c784e372` 为本轮内容基线 `ee4465de` 的祖先；v1.6.18 后差异只含 Hermes R2、DeepSeek Harness R1、共享 core/组装、测试、规格和发行坐标，canonical `SKILL.md` 与全部公开 references 相对 v1.6.18 无差异，付费提纲和红头实现路径未进入公开候选。
- 全量单元测试：`py -3 -B -m unittest discover -s maintenance/tests -p "test_*.py"`，723/723通过，测试报告耗时92.086秒。
- 发布定向回归：`test_skill_boundary`、`test_skillhub_package_builder`、`test_status_ledger_consistency`、Hermes/DSH adapter、Hook层契约和仓库链接共122/122通过，耗时8.896秒。首次运行的4项失败均为本轮发行维护缺口：DSH无 `hooks.json` 的断言范围、两处尚未创建的rc链接、Hermes旧候选状态；补齐后产品运行逻辑未因测试修改。
- DeepSeek Harness 组装为54文件、fingerprint `3488cbecb328ec70613abe9d3c01575ada3e43d15c283016d3dafe54634ae672`，随后 `node --check` 与原生生命周期 smoke 通过：首次 Stop 阻断、终态放行、原文不保留、终态脱敏、外部同名 Skill 拒绝和换事务脱敏均为true。首次直接对源码 adapter 运行 smoke 因缺组装后的 `skills/chinese-official-writing/SKILL.md` 返回 `ENOENT`，属于调用形态无效；按真实54文件 companion 复跑后通过。
- Promptfoo 0.121.11 本地 stub smoke：20/20通过，Skill 10胜、baseline 0胜、平票0、无效0、judge consistency 1.0；该项不冒充真实模型写稿。
- 固定上一 tag 的确定性消融：v1.6.18 为110/111、当前候选111/111，当前 create/revise failure 均为0。上一版唯一失败是当前用例 P022 要求九套自包含 adapter，而 v1.6.18 尚无本轮新增的 Hermes/DSH 组装；不解释为旧版写作质量失败，也不把工程覆盖增加冒充真实写稿收益。
- canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；143个 tracked Python 文件内存编译、143个 tracked JSON 文件解析通过。
- `sync_adapters.py` 复跑前后 tracked diff SHA-256 均为 `a6bf1ef44e8a78cdb89ef2adbc090269cab87c5548c607a43738812ec2873b58`，镜像同步幂等。
- SkillHub.cn 清洁包81文件，本地文件树指纹 `1d36f23e7b4f2bc2a2b0a61b665926899c41b94293f93164d9bdd70b5f934ed9`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。dry-run 返回 `slug=chinese-official-writing`、`version=1.6.19`。
- ClawHub 包33文件，本地文件树指纹 `829d4b06f1cf59f131bdd0cafe34724443aeecbfa6a4060c174da7a80b374a47`；Hook路径、Hook内容、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。ClawHub CLI 0.23.1 结构 dry-run 与绑定最终产品提交 `eef65336d5dfd5a09434f7ca6bed6e01975b37fb` 的 source-bound dry-run 均返回 `would-publish`、slug `chinese-official-writing`、展示名“中文公文写作”、版本1.6.19、33文件、平台 fingerprint `5fd17d00ab30a0fe214833be64b93470eabd68a48df4dd506eae8f06707888dc`。
- 本地指纹按相对 POSIX 路径排序，对每个文件依次写入 `path + NUL + bytes + NUL` 后计算 SHA-256；平台回执指纹单列，不与本地 Windows 检出字节混用。
- `git diff --check`、候选终审和最终清洁状态在产品提交前复核；正式发布结果见 `release-1.6.19.md`。

正式发布结果、最终产品提交绑定和平台回读另写发布回执，不由本地候选证据预断。
