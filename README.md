# ai技能库

**首次公开发布 · AI 开发 · 程序版本 1.3.2**

Windows 桌面 AI 技能管理工具，支持技能安装、切换、导入、备份、检查与撤销。
内置 53 项技能和 50 项扩展技能，适用于 Codex、Claude、DeepSeek Harness、Hermes、ZCode 和 WorkBuddy 国内版、国际版。

![控制台](docs/images/console.png)

## 使用说明

在[发布页面](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.3.2)下载 `AISkillLibrary-1.3.2-windows-x64.zip`，解压后双击 `ai技能库.exe`。
也可以直接下载同名版本的 `.exe` 文件。需要 Windows x64 与 Microsoft Edge WebView2 Runtime，无需安装 Python。

1. 确认客户端卡片上的配置目录。
2. 选择技能方案，开启对应客户端开关。
3. 点击“检查”确认文件完整，再重启客户端或新建会话确认模型读取。
4. 关闭开关可以撤销；程序会保留外部修改并提示冲突。

导入格式、客户端目录和备份操作见[完整使用说明](docs/USAGE.md)。

## 注意事项

- 写入前会自动备份，请先确认所选配置目录。
- 文件检查通过与模型实际读取是两个状态；技能涉及的工具与附件需要在本机核对。
- 第三方组件遵循各自许可证。完整事项见[NOTICE.md](NOTICE.md)。
- [逆向与安全报告](docs/security/REVERSE_ANALYSIS.md)公开程序哈希、源码对照、Defender 检查与运行证据；报告结论限定检查范围，并提供[复现步骤](docs/security/REPRODUCE.md)。
