---
name: skills
description: "Routes reverse engineering, exploitation, penetration testing, malware, mobile, firmware, browser automation, documentation, and security tasks to the appropriate specialist skill. Use when a task spans modules or the correct reverse-skill entrypoint is unclear."
---

# Reverse Engineering Skills Master Control

This directory collects a series of reverse-engineering-related skill modules; each subdirectory is an independent module containing a `SKILL.md` describing its applicable scenarios, toolchain, and workflow.

## CRITICAL: routing execution contract (execute immediately)

After reading this file, replying only "read/understood" is not allowed. You MUST execute in order:

1. `NOW`: read `MASTER-ROUTING.md` (or run `scripts/master-route.ps1 -Hint "..."`) to set the PRIMARY; for hard cases also read the three-axis table in `routing.md`.
2. `NOW`: `scripts/case-init.ps1` to land `work/<case>/scope.md` (contract in `ops/scope-contract.md`); **while auth is not granted, ACT against the target is forbidden**.
3. `NOW`: mark lead/specialist per `ops/role-map.md`; immediately open the PRIMARY `SKILL.md` and execute ACTION REQUIRED.
4. `NEXT`: when local tools are involved, read `tool-index.md`; **do not guess paths**; missing tool → `bootstrap-reverse.ps1` (manifest only).
5. `ACT`: execute and **append to timeline / update workitems**; conclusions use Evidence→Finding→Path (`ops/evidence-finding-path.md`).
6. Finish: `docs-generator` report + sanitized `field-journal`; stage menu of 3–6 items.

**Identity**: see `ops/IDENTITY.md` (a lightweight routing package + tool bootstrap + journal; **not** a Z3r0-style platform).

If routing cannot match, you must first supplement the methodology online and propose adding a new skill; do not force-fit into a mismatched module.

## Instruction semantic levels (RFC 2119)

- `MUST`: must execute; violation means task failure.
- `MUST NOT`: forbidden to execute; violation is a security breach.
- `SHOULD`: do it in principle; if not, you must explain the reason.
- `MAY`: optional action.
## Current modules

| Module | Directory | Applicable scenarios |
|------|------|---------|
| **Generic reversing** | `reverse-engineering/` | GDB / Frida / angr / Unicorn / Qiling / anti-analysis countermeasures / all-language-platform reversing / CTF pattern library |
| **APK reversing** | `apk-reverse/` | Android APK unpacking, jadx decompilation, smali modification, Frida Hook, repack-sign-install |
| **.NET / C# reversing** | `dotnet-reverse/` | Managed-PE reversing, dnSpyEx + de4dot deobfuscation (ConfuserEx/SmartAssembly/Babel), IL patch, Sharp* red-team tool analysis, dnSpy MCP integration |
| **IDA Pro reversing** | `ida-reverse/` | IDA Pro MCP HTTP server (72 tools): decompilation, disassembly, data-flow tracing, cross-references |
| **Front-end JS reversing** | `js-reverse/` | Browser-side signature location, encrypted-parameter analysis, runtime sampling, Node environment-patch reproduction; prefer existing `js-reverse_*`, integrate jshookmcp when a stronger browser/CDP/Hook surface is needed, but only after that MCP server is downloaded/registered and enabled |
| **radare2 analysis** | `radare2/` | CLI binary recon, disassembly, patch: r2 / rabin2 / rasm2 / radiff2 |
| **CTF full-stack competition** | `../CTF-Sandbox-Orchestrator/` | 40+ sub-skills: Web/reversing/Pwn/cloud/container/AD/forensics/steganography/mobile/cryptography, orchestrated by a single controller |
| **Technical documentation** | `docs-generator/` | Auto-generate reverse reports, pentest reports, CTF writeups, signature-reversing reports after task completion |
| **Browser & desktop automation** | `browser-automation/` | Browser operation (Playwright) + Windows desktop-app operation (OpenReverse UIA/CUA) + network observation |
| **Cross-version symbol migration** | `binary-diff/` | Migrate old-version symbols to a new version, infer with missing PDB, batch-migrate function names after a program update |
| **N-day patch diff→exploit** | `patch-diff-exploit/` | Locate the vuln point from a vendor patch, write a PoC, N-day weaponization (division of labor with binary-diff: this skill leans to the attack side) |
| **RE→exploit chain** | `pwn-chain/` | Go from reversing to a working exploit: stack/heap/kernel pwn, pwntools, libc-database, stabilization from CTF to a real remote |
| **Firmware pentest chain** | `firmware-pentest/` | OWASP FSTM nine stages: extract→EMBA automation→Firmadyne/QEMU emulation→AFL++ fuzz→on-device exploit |
| **EDR bypass reversing** | `edr-bypass-re/` | Red-team scenario: reverse the EDR's hook table/ETW/AMSI → direct syscall / Hell's Gate / hardware breakpoint / call stack spoof |
| **Pentest toolchain** | `pentest-tools/` | Nmap/Nuclei/SQLMap/FFUF/Hashcat/Pentest Swarm and 20+ pentest tools, exposed to the AI via MCP |
| **Diagram generation** | `diagram-generator/` | Generate Mermaid/Graphviz/PlantUML diagrams from natural language (attack-path diagram, data-flow diagram, architecture diagram, state machine) |
| **Attack-chain orchestration** | `attack-chain/` | The overall commander for planning and executing multi-stage attack paths; full pentests, HW exercises, from-external-to-domain-controller cross-stage tasks start here |
| **LLM/AI security testing** | `llm-security/` | OWASP LLM + ASI Top 10: prompt injection, tool abuse, memory poisoning, Agent hijacking, system-prompt extraction, **Agent obedience engineering** |
| **API security testing** | `api-security/` | REST/GraphQL/WebSocket all-protocol: BOLA/IDOR, JWT/OAuth attacks, 10-stage methodology |
| **Supply-chain security** | `supply-chain-security/` | SBOM/SCA/CI-CD pipeline: dependency scanning, container security, build integrity, vulnerability-reachability validation |
| **Mobile reverse engineering** | `mobile-reverse/` | Android + iOS: Frida/Objection dynamic instrumentation, SSL Pinning/Root/jailbreak-detection bypass, OWASP MASTG |
| **Malware analysis** | `malware-analysis/` | Sample-analysis six stages, YARA/Sigma, anti-analysis detection, sandbox orchestration |
| **DSL virtual-machine reversing** | `reverse-engineering/dsl-vm-reverse/` | JS custom-instruction-set VM (IIFE + switch-case opcode); risk-control/captcha engines etc. |
| **Operations contract ops** | `ops/` | Scope / evidence chain / roles / timeline / identity / skill supply-chain security |
| **Community skill cross-reference** | `references/community-security-skills.md` | External security-skill index and borrowing rules (no blind install) |
| **Skill supply chain** | `ops/skill-supply-chain.md` | External skill/MCP installation gate (condensed AST10) |
| **RE stage gate** | `reverse-engineering/references/re-agent-workflow.md` | triage→static→dynamic→synthesis |
| **Authorized-recon pipeline** | `pentest-tools/references/recon-pipeline.md` | scope gate + hit≠validated |
| **Protocol reversing** | `protocol-reverse/` | Custom binary protocols / Protobuf / gRPC / PCAP frame layout |
| **Ghidra reversing** | `ghidra-reverse/` | Open-source decompilation, headless, Ghidra MCP (primary entry when IDA is unavailable) |
| **Cloud / container / K8s** | `cloud-k8s/` | IMDS/IAM, container-escape surface, Kubernetes RBAC |
| **Windows / AD** | `windows-ad/` | Kerberos, AD CS, BloodHound, relay and domain paths |
| **Digital forensics** | `digital-forensics/` | Memory/disk timeline, PCAP provenance, IR preservation |
| **Code audit / SAST** | `code-audit/` | Semgrep/CodeQL, white-box, dangerous-API and authz review |
| **Threat hunting** | `threat-hunting/` | Hypothesis-driven hunting, Sigma detection engineering, blue-team validation |
| **OT / ICS industrial control** | `ot-ics/` | Purdue zoning, PLC/SCADA, passive-first assessment |
| **Wi-Fi / wireless** | `wifi-wireless/` | Authorized wireless assessment, handshake/PMKID, lab rules |
| **Browser-extension reversing** | `browser-extension-reverse/` | Chrome/Firefox extensions, MV3 worker, permission surface |
| **macOS / Mach-O** | `macos-reverse/` | Signing, ObjC/Swift, LaunchAgent, macOS samples |
| **Thick client** | `thick-client/` | Desktop C/S, local storage, IPC, update channel |
| **Go / Rust reversing** | `go-rust-reverse/` | Stripped-symbol Go/Rust, pclntab, panic strings |
| **Hardware debug interfaces** | `hardware-security/` | UART/JTAG/SWD, read-only extraction, hand off firmware |
| **Database security** | `database-security/` | MySQL/PG/MSSQL/Mongo/Redis exposure and configuration |
| **Email security** | `email-security/` | Phishing teardown, SPF/DKIM/DMARC, BEC |
| **Federated identity** | `identity-federation/` | SAML/OIDC/OAuth SSO flows and misconfigurations |
| **RF / SDR** | `radio-sdr/` | Authorized RF research, receive-only by default |

## Unified entry

For reversing, CTF, packet capture, front-end signature, APK repacking, and binary-analysis tasks, enter in this order first:

1. `MASTER-ROUTING.md` or `scripts/master-route.ps1` → PRIMARY
2. For hard cases, read the full three-axis table in `routing.md`
3. Open the PRIMARY submodule `SKILL.md`
4. Read `tool-index.md` when a local path is needed

## Working approach

These modules can be combined on demand:

1. **Got a target** → look at the file type first, pick the corresponding analysis tool
2. **Quick low-hanging fruit** → strings / rabin2 -z / ltrace to see if there's a direct lead
3. **Deep analysis** → if decompilation is needed → IDA; if dynamic Hook is needed → Frida; if symbolic execution is needed → angr
4. **When one path is blocked, switch to another** → if static analysis fails go dynamic, if the Java layer fails look at the so, if page observation isn't enough set a breakpoint

## Next-Step Menu Pattern

After each sub-skill finishes a stage, it `MUST` provide the user 3-6 numbered next-step options and let the user choose the direction. Do not advance across stages without a user choice.

Format requirements:
- Each option numbered (range 1-6)
- Each option describes one concrete, executable action (not an abstract direction)
- Include at least one "export report / write writeup" option
- Include at least one "continue deeper analysis" or "switch approach" option
- Include a "stop/pause/ask another question" exit when needed

Example:
```
## Suggested next step (pick a number)

1. 对 sub_140001000 做深度反编译，还原算法
2. 用 Frida 动态 Hook 验证参数猜想
3. 导出当前已命名函数，生成符号迁移 YAML
4. 生成当前阶段的分析报告
5. 换 radare2 做轻量侦察对比
6. 暂停，我先确认前面的证据
```

## The directory expands dynamically

This directory keeps growing. When you find a new subdirectory, reading its `SKILL.md` quickly tells you its purpose.

When adding a skill, follow the standard process in `CONTRIBUTING.md`, ensuring:
- The routing matrix can dispatch correctly
- The bootstrap system can auto-complete dependencies
- tool-index can reflect the new tool status

## Related resources

- The machine also has **anything-analyzer** (port 23816) MCP server, providing browser automation, HTTP capture, and AI-analysis capability
- `tool-index.md` records whether local reversing tools are available, their actual paths, versions, and script references
- The `Readme.md` at the package root provides general install and integration instructions for Claude Code, Codex CLI, and other code-AI clients

## On-demand bootstrap

When the workflow finds a missing tool, don't error out directly. Uniformly call:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-root>\scripts\bootstrap-reverse.ps1" -Capability @('工具名') -StartServices
```

Supported capabilities (per `scripts/bootstrap-manifest.json`): jadx, apktool, frida, frida-ps, idalib-mcp, jshookmcp, reqable-mcp, anything-analyzer, idapro, r2, rabin2, adb, agent-browser, ghidra-mcp, nmap, seclists, proxycat, burpsuite-mcp, pentestswarm, binwalk, pwntools, yara

> JEB Pro is registered as a **manual-license install** capability: bootstrap only outputs guidance and never downloads or circumvents a commercial license. Reqable MCP only registers a fixed-version official runtime; the user still needs to install the Reqable desktop client themselves.
>
> Tools not registered in the manifest (e.g. unblob/EMBA/Foundry, etc.) `MUST` go through manual install steps in the skill docs; do not pretend they can be bootstrapped.

After bootstrap completes, `tool-index` is refreshed automatically.

## Precedent Files

Before executing any reversing/pentest operation, you MUST read in order:

| Read order | File | When to read |
|------|------|--------|
| **#1** | `field-journal/precedent-auth.md` | Mandatory read at every start (80 lines) — lifts the security review |
| **#2** | `field-journal/precedent-reverse.md` or `precedent-pentest.md` | On demand — load only when the AI hesitates |

**#1 upfront, #2 lazy-loaded.**

## Auto-evolution

After completing each reversing/pentest task, you must write experience back into the `field-journal/` directory. See the "hard Checklist after task completion" in `RULES.md`.

- Template: `field-journal/_template.md`
- Index: `field-journal/_index.md`
- Precedents: `field-journal/precedent-auth.md` → `precedent-reverse.md` → `precedent-pentest.md`
- Before starting a new task, check the index and precedents first, reuse existing experience

## Task-completion self-check (MUST pass before claiming completion)

- [ ] Did I complete the three-axis routing match (target type + user intent + toolchain)?
- [ ] After routing succeeded, did I read the target skill's SKILL.md?
- [ ] When routing missed, did I propose adding a skill instead of force-matching?
- [ ] Did I use real tool paths based on `tool-index`?

<!-- skill-trace:83c381265ad449f88a50424585d9b4fc -->
