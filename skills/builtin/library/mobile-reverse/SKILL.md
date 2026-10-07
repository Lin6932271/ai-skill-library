---
name: mobile-reverse
description: "Use for Android or iOS application reverse engineering and security testing, including APK or IPA analysis, runtime instrumentation, SSL pinning, and platform protection checks."
---

# Mobile Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

2. `NOW`: confirm whether the current task falls within this skill's applicable scope
3. `NEXT`: read `../tool-index.md`, verify tool availability and actual paths
4. `NEXT`: when a tool is missing, invoke bootstrap; do not guess paths
5. `ACT`: enter step 1 of the "Workflow" and execute; do not stop at a confirmation state

> Unified Android + iOS reversing methodology
> Frida / Objection / OWASP MSTG / SSL Pinning Bypass

## Applicable scenarios

- Android APK reversing and security testing
- iOS IPA reversing and security testing
- Mobile-app runtime dynamic instrumentation
- SSL Pinning / root detection / jailbreak detection bypass
- Mobile-side crypto algorithm extraction (AES/RSA/HMAC keys)
- Mobile-app penetration testing (OWASP MASTG)
- App testing in a non-rooted/non-jailbroken environment

## Four-phase workflow

### Phase 1: Information gathering

```text
Android:
□ APK acquisition (Google Play / APKMirror / adb pull)
□ Manifest analysis: permissions, exported components, Intent Filter, backup flag
□ androguard: androguard analyze APK → components/permissions/signature
□ APKLeaks: scan for hardcoded API Key / Token / Secret
□ Hardening detection: is it packed (360/Tencent/Bangbang/Ijiami)

iOS:
□ IPA acquisition (App Store / ipatool / Apple Configurator)
□ Decrypt the App Store binary: frida-ios-dump / Clutch
□ Info.plist analysis: ATS config, URL Scheme, Queries Schemes
□ class-dump: export ObjC class structure
□ Hardening detection: is Swift/ObjC obfuscation used
```

### Phase 2: Static analysis

```text
Cross-platform:
□ JADX-GUI: APK → Java source (Android)
□ Ghidra / Hopper: .so / Mach-O decompilation
□ radare2 / Cutter: CLI quick recon

Android-specific:
□ apktool d app.apk → smali code + resources
□ dex2jar: DEX → JAR → JD-GUI
□ smali/baksmali: Dalvik bytecode modification

iOS-specific:
□ class-dump: export ObjC headers
□ Swift symbol recovery: swift-demangle
□ dsymutil: debug symbol extraction
□ otool -L: view dynamic-library dependencies
□ jtool2: Mach-O analysis
```

### Phase 3: Dynamic analysis

```text
Frida — general dynamic instrumentation:
□ frida-ps -U: list device processes
□ frida-trace -U -i "open*" com.app: trace function calls
□ Custom Hook script: modify args/return values, call private methods

Objection — Frida enhancement layer (no scripting needed):
□ objection -g "com.app" explore
□ android root disable / ios jailbreak disable
□ android sslpinning disable / ios sslpinning disable
□ android keystore list / ios keychain dump
□ env / ls / sqlite connect

Frida Gadget (no root/jailbreak):
□ Inject frida-gadget.so / FridaGadget.dylib into APK/IPA
□ Re-sign → install → Hook without device privileges
□ objection patchapk --source app.apk (fully automatic)
```

### Phase 4: Network analysis

```text
□ Burp Suite: intercept HTTP/HTTPS, modify requests/responses
□ mitmproxy: scriptable proxy (Python API)
□ Wireshark: PCAP capture analysis
□ Certificate install: Android user cert → system cert (Magisk + MoveCert)
□ SSL Pinning bypass: Frida/Objection/Xposed/SSL Kill Switch 2
□ WebSocket / gRPC traffic analysis
```

## Common bypass quick reference

### SSL Pinning

```bash
# Objection（最简）
objection -g "com.app" explore
android sslpinning disable

# Frida 通用脚本
frida -U -l ssl_pinning_bypass.js -f com.app

# Xposed（Android）
TrustMeAlready 模块 → 全局禁用证书校验
```

### Root / jailbreak detection

```bash
# Objection
android root disable
ios jailbreak disable

# Frida 自定义（多层检测）
Java.perform(function() {
    var RootBeer = Java.use("com.scottyab.rootbeer.RootBeer");
    RootBeer.isRooted.implementation = function() { return false; };
    // 额外绕过: Magisk su 检测、frida-server 检测、/proc/self/maps 检测
});
```

### Anti-debug

```bash
# Android
frida -U -l anti_debug_bypass.js -f com.app
# 绕过: ptrace(TracerPid)、/proc/self/status、isDebuggerConnected()

# iOS
# 绕过: PT_DENY_ATTACH、sysctl CTL_KERN/KERN_PROC/KERN_PROC_PID
frida -U -l ios_anti_debug.js -f com.app
```

## Mobile-side crypto extraction

```javascript
// Android — Hook Cipher.getInstance 获取密钥+算法
Java.perform(function() {
    var Cipher = Java.use("javax.crypto.Cipher");
    Cipher.getInstance.overload('java.lang.String').implementation = function(algo) {
        console.log("[Cipher] Algorithm: " + algo);
        return this.getInstance(algo);
    };
    Cipher.init.overload('int', 'java.security.Key').implementation = function(mode, key) {
        console.log("[Cipher] Key: " + bytesToHex(key.getEncoded()));
        return this.init(mode, key);
    };
});

// iOS — Hook CCCrypt
Interceptor.attach(Module.findExportByName("libcommonCrypto.dylib", "CCCrypt"), {
    onEnter: function(args) {
        console.log("CCCrypt op: " + args[0] + " alg: " + args[1]);
        console.log("Key: " + hexdump(args[3], { length: args[4].toInt32() }));
    }
});
```

## Toolchain

| Tool | Platform | Purpose |
|------|:--:|------|
| JADX-GUI | A | Java decompilation |
| apktool | A | APK unpack/rebuild |
| Ghidra | A+I | Multi-architecture decompilation |
| Hopper | I | iOS-specific disassembly |
| Frida | A+I | Dynamic instrumentation |
| Objection | A+I | Frida REPL enhancement |
| MobSF | A+I | Automated SAST+DAST |
| class-dump | I | ObjC class export |
| frida-ios-dump | I | IPA decryption |
| jtool2 | I | Mach-O analysis |
| Burp Suite | A+I | HTTP interception |
| mitmproxy | A+I | Scriptable proxy |

> A=Android, I=iOS

## References

- `references/frida-objection-deep.md` — deep Frida + Objection usage
- `references/ios-reverse-guide.md` — iOS reversing specifics
- `references/anti-detection-bypass.md` — root/jailbreak/anti-debug/SSL Pinning bypass

## Task-completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step in the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items required by RULES?

<!-- skill-trace:da0f3edbea0787205e40df3277ceb6a8 -->
