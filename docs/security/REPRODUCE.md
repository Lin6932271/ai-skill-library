# 复现 v1.3.2 检查

使用 Windows x64、Python 3.14，以及公开发布页下载的固定哈希 EXE。
静态分析只读取 PE、归档和代码对象，不执行提取出来的代码。

```powershell
python -m venv .audit-venv
.\.audit-venv\Scripts\python.exe -m pip install -r requirements-audit.txt
.\.audit-venv\Scripts\python.exe tools/audit_release.py --exe .\AISkillLibrary-1.3.2-windows-x64.exe --out .\artifacts\security-audit
```

额外运行短时桌面观察：

```powershell
.\.audit-venv\Scripts\python.exe tools/audit_release.py --exe .\AISkillLibrary-1.3.2-windows-x64.exe --out .\artifacts\security-audit --observe
```

桌面观察使用明确隔离的 home/data 路径及 `--sandbox`，显示应用窗口，自动关闭。
它采样该实例与其子进程的连接表，对 Run/RunOnce、启动目录、服务名称和计划任务定义进行前后快照。
这是短时观察，不是隔离虚拟机或全量抓包；本机代理可以隐藏最终目的地址。

`--native-reference-dir <目录>` 可补充构建时的原生运行库参考目录。
额外 CRT/API-set 参考文件需与构建环境对应。
不同机器上未安装相同参考文件时，原生库哈希匹配数量会变化；不应把缺少参考文件直接判为恶意。
核心代码对照需要相同 Python 字节码版本；bootloader 对照需要相同 PyInstaller 版本。

Bandit 两个低等级提示及人工分析均在报告中保留，工具返回码 1 可能表示存在提示，不能简单按“运行失败”解释。
Defender 定点扫描请遵循 Microsoft 官方说明，使用规范的 Windows 路径并记录平台、引擎、情报版本与完整输出。
报告与附件中的 SHA-256 清单可用于独立核对证据文件。
