# 使用说明

ai技能库程序版本 1.4.1。本软件由 AI 开发。

支持 Codex、Claude、DeepSeek Harness、Hermes、ZCode，以及 WorkBuddy 国内版和国际版。
包含 54 项内置技能、50 项扩展技能，以及基础与进阶方案。

## 运行程序

在 [1.4.1 发布页面](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.4.1)下载 `AISkillLibrary-1.4.1-windows-x64.exe`，双击即可运行。
也可下载 `AISkillLibrary-1.4.1-windows-x64.zip`，解压后双击 `ai技能库.exe`。本地交付文件名为 `ai技能库-1.4.1.exe`，与公开 EXE 内容相同。
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

## REA 自动配置

开启任意技能方案时，软件会自动安装配套 REA 技能，把内置 Node 与 REA 释放到数据目录，
然后测试 CLI 和 MCP 能否启动，最后保存客户端连接配置。无需联网下载或手动填写配置。
等待卡片显示“REA 已就绪”，退出并重新打开 AI 客户端即可加载连接。
直接告诉 AI“使用技能分析这个软件”并提供路径，AI 会自行选择技能。

从旧版升级、技能开关已经开启的用户，点击卡片上的“启用 REA”即可补齐环境和连接，无需先撤销技能。

REA 的后台进程由 AI 客户端在读取 MCP 配置时启动；本软件的启动测试会在结束后关闭测试进程。
因此不需要保持技能库窗口打开，REA 路径也不依赖 EXE 的临时解压目录。
关闭技能开关会撤销该客户端的技能和本软件注册的 REA 连接，保留共享运行环境供其他客户端使用。

| 客户端 | REA 连接文件 |
| --- | --- |
| Codex | 所选目录下 `config.toml` |
| Claude | 默认 `~/.claude.json`；自定义目录下 `.claude.json` |
| DeepSeek Harness | 所选目录下 `cordis.patch.yml` |
| Hermes | 当前目录或 profile 下 `config.yaml` |
| ZCode CLI | 所选目录下 `cli/config.json` |
| WorkBuddy | 所选目录下 `mcp.json` |

连接配置只管理 `ai_skill_library_rea` 条目，保留其他服务器、模型、认证和插件设置。
格式异常或该条目被用户修改时，程序会保留原内容并提示问题。
七个客户端的配置格式和撤销逻辑经过隔离测试；2026-10-09 已在实际 Codex 会话中确认 REA 工具响应。其他客户端版本的实际工具加载仍需在各自的新会话确认。

内置 REA 不等于内置所有反编译器：EXE/DLL 深度反编译需 IDA/Ghidra，Android 和固件等分析也有工具和平台要求。

## 1.4.1 的更新与恢复

已安装 REA 的用户点击卡片上的“更新 REA”。显示遗留连接时点击“修复并开启技能”，程序先备份，再恢复经过来源校验的托管连接。完成后完全退出并重新打开 AI 客户端。

DeepSeek 的正则报错和安装记录缺失的处理见 [修复说明](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/REA_COMPATIBILITY.md)。

## 遇到问题

| 现象 | 操作 |
| --- | --- |
| 首次准备较慢 | 等待界面完成释放、校验和启动测试，首次可能需要数分钟。 |
| 已开启技能，但没有 REA | 点击该客户端卡片的“启用 REA”，等待完成后退出并重新打开 AI 客户端。 |
| AI 提示没有 REA 工具 | 在技能库点击“检查”，确认客户端配置目录正确，再完全退出并重启客户端。无需重复安装 npm 包。 |
| 工具可用，但提示缺少 Ghidra、IDA 或其他引擎 | 这属于分析引擎依赖；让 AI 根据提示检查本机工具，不能用重复注入解决。 |
| 配置冲突或格式异常 | 按提示查看诊断和备份，保留自己的修改；不要直接清空配置文件。 |

详细验证范围见 [REA 集成与验收](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/REA_INTEGRATION.md)。

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
完整注意事项见[NOTICE.md](https://github.com/Lin6932271/ai-skill-library/blob/main/NOTICE.md)。[历史安全报告](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/REVERSE_ANALYSIS.md)针对 1.3.2，不能作为新版 EXE 的扫描结论。
