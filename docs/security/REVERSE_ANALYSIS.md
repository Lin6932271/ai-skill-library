# ai技能库 1.5.5 · 逆向与安全分析报告

**开发方式：AI 开发。报告类型：AI 协助的项目自审。**

日期：2026-10-13（Asia/Shanghai）。仅适用于以下固定 SHA-256 的 Windows x64 EXE。本文依据本次解包、代码对照、接口验证、短时桌面观察及本机扫描记录；未取得独立第三方认证。

## 结论与范围

本次检查中，应用编译代码、打包资源和原生库与对应源码或构建参考字节一致。Microsoft Defender 定点扫描输出未发现威胁，样本分析与扫描前后哈希保持一致。应用四个核心 Python 模块的 Bandit 扫描高等级 0、中等级 0、低等级 5。

依赖版本检查另有 **6 个随 npm 附带组件匹配 30 条公开漏洞记录**。组件公告最高包含“严重”等级，产品中的真实可利用性尚未验证；本报告保留这些结果，不将本版描述为“无已知依赖问题”。

在四个应用模块和本次启动路径的有限检查中，未发现凭据窃取、未声明持久化或隐藏执行入口的证据。软件会按用户操作写入客户端技能与 MCP 配置，并调用内置 Node/REA 完成启动测试，这些是明确的产品功能。第三方全部内部代码、后续 AI 工具调用和长期操作路径没有完成全覆盖审计。

## 样本与版本

| 项目 | 值 |
| --- | --- |
| 程序 | ai技能库 1.5.5 |
| 发布文件 | `AISkillLibrary-1.5.5-windows-x64.exe` |
| 大小 | 98,674,724 字节 |
| 类型 | Windows x64 PE、GUI 子系统、PyInstaller 单文件程序 |
| Authenticode | NotSigned |
| 权限清单 | asInvoker |
| 原版 / 精品 | 49 / 161 项可用正文 |
| 分析及扫描后样本 | 哈希一致 |

```text
SHA-256: ddfc22575e5fcc6fe73de826b538f807fe1ce5566141facf5016ec50cd7297a6
```

[对应源码](https://github.com/Lin6932271/ai-skill-library/tree/v1.5.5) · [版本下载](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.5.5) · [机器可读摘要](releases/v1.5.5/audit-summary.json)。重新构建或修改过的 EXE 不属于同一固定哈希样本。

## 解包与代码对照

静态读取 PE、CArchive/PYZ 和 Python 代码对象，没有执行提取出来的代码或技能附件。

| 检查 | 结果 |
| --- | --- |
| CArchive / PYZ | 505 个归档成员 / 892 个模块 |
| 核心代码 | main、backend、rea_config、rea_runtime 与源码递归代码对象比较一致 |
| 启动与运行钩子 | 与对应 PyInstaller / Python 参考源码比较，明细保留在证据中 |
| 界面、技能和运行包 | 294 项资源与源码实际字节一致 |
| 原生 DLL / PYD | 103/103 项与构建参考字节的 SHA-256 一致 |
| PE bootloader | 段、导入、权限清单和调试时间戳规范化比较结果均保留 |

递归代码比较含字节码、常量、名称、变量、异常表和行号表，忽略构建路径相关的 co_filename。原生参考结合对应 Python 环境、安装包、系统库及本次 Analysis-00.toc 指向的构建文件。哈希相同能证明字节一致，不能替代全部第三方代码审计。

证据：[编译代码](releases/v1.5.5/packed-python-comparison.json)、[资源对照](releases/v1.5.5/bundled-resource-comparison.json)、[原生库](releases/v1.5.5/native-library-comparison.json)、[归档清单](releases/v1.5.5/archive-members.json)、[PE 信息](releases/v1.5.5/pe-analysis.json)。单文件程序释放运行文件属于其打包机制，见 [PyInstaller 官方说明](https://pyinstaller.org/en/stable/operating-mode.html)。

## 接口与数据边界

- 本地服务绑定 127.0.0.1，POST 接口校验 Host、Origin 和随机令牌；实际 EXE 的 11 项非修改请求检查通过，包括错误 Host/Origin/令牌、异常 JSON、过大请求和静态路径越界。
- 页面设置 CSP 与 nosniff，正文经过转义再展示；CSP 和响应头已在实际程序中核对。
- ZIP 导入有 32 MB / 2000 文件限制，拒绝越界路径、重复路径和链接；导入脚本作为附件保存。
- 安装先检查冲突并备份，切换或事务失败时恢复；外部修改会保留。实际程序已验证精品 161 项正文哈希、原版切换、备份及撤销恢复。
- REA 启动测试直接调用内置 Node 和 rea.mjs，使用参数数组并保持 shell=False 的默认行为。os.startfile 用于用户选择“打开目录”。

证据：[本地接口检查](releases/v1.5.5/api-boundary.json)、[调用索引](releases/v1.5.5/application-call-index.json)、[导入索引](releases/v1.5.5/application-import-index.json)。文件、指令与 MCP 配置的写入，和 AI 客户端之后如何使用这些内容，属于不同的验证层级。

## 静态扫描提示

Bandit 1.9.4 检查四个核心模块，共 1558 行，高 0、中 0、低 5；无扫描错误，未用 nosec 屏蔽规则。完整结果见 [bandit.json](releases/v1.5.5/bandit.json)。

| 规则 | 位置 | 人工解释 |
| --- | --- | --- |
| B606 | main.py:47 | 按用户动作打开已存在的配置目录 |
| B105 | main.py:300 | 验收结果字典中的 pass=False，不是密码常量 |
| B404 | rea_runtime.py:12 | 引入 subprocess，属于进程执行边界提示 |
| B603 | rea_runtime.py:251、257 | 调用所选托管 Node/REA 的版本及 MCP 启动测试；保留原提示 |

这些解释不是全局安全保证，具体执行路径与参数仍应独立核对。[Bandit 方法说明](https://bandit.readthedocs.io/en/latest/start.html)。

## 依赖版本检查与风险矩阵

生成了 11 个 Python 组件及 282 个 npm 组件版本的清单，共向 OSV 查询 293 个版本，时间为 2026-10-13T02:44:43.420600+00:00。本次数据库查询完整返回，11 个 Python 组件未匹配到记录，6 个 npm 组件匹配 30 条公开记录。

| 组件 | 随包版本 | 匹配公告数 | 组件公告最高等级 | 后续处理 |
| --- | --- | ---: | --- | --- |
| `brace-expansion` | 5.0.6 | 6 | 高 | 同主版本修复记录至少到 5.0.12，升级后再检查 |
| `http-cache-semantics` | 4.2.0 | 1 | 高 | 公告未列出修复版本，跟进上游修补或替代 |
| `ip-address` | 10.2.0 | 7 | 高 | 同主版本修复记录至少到 10.7.1，升级后再检查 |
| `postcss-selector-parser` | 7.1.4 | 1 | 中 | 同主版本修复记录至少到 7.1.6，升级后再检查 |
| `tar` | 7.5.16 | 5 | 严重 | 同主版本修复记录至少到 7.5.21，升级后再检查 |
| `undici` | 6.26.0 | 10 | 高 | 同主版本修复记录至少到 6.28.1，升级后再检查 |

这些命中实例全部位于 `node/node_modules/npm/node_modules/`。应用自己的 REA 启动测试直接调用 Node 脚本，并不直接调用 npm；这只能说明该启动路径，不能证明 REA 内部、npm 手动使用或之后的所有工具方法均不可达。没有运行拒绝服务、SSRF 或注入攻击来证明产品级利用。

例如 tar 7.5.16 匹配的记录含压缩归档处理资源耗尽问题；维护者公告列出 <=7.5.18 受影响及 7.5.19 修复，这只是该条记录的版本边界，其他命中记录需要分别核对。[维护者公告](https://github.com/isaacs/node-tar/security/advisories/GHSA-23hp-3jrh-7fpw)。缓存处理及地址分类问题也有单独记录：[缓存组件讨论](https://github.com/kornelski/http-cache-semantics/issues/56)、[地址组件维护者公告](https://github.com/beaugunderson/ip-address/security/advisories/GHSA-mwp4-54f8-5fhr)。

清单、公告及范围见 [SBOM](releases/v1.5.5/dependency-sbom.json)、[查询结果](releases/v1.5.5/dependency-osv.json)、[30 条公告](releases/v1.5.5/dependency-advisories.json)、[路径与人工复核](releases/v1.5.5/dependency-findings-reviewed.json)。OSV 查询以具体组件版本为输入，见 [官方 API](https://google.github.io/osv.dev/api/)。Node 本体、系统原生库和全部可选依赖不在这次 PyPI/npm 查询覆盖内，未匹配到记录不等于没有漏洞。

| 项目 | 本次判断 | 优先级与处理 |
| --- | --- | --- |
| npm 附带组件记录 | 已知版本匹配；产品可利用性未定级 | P1：升级 npm 依赖或评估裁剪非必要安装工具，随后回归 REA 高级方法及安装流程 |
| 未附 Authenticode 签名 | 确认存在 | P2：考虑正式签名；下载后核对固定 SHA-256 |
| Bandit 低等级提示 | 5 项保留，已解释当前参数和用途 | P2：保持参数与路径检查，修改执行路径时复查 |
| 本机代理与未覆盖路径 | 本次观察限制 | P2：需要更广结论时增加隔离环境抓包和工具调用路径检查 |

## 实际桌面短时观察

在隔离 home/data 中运行实际 EXE，启动 WebView2，完成动画、窗口和滚动检查后自然退出。本次持续 11.342 秒，成功采样连接表 105 次，采样错误 0。

没有观察到直接非回环远端连接；观察到 WebView2 连接本机代理，代理后的最终目的地址没有完成核实，因此不将此结果表述为“零联网”。Run/RunOnce、启动目录、服务名称和计划任务定义前后快照可获取且一致。服务名称快照不等于全部服务配置审查，短时连接采样也可能遗漏瞬时连接。

证据：[native-observation.json](releases/v1.5.5/native-observation.json)。本次运行和接口检查均未安装或改写真实 AI 客户端。

## Microsoft Defender 定点扫描

本次使用 ScanType 3 与 DisableRemediation 扫描固定 EXE，返回码 0，命令输出明确报告未发现威胁；扫描前后样本哈希一致。未修改防护开关或添加排除项，没有显式上传多引擎检测服务。

| 项目 | 值 |
| --- | --- |
| 平台 | 4.18.26080.4 |
| 引擎 | 1.1.26080.3 |
| 安全情报 | 1.459.691.0 |
| 情报更新时间 | 2026-10-12T16:06:44.0000000Z |
| 实时保护 | True |
| 扫描结束 | 2026-10-13T02:38:51.2426578+00:00 |

证据：[扫描输出](releases/v1.5.5/defender-scan.log)、[环境与结果](releases/v1.5.5/defender-result.json)。这是本机单引擎单文件结果，不是独立认证。参数与返回码含义见 [Microsoft 官方文档](https://learn.microsoft.com/en-us/defender-endpoint/command-line-arguments-microsoft-defender-antivirus)。

## 复现与证据索引

[复现步骤](REPRODUCE.md)、[本版证据 SHA-256](releases/v1.5.5/SHA256SUMS.txt)和发布附件提供原始检查摘要及完整性核对信息。[1.3.2 历史报告](REVERSE_ANALYSIS-1.3.2.md)和原历史证据保留，其结论只适用于旧样本。

本报告不作“绝对无病毒、无后门、无漏洞”的保证。应用静态对照、单文件扫描、组件公告版本匹配、独立服务启动和实际业务成功分别记录。
