# v1.6.13 本地候选基线

日期：2026-08-22

状态：`READY_LOCAL_CANDIDATE`。本文件绑定本地发行候选；正式发布回执完成前，不表示 GitHub、SkillHub.cn 或 ClawHub 已存在 v1.6.13。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.12^{commit}=ae4a25b497fab1ccdd621ffbf21e43501701f8b9`。
- 上一远端发布回执：`origin/main@48e061f50111ebf61f1c94edec8a36dff3e1c434`。
- 本轮候选内容基线：`main@b572102f083f41c0180f0f14f62570340cae1d38`。
- 本地候选分支：`codex/release-v1.6.13`。
- 版本准备提交：`971024c30a78e35fc7bcb811dabd8007a1303fb7`。
- 目标版本：`1.6.13`。
- 公开候选只包含已合入 main 的 `WR-013`、`WR-011`、`UL-005` 与联网来源用途/命中页绑定，以及对应测试、镜像、规格和证据。
- `codex/paid-outline-review` 不反向合入；公开树不含 `outline_assist`、付费提纲 coordinator、胶水、测试或详细实现规格。

## 真实写稿依据

- `WR-013`：五条 Codex Desktop 路线验证材料和常识支持的一层原因、即时作用、发布者角色，以及非新闻控制。
- `WR-011`：三轮25份真实稿后，五条最终路线守住来源身份、原始出处、冲突和限定结论边界。
- `UL-005`：WorkBuddy / CodeBuddy 同一 D0 生命周期拒绝含强保障、材料外用途和多余请批语的风险 D1，并接受只含同一事实 span 低强度推断的受控 D1。
- 联网来源用途：R2f—R2h 共15份真实稿，最终五条路线均绑定实际打开的上海命中页 URL；严格工具调用次数不由提示词作确定性保证。

## 发布门

- 固定 `v1.6.12^{commit}=ae4a25b497fab1ccdd621ffbf21e43501701f8b9`；其为当前候选祖先，远端不存在 `v1.6.13` tag。
- 版本边界、SkillHub 包构建和 UL-005 直接相关定向测试首次104/105；唯一失败是 README 最近证据列表漏掉上一正式发布记录。只调整该列表后复跑105/105通过。
- 全量 unittest 655/655通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过。
- 固定 v1.6.12/current 的确定性消融分别110/111、111/111；当前候选0失败，基线唯一失败 P050 已由本轮已验证规则覆盖。
- `sync_adapters.py` 二次执行未改变候选 diff；`git diff --check`通过。

## 候选包与平台坐标

- SkillHub.cn 清洁包61文件，本地规范化文件树指纹 `4de24c3e635ff05df2cb9b1572970a51dd51e19fee1014aa10647da8fde42097`；slug `chinese-official-writing`，展示名“中文公文写作”，现有条目 `@user_f3d82da7/chinese-official-writing`。dry-run 返回 `dryRun=true`、version `1.6.13`。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing/` 的33文件无 Hook 包，本地规范化文件树指纹 `02b1900e9e6c5357d8e5cee3b7af6514dd7a6e7a6e02ea547ff4ea258990fd71`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中均为0。
- ClawHub 坐标保持 owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation`。dry-run 返回 `would-publish`、latestVersion `1.6.12`、fileCount `33`、平台 fingerprint `f39454f4577efb5d11980573569de4e77b2b670f1fcd850489ce8e5b747bd662`。
- 两包许可证与根 MIT `LICENSE` 的 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`。

## 当前发布边界

- 用户已明确授权发布 GitHub、SkillHub.cn 和 ClawHub；ClawHub 必须继续使用上述33文件无 Hook 包。
- 小红书 Red SkillHub 不在本次三平台范围内，不查询、不上传。
- 本文件写入时尚未推送 main、创建 tag 或 GitHub Release，也未正式上传 SkillHub.cn 或 ClawHub。
- 正式外部写入前仍须核对 HEAD、工作树、远端 main/tag 和两个包体指纹；正式 ClawHub 命令绑定最终产品 tag 提交。
