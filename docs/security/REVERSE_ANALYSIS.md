# ai技能库 v1.3.2 · 逆向与安全分析报告

**开发方式：AI 开发。报告类型：AI 协助的项目自审。**

分析日期：2026-10-07（Asia/Shanghai）。对象是下面 SHA-256 对应的 Windows x64 发布程序。
本文提供可复核的样本、代码对照与运行证据，未取得独立第三方安全机构认证。

## 结论与适用范围

在本次核对的自写代码、发布包结构、单文件防病毒扫描和短时运行观察范围内，**未发现病毒载荷、隐藏命令执行、凭据窃取或未声明持久化入口的证据**。
核心 Python 代码与公开源码相符，界面和技能资源未发现替换，Microsoft Defender 对该文件报告未发现威胁。

这是一项有限范围的检查，不构成“绝对无病毒、无后门、无漏洞”的保证。尤其是本机代理后的最终目的地址、第三方库全部内部代码以及长期或所有操作路径，均未得到完整验证。

## 1. 样本与对应源码

| 项目 | 值 |
| --- | --- |
| 软件 | ai技能库 1.3.2 |
| 发布文件 | `AISkillLibrary-1.3.2-windows-x64.exe` |
| 大小 | 24,850,640 字节 |
| 架构 / 类型 | x64 Windows PE，GUI 子系统，PyInstaller 单文件包 |
| 签名状态 | `NotSigned`，未附加 Authenticode 证书 |
| Windows 权限声明 | `asInvoker`，跟随当前用户权限 |
| 核心源码提交 | `c847ba94ff218ee14a1de78839feca9c632a2aab` |
| 分析前后文件 | SHA-256 保持一致 |

```text
SHA-256: 90fcc9798625f02eee86e59da6763f1a1144c1048c55d8cb4fc3f132f477026d
```

[源码提交](https://github.com/Lin6932271/ai-skill-library/tree/c847ba94ff218ee14a1de78839feca9c632a2aab) · [发布下载](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.3.2) · [机器可读摘要](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/audit-summary.json)

只有哈希相同的文件属于本报告对象。重新构建、二次修改或重新打包的文件需另行检查。

## 2. EXE 解包与代码对照

采用 PyInstaller CArchive/PYZ 读取器直接解析发布 EXE，不执行提取出来的代码或技能资源。
该文件的 CArchive 包含 **295 项**，PYZ 索引包含 **673 个模块**。

| 检查 | 实际结果 |
| --- | --- |
| `main` 与 `main.py` | 递归代码对象字段一致 |
| `backend` 与 `backend.py` | 递归代码对象字段一致 |
| 标准启动 / runtime hook / `struct` | 10 项均与本机对应 PyInstaller / Python 参考源码一致 |
| `frontend/`、`skills/` | 127 个资源的实际解包字节均与仓库相同 |
| 原生 DLL / PYD | 84/84 项与构建环境参考文件的 SHA-256 相同 |
| PE `.text` | 与 PyInstaller 6.22.3 标准 Windows x64 GUI bootloader 相同 |
| PE `.rdata` | 归一化 Debug 目录时间戳后与标准 bootloader 相同；原差异为该字段中的 3 个字节 |
| PE 资源类型 | ICON、GROUP_ICON、VERSION、MANIFEST；图标与版本资源属于声明的品牌修改 |

代码对照同时检查字节码、常量、导入名、变量、闭包、异常表与行号表；忽略构建路径相关的 `co_filename`。
这里比较的是发布文件里的实际代码对象，并非只在源码里搜索关键词。
84 个原生库参考包含 Python、已安装包、系统库，以及构建清单解析到的 libheif 环境 UCRT/API-set 文件。
**参考文件哈希一致说明这些文件未被另行替换；它不等于完整的第三方供应链审计。**

证据：[代码对照](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/packed-python-comparison.json)、[资源对照](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/bundled-resource-comparison.json)、[原生库对照](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/native-library-comparison.json)、[完整成员清单](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/archive-members.json)、[PE 分析](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/pe-analysis.json)、[PE 导入](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/pe-imports.csv)。

PyInstaller 单文件程序会解压运行库并启动应用进程，这是本次看到两层应用进程及临时运行库的实现背景。[PyInstaller 官方运行原理](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works)

## 3. 自写代码人工审查

```mermaid
flowchart LR
  A[标准 PyInstaller 启动器] --> B[main.py 与 Windows 窗口]
  B --> C[127.0.0.1 随机端口服务]
  D[WebView2 前端] --> C
  C --> E[backend.py 技能管理]
  E --> F[用户选择的客户端配置与技能目录]
  E --> G[本机备份和安装记录]
```

- **通信与访问控制**：后端仅绑定 `127.0.0.1`；GET 检查精确 Host，POST 继续检查精确 Origin 与随机令牌，使用 `hmac.compare_digest` 比较。前端业务 `fetch` 指向同源 `/api`，未发现原服务端调用或隐藏远端命令通道。定位：[main.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/main.py#L89), [main.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/main.py#L130), [frontend/app.js](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/frontend/app.js#L48)。
- **文件与导入边界**：API 命令按明确分支分派；ZIP 拒绝越界路径、重复路径和符号链接，限制 32 MB / 2000 文件。导入只复制 Markdown 和附件，未发现自动执行导入脚本的调用路径。定位：[backend.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/backend.py#L497), [backend.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/backend.py#L244)。
- **页面展示**：技能正文通过 `esc()` 转为文本后展示；未作为 JavaScript 执行。页面 CSP 限制脚本、连接与媒体同源。定位：[frontend/app.js](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/frontend/app.js#L3), [frontend/app.js](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/frontend/app.js#L147), [main.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/main.py#L77)。
- **写入与恢复**：技能安装保存原内容备份，再事务写入明确配置目录；冲突时保留外部修改；撤销检查已管理文件的哈希。未发现持久化服务、计划任务或自启动项的注册代码。定位：[backend.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/backend.py#L341), [backend.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/backend.py#L434)。
- **进程与截图**：业务里的 `os.startfile` 用于用户点击“打开目录”，先检查目录存在；`PrintWindow` 位于显式 `--smoke-file` 验收分支，目标为应用自己的窗口。未发现后台全桌面采集、键盘记录、浏览器密码读取或其他进程内存注入的自写实现。定位：[main.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/main.py#L43), [main.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/main.py#L193), [main.py](https://github.com/Lin6932271/ai-skill-library/blob/c847ba94ff218ee14a1de78839feca9c632a2aab/main.py#L298)。

“技能注入”在此应用中指写入客户端指令与技能文件，不是向其他程序地址空间注入机器码。
技能正文中出现逆向、后门、攻击或 Hook 等词汇属于可阅读资料；该应用的已审查路径只复制或展示它们。
随后 AI 客户端如何采用这些指令仍应单独检查，用户后续导入的内容也会影响客户端行为。

## 4. Bandit 静态扫描与人工判断

Bandit 1.9.4 扫描 `main.py`、`backend.py` 共 848 行有效代码。
结果为 **高等级 0、中等级 0、低等级 2**；未跳过规则，扫描错误为 0。

| 规则 / 位置 | 原始提示 | 人工判断 |
| --- | --- | --- |
| B606 · `main.py:47` | 无 shell 的进程启动 | `os.startfile(str(root))` 打开已存在的客户端目录，属于可见功能；未发现 shell 命令拼接。仍需使用可信配置目录。 |
| B105 · `main.py:300` | 可能的硬编码密码 `False` | 对验收结果字典 `pass: False` 的词法误判，不是认证凭据；真实 API 令牌运行时由 `secrets.token_urlsafe(32)` 生成。 |

两个原始提示均保留在 [bandit.json](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/bandit.json)，没有靠忽略规则来制造“零问题”结果。
静态扫描结果不能替代人工审查，也不能证明所有漏洞已经排除。[Bandit 官方说明](https://bandit.readthedocs.io/en/latest/start.html)

## 5. 实际运行与持久化观察

以发布 EXE 启动独立 `--sandbox` 实例，显式指定隔离的 home/data 目录。
本次覆盖启动动画、自动进入主界面与页面滚动，应用自然关闭，真实桌面验收通过。

| 项目 | 观察结果 |
| --- | --- |
| 观察时长 | 10.506 秒 |
| TCP/UDP 表成功采样 | 98 次，平均间隔 0.108 秒 |
| 采样权限错误 | 0 |
| 进程 | 9 个；名称为应用 EXE 与 `msedgewebview2.exe` |
| 直接非回环远端 IP | 本次采样未观察到 |
| 本机代理 | WebView2 连接 `127.0.0.1:7897`，与 Windows 已启用代理设置一致 |
| Run / RunOnce | HKCU/HKLM 的 32/64 位视图，观察前后未变化 |
| 两个启动目录 | 文件元数据清单未变化 |
| Windows 服务 | 服务名称清单未变化；未比较所有服务内部配置 |
| 计划任务 | 定义快照未变化 |

**代理边界必须保留**：本机代理可以转发远端流量。本次没有归因代理最终访问的域名、IP 或请求内容，
因此“未看到非回环 IP”不能写成“软件及 WebView2 完全不联网”。该观察采用连接表采样，也可能漏掉更短的连接，未进行完整抓包。
前述源码审查与页面同源策略支持业务接口仅本机通信；WebView2、系统代理和依赖的完整网络行为仍属于额外审计范围。

证据：[native-observation.json](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/native-observation.json)。
此前七种客户端适配的安装/切换/检查/撤销测试使用隔离目录，20 项通过；这不代表七款客户端的真实业务会话均已验收。

## 6. Microsoft Defender 单文件扫描

| 项目 | 实际值 |
| --- | --- |
| 扫描完成 | `2026-10-07T15:54:53.4553809+08:00` |
| Defender 平台 | `4.18.26080.4` |
| 引擎 | `1.1.26080.3` |
| 安全情报版本 | `1.459.576.0` |
| 情报更新时间 | `2026-10-06T07:12:32+08:00` |
| 模式 | 自定义单文件扫描，`-DisableRemediation` |
| 返回码 / 输出 | `0` / `found no threats` |

第一次与更换平台后的第二次尝试使用了正斜杠路径，返回 `0x80508023`，均未记为通过；
第三次使用规范 Windows 绝对路径完成扫描，报告未发现威胁。错误尝试和成功尝试都记录于摘要。
扫描前后 EXE 哈希一致。未修改防病毒保护、添加排除项或更改样本。
使用 `-DisableRemediation` 进行定点检查，其检测结果通过命令输出记录，不进行该次扫描的修复动作。[Microsoft 官方参数说明](https://learn.microsoft.com/en-us/defender-endpoint/command-line-arguments-microsoft-defender-antivirus)

证据：[脱敏扫描输出](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/defender-scan.log)、[扫描元数据](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/audit-summary.json)。
这是一个引擎、一个安全情报版本的检测结果；多引擎扫描和独立第三方审计尚未开展。

## 7. 仍需说明的限制

- 本报告由项目开发流程内的 AI 协助完成，未构成独立审计机构证明。
- 文件目前未签名。哈希、源码对照与查毒结果分别说明完整性、对应关系与本次检测状态，不能相互替代。
- 第三方 Python 模块与原生库未全部逐函数反编译或进行完整漏洞/供应链审计；匹配参考文件不能排除参考环境被污染的可能。
- 约 10 秒的运行观察覆盖特定路径；长期、所有导入格式和所有客户端环境需要更广测试。
- WebView2 到本机代理的最终目的地址未完成归因；未提供“全进程零外连”的结论。
- 用户可指定配置目录，也可能选择网络路径。备份和诊断可能含自己的指令或本机目录，应按个人数据管理。
- 后续更新、二次打包或不同哈希的文件不自动继承本结论。

## 8. 下载者如何复核

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath .\AISkillLibrary-1.3.2-windows-x64.exe
```

确认结果与第 1 节相同，再用自己的防病毒软件扫描该文件。
源码、解包字节码对照脚本、Bandit 原始结果、PE 导入和文件哈希清单均已公开。
[复现说明](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/REPRODUCE.md) · [证据 ZIP](https://github.com/Lin6932271/ai-skill-library/releases/download/v1.3.2/AISkillLibrary-1.3.2-audit-evidence.zip)
