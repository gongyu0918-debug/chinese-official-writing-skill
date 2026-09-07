# v1.6.29 发布记录

日期：2026-09-07（Asia/Taipei）。状态：`GITHUB_PUBLIC_RELEASE_CLOSED / SKILLHUB_EXACT_SIGNATURE_VERIFIED_AUDITS_UNCONFIRMED / CLAWHUB_PUBLIC_EXACT_VERSION_AND_SUBMITTED_FILES_VERIFIED`。初次传播未到齐，随后仅做只读复查，未重新提交。

## 产品与验证

- 用户明确授权先发布已成功的连续改稿接续、正文清理，再继续立项申请研究。实现提交为 `07c822de2d0788062f3bfdab36f4e1c025624202`，独立发行分支 `codex/release-v1.6.29`；产品提交及 tag 为 `52d60597c3850d9922b8959a619be80e21e9af83`。基于 main `b77f6381`，上一 tag v1.6.28 为祖先。main 已快进并与新 tag 一次 atomic push；后续证据提交不移动 tag。
- 相对上一产品只纳入六个 Hook 文件及版本坐标：Claude 同稿用户材料绑定、默认清理预处理后继续原审查、完整单 JSON 围栏接收，以及对应说明。Skill/references、自然字数解析、原稿事实纠错、示例和付费功能没有改动。自然字数和原稿事实纠错仍为 HOLD。
- [真实构建记录](hook-quality-build-r1/result.md)：两条正式原生会话共 13 版，保留旧第七版漏入和第八版实测恢复；最终解析器复放 13 请求、10 个已有 source hash 一致。P6 `755→589`、M6 `579→447`，正文逐字保全，清理预处理及后续默认审查均验证交付。有限样本不能换算总体无错率。
- 最终版本全量 **817/817 通过，131.951 秒**，五套 quick validate 通过，Claude companion 60 文件、fingerprint `ee5e80d57de31b7bf83c99f6729df249058a97df0b7167c7b1d25c897dd94cb9`，`claude plugin validate --strict` 通过。独立发布复核未发现 P1/P2；发布阶段没有新写稿模型调用。
- SkillHub 87 文件、ClawHub 无 Hook 包 37 文件，两平台 dry-run 通过，禁入文件扫描通过。SkillHub ZIP 成员逐字匹配冻结目录；ZIP SHA-256 `79bc71e180bee437b2f09a99397983603cda23d37928ca899ee7a97553d87ea9`，CLI content hash `b952326da9b02a57e297a1c40e749c5d7e6732c073a4bff0e2a7abd105ce312b`。导入 CLI 打包函数首次缺模块搜索路径，补充本进程路径后完成；未改产品或全局环境。

实际命令（Python 为 `C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe`）：

```text
python -B -X utf8 -m unittest discover -s maintenance/tests -p test_*.py
python -B -X utf8 C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py <canonical及四套普通Skill目录>
python -B -X utf8 maintenance/tools/build_skillhub_package.py --output output/release-v1.6.29/skillhub/chinese-official-writing --version 1.6.29
python -B -X utf8 maintenance/tools/assemble_hook_companion.py --host claude-code --output output/release-v1.6.29/claude-companion
claude plugin validate output/release-v1.6.29/claude-companion --strict
git diff --check
git push --atomic origin HEAD:main refs/tags/v1.6.29
```

同步兼容目录前逐一核准五个删除重建目标均在独立发行树 packages 内，无未跟踪文件或符号链接。逐文件范围、冻结包、实际提交参数及原始回执见[发布证据](release-v1629/publication-evidence.json)。

## 平台结果

- [GitHub Release](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.29) 已公开，`isDraft=false`、`isPrerelease=false`，`publishedAt=2026-09-07T06:08:55Z`。
- SkillHub.cn `@user_f3d82da7/chinese-official-writing` 唯一正式提交 `ok=true`，`skillId=70149`、`versionId=295346`、87 文件、fingerprint `485699313970764c1f125637bd0a978359bffaef847edb3194dcd7930d2da3de`，八个 tags 均指向 1.6.29。精确版本签名首查找不到，后续`verify --version 1.6.29 --zip ... --json`已返回`ok=true / content_hash_match=true`，签名issuer为skillhub.cn，与上传包content hash完全一致。三项审核在提交时为pending，本次签名校验不等于审核状态核验。
- ClawHub `gongyu0918-debug/chinese-official-writing` 唯一正式提交 `status=published`，`versionId=k978wxz7mfd37y3tkp1vg6h0b98dz4c3`、37 文件、fingerprint `bb199eb85fc0473a8b2030e1617b7fb76aeb2501f3bb8c3b588c727b1845954a` 与 dry-run 一致。source commit/ref绑定产品tag。后续`inspect --version 1.6.29 --files --json`已返回latest和精确版本1.6.29，所提交37文件全部逐项SHA-256一致，无缺失或变化；公开清单另有上传清单外的`skill-card.md`，共38项，不能称公开清单恰为37项。moderation verdict与汇总security status为clean，但security仍有hasWarnings，个别scanner报告未一致，不能称所有审核均通过。平台license元数据为MIT-0，包内LICENSE仍与发布的MIT文件hash一致；未修改仓库许可或重提版本。ClawHub无Hook，本次仅同步版本。

每个平台只提交一次，不因传播延迟重提，不把接受回执或旧版审核当作新版审核通过。

传播复查的原始结果及逐文件比较见[最终公开核验](release-v1629/propagation-final.json)。本次只更新证据，产品tag和包字节不变。

## 保留边界

Hook 默认关闭，本轮未修改本机安装、启用或信任。连续材料接续目前仅 Claude，最多 8 回合、4 MB 会话流和 4 万字符用户要求；其他宿主及分支历史没有新增在线覆盖。默认清理组合为真实模型 core Harness，不能冒称所有原生宿主均重新实测。首次尚未启动预处理且模块不可用时沿用原审查；预处理启动后模块不可用或回显耗尽则明确停止。一般事实错误、自然字数上限及“以下正文约……”包装变体仍有未闭环问题。
