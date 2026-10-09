# 1.4.1：DeepSeek Harness 兼容性与恢复

## 普通用户操作

从 [1.4.1 发布页](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.4.1) 下载新版 EXE，关闭旧技能库后运行新版。

1. 找到 DeepSeek Harness 卡片，确认配置目录与实际使用的目录一致。
2. 已开启技能时点击“更新 REA”；显示遗留连接时点击“修复并开启技能”；首次安装则开启开关。
3. 等待完成，完全退出并重新打开 DeepSeek Harness，新建会话发送 `hi`。

不用填写 MCP 参数。程序会先保存备份。不要直接删除整份 `cordis.patch.yml`，它可能还包含其他插件设置。
如果程序无法确认遗留连接来自本软件，或者发现外部修改，会保留文件并提示导出诊断。

## 两种已报告现象

`Invalid schema for function ... analyze_javascript_application ... is not a 'regex'` 出现在模型请求校验阶段。
REA 能启动和列出工具，并不保证远端模型接口接受这些工具的全部参数定义。
1.4.1 调整随包 REA 的正则表示，保留空字符、规范路径和保留环境变量的运行时校验。

`同名 REA 配置已存在，未覆盖` 表示配置中已有条目，而技能库当前没有对应安装记录。
它不能单独证明 DeepSeek Harness 无法启动的原因。新版提供经过来源校验、备份和冲突保护的恢复入口。

## 修复内容与来源

基础版本仍为 REA 6.1.0，加入本软件的 `portable-regex-v1` 补丁。
修改六个参数定义文件，使用 `\x00` 表示空字符，并把不适合通用 Schema 的先行断言改为服务端约束。
运行时包、文件索引及关键文件校验值同步更新；原始包哈希、补丁文件和前后哈希记录在 `runtime/manifest.json`。
重建补丁的脚本为 `tools/patch_rea_schema.py`。

恢复功能只识别本软件数据目录内、已发布运行包中的原始启动文件和完整注册结构。
没有指令残留时只替换已确认的托管连接；有完整技能残留时，验证管理段和技能内容后恢复安装记录。
失败时保留用户配置，恢复前的快照位于数据目录 `backups/recovery-*`。

## 验证边界

已完成 38 项自动测试、七种客户端配置与真实 MCP 启动测试、JavaScript 样例分析。
服务公布 138 个工具，安装检查遍历 347 个参数正则。恢复测试包含其他 DeepSeek 插件保留及修改冲突保护。
最终 EXE 的界面验收结果随 Release 的证据包提供。

这不代表已在对方机器上完成 DeepSeek 官方 API 的真实聊天，也不能证明“关闭后打不开”的唯一原因。
用户需在新版完成更新或恢复后重启客户端，确认 `hi` 和实际任务；继续失败时分享脱敏诊断及新报错。

[DeepSeek 官方工具调用说明](https://api-docs.deepseek.com/guides/tool_calls/) · [Harness 官方 MCP 配置说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.md)
