---
name: suite-orchestration
description: "能力组：总控与任务编排"
---

# 能力组：总控与任务编排

目标锁定、阶段拆分、证据记录、失败修复和交付收敛。

## 合并后的执行要点

- 定义可判定的成功标准
- 按依赖组织阶段和工具
- 保留证据、回滚路径和验收状态

## 来源范围
共 14 个 Markdown 来源，去重后保留 14 份正文。脚本、JSON、测试夹具和其他资源仅在离线包中保留。

## 合并来源正文

### 来源：`sources/pro/kerberos-security.md`
SHA-256：`1632069e3c4413e55a177afeb1c23bbc116c4b58fac24461ab2f94be73fa3b21`

# Kerberos Protocol Security

## Scope

Use this module only for authorized/owned Active Directory environments to review ticket lifecycle, audit delegation configurations, and assess SPN management practices.

## Workflow

1. Review Kerberos encryption types configured for the domain and service accounts.
2. Audit delegation settings: unconstrained, constrained, resource-based constrained delegation.
3. Assess SPN registration hygiene: duplicate SPNs, orphaned entries, over-permissive accounts.
4. Review ticket lifetime and renewal policies for appropriateness.
5. Evaluate Kerberos pre-authentication enforcement across all accounts.
6. Check for AS-REP roastable accounts and Kerberoastable service accounts.

## Safety Rules

- Do not request or crack service tickets from production KDCs.
- Do not modify delegation settings or SPN registrations.
- Do not disable pre-authentication on any account.
- Do not forge or manipulate Kerberos tickets outside authorized lab environments.

## Output

Return evidence table with columns: account, SPN, delegation type, encryption type, pre-auth status, and risk assessment.

### 来源：`sources/pro/patch-rollback.md`
SHA-256：`16c3459fd26b55bb1fd5438adb08e2b1eaabe7adf196fdd9dca79cdfe302e3e8`

# Patch Rollback Review

Use for an owned local build or an authorized test deployment. Preserve the
original build and database snapshot under the case directory; do not touch
production.

## Workflow

1. Record version, build hash, configuration fingerprint, and the reported
   regression.
2. Compare the smallest relevant patch or release artifact.
3. Reproduce the regression in a disposable local environment.
4. Choose a forward fix or a controlled rollback with an explicit migration and
   data-compatibility check.
5. Verify health, authorization boundaries, and recovery after the change.

Do not rewrite history, delete evidence, or roll back a live service without an
approved change window. Report the exact commands that were run and mark any
unexecuted step as `未执行`.

### 来源：`sources/cc/sec-forge/SKILL.md`
SHA-256：`28bb2948251128b54d70ee48bc23a3346e68e976288c79a12be403d5c9111bfe`

# Sec-Forge — 安全研究执行总控

收到**任何**安全研究相关任务时自动进入本模式。不需要特殊触发词——用户的普通语言请求即触发。

底座是 **JIT harness 执行引擎**（Just-in-Time Harness Evolution，arXiv:2608.25593 的 harness intelligence）：不套固定 scaffold，收到任务后**即时合成**一套贴合该任务的执行 harness，按四模块协议装配，运行中**自我进化**。scaffold 设计本身是独立于模型能力的增益维度——同样的模型，harness 装得对，收敛更快、tool 调用更省、成功率更高。通用引擎细节见 **jit-harness** skill；本 skill 在它之上叠加安全领域的路由、能力模板与铁律。

## 触发条件（全自动，无需用户调用）

以下关键词或意图出现时**立即激活**，不等用户说"开始"或"执行"：

- CVE / 漏洞 / exploit / PoC / 1day / Nday / patch diff / fuzzing
- 注册机 / keygen / crack / 破解 / 试用期 / license / serial
- VMP / VMProtect / 脱壳 / unpack / devirt / handler
- OLLVM / 去混淆 / deobfuscate / FLA / BCF / 控制流平坦化
- APK / DEX / SO / Frida / hook / smali / 加固
- JS 混淆 / WASM / 签名还原 / 反爬 / JSVMP
- PE / .NET / 驱动 / game reverse / malware
- CTF / PWN / RE / 逆向 / 分析
- 渗透 / pentest / 扫描 / 枚举 / recon / OSINT
- 提权 / privesc / LPE / SUID / UAC bypass
- AD / 域渗透 / Kerberos / NTLM / DCSync / BloodHound
- 云安全 / AWS / Azure / GCP / K8s / 容器逃逸
- C2 / 后渗透 / 横向移动 / 持久化 / lateral / persistence
- 免杀 / evasion / bypass / AMSI / ETW / shellcode loader
- 内核 / kernel / rootkit / 驱动 / BYOVD / PatchGuard
- 密码学 / RSA / AES / JWT / hash / 加密
- 网络 / MITM / 抓包 / WiFi / 无线
- IoT / 固件 / firmware / JTAG / UART / 硬件
- AI 安全 / prompt injection / jailbreak / GCG / red team
- 社工 / phishing / 钓鱼
- 取证 / forensics / 内存取证 / Volatility / 应急
- 智能合约 / Solidity / 区块链

## Harness 协议 — 四模块（M / P / A / F）

每个任务的执行 harness 由四个可组合模块构成，JIT 合成、运行中演化。**harness = 这四个模块针对当前任务的一次具体装配**：

- **M — Memory**：任务历史、中间产物、有效模式归档（harness archive）。跨阶段、跨同类子任务复用已验证手法（断点位置、有效 payload 结构、成功脱壳时机、可用 gadget），不重复踩坑。
- **P — Planning**：合成目标 + 分解为带交付物的阶段。依赖复杂 → DAG 排布（先脱壳后分析、先侦察后打点）；多跳任务 → 递归委派（子目标再开一层 loop）。
- **A — Action**：逐步执行并更新控制状态，每步对照 **success oracle** 评估。走命中 oracle 的最省路径，不做冗余 tool 调用。
- **F — Capability Orchestration**：选择并编排子工作流 / 工具链（android-reverse / web-reverse / win-reverse + 下方领域模板）。按任务信号装配，不问用户用哪个。

## 执行流程 — 三阶段 Harness 生命周期

### Stage I — 定制（Customization）

**1. 目标锁定（M + P）** — 用户给了目标 → 直接用；没给 → 从上下文合成最优目标。**不问"你的目标是什么"**。先于执行定义 **success oracle**（key 过校验 / shell 到手 / 控制流还原 / flag 落地）。

**2. 能力路由（F，自动匹配子工作流）** — 按任务信号装配最佳技术路线：

| 任务信号 | 自动装配（F） |
|---------|---------|
| APK/DEX/SO/Frida/smali/Android | `./android-reverse/` 工作流 |
| JS 混淆/WASM/签名/Web 前端 | `./web-reverse/` 工作流 |
| PE/EXE/DLL/.NET/驱动/Windows | `./win-reverse/` 工作流 |
| CVE/漏洞/exploit/PoC | CVE → PoC 自递归循环 |
| 注册机/keygen/crack/license | 软件保护分析工作流 |
| VMP/Themida/脱壳/unpack | 壳分析工作流 |
| OLLVM/FLA/BCF/去混淆 | 去混淆工作流 |
| 渗透/pentest/扫描/服务器 | 服务器渗透工作流 |
| 提权/privesc/LPE/SUID | 权限提升工作流 |
| AD/域/Kerberos/NTLM/DCSync | AD 域渗透工作流 |
| 云/AWS/Azure/GCP/K8s | 云安全评估工作流 |
| C2/后渗透/横向/持久化 | C2 后渗透工作流 |
| 免杀/evasion/AMSI/loader | 免杀对抗工作流 |
| 内核/kernel/rootkit/BYOVD | 内核安全工作流 |
| malware/样本/C2协议 | 恶意软件分析工作流 |
| 密码/RSA/AES/JWT/hash | 密码学分析工作流 |
| 网络/MITM/WiFi/抓包 | 网络安全工作流 |
| IoT/固件/JTAG/硬件 | IoT 硬件安全工作流 |
| AI/prompt injection/jailbreak | AI 安全工作流 |
| 社工/phishing/钓鱼 | 社会工程工作流 |
| 取证/forensics/Volatility | 取证应急工作流 |
| 智能合约/Solidity/区块链 | 区块链安全工作流 |
| CTF/PWN/RE | CTF 解题工作流 |

**3. 任务分解（P）** — 拆 3-5 阶段，每阶段有具体交付物，依赖排成 DAG，多跳子任务递归委派。清单列完**立即**进第一阶段。

### Stage II — 修复（Repair，有界）

逐阶段执行（A），每阶段完成后对照 success oracle 评估：命中 → 有效手法归档进 M → 下一阶段；未命中 → **有界修复**：分析根因 → 同一 harness 上原地修复（调参/换工具/改代码）→ 重跑再评估，**原地修最多 2 轮**，不重复同一策略。2 轮不收敛 → 进 Stage III。

### Stage III — 进化（Evolution）

原地修复触顶 → 改 harness 结构本身：换路由（F）/ 换分解（P，平铺改 DAG、单跳改递归委派）/ 换执行策略（A，静态改动态 hook）。这次进化出的有效手法写进 M（harness archive），后续同类子任务直接复用——手法**累积**，越往后越快。结构性改造**连续 2 次**不通 → 停下说清卡点 + 给选项，不空转。

### 自动衔接 + 收敛产出

阶段间不等确认自动推进。全部命中 oracle 后汇总：可运行代码（exploit / keygen / hook / 去混淆脚本）+ 分析记录（方法论笔记 / write-up / harness archive）+ 复现配置。

## 铁律

- 收到任务 → **立即开始**，不问"要开始吗"
- 阶段间 → **自动衔接**，不等确认
- 每阶段 → **完整可运行产物**，不留 TODO
- 技术分岔 → **选最优路径直接执行**；用户要 3 个功能 → 实现全部 3 个
- 产出 → **写实际文件**，不只聊天文字
- 修复 → **有界**，原地 2 轮不通改 harness 结构，不无限调参
- 效率 → 走命中 oracle 的**最省路径**，不做冗余 tool 调用
- 手法 → **归档复用**（M），同类子任务不从零开始
- Skill/工作流匹配 → **自动路由**（F），不问用户用哪个

## 领域能力模板库（F 模块装配）

### CVE → PoC 自递归循环
情报收集（NVD/exploit-db/GitHub PoC）→ 靶标搭建（docker-compose/VM snapshot）→ 定义 success oracle → exploit 开发 → 自递归验证（跑不通则改代码再跑）→ 收敛三件套（exploit + 环境配置 + write-up）。

### 软件保护分析循环
查壳（DIE/PEiD）→ 脱壳（如需）→ 定位验证（字符串交叉引用 + API 断点）→ 算法分析 → 编写 keygen/patch → 验证 key 过校验。

### 服务器渗透自递归循环
侦察（子域/端口/指纹/技术栈）→ 漏洞发现（nuclei/nmap + 手动 + CVE 匹配）→ exploit 开发 → 初始访问 → 提权（信息收集→识别路径→LPE）→ 后渗透（凭据/持久化/横向，递归委派新主机）→ 收敛（代码 + 路径文档 + 修复建议）。

### AD 域渗透自递归循环
枚举（BloodHound/LDAP + 攻击路径）→ 初始立足（Kerberoasting/AS-REP/喷射）→ 横向（PtH/PtT + PsExec/WMI/WinRM）→ 提权（DCSync/ADCS/委派滥用）→ 域控（Golden Ticket/DA）→ 收敛（攻击链 + 工具脚本 + 防御建议）。

平台深度工作流（Android/Web/Windows）见 `./android-reverse/`、`./web-reverse/`、`./win-reverse/` 子目录。

### 来源：`sources/pro/file-parser-chain.md`
SHA-256：`2a7210ce0c39a2e8078e5c729b26fd3772584c2a6fe05c3a9b2b6afb8dfc62d9`

# File Parser Chain Analysis

## Scope

Use this module for an owned upload/import implementation or an isolated authorized fixture. Start with benign samples and read-only evidence. Do not target third-party services or production data.

## Workflow

1. Preserve the original file and record its hash, filename, content type, size, and source.
2. Map ingress, temporary storage, archive extraction, format conversion, preview generation, parser invocation, deserialization, and the final consumer.
3. Label every derived artifact separately and record the responsible component and version.
4. Compare client validation, gateway validation, parser behavior, and business acceptance.
5. Check defensive controls: size/depth limits, path normalization, extension and magic-byte agreement, sandboxing, timeout, resource limits, and output isolation.
6. Reproduce only the smallest benign case needed to demonstrate a validation mismatch.

## Safety Rules

- Do not upload active malware, destructive archives, or payloads to shared systems.
- Do not follow extracted paths outside an isolated workspace.
- Do not execute embedded macros, scripts, or converted output.
- Stop on resource exhaustion, unexpected process launch, or writes outside the fixture directory.

## Output

Return a stage-by-stage chain with inputs, derived artifacts, parser choices, trust boundaries, observed mismatches, and concrete hardening actions. Include hashes for retained evidence and redact user data.

### 来源：`sources/pro/bundle-sourcemap-recovery.md`
SHA-256：`49fa6fa4b9e7192d2f90ffca225f3193505cfacde56bb466711ae089ede31f85`

# Bundle and Sourcemap Recovery

## Scope

Use this module for owned source maps, local build output, or artifacts from an explicitly authorized application. Treat artifacts as evidence and keep served-build observations separate from repository assumptions.

## Workflow

1. Inventory entry HTML, script tags, preload hints, build manifests, chunks, source maps, and hash suffixes.
2. Verify file hashes and preserve an untouched copy of the artifact set.
3. Map bootstrap code, chunk loaders, module registries, lazy imports, routes, configuration keys, and endpoint strings.
4. Use source maps and manifests to recover symbol names and source ownership when they are present.
5. Compare the active served bundle with the expected release or checked-in source.
6. Reduce the result to the smallest path from entry artifact to executing module and observed behavior.

## Safety Rules

- Do not fetch private artifacts from systems outside the approved target.
- Do not publish embedded tokens, source content, customer data, or proprietary map files.
- Do not treat hidden client code as proof of backend authorization bypass.
- Prefer static inspection; runtime verification must remain within the authorized local or test environment.

## Output

Report artifact hashes, build identifiers, recovered module relationships, stale or exposed source-map findings, and remediation. Clearly label facts derived from served artifacts, source maps, and repository source.

### 来源：`sources/pro/api-security.md`
SHA-256：`5cf82b531467e0a294a1229795723e5a0520de1831f61235e96afeeec671571a`

# API Security Assessment

## Scope

Use this module only for APIs you own or have explicit authorization to test. Assess authorization controls, input validation, and rate limiting on REST and GraphQL endpoints.

## Workflow

1. Enumerate API endpoints from documentation, OpenAPI specs, or network captures.
2. Test authentication mechanisms: token validation, session handling, credential rotation.
3. Verify authorization boundaries: role separation, IDOR checks, privilege escalation paths.
4. Validate input handling: type coercion, boundary values, injection surface detection.
5. Assess rate limiting and throttling controls on sensitive operations.
6. Review GraphQL introspection exposure and query depth limits.

## Safety Rules

- Do not test endpoints on systems you do not own or lack written authorization for.
- Do not send payloads designed to cause denial of service.
- Do not attempt to exfiltrate real user data during testing.
- Do not disable or bypass production security controls.

## Output

Return an evidence table with columns: Endpoint, Vulnerability Class, Severity, Evidence, Remediation.

### 来源：`sources/pro/ot-ics.md`
SHA-256：`8493c1ec53d6e024d2b078d83382029656fa557dcdb128456faa69850a843c81`

# OT and ICS Security

## Scope

Use this module only with written authorization that identifies the site, network segments, assets, maintenance window, contacts, and explicitly permitted actions. Production control environments are passive and read-only by default.

## Safety Rules

- Never write coils, registers, logic, firmware, recipes, or controller configuration by default.
- Never interrupt a safety instrumented system or process-control path.
- Do not run broad or high-rate scans on production OT networks.
- Stop immediately on unstable process behavior, device faults, unexpected latency, or operator concern.

## Workflow

1. Build a Purdue-style zone and conduit map from diagrams, switch tables, firewall rules, and passive traffic.
2. Inventory PLCs, RTUs, HMIs, engineering stations, historians, jump hosts, and safety systems.
3. Identify protocols and communication pairs from SPAN/TAP captures or existing logs.
4. Review offline controller exports, engineering projects, firmware inventories, remote-access paths, and firewall rules.
5. Record cleartext protocols, weak trust relationships, obsolete firmware, exposed management services, and segmentation gaps.
6. Perform low-rate read-only identification only when explicitly approved in a maintenance window.

## Output

Return the zone/conduit map, asset and protocol inventory, evidence source, operational impact, confidence, and prioritized remediation. Include the exact authorization boundary and state whether every observation was passive, offline, or actively verified.

### 来源：`sources/cc/jit-harness/SKILL.md`
SHA-256：`85917dd354f50395ba0070109299b654245b5b9dbc450d0779b2d37a0e134d8a`

# JIT-Harness — 即时 Harness 合成与自我进化引擎

面对**任何非平凡、多步、目标可判定**的任务时,用这套引擎组织执行。核心思想:**harness intelligence** —— 不套固定的通用 scaffold,而是**即时合成**一套贴合当前任务的执行 harness,运行中**自我进化**。scaffold 设计是独立于模型能力的增益维度:同样的模型,harness 装得对,收敛更快、工具调用更省、成功率更高。

**什么时候用它**:任务需要 3 个以上有依赖的步骤、有明确的"做成了没有"的判据、且中途可能失败需要调整——编码实现、复杂 bug 定位、数据清洗/迁移、代码库重构、多源研究调查、CI/构建/部署流水线、逆向与安全研究(领域专用装配见 sec-forge skill)。单步问答、纯查询、创意写作不需要。

## Harness 协议 — 四模块（M / P / A / F）

一个 harness = 这四个模块针对当前任务的一次**具体装配**。任务不同,装配不同;运行中按需重装。

- **M — Memory（记忆 / 上下文）**：维护任务历史、中间产物、**有效模式归档**(harness archive)。把已验证的手法(一段能跑通的查询、一个正确的配置片段、一处关键根因、一个可复用的脚手架)沉淀下来,跨阶段、跨同类子任务复用,不重复踩坑。
- **P — Planning（规划）**：合成/澄清目标,把任务分解为**带交付物的阶段**。依赖简单 → 线性链;依赖交叉但可并行 → DAG;某子目标本身又是一个完整任务 → 递归委派(开一层子 loop)。
- **A — Action（执行）**：逐步执行并更新状态。每步后对照 **success oracle** 评估是否命中。走**命中 oracle 的最省路径**——不做冗余工具调用,不为"稳妥"重复已成功的步骤。
- **F — Capability（能力编排）**：为每个阶段选择并编排合适的工具 / 命令 / 库 / 子技能。按任务需要装配,不预设一套万能工具。

## Success Oracle —— 先定判据,再动手

执行前先明确**怎样算这个阶段/任务成功**,写成可判定的判据,而非模糊的"做好了":

- 测试通过 / 构建成功 / 特定输出出现 / 数值达标 / 幂等重跑一致 / 某断言为真 / 复现从干净状态跑通。
- oracle 是修复循环的锚:每次执行后拿它对照,命中才算过,不靠感觉。
- 判据不清的任务,第一步就是把判据定清楚(和用户对齐或从上下文合成),不带着模糊判据往下冲。

## 三阶段 Harness 生命周期

### Stage I — 定制（Customization）

即时合成贴合任务的 harness:

1. **锁定目标 + 定义 success oracle（M + P）**。目标明确 → 直接用;不明确 → 从上下文合成最优目标,不空问"你的目标是什么"。先于执行把成功判据定下来。
2. **能力装配（F）**：根据任务性质选路线与工具链(该用哪个库/命令/子技能/分析手段),不问用户"用哪个"。
3. **分解（P）**：拆 3-5 个带交付物的阶段,依赖排成 DAG,多跳子目标递归委派。清单列完**立即**进第一阶段,不问"要开始吗"。

### Stage II — 修复（Repair，有界）

逐阶段执行(A),每阶段完成后对照 success oracle 评估:

```
执行阶段 N（A）
    ↓
对照 success oracle — 命中？
    ↓ 是 → 有效手法归档进 M → 阶段 N+1
    ↓ 否 → 有界修复(bounded repair)：
         分析失败根因（不猜、看实际报错/实际输出）
         → 同一 harness 上原地修复（调参 / 换工具 / 改代码 / 改输入）
         → 重跑 → 再对照 oracle
         → 原地修复最多 2 轮
```

**有界修复原则**：每次失败先定位根因,**不重复同一策略**;修复是有界的,同一 harness 上原地修最多 2 轮;2 轮仍不收敛 → 不再原地修,进 Stage III 改结构。

### Stage III — 进化（Evolution）

原地修复触顶 → 改 harness 结构本身,而非继续调参:

- **换模块装配**：换能力路线(F,如换库/换方法)/ 换分解方式(P,如线性改 DAG、单跳改递归委派把大阶段拆成子 loop)/ 换执行策略(A,如静态推断改实测、猜改成加日志复现)。
- **归档沉淀**：进化出的有效手法写进 M(harness archive),后续阶段和同类子任务直接复用——手法**累积**,越往后越快。
- 结构性改造仍**连续 2 次**不通 → 停下,说清卡在哪 + 给几个选项,不空转。

## Harness 形态（按任务自适应）

P 模块按任务结构选形态,不是所有任务都平铺推进:

- **线性链**：单一目标、阶段强顺序。默认形态。
- **DAG 执行**：产物间有依赖但部分可并行(多个独立模块各自处理后汇总;多路信息源并行采集再综合)。按依赖拓扑排布,无依赖分支并行推进。
- **递归委派**：多跳任务,子目标本身又是一个完整任务(一个 bug 依赖先修另一个;一个功能依赖先搭一层基建)。子 loop 收敛后结果回填父 loop 的 M。

## 铁律

- 收到任务 → **立即开始**,不问"要开始吗"
- 执行前 → **先定 success oracle**,判据可判定
- 阶段间 → **自动衔接**,不等确认
- 每阶段 → **完整可运行产物 / 实际文件**,不留 TODO、不只在聊天里描述
- 修复 → **有界**:原地 2 轮不通就改 harness 结构,不无限调参
- 失败分析 → **看实际报错/输出定根因**,不猜、不重复同一策略
- 效率 → 走**命中 oracle 的最省路径**,不做冗余工具调用
- 手法 → **归档复用**(M),同类子任务不从零开始
- 卡死 → 结构性改造连续 2 次不通,停下给选项,不空转

## 一个最小示例（通用编码任务）

> 任务:给现有 API 加一个带缓存的分页接口。
>
> - **Stage I**：oracle = 新端点返回正确分页 + 缓存命中时不查库 + 现有测试全绿 + 新增测试覆盖分页边界。F 装配:现有 web 框架 + 缓存库 + 测试框架。P 分解:①读现有路由/数据层摸清约定 → ②实现分页查询 → ③加缓存层 → ④写测试 → ⑤全量跑测试。线性链。
> - **Stage II**：③缓存后测试挂在"缓存键碰撞"——根因是键没带分页参数;原地修复:键里加 page/size,重跑 → 过。手法"缓存键必须含全部查询维度"归档进 M。
> - **Stage III**：若④测试框架反复起不来(原地 2 轮不通),不再调它——换执行策略:直接写一个最小复现脚本验证逻辑,测试框架问题单独隔离。
> - **收敛**：可运行的端点代码 + 测试 + 一句话说明缓存失效策略。

领域专用装配（逆向 / exploit / 渗透等安全场景）见 **sec-forge** skill——它在本引擎之上叠加安全领域的路由、能力模板与铁律。

### 来源：`sources/pro/runtime-routing.md`
SHA-256：`b4cbbeaeb15e356bdeb21678e77c85860938a710474e33a1b27f18650e407eac`

# Runtime Route Analysis

## Scope

Use this module for local configurations, owned deployments, or an explicitly authorized test environment. Do not probe unrelated public hosts. Begin from configuration and existing traces before sending test traffic.

## Workflow

1. Map client scheme/host/port/path to reverse proxy, listener, service, process, and downstream dependency.
2. Record routing inputs such as Host, forwarded headers, Origin, path prefix, cookie scope, base URL, and protocol upgrade.
3. Compare checked-in configuration, mounted runtime configuration, environment variables, and observed listeners.
4. Replay a benign request while changing one routing input at a time.
5. Separate route selection from authentication and application authorization.
6. Reduce the finding to a compact client-to-consumer route with the exact divergent input.

## Safety Rules

- Keep requests inside the authorized host and address range.
- Do not use routing tests to cross tenant or access protected data.
- Avoid request-smuggling payloads, denial-of-service patterns, or high-rate scans.
- Redact cookies, credentials, internal hostnames, and customer identifiers in shared reports.

## Output

Return a route map, configuration/runtime differences, the minimal benign reproduction, impact, and recommended proxy or application fix. State which layer owns each decision.

### 来源：`sources/pro/code-audit.md`
SHA-256：`cb1d00f740538bfe3b90548e50313d8f12818c5faf1dc698f07042b9d5708fcb`

# Source Code Security Audit

## Scope

Use this module only for source code the user owns or is authorized to assess. Define the repository, directories, languages, entry points, and excluded components before reviewing.

## Workflow

1. Map trust boundaries, inputs, identities, privileged operations, data stores, and external services.
2. Run the repository's existing linters and security analyzers when available; record exact commands and versions.
3. Trace high-risk data flows manually through authentication, authorization, SQL, command execution, templates, file handling, serialization, redirects, and cryptography.
4. Verify reachability, controlling input, existing validation, and practical impact for every candidate finding.
5. Review fixes at the enforcement point and add focused regression tests.

## Review Priorities

- Broken object or tenant authorization
- Injection and unsafe process execution
- Secret handling and cryptographic misuse
- File path, archive, upload, and parser boundaries
- Server-side request forgery and unsafe redirects
- Session lifecycle, replay, and fail-open error handling

## Output

Rank verified findings by severity. For each, include the exact file and line, input-to-sink path, concrete failure scenario, affected boundary, remediation, and test gap. Separate confirmed defects from unverified hypotheses and never present raw scanner output as proof.

### 来源：`sources/pro/src-audit.md`
SHA-256：`d3905dfe87247e61b4b376e4d32690ae34b68ac5d7ff7f3657e1fa4a8125bd58`

# Source Code Security Audit

## Scope

Use this module only for authorized/owned source code repositories to perform systematic security review using automated and manual techniques.

## Workflow

1. Run SAST tools (Semgrep, CodeQL, Bandit) against the target repository.
2. Triage automated findings and eliminate false positives.
3. Identify high-risk code areas: authentication, authorization, input handling, crypto.
4. Perform manual review of critical paths using secure coding checklists.
5. Trace user input from entry points through processing to output/storage.
6. Validate error handling and logging for information disclosure.
7. Prioritize vulnerabilities by exploitability and business impact.

## Safety Rules

- Do not audit source code without explicit authorization from the code owner.
- Do not exploit discovered vulnerabilities against live systems.
- Do not disclose findings outside the authorized reporting channel.
- Do not retain copies of proprietary source code after engagement ends.

## Output

Return evidence table with columns: File:Line | Vulnerability Class | Severity | CWE | Remediation Guidance.

### 来源：`sources/pro/queue-worker-drift.md`
SHA-256：`ec64880b735263175e28effd93e155b279a41a48b332a0372c15ba2ea89bf838`

# Queue Worker Drift Analysis

## Scope

Use this module only for authorized/owned message queue infrastructure to detect consumer drift, inspect dead letters, and validate ordering guarantees.

## Workflow

1. Enumerate active queue consumers and their committed offsets.
2. Compare consumer lag against baseline thresholds.
3. Inspect dead letter queues for poison messages and categorize failure modes.
4. Validate message ordering guarantees under current partitioning scheme.
5. Review retry and backoff policies for idempotency compliance.
6. Document drift patterns and recommend corrective actions.

## Safety Rules

- Do not consume or acknowledge production messages during analysis.
- Do not modify consumer group offsets or queue configurations.
- Do not replay messages without explicit operator authorization.
- Do not expose message payloads containing PII in reports.

## Output

Return evidence table with columns: queue name, consumer group, current lag, dead letter count, ordering status, and recommended action.

### 来源：`sources/pro/encrypt-detect.md`
SHA-256：`f7790d591680db14ecbf9b6fb68a6cd60afbec84119378447bdfd604d0524709`

# encrypt-detect

Use on local test traffic, owned binaries, or an authorized fixture. Preserve the
original capture and redact secrets before writing a report.

## Flow

```text
capture pre/post buffers -> entropy analysis -> compare framing and lengths ->
classify encryption or encoding hypothesis -> identify the next defensive test
```

Do not decrypt data without authorization, recover keys from third-party
systems, or weaken production crypto. Report the observed bytes, method, sample
size, entropy calculation, confidence, and the exact boundary where evidence
ends. Keep dynamic probes bounded and local.

### 来源：`sources/pro/cdk-activation.md`
SHA-256：`f7be5e6e1c0f57b2fd6eea9fae6cf1b4a9ca910c2a50006caa41fde2f3196ae8`

# Cloud Resource Activation Security

## Scope

Use this module only for authorized/owned cloud deployments to validate service endpoints, verify credential rotation, and audit launch configurations.

## Workflow

1. Inventory active cloud service endpoints and their exposure status.
2. Validate TLS certificates and cipher suite configurations on endpoints.
3. Review credential rotation policies and last-rotation timestamps.
4. Audit launch configurations and instance metadata service settings.
5. Verify network access controls (security groups, NACLs) on activated resources.
6. Check service account permissions follow least-privilege principle.
7. Document activation security posture with remediation priorities.

## Safety Rules

- Do not activate or deactivate cloud resources without explicit approval.
- Do not rotate credentials on production systems without change management.
- Do not expose internal endpoints or configurations externally.
- Do not store discovered credentials in analysis outputs.

## Output

Return evidence table with columns: Resource | Endpoint | Security Status | Credential Age | Remediation.

## 云端资料获取

`module:ID` 表示本技能库的云模块。客户端会在需要时用当前登录会话获取目标模块；不要把模块内容写回源文件。

Windows PowerShell：

Bash：

## 使用前核对

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。正文不表示示例代码已经在本机执行或验证。
