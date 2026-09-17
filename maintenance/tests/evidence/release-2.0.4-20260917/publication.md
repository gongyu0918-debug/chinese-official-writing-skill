# 2.0.4 发布记录

当前 main 的已验证脚本修复于 2026-09-17 发布。产品提交为 `f8b2e86f2cefa9a660c21faca37b24f42cb3ee64`，annotated tag `2.0.4` 固定指向该提交；后续维护证据提交不改变产品 tag。

| 平台 | 结果 | 提交回执 |
| --- | --- | --- |
| GitHub | Release 已创建 | [中文公文写作 2.0.4](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.4) |
| SkillHub | 提交成功；审核状态 `pending` | skillId `70149` / versionId `320181`，73 文件 |
| ClawHub | `published` | versionId `k9782ph66492q9sfabw4b1xkb98ek2e3`，72 文件 |

三平台各提交一次，完整参数、时间和原始回执保存在本目录。SkillHub、ClawHub 以成功提交回执收束；没有提交后查询、传播轮询或重复上传。

## 范围与验证

- 对比 2.0.3，产品改动为 `prose_lint.py`、`draft_length.py`、`prose-lint-usage.md` 及 README 版本说明。未合并的抗 AI 候选和新场景设想未进入发布。
- 已合并真实写稿证据见 [脚本评估](../script-fixes-merge-20260916/assessment.md)：4 对、8 次原生调用；脚本相同字节对应的 142 项程序检查沿用。本轮未重复模型调用。
- `python maintenance/tests/evidence/release-2.0.4-20260917/prepare.py` 完成 8 项机械检查和 SkillHub 本地预检；ClawHub 直接 Node CLI 预检返回 `would-publish`。
- 包清单最终核对为 canonical 73 文件、SkillHub 73 文件、ClawHub 72 文件。删除检查调用生成的单个字节码缓存后，逐项核对文件集合及 SHA-256；上传前再次验证清单一致。后续脚本调用禁写字节码。
- `git diff --check` 通过。main 和 tag 已原子推送；没有强推或移动旧 tag。
- 桌面 WorkBuddy 及其他适配归档保持原状，本轮未制作或上传适配压缩包。

## 状态边界

SkillHub 待审核是平台回执状态，不写为审核通过。本次发布不宣称所有模型都能消除旁白，也不宣称费用或速度普遍下降。
