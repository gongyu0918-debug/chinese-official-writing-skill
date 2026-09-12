# v1.6.35 发布记录

## 冻结范围

v1.6.35 是 2026年9月13日的纯维护版本。相较 v1.6.34，写作规则、检查脚本和 Hook 运行时代码不变；本版只统一公开版本元数据、补齐 v1.6.31—v1.6.33 发布证据与索引，并修正相应测试中的当前版本常量。

本轮曾验证讲话人物排序、文种族群分叶和旁白检测候选。讲话排序在 MiniMax 留出中重复破坏具体人物与泛称顺序；四文种与两文种分叶在通知、调研或采购控制中重复出现正文外说明及材料外推断；旁白检测只能证明显式运行脚本时提高发现率，不能证明普通路径稳定降低旁白。上述候选均未进入本版，也不以篇幅、票数或工程门掩盖写稿失败。

## 产品与平台边界

- GitHub 与 SkillHub 的 1.x 包保留 MIT Hook 目录；本版只改 adapter manifest 版本，不改 Hook 行为。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing` 无 Hook 包。
- `outline_assist`、`paid/redhead_docx`、2.0 规则和 Pro 源码均不在公开发布树。
- SkillHub 与 ClawHub 各只允许一次正式提交；取得成功回执后不做传播轮询。

## 发布前验证

候选提交、tag、包指纹、测试结果与平台 dry-run 在发布冻结后补记。

## 发布回执

GitHub、SkillHub 与 ClawHub 的正式回执在实际提交后补记。
