# ai技能库 v1.3.2 · 逆向与安全分析报告

**开发方式：AI 开发。报告类型：AI 协助的项目自审。**

分析日期：2026-10-07（Asia/Shanghai）。对象是以下 SHA-256 对应的 Windows x64 发布程序。
本文提供样本、代码对照、运行观察和扫描证据，未取得独立第三方安全机构认证。

## 结论与适用范围

在本次检查的应用代码、发布包结构、单文件扫描和短时运行观察范围内，**未发现病毒载荷、隐藏命令执行、凭据窃取或未声明持久化入口的证据**。
核心代码与公开源码相符，界面及技能资源与对应 Git 提交的实际字节相符，Microsoft Defender 对该文件报告未发现威胁。

有限范围检查不构成“绝对无病毒、无后门、无漏洞”的保证。本机代理后的最终目的地址、第三方库全部内部代码，以及长期和所有操作路径均未完整验证。

## 样本与对应源码

| 项目 | 值 |
| --- | --- |
| 软件 | ai技能库 1.3.2 |
| 发布文件 | `AISkillLibrary-1.3.2-windows-x64.exe` |
| 大小 | 24,841,797 字节 |
| 类型 | x64 Windows PE，GUI 子系统，PyInstaller 单文件包 |
| 签名 | NotSigned，未附加 Authenticode 证书 |
| 权限声明 | asInvoker，跟随当前用户权限 |
| 核心源码提交 | `4f4aea6d5478d91d3e04e45f8b5309c62191f39e` |
| 分析前后哈希 | 一致 |

```text
SHA-256: 1c46ac529db10ce25d9d90d52f05e8a614495afda57fc8d7b6037f34a6a24b42
```

[对应源码](https://github.com/Lin6932271/ai-skill-library/tree/4f4aea6d5478d91d3e04e45f8b5309c62191f39e) · [发布下载](https://github.com/Lin6932271/ai-skill-library/releases/tag/v1.3.2) · [机器可读摘要](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/audit-summary.json)

只有哈希相同的文件属于本报告对象，二次修改或重新构建的文件需另行检查。

## EXE 解包与代码对照

使用 PyInstaller CArchive/PYZ 读取器、pefile 和 Python 代码对象比较；静态分析不执行提取出来的代码。

| 检查 | 结果 |
| --- | --- |
| CArchive / PYZ | 295 个归档成员 / 673 个模块 |
| main、backend | 递归代码对象与对应源码编译结果一致 |
| 启动代码 / runtime hook / struct | 10 项均与对应工具参考源码一致 |
| 界面及技能资源 | 127 项实际解包字节均与公开源码一致 |
| 原生 DLL / PYD | 84/84 项与构建环境参考文件的 SHA-256 相同 |

代码比较包含字节码、常量、名称、变量、闭包、异常表和行号表；忽略构建路径相关的 co_filename。
资源额外与 Git 已提交的 blob 逐字节核对，防止 Windows 换行转换造成源码包与程序不一致。
原生参考包含 Python、安装包、系统库和构建环境附带的 UCRT/API-set 文件。哈希一致不等于完整的第三方供应链审计。
PE 标准 bootloader 对照、资源类型、导入和权限清单详见 [PE 分析](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/pe-analysis.json)。

证据：[代码对照](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/packed-python-comparison.json)、[资源对照](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/bundled-resource-comparison.json)、[原生库对照](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/native-library-comparison.json)、[成员清单](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/archive-members.json)。
单文件程序解压运行库及产生应用父子进程属于其打包机制。[PyInstaller 官方说明](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works)

## 应用代码访问边界

- 服务仅绑定 127.0.0.1；API 验证 Host、Origin 和随机令牌，页面请求指向同源接口。定位：[main.py](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/main.py#L133)、[frontend/app.js](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/frontend/app.js#L49)。
- ZIP 导入限制 32 MB / 2000 文件，拒绝越界路径、重复路径和链接；技能脚本只保存为附件。定位：[backend.py](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/backend.py#L258)。
- 技能正文先转义再展示，页面 CSP 限制脚本、连接和媒体同源。定位：[frontend/app.js](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/frontend/app.js#L3)、[main.py](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/main.py#L77)。
- 安装先保存备份，事务失败时恢复；撤销会保留外部修改。定位：[backend.py](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/backend.py#L355)、[backend.py](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/backend.py#L449)。
- os.startfile 用于用户点击“打开目录”；PrintWindow 位于显式验收分支，目标为应用自己的窗口。未发现后台全桌面采集、键盘记录、浏览器密码读取或进程内存注入的自写实现。定位：[main.py](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/main.py#L47)、[main.py](https://github.com/Lin6932271/ai-skill-library/blob/4f4aea6d5478d91d3e04e45f8b5309c62191f39e/main.py#L201)。

技能安装指写入客户端指令与技能文件。正文中出现安全、逆向、Hook 等词汇属于可阅读资料；用户导入内容和 AI 客户端后续采用指令的行为需单独检查。

## 静态扫描

Bandit 1.9.4 扫描 main.py 与 backend.py，未跳过规则。高等级 0、中等级 0、低等级 2。
完整结果见 [bandit.json](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/bandit.json)。低等级提示保留，未通过屏蔽规则消除。
其中 os.startfile 打开已存在的配置目录；结果字典中的 pass: false 不是密码常量。实际访问令牌由 secrets.token_urlsafe(32) 生成。
[Bandit 官方说明](https://bandit.readthedocs.io/en/latest/start.html)

## 真实程序短时运行观察

在隔离的 home/data 目录运行发布 EXE，实际启动 WebView2 窗口，完成启动动画、窗口框架和滚动验收。
进程与连接表观察及前后持久化快照见 [native-observation.json](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/native-observation.json)。

- 桌面验收通过；连接采样错误为 0。
- 观察到的直接非回环远端连接为 0。
- 本机可能启用回环代理，代理后的最终目标未得到完整验证；不能据此声称“零联网”。
- Run/RunOnce、启动目录、服务名称和计划任务定义前后快照均可获取且未变。服务名称快照不等于全部服务配置审查。

连接表采样不是全量抓包，短时观察可能遗漏很短的连接或其他操作路径。

## Microsoft Defender 定点扫描

使用规范的 Windows 绝对路径执行 ScanType 3 文件扫描，附加 DisableRemediation；未更改防护开关、排除项，也未上传到多引擎服务。
扫描返回码 0，输出报告 found no threats，样本扫描前后哈希一致。证据：[完整扫描输出](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/defender-scan.log)、[扫描环境摘要](https://github.com/Lin6932271/ai-skill-library/blob/main/docs/security/evidence/audit-summary.json)。

| 项目 | 值 |
| --- | --- |
| 平台 | 4.18.26080.4 |
| 引擎 | 1.1.26080.3 |
| 安全情报 | 1.459.576.0 |
| 安全情报更新时间 | 2026-10-06T07:12:32.0000000+08:00 |
| 实时保护 | True |
| 扫描完成时间 | 2026-10-07T16:53:38.8975139+08:00 |

该结果属于本机单引擎、单文件检查，不能冒充多引擎检测计数或独立安全认证。
[Microsoft 官方命令说明](https://learn.microsoft.com/en-us/defender-endpoint/command-line-arguments-microsoft-defender-antivirus)

## 复查与使用注意

[复现步骤](REPRODUCE.md)提供静态与桌面观察命令，[证据哈希清单](evidence/SHA256SUMS.txt)用于核对原始证据。
使用说明与注意事项见 [USAGE.md](../USAGE.md) 和 [NOTICE.md](../../NOTICE.md)。
未签名、第三方依赖、本机代理、用户导入内容和未覆盖操作路径均属于本报告的实际限制。
