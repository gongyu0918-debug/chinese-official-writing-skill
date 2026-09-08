# 1.6.30 冻结候选验收

候选由v1.6.29拆出，包含包内README、能力范围答复补全、一般用法与具体写稿分流、Hook说明互链和五套镜像；宿主与包版本元数据统一到1.6.30。根README仍准确标识已发布1.6.29。没有为了凑少量修复增加Hook行为。

不含R25全局分析、R26增项申请专页/路由、后续开发规则；全部writing references、scripts及Hook核心与v1.6.29一致，7个宿主manifest仅版本字段变化。main没有回退或修改。

## 验证

- `py -3.13 -B -X utf8 -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_skillhub_package_builder maintenance.tests.test_repository_reachability`：最终107项通过。首次5项失败是候选版本元数据未补全和新增spec未登记，已修正，未改变写稿规则。
- `py -3.13 -B -X utf8 -m unittest discover -s maintenance/tests -p test_*.py`：退出码、数量和耗时见[原始日志](full-tests.log)与[回执](full-tests.json)。
- 五套通用Skill执行 `quick_validate.py`，见[实际命令与结果](quick-validate.json)。OpenClaw另由仓库边界测试覆盖。
- `py -3.13 -B -X utf8 maintenance/tools/build_skillhub_package.py --output output/release-v1630-candidate/skillhub --version 1.6.30`：本地SkillHub包88文件，ClawHub无Hook包38文件。包清单为[SkillHub](skillhub-manifest.json)和[ClawHub](clawhub-manifest.json)，指纹按清单原始UTF-8字节计算。
- [范围检查](scope-check.json)核对已选README/入口与bb3eae9d一致（只允许候选版本变化），历史归档66项SHA256匹配。产品变动字节见[所选文件](selected-files.json)。

历史来源为 `cf4836c3` / `bb3eae9d` 的 `maintenance/tests/evidence/skill-package-readme/`；Git对象可追溯，本分支不复制全部历史实验。20次旧调用仅支持有限咨询分流，不是20份稿件通过。模型答复曾有过强保证，真实短申请仍有已记录问题；最后FAQ文字补全未新跑模型。本轮没有新的模型调用，不冒充新版宿主隔离证明。

## 明天使用这条基线

从 `codex/release-v1.6.30-candidate` 的冻结提交准备2026-09-09更新，勿从届时main整包取文件。发布前核对冻结提交、版本与清单指纹；如需新增写作规则或实现修复，应另建候选和验证，不能悄悄加进本冻结范围。

当前只冻结，不推送、不建tag、不创建Release、不上传平台，也没有安排自动发布。具体发布仍等待后续指令。未完成的事实纠错、多轮改稿与Hook稳定性留在后续主线。
