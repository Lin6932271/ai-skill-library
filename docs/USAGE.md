# ai技能库

版本 1.3.2。支持七种 AI 客户端的技能安装、切换、导入、自动备份、检查与撤销。

使用用户提供的图片作为程序、窗口与界面图标，将 `3.mp4` 作为启动动画。
动画约 7 秒，默认静音，完整播放后自动进入控制台，没有跳过按钮。媒体无法播放时自动进入控制台。
启动时不显示图标封面或图标浮层。视频保持比例铺满软件窗口，超出窗口的边缘居中裁切，不切换全屏。动画期间隐藏系统标题栏，播完后恢复标题栏和最小化、最大化、关闭按钮，保持窗口位置和大小。
界面与技能正文已清理来源、取回过程和云端返回状态的说明，保留技能流程、模块引用、安装记录、配置目录与导入内容。

## 使用

双击 `ai技能库.exe`。不需要安装 Python、登录或连接原服务器。
桌面窗口使用 Windows 已安装的 WebView2 Runtime。

1. 确认客户端卡片的配置目录，可用“设置”选择实际目录。
2. 默认选择“完整技能库 · 53 项”，开启技能；也可选择单个技能、50 项扩展技能、基础、进阶或导入方案。
3. 写入前自动保存备份。整套方案安装目录入口与对应模块，单个入口同时安装引用的内置模块。
4. 点击“检查”验证文件。重启实际客户端、新建会话，确认其是否读取技能。
5. 关闭开关可撤销。外部修改会保留，存在冲突时不会覆盖用户内容。

已有安装保留原选择，可从下拉框切换。升级程序本身不会重写客户端的技能文件。
如果客户端已经安装旧正文，关闭再开启对应技能即可更新，原始备份与撤销方式保持兼容。
文件检查只代表安装状态，模型读取需要在实际客户端确认。技能引用的工具与附件需核对本机环境。
Hermes 便携版需选择实际 `data/hermes-home` 或当前 profile 目录，其他客户端版本也可能需调整目录或手动选择技能。

| 客户端 | 默认目录 / 环境变量 | 指令文件 |
| --- | --- | --- |
| Codex | `~/.codex` / `CODEX_HOME` | `AGENTS.md` |
| Claude | `~/.claude` / `CLAUDE_CONFIG_DIR` | `CLAUDE.md` |
| DeepSeek Harness | `~/.dsh` / `DSH_HOME` | `AGENTS.md` |
| Hermes | 优先已有 `~/.hermes`，否则 `%LOCALAPPDATA%/hermes`；支持 `HERMES_HOME` | `HERMES.md` |
| ZCode | `~/.zcode` / `ZCODE_HOME` | `AGENTS.md` |
| WorkBuddy 国内版 | `~/.workbuddy` / `WORKBUDDY_CONFIG_DIR` | `CODEBUDDY.md` |
| WorkBuddy 国际版 | `~/.workbuddy-ai` / `WORKBUDDY_AI_CONFIG_DIR` | `CODEBUDDY.md` |

## 导入技能

在“技能库”中点击“导入技能”。支持 UTF-8 Markdown、根目录含 `SKILL.md` 的文件夹，或恰含一个 `SKILL.md` 的 ZIP。
文件夹和 ZIP 可附带 `references/`、`scripts/` 等资源，每次导入一个技能。单个 Markdown 不会收集相邻资源。
限制为 32 MB 和 2000 个文件，拒绝越界路径、重复 ZIP 路径和链接。
脚本只作为资源保存，助手不会执行。修改源文件后重新导入，再切换到新方案。
技能库支持搜索、领域分类，以及内置、扩展和开发与导入集合筛选。

## 数据与恢复

继续使用 `%LOCALAPPDATA%/PojiaLocal`，兼容旧版本。
`state.json` 保存安装、目录和技能索引，`backups/` 保存原始快照，`imports/` 保存导入资源。
只管理助手自身写入的段落和文件，撤销时保留其他内容，外部修改会报告冲突。
“状态检查”可导出诊断，其中可能包含本机目录，程序不会上传这些数据。

界面通过随机端口的 `127.0.0.1` 与后端通信。API 验证 Host、Origin 和随机令牌，页面限制连接为同源。
账户、订阅、反馈和原服务器调用继续保持移除状态。

## 开发与构建

入口为 `main.py`、`backend.py` 和 `frontend/app.js`，技能在 `skills/`。
品牌资源是 `frontend/assets/app-icon.jpg`、`app-icon.ico` 和 `startup.mp4`，窗口与 EXE 共用 ICO。
`version_info.txt` 设置 Windows 文件属性里的产品名称和版本。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
.\build.ps1
```

构建输出 `dist/AISkillLibrary.exe`，交付时命名为 `ai技能库.exe`。也可直接运行：

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name AISkillLibrary --icon frontend/assets/app-icon.ico --version-file version_info.txt --collect-all webview --add-data "frontend;frontend" --add-data "skills;skills" main.py
```

扩展正文生成器 `rebuild_library.py` 会覆盖生成内容，请先保存自己编辑的文件。
构建只读取现有文件，不需要恢复服务器连接。

```powershell
python tests/test_local.py
```

浏览器验收依赖 `requirements-dev.txt` 与本机 Edge，具体步骤见 [BUILD.md](BUILD.md)。
使用 `--sandbox --home <隔离目录> --data-dir <隔离目录>` 可避免接触实际客户端。
验收范围见 [VERIFICATION.md](VERIFICATION.md)。
