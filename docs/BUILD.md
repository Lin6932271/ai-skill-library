# Windows 构建

当前发布制品是在 Windows x64、Python 3.14 上构建，使用 `requirements.txt` 中固定的依赖版本。
桌面启动需要 Microsoft Edge WebView2 Runtime。

## 安装依赖

在仓库根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 测试

```powershell
.\.venv\Scripts\python.exe tests/test_local.py
```

20 项集成测试使用临时目录，覆盖七种客户端适配、技能切换、导入、备份恢复、冲突处理和本地 API。

浏览器验收为可选步骤，需要本机标准安装位置的 Microsoft Edge：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe tests/browser_acceptance.py
```

该验收通过临时配置目录运行，截图与记录输出至 `artifacts/acceptance/`。
测试会使用 `--serve --sandbox` 启动本地服务，无需修改日常客户端配置。

## 打包 EXE

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

构建脚本优先使用已创建的 `.venv`；现有工作区兼容路径可用时也支持其运行环境。
生成 `dist/AISkillLibrary.exe`，可复制并命名为 `ai技能库.exe`。
图标、启动视频和技能目录均打包在 EXE 中，不需要把源码放在程序旁边。

重新构建后请再次运行验收并计算 SHA-256。不同环境构建的二进制校验值可能不同。
`rebuild_library.py` 会重新生成扩展技能正文；普通构建无需运行它。

源码整理使浏览器验收不再依赖原工作区路径，并让 HTTP 授权测试一次发送完整请求，避免 Windows 提前关闭未授权连接造成测试时序干扰；拒绝条件、403 响应与有效请求检查均保留。
