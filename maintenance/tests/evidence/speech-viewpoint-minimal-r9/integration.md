# WR-029 本地集成与安装状态

2026-09-08。用户本轮授权继续构建、可用后合并。工作分支 `codex/speech-role-leaf-r1`，合并前 main 干净且仍为 `c7778f2627d025bc34f106cb8cb74bcf03fb011b`。独立复核未发现最小入口修正的产品阻断项后，执行 `git merge --ff-only --no-stat codex/speech-role-leaf-r1`，本地 main 快进至产品提交 `fb808f4927aca935f22c33fb8d78e1e4bc8bdc26`。

最终相对旧main产品只含canonical及五镜像的入口视角一句替换，canonical增加33个LF口径UTF-8字节；原有references和Hook均未改变，新讲话叶及路由撤回。实验和竞品研究记录进入maintenance；产品包不携带这些维护证据。WR-029登记 `PARTIAL / ENTRY_FIX_MERGED`，不是讲话专项或事实稳定性已完成。

真实稿、失败、比较和逐项检查见[结果](result.md)、[验证](validation.json)。本轮新增64次、累计88次真实调用，87次技术有效；R9六稿仅支持三类身份保持，未宣告全稿质量通过。全量测试817项首次815通过、1旧断言失败、1未暂存删除造成的打包错误；修复后86项相关测试通过。没有把补跑描述为再次全量817/817。

## 本机更新首次未完成（历史）

按既有本机同步授权运行 `sync_local_pro.py --config <local-config>`，退出码1，安装前拒绝：`selected local main does not contain the fetched remote main`。同步器参照的本地 `origin/main` 为 `73d20160e1a52748569fafd973f8f172f1ce0a47`，其分叉对应1.6.30选择性冻结、准备发布及发布回执三次提交。本次选定main有后续立项路线等本地改动；未为通过同步器引入额外发布分支合并或跳过来源检查。

工具已在其专用投影中接收main，来源绑定环节未通过，未走到新包安装。只读复查现存Pro安装：注册源与缓存一致，38/38普通规则仍匹配旧main `c7778f26`；37/38匹配本轮新main，仅 `mit/ENTRY.md` 未更新。插件列表观察到一个Pro安装且启用。未在本轮重新核对Hook信任或执行真实宿主Hook，不据插件启用声称Hook已验证。[脱敏安装核对](local-installation-check.json)。

当时待处理事项：解决选择性发布造成的本地main与来源绑定历史分叉后，再用原同步流程更新并核验入口。在此之前，仓库中的修正已合入，本机日常Pro内的普通入口仍是旧版；不得记“本机已生效”。

2026-09-08后续：独立Pro工程已修复并完成真实安装，接手任务再次核对实际缓存，38/38普通规则原字节匹配main `05c4465f`，无需重复安装。真实宿主写稿Hook未重跑，安装器AWAITING_HOST_TRUST保留；详情和证据提交见[维护恢复记录](../mit-maintenance-recovery-20260908/result.md)。上文首次失败不改写为成功。

## 外部状态

没有推送、创建Release、上传GitHub/ClawHub/SkillHub或移动tag。`v1.6.30`仍为 `d2f97ba05e592712ec4b73decceefb3fd29d7c5e`。当前main包版本字段仍1.6.29，本轮不是新发布。
