# 专项叶研究结论

2026-09-18，基于 main `70d241ca` / 2.0.4。**四路明文研究完成；值得进入最小候选与真实写稿验证，尚不构成合入依据。当前产品字节没有改动。**

## 从真实稿件得到的方向

| 范围 | 建议采用的方向 | 已有能力及减负边界 |
| --- | --- | --- |
| 经费预算附加页 | 支出与任务对应；分项测算；总额、年度安排、本次申请各自的口径；付款条件与本次请求相连；正文与明细一致 | 简单单项采购沿用请示叶。既有增项申请的单位与阶段规则能复用，不另复制事实边界 |
| 信息化建设附加页 | 已有系统与本次新增/改造/运维范围；业务与功能对应；数据、接口和迁移衔接；建设与后续运维费用；交付、试运行、验收的实际阶段 | 仍按请示、方案、可研或技术需求选主叶。只有确有相应内容时展开；普通服务器采购和新闻不会因词语相近而全读 |
| 采购既有组 | 补采购范围与价格含项、需求与交付验收的对应；更正公告的对象及前后内容 | 申请、响应、结果、终止的基本骨架已有覆盖，保留现有少读路径 |
| 整改既有组 | 统计时点、问题数/事项数等口径；措施、阶段结果、完成及复核证据对应；合理原因和下一步建议 | 问题-原因-措施骨架已具备。旧报告页部分表达偏窄，先测试澄清效果；不新增一套固定销号程序 |

真实稿件给出的优势是具体关系：钱怎么对应事项、改造如何接续存量、整改结论如何对应结果。没有依据要求把所有模板字段加入每篇正文。

## 选用的代表来源

- 短拨款请示：[扎兰屯](https://www.zhalantun.gov.cn/OpennessContent/show/515674.html)；总额与附表：[崇明](https://www.shcm.gov.cn/govxxgk/cjz/2025-12-15/9d6f4a67-ae15-4482-83d1-33e0f3c7927c.html)；跨年计费：[惠阳](http://www.huizhou.gov.cn/zdlyxxgk/ggzypz/zfcg/content/post_5491193.html)。这些页面的具体正文已从研究调用记录回读，主代理 web 工具单独访问失败的情况保留，不冒充再次联网成功。
- 系统改造：[九江批复](https://fgw.jiujiang.gov.cn/zwgk_205/xzsyxsf/zdjsxm/lxkypf/202503/t20250303_6861940.html)、[南通批复](https://shuju.nantong.gov.cn/ntsxzspj/pzjg/content/4d919f98-ec6c-41db-bf58-337568cd9438.html)；年度运维：[上海市民政局部门预算](https://www.shanghai.gov.cn/cmsres/ec/ec1850a9aea44c2f98f11fb3022b0e2d/5b67842fa15aaf31617a884078295f3c.pdf)。公开管理办法和空模板只作辅助。
- 整改汇总：[深圳绩效审计整改报告](https://www.sz.gov.cn/szzt2010/zdlyzl/sj/content/post_10563400.html)；具体问题及后续：[奉贤教育局整改报告](https://www.fengxian.gov.cn/jyj/gsgg/20250120/83002.html)；采购原文及高校整改链接见 [来源纠正](source-corrections.md)。

研究中出现的法规、金额标准、支付比例、试运行月数和当地流程只说明该样本的写法，不构成面向所有用户的默认要求。

## 竞品能借鉴什么

直接阅读的第三方包含医疗信息化解决方案、投标编写和政府项目脱敏工具。最可借鉴的是 [medinfo 的需求响应与证据对应](https://raw.githubusercontent.com/wangsanxing3210/medinfo-solution-expert/main/references/bidding.md) 和 [gov-bid-writer 的需求逐项分析](https://raw.githubusercontent.com/jytpeterjiang/gov-bid-writer/main/references/procurement_analysis.md)；其中部分能力与本产品已有核对原则重叠，只适合在采购场景里具体化。

未复制第三方代码或规则原文。不采用行业投资区间、固定篇幅公式、每章必有表格、必须无偏离等约束。自己的仓库及同源镜像排除在独立竞品证据之外；无可见许可证的对象仅用于了解一般方法。各原始报告的粗略规则建议已经由主代理筛选，完整拒绝/修正项见 [候选方向](candidate-directions.md)。

## 明文调用结果

| 任务 | provider/model | 实际结果 |
| --- | --- | --- |
| 预算 | alibaba-token-plan/deepseek-v4.1-flash | max，431.47秒，报告完成 |
| 信息化 | alibaba-token-plan-2/deepseek-v4.1-flash | max，566.72秒，报告完成 |
| 采购/整改 | command-code/deepseek-deepseek-v4.1-flash | max研究900秒超时；已有真实资料，同通道high仅整理115.33秒，完成报告 |
| 竞品 | ollama-cloud/deepseek-v4.1-flash | max，完成报告，时长见receipt |

原生CLI以明文stdin派发；独立临时上下文和叶子副本，未加载本机Pro/Hook。桌面子代理接口的两次加密失败单列，不记作研究完成。原始报告、prompt、模型参数、耗时和trace路径均保存。采购续次错误链接已从下载记录修正，原始报告保留以便追溯。

## 验证与未完成

- 实际运行：`python maintenance/tests/evidence/scenario-leaves-20260918/research.py`；三个任务max直接形成报告，采购初次超时后由明文high续次完成资料整理。
- 四份最终报告、调用回执和原始日志的绑定检查通过；`git diff --check`、`git diff main -- chinese-official-writing` 用于检查维护文件和产品边界。
- 已准备 [5道真实材料题及2道少读控制题](writing-cases.md)，**尚未运行真实写稿A/B**。本轮不宣称质量提升、路由更稳或成本下降。
- 下一步可按“预算单独、信息化单独、两页组合、采购/整改局部补强”分别验证，保持同题同模型对照，避免把组合收益和单点收益混为一谈。没有新证据时不为静态规则测试数量继续扩展。
- 本轮仅维护区研究提交；未合 main、未推送、未发布、未改本机安装。
