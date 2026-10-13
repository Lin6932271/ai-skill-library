# 复现 ai技能库 1.5.5 检查

使用 Windows x64、Python 3.14 和本版固定哈希 EXE。工具静态读取归档、PE 与代码对象，不执行提取出来的应用代码或技能附件。

```powershell
python -m venv .audit-venv
& .\.audit-venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-audit.txt
& .\.audit-venv\Scripts\python.exe tools/audit_release.py --exe .\AISkillLibrary-1.5.5-windows-x64.exe --out .\artifacts\security-audit --observe
& .\.audit-venv\Scripts\python.exe tools/audit_dependencies.py --out .\artifacts\security-audit
powershell -NoProfile -ExecutionPolicy Bypass -File tools/scan_release.ps1 -Exe .\AISkillLibrary-1.5.5-windows-x64.exe -Out .\artifacts\security-audit
```

Defender 命令按本机权限与 Microsoft 官方要求执行；不会关闭防护、添加排除项或执行补救动作。保存完整输出，不能只凭返回码 0 就忽略命令正文。OSV 查询发送组件名称与版本，不发送项目源码或凭据。

四个核心模块的代码对象比较要求相同 Python 字节码版本；bootloader 比较要求相同 PyInstaller 版本。Python 组件清单来自对应构建环境的应用依赖闭包；若要核对发布包，应使用固定版本的 requirements。

原生 DLL/PYD 可通过 `--native-reference-dir <目录>` 增加构建参考。保有对应构建资料时，使用 `--build-analysis-toc <Analysis-00.toc路径>` 对照精确源文件。不同机器缺少参考文件不等于发现恶意文件。

`--observe` 使用隔离 home/data 和 --sandbox，对应用及其子进程做短时连接表采样、启动窗口检查与持久化快照。不是全量抓包或完整虚拟机隔离，本机代理可能遮蔽最终目的地址。这里只验证启动路径，不代表所有 AI 客户端与 REA 工具均完成业务验证。

本地接口的 11 项检查和实际方案切换结果随本版证据提供。历史步骤见 [1.3.2 复现记录](REPRODUCE-1.3.2.md)。
