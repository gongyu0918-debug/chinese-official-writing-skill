# workflow 稀疏句原子扩展复验预注册（2026-08-01）

## 原因

- 产品提交保持 `ee02d9ab1cbe3b29285e4a7a7a2058461a09d41d`，不追加 Prompt。
- WS01 因自然读取 `task-route-cards.md` 且未完成预注册终审链，判 `INVALID`。
- WS02 两臂硬边界通过、读取集合对称，匿名 Baseline 小胜；负点是零增量解释句，但本题材料充分，被删句仅约束稀疏报告，尚无直接因果，也未达到三次共性。
- 本扩展只补两组命中完整报告路由的日常任务，用于区分随机波动与删除句的实际影响。

## 固定条件

- Baseline：`21084f3afd2feb7493a6158bb335b17e2d5d551b`。
- Candidate：`ee02d9ab1cbe3b29285e4a7a7a2058461a09d41d` 及其后的证据提交，产品文件不变。
- `gpt-5.6-terra/high`；同题两臂逐字同输入，各一次首个完整输出，不修订、不补抽。
- 两题都按序读取 `SKILL.md`、`information-selection.md`、`workflow.md`、`genre-checklist-report.md`，完整 D0 后读取 `final-review-layers.md`、`proofreading-checklist.md`；不读取 `task-route-cards.md` 或其他文种叶。任一臂读取集合不对称则该对 `INVALID`。

## 任务

- WS03：多条工作记录合并成 800—1000 字试运行情况报告，直接检验被删句覆盖的“材料较稀疏但进入完整流程”场景。
- WS04：900—1100 字延时服务运行情况报告，材料包含完整数据、问题、已做调整和后续安排，作为同文种控制题。

逐字任务分别固定在：

- `tests/evidence/workflow-sparse-line-atom-v1531-extension-tasks/WS03-task.txt`，SHA-256 `ecaff5beaa89cd75a65a5fc331319ca14b8a28603ed3c92f1c15581a74ab8a85`
- `tests/evidence/workflow-sparse-line-atom-v1531-extension-tasks/WS04-task.txt`，SHA-256 `16edc5b485a53f1445f1c1328c5b2734303f6103bfe931e20f7002aadcb324ef`

## 验收

- 两题均先核验事实、数字、日期、主体、状态、文种、格式、篇幅和输出模式；无 Candidate 独有 P0 或材料外事实。
- 匿名盲审比较结构、直接修改成本、重复解释和机械感，不以字数长短判优。
- WS02 的零增量解释若在 Candidate 中再次出现且 Baseline 没有，才形成第二次同机制线索；只有累计三题复现才登记为共性风险。
- 两题均不劣或一胜一难分，可支持把 WS02 负点判为波动并保留减载候选；再次出现明确 Candidate 独有硬回退则保持隔离，不合并。
