---
name: dotnet-reverse
description: ".NET / C# 二进制逆向。当目标是 .NET assembly（PE 头含 CLR、.exe/.dll 托管程序）、C# 编译产物（含 NativeAOT）、红队 Sharp* 工具（Rubeus / SharpHound / SharpHound 等）、.NET 混淆程序（ConfuserEx / SmartAssembly / Babel / Eazfuscator）、.NET loader / info-stealer / 套壳 malware 时使用。优先用 dnSpyEx + de4dot，需要 AI 直接操作时联动 dnSpy MCP。不用于纯 native 二进制（走 reverse-engineering / ida-reverse）。"
---

# .NET / C# reversing operations spec

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: use DIE/`file`/CLR header to confirm the target is .NET managed (otherwise SWITCH to `ida-reverse/` / `reverse-engineering/`)
2. `NOW`: if obfuscation is suspected → `de4dot` unpack first, produce `*-clean.exe`, keep the original sample
3. `NEXT`: dnSpyEx (or dnSpy MCP / `ilspycmd`) static: C# browsing + **IL view** for key decisions
4. `ACT`: dynamic debug when plaintext/C2 is needed; when changing logic, prefer **IL patch** over C# recompilation
5. At the end of a stage, give the user a 3–6 item next-step menu (including export report)

## Applicable scope

Prefer this skill when the task belongs to the following scenarios:

- Identify and reverse .NET / C# compilation products (managed PE / .exe / .dll)
- Analyze red-team Sharp* toolchains (Rubeus, SharpHound, SharpShell, etc.)
- Deobfuscate ConfuserEx / SmartAssembly / Babel / Eazfuscator / .NET Reactor, etc.
- Reverse the decryption and C2 logic of a .NET loader / info-stealer / RAT
- Patch a C# program (change a decision, change a constant, keygen)
- Analyze the pre-IL2CPP Mono/Unity managed layer (note: after IL2CPP compilation it's native, go to `reverse-engineering/` + seed-014)

If the target is a pure native binary (C/C++/Go/Rust compiled, no CLR), use `reverse-engineering/`, `ida-reverse/`, or `radare2/` instead.

## Core principles

- **Identify before you act**: first confirm it's a .NET managed program (PE header CLR + `#~` / `#Strings` streams + mscoree `_CorExeMain`), then decide to go dnSpy rather than IDA
- **IL over C#**: dnSpyEx's C# decompiler loses/distorts information (compiler-generated state machines, async/await, yield); key decisions and patches must switch to the **IL editor**; use the C# view only for quick browsing
- **de4dot first**: when facing an obfuscator, run one round of `de4dot` before static analysis, otherwise strings/control-flow are all garbled
- **MCP integration**: if dnSpy MCP is registered in the environment (`dnspy_*` tools), prefer the MCP surface for decompile / IL inspection to avoid switching GUI back and forth
- **Evidence-based output**: deobfuscation products, extracted config/C2/key, and patch diffs all land on disk

## Toolchain mapping

| Capability | Preferred | Note |
|------|------|------|
| Decompile + debug + patch | **dnSpyEx** | The trump card, the only GUI with an IL editor; old dnSpy is unmaintained, use the Ex fork |
| Lightweight CLI / headless decompilation | **ILSpy** (`ilspycmd`) | Good for batch, scripting, Linux/macOS |
| Deobfuscation | **de4dot** | The default solution for the ConfuserEx family, SmartAssembly, and other mainstream packers |
| Obfuscator identification | **Detect It Easy (DIE)** / **file** | Determine the packer type first, then decide de4dot parameters |
| Programmatic IL manipulation | **dnlib** | Write C# scripts to batch-edit metadata / string decryptors |
| AI direct operation | **dnSpy MCP** | `dnspy_decompile` / `dnspy_inspect_il` and other tool surfaces |

> Prerequisite: on a Windows host install dnSpyEx + de4dot (choco or release); on Linux/macOS use `ilspycmd` + `dotnet runtime`. See the install matrix in `references/sharp-tools.md`.

## Six-stage workflow

### 1. Identify (.NET identification)

Confirm the target is a managed program; don't analyze a native PE as .NET:

```powershell
# Windows
file target.exe                       # "PE32 executable ... for MS Windows" 不够
# 关键：看有没有 CLR
powershell -c "[System.Reflection.AssemblyName]::GetAssemblyName('target.exe')"
# 或
dnSpyEx 直接拖进去 —— 能打开就是托管

# 通用
strings target.exe | grep -iE "mscoree|_CorExeMain|mscorlib|System\\."
```

**.NET identification markers:**
- PE header `Data Directory[14]` (CLR Runtime Header) non-zero
- `mscoree.dll` import / `_CorExeMain` entry
- `#~`, `#Strings`, `#US`, `#GUID`, `#Blob` metadata streams
- `mscorlib` / `System.Private.CoreLib` strings

**NativeAOT exception:** compiled to native, no CLR header, but has `System.Private.CoreLib` strings and reconstructed type metadata — these go to `reverse-engineering/` (IDA/r2); this skill only does the identification hint.

### 2. Detect (detect the obfuscator)

```powershell
# DIE 快速识别
diec target.exe                        # Detect It Easy CLI
# 或拖进 dnSpyEx，看是否大量乱码类名 / 控制流变形
```

Common obfuscators → unpacking strategy (see `references/obfuscators.md`):

| Obfuscator | Signature | de4dot handling |
|--------|------|------------|
| ConfuserEx (1.0.0 / 2.x) | `<module>` anti-tamper, control-flow flattening, string encryption | `de4dot target.exe` usually auto-detects |
| SmartAssembly | `circular`/`string encoding`, resource compression | `de4dot target.exe` |
| Babel.NET | Method-body encryption, control flow | `de4dot target.exe` |
| Eazfuscator.NET | String/resource encryption | `de4dot`, some versions need manual work |
| .NET Reactor | anti-tamper + necrobit | `de4dot`, newer versions may fail and need manual work |

### 3. Deobfuscate

```powershell
# de4dot 默认自动识别大多数壳
de4dot target.exe -o target-clean.exe

# 指定类型（自动识别失败时）
de4dot --type cfze target.exe          # ConfuserEx
de4dot --type sa target.exe            # SmartAssembly

# 多层混淆 / de4dot 报 unknown
de4dot --detect target.exe             # 看它识别成什么
# 可能要先 patch anti-tamper 再 de4dot（见 references/obfuscators.md）
```

Output: `target-clean.exe`, use it for subsequent analysis. **Keep the original sample** for comparison.

### 4. Static Analyze

dnSpyEx loads the unpacked sample:

- **C# view**: quickly browse class structure, method signatures, strings (for locating)
- **IL view**: key decisions, encryption logic, state machines must be read in IL (right-click → Edit IL or IL view)
- Find the entry: `Main` / `Startup` / module initializer (`Module .cctor`)
- Find key logic: search `flag`, `password`, `verify`, `check`, `encrypt`, `http`, `Config`

```text
定位字符串 → 反向引用 → 找到使用它的方法 → IL 视图看判断逻辑
```

### 5. Dynamic (dynamic debugging)

dnSpyEx debugger: attach process / start debugging, set breakpoints in key methods, observe runtime:
- Decrypted plaintext strings (many obfuscators only decrypt strings at runtime)
- C2 address, config decryption result
- Exception-driven control flow (anti-debug often uses `try/catch` to hide the real path)

> .NET dynamic debugging is far friendlier than native — you can directly see object values and string contents. Prefer dynamic over grinding on static.

### 6. Patch (modify on demand)

```text
dnSpyEx → 右键方法 → Edit Method (C#) 或 Edit IL
  - 改判断：ldc.i4.0 → ldc.i4.1（false→true）
  - 改常量：直接编辑字符串/数字
  - 删除校验：nop 掉整段
File → Save Module → 替换原文件
```

**IL patch reliability > C# patch**: C# recompilation may fail (missing references, wrong syntax), IL editing hardly ever distorts. See `references/common-workflow.md`.

## Trigger-scenario routing

Enter this skill when the user says:
- ".NET / C# 二进制逆向" / "C# 程序反编译"
- "dnSpy 分析" / "dnSpyEx patch"
- "ConfuserEx / SmartAssembly / Babel 脱混淆 / 脱壳"
- "Sharp* 工具分析"（Rubeus / SharpHound / SharpShell）
- ".NET malware / loader / info-stealer 逆向"
- "C# 程序 patch / keygen / 修改判断"

## When to switch out

- IL2CPP-compiled Unity game → `reverse-engineering/` + `seed-014_unity-il2cpp-reverse.md` (IL2CPP is native, doesn't go through dnSpy)
- NativeAOT product → `reverse-engineering/` (same as above, native)
- Pure native PE (no CLR) → `reverse-engineering/` / `ida-reverse/`
- Need to batch-migrate symbols/functions to another version → `binary-diff/`
- Need to draw an attack-path / call-chain diagram → `diagram-generator/`

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Downstream exit**:
- IL2CPP / NativeAOT (native) → `reverse-engineering/`
- Deep native .so/.dll segment analysis → `ida-reverse/` / `radare2/`
- Need the AI to operate dnSpy directly → register and integrate dnSpy MCP (see `references/sharp-tools.md`)

**Peer-related modules**:
- `reverse-engineering/languages-compiled.md` (the .NET intro points to this module)
- `apk-reverse/` (Xamarin/MAUI Android reversing can switch back to this module for the C# layer)

## Reference docs

- [references/obfuscators.md](references/obfuscators.md) — ConfuserEx / SmartAssembly / Babel / Eazfuscator / .NET Reactor deobfuscation details + anti-tamper bypass
- [references/common-workflow.md](references/common-workflow.md) — full workflow, IL patch reliability, string-decryptor extraction, state-machine identification
- [references/sharp-tools.md](references/sharp-tools.md) — red-team Sharp* tool analysis, tool install matrix, dnSpy MCP integration, community resource index

## Task-completion self-check

- [ ] Did I confirm CLR / managed identity (or already SWITCH out of this skill)?
- [ ] Was the obfuscated sample de4dot'd / equivalently unpacked before deep analysis?
- [ ] Was key logic verified with the IL view (not just the C# pseudocode)?
- [ ] Are the products (clean sample / config / patch diff) on disk and reproducible?
- [ ] Did I provide a next-step menu or report exit?

<!-- skill-trace:a56c7e95f755123990ba44c5c3b6c248 -->
