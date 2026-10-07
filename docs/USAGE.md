# 使用说明

ai技能库首次公开发布，程序版本 1.3.2。本软件由 AI 开发。

支持 Codex、Claude、DeepSeek Harness、Hermes、ZCode，以及 WorkBuddy 国内版和国际版。
包含 53 项内置技能、50 项扩展技能，以及基础与进阶方案。

## 运行程序

从[发布页面](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.3.2)下载 `AISkillLibrary-1.3.2-windows-x64.zip`，解压后双击 `ai技能库.exe`。
也可直接下载 `AISkillLibrary-1.3.2-windows-x64.exe` 运行。
需要 Windows x64 和 Microsoft Edge WebView2 Runtime，无需安装 Python 或注册账户。

启动动画约 7 秒，静音播放并铺满软件窗口，播放完毕自动进入主界面。
动画期间隐藏标题栏，结束后恢复窗口按钮。界面支持搜索、分类筛选、滚动及浅色与深色主题。

## 安装与检查

1. 在客户端卡片上确认配置目录，必要时通过“设置”选择实际目录。
2. 在方案下拉框中选择完整技能库、单个技能、扩展技能、基础、进阶或已导入方案。
3. 开启对应客户端开关。程序会先备份原内容，再写入技能和目录入口。
4. 点击“检查”确认文件完整。随后重启对应客户端或新建会话，确认模型读取。
5. 需要更换方案时选择新的方案；关闭开关可以撤销程序管理的内容。

| 客户端 | 默认目录 / 环境变量 | 指令文件 |
| --- | --- | --- |
| Codex | `~/.codex` / `CODEX_HOME` | `AGENTS.md` |
| Claude | `~/.claude` / `CLAUDE_CONFIG_DIR` | `CLAUDE.md` |
| DeepSeek Harness | `~/.dsh` / `DSH_HOME` | `AGENTS.md` |
| Hermes | 优先已有 `~/.hermes`，否则 `%LOCALAPPDATA%/hermes`；支持 `HERMES_HOME` | `HERMES.md` |
| ZCode | `~/.zcode` / `ZCODE_HOME` | `AGENTS.md` |
| WorkBuddy 国内版 | `~/.workbuddy` / `WORKBUDDY_CONFIG_DIR` | `CODEBUDDY.md` |
| WorkBuddy 国际版 | `~/.workbuddy-ai` / `WORKBUDDY_AI_CONFIG_DIR` | `CODEBUDDY.md` |

Hermes 便携版应选择实际 `data/hermes-home` 或当前 profile 目录。
如果客户端使用自定义配置位置，请以客户端实际目录为准。

## 导入自己的技能

在“技能库”中点击“导入技能”，每次导入一项。支持以下格式：

- UTF-8 Markdown 文件。
- 根目录包含 `SKILL.md` 的文件夹，可同时包含 `references/`、`scripts/` 等附件。
- 恰含一个 `SKILL.md` 的 ZIP 文件，可同时包含附件。

导入限制为 32 MB、2000 个文件。单个 Markdown 不会自动收集相邻附件。
源文件修改后需重新导入，并选择对应方案。

程序已内置全部技能，日常使用无需另外下载技能集合 ZIP。
需要手动安装时，把集合中所需的 `skills/<名称>/` 复制到客户端技能目录；同名文件请先备份和比较。
通过软件导入集合时，应先解压，再选择一个具体技能目录。

## 备份与数据

数据目录为 `%LOCALAPPDATA%/PojiaLocal`。
`state.json` 保存安装记录和设置，`backups/` 保存原内容，`imports/` 保存导入资源。
“状态检查”可以查看安装状态并导出诊断。

撤销时只处理程序管理的段落和文件。外部修改会保留并报告冲突；遇到冲突请先检查提示和备份，再决定如何处理。

## 注意事项

文件写入成功与模型实际读取需要分别确认。技能里提及的工具和附件不代表已安装或已通过测试。
完整注意事项见[NOTICE.md](https://github.com/Lin6932271/ai-skill-library/blob/main/NOTICE.md)，[逆向与安全报告](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/REVERSE_ANALYSIS.md)包含已发布程序的检查范围与证据。
