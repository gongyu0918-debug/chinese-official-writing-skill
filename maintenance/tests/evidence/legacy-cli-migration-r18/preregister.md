# 旧 CLI 与显式两跳路由责任迁移（R18）

基线 HEAD：`8f9d08898cd1f52b6f16f32691739af5a7e4067d`。仅修改 `maintenance/tests/test_skill_boundary.py` 的 `read_routing_surfaces`、`test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority`、`test_review_command_includes_interpreter_and_draft_path`；其他方法、版本常量、产品和镜像不动，不 commit。

原测试模块 SHA-256：`f8095b65819f9d14383ce30670e49229e097fb3d60ebd6513d5a4eb2b207df9f`。原文件使用 CRLF；修改时按三个定义的原始字节范围替换，保持其他字节不变。

helper 必须验证首页显式链接 reference-index，索引显式链接 compatibility-scene-routing，再读取这个固定目标。允许当前实际两跳，不搜索任意页面补足失链。正例、首页缺入口、索引缺第二跳、目标缺文件、索引缺文件分别验证；首页有兼容页直链或其他页有链接也不能代替索引第二跳。

长度测试迁到 writing-rules/compression-details 的当前 owner，保留有据分析、上限无需填满及低于下限不得报达标；重点保留两个真实 stdin CLI：nonspace 为 8、cjk 为 2，文后提示不计入，状态 within，scope 为 draft-before-postscript。

文稿扫描测试迁到共性页及当前 prose-lint-usage 的带引号脚本/草稿路径与模式用法；真实执行 draft-body、gap-note-allowed、review-only，解析 JSON。正文模式发现独立提示、允许提示模式不将其误报为正文外残留，审核意见本身按 review-only 处理。文档断言置于独立 subTest，失败仍记录，并继续真实命令验证；不 skip、不恢复旧页。

使用显式 `C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe`，不使用 PATH 的 Hermes Python，不安装依赖。先运行两个修改方法及 helper 的两个现有调用方法，并记录实际子进程命令、stdout/stderr 和退出码；同时只做上述 helper 小验证。现有调用方法后续仍可能卡在范围外旧句，保留失败。最后完整 81 方法模块只跑一次，另存 R18 日志；不覆盖 R17 的 53 方法、78 failure、35 error 日志。

结果只说明本次三处迁移及剩余失败量；不把 helper 图修复或 CLI 成功外推为整体写稿质量通过。R18 共性页原型尚未进入 canonical，本次测试当前产品内容。
