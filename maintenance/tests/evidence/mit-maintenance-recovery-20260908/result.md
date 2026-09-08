# MIT 主维护状态恢复

2026-09-08，在应用新建的独立工作树接手，分支 `codex/mit-speech-revision-r10`。起始工作树干净，HEAD与本地main为 `05c4465fe6aa6187f31f0879120cc616a6f31e63`；保存的origin/main为 `73d20160e1a52748569fafd973f8f172f1ce0a47`，ahead16/behind3；v1.6.30为 `d2f97ba05e592712ec4b73decceefb3fd29d7c5e`。没有fetch，不声称实时远端状态。

## 已恢复的主线

- [R25](../global-grounded-analysis-r25/result.md)、[R26](../application-current-main-r26/result.md)及其集成记录已在本地main；保留有据分析与精简混合路线，事实、多版及Hook质量仍开放。
- [包内README](../skill-package-readme/result.md)与有限咨询路由已选择性进入1.6.30。发布证据位于提交 `73d20160e1a52748569fafd973f8f172f1ce0a47`，可用 `git show 73d20160e1a52748569fafd973f8f172f1ce0a47:maintenance/tests/evidence/release-1.6.30.md` 核对。该记录确认GitHub Release公开、ClawHub38文件匹配且安全扫描clean；SkillHub一次接受回执，最后记录公开传播和审核待核。此处复核已有记录，未重新查询平台，也不重复上传。
- [WR-029 R9](../speech-viewpoint-minimal-r9/result.md)仅入口一句合入，累计88次调用、87技术有效；新页和路由撤回，全稿未通过。WR-030/031继续TODO。HK-002a、CL-001的部分完成与HK-010、HK-002b的HOLD保持。

## 本机同步后续完成

R9集成时的来源绑定失败保留为历史。独立Pro修复工程 `F:/Workspaces/owp-local-pro-source-binding-fix-20260908`，证据HEAD `5be412f1810b21a34aa5093d1f3b2cfc42056c40`，证据目录 `evidence/local-source-binding-fix-20260908/` 的README、validation及after记录：修复后27+10项相关测试通过，真实PREPARED→INSTALLED→UNCHANGED。付费实现和配置留在Pro工程。

本任务再次逐文件读取实际安装缓存 `official-writing-pro/0.4.11/skills/chinese-official-writing-pro/mit`，与 `git show main:<canonical路径>` 的原字节比较SHA-256：ENTRY、README和36 references共38/38匹配，0差异。ENTRY SHA-256为 `da8aad64cd43d660ca6ff6df3272760e38a61626e2b01594ba4fccd604d9964e`。没有重复安装。

完整注册源与缓存一致、单一Pro启用及两Hook trusted/enabled引用独立修复的after记录；本轮未重新查询宿主列表。修复任务的离线握手通过，真实宿主写稿Hook未重跑，安装器AWAITING_HOST_TRUST原值保持。38/38只是普通文件当前一致，不能替代上述宿主执行状态。

已更正spec中的本机同步待处理和DOC-001未发布条目，不改变main版本字段，不把R25/R26标成已发布，不把另一付费分支的SYNC_REQUIRED改成完成。此次仅恢复维护状态，后续WR-029原型及真实稿另见[R10预注册](../speech-revision-r10/preregister.md)。
