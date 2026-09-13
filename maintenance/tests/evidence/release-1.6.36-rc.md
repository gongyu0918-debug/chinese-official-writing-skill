# v1.6.36 候选记录

## 基线与范围

- 已发布基线：`origin/main@c0abfeeb3d2a21cfd6ec722de7d8ae534ad68f61`，对应 v1.6.35 tag 解引用提交。
- 1.0 主线来源：本机 `main@1ce7112303172478faa2392667a2de1098eb912c`。
- 候选合并：`42b65ed8` 在独立分支汇合两条历史；本机及远端 `main` 均未改动。
- 产品范围：更聚焦的文种路径、讲话开场人物顺序规则、说明式开场检查，以及 v1.6.36 版本元数据和派生包同步。

## 公开更新说明

候选更新说明见 [`release-v1636/release-notes.md`](release-v1636/release-notes.md)。正文只写相对 v1.6.35 的正向改进，并明确所有公开 Skill 包继续采用 MIT 许可证。

## 验证

- `py -3.13 -B -X utf8 -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_repository_reachability maintenance.tests.test_status_ledger_consistency`：110/110 通过。
- `py -3.13 -B -X utf8 -m unittest discover -s maintenance/tests -p 'test_*.py'`：851/851 通过，耗时 158.296 秒。
- Skill Creator `quick_validate.py`：canonical、Agent Skills、Qwen Code、QwenWork、Hermes 共 5/5 通过；OpenClaw 扩展 frontmatter 由仓库边界测试覆盖。
- `sync_adapters.py` 复跑前后状态清单一致，`SYNC_IDEMPOTENT=True`；`git diff --check` 通过。
- 已发布基线与本机 1.0 主线均为候选祖先。七份仓内 Skill `LICENSE` 的 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`；六个 JSON manifest、DeepSeek Harness package 和 OpenClaw frontmatter 均声明 MIT。

## 候选包

- 候选产品提交：`2a629d361bbfab8c1d884bdf802544a7c2c0790a`。GitHub 候选以该提交树为准，不创建 tag 或 Release。
- SkillHub clean package：104 文件，版本 `1.6.36`，生成的 `LICENSE.md` 与根 MIT 许可证同哈希；ZIP SHA-256 为 `f510a244dcf6923aca6d01f6e7506e6c7b513e0b10e55ef28ef2944799fbd7ac`。本地 CLI dry-run 返回 `dryRun=true`。
- OpenClaw/ClawHub 无 Hook 包：53 文件，包内 `LICENSE` 与根 MIT 许可证同哈希；ZIP SHA-256 为 `05b09c4a6c7991fdb6f39852f0f2c3f3d207a6b8fd4e75e81fbb305a1e5b77c2`。ClawHub dry-run 返回 `status=would-publish`、`latestVersion=1.6.35`、fingerprint `b50501d2fe66e8d209298f71038b8c8b26ce0807f1162cc4e781b711428db699`。
- 本地制品目录：`output/release-v1.6.36-candidate-2a629d36/`。两个平台 dry-run 均复用 `release-v1636/release-notes.md` 的同一份正向自然语言说明。

## 外部状态

本轮只准备本地候选；未推送 `main`，未创建或移动 tag，未创建 GitHub Release，未向 SkillHub 或 ClawHub 提交，也未联系 2.0 构筑线。
