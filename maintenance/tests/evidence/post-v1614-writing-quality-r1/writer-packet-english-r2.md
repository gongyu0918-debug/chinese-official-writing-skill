# WR-019c 英文术语写稿包

只执行写稿，不评判规则，不联网，不修改文件。每题只输出可直接使用的中文正式正文。

## E1 标准英文术语首次出现

将以下英文技术材料整理为中文算力服务技术要求：采购对象包括 Graphics Processing Unit（GPU）computing service、Application Programming Interface（API）calls 和 Service Level Agreement（SLA）保障；Power Usage Effectiveness（PUE）由服务商按机房现有统计方法提供；调用量单位为Token；模型名DeepSeek-R1保持产品官方写法。API并发数、SLA具体数值、PUE目标值和Token总量尚未确定。必要标准术语首次出现时应让中文受众能够理解，不得自造阈值、性能成效或采购决定。

## E2 内部代号和产品名

起草一段接口变更说明：本次涉及内部接口代号ZQX-7，材料没有给出ZQX的英文展开或中文名称；调用方式仍为API；测试模型为DeepSeek-R1；已完成两轮测试，3个字段对应关系待确认；是否上线尚未决定。不得展开或翻译ZQX，不得改变ZQX-7和DeepSeek-R1大小写，不得把待确认或未决写成已完成、已上线。

## E3 英文口号和必要缩写并存

将下段改为正式、自然的项目说明，只输出改后正文：项目面向internal users，计划以end-to-end方式建立one-stop AI service，形成quick win并沉淀best practice。已给事实只有：项目拟把模型调用申请、额度审核、API密钥发放三个环节纳入同一线上页面；是否上线尚未决定。不得补用户范围、上线日期、效果、推广决定或其他流程；必要的AI、API可保留。

## 输出形态

依次输出 `【E1】`、`【E2】`、`【E3】`，末行写技术回执；缺一题则只报 `TECHNICAL_INVALID` 和缺失题号。
