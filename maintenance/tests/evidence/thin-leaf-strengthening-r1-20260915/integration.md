# 意见、说明两页合入记录

日期：2026-09-15。用户本轮明确授权：选择表现较好、达到准入标准的部分合并。

## 已合入范围

本地 `main` 从 `9c4f12166c3a6a5920153b6e28a57d781993bb36` 快进至 `77a0c86af72e2818be01dc274c75396156682ef4`，保留完整实验和取舍历史。

- 意见页：补清上报、下发及向不相隶属单位提出意见时的语气、对象和收束。
- 说明页：补入文件起草、修订说明的内容选择，并区分实际业务变化与新稿的确认、施行状态。
- 公报试加内容已经撤回，不进入产品净差异。其他文种、首页、脚本和版本号保持原样。

两页合计增加 348 个 LF 归一化字符，没有增加页数或读取层级。合入产品树为 `b3aa18e7b396831b9ee8c55675ee0f6ec605ca48`，与最终受测产品提交 `c7e6deb17e6142da5c60d3ec569dba5e5bca773f` 完全一致。

## 准入依据和限度

采用已有 40 次原生真实写稿及独立审阅，不因合并再重复调用模型。完整读取主叶的最终 8 对比较，经逐稿校准为候选较好 2 对、基线较好 2 对、接近 4 对；另 1 对保留为端到端观察，不计入规则效果比较。详见 [结果](result.md) 和 [审阅校准](adjudication.md)。

这些证据支持保留必要功能补充，未发现新增的跨模型共性回退；样本不足以证明所有文种质量、费用或速度全面提升。MiniMax 偶尔补入具体流程、字段等问题仍然存在，候选和基线的失败均保留。公报的必要补充依据不足，故撤回。

## 本次工程核对

以下命令只检查结构和路径，不承担写稿语义评分：

```text
python maintenance/tools/audit_product_surface.py --root chinese-official-writing
python C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing
git diff --check main...HEAD -- chinese-official-writing
git -c core.whitespace=-blank-at-eof diff --check main...HEAD
```

以上在快进前候选工作树执行，均返回 0。普通全差异 `git diff --check main...HEAD` 提示 3 份盲审包末尾各有空行；它们是已绑定哈希的审阅原件，保留原字节。产品差异没有空白错误；仅本次命令关闭文件末尾空行告警，未修改 Git 全局配置。早期 `checks.json` 保留当时验证记录，本页补充集成检查结果。

## 本机同步与发布边界

本地 main 已合入，本机 Pro 的普通写作层已同步到 `77a0c86a`。首次同步发现本机仍绑定旧重构分支，且指定投影工作树已经缺失：备份本机配置后改为跟随 `refs/heads/main`，从保留的专用投影分支 `64d7ca59` 恢复目录，再运行既有同步工具；没有修改同步器或 Pro 功能代码。

重试返回 0、状态 `INSTALLED`，旧安装及配置备份保留。构建来源为已提交内容，安装文件和宿主缓存比对通过。另将两份已安装叶子逐字节对比 `git show 77a0c86a:chinese-official-writing/references/<叶子>`，均相等；Windows 工作树的 CRLF 与 Git blob 的 LF 差异已单独排除。

宿主返回的两条 Hook 均为启用、可信；安装回执的 `activation_state` 仍记为 `AWAITING_HOST_TRUST`，此处保留两种状态来源，未据此声称新增原生生命周期或在线写稿验收。本轮真实写稿结论继续只来自上述普通版隔离 A/B。

未推送、打 tag、发布平台或重制桌面发行包。
