# WR-027 投诉与情况反映 R1/R2 结果

日期：2026-09-02。

状态：`R2_REAL_WRITING_PASSED / ENGINEERING_VERIFIED / MERGED_MAIN_POST_V1.6.25_FROZEN`。

## 范围与判断基线

本原子只处理本人或本单位作为亲历方提交的投诉、问题反映和情况反映。投诉请求与解决建议分开：材料已经给出`请核实`、`请处理`、`请反馈结果`时保留请求，但不替接收方设计退款、补偿、系统改造、内部流程、责任分工、期限或结果承诺。建议方提出改进主张仍走意见建议专叶；办理方整理已收事项和处理结果仍按报告、说明或指定文种处理。

公开校准只提取不可版权化的方法边界，不复制公开网页表述：

- 国务院《信访工作条例》区分情况反映、意见建议和投诉请求，并要求书面投诉请求载明请求、事实、理由，客观真实地反映情况：<https://www.gjxfj.gov.cn/2022-04/08/c_1310549186.htm>。
- 市场监管总局《市场监督管理投诉举报处理暂行办法》现行页面将投诉界定为请求调解权益争议，并要求有具体投诉请求和事实依据：<https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/fgs/art/2026/art_e4d03a20c0fd49769e408c7bf3791ff5.html>。
- 福建省12345便民服务平台页面分别列出投诉与建议入口，支持产品将亲历问题陈述与合作性改进建议分路：<https://www.fj.gov.cn/hdjl/zxts/wyqz/>。

## 候选与真实写稿

- 固定公开主线基线：`2d50fcd3c2d7449dfa5baf1a8f11e80da9c083c8`。
- R1产品候选：`f63d106206921eec41ec8c3719a0aa3a61919269`。
- R2产品候选：`62b8cf10d6df007880a0a338c8598a7b188868e2`。
- 模型：Alibaba Token Plan 2 / Alibaba Token Plan / Ollama Cloud / OpenCode Go 的 DeepSeek V4 Flash 与 MiniMax M3，均为 `max` 思考强度；使用 Codex Desktop CLI `0.152.1`，只读运行，关闭插件、Apps 和 Memories。

首轮误用`--ignore-user-config`后没有形成 Skill 读取轨迹，25份输出全部作废，不进入质量统计。修复运行方式后的 R1 基线和候选各25份，共50/50技术有效并实际读取隔离运行时`SKILL.md`。三道正向题中候选专叶读取11/15；意见建议与收到投诉内部记录两道控制题0/10误读。15份候选正向稿均未追加平台解决方案，带明确请求题5/5保留核实与反馈请求。

R1 暴露三项候选独有直接问题：一稿漏独立标题并新增材料外后续安排，一稿用`&nbsp;`模拟落款对齐，一稿在正文前输出读取过程。R2只补标题锁定、未决材料不顺势续写、纯正文与纯文本排版三项，不改路由范围；随后五家各重跑三道正向题。

R2原批14/15技术有效；MiniMax一份误读全局同名Skill，作技术无效。官方配置规定`skills.config.path`应指向包含`SKILL.md`的目录，runner据此从文件路径改为目录路径后，仅定向补跑该样本。补跑实际读取隔离`SKILL.md`，没有全局Skill或Hook污染，形成第15份有效正向稿，不重复整批。

最终R2的15/15有效正向稿均保留关键事实、当前状态和材料明示请求，0/15追加退款、补偿、平台改造、责任分工或办理期限；独立情况反映5/5保留标题，纯文本0/15出现HTML空格，0/15新增材料外后续承诺。同题基线有6/15份正文前后包装，R2为1/15；剩余Alibaba Token Plan一稿仅有`正文如下`，其基线同题存在更强的`已使用Skill`说明，因此记模型遵从残余而非候选独有硬回退。

机械摘要仍把同年语境中的`8月9日`误判为缺少`2026年8月9日`，把`仍未`误判为缺少`尚未`，并曾把正文中的`后台核验过程中`误判成过程包装。这些均经逐稿核对为等义日期/状态或正文事实，不作产品失败；材料事实与常识直接支持的一层影响、目的或归纳同样不因未逐字出现而判失败。

## 产品与工程边界

所选产品范围只有：

1. `SKILL.md`增加亲历方投诉/情况反映的正向直达路由，并从通用套语页移除`情况反映`伴读入口；
2. 新增`references/genre-playbook-complaint-reflection.md`；
3. 同步 Agent Skills、Qwen Code、QwenWork、Hermes、OpenClaw 五套普通兼容镜像。

不修改 description、Hook、adapter、通用短稿页、版本号或发布包。六种临时 companion 组装只用于字节一致性测试，不形成新的常驻产品目录。所选候选已合入本地`main`，但没有进入冻结v1.6.25，也没有推送、移动标签或平台发布；精确坐标见`main-merge.md`。

## 证据坐标与命令

- R1基线摘要 SHA-256：`C7F6EC0179902926CB5C8F227DA00923CCD877B42E0828FFBA0E16BD7357BD47`。
- R1候选摘要 SHA-256：`262E4616EA177F8020BA999213C246610BDFD9CDE822D85E1B1FC15E46099A5B`。
- R2原批摘要 SHA-256：`3018EE3B85D1AE19141FA6D8B298941090B2D6E548AF53C3CEE8775FE7D43D09`。
- R2 MiniMax定向补跑结果 SHA-256：`BDF1B52C04FF3B835A356ECEBD529CAD0360999195E47D3A0C0E050C5D58FDE6`。
- 原始输出位于忽略目录`output/complaint-reflection-r1/`，摘要、题面、runner和判定记录可复现对应关系。

实际运行命令：

```powershell
python maintenance/tests/evidence/complaint-reflection-r1/run_probe.py --arm baseline --prepare
python maintenance/tests/evidence/complaint-reflection-r1/run_probe.py --arm baseline --provider <provider>
python maintenance/tests/evidence/complaint-reflection-r1/run_probe.py --arm baseline --summarize
python maintenance/tests/evidence/complaint-reflection-r1/run_probe.py --arm candidate --prepare
python maintenance/tests/evidence/complaint-reflection-r1/run_probe.py --arm candidate --provider <provider>
python maintenance/tests/evidence/complaint-reflection-r1/run_probe.py --arm candidate --summarize
python maintenance/tests/evidence/complaint-reflection-r1/run_candidate.py --prepare
python maintenance/tests/evidence/complaint-reflection-r1/run_candidate.py --provider <provider>
python maintenance/tests/evidence/complaint-reflection-r1/run_candidate.py --summarize
python maintenance/tests/evidence/complaint-reflection-r1/retry_invalid.py --provider minimax --case COMPLAINT-EXPLICIT-REQUEST --output-name candidate-r3-minimax-retry
python maintenance/tools/sync_adapters.py --help
python -m unittest maintenance.tests.test_complaint_reflection_leaf
python -m unittest maintenance.tests.test_advisory_feedback_leaf
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py <skill-root>
python -m unittest discover -s maintenance/tests
git diff --check
```

`sync_adapters.py`没有帮助参数；上列`--help`调用实际执行了一次五套镜像同步，未把它冒充帮助查询。完成后的工程结果为：投诉专叶与相邻建议专叶定向测试12/12通过；canonical、Agent Skills、Qwen Code、QwenWork、Hermes五处`quick_validate.py`均返回`Skill is valid!`；全量`python -m unittest discover -s maintenance/tests`为771/771通过；runner文件编译、镜像复跑和`git diff --check`通过。OpenClaw沿用宿主专用frontmatter，不用通用validator冒充通过，其字节一致性由专叶测试覆盖。

## 剩余风险

- 一家模型在一份稿件中仍输出`正文如下`；基线同题包装更重，故不阻断本原子，但交付洁净度仍是模型遵从风险。
- 新专叶在最终15份正向稿中实际读取10份；其余稿件均读取新增直达路由所在的`SKILL.md`并达到目标，不能把15份全部记作专叶读取。
- 本项没有验证真实外部投诉平台字段限制、在线提交或DOCX版式；只证明正文生成与静态产品集成。
