# R6 文种功能按材料选择 A/B 预注册

日期：2026-08-17

候选-only 4篇已满足事实、状态、篇幅、结构和文种硬边界。本轮固定同4题、同2家 provider，按 baseline/candidate 交错顺序执行8次；不再修改候选文本。

- baseline 为 `v1.6.6^{commit}=b49da7f2a5a8ac2327252d29efd66f1d54ccbc35`。
- candidate 仅改 `formulaic-language.md` 的总表说明和表头；其他文件逐字同 baseline。
- Ollama、Alibaba 各2对，DeepSeek V4 Flash 0731 max、1200秒、0 retry、每臂隔离。
- 两臂都必须读取常用语页。匿名复核分别判断事实、状态、篇幅、用户结构、文种、机械化簇和直接使用成本。
- 候选独有事实、状态、用户结构或文种 FAIL 为0，机械化 FAIL 不多于基线，并至少2组减少逐项补齐、同义复述或口号式收束，才考虑接入产品。
