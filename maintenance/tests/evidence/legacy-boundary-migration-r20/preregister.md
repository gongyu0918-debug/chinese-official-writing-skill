# R20 旧测试责任迁移

基线 HEAD：`95e29838e7f8cf4ef54c7433870eb5d8ab214458`。开始时工作树干净。测试基线副本 SHA-256：`5c36737545e84d0a04ddcca17d2107ec564484904050f0db01195d7851713233`。

只编辑 `maintenance/tests/test_skill_boundary.py` 和本证据目录，不改产品、镜像、版本常量，不 commit，不启动模型或全仓套件。

依据 R17 只读诊断、R18 两个 CLI 方法与两跳 helper 迁移，以及当前真实页面逐项承接责任。保留 81 个方法及其名称，不 skip、不 expectedFailure、不删除测试。优先标题/编号、成语/引语/的地得/量词、多轮底稿、条件专叶。长短卡片终点、首页直链共性细项、旧日期默认省略及固定整句不再作现行契约；分别用统一主文种与共性流程、显式当前链接、确认的草稿日期/指定留空规则和明确行为关系替代。

这不是继续压缩产品。迁移必须说明被保护的功能，不能只检页名或通用词。具体渠道接收方与发文主体、Token 与调用次数的规则保真可以迁到明确主体/单位语义；它们的真实模型表现仍单列未验证，不因缺原例句判能力丢失。确实找不到明确承接的责任应保留为具体缺口，不修改产品凑断言。

R18 两个 CLI 方法保留实际 subprocess：`draft_length` 的 nonspace/cjk、stdin、JSON、篇幅与文后提示隔离，以及 `prose_lint` 的三种模式、stdin、JSON、结构/格式参数。当前 module 只完整执行一次：

```text
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B -m unittest -v maintenance.tests.test_skill_boundary
```

输出写入新日志，不覆盖 R17/R18。逐项记录失败事件与受影响方法数量，不能把 subtest 计数当独立能力数。若发生失败，按实际原因处理，只对修正涉及的方法做必要复验；完整模块不再次运行。

测试通过仅说明可执行的文档/路由/CLI 契约成立，不等于 81 项写稿能力通过。当前两个 reference 测试模块只用于辨认已有覆盖，不额外运行。
