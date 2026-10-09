# 从源码构建

普通用户下载 [Windows 发布包](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.4.1)即可，无需执行本页命令。

## 环境与步骤

构建环境为 Windows x64、Python 3.14.3。运行界面需要 Microsoft Edge WebView2 Runtime。
源码已经包含 `runtime/rea-windows-x64.zip` 和 `runtime/manifest.json`，构建时无需另装 REA 或 Node。
Python 依赖的首次安装需要联网；依赖版本固定在 `requirements.txt`。

打开 PowerShell，在源码根目录执行：

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

产物为 `dist/AISkillLibrary.exe`。`build.ps1` 优先使用项目已有的运行环境，其次使用 `.venv`，最后使用 PATH 中的 Python。
发布 EXE 的 SHA-256 见同版本 Release 的 `SHA256SUMS.txt`；本机重新构建的二进制可能因环境和构建时间而有不同哈希。

## 额外验收

```powershell
& .\.venv\Scripts\python.exe tests/rea_acceptance.py
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe tests/browser_acceptance.py dist/AISkillLibrary.exe
```

REA 验收使用隔离配置和数据目录，测试内置包解压、七种连接配置、CLI/MCP 启动及样例分析。
浏览器验收需要本机 Edge。配置与独立服务验收不等于七种真实 AI 客户端都已完成会话验收。

## 运行包来源

运行包固定为 `rea-agents@6.1.0` 与 Node 24.19.0，SHA-256、关键文件和许可证位置记录在 `runtime/manifest.json`。
`tools/bundle_rea.py` 用于从已有的同版本 Node/REA 重建运行包；更换包后需同步更新技能目录校验值并重新验收。
运行包内保留 REA、Node 及依赖的许可证。
