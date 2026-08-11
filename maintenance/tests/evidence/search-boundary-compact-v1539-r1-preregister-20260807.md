# 单位名称搜索边界去冗余候选复验预注册（v1539-r1）

## 基线与来源

- 候选来源：v1537 系列 `codex/search-boundary-compact-v1537-r1`（d550ae4），原预注册 `search-boundary-compact-v1537-r1-preregister-20260806.md`。
- 本轮固定基线：`v1.5.38` 产品提交 `c3fa2128ef9426b4ebb135986a7e19feccf08421`。
- 候选已 rebase 到 1.5.38 之后的 main（968daac）。

## 单变量改动

删除入口联网搜索一条的末句"不因出现单位名称就搜索单位公开样文、固定格式或写作风格"。该边界继续由 `references/handling-elements.md`（原句 + 中性称谓）、`references/external-research.md`（"只出现单位名称，不触发搜索单位公开样文"）和 `references/review-checklist.md`（"未因单位名称自动搜索单位公开样文"）三处承载；入口"默认不外搜"、用户明确要求核验和时效事实触发条件不变。

不改三个 reference 的承接规则，不改脚本、输出模式、复核顺序和发布链。

## 验证计划

1. 工程门：全量 unittest（入口断言收敛到 handling-elements 承载）、Promptfoo smoke、固定 1.5.38 消融（P033 增加备选断言集）、quick validate、镜像同步幂等、`git diff --check`。
2. 真实 A/B（对固定 1.5.38，独立盲审；工具调用轨迹为主要证据）：
   - SB01 普通含单位名称的自然起草题：不得调用联网搜索；
   - SB02 明确要求核验现行政策的控制题：仍应进入公开来源核验路由。
3. 随机文风不计负项。

通过要求：SB01 不因单位名称自行联网，SB02 不失核验路由；任一条件不满足即不合并。
