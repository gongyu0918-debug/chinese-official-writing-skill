# GitHub 2.0 测试版更新回执

2026-09-14 按用户授权完成 GitHub 更新，ClawHub、SkillHub 未提交。

- 1.x 历史分支：`legacy/1.x` → `d561bf6b54952e562be5910feda9182cff7d3646`，对应最后的 1.6.36 发布线。原 tag 与发行物保留。
- 2.0 产品提交：`40ea1ccc06fbceba05cb2a14f5d17db555526acb`。第一父提交为上述 1.x 分支头，第二父提交为 `9faf5a719f2b19cc66e9160aeaf10f37811aaa3d`。GitHub API 已核对两个父提交，历史连续。
- `git push --atomic` 同时成功更新 main 和新建历史分支，未强推或改写旧历史。
- GitHub prerelease：[v2.0.0-beta.1](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v2.0.0-beta.1)，发布时间 `2026-09-14T13:58:18Z`，targetCommitish 为产品提交。
- 附件：`chinese-official-writing-v2-2.0.0-beta.1.zip`，118561 字节；GitHub 返回 `uploaded`。
- 本地与 GitHub asset digest 一致：`79ef8987c46434cff5f8ff60fa3381e187a2293216eed7d437e4d0ef405df186`。

本提交仅补发布回执，不改变产品 tag 或已上传字节。Pro 普通层切换与本地安装继续在独立 Pro 工程完成，来源和安装回执分别记录。

## 当日说明和安装标识修正

用户最终确认沿用原 Skill 名称与安装标识。已发布字节保持不变，新测试包使用 `chinese-official-writing`，README 删除了把对话纠正写成产品说明的句子。

- GitHub prerelease：[v2.0.0-beta.2](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v2.0.0-beta.2)，发布时间 `2026-09-14T14:26:52Z`，产品提交 `dd35b6142ffe5286c6eb0c2ac044425587cbdca5`。
- 附件：`chinese-official-writing-2.0.0-beta.2.zip`，118014 字节，GitHub 返回 `uploaded`。
- 本地与 GitHub digest 一致：`c7d90059fd2867d57a2e97097bbc7d148c6d6b8aaa61ab3774850578f290abfb`。
- 安装包逐文件复制当前 canonical；1.x 分支、beta.1 tag 及旧附件未修改。ClawHub、SkillHub 本轮均未提交。
