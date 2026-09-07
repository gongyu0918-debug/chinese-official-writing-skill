# R26 本地合并登记

2026-09-08，按用户此前“经过真实写稿验证、可用即可合并”的持续授权，将 `codex/application-current-main-r26` 合入本地 `main`。

- 写稿基线：`fe1c30fac2b57661f077a36d1243c42eb4a0415b`。
- 合并前main：`2fe748fb5c4e11e3cb890e260f402fdbb380ed5d`。新增的AGENTS与两份维护文档全部保留；相对写稿基线，产品和测试未变。
- 产品提交：`362dc826203bad108b587232405f1f359b14bcb1`。
- 实际命令：`git merge --ff-only --no-stat codex/application-current-main-r26`，成功；合并后main工作树干净。第一次尝试遇到短暂的其他Git进程锁，未删除锁，待其自然消失并重核基线、清洁状态后重试。

## 合入范围与实际验证

仅合入申请入口、一个精选增项专页、五套普通镜像、对应路由断言，以及本轮原稿和需求记录；没有将R23/R24整分支或旧Hook增量带入main。canonical净增5616字节，reference任务读取的有限减载口径见[写稿结果](result.md)。

真实写稿使用Claude Code CLI隔离会话，Qwen 3.8 Max与MiniMax M3三题两臂共12次，11次符合约定工具范围。五组成对偏好混合2、旧2、平1；原稿全部保存，不宣称总体正确率提高。用户本轮澄清继续使用现有Harness测试即可，因此没有调整本机安装。

写稿通过有限收益判断后，实际执行 `py -3.13 -B -X utf8 -m unittest discover -s maintenance/tests -p test_*.py`：817/817通过；五处 `quick_validate.py` 通过，清洁包89文件，归档来源、匿名包和评阅原字节核验通过。原始失败及完整命令见[验证记录](validation.json)。

rebase只接纳并发的三份开发文档；产品和测试与已跑回归的版本逐字节一致。合并后的本登记和规格更新为文档变化，检查链接、JSON和Git差异，不重复模型调用或全量回归。

## 保留边界

`WR-023b` 为 `IN_PROGRESS / R26_SELECTED_ROUTE / MERGED_LOCAL / NOT_RELEASED`：精选组合已合入；具体事实补写、局部状态遗漏、长稿多版任务与Hook同稿事实校正仍开放。R23纯新加R25未作为第三个当前对照臂，不能据此给三臂做完整排名。

本轮没有推送、移动tag、创建Release、上传平台或改动本机Skill安装。v1.6.29仍是原发布事实，本地89文件同版本包只是验证预览。
