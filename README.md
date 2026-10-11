# ai技能库

**AI 开发 · 程序版本 1.5.2**

Windows 桌面 AI 技能管理工具，支持技能安装、切换、导入、备份、检查与撤销。
默认推荐技能库包含 117 项技能，AI 按任务自动选择相关模块。兼容技能库、扩展技能库和自定义方案可在高级选项中使用。适用于 Codex、Claude、DeepSeek Harness、Hermes、ZCode 和 WorkBuddy 国内版、国际版。

![控制台](docs/images/console.png)

## 使用说明

从 [1.5.2 发布页面](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.5.2)下载 Windows EXE，直接运行；便携 ZIP 解压后双击 `ai技能库.exe`。
1.4.2 等历史发行版继续保留。
需要 Windows x64 与 Microsoft Edge WebView2 Runtime，无需安装 Python。

1. 找到正在使用的 AI 客户端，直接开启技能；推荐技能库已默认选择。旧版已开启的用户点击“更新到推荐技能库”。
2. 开启对应客户端开关，等待软件自动准备 REA 并完成启动测试。
3. 退出并重新打开 AI 客户端，直接说“使用技能……”并描述任务。
4. 关闭开关可以撤销；程序会保留外部修改并提示冲突。

导入格式、客户端目录和备份操作见[完整使用说明](docs/USAGE.md)。

旧版已经开启技能的用户，运行新版后点击客户端卡片上的“更新 REA”；显示“启用 REA”时点击该按钮，显示遗留连接时点击“修复并开启技能”。等待完成后完全退出并重新打开 AI 客户端，再新建会话。原有配置会先备份，无需先撤销技能。

REA 6.1.0 和配套 Node 24.19.0 已内置，首次注入无需联网、安装 Node 或手动编辑 MCP。
各客户端启动时自动运行 REA MCP。安装测试成功与客户端实际连接是两个状态；“检查”会明确显示验证范围。
EXE/DLL 的深度反编译仍需要 IDA/Ghidra；其他分析功能也需要对应的运行条件。

## 更新与验证

[1.5.2 更新记录](docs/CHANGELOG.md) · [1.5.2 升级说明](docs/UPGRADE_1_5_2.md) · [升级与验收报告](docs/2026-10-11_release-ai-skill-library-1.5.2-report.md) · [升级与验收报告](docs/2026-10-11_release-ai-skill-library-1.5.2-report.md) · [升级与验收报告](docs/2026-10-11_release-ai-skill-library-1.5.2-report.md) · [DeepSeek 修复与恢复](docs/REA_COMPATIBILITY.md) · [REA 配置与验收](docs/REA_INTEGRATION.md) · [源码构建](docs/BUILD.md)

推荐技能库包含 117 项技能，合并完整技能与增强模块，用户无需判断该选哪套。使用本地路径读取，优化目标路由、失败恢复和证据状态。技能说明与相关工具安装分别核对。

1.5.2 的 50 项自动测试、最终 EXE 资源核对、本地接口、原生窗口和隔离配置升级与撤销验收已通过。真实 AI 会话读取仍需在使用环境中确认。
1.4.0 在 2026-10-09 的实际 Codex 会话中调用 `ai_skill_library_rea`，确认 REA 6.1.0 响应，公布 138 个工具。
1.4.2 补充 Rust 正则引擎兼容检查，对 347 个参数正则执行四种引擎的检查。2026-10-10 已收到 DeepSeek Harness 官方直连场景的修复成功反馈；该用户反馈与本地自动验收分别记录，不能代表所有客户端、工具及反编译引擎均已逐一验收。

## 致谢

感谢 QQ 2608422753 这位好友参与测试，帮助发现并验证修复 DeepSeek Harness 的 REA 兼容问题。

## 注意事项

- 写入前会自动备份，请先确认所选配置目录。
- 文件检查通过与模型实际读取是两个状态；技能涉及的工具与附件需要在本机核对。
- 第三方组件遵循各自许可证。完整事项见[NOTICE.md](NOTICE.md)。
- [1.3.2 历史安全报告](docs/security/REVERSE_ANALYSIS.md)及[复现步骤](docs/security/REPRODUCE.md)予以保留，不能作为 1.5.2 EXE 的扫描结论。
