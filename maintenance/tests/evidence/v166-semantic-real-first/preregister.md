# WR-003/004/005 真实写稿优先测试预注册

## 目的

本轮不先修改 canonical Skill、references、Hook 或工程胶水。使用 v1.6.5 产品树、未合并的 `formulaic-language.md` 研究候选和三条简短语义要求组成强制路由原型，直接观察真实成稿。

## 固定输入

- 产品提交：`81061bd78c0dbf5604fb2927ba275169fc93f5ed`。
- 产品 tree：`785b405584c6365f0f7ae07b3e8eef96fad9e7ad`，与当前工作树一致。
- `formulaic-language.md` SHA-256：`95e136ab2f044ad214a43d465aaaa399530f17546a6f55c50d1c8d049b6f9cc8`；该文件只作 system prompt 强制读取原型，不冒充已发布产品文件。
- 题面与 provider 分配见 `cases.json`；system prompt 见 `prototype-system-prompt.txt`。

## 模型与执行

- OpenCode Go：`opencode-go/deepseek-v4-flash`，max，S01—S02。
- Ollama Cloud：`ollama-cloud/deepseek-v4-flash:0731`，max，S03—S04。
- Alibaba Token Plan 2：`alibaba-token-plan-2/deepseek-v4-flash-0731`，max，S05—S06。
- 三 provider 可并行；每个 provider 内严格串行。每题独立 HOME、配置和临时目录，1200秒上限，0 retry，只取首个非空终稿。
- 普通 Skill 路径，不安装或启用 Hook。用户输入只含冻结题面，路由指令只放 system prompt。

## 功能判定

每稿分别检查：

1. 文种功能、结构、行文关系和开端/承启/结尾语是否正确；
2. 新增动作、承诺、预期是否有材料明示或可继承的责任主体；
3. 是否新增具体主体、程序、期限、数字、结论、结果或成效；
4. 是否出现无头结论、机械重复主语、连续自证、同义复述、过程旁白或正文外包装；
5. 是否满足用户给定篇幅和输出范围，能否直接使用。

本轮不要求候选对旧版本总体胜出。共同问题至少出现在3份真实稿、覆盖2个 provider，才形成产品语义原子；单例只记录观察。真实稿未通过时先修语义，不扩张胶水和工程测试。
