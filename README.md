# ai技能库

**AI 开发 · 程序版本 1.4.1**

Windows 桌面 AI 技能管理工具，支持技能安装、切换、导入、备份、检查与撤销。
内置 54 项技能和 50 项扩展技能，适用于 Codex、Claude、DeepSeek Harness、Hermes、ZCode 和 WorkBuddy 国内版、国际版。

![控制台](docs/images/console.png)

## 使用说明

在 [1.4.1 发布页面](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.4.1)下载
[Windows 程序](https://github.com/Lin6932271/ai-skill-library/releases/download/v1.4.1/AISkillLibrary-1.4.1-windows-x64.exe)直接运行，
或下载 [ZIP 包](https://github.com/Lin6932271/ai-skill-library/releases/download/v1.4.1/AISkillLibrary-1.4.1-windows-x64.zip)，解压后双击 `ai技能库.exe`。
需要 Windows x64 与 Microsoft Edge WebView2 Runtime，无需安装 Python。

1. 找到正在使用的 AI 客户端，保留默认的完整技能库。
2. 开启对应客户端开关，等待软件自动准备 REA 并完成启动测试。
3. 退出并重新打开 AI 客户端，直接说“使用技能……”并描述任务。
4. 关闭开关可以撤销；程序会保留外部修改并提示冲突。

导入格式、客户端目录和备份操作见[完整使用说明](docs/USAGE.md)。

旧版已经开启技能的用户，运行新版后点击客户端卡片上的“启用 REA”，等待完成并重启 AI 客户端。原有配置会先备份，无需先撤销技能。

REA 6.1.0 和配套 Node 24.19.0 已内置，首次注入无需联网、安装 Node 或手动编辑 MCP。
各客户端启动时自动运行 REA MCP。安装测试成功与客户端实际连接是两个状态；“检查”会明确显示验证范围。
EXE/DLL 的深度反编译仍需要 IDA/Ghidra；其他分析功能也需要对应的运行条件。

## 更新与验证

[1.4.1 更新记录](docs/CHANGELOG.md) · [DeepSeek 修复与恢复](docs/REA_COMPATIBILITY.md) · [REA 配置与验收](docs/REA_INTEGRATION.md) · [源码构建](docs/BUILD.md)

38 项自动测试、七种客户端配置写入与撤销、最终 EXE 界面和真实 CLI/MCP 启动测试已通过。
1.4.0 在 2026-10-09 的实际 Codex 会话中调用 `ai_skill_library_rea`，确认 REA 6.1.0 响应，公布 138 个工具。
1.4.1 已完成本地参数和恢复检查；其余六个客户端完成了配置及独立服务测试，尚未逐一验证真实客户端会话；全部工具与反编译引擎也未逐一验收。

## 注意事项

- 写入前会自动备份，请先确认所选配置目录。
- 文件检查通过与模型实际读取是两个状态；技能涉及的工具与附件需要在本机核对。
- 第三方组件遵循各自许可证。完整事项见[NOTICE.md](NOTICE.md)。
- [1.3.2 历史安全报告](docs/security/REVERSE_ANALYSIS.md)及[复现步骤](docs/security/REPRODUCE.md)予以保留，不能作为 1.4.1 EXE 的扫描结论。
