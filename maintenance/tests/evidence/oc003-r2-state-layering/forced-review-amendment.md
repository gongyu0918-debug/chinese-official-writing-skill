# OC-003-R2 反向审稿显式激活修正

日期：2026-08-25。

首轮12次调用中，三条正向起草 A/B 均读取隔离 Skill；反向只审题只有 Alibaba 两臂有效。Luna 两臂实际读取了用户级同名 Skill，Ollama 两臂没有留下任何隔离 Skill 读取轨迹。四个无效臂保留原样，不重记为质量通过或失败。

为判断产品 reference 而不是自动触发，本修正复用同一材料、现稿、输出模式和裁判，只在题首明确要求读取当前工作区 `.agents/skills/chinese-official-writing/SKILL.md` 及其实际路由 reference，并禁止读取用户级同名 Skill。三家 provider 重新各跑 Baseline/Candidate 一次，共6次；这是显式激活控制，不替换首轮自动路由证据。

只有精确隔离 Skill 读取、无用户级污染的臂进入质量比较。Candidate 三路仍须识别五类状态/效果错误，只恢复原状态或删除，不新增另一套程序。任一 Candidate 有效稿把“原因尚无结论”保留为“正在核查”，或新增核查、比价、审批、选型、上线、验收安排，即为硬回退。
