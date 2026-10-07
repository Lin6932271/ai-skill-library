# 注意事项

本软件由 AI 开发。

- 运行环境为 Windows x64，需要 Microsoft Edge WebView2 Runtime；已打包程序无需安装 Python。
- 开启技能前确认客户端配置目录。重要配置建议另行备份，程序会在写入前保存原内容。
- “检查”通过表示技能文件已正确写入；需要在对应客户端重启或新建会话，确认模型实际读取。
- 技能正文提及的工具、脚本和参考附件需按实际环境核对。导入的脚本只作为附件保存，软件不会自动执行。
- 撤销技能时会保留外部修改并报告冲突，请按提示检查有关文件。
- 状态诊断可能包含本机目录，分享诊断文件前请检查其中内容。
- 第三方组件遵循各自的许可证，相关依赖列在 `requirements.txt` 中。
- [逆向与安全报告](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/REVERSE_ANALYSIS.md)提供程序哈希、源码对照和检查证据；结论限定于报告注明的样本与检查范围。

操作步骤见[使用说明](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/USAGE.md)。
