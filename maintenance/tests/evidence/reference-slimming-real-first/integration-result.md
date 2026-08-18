# Reference 减载集成结果

## 边界

- 固定公开基线：`d0478c365790200dbdaf5b833221628b5c3415d1`。
- 三个独立审计上下文：`gpt-5.6-sol` max、`xai/grok-4.6` max、`alibaba-token-plan-2/qwen3.8-max` max。
- 发现门槛：三家一致可进入低风险首原子；至少两家发现即进入 TEST-FIRST，不因第三家漏看而丢弃；一家发现保留观察并补证。
- 本轮不新增功能，不改 `SKILL.md`、Hook、版本或发行面。

## 集成范围

真实写稿通过并进入公开版：

- `references/genre-playbooks.md`
- `references/genre-playbook-minutes.md`
- `references/genre-playbook-correspondence.md`

三份叶子各把三条重复“使用方式”压成一条短契约，仍保留入口直达、字段单元、信息选择、材料外事实禁入和复杂任务条件补读。canonical 合计减少 552 个字符，四个普通平台镜像同步一致。

未进入公开版：

- 报告叶在聚焦复测中仍出现材料外主体动作，恢复基线。
- 方案叶的基线写稿 final 没有正文，整对按零重试合同无效，恢复基线。
- `official-style.md` 属于两家审计发现的测试项；普通事务稿无变化，但 AI 算力候选出现 Token 计量口径和保证性结论硬伤，恢复基线。

## 真实证据

- R1 六个写稿臂因路由读取与终稿技术泄漏无效，未用于准入。
- R2 六个有效臂完成征求意见函、报告、会议纪要 A/B；会议纪要通过，另两组进入聚焦修正。
- R3 四个有效臂确认征求意见函通过、报告叶撤回。
- R4 当前会议纪要终态六维全 PASS，并由独立 SOL 判胜。
- 普通工作联系函同题 A/B 六维全 PASS、TIE；候选更简洁。
- 研究证据终态：`codex/reference-slimming-real-first@87c847ec30808c50a4432bcfc547131192ef6f7c`。

## 集成验证

- `python -B -m unittest maintenance.tests.test_repository_reachability -q`
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`
- canonical 与 Agent Skills、Qwen Code、Hermes、OpenClaw 的三个目标叶逐文件 Git blob 一致。
- `git diff --check`

公开 `main` 只接收上述普通写作减载；付费提纲候选通过合并最新 `main` 继承，不复制第二套普通 references。
