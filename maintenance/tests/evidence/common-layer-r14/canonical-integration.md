# 共性主线落入 2.0 开发候选

本次在 `codex/reference-rewrite-20260912` 继续，基于提交 `4a47407b7ae6671d0668ddb72d22134865cf7472` 的干净产品树接入完整 R13。冻结 1.x 金线为 `1ce7112303172478faa2392667a2de1098eb912c`；本次没有合入 main、推送、安装或发布。

## 实际变化

- 取材、事实与文种复核、交付归并到 writing-rules；抗 AI 味和文稿扫描用法保持独立且可达。
- 删除已归并的 information-selection、final-review-layers、delivery、task-route-cards、short-draft-naturalness 五页。所有稿件使用同一共性主线；短稿自然段优化、普通完整稿 80 字下限、局部范围及复杂任务按需专项能力保留。
- 同步五个过时“首页编号检查”、两个泛称交付页的指向，以及“得”字提示的适用范围。两个普通脚本逐字未变。
- 五份仓库兼容镜像、旧页功能映射、机器清单及维护评测器改接当前页面。维护评测器仍是预选上下文工具，其静态测试不代替模型自主选路。

当前 68 页 references；首页 2356 字符；共性三页 1737 + 905 + 435 = 3077 字符。与前期 R8 的五页 5944 字符相比减少 48.23%。这不是相对 1.x 全 Skill 的 token 或质量收益比例。

## 验证及限制

整套来源 R12/R13 的原生写稿、匿名评阅与局限见 [R12](../common-layer-r10/r12-results.md)、[R13](../common-layer-r10/r13-results.md)；独立文件语义对照见 [整合审计](canonical-adoption-audit-r14.md)。原始输出、失败和复跑均保留，不把文件精简扩写为全面不回退结论。

当前整合最小检查：

- `python -B -m unittest maintenance.tests.test_reference_uniqueness maintenance.tests.test_draft_length maintenance.tests.test_mit_script_boundary maintenance.tests.test_scene_filler_lint`：23 项通过。首次执行其中三个模块时，2 项仍查旧页或旧首页路径；更新到实际共性归属后复跑通过，未恢复旧页或删除脚本。
- `python -m unittest maintenance.tests.test_reference_rewrite_contract -q`：29 项通过。初次一条旧许可字面断言失败，按用户最新要求保留 1.x 及既有 Hook 的 MIT 分线后通过。
- Skill Creator 的 `quick_validate.py chinese-official-writing`：通过。
- 唯一性工具：未检出相同的长正文规则行及选定交付偏好错位。语义重复、临时选错叶及执行是否有效仍由独立审计和真实写稿判断。

未运行合并或发布全量门，未声称完成全体文种对旧 1.x 的最终验收。当前没有新写稿专门覆盖整合时八处修正；这些是经过静态语义审计的路径与语法精确化，不能外推为真实质量改善。

R14 的 A/B 原子及 AB 组合继续使用独立冻结快照，未随整合进入产品。另已定位采购公告用途、函的审批表达、编者按混入消息规则及路由表重复的问题，留作独立修复和实写回归。
