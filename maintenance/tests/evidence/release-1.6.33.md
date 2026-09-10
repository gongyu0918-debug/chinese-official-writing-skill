# v1.6.33

正式词语按语义审校：保留具有具体对象、专业含义或必要强调作用的表述，减少按词频机械换词；空泛评价仍依据已有事实处理。

## 产品范围

以已发布v1.6.32（`236784ef`）为基线，纳入当前main已验证的Q1高频正式词段（来源 `b997a0ff`）。只改 `references/anti-ai-patterns.md` 的一个段落，5409→5340个LF字符，减少69。首页保持7930字符；路由、其余写作叶、Hook与脚本行为保持原版。七个既有adapter只更新version字段，另同步既有发布元数据与安装说明。

本次不迁入main的增项申请、讲话修稿、源事实Hook、脚本/字段/结构/压缩细则、术语页、函件路由、篇幅复核、算力示例、总审结构归位和局部修改触发调整。完整待续范围见[存量清单](release-v1633/writing-scope.json)，没有将当前main整树发出。

写作冻结 `dded78a7`；版本字段完成后的产品提交 `5d84c5d3`，canonical tree `bc9f538eab44cf8d83d3e6af33018c52bd24d658`。后续提交只记录验证及发布，不改变产品树。

## 真实写稿与工程

对v1.6.32重新运行原五题及五条便宜通道。12次调用、11份技术有效终稿、5组同档完整对照（4组max、1组high）；GLM候选max的502及duplicate-tool-result技术失败保留，仅按预登记补一次两臂high。四组双臂确实读取修改叶，一组为未读该叶的旁路控制。

根任务逐字读取全部十份选定终稿并核对SHA，没有观察到该单原子的候选单侧事实、状态或文种硬退化。候选定向审稿仍有过程自报和欠准确的“自指”理由；旁路说明多“特此说明”，不能归因于未读取的改动页。不宣称每项更好或每份首稿完美。详见[写稿报告](../../docs/release-v1633-writing-validation.md)、[逐稿路径和SHA](release-v1633/writing-summary.json)、[归档](release-v1633/archive.json)及[根复核](release-v1633/root-review.json)。

相关116/116、唯一一次全量827/827、五处常规quick_validate通过。首轮封包发现未改索引页的LF/CRLF字节差异；保留失败记录，最终生成包只恢复该页原Git字节，未改规则、未扩大允许差异集合，也未重复全量和quick。GitHub/SkillHub/ClawHub分别90/90/40文件，两个市场的文件集合均与v1.6.32相同。详见[工程报告](../../docs/release-v1633-engineering.md)和[包清单与SHA](release-v1633-engineering/package-manifests.json)。

## 并行的本机Hook核验

当前完整main所对应的Pro安装另做了一次隔离交互式Codex 0.144.6／GLM max任务，UserPromptSubmit及Stop实际执行，唯一正文与task_complete一致，安装状态刷新为ENABLED。此为本机现有Pro的执行核验，不是1.6.33新增Hook功能或纠错效果的证明。

Pro证据独立提交在 `codex/pro-hook-verification-20260911@3e88b508`，路径 `evidence/installed-hook-20260911/README.md`。原验收器遇最终消息phase缺失，已保留不兼容结果并用同份完成事件作限定复核，没有改写rollout或生产验收器。自动审批拒绝隔离目录及逐文件清理，原始临时文件仍留本机隔离目录；不将执行核实说成包含清理在内的完全闭环。

## 发布状态

已完成准备，三平台正式操作及成功回执单独记录。沿用用户此前已授权的GitHub、SkillHub、ClawHub更新流程及本次指定的1.6.33小范围；不将其他main存量附带发布。两个市场各提交一次，成功回执即完成，不再提交后只读核验或等待审核。
