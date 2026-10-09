# 1.4.0：REA 集成与验收

本次在 1.3.2 的本地技能管理器基础上加入 REA，原版本 EXE 保留在交付目录。

## 用户如何使用

1. 双击 `ai技能库-1.4.0.exe`，找到自己的 AI 客户端。
2. 保留默认的完整技能库，点击“开启技能”，等待准备完成。首次可能需要数分钟。
3. 退出并重新打开 AI 客户端，直接说“使用技能分析这个软件”，提供文件位置和目标。

旧版已经开启技能的用户，直接点击卡片上的“启用 REA”。无需先撤销，无需知道技能名称或编辑 MCP。

## 本次加入的功能

- 54 项内置技能：原有 53 项加 `reverse-engineer-anything`，同时保留 50 项扩展技能。
- REA 技能和配套参考文件随所有注入方案一起安装，包括基础、进阶、单个技能和自定义导入方案。
- 运行包内置 REA 6.1.0、Node 24.19.0、npm 及相关依赖，首次准备不需要从网络下载。
- 点击开启时自动解压、校验、测试 CLI/MCP，再写入对应客户端的连接文件。界面显示释放、校验和启动测试进度。
- 注入指令要求 AI 按任务自动选择技能，不要求用户提供具体技能名称。
- REA 安装在长期保留的数据目录中，不依赖 EXE 的临时解压路径，不需要一直打开技能库。
- 客户端在启动或重新加载配置时运行 REA MCP；安装阶段启动的测试进程会正常关闭。

默认持久目录为 `%LOCALAPPDATA%/PojiaLocal/rea/`。不修改系统 PATH，不安装系统服务，不需要管理员权限。

## 配置与恢复

注册名为 `ai_skill_library_rea`，保留已有的其他 MCP、模型、认证和插件设置。

| 客户端 | 连接文件 | 配置结构 |
| --- | --- | --- |
| Codex | 所选目录 `config.toml` | `mcp_servers` |
| Claude | 默认 `~/.claude.json`，自定义目录下 `.claude.json` | `mcpServers` |
| DeepSeek Harness | 所选目录 `cordis.patch.yml` | 插入 `@deepseek-ai/dsh-mcp-client` |
| Hermes | 当前目录或 profile 的 `config.yaml` | `mcp_servers` |
| ZCode CLI | 所选目录 `cli/config.json` | `mcp.servers` |
| WorkBuddy 国内版 | 所选目录 `mcp.json` | `mcpServers` |
| WorkBuddy 国际版 | 所选目录 `mcp.json` | `mcpServers` |

写入前保存快照。启动测试失败不提交客户端修改，写入失败回滚。
准备期间用户或客户端修改了相关文件时，停止提交并保留修改。
配置格式异常、同名非托管条目、托管条目被修改时不覆盖。
撤销时恢复原配置；安装后新增的其他设置予以保留，共享运行环境保留给其他客户端使用。
ZCode 用户明确关闭 MCP 时尊重其设置并给出提示。

## 已验证

- 33 项自动测试通过：技能部署、老记录迁移、备份与回滚、同名文件保护、格式保留、七种配置的撤销、准备期间外部编辑保护等。
- 独立隔离测试实际释放内置包，在中文和空格路径下完成七种客户端配置写入与撤销。
- 七次真实 REA CLI/MCP 启动测试均通过，版本为 6.1.0，服务公布 138 个工具。
- MCP 实际调用 JavaScript 分析工具，识别测试应用中的模块。
- 安装测试禁用了 Python 网络访问；没有调用在线下载器。浏览器验收拦截非本机请求，没有页面外部请求或 JavaScript 错误。
- 最终 EXE 在 Edge 自动验收中完成开启、旧用户升级按钮、检查、方案切换、撤销、导入和搜索。
- 关闭 EXE 后，已释放的运行环境仍能启动 MCP 并分析样例。
- 实际 WebView2 桌面窗口启动、动画、窗口恢复、滚动和七个客户端卡片验收通过。

上述配置与分析测试使用隔离 home/data，不改动开发者真实客户端配置。
详细证据随 `AISkillLibrary-1.4.0-evidence.zip` 交付。隔离测试结果中的 `actual_agent_client_loaded` 为 `false`，表示该次测试没有启动真实 AI 客户端。

## 安装后的实际 Codex 连接

2026-10-09，在用户安装新版后的实际 Codex 会话中，成功调用 `ai_skill_library_rea` 的 `binary_session`。
服务报告 REA 6.1.0、138 个 MCP 工具，技能与运行程序版本对齐，运行路径位于持久数据目录。
该结果证明这个 Codex 会话已连接；不代表其他六种客户端或全部工具都已实际验证。
不含用户目录与账户信息的摘要见 [codex-session.json](releases/v1.4.0/codex-session.json)。

## 验证边界

本轮没有逐一运行其余六个真实 AI 客户端、登录账户并让其模型调用工具。
配置文件通过验证、独立 MCP 服务能启动，不等于当前聊天已连接，仍需退出并重新打开客户端。
客户端版本、自定义配置路径或管理员禁用策略可能影响加载，界面提供检查和配置目录选择。

内置 REA 不等于所有分析引擎均已安装。EXE/DLL 深度反编译依赖 IDA/Ghidra，Android、固件和动态调试等也有各自平台与工具条件。
本轮实际样例分析限定 JavaScript，不声称完成所有 138 个工具或全部目标格式的业务验收。

## 版本与来源

REA 技能取自 npm `rea-agents@6.1.0` 同版本随包技能，与运行程序配套。
REA 和 Node 的许可证及依赖许可证保留在运行包内，源码包也包含完整运行包和清单。

- [REA 项目与安装文档](https://github.com/morluto/rea/blob/main/docs/installation.md)
- [Node 官方发行包](https://nodejs.org/dist/v24.19.0/)
- [Codex MCP 官方说明](https://developers.openai.com/codex/mcp/)
- [Hermes MCP 官方说明](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/mcp.md)
- [DeepSeek Harness MCP 客户端](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.md)
- [ZCode CLI 配置说明](https://github.com/zai-org/ZCode/blob/main/apps/zcode-cli/README.md)
- [WorkBuddy MCP 说明](https://www.codebuddy.ai/docs/zh/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide)

## 源码构建

Windows x64，Python 3.14.3。安装 `requirements.txt` 的依赖后运行 `build.ps1`，完整命令见 [源码构建](BUILD.md)。
源码包已含 `runtime/rea-windows-x64.zip` 和 `runtime/manifest.json`，构建时不需要重新下载 REA。
`tools/bundle_rea.py` 可以从已安装的同版本 Node/REA 重建运行包，随后使用 `tools/update_rea_catalog.py` 更新技能目录校验值。

运行测试：`python -m unittest discover -s tests -p "test_*.py"`。
实际离线测试：`python tests/rea_acceptance.py`。
EXE 界面测试：`python tests/browser_acceptance.py dist/AISkillLibrary.exe`，需要开发测试依赖和本机 Edge。

程序、源码与验收证据通过 [v1.4.0 Release](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.4.0) 分发；下载后可以对照同页 `SHA256SUMS.txt` 检查完整性。
旧安全报告针对其中注明的 1.3.2 样本，不能作为新版 EXE 的安全检查结论。
