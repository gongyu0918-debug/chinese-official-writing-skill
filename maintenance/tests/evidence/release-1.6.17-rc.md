# v1.6.17 本地候选基线

日期：2026-08-26。

状态：`READY_LOCAL_CANDIDATE / NOT_PUBLISHED`。本文件绑定本地发行候选；正式发布回执完成前，不表示 GitHub、SkillHub.cn 或 ClawHub 已存在 v1.6.17。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.16^{commit}=f6293aaaa4095530b386b50e3a56c07e35206af5`。
- 本轮内容基线：`main@a8742318e70278487afab00f63f0562781587acf`。
- 本地发行分支：`codex/release-v1.6.17`；目标版本：`1.6.17`。
- 本版是维护补丁：公开写作规则和 Hook 协议相对 v1.6.16 不变；新增内容为 `WR-014-R6/R6b`、`WR-013c`、`WR-020a2`、`WR-021` 的预登记、真实写稿结果、官方校准、状态收口和五提交复核。
- 没有跨模型共同目标失败，不把单 provider 风险写成新规则，不新增统一篇幅门、禁词、adapter 或工程门。
- `codex/paid-outline-review` 的提纲与红头 DOCX 能力不反向进入公开版。ClawHub 继续使用 `packages/openclaw/skills/chinese_official_writing/` 的无 Hook 普通包。

## 真实写稿依据

- `WR-014-R6` 原“未开展被写成继续”目标2/2未复现；另行预登记的R6b只有Ollama 1/2把证据未附外推为待后续核验。
- `WR-013c` 两路均由资源利用率、排队和等待形成原因前置与低强度预期，没有升级成延期、中断或不稳定。
- `WR-020a2` 的OpenCode 2326字符五节报告通过局部未发生/整体结论目标；Ollama首跑及唯一重试均无终稿，按技术失效记录。
- 7份有效终稿中6份带正文外包装，作为无Hook直写服从性残余保留；当前已有 `CL-001` 可选能力，本版不重复造规则。

## 发布坐标与边界

- GitHub：`gongyu0918-debug/chinese-official-writing-skill`，tag 与 Release 名均为 `v1.6.17`。
- SkillHub.cn：现有 `skillId=70149`、坐标 `@user_f3d82da7/chinese-official-writing`、slug `chinese-official-writing`、展示名“中文公文写作”；清洁包允许包含默认关闭的可选 Hook，不含 `agents/openai.yaml` 和付费实现。
- ClawHub：owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`；发布包必须为33文件且 Hook、`agents/openai.yaml`、付费提纲和红头实现命中均为0。
- 小红书 Red SkillHub 及其他平台不在本轮范围。

## 发布门结果

- 全量单元测试：`py -3.13 -B -m unittest discover -s maintenance/tests -p "test_*.py"`，693/693通过，耗时70.246秒。
- 发布定向回归：94/94通过。首次与 `sync_adapters.py` 并行运行时读到镜像重建中间态，形成2个缺文件错误和2个瞬态镜像失败；同步结束后在静态目录串行重跑通过，该并发样本不计作候选结果。
- Promptfoo 本地 stub smoke：20/20通过，Skill 10胜、baseline 0胜、平票0、无效0、judge consistency 1.0；该项不冒充真实模型写稿。
- 固定上一 tag 的确定性消融：v1.6.16 与当前候选均为111/111，新增 create/revise failure 均为0。
- canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；136个 tracked Python 文件内存编译、142个 tracked JSON 文件解析通过。
- `sync_adapters.py` 复跑前后 diff hash 均为 `8537fb8e03e14a39fcb53737ddac2f2c2e60fae9`，镜像同步幂等。
- SkillHub.cn 清洁包71文件，本地文件树指纹 `2ef79003a0cd9d0343d30f94d9b95c1414d5ae9e71910449ca449b8383bf4a54`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。dry-run 返回 `slug=chinese-official-writing`、`version=1.6.17`。
- ClawHub 包33文件，本地文件树指纹 `7c68fd98e77e9f9cb7f4abf6ff8e483b7eacc727eaaf4ce6b6475e9eb75cb50f`；Hook、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。结构 dry-run 与绑定产品提交 `7b4577843d6d98e5583aa6615d813c1c82a56db3` 的最终 dry-run 均返回 `would-publish`、展示名“中文公文写作”、版本1.6.17、33文件、平台 fingerprint `811cd3dac093d8639adbfd9ad84a1844f4710730c695194ba65e64c1900d5a30`。
- 本地指纹按相对 POSIX 路径排序，对每个文件依次写入 `path + NUL + bytes + NUL` 后计算 SHA-256；平台回执指纹单列，不与本地 Windows 检出字节混用。
- `git diff --check` 与最终清洁状态在候选 commit 前复核；所有正式外部写入均尚未发生。

正式发布结果与平台回读另写发布回执，不由本地候选证据预断。
