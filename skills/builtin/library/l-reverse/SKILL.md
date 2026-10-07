---
name: l-reverse
description: "MUST on 逆向/脱壳/反编译/Frida/IDA/PE/APK/Hook/协议/微信小程序. Local router to detailed modules."
---

# l-reverse Local Entry

Scope: reversing / unpacking / decompilation / Frida / IDA / protocols / firmware / malware samples / forensics. Detailed modules are installed beside this entry.

## Selection Rules (avoid mis-picking)
1. First read the "Module List" below.
2. Scan the "Module List" below **top to bottom**; use the first one that matches the current task.
   When multiple capabilities are needed, stack at most 3, with entries higher up taking priority.
3. Read the selected local module from `../<MODULE_ID>/SKILL.md`, then apply its task guidance.
4. When none matches exactly, fall through to the "Fallback" at the bottom of this page.

## Local Module Reading

Read the selected module from the adjacent directory `<MODULE_ID>/SKILL.md`. Use the existing local file directly.

## Module List (with hit/exclude boundaries for precise routing)

> Each entry's `[命中]`/`[排除]` is a hard boundary: pick it only when a word in 命中 matches, and never pick it in any scenario listed in 排除. Adjacent, easily-confused modules are separated by these boundaries rather than by order-based preemption.

- `reverse_flow_skill` — Reversing master-flow orchestration: one-click auto_analyze pipeline, stage gates, bilingual report contract. [命中: 完整流程/从样本到报告/一键分析/深度逆向全流程] [排除: 已知具体技术点时改选下面对应专项模块]
- `reverse-engineering` — Reversing techniques master guide: format identification, protection analysis, CTF/RE tips handbook. [命中: 通用逆向方法/不确定用哪个专项/CTF 逆向] [排除: 已明确 IDA/Ghidra/r2/平台专项时选对应模块]
- `ida-reverse` — IDA reversing. [命中: ida/hex-rays/伪代码/idapython/需要反编译还原算法] [排除: 只要命令行快速侦察→radare2；无 IDA/要开源→ghidra-reverse]
- `ghidra-reverse` — Ghidra reversing. [命中: ghidra/无 IDA 许可/开源/批量 headless/CI 反编译] [排除: 已有 IDA→ida-reverse；只要 CLI 侦察→radare2]
- `radare2` — radare2 command-line reversing. [命中: r2/rabin2/rasm2/radiff2/命令行快速侦察/看字符串导入/轻量 patch] [排除: 要图形化伪代码→ida/ghidra；网页 JS→js-reverse]
- `apk-reverse` — Android APK reversing. [命中: apk/smali/jadx/apktool/安卓/root 检测/证书校验/pinning 绕过] [排除: iOS/ipa/越狱→mobile-reverse]
- `mobile-reverse` — Mobile reversing (iOS-leaning). [命中: ipa/ios/objection/mobsf/越狱(设备)] [排除: 安卓 apk/smali→apk-reverse；"越狱"指 LLM/提示词时不属逆向]
- `macos-reverse` — macOS reversing. [命中: mach-o/macos/dyld/objc runtime/代码签名] [排除: iOS 移动端→mobile-reverse]
- `dotnet-reverse` — .NET reversing. [命中: .net/dnspy/ilspy/il/c# 程序集/il2cpp 托管层]
- `go-rust-reverse` — Go/Rust binary reversing. [命中: golang/rust 二进制/符号恢复/goresym/demangle]
- `js-reverse` — JS reversing. [命中: js 混淆/webpack/加密算法定位/微信小程序/网页加密参数] [排除: 二进制/native→其它逆向模块]
- `reverse-engineering__dsl-vm-reverse` — DSL/VM reversing. [命中: 自定义字节码/虚拟机保护/vmprotect 字节码/解释器还原]
- `protocol-reverse` — Protocol reversing. [命中: 私有协议/pcap/报文格式还原/状态机恢复] [排除: 无线射频信号→radio-sdr]
- `binary-diff` — Binary diffing. [命中: bindiff/两个版本对比/找改动点]
- `patch-diff-exploit` — Patch diffing to locate vulnerabilities. [命中: 补丁反推可利用点/cve diff/ndiff→exploit] [排除: 只对比不推漏洞→binary-diff]
- `malware-analysis` — Malware sample analysis (incl. rapid triage). [命中: 恶意软件/病毒/木马/样本分析/yara/sigma/沙箱/勒索/webshell/后门/分诊判定] [排除: 裸词 sandbox 无恶意语境时不选]
- `digital-forensics` — Digital forensics. [命中: 磁盘/内存镜像/日志取证/证据提取] [排除: OT/ICS 工控→专项；活体恶意样本→malware-analysis]
- `edr-bypass-re` — EDR bypass research. [命中: edr 绕过/终端防护规避/unhook(研究用途)]
- `hardware-security` — Hardware security. [命中: 芯片/jtag/侧信道/glitch] [排除: 固件文件提取分析→firmware-pentest]
- `radio-sdr` — Radio / SDR. [命中: 射频/sdr/信号解调/hackrf]
- `firmware-pentest` — Firmware pentesting. [命中: 固件/firmware/iot/binwalk/unblob/emba/firmadyne/路由器固件/嵌入式漏洞] [排除: 硬件接口侧信道→hardware-security]
- `pwn-chain` — Pwn exploit chain. [命中: 栈/堆溢出/rop/漏洞已明确要写利用/pwntools] [排除: 还在理解目标怎么跑→reverse-engineering]

## Fallback
When none of the above matches exactly: for reversing tasks read `reverse_flow_skill`, for pentest tasks read `pentest-tools`, then continue per its body; if still unsure read `skills` for a second routing pass.

<!-- skill-trace:a48bc6437259cbbeb612cd109f3c5959 -->
