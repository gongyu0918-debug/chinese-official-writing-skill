# v1.6.25 本地候选记录

日期：2026-09-02。

状态：`LOCAL_TAG_FROZEN / PREFLIGHT_PASSED / PUBLICATION_PAUSED_BY_USER`。本记录只证明本地候选冻结和发布前验证；未推送 tag、未创建 GitHub Release，也未向 SkillHub.cn 或 ClawHub 正式提交。

## 候选边界

- 当前 `main` 产品基线为 `821364abfd7df2fa0af04f5e3ab7277897110ff0`；版本坐标提交为 `cf8e181591ea01ba81138352c12b5b93a8acf098`，分支为 `codex/release-v1.6.25`。
- 本地 annotated tag 的 tag object 为 `b41a173d302bb577da4cdcb3ab62205295d51980`，`v1.6.25^{commit}=cf8e181591ea01ba81138352c12b5b93a8acf098`。上一公开产品 `v1.6.24^{commit}=105fc3b134ef2c17fb8a541a6e41ec1859c12bb3` 是候选祖先。
- 相对 v1.6.24 的写作产品增量为：`WR-025 / WR-008b` 建议反馈专叶与标题版式规则、`WR-025c` 第一方证据顺序与建议型分项标题；`WR-025d` 只形成基线充分证据，没有产品改动。版本坐标提交只同步版本号，不改变写作规则或 Hook 行为。
- 付费提纲、红头 DOCX、付费 Hook 及独立付费线程内容不在本 tag 中；ClawHub 继续使用无 Hook 清洁包。

## 本次工程门

- `git merge-base --is-ancestor v1.6.24 cf8e1815`：通过；固定上一 tag 是候选祖先。
- 聚焦回归：`python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_hook_layer_contract maintenance.tests.test_status_ledger_consistency`，104/104 通过。
- 一次全量回归：`python -m unittest discover -s maintenance/tests -p "test_*.py"`，765/765 通过，耗时 120.681 秒。
- 冻结记录写入后复跑 `python -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability maintenance.tests.test_skill_boundary`，102/102 通过；本测试同时锁定公开版仍为 v1.6.24、v1.6.25 没有发布记录以及候选证据可达。
- canonical、Agent Skills、Qwen Code、QwenWork、Hermes 五套 `quick_validate.py` 均返回 `Skill is valid!`。
- `python maintenance/tools/sync_adapters.py` 复跑前后产品树无差异；185 个受控 Python 文件通过语法解析，190 个受控 JSON 文件通过解析，`git diff --check` 通过。
- `v1.6.24^{commit}..cf8e1815` 共 140 个变更路径；付费、红头、提纲禁入路径命中为 0。

## 本地包预检

- SkillHub.cn 清洁包位于 `output/release-v1.6.25-cf8e1815/skillhub/chinese-official-writing`，共 84 文件，规范化文件树 fingerprint 为 `ac419578fd3da59b763fa68c9e5d8a57a94ea37cbb5eb7b593482953bf9e7955`；slug 为 `chinese-official-writing`、展示名为“中文公文写作”、版本为 `1.6.25`，含 canonical Hook，排除根 `LICENSE` 与 `agents/openai.yaml`，使用 `LICENSE.md`。官方 CLI dry-run 返回 `dryRun=true`、slug 和版本正确。
- ClawHub 无 Hook 包位于 `packages/openclaw/skills/chinese_official_writing`，共 35 文件，本地规范化文件树 fingerprint 为 `09ad6064bf1cb9aee91019eef889a5eb36a3b3af7945572c2409b05233a90c4a`；平台 dry-run fingerprint 为 `a1298d045f7ee6aadc5b5304da26530e12fb478c0bb038796ef0444d6f4f6c9e`。平台 dry-run 返回 `would-publish`，slug 为 `chinese-official-writing`、展示名为“中文公文写作”、owner 为 `gongyu0918-debug`、版本为 `1.6.25`、文件数为 35；Hook、付费提纲、红头实现、`agents/openai.yaml` 等禁入项命中为 0。
- SkillHub.cn 当前账号为 `user_f3d82da7`；公开 latest 为 v1.6.24。ClawHub 当前 owner 为 `gongyu0918-debug`；公开 latest 为 v1.6.24。GitHub 远端不存在 v1.6.25 tag 或 Release。以上均为只读查询或 dry-run，不是发布回执。

## 暂缓与复用边界

- 用户已明确暂缓发布，因此没有执行 `git push`、GitHub Release 创建、SkillHub.cn 正式发布或 ClawHub 正式发布命令。
- 后续如重新授权发布，应复用 `v1.6.25^{commit}=cf8e181591ea01ba81138352c12b5b93a8acf098` 和上述两个包面；先复核本地 tag、包 fingerprint、远端缺失与账号/slug，再按每个平台一次提交执行。
- 本记录和后续状态提交位于产品 tag 之后，不改变 v1.6.25 产品字节。若冻结产品提交或包 fingerprint 发生变化，应废弃本候选并重新走发布前门，不能沿用本记录冒充通过。
