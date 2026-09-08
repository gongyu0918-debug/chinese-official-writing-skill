# HK-002b 本地集成

2026-09-09按用户本轮授权，已将本地main从 `f69534f05a2ae8c2da4f39d35a35497a90d0efff` 快进到产品提交 `893d481070c962c046612d1dcbfae260bfcdc8e8`。集成分支为 `codex/hk002b-main-integration-20260909`，来源候选为 `4fd63ce3`。用户要求的架构修改授权限制也已随 `7464880e` 进入main。没有推送或平台发布。

产品只新增来源关系定位模块，并在现有review_gate、gate_stop_hook接入两类局部纠错及绑定核验；companion组装器补充模块依赖。canonical从89变为90文件。SKILL、README、references、静态adapter行为及五套普通包均与集成前main相同；没有删页、改核心路由或改主要工作流。

## 已有收益与本轮补证

[五路同稿结果](../hk002b-source-state-r1/result.md)保留42次CLI调用、8份合法核验并实际交付的D1、2份格式失败后保留D0及真实坏候选拒收。窄范围为明确进行误写成未开展、无据日期前置条件；不把全文事实复核标为完成。

[原生Stop结果](../hk002b-native-stop-r1/result.md)使用冻结4fd63ce3完整64文件companion，在两个独立Codex 0.151.0安装环境验证 `ollama-cloud/glm-5.3-flash` / max。错误样本的D0由受控输入提供，原生续行将“尚未开展”修为“正在核对”，保留18/10/8、日期未定及有据分析；正常样本保持原文，未进入repair/verdict。两份最终正文SHA均匹配实际选稿，终态脱敏成功。这里只补明确进行态的原生路径，没有新增首稿质量或全宿主结论。

原生续行的修订与核验同属一次会话，不称跨provider独立核验。调用级Hook信任开关不等于永久信任。正常样本前段有读工具空输出和进度说明，随后完成真实读页；WebSocket 426和调用级信任警告保留。前轮独立路线核验结果与本轮宿主链路证据分别判断。

## 工程检查与失败处理

- `py -3.13 -B -X utf8 -m unittest discover -s maintenance/tests -p test_*.py`：最终845/845通过，见[完整命令与结果](full-tests-final.json)。
- 首次全量845项中有5处函数复杂度/长度断言失败，见[初始日志](full-tests.log)。仅对review_gate中的5个函数作局部提取；路由、协议、字段、阈值及写稿规则保持。没有放宽复杂度检查。
- [等价复核](complexity-extraction-equivalence.json)：30份历史报告逐字段相等，20个实际事务的候选、绑定、核验与选稿结果相等。复杂度3项及根环境[source相关28项](source-tests-after-extraction.log)通过；子环境临时目录权限失败单列，未当作产品失败。以上与全量重叠，不相加。
- 4fd63ce3与893d4810只存在上述保行为提取，原生包固定前者；不因提取重跑42次模型批次，也不把离线等价说成新的在线调用。

1.6.31另从已发布1.6.30切出R25两处有据分析规则，冻结于 `codex/release-v1.6.31-candidate@9e5b246a`，817项全量、五处Skill校验通过。用户已明确今夜不发布、早上接续；本次Hook不进入该候选，未设置自动发布。

main推进后的本机Pro同步已完成，[实际安装核对](local-install.json)记录 `INSTALLED`、MIT来源893d4810及入口原字节匹配。Hook当前读回为enabled/trusted，工具旧activation_state仍为AWAITING_HOST_TRUST，两字段原样分列；本轮没有另外运行Pro写稿模型，不把MIT隔离Stop结果冒充Pro在线验证。旧安装保留在扫描目录外的回退位置。
