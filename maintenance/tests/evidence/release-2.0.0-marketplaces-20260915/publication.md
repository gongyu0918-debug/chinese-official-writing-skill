# 2.0.0 平台发布回执

2026-09-15 用户授权将昨天冻结的2.0.0 Skill主体发布至SkillHub和ClawHub；2.0.1抗AI候选未混入。

- 产品来源：`eb20eed0e0f63926c2ac49a7becfdda0baec6212`，与 `release/2.0.0-frozen-20260914` 及73文件冻结清单一致。
- SkillHub：一次提交成功，version `2.0.0`，versionId `313206`，回执 `ok=true`；审核和安全扫描状态为pending。本次按用户规范以成功提交为完成，不等待后续审核。
- ClawHub：一次提交成功，version `2.0.0`，versionId `k97atgngzym9spgwc1xth23ys98ecj98`，回执 `status=published`；包fingerprint `9603879f182ff924ee8d408b458cd2a27ddf38a546eea08a74a85e053333cac2`。回执中的latestVersion仍显示1.6.36，不据此重传或追加查询。
- 两个平台均保留73文件；SkillHub使用既有构建器生成平台元数据和LICENSE.md，ClawHub使用标准Skill包；正文规则与脚本逐文件绑定冻结源码。
- 验证：两平台 `publish --dry-run --json` 均通过；实际 `publish --version 2.0.0 --changelog <release-notes.md内容> --json` 各执行一次，返回码均为0。
- 无发布后只读核验、无传播轮询；未移动GitHub tag或修改Release，未合入2.0.1候选。

实际命令的参数由文件读取并作为进程参数传入，回执、首次提交标记、退出码和包清单保留于本目录。
