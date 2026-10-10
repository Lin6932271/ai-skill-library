# 1.4.2：DeepSeek Harness 正则兼容性与恢复

## 普通用户操作

完全关闭 DeepSeek Harness 和旧技能库，从 [1.4.2 发布页面](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.4.2)下载并运行新版。1.4.0、1.4.1 因正则兼容问题已撤下。

1. 找到 DeepSeek Harness 卡片，确认配置目录与实际使用的目录一致。
2. 已开启技能时点击“更新 REA”；显示遗留连接时点击“修复并开启技能”；首次安装则开启开关。
3. 等待完成，完全退出并重新打开 DeepSeek Harness，新建会话发送 `hi`。

不用填写 MCP 参数。程序会先保存备份。不要直接删除整份 `cordis.patch.yml`，它可能还包含其他插件设置。
如果程序无法确认遗留连接来自本软件，或者发现外部修改，会保留文件并提示导出诊断。

## 两种已报告现象

`Invalid schema for function ... analyze_javascript_application ... is not a 'regex'` 出现在模型请求校验阶段。
REA 能启动和列出工具，并不保证远端模型接口接受这些工具的全部参数定义。
1.4.1 调整随包 REA 的正则表示，保留空字符、规范路径和保留环境变量的运行时校验。

随后报告的 `observe_native_calls ... "^[^\\s[\\]]+$" is not a "regex"` 表明 1.4.1 仍有遗漏。
该表达式在 Python 和 JavaScript 中可编译，但 Rust regex 将其中未转义的 `[` 视为嵌套字符集合并报告未闭合。
本地已复现该差异；这能解释兼容风险，不代表已确认 DeepSeek 服务内部具体使用哪一种正则引擎。
1.4.2 改为 `^[^\\s\\x5b\\x5d]+$`。工具名称、参数结构和服务端校验不变，仍然拒绝空白及方括号。

`同名 REA 配置已存在，未覆盖` 表示配置中已有条目，而技能库当前没有对应安装记录。
它不能单独证明 DeepSeek Harness 无法启动的原因。新版提供经过来源校验、备份和冲突保护的恢复入口。

## 修复内容与来源

基础版本仍为 REA 6.1.0，加入本软件的 `portable-regex-v2` 补丁。
在原有六个文件的补丁中保留 `\x00` 空字符表示和服务端约束，另补充裸类型名称的方括号兼容写法。
运行时包、文件索引及关键文件校验值同步更新；原始包哈希、补丁文件和前后哈希记录在 `runtime/manifest.json`。
重建补丁的脚本为 `tools/patch_rea_schema.py`。

恢复功能只识别本软件数据目录内、已发布运行包中的原始启动文件和完整注册结构。
没有指令残留时只替换已确认的托管连接；有完整技能残留时，验证管理段和技能内容后恢复安装记录。
失败时保留用户配置，恢复前的快照位于数据目录 `backups/recovery-*`。

## 验证边界

40 项自动测试通过。服务公布 138 个工具，检查遍历 347 个参数正则，并补充 Rust regex 校验以及 10000 个输入的改写前后语义比较。
七种客户端配置、实际 MCP 启动、JavaScript 样例分析及最终 EXE 的验收结果见随包证据。
恢复测试包含其他 DeepSeek 插件保留及修改冲突保护；额外覆盖 1.4.1 的托管运行包识别。
最终 EXE 的界面验收结果随 Release 的证据包提供。

2026-10-10 已收到测试用户在 DeepSeek Harness 官方直连场景的修复成功反馈。感谢 QQ 2608422753 这位好友提供测试。
这是用户反馈，发布证据中的 `deepseek_official_api_chat_verified: false` 仍表示自动验收没有代替用户向官方接口发起真实聊天。该反馈不能证明所有客户端、全部工具均已验收，也不能据此确定“关闭后打不开”的唯一原因。
其他用户仍需在新版完成更新或恢复后重启客户端，确认 `hi` 和实际任务；继续失败时分享脱敏诊断及新报错。

[DeepSeek 官方工具调用说明](https://api-docs.deepseek.com/guides/tool_calls/) · [Harness 官方 MCP 配置说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.md)
