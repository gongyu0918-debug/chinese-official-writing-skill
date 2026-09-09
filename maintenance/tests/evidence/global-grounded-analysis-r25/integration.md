# R25 合并记录

2026-09-08，用户明确授权通过真实写稿验证后合并。全量检查完成后，已将 `codex/global-grounded-analysis-r25` 快进合入本地 `main`：`176da7422b4ec2ffea82145c35498b09eddfea69` → 产品提交 `a440f97e8787a1143835c2c04342a3d28e00068f`。合并后工作树干净。没有推送、移动tag或发布；本记录及规格状态属于后续文档登记，不改变产品字节。

产品变动仍为入口与信息选择页两处及五套兼容镜像。canonical 净增1354字节，没有新增参考页，不能称为减载。全局有据分析是写作口径澄清：允许据事实与常识论证原因、影响、后果和结论，未放开无依据的具体业务事实和已定安排。

## 真实稿中的具体问题

- [采购候选](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/global-grounded-analysis-r25/actual-minimax/runs/equipment-request/minimax/candidate/document-1.txt)把未定分工写成新机批量扫描、旧机零散扫描。
- [复杂申请候选](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/global-grounded-analysis-r25/actual-minimax/runs/project-application/minimax/candidate/document-1.txt)把复用迹象写成复用情形，补入按月报进度、里程碑与验收等材料外办理义务。
- [复杂申请基线](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/global-grounded-analysis-r25/actual-minimax/runs/project-application/minimax/baseline/document-1.txt)也有从下载与获奖推成付费意愿已验证、补入固定管理程序等问题。这类风险在本批便宜模型的新旧稿中均见，不能归因为本次全局原则导致。
- [Qwen候选附件](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/global-grounded-analysis-r25/actual-qwen/runs/project-application/qwen/candidate/document-2.txt)概述句把scripts/hooks职责顺序写反，后文各节说明正确。目前属于单例的对应关系笔误，尚无跨模型共性证据。

前三类可归纳为：扩展论证时跨入未明确的具体事实、安排或义务。有依据的必要性、影响和条件分析仍可保留；这些具体错误不要求把写作压回只复述材料。

正常的文后补充建议属于产品交付设计。本轮仅[采购题](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/global-grounded-analysis-r25/prompts/equipment-request.txt)和[报告题](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/global-grounded-analysis-r25/prompts/service-report.txt)明确“我只想要正文”，所以其中的自检前言按未遵守该要求记录；原始复杂申请没有此限制，其正文外说明不据此判错。超时只单列为执行/交付情况，不据此推定正文质量下降，也不作为合并否决理由。

## 合并检查

`python -B -X utf8 -m unittest discover -s maintenance/tests -p test_*.py`：817/817通过，134.365秒；全量只运行一次。上轮94项定向检查、五处quick_validate及真实稿证据沿用，不增加写稿模型调用。

`python -B -X utf8 maintenance/tools/build_skillhub_package.py --output output/global-grounded-analysis-r25/merge-skillhub --version 1.6.29`：本地核对包88文件，禁入路径检查通过。仅用于合并检查，不是新发布版本。上一tag v1.6.29为main基线祖先，基线为候选祖先；精确产品diff只有两处，Hook与版本不变。清单fingerprint和方法见 [机器记录](merge-check.json)。

`git diff 176da742..a440f97e --check`、main清洁检查和 `git merge --ff-only codex/global-grounded-analysis-r25` 均通过。只合入本次公开增量，另一任务的付费分支未改；长程改稿及Hook对有据分析的实际表现仍按既有任务继续，不在本次合并中宣称解决。
