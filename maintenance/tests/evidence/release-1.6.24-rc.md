# v1.6.24 本地候选记录

日期：2026-09-02。

状态：`PUBLISHED / SEE release-1.6.24.md`。下文保留正式提交前的本地冻结快照；最终回执与传播状态见 [`release-1.6.24.md`](release-1.6.24.md)。

## 候选边界

- 冻结产品基线为 `ecca5604e9c1f2b948e70d0611b3c36a7e4216be`，版本坐标提交为 `49655451300d6a21d157c901da11051f5613c396`；合并 v1.6.23 已发布回执后，产品 tag 目标为 `105fc3b134ef2c17fb8a541a6e41ec1859c12bb3`，分支为 `codex/release-v1.6.24`。
- 上一公开产品为 `v1.6.23^{commit}=6a6ededa7e3dc949e0afe1a9b3329014c260ad60`，是当前候选祖先。本地 annotated tag `v1.6.24` 已固定到上述产品提交；本记录写入时尚未推送 tag、创建 GitHub Release 或向 SkillHub.cn、ClawHub 提交。
- 相对 v1.6.23 的产品增量仅包括：`WR-005b` 由固定字数阈值改为结合文种、材料密度和交付形态识别短稿任务，以及可选 Hook README 将使用说明前置、暂停和关闭说明后移。后续建议反馈、小标题、短意见等候选不在本 tag 祖先中。

## 本次工程门

- `git merge-base --is-ancestor v1.6.23 105fc3b1`：通过；固定上一 tag 是候选祖先。
- 聚焦回归：`python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_hook_layer_contract maintenance.tests.test_status_ledger_consistency`，101/101 通过。
- 一次全量回归：`python -m unittest discover -s maintenance/tests -p "test_*.py"`，756/756 通过，耗时 127.876 秒。
- canonical、Agent Skills、Qwen Code、QwenWork、Hermes 五套 `quick_validate.py` 均通过。
- `sync_adapters.py` 复跑后镜像保持幂等；`git diff --check` 通过。

## 本地包预检

- SkillHub.cn 清洁包位于 `output/release-v1.6.24-105fc3b1/skillhub/chinese-official-writing`，共 83 文件，规范化文件树 fingerprint 为 `c7c154b748b4ab974b893da564a9282e20cdc2751b1469f1f8e43c8eb01fe59f`；slug 为 `chinese-official-writing`、展示名为“中文公文写作”、版本为 `1.6.24`，含 `LICENSE.md`，排除根 `LICENSE` 与 `agents/openai.yaml`。官方 CLI dry-run 返回 `dryRun=true`、slug 和版本正确。
- ClawHub 无 Hook 包位于 `packages/openclaw/skills/chinese_official_writing`，共 34 文件，本地规范化文件树 fingerprint 为 `58db6cfcafb14b886619faaa677981e56bdae20e80c82099b013424e49dc09f2`；平台 dry-run fingerprint 为 `ac29da4032bf9b9bedf0c788286caf6f9bf27519efd10d52e18eca7164fcd7db`。平台 slug 为 `chinese-official-writing`、展示名为“中文公文写作”、owner 为 `gongyu0918-debug`、版本为 `1.6.24`，34 文件；Hook、付费提纲、红头实现、`agents/openai.yaml` 等禁入项命中为 0。
- GitHub `v1.6.24` tag 和 Release 的远端缺失已在提交前只读确认；SkillHub.cn 与 ClawHub 正式发布命令均未执行。

## 剩余边界

- 外部发布已复用产品提交 `105fc3b134ef2c17fb8a541a6e41ec1859c12bb3` 和上述两个已预检包面；平台接受后只做只读传播核验，不重复提交。
- 本记录及后续回执提交位于产品 tag 之后，不改变 v1.6.24 产品字节。
