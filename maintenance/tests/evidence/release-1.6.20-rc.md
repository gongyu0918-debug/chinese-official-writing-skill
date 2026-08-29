# v1.6.20 本地候选基线

日期：2026-08-29。

状态：`PUBLISHED / SEE release-1.6.20.md`。本文件保留发布前候选门；正式外部回执见同目录 `release-1.6.20.md`。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.19^{commit}=eef65336d5dfd5a09434f7ca6bed6e01975b37fb`。
- 本轮公开内容基线：`main@31dacd0805035521ad848bdc10e70c0a366d554c`，并与 `origin/main` 一致。
- 本地发行分支：`codex/release-v1.6.20`；目标版本：`1.6.20`。
- 本版产品增量只有 `AH-002` 来源绑定的新闻完整日期写后修复，以及 Hook README 将安装、使用和适配说明前移、彻底删除说明后移。canonical `SKILL.md`、description 与全部公开 references 相对 v1.6.19 不变。
- `AH-002` 只在默认 `delivery_review` 的 Stop 前检查唯一完整来源日期和唯一目标新闻文种；多日期、非新闻、歧义材料、非完整日期及其他 capability 旁路，失败时保留 D0。
- 四个 references 减载原子已用五条低成本路线形成190次真实任务输出、186次技术有效结果；纪要、通知、采购公告与复核分层候选均未达到预登记的可归因收益门，产品字节恢复 v1.6.19 基线并进入 `REJECTED`，不以证据数量冒充产品变化。
- `codex/paid-outline-review` 的提纲与红头 DOCX 能力不反向进入公开版。ClawHub 继续使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 普通包。

## 真实写稿与生命周期依据

- `AH-002` 先完成五家冻结续写20/20精确机械替换，再在 Claude Code 2.1.195 隔离 companion 中完成三 provider 九次真实生命周期：3次精确修复、3次目标稿自然写全、3次控制稿逐字不变。Alibaba Token Plan 2 与 OpenCode Go 各至少一次修复且控制不动，达到预登记的两家门；Ollama 三题自然正确，不冒充修复成功。
- references 减载研究包含180次起草/改写与10次纯格式复核控制。只有与候选 diff 可归因的读取收益或正文回退用于判断；合理原因、影响、结论和常识范围推断不作为失败。四项均已终态，不留 `HOLD`。
- Hook README 只调整文档顺序，不改变协议、capability、默认关闭状态或产品规则；原候选已完成定向测试与真实组装偏移检查，本轮发行门只验证合并后的最终字节。

## 发布坐标与边界

- GitHub：`gongyu0918-debug/chinese-official-writing-skill`，tag 与 Release 名均为 `v1.6.20`。
- SkillHub.cn：现有 `skillId=70149`、坐标 `@user_f3d82da7/chinese-official-writing`、slug `chinese-official-writing`、展示名“中文公文写作”；清洁包允许包含默认关闭的可选 Hook，不含 `agents/openai.yaml` 和付费实现。
- ClawHub：owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`；发布包必须为33文件且 Hook、`agents/openai.yaml`、付费提纲和红头实现命中均为0。
- 小红书 Red SkillHub、付费包及其他平台不在本轮范围。

## 发布门结果

- 固定基线复核确认 `v1.6.19^{commit}=eef65336d5dfd5a09434f7ca6bed6e01975b37fb`，本轮公开基线 `main@31dacd0805035521ad848bdc10e70c0a366d554c` 与 `origin/main` 一致。相对 main 的产品差异不含 canonical `SKILL.md`、公开 references、付费提纲或红头实现路径。
- 全量单元测试：`py -3 -B -m unittest discover -s maintenance/tests -p "test_*.py"`，734/734通过，耗时105.283秒。
- 发布定向回归：`test_skill_boundary`、`test_skillhub_package_builder`、`test_status_ledger_consistency`、AH-002、Hook层契约和仓库链接共150/150通过，耗时17.217秒。首次运行的2项失败均为发行版本坐标未同步到既有 adapter manifest；补齐八个版本字段并同步后通过，不涉及运行逻辑修改。
- Promptfoo 0.122.2 本地 stub smoke：20/20通过，Skill 10胜、baseline 0胜、平票0、无效0、judge consistency 1.0；该项不冒充真实模型写稿。
- 固定上一 tag 的确定性消融：v1.6.19 为111/111、当前候选111/111，双方 create/revise failure 均为0。该工具不调用 LLM，只证明发行候选未破坏确定性路由与支持面。
- canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；149个 tracked Python 文件内存编译、147个 tracked JSON 文件解析通过。
- `sync_adapters.py` 复跑前后 tracked diff SHA-256 均为 `5b747dcbf63c3b11388815040746cae6dbca3b43f2e3586b7da147cd57faf000`，镜像同步幂等。
- SkillHub.cn 清洁包82文件，本地文件树指纹 `77424ba02234474f8d57fc2b9f5062851f779de5967a1f64d149f8c674365b8d`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。dry-run 返回 `slug=chinese-official-writing`、`version=1.6.20`。
- ClawHub 包33文件，本地文件树指纹 `39d2e7b093bcc8001c58444965332bab6e06fccdf41feac9c9b85cb2b3d8f392`；Hook路径、Hook内容、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。ClawHub CLI 0.23.1 结构 dry-run 与绑定最终产品提交 `2fc9d1d4baf8b5b74009d6ac28cf92135881a5c8` 的 source-bound dry-run 均返回 `would-publish`、slug `chinese-official-writing`、展示名“中文公文写作”、版本1.6.20、33文件、平台 fingerprint `1386bf0fb02bf836d7f00f5eaed48e351d152442992a0876f41195b4d84d8d24`。
- 本地指纹按相对 POSIX 路径排序，对每个文件依次写入 `path + NUL + bytes + NUL` 后计算 SHA-256；平台回执指纹单列，不与本地 Windows 检出字节混用。
- `git diff --check`、候选终审和最终清洁状态已在产品提交前复核；正式发布结果见 `release-1.6.20.md`。

正式发布结果、最终产品提交绑定和平台回读另写发布回执，不由本地候选证据预断。
