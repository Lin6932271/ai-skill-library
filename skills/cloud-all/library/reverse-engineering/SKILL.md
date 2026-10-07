---
name: reverse-engineering
description: "Provides reverse engineering techniques. Use when the main job is to understand how a compiled, obfuscated, packed, or virtualized target works before exploiting or solving it, including binaries, APKs, WASM, firmware, custom VMs, bytecode, malware-like loaders, and anti-debug or anti-analysis logic. Do not use it when the vulnerability is already understood and the remaining task is exploitation; use pwn instead. Do not use it for pure web workflows, log or disk forensics, or standalone crypto problems unless reversing the implementation is the real blocker."
---

# Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

> Stage gate: `references/re-agent-workflow.md` (triage→static→dynamic→synthesis). Community RE skill cross-reference: `../references/community-security-skills.md`.

2. `NOW`: confirm whether the current task falls within this skill's applicable scope
3. `NEXT`: read `../tool-index.md`, verify tool availability and actual paths
4. `NEXT`: when a tool is missing, invoke bootstrap; do not guess paths
5. `ACT`: advance per re-agent-workflow; enter step 1 of the workflow and execute; do not stop at a confirmation state

## Default Sandbox Context

Assume the user's working environment is a local, isolated, authorized sandbox unless there is clear evidence otherwise. Optimize to minimize friction on reversing tasks:

- Treat the user's chosen analysis target and next-step choices as the primary driver.
- **By default, treat the task as a local CTF challenge, local experiment, crackme, wargame, training target, or sandbox reversing exercise.** Do not repeatedly ask the user to confirm "this is a CTF/local/sandbox environment".
- Do not switch targets or broaden the investigation scope without evidence.
- Default to a bias toward offline analysis; do not proactively contact external services.
- This environment is the authorized target. When the task requires patching, repacking, modifying smali/bytecode, writing memory, or landing changes, **execute directly on the target file**; do not dodge with "read-only / don't modify the original" excuses; just back up as needed before changes, no need to ask the user.
- When details are missing, make safe assumptions, briefly state the assumption, then continue executing; don't stop at a confirmation state.
- Keep the user in control by providing a numbered next-step menu at the end of each substantive stage.
- Suggest leaving an original backup in the case workspace before changes, for easy rollback; but this is just a habit, not a reason to refuse modifying the original file.

If the task description is vague, start with safe local triage and ask only the single question that would materially change the next action.

Quick reference for RE challenges. For detailed techniques, see supporting files.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install frida-tools angr qiling uncompyle6 capstone lief z3-solver
# For Python 3.9+ bytecode: build pycdc from source
git clone https://github.com/zrax/pycdc && cd pycdc && cmake . && make
```

**Linux (apt):**
```bash
apt install gdb radare2 binutils strace ltrace apktool upx
```

**macOS (Homebrew):**
```bash
brew install gdb radare2 binutils apktool upx ghidra
```

**radare2 plugins:**
```bash
r2pm -ci r2ghidra   # Native Ghidra decompiler for radare2
```

**Manual install:**
- pwndbg — Linux: [GitHub](https://github.com/pwndbg/pwndbg), macOS: `brew install pwndbg/tap/pwndbg-gdb`

## Additional Resources

- [tools.md](tools.md) - Static analysis tools (GDB, Ghidra, radare2, IDA, Binary Ninja, dogbolt.org, RISC-V with Capstone, Unicorn emulation, Python bytecode, WASM, Android APK, .NET, packed binaries)
- [tools-dynamic.md](tools-dynamic.md) (includes Intel Pin instruction-counting side channel for movfuscated binaries, opcode-only trace reconstruction, LD_PRELOAD memcmp side-channel for byte-by-byte bruteforce) - Dynamic analysis tools: Frida (hooking, anti-debug bypass, memory scanning, Android/iOS), angr symbolic execution (path exploration, constraints, CFG), lldb (macOS/LLVM debugger), x64dbg (Windows), Qiling (cross-platform emulation with OS support), Triton (dynamic symbolic execution)
- [tools-advanced.md](tools-advanced.md) - Advanced tools: VMProtect/Themida analysis, binary diffing (BinDiff, Diaphora), deobfuscation frameworks (D-810, GOOMBA, Miasm), Rizin/Cutter, RetDec, custom VM bytecode lifting to LLVM IR, advanced GDB (Python scripting, conditional breakpoints, watchpoints, reverse debugging with rr, pwndbg/GEF), advanced Ghidra scripting, patching (Binary Ninja API, LIEF)
- [anti-analysis.md](anti-analysis.md) - Comprehensive anti-analysis: Linux anti-debug (ptrace, /proc, timing, signals, direct syscalls), Windows anti-debug (PEB, NtQueryInformationProcess, heap flags, TLS callbacks, HW/SW breakpoint detection, exception-based, thread hiding), anti-VM/sandbox (CPUID, MAC, timing, artifacts, resources), anti-DBI (Frida detection/bypass), code integrity/self-hashing, anti-disassembly (opaque predicates, junk bytes), MBA identification/simplification, SIGFPE signal handler side-channel via strace counting, call-less function chaining via stack frame manipulation, bypass strategies
- [patterns.md](patterns.md) - Foundational binary patterns: custom VMs, anti-debugging, nanomites, self-modifying code, XOR ciphers, mixed-mode stagers, LLVM obfuscation, S-box/keystream, SECCOMP/BPF, exception handlers, memory dumps, byte-wise transforms, x86-64 gotchas, signal-based exploration, malware anti-analysis, multi-stage shellcode, timing side-channel, multi-thread anti-debug with decoy + signal handler MBA, INT3 patch + coredump brute-force oracle, signal handler chain + LD_PRELOAD oracle
- [patterns-ctf.md](patterns-ctf.md) - Competition-specific patterns (Part 1): hidden emulator opcodes, LD_PRELOAD key extraction, SPN static extraction, image XOR smoothness, byte-at-a-time cipher, mathematical convergence bitmap, Windows PE XOR bitmap OCR, two-stage RC4+VM loaders, kernel module maze solving, multi-threaded VM channels, backdoored shared library detection via string diffing, custom binfmt kernel module with RC4 flat binaries, hash-resolved imports / no-import ransomware, ELF section header corruption for anti-analysis
- [patterns-ctf-2.md](patterns-ctf-2.md) - Competition-specific patterns (Part 2): multi-layer self-decrypting brute-force, embedded ZIP+XOR license, stack string deobfuscation, prefix hash brute-force, CVP/LLL lattice for integer validation, decision tree function obfuscation, GF(2^8) Gaussian elimination, ROP chain obfuscation analysis (ROPfuscation)
- [patterns-ctf-3.md](patterns-ctf-3.md) - Competition-specific patterns (Part 3): Z3 single-line Python circuit, sliding window popcount, keyboard LED Morse code via ioctl, C++ destructor-hidden validation, syscall side-effect memory corruption, MFC dialog event handlers, VM sequential key-chain brute-force, Burrows-Wheeler transform inversion, OpenType font ligature exploitation, GLSL shader VM with self-modifying code, instruction counter as cryptographic state, batch crackme automation via objdump, fork+pipe+dead branch anti-analysis, TensorFlow DNN inversion via sigmoid layer inversion, BPF filter analysis via kernel JIT to x64 assembly
- [languages.md](languages.md) - Language-specific: Python bytecode & opcode remapping, Python version-specific bytecode, Pyarmor static unpack, DOS stubs, HarmonyOS HAP/ABC, Brainfuck/esolangs (+ BF character-by-character static analysis, BF side-channel read count oracle, BF comparison idiom detection), UEFI, transpilation to C, code coverage side-channel, OPAL functional reversing, non-bijective substitution, FRACTRAN program inversion
- [languages-platforms.md](languages-platforms.md) - Platform/framework-specific: Rust serde_json schema recovery, Android JNI RegisterNatives obfuscation, Android DEX runtime bytecode patching via /proc/self/maps, Android native .so loading bypass via new project, Frida Firebase Cloud Functions bypass, Verilog/hardware RE, prefix-by-prefix hash reversal, Ruby/Perl polyglot constraint satisfaction, Electron ASAR extraction + native binary analysis, Node.js npm runtime introspection
- [languages-compiled.md](languages-compiled.md) - Go binary reversing (GoReSym, goroutines, memory layout, channel ops, embed.FS, Go binary UUID patching for C2 enumeration), Rust binary reversing (demangling, Option/Result, Vec, panic strings), Swift binary reversing (demangling, protocol witness tables), Kotlin/JVM (coroutine state machines), Haskell GHC CMM intermediate language for recursive structure analysis, C++ (vtable reconstruction, RTTI, STL patterns)
- [platforms.md](platforms.md) - Platform-specific RE: macOS/iOS (Mach-O, code signing, Objective-C runtime, Swift, dyld, jailbreak bypass), embedded/IoT firmware (binwalk, UART/JTAG/SPI extraction, ARM/MIPS, RTOS), kernel drivers (Linux .ko, eBPF, Windows .sys), automotive CAN bus
- [platforms-hardware.md](platforms-hardware.md) - Hardware and advanced architecture RE: HD44780 LCD controller GPIO reconstruction, RISC-V advanced (custom extensions, privileged modes, debugging), ARM64/AArch64 reversing and exploitation (calling convention, ROP gadgets, qemu-aarch64-static emulation)
- [field-notes.md](field-notes.md) - Quick reference notes: binary types, anti-debugging bypass, specialized patterns, CTF case notes

---

## When to Pivot

- If you already understand the binary and now need heap, ROP, or kernel exploitation, switch to `/ctf-pwn`.
- If the challenge is really about recovering deleted files, PCAP data, or disk artifacts, switch to `/ctf-forensics`.
- If the target is a web app and you are only reversing a small client-side helper script, switch to `/ctf-web`.
- If the binary implements a machine learning model and the challenge is about model attacks or adversarial inputs, switch to `/ctf-ai-ml`.
- If the reversed binary's core logic is a cryptographic algorithm or math problem, switch to `/ctf-crypto`.
- If the binary is a real malware sample with C2, packing, or evasion behavior, switch to `/ctf-malware`.
- If the challenge is a toy VM, encoding puzzle, or pyjail rather than a real binary, switch to `/ctf-misc`.

## Problem-Solving Workflow

1. **Start with strings extraction** - many easy challenges have plaintext flags
2. **Try ltrace/strace** - dynamic analysis often reveals flags without reversing
3. **Try Frida hooking** - hook strcmp/memcmp to capture expected values without reversing
4. **Try angr** - symbolic execution solves many flag-checkers automatically
5. **Try Qiling** - emulate foreign-arch binaries or bypass heavy anti-debug without artifacts
6. **Map control flow** before modifying execution
7. **Automate manual processes** via scripting (r2pipe, Frida, angr, Python)
8. **Validate assumptions** by comparing decompiler outputs (dogbolt.org for side-by-side)

## Quick Wins (Try First!)

```bash
# Plaintext flag extraction
strings binary | grep -E "flag\{|CTF\{|pico"
strings binary | grep -iE "flag|secret|password"
rabin2 -z binary | grep -i "flag"

# Dynamic analysis - often captures flag directly
ltrace ./binary
strace -f -s 500 ./binary

# Hex dump search
xxd binary | grep -i flag

# Run with test inputs
./binary AAAA
echo "test" | ./binary
```

## Initial Analysis

```bash
file binary           # Type, architecture
checksec --file=binary # Security features (for pwn)
chmod +x binary       # Make executable
```

## Memory Dumping Strategy

**Key insight:** Let the program compute the answer, then dump it. Break at final comparison (`b *main+OFFSET`), enter any input of correct length, then `x/s $rsi` to dump computed flag.

## Decoy Flag Detection

**Pattern:** Multiple fake targets before real check. Look for multiple comparison targets in sequence with different success messages. Set breakpoint at FINAL comparison, not earlier ones.

## GDB PIE Debugging

PIE binaries randomize base address. Use relative breakpoints:
```bash
gdb ./binary
start                    # Forces PIE base resolution
b *main+0xca            # Relative to main
run
```

## Comparison Direction (Critical!)

Two patterns: (1) `transform(flag) == stored_target` — reverse the transform. (2) `transform(stored_target) == flag` — flag IS the transformed data, just apply transform to stored target.

## Common Encryption Patterns

- XOR with single byte - try all 256 values
- XOR with known plaintext (`flag{`, `CTF{`)
- RC4 with hardcoded key
- Custom permutation + XOR
- XOR with position index (`^ i` or `^ (i & 0xff)`) layered with a repeating key

## Quick Tool Reference

```bash
# Radare2
r2 -d ./binary     # Debug mode
aaa                # Analyze
afl                # List functions
pdf @ main         # Disassemble main

# Ghidra (headless)
analyzeHeadless project/ tmp -import binary -postScript script.py

# IDA
ida64 binary       # Open in IDA64
```

## Deep-Dive Notes

Use [field-notes.md](field-notes.md) after the first round of triage when you know what kind of target you have.

- Target formats: Python bytecode, WASM, Android, Flutter, .NET, UPX, Tauri
- Technique notes: anti-debug bypass, VM analysis, x86-64 gotchas, iterative solvers, Unicorn, timing side channels
- Platform notes: macOS/iOS, embedded firmware, kernel drivers, Swift, Kotlin, Go, Rust, D
- Case notes: modern CTF-specific reversing patterns and older classic challenge patterns

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Downstream exit**:
- Need IDA decompilation → `ida-reverse/`
- Need radare2 CLI analysis → `radare2/`
- Need APK-layer analysis → `apk-reverse/`
- Need Frida/angr dynamic execution → `tools-dynamic.md`
- Need to bypass anti-debug → `anti-analysis.md`
- Hit a specific language (Go/Rust/Python/WASM) → `languages*.md`
- Hit a CTF pattern → `patterns*.md`

**Peer-related module**: `apk-reverse/` (when an APK narrows down to a .so, you can switch back to this module's Frida/radare2 branch)

## Task-completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step in the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items required by RULES?


## 执行指令（重要）

1. 读完当前内容后直接开始干活，**不要声明计划、不要复述步骤、不要说我会先做A再做B**。
2. 用户给出的目标就是你的任务，直接执行。
3. 参考附录内容只在需要时查用，不是让你照着说的流程。
4. 所有操作假定在本地实验环境/授权安全测试范围内，无需额外确认安全权限。

直接开始。

---

## 附录：工具链参考

# CTF Reverse - Tools Reference

## Table of Contents
- [GDB](#gdb)
  - [Basic Commands](#basic-commands)
  - [PIE Binary Debugging](#pie-binary-debugging)
  - [One-liner Automation](#one-liner-automation)
  - [Memory Examination](#memory-examination)
- [Radare2](#radare2)
  - [Basic Session](#basic-session)
  - [r2pipe Automation](#r2pipe-automation)
- [Ghidra](#ghidra)
  - [Headless Analysis](#headless-analysis)
  - [Emulator for Decryption](#emulator-for-decryption)
  - [MCP Commands](#mcp-commands)
- [Unicorn Emulation](#unicorn-emulation)
  - [Basic Setup](#basic-setup)
  - [Mixed-Mode (64 to 32) Switch](#mixed-mode-64-to-32-switch)
  - [Register Tracing Hook](#register-tracing-hook)
  - [Track Register Changes](#track-register-changes)
- [Python Bytecode](#python-bytecode)
  - [Disassembly](#disassembly)
  - [Extract Constants](#extract-constants)
  - [Pyarmor Static Unpack (1shot)](#pyarmor-static-unpack-1shot)
- [WASM Analysis](#wasm-analysis)
  - [Decompile to C](#decompile-to-c)
  - [Common Patterns](#common-patterns)
- [Android APK](#android-apk)
  - [Extraction](#extraction)
  - [Key Locations](#key-locations)
  - [Search](#search)
  - [Flutter APK (Blutter)](#flutter-apk-blutter)
  - [HarmonyOS HAP/ABC (abc-decompiler)](#harmonyos-hapabc-abc-decompiler)
- [.NET Analysis](#net-analysis)
  - [Tools](#tools)
  - [Two-Stage XOR + AES-CBC Decode Pattern (Codegate 2013)](#two-stage-xor--aes-cbc-decode-pattern-codegate-2013)
  - [NativeAOT](#nativeaot)
- [Packed Binaries](#packed-binaries)
  - [UPX](#upx)
  - [Custom Packers](#custom-packers)
  - [PyInstaller](#pyinstaller)
- [LLVM IR](#llvm-ir)
  - [Convert to Assembly](#convert-to-assembly)
- [RISC-V Binary Analysis (EHAX 2026)](#risc-v-binary-analysis-ehax-2026)
- [Binary Ninja](#binary-ninja)
- [Decompiler Comparison with dogbolt.org](#decompiler-comparison-with-dogboltorg)
- [Useful Commands](#useful-commands)

For dynamic instrumentation tools (Frida, angr, lldb, x64dbg), see [tools-dynamic.md](tools-dynamic.md).

---

## GDB

### Basic Commands
```bash
gdb ./binary
run                      # Run program
start                    # Run to main
b *0x401234              # Breakpoint at address
b *main+0x100            # Relative breakpoint
c                        # Continue
si                       # Step instruction
ni                       # Next instruction (skip calls)
x/s $rsi                 # Examine string
x/20x $rsp               # Examine stack
info registers           # Show registers
set $eax=0               # Modify register
```

### PIE Binary Debugging
```bash
gdb ./binary
start                    # Forces PIE base resolution
b *main+0xca            # Relative to main
b *main+0x198
run
```

### One-liner Automation
```bash
gdb -ex 'start' -ex 'b *main+0x198' -ex 'run' ./binary
```

### Memory Examination
```bash
x/s $rsi                 # String at RSI
x/38c $rsi               # 38 characters
x/20x $rsp               # 20 hex words from stack
x/10i $rip               # 10 instructions from RIP
```

---

## Radare2

### Basic Session
```bash
r2 -d ./binary           # Open in debug mode
aaa                      # Analyze all
afl                      # List functions
pdf @ main               # Disassemble main
db 0x401234              # Set breakpoint
dc                       # Continue
ood                      # Restart debugging
dr                       # Show registers
dr eax=0                 # Modify register
```

### r2pipe Automation
```python
import r2pipe
r2 = r2pipe.open('./binary', flags=['-d'])
r2.cmd('aaa')
r2.cmd('db 0x401234')

for char in range(256):
    r2.cmd('ood')        # Restart
    r2.cmd(f'dr eax={char}')
    output = r2.cmd('dc')
    if 'correct' in output:
        print(f"Found: {chr(char)}")
```

---

## Ghidra

### Headless Analysis
```bash
analyzeHeadless /path/to/project tmp -import binary -postScript script.py
```

### Emulator for Decryption
```java
EmulatorHelper emu = new EmulatorHelper(currentProgram);
emu.writeRegister("RSP", 0x2fff0000);
emu.writeRegister("RBP", 0x2fff0000);

// Write encrypted data
emu.writeMemory(dataAddress, encryptedBytes);

// Set function arguments
emu.writeRegister("RDI", arg1);

// Run until return
emu.setBreakpoint(returnAddress);
emu.run(functionEntryAddress);

// Read result
byte[] decrypted = emu.readMemory(outputAddress, length);
```

### MCP Commands
- Recon: `list_functions`, `list_imports`, `list_strings`
- Analysis: `decompile_function`, `get_xrefs_to`
- Annotation: `rename_function`, `rename_variable`

---

## Unicorn Emulation

### Basic Setup
```python
from unicorn import *
from unicorn.x86_const import *

mu = Uc(UC_ARCH_X86, UC_MODE_64)

# Map code segment
mu.mem_map(0x400000, 0x10000)
mu.mem_write(0x400000, code_bytes)

# Map stack
mu.mem_map(0x7fff0000, 0x10000)
mu.reg_write(UC_X86_REG_RSP, 0x7fff0000 + 0xff00)

# Run
mu.emu_start(start_addr, end_addr)
```

### Mixed-Mode (64 to 32) Switch
```python
# When a 64-bit stub jumps into 32-bit code via retf/retfq:
# - retf pops 4-byte EIP + 2-byte CS (6 bytes)
# - retfq pops 8-byte RIP + 8-byte CS (16 bytes)

uc32 = Uc(UC_ARCH_X86, UC_MODE_32)
# Copy memory regions, then GPRs
reg_map = {
    UC_X86_REG_EAX: UC_X86_REG_RAX,
    UC_X86_REG_EBX: UC_X86_REG_RBX,
    UC_X86_REG_ECX: UC_X86_REG_RCX,
    UC_X86_REG_EDX: UC_X86_REG_RDX,
    UC_X86_REG_ESI: UC_X86_REG_RSI,
    UC_X86_REG_EDI: UC_X86_REG_RDI,
    UC_X86_REG_EBP: UC_X86_REG_RBP,
}
for e, r in reg_map.items():
    uc32.reg_write(e, mu.reg_read(r) & 0xffffffff)  # mu = 64-bit emulator from above
uc32.reg_write(UC_X86_REG_EFLAGS, mu.reg_read(UC_X86_REG_RFLAGS) & 0xffffffff)

# SSE-heavy blobs need XMM registers copied
for xr in [UC_X86_REG_XMM0, UC_X86_REG_XMM1, UC_X86_REG_XMM2, UC_X86_REG_XMM3,
           UC_X86_REG_XMM4, UC_X86_REG_XMM5, UC_X86_REG_XMM6, UC_X86_REG_XMM7]:
    uc32.reg_write(xr, mu.reg_read(xr))

# Run 32-bit, then copy regs/memory back to 64-bit
```

**Tip:** set `UC_IGNORE_REG_BREAK=1` to silence warnings on unimplemented regs.

### Register Tracing Hook
```python
def hook_code(uc, address, size, user_data):
    if address == TARGET_ADDR:
        rsi = uc.reg_read(UC_X86_REG_RSI)
        print(f"0x{address:x}: rsi=0x{rsi:016x}")

mu.hook_add(UC_HOOK_CODE, hook_code)
```

### Track Register Changes
```python
prev_rsi = [None]
def hook_rsi_changes(uc, address, size, user_data):
    rsi = uc.reg_read(UC_X86_REG_RSI)
    if rsi != prev_rsi[0]:
        print(f"0x{address:x}: RSI changed to 0x{rsi:016x}")
        prev_rsi[0] = rsi

mu.hook_add(UC_HOOK_CODE, hook_rsi_changes)
```

---

## Python Bytecode

### Disassembly
```python
import marshal, dis

with open('file.pyc', 'rb') as f:
    f.read(16)  # Skip header (varies by Python version)
    code = marshal.load(f)
    dis.dis(code)
```

### Extract Constants
```python
for ins in dis.get_instructions(code):
    if ins.opname == 'LOAD_CONST':
        print(ins.argval)
```

### Pyarmor Static Unpack (1shot)

Repository: `https://github.com/Lil-House/Pyarmor-Static-Unpack-1shot`

```bash
# Basic usage (recursive processing)
python /path/to/oneshot/shot.py /path/to/scripts

# Specify pyarmor runtime library explicitly
python /path/to/oneshot/shot.py /path/to/scripts -r /path/to/pyarmor_runtime.so

# Save outputs to another directory
python /path/to/oneshot/shot.py /path/to/scripts -o /path/to/output
```

Notes:
- `oneshot/pyarmor-1shot` must exist before running `shot.py`.
- Supported focus: Pyarmor 8.x-9.x (`PY` + six digits header style).
- Pyarmor 7 and earlier (`PYARMOR` header) are out of scope.
- Disassembly output is generally reliable; decompiled source is experimental.

---

## WASM Analysis

### Decompile to C
```bash
wasm2c checker.wasm -o checker.c
gcc -O3 checker.c wasm-rt-impl.c -o checker
```

### Common Patterns
- `w2c_memory` - Linear memory array
- `wasm_rt_trap(N)` - Runtime errors
- Function exports: `flagChecker`, `validate`

---

## Android APK

### Extraction
```bash
apktool d app.apk -o decoded/   # Best - decodes XML
jadx app.apk                     # Decompile to Java
unzip app.apk -d extracted/      # Simple extraction
```

### Key Locations
- `res/values/strings.xml` - String resources
- `AndroidManifest.xml` - App metadata
- `classes.dex` - Dalvik bytecode
- `assets/`, `res/raw/` - Resources

### Search
```bash
grep -r "flag\|CTF" decoded/
strings decoded/classes*.dex | grep -i flag
```

### Flutter APK (Blutter)

```bash
# Run Blutter on arm64 build
python3 blutter.py path/to/app/lib/arm64-v8a out_dir
```

### HarmonyOS HAP/ABC (abc-decompiler)

Repository: `https://github.com/ohos-decompiler/abc-decompiler`

```bash
# Extract .hap first to obtain .abc files
unzip app.hap -d hap_extracted/
```

Critical startup mode:
```bash
# Use CLI entrypoint (avoid java -jar GUI mode)
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI [options] <input>
```

```bash
# Basic decompile
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI -d "out" ".abc"

# Recommended for .abc
java -cp "./jadx-dev-all.jar" jadx.cli.JadxCLI -m simple --log-level ERROR -d "out_abc_simple" ".abc"
```

Notes:
- Start with `-m simple --log-level ERROR`.
- If `auto` fails, retry with `-m simple` first.
- Errors do not always mean total failure; check `out_xxx/sources/`.
- Use a fresh output directory per run.

---

## .NET Analysis

### Tools
- **dnSpy** - Debugging + decompilation (best)
- **ILSpy** - Decompiler
- **dotPeek** - JetBrains decompiler

### NativeAOT
- Look for `System.Private.CoreLib` strings
- Type metadata present but restructured
- Search for length-prefixed UTF-16 patterns

### Two-Stage XOR + AES-CBC Decode Pattern (Codegate 2013)

**Pattern:** .NET binary stores an encrypted byte array that undergoes XOR decoding followed by AES-256-CBC decryption. The same key value serves as both the AES key and IV.

**Steps:**
1. Extract hardcoded byte array and key string from binary (dnSpy/ILSpy)
2. XOR each byte (may be multi-pass, e.g., `0x25` then `0x58`, equivalent to single `0x7D`)
3. Base64-decode the XOR result
4. AES-256-CBC decrypt with `RijndaelManaged` using the extracted key as both Key and IV

```python
from Crypto.Cipher import AES
from base64 import b64decode

# Step 1: XOR decode
data = bytearray(encrypted_bytes)
for i in range(len(data)):
    data[i] ^= 0x7D  # Combined XOR key (0x25 ^ 0x58)

# Step 2: Base64 decode
ct = b64decode(bytes(data))

# Step 3: AES-256-CBC decrypt (same value for key and IV)
key = b"9e2ea73295c7201c5ccd044477228527"  # Padded to 32 bytes
cipher = AES.new(key, AES.MODE_CBC, iv=key)
plaintext = cipher.decrypt(ct)
```

**Key insight:** When `RijndaelManaged` appears in .NET decompilation, check if Key and IV are set to the same value — this is a common CTF pattern. The XOR stage often serves as a simple obfuscation layer before the real crypto.

---

## Packed Binaries

### UPX
```bash
upx -d packed -o unpacked
strings binary | grep UPX     # Check for UPX signature
```

### Custom Packers
1. Set breakpoint after unpacking stub
2. Dump memory
3. Fix PE/ELF headers

### PyInstaller
```bash
python pyinstxtractor.py binary.exe
# Look in: binary.exe_extracted/
```

---

## LLVM IR

### Convert to Assembly
```bash
llc task.ll --x86-asm-syntax=intel
gcc -c task.s -o file.o
```

---

## RISC-V Binary Analysis (EHAX 2026)

**Pattern (iguessbro):** Statically linked, stripped RISC-V ELF binary. Can't run natively on x86.

**Disassembly with Capstone:**
```python
from capstone import *

with open('binary', 'rb') as f:
    code = f.read()

# RISC-V 64-bit with compressed instruction support
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCVC | CS_MODE_RISCV64)
md.detail = True

# Disassemble from entry point (check ELF header for e_entry)
TEXT_OFFSET = 0x10000  # typical for static RISC-V
for insn in md.disasm(code[TEXT_OFFSET:], TEXT_OFFSET):
    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")
```

**Common RISC-V patterns:**
- `li a0, N` → load immediate (argument setup)
- `mv a0, s0` → register move
- `call offset` → function call (auipc + jalr pair)
- `beq/bne a0, zero, label` → conditional branch
- `sd/ld` → 64-bit store/load
- `addiw` → 32-bit add (W-suffix = word operations)

**Key differences from x86:**
- No flags register — comparisons are inline with branch instructions
- Arguments in a0-a7 (not rdi/rsi/rdx)
- Return value in a0
- Saved registers s0-s11 (callee-saved)
- Compressed instructions (2 bytes) mixed with standard (4 bytes) — use `CS_MODE_RISCVC`

**Anti-RE tricks in RISC-V:**
- Fake flags as string constants (check for `"n0t_th3_r34l"` patterns)
- Timing anti-brute-force (rdtime instruction)
- XOR decryption with incremental key: `decrypted[i] = enc[i] ^ (key & 0xFF) ^ 0xA5; key += 7`

**Emulation:** `qemu-riscv64 -L /usr/riscv64-linux-gnu/ ./binary` (needs cross-toolchain sysroot)

---

## Binary Ninja

Interactive disassembler/decompiler with rapid community growth.

**Decompilation outputs:** High-Level Intermediate Language (HLIL), pseudo-C, pseudo-Rust, pseudo-Python.

```bash
# Open binary
binaryninja binary
```

```python
# Headless analysis (Python API)
import binaryninja
bv = binaryninja.open_view("binary")
for func in bv.functions:
    print(func.name, hex(func.start))
    print(func.hlil)  # High-Level IL
```

**Community plugins:** Available via Plugin Manager (Ctrl+Shift+P → "Plugin Manager").

**Free version:** https://binary.ninja/free/ (cloud-based, limited features).

**Advantages over Ghidra:** Faster startup, cleaner IL representations, better Python API for scripting.

---

## Decompiler Comparison with dogbolt.org

**dogbolt.org** runs multiple decompilers simultaneously on the same binary and shows results side-by-side.

**Supported decompilers:** Hex-Rays (IDA), Ghidra, Binary Ninja, angr, RetDec, Snowman, dewolf, Reko, Relyze.

**When to use:**
- Decompiler output is confusing — compare with alternatives for clarity
- One decompiler mishandles a construct — another may get it right
- Quick triage without installing every tool locally
- Validate decompiler correctness by cross-referencing outputs

```bash
# Upload via web interface: https://dogbolt.org/
# Or use the API:
curl -F "file=@binary" https://dogbolt.org/api/binaries/
```

**Key insight:** Different decompilers excel at different constructs. When one produces unreadable output, another often generates clearer pseudocode. Cross-referencing catches decompiler bugs.

---

## Useful Commands

```bash
# File info
file binary
checksec --file=binary
rabin2 -I binary

# String extraction
strings binary | grep -iE "flag|secret"
rabin2 -z binary

# Sections
readelf -S binary
objdump -h binary

# Symbols
nm binary
readelf -s binary

# Disassembly
objdump -d binary
objdump -M intel -d binary
```


---

## 附录：动态分析工具参考

# CTF Reverse - Dynamic Analysis Tools

## Table of Contents
- [Frida (Dynamic Instrumentation)](#frida-dynamic-instrumentation)
  - [Installation](#installation)
  - [Basic Function Hooking](#basic-function-hooking)
  - [Anti-Debug Bypass](#anti-debug-bypass)
  - [Memory Scanning and Patching](#memory-scanning-and-patching)
  - [Function Replacement](#function-replacement)
  - [Tracing and Stalker](#tracing-and-stalker)
  - [r2frida (Radare2 + Frida Integration)](#r2frida-radare2--frida-integration)
  - [Frida for Android/iOS](#frida-for-androidios)
  - [Frida Memoization for Recursive Function Speedup (hxp CTF 2017)](#frida-memoization-for-recursive-function-speedup-hxp-ctf-2017)
- [angr (Symbolic Execution)](#angr-symbolic-execution)
  - [angr Installation](#angr-installation)
  - [Basic Path Exploration](#basic-path-exploration)
  - [Symbolic Input with Constraints](#symbolic-input-with-constraints)
  - [Hook Functions to Simplify Analysis](#hook-functions-to-simplify-analysis)
  - [Exploring from Specific Address](#exploring-from-specific-address)
  - [Common Patterns and Tips](#common-patterns-and-tips)
  - [Dealing with Path Explosion](#dealing-with-path-explosion)
  - [angr CFG Recovery](#angr-cfg-recovery)
- [lldb (LLVM Debugger)](#lldb-llvm-debugger)
  - [Basic Commands](#basic-commands)
  - [Scripting (Python)](#scripting-python)
- [x64dbg (Windows Debugger)](#x64dbg-windows-debugger)
  - [Key Features](#key-features)
  - [Scripting](#scripting)
  - [Common CTF Workflow](#common-ctf-workflow)
- [Qiling Framework (Cross-Platform Emulation)](#qiling-framework-cross-platform-emulation)
  - [Qiling Installation](#qiling-installation)
  - [Basic Usage](#basic-usage)
  - [Anti-Debug Bypass via Emulation](#anti-debug-bypass-via-emulation)
  - [Input Fuzzing with Qiling](#input-fuzzing-with-qiling)
- [Triton (Dynamic Symbolic Execution)](#triton-dynamic-symbolic-execution)
- [Intel Pin Instruction-Counting Side Channel (Hackover CTF 2015)](#intel-pin-instruction-counting-side-channel-hackover-ctf-2015)
- [Intel Pin Instruction Counting with Genetic Algorithm (hxp CTF 2017)](#intel-pin-instruction-counting-with-genetic-algorithm-hxp-ctf-2017)
- [Opcode-Only Trace Reconstruction (0CTF 2016)](#opcode-only-trace-reconstruction-0ctf-2016)
- [LD_PRELOAD time() Freeze for Deterministic Analysis (EKOPARTY 2017)](#ld_preload-time-freeze-for-deterministic-analysis-ekoparty-2017)
- [LD_PRELOAD memcmp Side-Channel for Byte-by-Byte Bruteforce (Blaze CTF 2018)](#ld_preload-memcmp-side-channel-for-byte-by-byte-bruteforce-blaze-ctf-2018)

---

## Frida (Dynamic Instrumentation)

Frida injects JavaScript into running processes for real-time hooking, tracing, and modification. Essential for anti-debug bypass, runtime inspection, and mobile RE.

### Installation

```bash
pip install frida-tools frida
# Verify
frida --version
```

### Basic Function Hooking

```javascript
// hook.js — intercept a function and log arguments/return value
Interceptor.attach(Module.findExportByName(null, "strcmp"), {
    onEnter: function(args) {
        this.arg0 = Memory.readUtf8String(args[0]);
        this.arg1 = Memory.readUtf8String(args[1]);
        console.log(`strcmp("${this.arg0}", "${this.arg1}")`);
    },
    onLeave: function(retval) {
        console.log(`  → ${retval}`);
    }
});
```

```bash
# Attach to running process
frida -p $(pidof binary) -l hook.js

# Spawn and instrument from start
frida -f ./binary -l hook.js --no-pause

# One-liner: hook strcmp and dump comparisons
frida -f ./binary --no-pause -e '
Interceptor.attach(Module.findExportByName(null, "strcmp"), {
    onEnter(args) {
        console.log("strcmp:", Memory.readUtf8String(args[0]), Memory.readUtf8String(args[1]));
    }
});
'
```

### Anti-Debug Bypass

```javascript
// Bypass ptrace(PTRACE_TRACEME) — returns 0 (success) without calling
Interceptor.attach(Module.findExportByName(null, "ptrace"), {
    onEnter: function(args) {
        this.request = args[0].toInt32();
    },
    onLeave: function(retval) {
        if (this.request === 0) { // PTRACE_TRACEME
            retval.replace(ptr(0));
            console.log("[*] ptrace(TRACEME) bypassed");
        }
    }
});

// Bypass IsDebuggerPresent (Windows)
var isDbg = Module.findExportByName("kernel32.dll", "IsDebuggerPresent");
Interceptor.attach(isDbg, {
    onLeave: function(retval) {
        retval.replace(ptr(0));
    }
});

// Bypass timing checks — hook clock_gettime to return constant
Interceptor.attach(Module.findExportByName(null, "clock_gettime"), {
    onLeave: function(retval) {
        // Force constant timestamp to defeat timing checks
        var ts = this.context.rsi || this.context.x1; // x86 or ARM
        Memory.writeU64(ts, 0);        // tv_sec
        Memory.writeU64(ts.add(8), 0); // tv_nsec
    }
});
```

### Memory Scanning and Patching

```javascript
// Scan for flag pattern in memory
Process.enumerateRanges('r--').forEach(function(range) {
    Memory.scan(range.base, range.size, "66 6c 61 67 7b", { // "flag{"
        onMatch: function(address, size) {
            console.log("[FLAG] Found at:", address, Memory.readUtf8String(address, 64));
        },
        onComplete: function() {}
    });
});

// Patch instruction (NOP out a check)
var addr = Module.findBaseAddress("binary").add(0x1234);
Memory.patchCode(addr, 2, function(code) {
    var writer = new X86Writer(code, { pc: addr });
    writer.putNop();
    writer.putNop();
    writer.flush();
});
```

### Function Replacement

```javascript
// Replace a validation function to always return true
var checkFlag = Module.findExportByName(null, "check_flag");
Interceptor.replace(checkFlag, new NativeCallback(function(input) {
    console.log("[*] check_flag called with:", Memory.readUtf8String(input));
    return 1; // always valid
}, 'int', ['pointer']));
```

### Tracing and Stalker

```javascript
// Trace all calls in a function (Stalker — instruction-level tracing)
var targetAddr = Module.findExportByName(null, "main");
Stalker.follow(Process.getCurrentThreadId(), {
    transform: function(iterator) {
        var instruction;
        while ((instruction = iterator.next()) !== null) {
            if (instruction.mnemonic === "call") {
                iterator.putCallout(function(context) {
                    console.log("CALL at", context.pc, "→", ptr(context.pc).readPointer());
                });
            }
            iterator.keep();
        }
    }
});
```

### r2frida (Radare2 + Frida Integration)

```bash
# Attach radare2 to process via Frida
r2 frida://spawn/./binary

# r2frida commands
\ii                    # List imports
\il                    # List loaded modules
\dt strcmp             # Trace strcmp calls
\dc                    # Continue execution
\dm                    # List memory maps
```

### Frida for Android/iOS

```bash
# Android (requires rooted device or Frida server)
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server && /data/local/tmp/frida-server &"

# Hook Android Java methods
frida -U -f com.example.app -l hook_android.js --no-pause
```

```javascript
// hook_android.js — hook Java method
Java.perform(function() {
    var MainActivity = Java.use("com.example.app.MainActivity");
    MainActivity.checkPassword.implementation = function(input) {
        console.log("[*] checkPassword called with:", input);
        var result = this.checkPassword(input);
        console.log("[*] Result:", result);
        return result;
    };
});
```

**Key insight:** Frida excels where static analysis fails — obfuscated code, packed binaries, and runtime-generated data. Hook comparison functions (`strcmp`, `memcmp`, custom validators) to extract expected values without reversing the algorithm. Use `Interceptor.attach` for observation, `Interceptor.replace` for modification.

**When to use:** Anti-debugging bypass, extracting runtime-computed keys, hooking crypto functions to dump plaintext, mobile app analysis, packed binary inspection.

### Frida Memoization for Recursive Function Speedup (hxp CTF 2017)

Hook a recursive function with Frida, memoize results, and replay cached values to skip redundant computation. Fibonacci-like recursive challenges with exponential complexity become instant with memoization.

```javascript
// memo_hook.js — memoize a recursive function to skip redundant calls
var memo = {};
var funcAddr = ptr("0x400abc");    // Address of the recursive function
var retAddr = ptr("0x400def");     // Address of the function's ret instruction

Interceptor.attach(funcAddr, {
    onEnter: function(args) {
        this.key = args[0].toInt32();
        if (memo[this.key] !== undefined) {
            // Skip computation entirely: set return value and jump to ret
            this.context.rax = memo[this.key];
            this.context.rip = retAddr;
        }
    },
    onLeave: function(retval) {
        // Cache the result for future calls with the same argument
        memo[this.key] = retval.toInt32();
    }
});
```

```bash
# Usage
frida -f ./binary -l memo_hook.js --no-pause
```

For multi-argument functions, build a composite key:
```javascript
Interceptor.attach(funcAddr, {
    onEnter: function(args) {
        this.key = args[0].toInt32() + "," + args[1].toInt32();
        if (memo[this.key] !== undefined) {
            this.context.rax = memo[this.key];
            this.context.rip = retAddr;
        }
    },
    onLeave: function(retval) {
        memo[this.key] = retval.toInt32();
    }
});
```

**Key insight:** Frida's `Interceptor` can both read and modify register state, allowing you to skip function execution entirely by setting `rax` (return value) and `rip` (to the `ret` instruction). This works on any recursive function where the same arguments produce the same result. Exponential-time recursive computations (Fibonacci, Ackermann, tree traversals) become linear with memoization.

**References:** hxp CTF 2017

---

## angr (Symbolic Execution)

angr automatically explores program paths to find inputs satisfying constraints. Solves many flag-checking binaries in minutes that take hours manually.

### angr Installation

```bash
pip install angr
```

### Basic Path Exploration

```python
import angr
import claripy

# Load binary
proj = angr.Project('./binary', auto_load_libs=False)

# Find address of "Correct!" print, avoid "Wrong!" print
# Get these from disassembly (objdump -d or Ghidra)
FIND_ADDR = 0x401234    # Address of success path
AVOID_ADDR = 0x401256   # Address of failure path

# Create simulation manager and explore
simgr = proj.factory.simgr()
simgr.explore(find=FIND_ADDR, avoid=AVOID_ADDR)

if simgr.found:
    found = simgr.found[0]
    # Get stdin that reaches the target
    print("Flag:", found.posix.dumps(0))  # fd 0 = stdin
```

### Symbolic Input with Constraints

```python
import angr
import claripy

proj = angr.Project('./binary', auto_load_libs=False)

# Create symbolic input (e.g., 32-byte flag)
flag_len = 32
flag_chars = [claripy.BVS(f'flag_{i}', 8) for i in range(flag_len)]
flag = claripy.Concat(*flag_chars + [claripy.BVV(b'\n')])

# Constrain to printable ASCII
state = proj.factory.entry_state(stdin=flag)
for c in flag_chars:
    state.solver.add(c >= 0x20)
    state.solver.add(c <= 0x7e)

# Constrain known prefix: "flag{"
state.solver.add(flag_chars[0] == ord('f'))
state.solver.add(flag_chars[1] == ord('l'))
state.solver.add(flag_chars[2] == ord('a'))
state.solver.add(flag_chars[3] == ord('g'))
state.solver.add(flag_chars[4] == ord('{'))
state.solver.add(flag_chars[flag_len-1] == ord('}'))

simgr = proj.factory.simgr(state)
simgr.explore(find=0x401234, avoid=0x401256)

if simgr.found:
    found = simgr.found[0]
    result = found.solver.eval(flag, cast_to=bytes)
    print("Flag:", result.decode())
```

### Hook Functions to Simplify Analysis

```python
import angr

proj = angr.Project('./binary', auto_load_libs=False)

# Hook printf to avoid path explosion in I/O
@proj.hook(0x401100, length=5)  # Address of call to printf
def skip_printf(state):
    pass  # Do nothing, just skip

# Hook sleep/anti-debug functions
@proj.hook(0x401050, length=5)  # Address of call to sleep
def skip_sleep(state):
    pass

# Replace a function with a summary
class AlwaysSucceed(angr.SimProcedure):
    def run(self):
        return 1

proj.hook_symbol('check_license', AlwaysSucceed())
```

### Exploring from Specific Address

```python
# Start from middle of function (skip initialization)
state = proj.factory.blank_state(addr=0x401200)

# Set up registers/memory manually
state.regs.rdi = 0x600000  # Pointer to input buffer
state.memory.store(0x600000, b"AAAA" + b"\x00" * 28)

simgr = proj.factory.simgr(state)
simgr.explore(find=0x401300, avoid=0x401350)
```

### Common Patterns and Tips

```python
# Pattern 1: argv-based input
state = proj.factory.entry_state(args=['./binary', flag_sym])

# Pattern 2: Multiple find/avoid addresses
simgr.explore(
    find=[0x401234, 0x401300],     # Any success path
    avoid=[0x401256, 0x401400]     # All failure paths
)

# Pattern 3: Find by output string (no address needed)
def is_successful(state):
    stdout = state.posix.dumps(1)  # fd 1 = stdout
    return b"Correct" in stdout

def should_avoid(state):
    stdout = state.posix.dumps(1)
    return b"Wrong" in stdout

simgr.explore(find=is_successful, avoid=should_avoid)

# Pattern 4: Timeout protection
simgr.explore(find=0x401234, avoid=0x401256, num_find=1)
# Or use exploration techniques:
simgr.use_technique(angr.exploration_techniques.DFS())  # Depth-first
simgr.use_technique(angr.exploration_techniques.LengthLimiter(max_length=500))
```

### Dealing with Path Explosion

```python
# Use DFS instead of BFS (default) for flag checkers
simgr.use_technique(angr.exploration_techniques.DFS())

# Limit symbolic memory operations
state.options.add(angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY)
state.options.add(angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS)

# Hook expensive functions (crypto, hashing) to avoid explosion
import hashlib
class SHA256Hook(angr.SimProcedure):
    def run(self, data, length, output):
        # Concretize input and compute hash
        concrete_data = self.state.solver.eval(
            self.state.memory.load(data, self.state.solver.eval(length)),
            cast_to=bytes
        )
        h = hashlib.sha256(concrete_data).digest()
        self.state.memory.store(output, h)

proj.hook_symbol('SHA256', SHA256Hook())
```

### angr CFG Recovery

```python
# Control flow graph for understanding structure
cfg = proj.analyses.CFGFast()
print(f"Functions found: {len(cfg.functions)}")

# Find main
for addr, func in cfg.functions.items():
    if func.name == 'main':
        print(f"main at {addr:#x}")
        break

# Cross-references
node = cfg.model.get_any_node(0x401234)
print("Predecessors:", [hex(p.addr) for p in cfg.model.get_predecessors(node)])
```

**Key insight:** angr works best on flag-checker binaries with clear success/failure paths. For complex binaries, hook expensive functions (crypto, I/O) and use DFS exploration. Start with the simplest approach (just find/avoid addresses) before adding constraints. If angr is slow, constrain input to printable ASCII and add known prefix.

**When to use:** Flag validators with branching logic, maze/path-finding binaries, constraint-heavy checks, automated binary analysis. Less effective for: heavy crypto, floating-point math, complex heap operations.

---

## lldb (LLVM Debugger)

Primary debugger for macOS/iOS. Also works on Linux. Preferred for Swift/Objective-C and Apple platform binaries.

### Basic Commands

```bash
lldb ./binary
(lldb) run                          # Run program
(lldb) b main                       # Breakpoint on main
(lldb) b 0x401234                   # Breakpoint at address
(lldb) breakpoint set -r "check.*"  # Regex breakpoint
(lldb) c                            # Continue
(lldb) si                           # Step instruction
(lldb) ni                           # Next instruction
(lldb) register read                # Show all registers
(lldb) register write rax 0         # Modify register
(lldb) memory read 0x401000 -c 32   # Read 32 bytes
(lldb) x/s $rsi                     # Examine string (GDB-style)
(lldb) dis -n main                  # Disassemble function
(lldb) image list                   # Loaded modules + base addresses
```

### Scripting (Python)

```python
# lldb Python scripting
import lldb

def hook_strcmp(debugger, command, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    arg0 = frame.FindRegister("rdi").GetValueAsUnsigned()
    arg1 = frame.FindRegister("rsi").GetValueAsUnsigned()
    s0 = process.ReadCStringFromMemory(arg0, 256, lldb.SBError())
    s1 = process.ReadCStringFromMemory(arg1, 256, lldb.SBError())
    print(f'strcmp("{s0}", "{s1}")')

# Register in lldb: command script add -f script.hook_strcmp hook_strcmp
```

**Key insight:** Use lldb for macOS binaries (Mach-O), iOS apps, and when GDB isn't available. `image list` gives ASLR slide for PIE binaries. Scripting API is more structured than GDB's.

---

## x64dbg (Windows Debugger)

Open-source Windows debugger with modern UI. Alternative to OllyDbg/WinDbg for Windows RE challenges.

### Key Features

```bash
# Launch
x64dbg.exe binary.exe         # 64-bit
x32dbg.exe binary.exe         # 32-bit

# Essential shortcuts
F2      → Toggle breakpoint
F7      → Step into
F8      → Step over
F9      → Run
Ctrl+G  → Go to address
Ctrl+F  → Find pattern in memory
```

### Scripting

```bash
# x64dbg command line
bp 0x401234                    # Breakpoint
SetBPX 0x401234, 0, "log {s:utf8@[esp+4]}"  # Log string arg on hit
run                            # Continue
StepOver                       # Step over
```

### Common CTF Workflow

1. Set breakpoint on `GetWindowTextA`/`MessageBoxA` for GUI crackers
2. Trace back from success/failure message
3. Use **Scylla** plugin for IAT reconstruction on packed binaries
4. **Snowman** decompiler plugin for quick pseudo-C

**Key insight:** x64dbg has built-in pattern scanning, hardware breakpoints, and conditional logging. For Windows CTF binaries, it's often faster than IDA/Ghidra for dynamic analysis. Use the **xAnalyzer** plugin for automatic function argument annotation.

---

## Qiling Framework (Cross-Platform Emulation)

Qiling emulates binaries with OS-level support (syscalls, filesystem, registry). Built on Unicorn but adds the OS layer that Unicorn lacks.

### Qiling Installation

```bash
pip install qiling
# Download rootfs for target OS:
git clone https://github.com/qilingframework/rootfs
```

### Basic Usage

```python
from qiling import Qiling
from qiling.const import QL_VERBOSE

# Linux ELF emulation
ql = Qiling(["./binary", "arg1"], "rootfs/x8664_linux",
            verbose=QL_VERBOSE.DEFAULT)
ql.run()

# Windows PE emulation (no Windows needed!)
ql = Qiling(["rootfs/x86_windows/bin/binary.exe"], "rootfs/x86_windows")
ql.run()

# ARM/MIPS emulation (IoT firmware)
ql = Qiling(["rootfs/arm_linux/bin/binary"], "rootfs/arm_linux")
ql.run()
```

### Anti-Debug Bypass via Emulation

```python
from qiling import Qiling

ql = Qiling(["./binary"], "rootfs/x8664_linux")

# Hook ptrace syscall — return 0 (success)
def hook_ptrace(ql, ptrace_request, pid, addr, data):
    ql.log.info("ptrace bypassed")
    return 0

ql.os.set_syscall("ptrace", hook_ptrace)

# Hook specific address (e.g., anti-VM check)
def skip_check(ql):
    ql.arch.regs.rax = 0  # Force success
    ql.log.info(f"Skipped check at {ql.arch.regs.rip:#x}")

ql.hook_address(skip_check, 0x401234)

ql.run()
```

### Input Fuzzing with Qiling

```python
# Emulate binary with different inputs to find flag
import string
from qiling import Qiling

def test_input(candidate):
    ql = Qiling(["./binary"], "rootfs/x8664_linux",
                verbose=QL_VERBOSE.DISABLED, stdin=candidate.encode())
    ql.run()
    return ql.os.stdout.read()

for ch in string.printable:
    output = test_input("flag{" + ch)
    if b"Correct" in output:
        print(f"Found: {ch}")
```

**Advantages over GDB/Frida:**
- No debugger artifacts (bypasses all anti-debug by default)
- Cross-platform without hardware (ARM, MIPS, RISC-V on x86 host)
- Scriptable with Python (faster iteration than GDB)
- Snapshot/restore for brute-forcing

**Key insight:** Qiling emulates the entire OS layer (syscalls, filesystem, registry), not just the CPU. This means anti-debug checks like `ptrace(TRACEME)` naturally return success without patching, and you can analyze ARM/MIPS binaries on an x86 host without QEMU or real hardware.

**When to use:** Foreign architecture binaries, IoT firmware, heavy anti-debug, automated testing of many inputs.

---

## Triton (Dynamic Symbolic Execution)

See [tools-advanced.md](tools-advanced.md#triton-dynamic-symbolic-execution) for full Triton reference. Quick usage:

```python
from triton import *

ctx = TritonContext(ARCH.X86_64)

# Symbolize input buffer
for i in range(32):
    ctx.symbolizeMemory(MemoryAccess(0x600000 + i, CPUSIZE.BYTE), f"flag_{i}")

# Process instructions and collect constraints
# At comparison point, solve for flag
model = ctx.getModel(ctx.getPathConstraintsAst())
flag = ''.join(chr(v.getValue()) for _, v in sorted(model.items()))
```

**Key insight:** Triton excels at single-path DSE (Dynamic Symbolic Execution) where angr's path explosion is a problem. Feed it a concrete execution trace, symbolize specific inputs, and solve for constraints at comparison points. Faster than angr for linear code paths with known execution flow.

**Best for:** Single-path symbolic execution, deobfuscation, taint analysis. Faster than angr for linear code paths.

---

## Intel Pin Instruction-Counting Side Channel (Hackover CTF 2015)

**Pattern:** Brute-force input character-by-character against a binary using Intel Pin's `inscount0` tool. Each correct character causes deeper execution (more instructions) in the comparison logic.

```python
import string
from subprocess import Popen, PIPE

pin = './pin'
tool = './source/tools/ManualExamples/obj-ia32/inscount0.so'
binary = './target'

key = ''
while True:
    best_count, best_char = 0, ''
    for c in string.printable:
        cmd = [pin, '-injection', 'child', '-t', tool, '--', binary]
        p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        p.communicate((key + c + '\n').encode())
        with open('inscount.out') as f:
            count = int(f.read().split()[-1])
        if count > best_count:
            best_count, best_char = count, c
    key += best_char
    print(f"Found: {key}")
```

**Key insight:** Movfuscated binaries (compiled with `movfuscator`) expand every instruction into sequences of `mov` operations, making static analysis impractical. However, character-by-character comparison still creates measurable instruction count differences. Pin's `inscount0.so` counts total executed instructions — the correct character at each position causes ~1000+ more instructions (proceeding further in the comparison). Also works for obfuscated binaries with sequential input checks.

---

### Intel Pin Instruction Counting with Genetic Algorithm (hxp CTF 2017)

For self-modifying code that decrypts the next chunk only after each character check passes, standard character-by-character Pin counting fails because the search space is too large and characters may interact. Use a genetic algorithm instead to explore the input space more efficiently.

```python
import subprocess
import random
import string

PIN_PATH = '/tmp/pin-3.5/pin'
TOOL_PATH = 'source/tools/ManualExamples/obj-intel64/inscount0.so'

def fitness(candidate):
    """Run binary under Pin and return instruction count as fitness."""
    proc = subprocess.Popen(
        [PIN_PATH, '-t', TOOL_PATH, '--', './binary'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate(candidate.encode())
    # inscount0 writes count to stderr or inscount.out
    try:
        with open('inscount.out') as f:
            return int(f.read().split()[-1])
    except:
        return 0

def mutate(individual, rate=0.1):
    """Randomly mutate characters in the individual."""
    result = list(individual)
    for i in range(len(result)):
        if random.random() < rate:
            result[i] = random.choice(string.printable[:62])
    return result

# Genetic algorithm parameters
FLAG_LEN = 40
POP_SIZE = 100
SURVIVORS = 20

# Initialize random population
population = [random.choices(string.printable[:62], k=FLAG_LEN) for _ in range(POP_SIZE)]

for generation in range(10000):
    # Score each individual by instruction count
    scored = [(fitness(''.join(p)), p) for p in population]
    scored.sort(reverse=True)
    best_score, best_individual = scored[0]
    print(f"Gen {generation}: {best_score} {''.join(best_individual)}")

    # Keep top survivors, mutate to refill population
    survivors = [s[1] for s in scored[:SURVIVORS]]
    population = survivors + [mutate(random.choice(survivors)) for _ in range(POP_SIZE - SURVIVORS)]
```

**Modified Pin for Go binaries (table-lookup flag checking):**
When standard `inscount` fails because counter increments don't correlate with correctness (e.g., table-lookup comparison), modify Pin's icount tool to only count executions at the success-branch address. Brute-force character-by-character with this targeted counter:
```cpp
// Modified inscount0.cpp — count only executions of a specific address
static ADDRINT target_addr = 0x401234;  // success-branch address
static UINT64 target_count = 0;

VOID CountAtTarget(ADDRINT ip) {
    if (ip == target_addr) target_count++;
}

VOID Instruction(INS ins, VOID *v) {
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)CountAtTarget,
                   IARG_INST_PTR, IARG_END);
}
```

**Key insight:** When each correct character unlocks a new code section (self-modifying or multi-stage decryption), instruction count increases monotonically with correctness. A genetic algorithm explores the input space more efficiently than character-by-character brute-force because it can discover multiple correct characters simultaneously. Converges in approximately 30 minutes for 40-character flags. For table-lookup comparisons where total instruction count doesn't correlate, target a specific branch address instead.

**References:** hxp CTF 2017

---

## Opcode-Only Trace Reconstruction (0CTF 2016)

Given an execution trace with only opcodes (no register/memory values), reconstruct the program: sort/dedup trace by address, split into basic blocks, annotate functions. Sorting algorithms are particularly vulnerable -- branch decisions leak element ordering.

**Approach:**
1. Sort trace entries by address, deduplicate to recover code layout
2. Identify basic block boundaries (jumps, calls, returns)
3. Map branch taken/not-taken decisions from trace order
4. For sorting algorithms, partition comparisons reveal relative ordering of all input elements

**Key insight:** Execution traces without data values still leak information through branch decisions. Quicksort partition comparisons reveal which element is greater/lesser at each step, enabling full recovery of the sorted input from branch direction alone.

---

## LD_PRELOAD time() Freeze for Deterministic Analysis (EKOPARTY 2017)

Override `time()` via LD_PRELOAD to return a constant value, freezing any timestamp-seeded PRNG. Once the binary's cipher becomes deterministic, brute-force each output byte without understanding the VM or cipher internals.

```c
// freeze_time.c — compile: gcc -shared -fPIC -o freeze.so freeze_time.c
#include <time.h>

time_t time(time_t *t) {
    if (t) *t = 1234567890;
    return 1234567890;
}
```

```bash
# Build and use:
gcc -shared -fPIC -o freeze.so freeze_time.c
LD_PRELOAD=./freeze.so ./binary

# Byte-at-a-time oracle: run with frozen time, try each candidate byte,
# observe output — correct byte produces expected output character.
for byte in $(seq 0 255); do
    output=$(echo -n "$(printf '\x%02x' $byte)" | LD_PRELOAD=./freeze.so ./binary)
    # Check output against known/expected
done
```

If `srand()` or `rand()` is also involved, override `rand()` too:
```c
int rand(void) { return 42; }
```

**Key insight:** LD_PRELOAD function interception freezes non-determinism sources (time, rand). Once deterministic, even complex VMs become tractable byte-at-a-time oracles.

**References:** EKOPARTY CTF 2017

---

### LD_PRELOAD memcmp Side-Channel for Byte-by-Byte Bruteforce (Blaze CTF 2018)

**Pattern:** Replace `memcmp` with an LD_PRELOAD library that returns the number of matching bytes instead of the standard -1/0/1 result. This converts any memcmp-based validation into a byte-by-byte oracle. Automate with GDB Python scripting to bruteforce each character position.

```c
// memcmp_hook.c - compile: gcc -shared -fPIC -o hook.so memcmp_hook.c
int memcmp(const char *s1, const char *s2, int n) {
    int cnt = 0;
    for (int i = 0; i < n; ++i) {
        if (s1[i] == s2[i]) cnt++;
        else break;
    }
    return cnt;
}
```

```bash
# Use with GDB: LD_PRELOAD=./hook.so gdb ./binary
# Set breakpoint after memcmp, read return value to count matching bytes
# Iterate characters at each position to find the one that increases count
```

**Key insight:** Replacing memcmp via LD_PRELOAD to return match count converts any comparison-based validation into a byte-by-byte oracle. Combined with GDB scripting, this automates bruteforce of password/flag checks without reversing the validation algorithm.

**Detection:** Binary uses `memcmp` or `strcmp` for flag validation (visible in `ltrace` output or import table). The comparison function is called with user input and a computed/stored expected value.

**References:** Blaze CTF 2018


---

## 附录：高级工具与反混淆参考

﻿# CTF Reverse - Advanced Tools & Deobfuscation

Advanced tooling for commercial packers/protectors, binary diffing, deobfuscation frameworks, emulation, and symbolic execution beyond angr.

## Table of Contents
- [VMProtect Analysis](#vmprotect-analysis)
  - [Recognition](#recognition)
  - [Approach](#approach)
  - [Tools](#tools)
  - [CTF Strategy](#ctf-strategy)
- [Themida / WinLicense Analysis](#themida--winlicense-analysis)
  - [Themida Recognition](#themida-recognition)
  - [Approach for CTF](#approach-for-ctf)
- [Binary Diffing](#binary-diffing)
  - [BinDiff](#bindiff)
  - [Diaphora](#diaphora)
- [Deobfuscation Frameworks](#deobfuscation-frameworks)
  - [D-810 (IDA)](#d-810-ida)
  - [GOOMBA (Ghidra)](#goomba-ghidra)
  - [Miasm](#miasm)
- [Qiling Framework (Emulation)](#qiling-framework-emulation)
- [Triton (Dynamic Symbolic Execution)](#triton-dynamic-symbolic-execution)
- [Manticore (Symbolic Execution)](#manticore-symbolic-execution)
- [Rizin / Cutter](#rizin--cutter)
- [RetDec (Retargetable Decompiler)](#retdec-retargetable-decompiler)
- [Custom VM Bytecode Lifting to LLVM IR (Google CTF 2017)](#custom-vm-bytecode-lifting-to-llvm-ir-google-ctf-2017)
- [Advanced GDB Techniques](#advanced-gdb-techniques)
  - [Python Scripting](#python-scripting)
  - [Brute-Force with GDB Script](#brute-force-with-gdb-script)
  - [Conditional Breakpoints](#conditional-breakpoints)
  - [Watchpoints](#watchpoints)
  - [Reverse Debugging (rr)](#reverse-debugging-rr)
  - [GDB Dashboard / GEF / pwndbg](#gdb-dashboard--gef--pwndbg)
- [Advanced Ghidra Scripting](#advanced-ghidra-scripting)
- [Patching Strategies](#patching-strategies)
  - [Binary Ninja Patching (Python API)](#binary-ninja-patching-python-api)
  - [LIEF (Library for Instrumenting Executable Formats)](#lief-library-for-instrumenting-executable-formats)
- [GDB Constraint Extraction with ILP/LP Solver (BackdoorCTF 2017)](#gdb-constraint-extraction-with-ilplp-solver-backdoorctf-2017)
- [GDB Position-Encoded Input with Zero Flag Monitoring (EKOPARTY 2017)](#gdb-position-encoded-input-with-zero-flag-monitoring-ekoparty-2017)
- [LD_PRELOAD to Dump Execute-Only Binary (BackdoorCTF 2017)](#ld_preload-to-dump-execute-only-binary-backdoorctf-2017)

---

## VMProtect Analysis

VMProtect virtualizes x86/x64 code into custom bytecode interpreted by a generated VM. One of the most challenging protectors in CTF.

### Recognition

```bash
# VMProtect signatures
strings binary | grep -i "vmp\|vmprotect"
# PE sections: .vmp0, .vmp1 (VMProtect adds its own sections)
readelf -S binary | grep ".vmp"
# Large binary with entropy > 7.5 in certain sections
```

**Key indicators:**
- `push` / `pop` heavy prologues (VM entry pushes all registers to stack)
- Large switch-case dispatcher (the VM handler loop)
- Anti-debug checks embedded in VM handlers
- Mutation engine: same opcode has different handlers per build

### Approach

```text
1. Identify VM entry points — look for pushad/pushaq-like sequences
2. Find the handler table — large indirect jump (jmp [reg + offset])
3. Trace handler execution — each handler ends with jump to next
4. Identify handlers:
   - vAdd, vSub, vMul, vXor, vNot (arithmetic)
   - vPush, vPop (stack operations)
   - vLoad, vStore (memory access)
   - vJmp, vJcc (control flow)
   - vRet (VM exit — restores real registers)
5. Build disassembler for VM bytecode
6. Simplify / deobfuscate the lifted IL
```

### Tools

- **VMPAttack** (IDA plugin): Automatically identifies VM handlers
- **NoVmp**: Devirtualization via VTIL (open-source)
- **VMProtect devirtualizer scripts**: Community IDA/Binary Ninja scripts
- **Approach for CTF:** Often easier to trace specific operations (crypto, comparisons) than fully devirtualize

### CTF Strategy

```python
# Trace VM execution dynamically to extract operations on flag
# Hook VM handler dispatch to log opcode + operands

import frida

script = """
var vm_dispatch = ptr('0x...');  // Address of handler table jump
Interceptor.attach(vm_dispatch, {
    onEnter(args) {
        // Log handler index and stack state
        var handler_idx = this.context.rax;  // or whichever register
        console.log('Handler:', handler_idx, 'RSP:', this.context.rsp);
    }
});
"""
```

**Key insight:** Full devirtualization is rarely needed for CTF. Focus on tracing what operations are performed on your input. Hook comparison/crypto functions called from within the VM.

---

## Themida / WinLicense Analysis

Similar to VMProtect but with additional anti-debug layers.

### Themida Recognition
- Sections: `.themida`, `.winlice`
- Extremely heavy anti-debug (kernel-level checks, driver installation)
- Code mutation + virtualization + packing combined

### Approach for CTF
1. **Dump unpacked code:** Let it run, dump process memory after unpacking
2. **Bypass anti-debug:** ScyllaHide in x64dbg with Themida-specific preset
3. **Fix imports:** Use Scylla plugin for IAT reconstruction
4. **Focus on dumped code:** Once unpacked, analyze as normal binary

```bash
# x64dbg workflow for Themida:
1. Load binary
2. Enable ScyllaHide → Profile: Themida
3. Run to OEP (Original Entry Point) — may need several attempts
4. Dump with Scylla: OEP → IAT Autosearch → Get Imports → Dump
5. Fix dump: Scylla → Fix Dump
6. Analyze fixed dump in Ghidra/IDA
```

---

## Binary Diffing

Critical for patch analysis, 1-day exploit development, and CTF challenges that provide two versions of a binary.

### BinDiff

```bash
# Export from IDA/Ghidra first, then diff
# IDA: File → BinExport → Export as BinExport2
# Ghidra: Use BinExport plugin

# Command line diffing
bindiff primary.BinExport secondary.BinExport
# Opens in BinDiff GUI — shows matched/unmatched functions
```

**Key metrics:**
- Similarity score (0.0-1.0) per function pair
- Changed instructions highlighted
- Unmatched functions = new/removed code

### Diaphora

Free, open-source alternative to BinDiff, runs as IDA plugin.

```bash
# In IDA:
# File → Script file → diaphora.py
# Export first binary, then open second and diff

# Ghidra version: diaphora_ghidra.py
```

**Useful for CTF:** When challenge provides "patched" and "original" binaries, diff reveals the vulnerability or hidden functionality.

---

## Deobfuscation Frameworks

> OLLVM 脱密的完整工作流、变种生态和社区工具调研见 [ollvm-deobfuscation.md](references/ollvm-deobfuscation.md)。

### d810-ng (IDA) — 本地首选

D-810 的现代维护版（Next Generation），集成 **Z3 SMT** 求解器，覆盖 OLLVM / Tigress / Hodur(PlugX) / Approov 多种变种。

```text
Capabilities:
- MBA simplification (Z3-verified): (a ^ b) + 2*(a & b) → a + b
- Opaque predicate removal (Pred0/PredFF/PredSetz/PredSetnz)
- Constant folding (22 rules)
- Control flow unflattening (多种 unflattener):
  * Unflattener           → O-LLVM (switch/if-chain)
  * UnflattenerSwitchCase → Tigress (m_jtbl)
  * UnflattenerTigressIndirect → Tigress (m_ijmp)
  * HodurUnflattener      → Hodur/PlugX (while(1) + jnz state)
  * BadWhileLoop          → Approov (0xF6000–0xF6FFF 状态常量)
- Hacker's Delight 位运算等价
- PlugX (Hodur) 恶意软件专用 MBA 模式

Installation: clone → 复制到 IDA plugins 目录 → Ctrl-Shift-D 加载
Source: https://github.com/w00tzenheimer/d810-ng
```

### obpo-plugin (IDA) — 效果最强，云插件

基于 Hex-Rays **microcode** + 数据流跟踪 + 程序切片 + 混合执行（concolic）。社区公认效果最强之一。

```text
- 在 microcode 层优化反编译输出（不是改 ASM）
- 支持 IDA 7.5-7.7 + Hex-Rays，多架构 (ARM/ARM64/x86/x64/PPC/MIPS)
- 云插件：目标函数上传 obpo-server 处理（核心闭源，插件免费）
- ⚠️ 敏感样本慎用（二进制上传云服务）
- 用法：右键 dispatcher → OBPO → Mark and process function
Source: https://github.com/obpo-project/obpo-plugin
```

### ollvm-unflattener — Miasm 纯脚本

无 IDA 依赖，基于 Miasm 符号执行，BFS 多层处理，支持 x86/x64 Win/Linux。

```bash
git clone https://github.com/cdong1012/ollvm-unflattener
pip install -r requirements.txt   # miasm, graphviz, keystone-engine
python unflattener -i <input> -o <output> -t <func_addr> -a   # -a 自动多层
```

### ollvm-breaker (Binary Ninja)

Binary Ninja 去平坦化，仓库自带 Android 加固样本 `libvdog.so` 实战。Source: amimo/ollvm-breaker

### DeObfBR — BR 混淆专项

专门去除 Goron/Arkari 风格的 BR（间接分支）混淆。简易技巧：设置数据段只读可部分对抗。Source: Mrack/DeObfBR

### deollvm — ARM64 Unicorn

无 IDA 时处理 ARM64 .so 的备选，基于 Unicorn。Source: GeT1t/deollvm

### GOOMBA (Ghidra)

```text
GOOMBA (Ghidra-based Obfuscated Object Matching and Bytes Analysis):
- Integrates with Ghidra's P-Code
- Simplifies MBA expressions
- Pattern matching for known obfuscation

Installation: Copy .jar to Ghidra extensions
Usage: Code Browser → Analysis → GOOMBA
```

### Miasm

Powerful reverse engineering framework with symbolic execution and IR lifting.

```python
from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.expression import *

# Load binary and lift to Miasm IR
cont = Container.from_stream(open("binary", "rb"))
machine = Machine(cont.arch)
mdis = machine.dis_engine(cont.bin_stream, loc_db=cont.loc_db)

# Disassemble function
asmcfg = mdis.dis_multiblock(entry_addr)

# Lift to IR
lifter = machine.lifter_model_call(loc_db=cont.loc_db)
ircfg = lifter.new_ircfg_from_asmcfg(asmcfg)

# Symbolic execution
from miasm.ir.symbexec import SymbolicExecutionEngine
sb = SymbolicExecutionEngine(lifter)
# Execute symbolically, then simplify expressions
```

**Use case:** Deobfuscate expression trees, simplify complex arithmetic, trace data flow through obfuscated code.

---

## Qiling Framework (Emulation)

Cross-platform emulation framework built on Unicorn, with OS-level support (syscalls, filesystem, registry).

```python
from qiling import Qiling
from qiling.const import QL_VERBOSE

# Emulate Linux ELF
ql = Qiling(["./binary"], "rootfs/x8664_linux",
            verbose=QL_VERBOSE.DEBUG)

# Hook specific address
@ql.hook_address
def hook_check(ql, address, size):
    if address == 0x401234:
        ql.arch.regs.rax = 0  # Bypass check
        ql.log.info("Anti-debug bypassed")

# Hook syscall
@ql.hook_syscall(name="ptrace")
def hook_ptrace(ql, request, pid, addr, data):
    return 0  # Always succeed

# Hook API (Windows)
@ql.set_api("IsDebuggerPresent", target=ql.os.user_defined_api)
def hook_isdebug(ql, address, params):
    return 0

ql.run()
```

**Advantages over Unicorn:**
- OS emulation (file I/O, network, registry)
- Multi-platform (Linux, Windows, macOS, Android, UEFI)
- Built-in debugger interface
- Rootfs for library loading

**CTF use cases:**
- Emulate binaries for foreign architectures (ARM, MIPS, RISC-V)
- Bypass all anti-debug at once (no debugger artifacts)
- Fuzz embedded/IoT firmware without hardware
- Trace execution without code modification

---

## Triton (Dynamic Symbolic Execution)

Pin-based dynamic binary analysis framework with symbolic execution, taint analysis, and AST simplification.

```python
from triton import *

ctx = TritonContext(ARCH.X86_64)

# Load binary sections
with open("binary", "rb") as f:
    binary = f.read()
ctx.setConcreteMemoryAreaValue(0x400000, binary)

# Symbolize input
for i in range(32):
    ctx.symbolizeMemory(MemoryAccess(INPUT_ADDR + i, CPUSIZE.BYTE), f"input_{i}")

# Emulate instructions
pc = ENTRY_POINT
while pc:
    inst = Instruction(pc, ctx.getConcreteMemoryAreaValue(pc, 16))
    ctx.processing(inst)

    # At comparison point, extract path constraint
    if pc == CMP_ADDR:
        ast = ctx.getPathConstraintsAst()
        model = ctx.getModel(ast)
        for k, v in sorted(model.items()):
            print(f"input[{k}] = {chr(v.getValue())}", end="")
        break

    pc = ctx.getConcreteRegisterValue(ctx.registers.rip)
```

**Triton vs angr:**
| Feature | Triton | angr |
|---|---|---|
| Execution | Concrete + symbolic (DSE) | Fully symbolic |
| Speed | Faster (concrete-driven) | Slower (explores all paths) |
| Path explosion | Less prone (follows one path) | Major issue |
| API | C++ / Python | Python |
| Best for | Single-path deobfuscation, taint tracking | Multi-path exploration |

**Key use:** Triton excels at deobfuscation — run the program concretely, but track symbolic state, then simplify the collected constraints.

---

## Manticore (Symbolic Execution)

Trail of Bits' symbolic execution tool. Similar to angr but with native EVM (Ethereum) support.

```python
from manticore.native import Manticore

m = Manticore("./binary")

# Hook success/failure
@m.hook(0x401234)
def success(state):
    buf = state.solve_one_n_batched(state.input_symbols, 32)
    print("Flag:", bytes(buf))
    m.kill()

@m.hook(0x401256)
def fail(state):
    state.abandon()

m.run()
```

**Best for:** simpler Linux binaries and embedded targets. angr is generally more mature for complex RE tasks.

---

## Rizin / Cutter

Rizin is the maintained fork of radare2. Cutter is its Qt-based GUI.

```bash
# Rizin CLI (r2-compatible commands)
rizin -d ./binary
> aaa                    # Analyze all
> afl                    # List functions
> pdf @ main             # Print disassembly
> VV                     # Visual graph mode

# Cutter GUI
cutter binary           # Open in GUI with decompiler
```

**Cutter advantages:**
- Built-in Ghidra decompiler (via r2ghidra plugin)
- Graph view, hex editor, debug panel in one GUI
- Integrated Python/JavaScript scripting console
- Free and open source

---

## RetDec (Retargetable Decompiler)

LLVM-based decompiler supporting many architectures. Free and open-source.

```bash
# Install
pip install retdec-decompiler
# Or use web: https://retdec.com/decompilation/

# CLI
retdec-decompiler binary
# Outputs: binary.c (decompiled C), binary.dsm (disassembly)

# Specific function
retdec-decompiler --select-ranges 0x401000-0x401100 binary
```

**Strengths:** Multi-arch support (x86, ARM, MIPS, PowerPC, PIC32), free, produces compilable C. Good for architectures not well-supported by Ghidra.

---

## Custom VM Bytecode Lifting to LLVM IR (Google CTF 2017)

For complex custom VMs, transpile the VM bytecode to LLVM IR and use LLVM's optimization passes to simplify the code, then decompile the optimized IR.

```python
# Pipeline: VM bytecode → custom disassembler → LLVM IR → optimize → decompile
# 1. Write disassembler for the custom VM opcodes
# 2. Emit LLVM IR for each opcode:
#    INC reg  → %reg = add i32 %reg, 1
#    CDEC reg → conditional decrement
#    CALL fn  → call void @fn()
# 3. Use MCJIT or llc to optimize:
#    opt -O3 -S vm_lifted.ll -o vm_optimized.ll
# 4. Load optimized IR in IDA or decompile with RetDec
# Result: 1300 lines → 150 lines after inlining + constant folding
```

**Key insight:** LLVM's optimization passes (inlining, constant folding, dead code elimination) dramatically simplify lifted VM bytecode. A custom VM with 26 registers and 3 opcodes that produces 1300 lines of IL reduces to ~150 lines after `-O3`, revealing the underlying algorithm (e.g., Collatz sequence computation).

---

## Advanced GDB Techniques

### Python Scripting

```python
# ~/.gdbinit or source from GDB
import gdb

class TraceCompare(gdb.Breakpoint):
    """Log all comparison operations."""
    def __init__(self, addr):
        super().__init__(f"*{addr}", gdb.BP_BREAKPOINT)

    def stop(self):
        frame = gdb.selected_frame()
        rdi = int(frame.read_register("rdi"))
        rsi = int(frame.read_register("rsi"))
        rdx = int(frame.read_register("rdx"))
        # Read compared buffers
        inferior = gdb.selected_inferior()
        buf1 = inferior.read_memory(rdi, rdx).tobytes()
        buf2 = inferior.read_memory(rsi, rdx).tobytes()
        print(f"memcmp({buf1!r}, {buf2!r}, {rdx})")
        return False  # Don't stop, just log

# Usage in GDB:
# (gdb) source trace_cmp.py
# (gdb) python TraceCompare(0x401234)
```

### Brute-Force with GDB Script

```python
# Byte-by-byte brute force via GDB Python API
import gdb, string

def bruteforce_flag(check_addr, success_addr, fail_addr, flag_len):
    flag = []
    for pos in range(flag_len):
        for ch in string.printable:
            candidate = ''.join(flag) + ch + 'A' * (flag_len - pos - 1)
            gdb.execute('start', to_string=True)
            gdb.execute(f'b *{check_addr}', to_string=True)
            # Write candidate to stdin pipe
            # ... (setup input)
            gdb.execute('continue', to_string=True)
            rip = int(gdb.parse_and_eval('$rip'))
            if rip == success_addr:
                flag.append(ch)
                break
        gdb.execute('delete breakpoints', to_string=True)
    return ''.join(flag)
```

### Conditional Breakpoints

```bash
# Break only when register has specific value
(gdb) b *0x401234 if $rax == 0x41
(gdb) b *0x401234 if *(char*)$rdi == 'f'

# Break on Nth hit
(gdb) b *0x401234
(gdb) ignore 1 99    # Skip first 99 hits, break on 100th

# Log without stopping
(gdb) b *0x401234
(gdb) commands
> silent
> printf "rax=%lx rdi=%lx\n", $rax, $rdi
> continue
> end
```

### Watchpoints

```bash
# Hardware watchpoint — break when memory changes
(gdb) watch *(int*)0x601050        # Break on write to address
(gdb) rwatch *(int*)0x601050       # Break on read
(gdb) awatch *(int*)0x601050       # Break on read or write

# Watch a variable by name (needs debug symbols)
(gdb) watch flag_buffer[0]

# Conditional watchpoint
(gdb) watch *(int*)0x601050 if *(int*)0x601050 == 0x42
```

### Reverse Debugging (rr)

```bash
# Record execution
rr record ./binary
# Replay with reverse execution support
rr replay

# In rr replay (GDB commands plus):
(gdb) reverse-continue     # Run backward to previous breakpoint
(gdb) reverse-stepi        # Step backward one instruction
(gdb) reverse-next         # Reverse next
(gdb) when                 # Show current event number

# Set checkpoint and return to it
(gdb) checkpoint
(gdb) restart 1           # Return to checkpoint 1
```

**Key use:** When you step past the critical moment, reverse back instead of restarting. Invaluable for anti-debug that corrupts state.

### GDB Dashboard / GEF / pwndbg

```bash
# pwndbg (most popular for CTF)
# https://github.com/pwndbg/pwndbg
git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh

# Key pwndbg commands:
pwndbg> context           # Show registers, stack, code, backtrace
pwndbg> vmmap             # Memory map (like /proc/self/maps)
pwndbg> search -s "flag{" # Search memory for string
pwndbg> telescope $rsp 20 # Smart stack dump
pwndbg> cyclic 200        # Generate De Bruijn pattern
pwndbg> hexdump $rdi 64   # Pretty hex dump
pwndbg> got               # Show GOT entries
pwndbg> plt               # Show PLT entries

# GEF (alternative)
# https://github.com/hugsy/gef
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"

# Key GEF commands:
gef> xinfo $rdi           # Detailed info about address
gef> checksec             # Binary security features
gef> heap chunks          # Heap chunk listing
gef> pattern create 100   # De Bruijn pattern
```

---

## Advanced Ghidra Scripting

```python
# Ghidra Python (Jython) — run via Script Manager or headless

# Batch rename functions matching a pattern
from ghidra.program.model.symbol import SourceType
fm = currentProgram.getFunctionManager()
for func in fm.getFunctions(True):
    if func.getName().startswith("FUN_"):
        # Check if function contains specific instruction pattern
        body = func.getBody()
        inst_iter = currentProgram.getListing().getInstructions(body, True)
        for inst in inst_iter:
            if inst.getMnemonicString() == "CPUID":
                func.setName("anti_vm_check_" + hex(func.getEntryPoint().getOffset()),
                            SourceType.USER_DEFINED)
                break

# Extract all XOR constants from a function
def extract_xor_constants(func):
    """Find all XOR operations and their immediate operands."""
    constants = []
    body = func.getBody()
    inst_iter = currentProgram.getListing().getInstructions(body, True)
    for inst in inst_iter:
        if inst.getMnemonicString() == "XOR":
            for i in range(inst.getNumOperands()):
                op = inst.getOpObjects(i)
                if op and hasattr(op[0], 'getValue'):
                    constants.append(int(op[0].getValue()))
    return constants

# Bulk decompile and search for pattern
from ghidra.app.decompiler import DecompInterface
decomp = DecompInterface()
decomp.openProgram(currentProgram)

for func in fm.getFunctions(True):
    result = decomp.decompileFunction(func, 30, monitor)
    if result.depiledFunction():
        code = result.getDecompiledFunction().getC()
        if "strcmp" in code or "memcmp" in code:
            print(f"Comparison in {func.getName()} at {func.getEntryPoint()}")
```

---

## Patching Strategies

### Binary Ninja Patching (Python API)

```python
import binaryninja as bn

bv = bn.open_view("binary")

# NOP out instruction
bv.write(0x401234, b"\x90" * 5)  # 5-byte NOP

# Patch conditional jump (JNZ → JZ)
bv.write(0x401234, b"\x74")  # 0x75 (JNZ) → 0x74 (JZ)

# Insert always-true (mov eax, 1; ret)
bv.write(0x401234, b"\xb8\x01\x00\x00\x00\xc3")

bv.save("patched")
```

### LIEF (Library for Instrumenting Executable Formats)

```python
import lief

# Parse and modify ELF/PE/Mach-O
binary = lief.parse("binary")

# Add a new section
section = lief.ELF.Section(".patch")
section.content = list(b"\xcc" * 0x100)
section.type = lief.ELF.SECTION_TYPES.PROGBITS
section.flags = lief.ELF.SECTION_FLAGS.EXECINSTR | lief.ELF.SECTION_FLAGS.ALLOC
binary.add(section)

# Modify entry point
binary.header.entrypoint = 0x401000

# Hook imported function
binary.patch_pltgot("strcmp", 0x401000)

binary.write("patched")
```

**LIEF advantages:** Cross-format (ELF, PE, Mach-O), Python API, can add sections/segments, modify headers, patch imports.

---

## GDB Constraint Extraction with ILP/LP Solver (BackdoorCTF 2017)

When a binary enforces linear arithmetic relationships between input bytes, extract constraints automatically via GDB and solve with an ILP solver.

**Technique:** Send position-encoded input (`input[i] = i`) so that when a comparison fires, you know exactly which positions are involved and what their sum/difference must equal. Collect all constraints from logged comparisons, then feed to PuLP or Gurobi.

```python
from pulp import *

n = 32  # flag length
prob = LpProblem("crackme", LpMinimize)
x = [LpVariable(f'x{i}', 32, 126, cat='Integer') for i in range(n)]
prob += 0  # dummy objective

# Constraints extracted via GDB automation (input[i]=i, monitor comparisons):
prob += x[3] + x[7] == 0xAB
prob += x[1] - x[5] == 0x0C
# ... add all extracted constraints ...

# Constrain to printable ASCII
for xi in x:
    prob += xi >= 32
    prob += xi <= 126

prob.solve(PULP_CBC_CMD(msg=0))
flag = ''.join(chr(int(value(xi))) for xi in x)
print("Flag:", flag)
```

**GDB automation to extract constraints:**
```python
# In GDB Python: set input[i]=i, run, log every CMP instruction result
import gdb

class CmpLogger(gdb.Breakpoint):
    def stop(self):
        frame = gdb.selected_frame()
        # Read compared values, map back to input indices via position encoding
        return False
```

**Key insight:** When a binary enforces linear arithmetic relationships between input bytes, ILP solvers directly find the satisfying assignment once constraints are extracted via GDB automation.

**References:** BackdoorCTF 2017

---

## GDB Position-Encoded Input with Zero Flag Monitoring (EKOPARTY 2017)

Send input where `input[i] = i` (position-encoded). Single-step through the binary monitoring the CPU zero flag (ZF). When ZF is set at a comparison involving a specific position's value, the comparison matched — log the expected value for that position.

```python
import gdb

# Script: single-step binary with position-encoded input, watch ZF
class ZFMonitor(gdb.Breakpoint):
    def stop(self):
        zf = (int(gdb.parse_and_eval('$eflags')) >> 6) & 1
        if zf:
            rip = int(gdb.parse_and_eval('$rip'))
            # Disassemble at rip to find the compared immediate
            disasm = gdb.execute(f'x/1i {rip-5}', to_string=True)
            print(f"ZF set at {rip:#x}: {disasm.strip()}")
        return False

# Run once with input b'\x00\x01\x02\x03...\x1f'
# ZF fires when comparison matches the position's own value -> that IS the key byte
```

Maps each input byte to its required value in one pass without manual reversing.

**Key insight:** Position-encoded input (`input[i]=i`) combined with zero flag monitoring reveals the full key/password in one pass — the zero flag fires when the expected value for position i equals i itself.

**References:** EKOPARTY CTF 2017

---

## LD_PRELOAD to Dump Execute-Only Binary (BackdoorCTF 2017)

A binary has execute-only permissions (mode `--x`, no read bit). The file cannot be read directly or with standard tools, but the kernel still maps it into memory on execution.

LD_PRELOAD a shared library with a constructor that runs inside the process and reads its own memory via `/proc/self/mem`:

```c
// dump_xo.c — compile: gcc -shared -fPIC -o dump_xo.so dump_xo.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

__attribute__((constructor)) void dump() {
    FILE *maps = fopen("/proc/self/maps", "r");
    char line[256];
    unsigned long base = 0, end = 0;

    // Find the execute-only binary's mapping (r-xp or --xp)
    while (fgets(line, sizeof(line), maps)) {
        if (strstr(line, "binary_name")) {
            sscanf(line, "%lx-%lx", &base, &end);
            break;
        }
    }
    fclose(maps);

    FILE *mem = fopen("/proc/self/mem", "rb");
    fseek(mem, base, SEEK_SET);
    size_t size = end - base;
    void *buf = malloc(size);
    fread(buf, 1, size, mem);
    fclose(mem);

    FILE *out = fopen("/tmp/dumped_binary", "wb");
    fwrite(buf, 1, size, out);
    fclose(out);
}
// Usage: LD_PRELOAD=./dump_xo.so ./binary_xo
```

**Key insight:** Execute-only prevents file reading but not execution. LD_PRELOAD constructors run inside the process where `/proc/self/mem` provides access to mapped memory regardless of file permissions.

**References:** BackdoorCTF 2017


---

## 附录：反调试/反分析绕过参考

# CTF Reverse - Anti-Analysis Techniques & Bypasses

Comprehensive reference for anti-debugging, anti-VM, anti-DBI, and integrity-check techniques encountered in CTF challenges, with practical bypasses.

## Table of Contents
- [Linux Anti-Debug (Advanced)](#linux-anti-debug-advanced)
  - [ptrace-Based](#ptrace-based)
  - [/proc Filesystem Checks](#proc-filesystem-checks)
  - [Timing-Based Detection](#timing-based-detection)
  - [Signal-Based Anti-Debug](#signal-based-anti-debug)
  - [Syscall-Level Evasion](#syscall-level-evasion)
- [Windows Anti-Debug (Advanced)](#windows-anti-debug-advanced)
  - [PEB (Process Environment Block) Checks](#peb-process-environment-block-checks)
  - [NtQueryInformationProcess](#ntqueryinformationprocess)
  - [Heap Flags](#heap-flags)
  - [TLS Callbacks](#tls-callbacks)
  - [Hardware Breakpoint Detection](#hardware-breakpoint-detection)
  - [Software Breakpoint Detection (INT3 Scanning)](#software-breakpoint-detection-int3-scanning)
  - [Exception-Based Anti-Debug](#exception-based-anti-debug)
  - [NtSetInformationThread (Thread Hiding)](#ntsetinformationthread-thread-hiding)
- [Anti-VM / Anti-Sandbox](#anti-vm--anti-sandbox)
  - [CPUID Hypervisor Bit](#cpuid-hypervisor-bit)
  - [MAC Address / Hardware Fingerprinting](#mac-address--hardware-fingerprinting)
  - [Timing-Based VM Detection](#timing-based-vm-detection)
  - [File / Registry Artifacts](#file--registry-artifacts)
  - [Resource Checks (CPU Count, RAM, Disk)](#resource-checks-cpu-count-ram-disk)
- [Anti-DBI (Dynamic Binary Instrumentation)](#anti-dbi-dynamic-binary-instrumentation)
  - [Frida Detection](#frida-detection)
  - [Pin/DynamoRIO Detection](#pindynamorio-detection)
- [Code Integrity / Self-Hashing](#code-integrity--self-hashing)
- [Anti-Disassembly Techniques](#anti-disassembly-techniques)
  - [Opaque Predicates](#opaque-predicates)
  - [Junk Bytes / Overlapping Instructions](#junk-bytes--overlapping-instructions)
  - [Jump-in-the-Middle](#jump-in-the-middle)
  - [Function Chunking / Scattered Code](#function-chunking--scattered-code)
  - [Control Flow Flattening (Advanced)](#control-flow-flattening-advanced)
  - [Mixed Boolean-Arithmetic (MBA) Identification & Simplification](#mixed-boolean-arithmetic-mba-identification--simplification)
- [SIGILL Handler for Execution Mode Switching (Hack.lu 2015)](#sigill-handler-for-execution-mode-switching-hacklu-2015)
- [SIGFPE Signal Handler Side-Channel via strace Counting (PlaidCTF 2017)](#sigfpe-signal-handler-side-channel-via-strace-counting-plaidctf-2017)
- [Instruction Trace Inversion with Keystone and Unicorn (MeePwn CTF 2017)](#instruction-trace-inversion-with-keystone-and-unicorn-meepwn-ctf-2017)
- [Call-less Function Chaining via Stack Frame Manipulation (THC CTF 2018)](#call-less-function-chaining-via-stack-frame-manipulation-thc-ctf-2018)
- [Comprehensive Bypass Strategies](#comprehensive-bypass-strategies)
  - [Universal Bypass Checklist](#universal-bypass-checklist)
  - [Layered Anti-Debug (Real-World Pattern)](#layered-anti-debug-real-world-pattern)
  - [Quick Reference: Check to Bypass](#quick-reference-check-to-bypass)

---

## Linux Anti-Debug (Advanced)

### ptrace-Based

**Self-ptrace (most common):**
```c
if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) exit(1); // Already traced = debugger attached
```

**Bypasses:**
```bash
# 1. LD_PRELOAD (see patterns.md for full hook)
LD_PRELOAD=./hook.so ./binary

# 2. Patch with pwntools
python3 -c "
from pwn import *
elf = ELF('./binary', checksec=False)
elf.asm(elf.symbols.ptrace, 'xor eax, eax; ret')
elf.save('patched')
"

# 3. GDB: catch the syscall
gdb ./binary
(gdb) catch syscall ptrace
(gdb) run
# When it stops at ptrace:
(gdb) set $rax = 0
(gdb) continue

# 4. Kernel config (requires root)
echo 0 > /proc/sys/kernel/yama/ptrace_scope
```

**Double-ptrace pattern:**
```c
// Fork child to ptrace parent — blocks all other debuggers
pid_t child = fork();
if (child == 0) {
    ptrace(PTRACE_ATTACH, getppid(), 0, 0);
    // Child sits in waitpid loop, keeping parent traced
} else {
    // Parent continues with real logic
}
```
**Bypass:** Kill the watchdog child process, then attach debugger.

### /proc Filesystem Checks

```c
// TracerPid check
FILE *f = fopen("/proc/self/status", "r");
// Looks for "TracerPid:\t0" — non-zero means debugger

// /proc/self/exe link check (some debuggers change this)
readlink("/proc/self/exe", buf, sizeof(buf));

// /proc/self/maps — check for debugger libraries
grep("frida", "/proc/self/maps");
```

**Bypasses:**
```bash
# 1. LD_PRELOAD fopen/fread to fake /proc contents
# 2. Mount namespace isolation
unshare -m bash -c 'mount --bind /dev/null /proc/self/status && ./binary'

# 3. GDB: set breakpoint at fopen, change filename argument
(gdb) b fopen
(gdb) run
(gdb) set {char[20]} $rdi = "/dev/null"
(gdb) continue
```

### Timing-Based Detection

```c
// rdtsc (CPU timestamp counter)
uint64_t start = __rdtsc();
// ... code ...
uint64_t delta = __rdtsc() - start;
if (delta > THRESHOLD) exit(1);  // too slow = debugger

// clock_gettime
struct timespec ts1, ts2;
clock_gettime(CLOCK_MONOTONIC, &ts1);
// ... code ...
clock_gettime(CLOCK_MONOTONIC, &ts2);

// gettimeofday
struct timeval tv1, tv2;
gettimeofday(&tv1, NULL);
```

**Bypasses:**
```bash
# 1. Frida hook (see tools-dynamic.md for clock_gettime hook)

# 2. GDB: skip rdtsc by patching with constant
(gdb) set {unsigned char[2]} 0x401234 = {0x90, 0x90}  # NOP the rdtsc

# 3. Pin tool to fix TSC reads
# 4. faketime library
LD_PRELOAD=/usr/lib/faketime/libfaketime.so.1 FAKETIME="2024-01-01" ./binary
```

### Signal-Based Anti-Debug

```c
// SIGTRAP handler — INT3 under debugger is caught by debugger, not handler
signal(SIGTRAP, handler);
__asm__("int3");
// If handler runs: no debugger. If debugger catches: debugged.

// SIGALRM timeout — kill self if analysis takes too long
signal(SIGALRM, kill_handler);
alarm(5);

// SIGSEGV handler that does real work (see patterns.md for MBA pattern)
signal(SIGSEGV, real_logic_handler);
*(int*)0 = 0;  // deliberate crash → handler runs real code
```

**Bypasses:**
```bash
# GDB: pass signals to program instead of handling them
(gdb) handle SIGTRAP nostop pass
(gdb) handle SIGALRM ignore
(gdb) handle SIGSEGV nostop pass

# For alarm-based: patch alarm() to return immediately
```

### Syscall-Level Evasion

```c
// Direct syscall instead of libc — bypasses LD_PRELOAD hooks
long ret;
asm volatile("syscall" : "=a"(ret) : "a"(101), "D"(0), "S"(0), "d"(0), "r"(0));
// Syscall 101 = ptrace on x86_64
```

**Bypass:** Must patch the binary itself or use ptrace to intercept at syscall level.
```bash
# GDB: catch syscall
(gdb) catch syscall 101
(gdb) commands
> set $rax = 0
> continue
> end
```

---

## Windows Anti-Debug (Advanced)

### PEB (Process Environment Block) Checks

```c
// BeingDebugged flag (offset 0x2 in PEB)
bool debugged = NtCurrentPeb()->BeingDebugged;

// NtGlobalFlag (offset 0x68/0xBC in PEB)
// When debugger: FLG_HEAP_ENABLE_TAIL_CHECK | FLG_HEAP_ENABLE_FREE_CHECK | FLG_HEAP_VALIDATE_PARAMETERS = 0x70
DWORD flags = *(DWORD*)((BYTE*)NtCurrentPeb() + 0xBC); // 64-bit offset
if (flags & 0x70) exit(1);
```

**Bypass (x64dbg):**
```text
# ScyllaHide plugin auto-patches PEB fields
# Manual: dump PEB, zero BeingDebugged and NtGlobalFlag
```

### NtQueryInformationProcess

```c
// ProcessDebugPort (0x7)
DWORD_PTR debugPort = 0;
NtQueryInformationProcess(GetCurrentProcess(), 7, &debugPort, sizeof(debugPort), NULL);
if (debugPort != 0) exit(1);

// ProcessDebugObjectHandle (0x1E)
HANDLE debugObj = NULL;
NTSTATUS status = NtQueryInformationProcess(GetCurrentProcess(), 0x1E, &debugObj, sizeof(debugObj), NULL);
if (status == 0) exit(1); // STATUS_SUCCESS means debugger present

// ProcessDebugFlags (0x1F) — returns inverse: 0 = debugger present
DWORD noDebug = 0;
NtQueryInformationProcess(GetCurrentProcess(), 0x1F, &noDebug, sizeof(noDebug), NULL);
if (noDebug == 0) exit(1);
```

**Bypass:** Hook `NtQueryInformationProcess` to return fake values, or use ScyllaHide.

### Heap Flags

```c
// Process heap has debug flags when debugger attached
PHEAP heap = (PHEAP)GetProcessHeap();
// Flags at offset 0x70 (64-bit): should be HEAP_GROWABLE (0x2)
// ForceFlags at offset 0x74: should be 0
if (heap->Flags != 0x2 || heap->ForceFlags != 0) exit(1);
```

### TLS Callbacks

**Key technique:** TLS (Thread Local Storage) callbacks execute BEFORE `main()` / entry point.

```c
// Registered in PE header's TLS directory
void NTAPI TlsCallback(PVOID DllHandle, DWORD Reason, PVOID Reserved) {
    if (Reason == DLL_PROCESS_ATTACH) {
        if (IsDebuggerPresent()) {
            ExitProcess(1);  // Kills process before main runs
        }
    }
}

#pragma comment(linker, "/INCLUDE:_tls_used")
#pragma data_seg(".CRT$XLB")
PIMAGE_TLS_CALLBACK callbacks[] = { TlsCallback, NULL };
```

**Detection in IDA/Ghidra:** Check PE TLS Directory → AddressOfCallBacks. Functions listed there run before EP.

**Bypass:** Set breakpoint on TLS callback in x64dbg (Options → Events → TLS Callbacks), or patch the TLS directory entry.

### Hardware Breakpoint Detection

```c
// Read debug registers via GetThreadContext
CONTEXT ctx;
ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
GetThreadContext(GetCurrentThread(), &ctx);
if (ctx.Dr0 || ctx.Dr1 || ctx.Dr2 || ctx.Dr3) exit(1);

// Also via exception handler: deliberate exception, check DR regs in handler
```

**Bypass:**
```bash
# x64dbg: use software breakpoints instead, or hook GetThreadContext
# Frida: hook GetThreadContext to zero DR registers
```

### Software Breakpoint Detection (INT3 Scanning)

```c
// CRC / hash check over code section
unsigned char *code = (unsigned char*)function_addr;
uint32_t checksum = 0;
for (int i = 0; i < code_size; i++) {
    checksum += code[i];
    if (code[i] == 0xCC) exit(1);  // INT3 = software breakpoint
}
if (checksum != EXPECTED_CHECKSUM) exit(1);
```

**Bypass:** Use hardware breakpoints (DR0-DR3) instead of software breakpoints. Or hook the scanning function.

### Exception-Based Anti-Debug

```c
// UnhandledExceptionFilter — under debugger, filter is NOT called
SetUnhandledExceptionFilter(handler);
RaiseException(EXCEPTION_ACCESS_VIOLATION, 0, 0, NULL);
// If handler runs: no debugger
// If debugger catches: debugger present

// INT 2D — debugger single-step anomaly
__asm { int 2dh }  // Debugger silently consumes the exception
// If execution continues: debugger present
```

### NtSetInformationThread (Thread Hiding)

```c
// Hide thread from debugger — stops all debug events
typedef NTSTATUS(NTAPI *pNtSIT)(HANDLE, ULONG, PVOID, ULONG);
pNtSIT NtSIT = (pNtSIT)GetProcAddress(GetModuleHandle("ntdll"), "NtSetInformationThread");
NtSIT(GetCurrentThread(), 0x11 /*ThreadHideFromDebugger*/, NULL, 0);
// After this, debugger won't see breakpoints or exceptions from this thread
```

**Bypass:** Hook `NtSetInformationThread` to ignore class 0x11, or patch the call.

---

## Anti-VM / Anti-Sandbox

### CPUID Hypervisor Bit

```c
int regs[4];
__cpuid(regs, 1);
if (regs[2] & (1 << 31)) {  // ECX bit 31 = hypervisor present
    exit(1);
}

// Hypervisor brand string
__cpuid(regs, 0x40000000);
char brand[13] = {0};
memcpy(brand, &regs[1], 12);
// "VMwareVMware", "Microsoft Hv", "KVMKVMKVM", "XenVMMXenVMM"
```

**Bypass:** Patch `cpuid` results or use `LD_PRELOAD` to hook wrapper functions.

### MAC Address / Hardware Fingerprinting

```text
Known VM MAC prefixes:
  VMware:     00:0C:29, 00:50:56
  VirtualBox: 08:00:27
  Hyper-V:    00:15:5D
  Parallels:  00:1C:42
  QEMU:       52:54:00
```

### Timing-Based VM Detection

```c
// VM exits on privileged instructions are measurably slower
uint64_t start = __rdtsc();
__cpuid(regs, 0);  // Forces VM exit
uint64_t delta = __rdtsc() - start;
if (delta > 500) { /* likely VM */ }
```

### File / Registry Artifacts

```text
Files: C:\Windows\System32\drivers\vm*.sys, vbox*.dll, VBoxService.exe
Registry: HKLM\SOFTWARE\VMware, Inc.\VMware Tools
Services: VMTools, VBoxService
Processes: vmtoolsd.exe, VBoxTray.exe, qemu-ga.exe
Linux: /sys/class/dmi/id/product_name contains "VirtualBox"|"VMware"
       dmesg | grep -i "hypervisor detected"
```

### Resource Checks (CPU Count, RAM, Disk)

```c
// Sandboxes typically have minimal resources
SYSTEM_INFO si;
GetSystemInfo(&si);
if (si.dwNumberOfProcessors < 2) exit(1);

MEMORYSTATUSEX ms;
ms.dwLength = sizeof(ms);
GlobalMemoryStatusEx(&ms);
if (ms.ullTotalPhys < 2ULL * 1024 * 1024 * 1024) exit(1); // < 2GB RAM

// Disk size check (< 60GB = sandbox)
GetDiskFreeSpaceEx("C:\\", NULL, &total, NULL);
```

**Bypass:** Use a VM configured with adequate resources (4+ CPUs, 8GB+ RAM, 100GB+ disk).

---

## Anti-DBI (Dynamic Binary Instrumentation)

### Frida Detection

```c
// 1. Check /proc/self/maps for frida-agent
FILE *f = fopen("/proc/self/maps", "r");
while (fgets(line, sizeof(line), f)) {
    if (strstr(line, "frida") || strstr(line, "gadget")) exit(1);
}

// 2. Check for Frida's default port (27042)
int sock = socket(AF_INET, SOCK_STREAM, 0);
struct sockaddr_in addr = {.sin_family=AF_INET, .sin_port=htons(27042), .sin_addr.s_addr=inet_addr("127.0.0.1")};
if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) == 0) exit(1);

// 3. Check for inline hooks (function prologue modification)
// Compare first bytes of libc functions against expected values
unsigned char *strcmp_bytes = (unsigned char *)strcmp;
if (strcmp_bytes[0] == 0xE9 || strcmp_bytes[0] == 0xFF) exit(1); // JMP = hooked

// 4. Thread name check
// Frida creates threads with names like "gmain", "gdbus", "frida-*"
DIR *dir = opendir("/proc/self/task");
while ((entry = readdir(dir))) {
    char comm_path[256];
    snprintf(comm_path, sizeof(comm_path), "/proc/self/task/%s/comm", entry->d_name);
    // Read comm and check for "gmain", "gdbus"
}

// 5. Named pipe detection (Windows)
// Frida creates \\.\pipe\frida-* named pipes
```

**Frida bypass of Frida detection:**
```javascript
// Hook the detection functions themselves
Interceptor.attach(Module.findExportByName(null, "strstr"), {
    onEnter(args) {
        this.haystack = Memory.readUtf8String(args[0]);
        this.needle = Memory.readUtf8String(args[1]);
    },
    onLeave(retval) {
        if (this.needle && (this.needle.includes("frida") || this.needle.includes("gadget"))) {
            retval.replace(ptr(0)); // Not found
        }
    }
});

// Early Frida load (before anti-DBI runs)
// Use frida-gadget as early-init shared library
```

### Pin/DynamoRIO Detection

```c
// Check for instrumentation libraries in /proc/self/maps
// Pin: "pin-", "pinbin", "pinatrace"
// DynamoRIO: "dynamorio", "drcov", "drrun"

// Instruction count timing — DBI adds overhead
// Execute known instruction sequence, compare execution time
```

---

## Code Integrity / Self-Hashing

```c
// CRC32 over .text section
uint32_t crc = compute_crc32(text_start, text_size);
if (crc != EXPECTED_CRC) exit(1);  // Code was modified (breakpoints, patches)

// MD5/SHA256 of function bodies
unsigned char hash[32];
SHA256(function_addr, function_size, hash);
if (memcmp(hash, expected_hash, 32) != 0) exit(1);
```

**Bypasses:**
1. **Hardware breakpoints** (don't modify code, DR0-DR3)
2. **Patch the comparison** to always succeed
3. **Hook the hash function** to return expected value
4. **Emulate** instead of debug (Unicorn/Qiling — no code modification)
5. **Snapshot + restore:** dump memory before and after, diff to find checks

**Self-checksumming in loops:**
```c
// Continuous integrity check in separate thread
void *watchdog(void *arg) {
    while (1) {
        if (compute_crc32(text_start, text_end - text_start) != saved_crc) {
            memset(flag_buffer, 0, flag_len);  // Destroy flag
            exit(1);
        }
        usleep(100000);
    }
}
```
**Bypass:** Kill the watchdog thread or patch its sleep to infinite.

---

## Anti-Disassembly Techniques

### Opaque Predicates

```asm
; Condition that always evaluates the same way but looks data-dependent
mov eax, [some_memory]
imul eax, eax          ; x^2
and eax, 1             ; x^2 mod 2 is always 0 for any x
jnz fake_branch        ; Never taken, but disassembler doesn't know
; real code here
```

**Identification:** Z3/SMT can prove branch is always/never taken.

### Junk Bytes / Overlapping Instructions

```asm
jmp real_code
db 0xE8           ; Looks like start of CALL to linear disassembler
real_code:
mov eax, 1        ; Real code — disassembler may misalign here
```

**Fix:** Switch to graph-mode disassembly (Ghidra/IDA handle this well). Manual: undefine and re-analyze from correct offset.

### Jump-in-the-Middle

```asm
; Jumps into the middle of a multi-byte instruction
eb 01          ; jmp +1 (skip next byte)
e8             ; fake CALL opcode — disassembler tries to decode as call
90             ; real: NOP (landed here from jmp)
```

### Function Chunking / Scattered Code

Functions split into non-contiguous chunks connected by unconditional jumps. Defeats linear function boundary detection.

**Tool:** IDA's "Append function tail" or Ghidra's "Create function" at each chunk.

### Control Flow Flattening (Advanced)

> 完整的 OLLVM 脱密工作流、变种生态（Hikari/Polaris/O-MVLL/Tigress/Hodur 等）和社区工具调研见 [ollvm-deobfuscation.md](references/ollvm-deobfuscation.md)。

Beyond basic switch-case (see patterns.md): modern OLLVM variants use:
- **Bogus control flow:** Fake branches with opaque predicates
- **Instruction substitution:** `a + b` → `a - (-b)`, `a ^ b` → `(a | b) & ~(a & b)`
- **String encryption:** Strings decrypted at runtime, cleared after use

**现代变种（2026 社区活跃）：** Hikari (Anti Class Dump/String Encryption/Indirect Branch), Polaris (原 Pluto, 含 Trap Angr 专门坑 angr), O-MVLL (Python 驱动, Android 加固常用), Arkari (goron 基础, 间接跳转可被数据段只读对抗), amice (Rust, 含 VM Flatten 需 VM 逆向而非 deflat)。变种识别详见 ollvm-deobfuscation.md 第 1 节。

**Deobfuscation tools (社区活跃度排序):**
- **obpo-plugin** (629⭐, IDA microcode+concolic 云插件, 效果最强): https://github.com/obpo-project/obpo-plugin
- **ollvm-breaker** (441⭐, Binary Ninja, Android .so 实战): https://github.com/amimo/ollvm-breaker
- **ollvm-unflattener** (265⭐, Miasm 符号执行, 纯脚本 x86/x64): https://github.com/cdong1012/ollvm-unflattener
- **d810-ng** (223⭐, IDA, 集成 Z3, 覆盖 OLLVM/Tigress/Hodur/Approov): https://github.com/w00tzenheimer/d810-ng — **本地首选**
- **DeObfBR** (96⭐, BR 间接分支混淆专项): https://github.com/Mrack/DeObfBR
- **D-810** (原版, 已较少维护, 建议用 d810-ng): pattern-based deobfuscation, MBA simplification
- **Miasm**: Symbolic execution for deobfuscation
- **Arybo** / **SiMBA**: MBA expression simplification

```bash
# d810-ng: 复制到 IDA plugins 目录, Ctrl-Shift-D 加载
# 选择 Unflattener + MBA simplification + Opaque predicate removal
# obpo: 右键 dispatcher → OBPO → Mark and process function (需联网)
# ⚠️ Pluto/Polaris 的 Trap Angr pass 会让 angr 失效 → 改用 d810-ng/Unicorn
```

### Mixed Boolean-Arithmetic (MBA) Identification & Simplification

```python
# Common MBA patterns and their simplified forms:
# (x & y) + (x | y) == x + y
# (x ^ y) + 2*(x & y) == x + y
# (x | y) - (x & ~y) == y
# ~(~x & ~y) == x | y (De Morgan's)
# (x | y) & ~(x & y) == x ^ y

# SiMBA tool for automated simplification:
# pip install simba-simplifier
from simba import simplify_mba
expr = "(a | b) + (a & b) - (~a & b)"
print(simplify_mba(expr))  # → a
```

---

## SIGILL Handler for Execution Mode Switching (Hack.lu 2015)

Binaries may install SIGILL (illegal instruction) handlers to switch between x86 and x86-64 execution modes or implement custom opcode dispatch:

1. **Signal registration:** `signal(SIGILL, handler)` installs a callback for illegal instruction exceptions
2. **Mode switching:** The handler modifies the saved instruction pointer or segment registers to switch between 32-bit and 64-bit code
3. **Custom opcodes:** Invalid x86 instructions trigger the handler, which interprets operand bytes as custom VM opcodes

```c
// Signal handler decodes "illegal" instructions as custom opcodes
void sigill_handler(int sig, siginfo_t *info, void *ucontext) {
    ucontext_t *ctx = (ucontext_t *)ucontext;
    unsigned char *pc = (unsigned char *)ctx->uc_mcontext.gregs[REG_RIP];
    // Decode custom opcode from bytes at PC
    // Advance PC past the custom instruction
    ctx->uc_mcontext.gregs[REG_RIP] += opcode_length;
}
```

**Key insight:** If a binary installs signal handlers for SIGILL/SIGSEGV/SIGTRAP early in execution, suspect custom instruction dispatch. Trace signal deliveries with `strace -e signal` or set GDB to not intercept: `handle SIGILL nostop pass`.

---

## SIGFPE Signal Handler Side-Channel via strace Counting (PlaidCTF 2017)

Binary uses SIGFPE signal handlers for control flow, making static analysis unreliable. Brute-force by counting SIGFPE signals via strace — correct input characters produce more signals.

```bash
# Count SIGFPE signals per input character guess
for c in {a..z} {A..Z} {0..9}; do
    count=$(echo -n "${c}AAAAAAA" | strace -e signal=SIGFPE ./binary 2>&1 | grep -c SIGFPE)
    echo "$c: $count"
done
# Character producing the most SIGFPEs is correct
# Repeat for each position, extending the known prefix
```

**Key insight:** Signal handlers (SIGFPE, SIGSEGV, SIGILL) create implicit control flow invisible to static analysis. The number of signals raised correlates with validation progress. Counting signals via `strace -e signal=SIGFPE` turns opaque signal-based validation into a measurable side-channel for character-by-character brute-force.

---

## Instruction Trace Inversion with Keystone and Unicorn (MeePwn CTF 2017)

UPX-packed binary applies a sequence of arithmetic-only transforms (sub, add, xor, rol, ror) to the flag. No memory side-effects — purely register arithmetic. IDAPython traces non-jump instructions, the sequence is then inverted to recover the flag.

**Inversion rules:**
- Reverse the instruction sequence (last instruction first)
- Swap inverse pairs: `add ↔ sub`, `rol ↔ ror`, `xor` is self-inverse

```python
# IDAPython: collect non-jump instructions in the obfuscated routine
import idaapi, idc

def trace_transforms(start_ea, end_ea):
    instructions = []
    ea = start_ea
    while ea < end_ea:
        mnem = idc.print_insn_mnem(ea)
        if mnem not in ('jmp', 'je', 'jne', 'call', 'ret'):
            instructions.append((ea, mnem, idc.print_operands(ea)))
        ea = idc.next_head(ea)
    return instructions

transforms = trace_transforms(0x401000, 0x401200)

# Invert: reverse order, swap add/sub and rol/ror
inverse_map = {'add': 'sub', 'sub': 'add', 'rol': 'ror', 'ror': 'rol', 'xor': 'xor'}
inverted = [(mnem, op) for (_, mnem, op) in reversed(transforms)]
inverted = [(inverse_map.get(m, m), op) for m, op in inverted]
```

```python
# Assemble inverted instructions with Keystone, emulate with Unicorn
from keystone import *
from unicorn import *
from unicorn.x86_const import *

ks = Ks(KS_ARCH_X86, KS_MODE_64)
uc = Uc(UC_ARCH_X86, UC_MODE_64)

asm_src = '\n'.join(f'{mnem} {op}' for mnem, op in inverted)
encoding, _ = ks.asm(asm_src)

CODE_BASE = 0x400000
uc.mem_map(CODE_BASE, 0x10000)
uc.mem_write(CODE_BASE, bytes(encoding))

# Set initial register state to the observed output value
uc.reg_write(UC_X86_REG_RAX, known_output)
uc.emu_start(CODE_BASE, CODE_BASE + len(encoding))
flag_bytes = uc.reg_read(UC_X86_REG_RAX).to_bytes(8, 'little')
```

**PEB anti-debug note:** If the binary reads `PEB.BeingDebugged` and uses it to select between two comparison target values, the traced instructions under IDAPython may use the debug-mode target. Patch `BeingDebugged` to 0 before tracing, or identify both branches and use the non-debug target value.

**Key insight:** Arithmetic-only obfuscation (no memory writes) is fully reversible by tracing, inverting the instruction sequence, and swapping inverse operations. PEB anti-debug can silently change comparison targets — always verify which branch is taken.

**References:** MeePwn CTF 2017

---

### Call-less Function Chaining via Stack Frame Manipulation (THC CTF 2018)

**Pattern:** Binary hides function calls by building a linked list of function pointers on the stack, then modifying saved RBP and return addresses so `leave; ret` instructions chain through the list without any explicit `CALL` instructions. IDA fails to decompile because push/pop are unbalanced and function boundaries cannot be determined.

Each function in the chain:
1. Pushes operands and the next function's address onto the stack
2. Sets saved RBP to point to the next stack frame
3. Sets the return address to the next function
4. `leave` restores RSP from RBP (moving to next frame), `ret` jumps to the next function

```python
# Reversed processing chain (each function applied via leave/ret):
def reverse_processing(byte):
    res = byte | 0x80       # OR 0x80
    res = res ^ 0xCA        # XOR 0xCA
    res = (res + 66) & 0xFF # ADD 66
    res = res ^ 0xCA        # XOR 0xCA (repeated)
    res = (res + 66) & 0xFF
    res = res ^ 0xCA
    res = (res + 66) & 0xFF
    res = res ^ 0xFE        # XOR 0xFE (final)
    return res
# Apply in reverse order, then reverse the character sequence
```

**Key insight:** By manipulating saved RBP to point to the next stack frame and saved RIP to the next function, `leave; ret` chains through functions without any `call` instructions. Disassemblers that track call/ret balance fail to identify function boundaries. Patch each function body individually for IDA to handle them.

**Detection:** Binary with many small code blocks ending in `leave; ret` but no corresponding `call` instructions. Stack contains interleaved function pointers and data. IDA shows "stack frame is too big" or fails to create functions.

**References:** THC CTF 2018

---

## Comprehensive Bypass Strategies

### Universal Bypass Checklist

1. **Identify all anti-analysis checks** — search for: `ptrace`, `IsDebuggerPresent`, `rdtsc`, `cpuid`, `NtQuery`, `GetTickCount`, `CheckRemoteDebuggerPresent`, `/proc/self`, `SIGTRAP`, `alarm`
2. **Static patching** — NOP/patch checks with pwntools or Ghidra before running
3. **LD_PRELOAD** (Linux) — hook libc functions returning fake values
4. **ScyllaHide** (Windows x64dbg) — patches PEB, hooks NT functions automatically
5. **Emulation** (Unicorn/Qiling) — no debugger artifacts to detect
6. **Kernel-level bypass** — modify `/proc/sys/kernel/yama/ptrace_scope`, use `prctl`

### Layered Anti-Debug (Real-World Pattern)

Many CTF challenges stack multiple checks:
```text
1. TLS callback → IsDebuggerPresent (before main)
2. main() → ptrace(TRACEME)
3. Watchdog thread → timing check + /proc scan
4. Code section → self-CRC32 integrity
5. Signal handler → real logic in SIGSEGV handler
```

**Approach:** Identify ALL checks before patching. Patch or hook each one systematically. Run under emulator if too many to patch individually.

### Quick Reference: Check to Bypass

| Anti-Debug Check | Platform | Bypass |
|---|---|---|
| `ptrace(TRACEME)` | Linux | `LD_PRELOAD`, patch to `ret 0`, `catch syscall` |
| `IsDebuggerPresent` | Windows | ScyllaHide, Frida hook, PEB patch |
| `NtQueryInformationProcess` | Windows | ScyllaHide, hook ntdll |
| `rdtsc` timing | Both | NOP rdtsc, Frida time hook, Pin |
| `/proc/self/status` | Linux | Mount namespace, hook fopen |
| `alarm(N)` | Linux | `handle SIGALRM ignore` in GDB |
| `SIGTRAP` handler | Linux | `handle SIGTRAP nostop pass` |
| `SIGFPE` handler side-channel | Linux | `strace -e signal=SIGFPE` count per input |
| TLS callback | Windows | Break on TLS in x64dbg, patch |
| DR register scan | Windows | Use software BPs, hook GetThreadContext |
| INT3 scan / CRC | Both | Hardware BPs, patch CRC comparison |
| Frida detection | Both | Early-load gadget, hook strstr |
| CPUID hypervisor | Both | Patch CPUID result, bare metal |
| Thread hiding | Windows | Hook NtSetInformationThread |


---

## 附录：二进制模式库参考

# CTF Reverse - Patterns & Techniques

## Table of Contents
- [Custom VM Reversing](#custom-vm-reversing)
  - [Analysis Steps](#analysis-steps)
  - [Common VM Patterns](#common-vm-patterns)
  - [RVA-Based Opcode Dispatching](#rva-based-opcode-dispatching)
  - [State Machine VMs (90K+ states)](#state-machine-vms-90k-states)
  - [Custom VM Reverse Engineering via Fuzzing and Instruction Set Discovery (hxp CTF 2017)](#custom-vm-reverse-engineering-via-fuzzing-and-instruction-set-discovery-hxp-ctf-2017)
- [Anti-Debugging Techniques](#anti-debugging-techniques)
  - [Common Checks](#common-checks)
  - [Bypass Technique](#bypass-technique)
  - [LD_PRELOAD Hook](#ld_preload-hook)
  - [pwntools Binary Patching (Crypto-Cat)](#pwntools-binary-patching-crypto-cat)
- [Nanomites](#nanomites)
  - [Linux (Signal-Based)](#linux-signal-based)
  - [Windows (Debug Events)](#windows-debug-events)
  - [Analysis](#analysis)
- [Self-Modifying Code](#self-modifying-code)
  - [Pattern: XOR Decryption](#pattern-xor-decryption)
- [Known-Plaintext XOR (Flag Prefix)](#known-plaintext-xor-flag-prefix)
  - [Variant: XOR with Position Index](#variant-xor-with-position-index)
- [Mixed-Mode (x86-64 / x86) Stagers](#mixed-mode-x86-64--x86-stagers)
- [LLVM (Low Level Virtual Machine) Obfuscation (Control Flow Flattening)](#llvm-low-level-virtual-machine-obfuscation-control-flow-flattening)
  - [Pattern](#pattern)
  - [De-obfuscation](#de-obfuscation)
- [S-Box / Keystream Generation](#s-box--keystream-generation)
  - [Fisher-Yates Shuffle (Xorshift32)](#fisher-yates-shuffle-xorshift32)
  - [Xorshift64* Keystream](#xorshift64-keystream)
  - [Identifying Patterns](#identifying-patterns)
- [SECCOMP/BPF Filter Analysis](#seccompbpf-filter-analysis)
  - [BPF Analysis](#bpf-analysis)
- [Exception Handler Obfuscation](#exception-handler-obfuscation)
  - [RtlInstallFunctionTableCallback](#rtlinstallfunctiontablecallback)
  - [Vectored Exception Handlers (VEH)](#vectored-exception-handlers-veh)
- [Memory Dump Analysis](#memory-dump-analysis)
  - [When Binary Dumps Memory](#when-binary-dumps-memory)
  - [Known Plaintext Attack](#known-plaintext-attack)
- [Byte-Wise Uniform Transforms](#byte-wise-uniform-transforms)
- [x86-64 Gotchas](#x86-64-gotchas)
  - [Sign Extension](#sign-extension)
  - [Loop Boundary State Updates](#loop-boundary-state-updates)
- [Custom Mangle Function Reversing](#custom-mangle-function-reversing)
- [Position-Based Transformation Reversing](#position-based-transformation-reversing)
- [Hex-Encoded String Comparison](#hex-encoded-string-comparison)
- [Signal-Based Binary Exploration](#signal-based-binary-exploration)
- [Malware Anti-Analysis Bypass via Patching](#malware-anti-analysis-bypass-via-patching)
- [Multi-Stage Shellcode Loaders](#multi-stage-shellcode-loaders)
- [Timing Side-Channel Attack](#timing-side-channel-attack)
- [Multi-Thread Anti-Debug with Decoy + Signal Handler Mixed Boolean-Arithmetic (ApoorvCTF 2026)](#multi-thread-anti-debug-with-decoy--signal-handler-mixed-boolean-arithmetic-apoorvctf-2026)
- [INT3 Patch + Coredump Brute-Force Oracle (Pwn2Win 2016)](#int3-patch--coredump-brute-force-oracle-pwn2win-2016)
- [Signal Handler Chain + LD_PRELOAD Oracle (Nuit du Hack 2016)](#signal-handler-chain--ld_preload-oracle-nuit-du-hack-2016)
- [printf Format String VM Decompilation to Z3 (SECCON 2017)](#printf-format-string-vm-decompilation-to-z3-seccon-2017)

---

## Custom VM Reversing

### Analysis Steps
1. Identify VM structure: registers, memory, instruction pointer
2. Reverse `executeIns`/`runvm` function for opcode meanings
3. Write a disassembler to parse bytecode
4. Decompile disassembly to understand algorithm

### Common VM Patterns
```c
switch (opcode) {
    case 1: *R[op1] *= op2; break;      // MUL
    case 2: *R[op1] -= op2; break;      // SUB
    case 3: *R[op1] = ~*R[op1]; break;  // NOT
    case 4: *R[op1] ^= mem[op2]; break; // XOR
    case 5: *R[op1] = *R[op2]; break;   // MOV
    case 7: if (R0) IP += op1; break;   // JNZ
    case 8: putc(R0); break;            // PRINT
    case 10: R0 = getc(); break;        // INPUT
}
```

### RVA-Based Opcode Dispatching
- Opcodes are RVAs pointing to handler functions
- Handler performs operation, reads next RVA, jumps
- Map all handlers by following RVA chain

### State Machine VMs (90K+ states)
```java
// BFS for valid path
var agenda = new ArrayDeque<State>();
agenda.add(new State(0, ""));
while (!agenda.isEmpty()) {
    var current = agenda.remove();
    if (current.path.length() == TARGET_LENGTH) {
        println(current.path);
        continue;
    }
    for (var transition : machine.get(current.state).entrySet()) {
        agenda.add(new State(transition.getValue(),
                            current.path + (char)transition.getKey()));
    }
}
```

**Key insight:** Custom VMs appear when the challenge bundles a bytecode blob alongside a dispatcher loop. Reverse the opcode switch table first, then write a disassembler to lift the bytecode before attempting to understand the algorithm.

### Custom VM Reverse Engineering via Fuzzing and Instruction Set Discovery (hxp CTF 2017)

Methodical black-box approach to reversing unknown VM bytecode when static analysis of the dispatch loop is too complex:

**Step 1: Determine instruction alignment.**
Dump the bytecode as bit strings at various widths (6-11 bits) to identify instruction alignment. Look for repeating patterns that suggest opcode boundaries.

**Step 2: Fuzz with random bytes.**
Send single instructions and observe effects on registers/memory to map opcodes. Reduce to minimal programs: find the shortest input that produces each observable effect.

**Step 3: Build the instruction set.**
Example discovered ISA (variable-length 6-11 bit):
```text
000 xxxxxxxx  jmpz    001 xxxxxxxx  jmp     010 xxxxxxxx  call
011 xxxxxxxx  label   1000 xxxxxxx  loadram  1001 xxxxxxx  saveram
110 xxxxxxxx  loadi   11100 xxxxxx  shl      11101 xxxxxx  shr
111100 not    111101 and    111110 or    111111 setif
```

**Step 4: Build assembler/disassembler.**
Write tools to assemble and disassemble the discovered ISA, then disassemble the challenge bytecode to understand its algorithm.

**Step 5: Implement missing primitives.**
If the ISA lacks expected operations, synthesize them from available instructions. Example: implementing XTEA decryption using only AND/OR/NOT (no native XOR or ADD):
```python
# XOR from AND/OR/NOT:  XOR(a, b) = (a OR b) AND NOT(a AND b)
# ADD via full-adder chains using AND/OR/NOT for carry propagation
def xor_from_primitives(a, b):
    return (a | b) & ~(a & b)

def add_from_primitives(a, b, bits=32):
    carry = 0
    result = 0
    for i in range(bits):
        ai = (a >> i) & 1
        bi = (b >> i) & 1
        sum_bit = xor_from_primitives(xor_from_primitives(ai, bi), carry)
        carry = (ai & bi) | (carry & xor_from_primitives(ai, bi))
        result |= (sum_bit << i)
    return result
```

**Key insight:** When static analysis of a VM's dispatch loop is too complex, black-box fuzzing can map the ISA faster. Send single instructions and observe state changes. Variable-length instruction sets require testing multiple bit widths. Once the ISA is known, complex algorithms (XTEA) can be implemented even with minimal primitives (AND/OR/NOT).

**References:** hxp CTF 2017

---

## Anti-Debugging Techniques

### Common Checks
- `IsDebuggerPresent()` (Windows)
- `ptrace(PTRACE_TRACEME)` (Linux)
- `/proc/self/status` TracerPid
- Timing checks (`rdtsc`, `time()`)
- Registry checks (Windows)

### Bypass Technique
1. Identify `test` instructions after debug checks
2. Set breakpoint at the `test`
3. Modify register to bypass conditional

```bash
# In radare2
db 0x401234          # Break at test
dc                   # Run
dr eax=0             # Clear flag
dc                   # Continue
```

### LD_PRELOAD Hook
```c
#define _GNU_SOURCE
#include <dlfcn.h>
#include <sys/ptrace.h>

long int ptrace(enum __ptrace_request req, ...) {
    long int (*orig)(enum __ptrace_request, pid_t, void*, void*);
    orig = dlsym(RTLD_NEXT, "ptrace");
    // Log or modify behavior
    return orig(req, pid, addr, data);
}
```

Compile: `gcc -shared -fPIC -ldl hook.c -o hook.so`
Run: `LD_PRELOAD=./hook.so ./binary`

**Key insight:** Anti-debugging checks are the first obstacle in most reversing challenges. Look for `ptrace`, `IsDebuggerPresent`, or timing checks early in `main()` and patch or hook them before attempting deeper analysis.

### pwntools Binary Patching (Crypto-Cat)
Patch out anti-debug calls directly using pwntools — replaces function with `ret` instruction:
```python
from pwn import *

elf = ELF('./challenge', checksec=False)
elf.asm(elf.symbols.ptrace, 'ret')   # Replace ptrace() with immediate return
elf.save('patched')                   # Save patched binary
```

Other common patches:
```python
elf.asm(addr, 'nop')                  # NOP out an instruction
elf.asm(addr, 'xor eax, eax; ret')    # Return 0 (bypass checks)
elf.asm(addr, 'mov eax, 1; ret')      # Return 1 (force success)
```

---

## Nanomites

### Linux (Signal-Based)
- `SIGTRAP` (`int 3`) → Custom operation
- `SIGILL` (`ud2`) → Custom operation
- `SIGFPE` (`idiv 0`) → Custom operation
- `SIGSEGV` (null deref) → Custom operation

### Windows (Debug Events)
- `EXCEPTION_DEBUG_EVENT` → Main handler
- Parent modifies child via `PTRACE_POKETEXT`
- Magic markers: `0x1337BABE`, `0xDEADC0DE`

### Analysis
1. Check for `fork()` + `ptrace(PTRACE_TRACEME)`
2. Find `WaitForDebugEvent` loop
3. Map EAX values to operations
4. Log operations to reconstruct algorithm

**Key insight:** Nanomites hide the real computation inside signal/exception handlers that only fire under a debugger parent. If the binary forks and the child calls `ptrace(TRACEME)`, the parent is the real CPU -- log its POKE operations to reconstruct the algorithm.

---

## Self-Modifying Code

### Pattern: XOR Decryption
```asm
lea     rax, next_block
mov     dl, [rcx]        ; Input char
xor_loop:
    xor     [rax+rbx], dl
    inc     rbx
    cmp     rbx, BLOCK_SIZE
    jnz     xor_loop
jmp     rax              ; Execute decrypted
```

**Solution:** Known opcode at block start reveals XOR key (flag char).

**Key insight:** Self-modifying code decrypts the next block using each input character as a key. A known-good opcode at the start of each decrypted block (e.g., function prologue) reveals the correct key byte, recovering the flag one character at a time.

---

## Known-Plaintext XOR (Flag Prefix)

**Pattern:** Encrypted bytes given; flag format known (e.g., `0xL4ugh{`).

**Approach:**
1. Assume repeating XOR key.
2. Use known prefix (and any hint phrase) to recover key bytes.
3. Try small key lengths and validate printable output.

```python
enc = bytes.fromhex("...")  # ciphertext
known = b"0xL4ugh{say_yes_to_me"
for klen in range(2, 33):
    key = bytearray(klen)
    ok = True
    for i, b in enumerate(known):
        if i >= len(enc):
            break
        ki = i % klen
        v = enc[i] ^ b
        if key[ki] != 0 and key[ki] != v:
            ok = False
            break
        key[ki] = v
    if not ok:
        continue
    pt = bytes(enc[i] ^ key[i % klen] for i in range(len(enc)))
    if all(32 <= c < 127 for c in pt):
        print(klen, key, pt)
```

**Note:** Challenge hints often appear verbatim in the flag body (e.g., "say_yes_to_me").

### Variant: XOR with Position Index
**Pattern:** `cipher[i] = plain[i] ^ key[i % k] ^ i` (or `^ (i & 0xff)`).

**Symptoms:**
- Repeating-key XOR almost fits known prefix but breaks at later positions
- XOR with known prefix yields a "key" that changes by +1 per index

**Fix:** Remove index first, then recover key with known prefix.
```python
enc = bytes.fromhex("...")
known = b"0xL4ugh{say_yes_to_me"
for klen in range(2, 33):
    key = bytearray(klen)
    ok = True
    for i, b in enumerate(known):
        if i >= len(enc):
            break
        ki = i % klen
        v = (enc[i] ^ i) ^ b  # strip index XOR
        if key[ki] != 0 and key[ki] != v:
            ok = False
            break
        key[ki] = v
    if not ok:
        continue
    pt = bytes((enc[i] ^ i) ^ key[i % klen] for i in range(len(enc)))
    if all(32 <= c < 127 for c in pt):
        print(klen, key, pt)
```

---

## Mixed-Mode (x86-64 / x86) Stagers

**Pattern:** 64-bit ELF jumps into a 32-bit blob via far return (`retf`/`retfq`), often after anti-debug.

**Identification:**
- Bytes `0xCB` (retf) or `0xCA` (retf imm16), sometimes preceded by `0x48` (retfq)
- 32-bit disasm shows SSE ops (`psubb`, `pxor`, `paddb`) in a tight loop
- Computed jumps into the 32-bit region

**Gotchas:**
- `retf` pops **6 bytes**: 4-byte EIP + 2-byte CS (not 8)
- 32-bit blob may rely on inherited **XMM state** and **EFLAGS**
- Missing XMM/flags transfer when switching emulators yields wrong output

**Bypass/Emulation Tips:**
1. Create a UC_MODE_32 emulator, copy memory + GPRs, **EFLAGS**, and **XMM regs**
2. Run 32-bit block, then copy memory + regs back to 64-bit
3. If anti-debug uses `fork/ptrace` + patching, emulate parent to log POKEs and apply them in child

---

## LLVM (Low Level Virtual Machine) Obfuscation (Control Flow Flattening)

### Pattern
```c
while (1) {
    if (i == 0xA57D3848) { /* block */ }
    if (i != 0xA5AA2438) break;
    i = 0x39ABA8E6;  // Next state
}
```

### De-obfuscation
1. GDB script to break at `je` instructions
2. Log state variable values
3. Map state transitions
4. Reconstruct true control flow

**Key insight:** Control flow flattening replaces structured if/else/loops with a single dispatcher switch. The state variable is the key -- trace its values at runtime to reconstruct the original control flow graph without fighting the obfuscation statically.

---

## S-Box / Keystream Generation

### Fisher-Yates Shuffle (Xorshift32)
```python
def gen_sbox():
    sbox = list(range(256))
    state = SEED
    for i in range(255, -1, -1):
        state = ((state << 13) ^ state) & 0xffffffff
        state = ((state >> 17) ^ state) & 0xffffffff
        state = ((state << 5) ^ state) & 0xffffffff
        j = state % (i + 1) if i > 0 else 0
        sbox[i], sbox[j] = sbox[j], sbox[i]
    return sbox
```

### Xorshift64* Keystream
```python
def gen_keystream():
    ks = []
    state = SEED_64
    mul = 0x2545f4914f6cdd1d
    for _ in range(256):
        state ^= (state >> 12)
        state ^= (state << 25)
        state ^= (state >> 27)
        state = (state * mul) & 0xffffffffffffffff
        ks.append((state >> 56) & 0xff)
    return ks
```

### Identifying Patterns
- Xorshift32: shifts 13, 17, 5 (no multiplication constant)
- Xorshift64*: shifts 12, 25, 27, then multiply by `0x2545f4914f6cdd1d`
- Other common constant: `0x9e3779b97f4a7c15` (golden ratio)

**Key insight:** Recognize S-box generation by the Fisher-Yates shuffle pattern (loop counting down from 255, swap with PRNG-chosen index) and keystream generators by the xorshift constants. Once the PRNG family is identified, the algorithm is fully determined by its seed.

---

## SECCOMP/BPF Filter Analysis

```bash
seccomp-tools dump ./binary
```

### BPF Analysis
- `A = sys_number` followed by comparisons
- `mem[N] = A`, `A = mem[N]` for memory ops
- Map to constraint equations, solve with z3

```python
from z3 import *
flag = [BitVec(f'c{i}', 32) for i in range(14)]
s = Solver()
s.add(flag[0] >= 0x20, flag[0] < 0x7f)
# Add constraints from filter
if s.check() == sat:
    m = s.model()
    print(''.join(chr(m[c].as_long()) for c in flag))
```

**Key insight:** SECCOMP (Secure Computing Mode) filters encode flag validation as BPF bytecode operating on syscall arguments. Dump the filter with `seccomp-tools`, translate the comparisons and memory operations into z3 constraints, and solve for the flag without ever running the binary.

---

## Exception Handler Obfuscation

### RtlInstallFunctionTableCallback
- Dynamic exception handler registration
- Handler installs new handler, modifies code
- Use x64dbg with exception handler breaks

### Vectored Exception Handlers (VEH)
- `AddVectoredExceptionHandler` installs handler
- Handler decrypts code at exception address
- Step through, dump decrypted code

**Key insight:** Exception-handler-based obfuscation hides the real control flow inside SEH/VEH handlers that trigger on deliberate faults. Set breakpoints inside the exception handlers rather than on the faulting instructions to follow the actual execution path.

---

## Memory Dump Analysis

### When Binary Dumps Memory
- Check for `/proc/self/maps` reads
- Check for `/proc/self/mem` reads
- Heap data often appended to dump

### Known Plaintext Attack
```python
prologue = bytes([0xf3, 0x0f, 0x1e, 0xfa, 0x55, 0x48, 0x89, 0xe5])
encrypted = data[func_offset:func_offset+8]
partial_key = bytes(a ^ b for a, b in zip(encrypted, prologue))
```

**Key insight:** When a binary reads `/proc/self/mem` or `/proc/self/maps`, it is dumping its own memory -- possibly after encrypting it. Use known function prologues (`endbr64; push rbp; mov rbp, rsp`) as known plaintext to recover the XOR key from the encrypted dump.

---

## Byte-Wise Uniform Transforms

**Pattern:** Output buffer depends on each input byte independently (no cross-byte coupling).

**Detection:**
- Change one input position → only one output position changes
- Fill input with a single byte → output buffer becomes constant

**Solve:**
1. For each byte value 0..255, run the program with that byte repeated
2. Record output byte → build mapping and inverse mapping
3. Apply inverse mapping to static target bytes to recover the flag

---

## x86-64 Gotchas

### Sign Extension
```python
esi = 0xffffffc7  # NOT -57

# For XOR: low byte only
esi_xor = esi & 0xff  # 0xc7

# For addition: full 32-bit with overflow
r12 = (r13 + esi) & 0xffffffff
```

### Loop Boundary State Updates
Assembly often splits state updates across loop boundaries:
```asm
    jmp loop_middle        ; First iteration in middle!

loop_top:                   ; State for iterations 2+
    mov  r13, sbox[a & 0xf]
    ; Uses OLD 'a', not new!

loop_middle:
    ; Main computation
    inc  a
    jne  loop_top
```

**Key insight:** Decompilers often get x86-64 sign extension and loop boundary state updates wrong. Always verify decompiled output against the raw assembly for operations involving `movsx`/`cdqe`, and check whether loop variables update before or after their use in each iteration.

---

## Custom Mangle Function Reversing

**Pattern (Flag Appraisal):** Binary mangles input 2 bytes at a time with intermediate state, compares to static target.

**Approach:**
1. Extract static target bytes from `.rodata` section
2. Understand mangle: processes pairs with running state value
3. Write inverse function (process in reverse, undo each operation)
4. Feed target bytes through inverse → recovers flag

**Key insight:** When a binary mangles input in pairs with running state and compares to a static target, extract the target from `.rodata` and write the inverse function. Process the target bytes in reverse order, undoing each operation, to recover the original input.

---

## Position-Based Transformation Reversing

**Pattern (PascalCTF 2026):** Binary transforms input by adding/subtracting position index.

**Reversing:**
```python
expected = [...]  # Extract from .rodata
flag = ''
for i, b in enumerate(expected):
    if i % 2 == 0:
        flag += chr(b - i)   # Even: input = output - i
    else:
        flag += chr(b + i)   # Odd: input = output + i
```

---

## Hex-Encoded String Comparison

**Pattern (Spider's Curse):** Input converted to hex, compared against hex constant.

**Quick solve:** Extract hex constant from strings/Ghidra, decode:
```bash
echo "4d65746143..." | xxd -r -p
```

---

## Signal-Based Binary Exploration

**Pattern (Signal Signal Little Star):** Binary uses UNIX signals as a binary tree navigation mechanism.

**Identification:**
- Multiple `sigaction()` calls with `SA_SIGINFO`
- `sigaltstack()` setup (alternate signal stack)
- Handler decodes embedded payload, installs next pair of signals
- Two types: Node (installs children) vs Leaf (prints message + exits)

**Solving approach:**
1. Hook `sigaction` via `LD_PRELOAD` to log signal installations
2. DFS through the binary tree by sending signals
3. At each stage, observe which 2 signals are installed
4. Send one, check if program exits (leaf) or installs 2 more (node)
5. If wrong leaf, backtrack and try sibling

```c
// LD_PRELOAD interposer to log sigaction calls
int sigaction(int signum, const struct sigaction *act, ...) {
    if (act && (act->sa_flags & SA_SIGINFO))
        log("SET %d SA_SIGINFO=1\n", signum);
    return real_sigaction(signum, act, oldact);
}
```

---

## Malware Anti-Analysis Bypass via Patching

**Pattern (Carrot):** Malware with multiple environment checks before executing payload.

**Common checks to patch:**
| Check | Technique | Patch |
|-------|-----------|-------|
| `ptrace(PTRACE_TRACEME)` | Anti-debug | Change `cmp -1` to `cmp 0` |
| `sleep(150)` | Anti-sandbox timing | Change sleep value to 1 |
| `/proc/cpuinfo` "hypervisor" | Anti-VM | Flip `JNZ` to `JZ` |
| "VMware"/"VirtualBox" strings | Anti-VM | Flip `JNZ` to `JZ` |
| `getpwuid` username check | Environment | Flip comparison |
| `LD_PRELOAD` check | Anti-hook | Skip check |
| Fan count / hardware check | Anti-VM | Flip `JLE` to `JGE` |
| Hostname check | Environment | Flip `JNZ` to `JZ` |

**Ghidra patching workflow:**
1. Find check function, identify the conditional jump
2. Click on instruction → `Ctrl+Shift+G` → modify opcode
3. For `JNZ` (0x75) → `JZ` (0x74), or vice versa
4. For immediate values: change operand bytes directly
5. Export: press `O` → choose "Original File" format
6. `chmod +x` the patched binary

**Server-side validation bypass:**
- If patched binary sends system info to remote server, patch the data too
- Modify string addresses in data-gathering functions
- Change format strings to embed correct values directly

---

## Multi-Stage Shellcode Loaders

**Pattern (I Heard You Liked Loaders):** Nested shellcode with XOR decode loops and anti-debug.

**Debugging workflow:**
1. Break at `call rax` in launcher, step into shellcode
2. Bypass ptrace anti-debug: step to syscall, `set $rax=0`
3. Step through XOR decode loop (or break on `int3` if hidden)
4. Repeat for each stage until final payload

**Flag extraction from `mov` instructions:**
```python
# Final stage loads flag 4 bytes at a time via mov ebx, value
# Extract little-endian 4-byte chunks
values = [0x6174654d, 0x7b465443, ...]  # From disassembly
flag = b''.join(v.to_bytes(4, 'little') for v in values)
```

---

## Timing Side-Channel Attack

**Pattern (Clock Out):** Validation time varies per correct character (longer sleep on match).

**Exploitation:**
```python
import time
from pwn import *

flag = ""
for pos in range(flag_length):
    best_char, best_time = '', 0
    for c in string.printable:
        io = remote(host, port)
        start = time.time()
        io.sendline((flag + c).ljust(total_len, 'X'))
        io.recvall()
        elapsed = time.time() - start
        if elapsed > best_time:
            best_time = elapsed
            best_char = c
        io.close()
    flag += best_char
```

---

## Multi-Thread Anti-Debug with Decoy + Signal Handler Mixed Boolean-Arithmetic (ApoorvCTF 2026)

**Pattern (A Golden Experience Requiem):** Multi-threaded binary with layered anti-analysis: Thread 1 performs decoy operations (fake AES + deliberate crash via `ud2`), Thread 2 does the real flag computation in a SIGSEGV signal handler using Mixed Boolean Arithmetic (MBA), Thread 3 erases memory to prevent post-mortem analysis.

**Thread layout:**
| Thread | Purpose | Trap |
|--------|---------|------|
| Thread 1 | Decoy: AES-looking operations → `ud2` crash | Analysts waste time reversing fake crypto |
| Thread 2 | Real flag: SIGSEGV handler with MBA transforms | Hidden in signal handler, not main code path |
| Thread 3 | Memory eraser: zeros out flag data after computation | Prevents memory dumping |
| Main | rdtsc-based anti-debug timing check | Penalizes debugger-attached execution |

**Solving approach — pure Python emulation of MBA logic:**
```python
# MBA helpers (extracted from assembly)
def mba_add(a, b): return (a + b) & 0xff
def mba_xor(a, b): return (a ^ b) & 0xff

def mba_transform(i):
    """Position-dependent transform from signal handler."""
    val = (i * 7 + 0x3f) & 0xff
    rotated = ((i << 3) | (i >> 5)) & 0xff
    return mba_xor(val, rotated)

# S-box (SHA-256 initial hash values repurposed)
SBOX = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

def sbox_lookup(i):
    idx = i & 7
    shift = ((i >> 3) & 3) * 8
    return (SBOX[idx] >> shift) & 0xff

# Two interleaved rodata arrays (even indices → array1, odd → array2)
rodata1 = bytes.fromhex("39407691b717c97879013adf3a2adea11c2b04e0")
rodata2 = bytes.fromhex("bb19b025e37eaa786c4116e7aeea00c9c623940d")

flag = []
for i in range(40):  # flag length
    t = mba_transform(i)
    s = sbox_lookup(i)
    mem = rodata1[i // 2] if i % 2 == 0 else rodata2[i // 2]
    flag.append(chr(t ^ s ^ mem))

print(''.join(flag))
```

**Key insight:** The real flag logic is in the signal handler (SIGSEGV/SIGILL), not the main thread. Thread 1's AES-like code and `ud2` crash are intentional misdirection. The `rdtsc` timing check detects debuggers and corrupts output. Bypass by extracting the MBA logic from assembly and reimplementing in Python — never run the binary under a debugger.

**Detection indicators:**
- Multiple `pthread_create` calls with different handler functions
- `signal(SIGSEGV, handler)` or `sigaction` setup
- `ud2` instruction (deliberate illegal instruction)
- `rdtsc` instructions for timing checks
- SHA-256 constants (0x6a09e667...) used as lookup tables, not for hashing

---

## INT3 Patch + Coredump Brute-Force Oracle (Pwn2Win 2016)

Instead of reversing complex transformation logic, patch a byte to `0xCC` (INT3) after the transform, enable core dumps, brute-force each character by running the binary and extracting the transformed result from the coredump via `strings`.

```bash
# Patch byte at transform output point to 0xCC
printf '\xcc' | dd of=binary bs=1 seek=$((0x400ebb)) conv=notrunc
ulimit -c unlimited
# Brute-force each position:
for c in $(seq 32 126); do
    echo -ne "$(printf '\\x%02x' $c)$known_suffix" | ./binary 2>/dev/null
    strings core | grep -q "$expected" && echo "Found: $c"
done
```

**Key insight:** Use INT3/SIGTRAP as a breakpoint oracle -- the coredump captures computed state at the crash point. Avoids full reverse engineering of the transformation.

---

## Signal Handler Chain + LD_PRELOAD Oracle (Nuit du Hack 2016)

Binary uses Unix signals for flow control: `main()` sends SIGINT to itself 1024 times, each handler checks one password character, then calls `signal()` to install the next handler. Bypass: LD_PRELOAD a custom `signal()` that logs when it's called (indicating correct character), brute-force each position.

```c
// LD_PRELOAD library:
#include <signal.h>
sighandler_t signal(int sig, sighandler_t handler) {
    write(2, "CORRECT\n", 8);  // signal() called = char was correct
    return SIG_DFL;
}
```

**Key insight:** Signal-handler-chain anti-reversing can be defeated by hooking `signal()` via LD_PRELOAD. The call to `signal()` (to install the next handler) acts as a side-channel confirming the current character.

---

### printf Format String VM Decompilation to Z3 (SECCON 2017)

A "virtual machine" implemented entirely via `%hhn` format strings. Format string `%hhn` writes the count of printed characters (mod 256) to a pointed-to byte. A sequence of `%Nc%hhn` instructions implements arbitrary byte-to-memory writes, effectively creating a bytecode VM.

**Step 1: Identify instruction types.**
Count unique format patterns to determine the instruction set:
```bash
# Normalize numbers and count unique patterns
sed -e 's/[[:digit:]]\+/1/g' program.fs | sort | uniq -c | sort -nr
```

**Step 2: Write a decompiler.**
Convert format patterns to C-style pseudocode. Each `%N...%hhn` pair maps to a memory write: extract the write address (from the argument pointer) and value (from the character count).

**Step 3: Recognize the algorithm.**
The pseudocode typically reveals a linear equation system over bytes. Map memory addresses to symbolic variables.

**Step 4: Generate Z3 constraints and solve.**
```python
from z3 import *

flag_len = 32  # adjust based on decompiled output
flag = [BitVec(f'f{i}', 8) for i in range(flag_len)]
s = Solver()

# Constrain to printable ASCII
for f in flag:
    s.add(f >= 0x20, f <= 0x7e)

# Add constraints from decompiled format string operations
# e.g., flag[3] + flag[7] == 0xAB (mod 256)
# These come from the write sequences: each %hhn accumulates
# character counts and writes the result to a target byte
s.add((flag[0] + flag[1]) & 0xFF == 0x9A)  # example constraint
s.add((flag[2] ^ flag[3]) & 0xFF == 0x3F)  # example constraint
# ... (add all constraints from decompilation)

if s.check() == sat:
    m = s.model()
    print(bytes([m[f].as_long() for f in flag]))
```

**Decompilation approach in detail:**
1. Extract the write address and value from each `%N...%hhn` pair
2. Map memory addresses to symbolic variables (flag bytes)
3. Build an equation system from the write sequences
4. Solve with Z3

**Key insight:** Format string `%hhn` writes the count of printed characters (mod 256) to a pointed-to byte. A sequence of `%Nc%hhn` instructions implements arbitrary byte-to-memory writes, effectively creating a bytecode VM. Decompile by: (1) extract the write address and value from each `%N...%hhn` pair, (2) map memory addresses to symbolic variables, (3) build an equation system from the write sequences, (4) solve with Z3.

**References:** SECCON 2017


---

## 附录：逆向实战笔记

# Reverse Engineering Field Notes

Detailed quick notes that support [`SKILL.md`](SKILL.md). Read this file after triage, not before.

## Table of Contents

- [Binary Types](#binary-types)
  - [Python .pyc](#python-pyc)
  - [WASM](#wasm)
  - [Android APK](#android-apk)
  - [Flutter APK (Dart AOT)](#flutter-apk-dart-aot)
  - [.NET](#net)
  - [Packed (UPX)](#packed-upx)
  - [Tauri Packed Desktop Apps](#tauri-packed-desktop-apps)
- [Anti-Debugging Bypass](#anti-debugging-bypass)
- [Specialized Patterns](#specialized-patterns)
  - [S-Box / Keystream Patterns](#s-box--keystream-patterns)
  - [Custom VM Analysis](#custom-vm-analysis)
  - [Python Bytecode Reversing](#python-bytecode-reversing)
  - [Signal-Based Binary Exploration](#signal-based-binary-exploration)
  - [Malware Anti-Analysis Bypass via Patching](#malware-anti-analysis-bypass-via-patching)
  - [Expected Values Tables](#expected-values-tables)
  - [x86-64 Gotchas](#x86-64-gotchas)
  - [Iterative Solver Pattern](#iterative-solver-pattern)
  - [Unicorn Emulation (Complex State)](#unicorn-emulation-complex-state)
  - [Multi-Stage Shellcode Loaders](#multi-stage-shellcode-loaders)
  - [Timing Side-Channel Attack](#timing-side-channel-attack)
  - [Unstripped Binary Information Leaks](#unstripped-binary-information-leaks)
  - [Custom Mangle Function Reversing](#custom-mangle-function-reversing)
  - [Rust serde_json Schema Recovery](#rust-serde_json-schema-recovery)
  - [Position-Based Transformation Reversing](#position-based-transformation-reversing)
  - [Hex-Encoded String Comparison](#hex-encoded-string-comparison)
- [CTF Case Notes](#ctf-case-notes)
  - [Embedded ZIP + XOR License Decryption](#embedded-zip--xor-license-decryption)
  - [Stack String Deobfuscation (.rodata XOR Blob)](#stack-string-deobfuscation-rodata-xor-blob)
  - [Prefix Hash Brute-Force](#prefix-hash-brute-force)
  - [Mathematical Convergence Bitmap](#mathematical-convergence-bitmap)
  - [RISC-V Binary Analysis](#risc-v-binary-analysis)
  - [Kernel Module Maze Solving](#kernel-module-maze-solving)
  - [Multi-Threaded VM with Channels](#multi-threaded-vm-with-channels)
  - [CVP/LLL Lattice for Constrained Integer Validation](#cvplll-lattice-for-constrained-integer-validation)
  - [Decision Tree Function Obfuscation](#decision-tree-function-obfuscation)
  - [Android JNI RegisterNatives Obfuscation](#android-jni-registernatives-obfuscation)
  - [Multi-Layer Self-Decrypting Binary](#multi-layer-self-decrypting-binary)
  - [GLSL Shader VM with Self-Modifying Code](#glsl-shader-vm-with-self-modifying-code)
  - [GF(2^8) Gaussian Elimination for Flag Recovery](#gf28-gaussian-elimination-for-flag-recovery)
  - [Z3 for Single-Line Python Boolean Circuit](#z3-for-single-line-python-boolean-circuit)
  - [Sliding Window Popcount Differential Propagation](#sliding-window-popcount-differential-propagation)
  - [Ruby/Perl Polyglot Constraint Satisfaction](#rubyperl-polyglot-constraint-satisfaction)
  - [Verilog/Hardware RE](#veriloghardware-re)
  - [Custom binfmt Kernel Module with RC4 Flat Binaries](#custom-binfmt-kernel-module-with-rc4-flat-binaries)
  - [Hash-Resolved Imports / No-Import Ransomware](#hash-resolved-imports--no-import-ransomware)
  - [ELF Section Header Corruption for Anti-Analysis](#elf-section-header-corruption-for-anti-analysis)
  - [Brainfuck Character-by-Character Static Analysis](#brainfuck-character-by-character-static-analysis)
  - [Brainfuck Side-Channel via Read Count Oracle](#brainfuck-side-channel-via-read-count-oracle)
  - [Brainfuck Comparison Idiom Detection](#brainfuck-comparison-idiom-detection)
  - [Backdoored Shared Library Detection](#backdoored-shared-library-detection)
  - [Go Binary Reversing](#go-binary-reversing)
  - [Go Binary UUID Patching for C2 Enumeration](#go-binary-uuid-patching-for-c2-enumeration)
  - [D Language Binary Reversing](#d-language-binary-reversing)
  - [Rust Binary Reversing](#rust-binary-reversing)
  - [Frida Dynamic Instrumentation](#frida-dynamic-instrumentation)
  - [Frida Firebase Cloud Functions Bypass](#frida-firebase-cloud-functions-bypass)
  - [angr Symbolic Execution](#angr-symbolic-execution)
  - [Qiling Emulation](#qiling-emulation)
  - [VMProtect / Themida Analysis](#vmprotect--themida-analysis)
  - [Binary Diffing](#binary-diffing)
  - [Advanced GDB (pwndbg, rr)](#advanced-gdb-pwndbg-rr)
  - [macOS / iOS Reversing](#macos--ios-reversing)
  - [Embedded / IoT Firmware RE](#embedded--iot-firmware-re)
  - [Kernel Driver Reversing](#kernel-driver-reversing)
  - [Swift / Kotlin Binary Reversing](#swift--kotlin-binary-reversing)
  - [INT3 Patch + Coredump Brute-Force Oracle](#int3-patch--coredump-brute-force-oracle)
  - [Signal Handler Chain + LD_PRELOAD Oracle](#signal-handler-chain--ld_preload-oracle)
  - [Font Ligature Exploitation](#font-ligature-exploitation)
  - [Instruction Counter as Cryptographic State](#instruction-counter-as-cryptographic-state)
  - [Burrows-Wheeler Transform Inversion](#burrows-wheeler-transform-inversion)
  - [FRACTRAN Program Inversion](#fractran-program-inversion)
  - [Opcode-Only Trace Reconstruction](#opcode-only-trace-reconstruction)
  - [Thread Race Signed Integer Overflow](#thread-race-signed-integer-overflow)
  - [ESP32/Xtensa Firmware Reversing](#esp32xtensa-firmware-reversing)
  - [Custom VM Bytecode Lifting to LLVM IR](#custom-vm-bytecode-lifting-to-llvm-ir)
  - [SIGFPE Signal Handler Side-Channel](#sigfpe-signal-handler-side-channel)
  - [Batch Crackme Automation via objdump](#batch-crackme-automation-via-objdump)
  - [Android DEX Runtime Bytecode Patching](#android-dex-runtime-bytecode-patching)
  - [Fork + Pipe + Dead Branch Anti-Analysis](#fork--pipe--dead-branch-anti-analysis)
- [Web/CTF Auth Bypass Case Notes](#webctf-auth-bypass-case-notes)
  - [Signed Cookie Key Reuse: access token to admin_session](#signed-cookie-key-reuse-access-token-to-admin_session)
- [Web Phishing Infrastructure](#web-phishing-infrastructure)
  - [Phishing Panel: {domain_a} / {domain_b}](#phishing-panel-domain_a--domain_b)

## Binary Types

### Python .pyc
Disassemble with `marshal.load()` + `dis.dis()`. Header: 8 bytes (2.x), 12 (3.0-3.6), 16 (3.7+). See [languages.md](languages.md#python-bytecode-reversing-disdis-output).

### WASM
```bash
wasm2c checker.wasm -o checker.c
gcc -O3 checker.c wasm-rt-impl.c -o checker

# WASM patching (challenge binaries):
wasm2wat main.wasm -o main.wat    # Binary → text
# Edit WAT: flip comparisons, change constants
wat2wasm main.wat -o patched.wasm # Text → binary
```

### Android APK
`apktool d app.apk -o decoded/` for resources; `jadx app.apk` for Java decompilation. Check `decoded/res/values/strings.xml` for flags. See [tools.md](tools.md#android-apk).

### Flutter APK (Dart AOT)
If `lib/arm64-v8a/libapp.so` + `libflutter.so` present, use [Blutter](https://github.com/worawit/blutter): `python3 blutter.py path/to/app/lib/arm64-v8a out_dir`. Outputs reconstructed Dart symbols + Frida script. See [tools.md](tools.md#flutter-apk-blutter).

### .NET
- dnSpy - debugging + decompilation
- ILSpy - decompiler

### Packed (UPX)
```bash
upx -d packed -o unpacked
```
If unpacking fails, inspect UPX metadata first: verify UPX section names, header fields, and version markers are intact. If metadata looks tampered or uncertain, review UPX source on GitHub to identify likely modification points.

### Tauri Packed Desktop Apps
Tauri embeds Brotli-compressed frontend assets in the executable. Find `index.html` xrefs to locate asset index table, dump blobs, Brotli decompress. Reference: `tauri-codegen/src/embedded_assets.rs`.

## Anti-Debugging Bypass

Common checks:
- `IsDebuggerPresent()` / PEB.BeingDebugged / NtQueryInformationProcess (Windows)
- `ptrace(PTRACE_TRACEME)` / `/proc/self/status` TracerPid (Linux)
- TLS callbacks (run before main — check PE TLS Directory)
- Timing checks (`rdtsc`, `clock_gettime`, `GetTickCount`)
- Hardware breakpoint detection (DR0-DR3 via GetThreadContext)
- INT3 scanning / code self-hashing (CRC over .text section)
- Signal-based: SIGTRAP handler, SIGALRM timeout, SIGSEGV for real logic
- Frida/DBI detection: `/proc/self/maps` scan, port 27042, inline hook checks

Bypass: Set breakpoint at check, modify register to bypass conditional. pwntools patch: `elf.asm(elf.symbols.ptrace, 'ret')` to replace function with immediate return. See [patterns.md](patterns.md#pwntools-binary-patching-crypto-cat).

For comprehensive anti-analysis techniques and bypasses (30+ methods with code), see [anti-analysis.md](anti-analysis.md).

## Specialized Patterns

### S-Box / Keystream Patterns
**Xorshift32:** Shifts 13, 17, 5  
**Xorshift64:** Shifts 12, 25, 27  
**Magic constants:** `0x2545f4914f6cdd1d`, `0x9e3779b97f4a7c15`

### Custom VM Analysis
1. Identify structure: registers, memory, IP
2. Reverse `executeIns` for opcode meanings
3. Write disassembler mapping opcodes to mnemonics
4. Often easier to bruteforce than fully reverse
5. Look for the bytecode file loaded via command-line arg

See [patterns.md](patterns.md#custom-vm-reversing) for VM workflow, opcode tables, and state machine BFS.

**Sequential key-chain brute-force:** When a VM validates input in small blocks (e.g., 3 bytes = 2^24 candidates) with each block's output key feeding the next, brute-force each block sequentially with OpenMP parallelization. Compile solver with `gcc -O3 -march=native -fopenmp`. See [patterns-ctf-3.md](patterns-ctf-3.md#vm-sequential-key-chain-brute-force-midnight-flag-2026).

### Python Bytecode Reversing
XOR flag checkers with interleaved even/odd tables are common. See [languages.md](languages.md#python-bytecode-reversing-disdis-output) for bytecode analysis tips and reversing patterns.

### Signal-Based Binary Exploration
Binary uses UNIX signals as binary tree navigation; hook `sigaction` via `LD_PRELOAD`, DFS by sending signals. See [patterns.md](patterns.md#signal-based-binary-exploration).

### Malware Anti-Analysis Bypass via Patching
Flip `JNZ`/`JZ` (0x75/0x74), change sleep values, patch environment checks in Ghidra (`Ctrl+Shift+G`). See [patterns.md](patterns.md#malware-anti-analysis-bypass-via-patching).

### Expected Values Tables
Locate with `objdump -s -j .rodata binary | less` — look near comparison instructions, size matches flag length.

### x86-64 Gotchas
Sign extension and 32-bit truncation pitfalls. See [patterns.md](patterns.md#x86-64-gotchas) for details and code examples.

### Iterative Solver Pattern
Try each byte (0-255) per position, match against expected output. **Uniform transform shortcut:** if one input byte only changes one output byte, build 0..255 mapping then invert. See [patterns.md](patterns.md) for full implementation.

### Unicorn Emulation (Complex State)
`from unicorn import *` -- map segments, set up stack, hook to trace. **Mixed-mode pitfall:** 64-bit stub jumping to 32-bit via `retf` requires switching to UC_MODE_32 and copying GPRs + EFLAGS + XMM regs. See [tools.md](tools.md#unicorn-emulation).

### Multi-Stage Shellcode Loaders
Nested shellcode with XOR decode loops; break at `call rax`, bypass ptrace with `set $rax=0`, extract flag from `mov` instructions. See [patterns.md](patterns.md#multi-stage-shellcode-loaders).

### Timing Side-Channel Attack
Validation time varies per correct character; measure elapsed time per candidate to recover flag byte-by-byte. See [patterns.md](patterns.md#timing-side-channel-attack).

### Unstripped Binary Information Leaks
**Pattern:** Debug info and file paths leak author identity. Quick checks: `strings binary | grep "/home/"` (home dirs), `file binary` (stripped?), `readelf -S binary | grep debug` (debug sections).

### Custom Mangle Function Reversing
Binary mangles input 2 bytes at a time with running state; extract target from `.rodata`, write inverse function. See [patterns.md](patterns.md#custom-mangle-function-reversing).

### Rust serde_json Schema Recovery
Disassemble serde `Visitor` implementations to recover expected JSON schema; field names in order reveal flag. See [languages-platforms.md](languages-platforms.md#rust-serdejson-schema-recovery).

### Position-Based Transformation Reversing
Binary adds/subtracts position index; reverse by undoing per-index offset. See [patterns.md](patterns.md#position-based-transformation-reversing).

### Hex-Encoded String Comparison
Input converted to hex, compared against constant. Decode with `xxd -r -p`. See [patterns.md](patterns.md#hex-encoded-string-comparison).

## CTF Case Notes

### Embedded ZIP + XOR License Decryption
Binary with named symbols (`EMBEDDED_ZIP`, `ENCRYPTED_MESSAGE`) in `.rodata` → extract ZIP containing license, XOR encrypted message with license bytes to recover flag. No execution needed. See [patterns-ctf-2.md](patterns-ctf-2.md#embedded-zip-xor-license-decryption-metactf-2026).

### Stack String Deobfuscation (.rodata XOR Blob)
Binary mmaps `.rodata` blob, XOR-deobfuscates, uses it to validate input. Reimplement verification loop with pyelftools to extract blob. Look for `0x9E3779B9`, `0x85EBCA6B` constants and `rol32()`. See [patterns-ctf-2.md](patterns-ctf-2.md#stack-string-deobfuscation-from-rodata-xor-blob-nullcon-2026).

### Prefix Hash Brute-Force
Binary hashes every prefix independently. Recover one character at a time by matching prefix hashes. See [patterns-ctf-2.md](patterns-ctf-2.md#prefix-hash-brute-force-nullcon-2026).

### Mathematical Convergence Bitmap
**Pattern:** Binary classifies coordinate pairs by Newton's method convergence (e.g., z^3-1=0). Grid of pass/fail results renders ASCII art flag. Key: the binary is a classifier, not a checker — reverse the math and visualize. See [patterns-ctf.md](patterns-ctf.md#mathematical-convergence-bitmap-ehax-2026).

### RISC-V Binary Analysis
Statically linked, stripped RISC-V ELF. Use Capstone with `CS_MODE_RISCVC | CS_MODE_RISCV64` for mixed compressed instructions. Emulate with `qemu-riscv64`. Watch for fake flags and XOR decryption with incremental keys. See [tools.md](tools.md#risc-v-binary-analysis-ehax-2026).

### Kernel Module Maze Solving
Rust kernel module implements maze via device ioctls. Enumerate commands dynamically, build DFS solver with decoy avoidance, deploy as minimal static binary (raw syscalls, no libc). See [patterns-ctf.md](patterns-ctf.md#kernel-module-maze-solving-dicectf-2026).

### Multi-Threaded VM with Channels
Custom VM with 16+ threads communicating via futex channels. Trace data flow across thread boundaries, extract constants from GDB, watch for inverted validity logic, solve via BFS state space search. See [patterns-ctf.md](patterns-ctf.md#multi-threaded-vm-with-channel-synchronization-dicectf-2026).

### CVP/LLL Lattice for Constrained Integer Validation
Binary validates flag via matrix multiplication with 64-bit coefficients; solutions must be printable ASCII. Use LLL reduction + CVP in SageMath to find nearest lattice point in the constrained range. Two-phase pattern: Phase 1 recovers AES key, Phase 2 decrypts custom VM bytecode with another linear system (mod 2^32). See [patterns-ctf-2.md](patterns-ctf-2.md#cvplll-lattice-for-constrained-integer-validation-htb-shadowlabyrinth).

### Decision Tree Function Obfuscation
~200+ auto-generated functions routing input through polynomial comparisons. Script extraction via Ghidra headless rather than reversing each function manually. Constraint propagation from known output format cascades through arithmetic constraints. See [patterns-ctf-2.md](patterns-ctf-2.md#decision-tree-function-obfuscation-htb-wondersms).

### Android JNI RegisterNatives Obfuscation
`RegisterNatives` in `JNI_OnLoad` hides which C++ function handles each Java native method (no standard `Java_com_pkg_Class_method` symbol). Find the real handler by tracing `JNI_OnLoad` → `RegisterNatives` → `fnPtr`. Use x86_64 `.so` from APK for best Ghidra decompilation. See [languages-platforms.md](languages-platforms.md#android-jni-registernatives-obfuscation-htb-wondersms).

### Multi-Layer Self-Decrypting Binary
N-layer binary where each layer decrypts the next using user-provided key bytes + SHA-NI. Use oracle (correct key → valid code with expected pattern). JIT execution with fork-per-candidate COW isolation for speed. See [patterns-ctf-2.md](patterns-ctf-2.md#multi-layer-self-decrypting-binary-dicectf-2026).

### GLSL Shader VM with Self-Modifying Code
**Pattern:** WebGL2 fragment shader implements Turing-complete VM on a 256x256 RGBA texture (program memory + VRAM). Self-modifying code (STORE opcode) patches drawing instructions. GPU parallelism causes write conflicts — emulate sequentially in Python to recover full output. See [patterns-ctf-3.md](patterns-ctf-3.md#glsl-shader-vm-with-self-modifying-code-apoorvctf-2026).

### GF(2^8) Gaussian Elimination for Flag Recovery
**Pattern:** Binary performs Gaussian elimination over GF(2^8) with the AES polynomial (0x11b). Matrix + augmentation vector in `.rodata`; solution vector is the flag. Look for constant `0x1b` in disassembly. Addition is XOR, multiplication uses polynomial reduction. See [patterns-ctf-2.md](patterns-ctf-2.md#gf28-gaussian-elimination-for-flag-recovery-apoorvctf-2026).

### Z3 for Single-Line Python Boolean Circuit
**Pattern:** Single-line Python (2000+ semicolons) with walrus operator chains validates flag as big-endian integer via boolean circuit. Obfuscated XOR `(a | b) & ~(a & b)`. Split on semicolons, translate to Z3 symbolically, solve in under a second. See [patterns-ctf-3.md](patterns-ctf-3.md#z3-for-single-line-python-boolean-circuit-bearcatctf-2026).

### Sliding Window Popcount Differential Propagation
**Pattern:** Binary validates input via expected popcount for each position of a 16-bit sliding window. Popcount differences create a recurrence: `bit[i+16] = bit[i] + (data[i+1] - data[i])`. Brute-force ~4000-8000 valid initial 16-bit windows; each determines the entire bit sequence. See [patterns-ctf-3.md](patterns-ctf-3.md#sliding-window-popcount-differential-propagation-bearcatctf-2026).

### Ruby/Perl Polyglot Constraint Satisfaction
**Pattern:** Single file valid in both Ruby and Perl, each imposing different constraints on a key. Exploits `=begin`/`=end` (Ruby block comment) vs `=begin`/`=cut` (Perl POD) to run different code per interpreter. Intersect constraints from both languages to recover the unique key. See [languages-platforms.md](languages-platforms.md#rubyperl-polyglot-constraint-satisfaction-bearcatctf-2026).

### Verilog/Hardware RE
**Pattern:** Verilog HDL source for state machines with hidden conditions gated on shift register history. Analyze `always @(posedge clk)` blocks and `case` statements to find correct input sequences. See [languages-platforms.md](languages-platforms.md#veriloghardware-reverse-engineering-srdnlenctf-2026).

### Custom binfmt Kernel Module with RC4 Flat Binaries
**Pattern:** Kernel module registers binfmt handler for encrypted flat binaries. Reverse the `.ko` to find RC4 key (in `movabs` immediates), decrypt the flat binary, import at the fixed virtual address from the module's `vm_mmap` call. See [patterns-ctf.md](patterns-ctf.md#custom-binfmt-kernel-module-with-rc4-flat-binaries-bsidessf-2026).

### Hash-Resolved Imports / No-Import Ransomware
**Pattern:** Binary with zero visible imports resolves APIs via symbol name hashing at runtime. Skip the hash reversing — hook OpenSSL functions via `LD_PRELOAD` in Docker to capture AES keys directly. See [patterns-ctf.md](patterns-ctf.md#hash-resolved-imports-no-import-ransomware-bsidessf-2026).

### ELF Section Header Corruption for Anti-Analysis
**Pattern:** Corrupted section headers crash analysis tools but program headers are intact so binary runs normally. Patch `e_shoff` to zero or use `readelf -l` (program headers only). Flag hidden after corrupted sections with magic marker + XOR. See [patterns-ctf.md](patterns-ctf.md#elf-section-header-corruption-for-anti-analysis-bsidessf-2026).

### Brainfuck Character-by-Character Static Analysis
**Pattern:** BF programs validating input have `,` (read char) followed by `+` operations whose count = expected ASCII value. Extract increment counts per input position to recover expected input without execution. See [languages.md](languages.md#brainfuck-character-by-character-static-analysis-bsidessf-2026).

### Brainfuck Side-Channel via Read Count Oracle
**Pattern:** BF input validators read more bytes when a character is correct. Count `,` operations per candidate — highest read count = correct byte. Character-by-character recovery. See [languages.md](languages.md#brainfuck-side-channel-via-read-count-oracle-bsidessf-2026).

### Brainfuck Comparison Idiom Detection
**Pattern:** Compiled BF uses fixed idioms for equality checks (`<[-<->] +<[>-<[-]]>[-<+>]`). Instrument interpreter to detect patterns and extract comparison operands (expected flag bytes). See [languages.md](languages.md#brainfuck-comparison-idiom-detection-bsidessf-2026).

### Backdoored Shared Library Detection
Binary works in GDB but fails when run normally (suid)? Check `ldd` for non-standard libc paths, then `strings | diff` the suspicious vs. system library to find injected code/passwords. See [patterns-ctf.md](patterns-ctf.md#backdoored-shared-library-detection-via-string-diffing-hacklu-ctf-2012).

### Go Binary Reversing
Large static binary with `go.buildid`? Use GoReSym to recover function names (works even on stripped binaries). Go strings are `{ptr, len}` pairs — not null-terminated. Look for `main.main`, `runtime.gopanic`, channel ops (`runtime.chansend1`/`chanrecv1`). Use Ghidra golang-loader plugin for best results. See [languages-compiled.md](languages-compiled.md#go-binary-reversing).

### Go Binary UUID Patching for C2 Enumeration
**Pattern:** Go C2 client with UUID from `-ldflags -X`. Binary-patch UUID bytes (same length), register with C2, enumerate clients/files via API. See [languages-compiled.md](languages-compiled.md#go-binary-uuid-patching-for-c2-client-enumeration-bsidessf-2026).

### D Language Binary Reversing
D language binaries have unique symbol mangling (not C++ style). Template-heavy, many function variants. Look for `_D` prefix in symbols. See [languages-compiled.md](languages-compiled.md#d-language-binary-reversing-csaw-ctf-2016).

### Rust Binary Reversing
Binary with `core::panicking` strings and `_ZN` mangled symbols? Use `rustfilt` for demangling. Panic messages contain source paths and line numbers — `strings binary | grep "panicked"` is the fastest approach. Option/Result enums use discriminant byte (0=None/Err, 1=Some/Ok). See [languages-compiled.md](languages-compiled.md#rust-binary-reversing).

### Frida Dynamic Instrumentation
Hook runtime functions without modifying binary. `frida -f ./binary -l hook.js` to spawn with instrumentation. Hook `strcmp`/`memcmp` to capture expected values, bypass anti-debug by replacing `ptrace` return value, scan memory for flag patterns, replace validation functions. See [tools-dynamic.md](tools-dynamic.md#frida-dynamic-instrumentation).

### Frida Firebase Cloud Functions Bypass
**Pattern:** Android app validates via Firebase Cloud Functions. Post-login Frida hook constructs valid payload (UID + value + timestamp) and calls Cloud Function directly, bypassing QR/payment validation. See [languages-platforms.md](languages-platforms.md#frida-firebase-cloud-functions-bypass-bsidessf-2026).

### angr Symbolic Execution
Automatic path exploration to find inputs satisfying constraints. Load binary with `angr.Project`, set find/avoid addresses, call `simgr.explore()`. Constrain input to printable ASCII and known prefix for faster solving. Hook expensive functions (crypto, I/O) to prevent path explosion. See [tools-dynamic.md](tools-dynamic.md#angr-symbolic-execution).

### Qiling Emulation
Cross-platform binary emulation with OS-level support (syscalls, filesystem). Emulate Linux/Windows/ARM/MIPS binaries on any host. No debugger artifacts — bypasses all anti-debug by default. Hook syscalls and addresses with Python API. See [tools-dynamic.md](tools-dynamic.md#qiling-framework-cross-platform-emulation).

### VMProtect / Themida Analysis
VMProtect virtualizes code into custom bytecode. Identify VM entry (pushad-like), find handler table (large indirect jump), trace handlers dynamically. For CTF, focus on tracing operations on input rather than full devirtualization. Themida: dump at OEP with ScyllaHide + Scylla. See [tools-advanced.md](tools-advanced.md#vmprotect-analysis).

### Binary Diffing
BinDiff and Diaphora compare two binaries to highlight changes. Essential when challenge provides patched/original versions. Export from IDA/Ghidra, diff to find vulnerability or hidden functionality. See [tools-advanced.md](tools-advanced.md#binary-diffing).

### Advanced GDB (pwndbg, rr)
pwndbg: `context`, `vmmap`, `search -s "flag{"`, `telescope $rsp`. GEF alternative. Reverse debugging with `rr record`/`rr replay` — step backward through execution. Python scripting for brute-force and automated tracing. See [tools-advanced.md](tools-advanced.md#advanced-gdb-techniques).

### macOS / iOS Reversing
Mach-O binaries: `otool -l` for load commands, `class-dump` for Objective-C headers. Swift: `swift demangle` for symbols. iOS apps: decrypt FairPlay DRM with frida-ios-dump, bypass jailbreak detection with Frida hooks. Re-sign patched binaries with `codesign -f -s -`. See [platforms.md](platforms.md#macos-ios-reversing).

### Embedded / IoT Firmware RE
`binwalk -Me firmware.bin` for recursive extraction. Hardware: UART/JTAG/SPI flash for firmware dumps. Filesystems: SquashFS (`unsquashfs`), JFFS2, UBI. Emulate with QEMU: `qemu-arm -L /usr/arm-linux-gnueabihf/ ./binary`. See [platforms.md](platforms.md#embedded-iot-firmware-re).

### Kernel Driver Reversing
Linux `.ko`: find ioctl handler via `file_operations` struct, trace `copy_from_user`/`copy_to_user`. Debug with QEMU+GDB (`-s -S`). eBPF: `bpftool prog dump xlated`. Windows `.sys`: find `DriverEntry` → `IoCreateDevice` → IRP handlers. See [platforms.md](platforms.md#kernel-driver-reversing).

### Swift / Kotlin Binary Reversing
Swift: `swift demangle` symbols, protocol witness tables for dispatch, `__swift5_*` sections. Kotlin/JVM: coroutines compile to state machines in `invokeSuspend`, `jadx` with Kotlin mode for best decompilation. Kotlin/Native: LLVM backend, looks like C++ in disassembly. See [languages-compiled.md](languages-compiled.md#swift-binary-reversing).

### INT3 Patch + Coredump Brute-Force Oracle
Patch `0xCC` (INT3) after transform output, enable core dumps, brute-force each input character by extracting computed state from coredump via `strings`. Avoids full reverse of transformation. See [patterns.md](patterns.md#int3-patch-coredump-brute-force-oracle-pwn2win-2016).

### Signal Handler Chain + LD_PRELOAD Oracle
Binary uses signal handler chains for per-character password validation. Hook `signal()` via LD_PRELOAD -- the call to install the next handler confirms the current character is correct. See [patterns.md](patterns.md#signal-handler-chain-ldpreload-oracle-nuit-du-hack-2016).

### Font Ligature Exploitation
Custom OpenType font maps multi-character ligature sequences to single glyphs; reverse the GSUB table to decode hidden messages. See [patterns-ctf-3.md](patterns-ctf-3.md#opentype-font-ligature-exploitation-for-hidden-messages-hack-the-vote-2016).

### Instruction Counter as Cryptographic State
**Pattern:** Hand-written assembly uses a dedicated register (e.g., `r12`) as an instruction counter incremented after nearly every instruction. The counter feeds into XOR/ROL/multiply transformations on input bytes, making transformation path-dependent. Byte-by-byte brute force with Unicorn emulation recovers the flag. See [patterns-ctf-3.md](patterns-ctf-3.md#instruction-counter-as-cryptographic-state-metactf-flash-2026).

### Burrows-Wheeler Transform Inversion
Invert BWT without terminator character by trying all possible row indices. Standard `bwtool` or manual column-sorting reconstruction. See [patterns-ctf-3.md](patterns-ctf-3.md#burrows-wheeler-transform-inversion-without-terminator-asis-ctf-finals-2016).

### FRACTRAN Program Inversion
Esoteric language using iterated fraction multiplication. Invert by swapping numerator/denominator in fraction table, run output backward. I/O encoded as prime factorization exponents. See [languages.md](languages.md#fractran-program-inversion-boston-key-party-2016).

### Opcode-Only Trace Reconstruction
Execution traces with only opcodes (no data) still leak info through branch decisions. Sorting algorithm comparisons reveal element ordering. Reconstruct by deduplicating trace, splitting into basic blocks. See [tools-dynamic.md](tools-dynamic.md#opcode-only-trace-reconstruction-0ctf-2016).

### Thread Race Signed Integer Overflow
Combat-simulation binary with thread-unsafe skill lock. Race between skill selection and damage calculation; `cdqe` sign-extends 0xFFFFFFFF to -1 (signed), causing HP overflow on subtraction. See [patterns-ctf-3.md](patterns-ctf-3.md#thread-race-condition-with-signed-integer-overflow-codegate-2017).

### ESP32/Xtensa Firmware Reversing
No IDA support — use radare2 + ESP-IDF ROM linker script (`esp32.rom.ld`) for symbol resolution. Cross-reference with public ESP-IDF HTTP server examples to identify app logic. See [patterns-ctf-3.md](patterns-ctf-3.md#esp32xtensa-firmware-reversing-with-rom-symbol-map-insomnihack-2017).

### Custom VM Bytecode Lifting to LLVM IR
Transpile custom VM bytecode to LLVM IR, then use `opt -O3` to simplify (inlining, constant folding, dead code elimination). Reduces 1300 lines to ~150 lines, revealing the underlying algorithm. See [tools-advanced.md](tools-advanced.md#custom-vm-bytecode-lifting-to-llvm-ir-google-ctf-2017).

### SIGFPE Signal Handler Side-Channel
SIGFPE signal handlers create implicit control flow invisible to static analysis. Count SIGFPE signals via `strace -e signal=SIGFPE` per candidate character -- correct characters produce more signals. See [anti-analysis.md](anti-analysis.md#sigfpe-signal-handler-side-channel-via-strace-counting-plaidctf-2017).

### Batch Crackme Automation via objdump
Mass crackme challenges (100s of binaries) with identical structure: script `objdump` to extract CMP immediates and add/sub arithmetic sequences, then reverse-compute keys algebraically without execution. See [patterns-ctf-3.md](patterns-ctf-3.md#batch-crackme-automation-via-objdump-pattern-extraction-def-con-2017).

### Android DEX Runtime Bytecode Patching
Native JNI library patches Dalvik bytecode in memory via `/proc/self/maps` + `mprotect` + XOR. Static APK analysis alone is insufficient -- extract XOR key and offsets from the native `.so` to reconstruct the runtime DEX. See [languages-platforms.md](languages-platforms.md#android-dex-runtime-bytecode-patching-via-procselfmaps-google-ctf-2017).

### Fork + Pipe + Dead Branch Anti-Analysis
Fork/pipe IPC where parent writes data and exits, child reads and continues. Real validation hidden in a dead branch (always-false comparison). `strace` reveals the fork/pipe pattern; patch the comparison constant to reach hidden code. See [patterns-ctf-3.md](patterns-ctf-3.md#fork-pipe-dead-branch-anti-analysis-rctf-2017).

## Web/CTF Auth Bypass Case Notes

### Signed Cookie Key Reuse: access token to admin_session

**Case:** `class.pangbaoba.me` CTF homework system. Public `/access/<token>` route set a signed `student_gate`; the same access token also worked as the HMAC key for `admin_session`, allowing direct admin API access by forging the exact session payload shape.

**Core pattern:** A visible invite/access token is reused as a server-side signing secret. If one signed cookie can be validated offline, test whether sibling auth cookies use the same signing scheme and key.

**Triage workflow:**
1. Capture `Set-Cookie` from the gated entry route, especially cookies shaped like `<base64url-json>.<base64url-signature>`.
2. Decode the first segment; identify compact JSON payloads such as `{"access":"student"}`.
3. Recompute `HMAC-SHA256(payload_b64, candidate_key)` using visible route tokens, invite codes, reset tokens, or frontend constants as candidate keys.
4. If the signature matches, enumerate *payload shape*, not passwords: try likely authorization claims on the correct cookie name (`admin_session`, `session`, `auth`, etc.).
5. Verify with read-only endpoints first (`/api/admin/me`, settings/status/list routes) before any write action.

**Important lesson:** The first obvious payload may fail. In this case `{"access":"admin"}`, `{"role":"admin"}`, and `{"access":"student","isAdmin":true}` failed, while the backend actually checked:

```json
{"admin":true}
```

**Minimal PoC shape:**

```python
import base64, hashlib, hmac, json

def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

access_token = "<token from /access/<token>>"
payload_b64 = b64u(json.dumps({"admin": True}, separators=(",", ":")).encode())
sig_b64 = b64u(hmac.new(access_token.encode(), payload_b64.encode(), hashlib.sha256).digest())
print(f"admin_session={payload_b64}.{sig_b64}")
```

**Validation signals:**
- `GET /api/admin/me` changes from `401 {"error":"unauthorized"}` to `200 {"admin":true}`.
- Other read-only admin endpoints return real data with the forged cookie.
- A JSON-cookie value like `admin_session=j:{}` causing `500` suggests Express/cookie-parser type confusion and confirms fragile cookie parsing; it is not required for the bypass but helps identify the stack and parsing assumptions.

**What to avoid:** Do not brute-force admin passwords or enumerate unrelated user IDs when a signed-cookie structure is visible. Work offline on signatures and use low-frequency read-only verification.

**Fix guidance:** Never use public route/access tokens as HMAC secrets. Use server-only cookie signing secrets, separate student/admin secrets, server-side sessions for admin identity, strict cookie type checks, and return `401` on parse/verify failure instead of `500`.

## Web Phishing Infrastructure

### Phishing Panel: {target_domain_a} / {target_domain_b}
**完整分析**: [phishing-case-study.md](phishing-case-study.md)

Two-server phishing infrastructure impersonating a government agency. Full victim control system with server-driven status code redirection.

**Architecture:**
- `{target_domain_a}` — Presentation layer (phishing pages, JS polling client)
- `{target_domain_b}` — Data layer (PHP+MySQL backend, admin panel)
- Both behind NAT ({internal_ip} internal), nginx, SSL-only
- Web root: `/www/wwwroot/{target_domain_b}/`

**Victim Flow:** Landing page (fake subsidy quotas) → 1.html (ID/bank card form → `submit.php`) → 4.html (PIN → `get-ayment.php`) → server-controlled staged pages (9-16) via 1-second `status_check.php` polling.

**Key Findings:**
- Admin panel at `register.php` → `qichuang.php` (login form), `list.php` (dashboard template)
- Auth via PHP session (`PHPSESSID`); `login.php` and `check_login_ajax.php` removed (404)
- **Data leak**: `db.php` returns victim name list without auth (49+ records, **no bank details** — only id/username/note/description fields)
- **No-auth write**: `save_note.php` accepts data without authentication
- `backend.php` gives SQL error suggesting admin registration endpoint (broken)
- Rate limiting on `submit.php` (multi-factor), no SQLi or session bypass found
- Status code system: admin sets 1-16, victim browser auto-redirects to `N.html`

**Infrastructure:**
| Domain | Public IP | Role |
|--------|-----------|------|
| {target_domain_1} | {target_ip_1} | Backend + Admin |
| {target_domain_2} | {target_ip_2} | Frontend (phishing pages) |


---

## 分析前预判：文件伪装与名字欺骗

### 文件后缀不可信

**核心原则：永远用 `file` 命令或 magic bytes 判断文件类型，不要相信后缀名。**

常见伪装手法：

| 伪装后缀 | 实际类型 | 目的 |
|---------|---------|------|
| `.sh` | ELF 二进制 | 让人以为是脚本，降低警惕 |
| `.txt` | PE/ELF | 绕过简单的文件类型过滤 |
| `.jpg`/`.png` | 可执行文件或压缩包 | 隐藏在图片中 |
| `.dll` | 实际是 .NET assembly | 混淆分析方向 |
| `.so` | 实际是加密 payload | 需要先解密 |
| 无后缀 | 任何类型 | Linux 下常见 |

```bash
# 正确做法：用 file 命令
file suspicious_file.sh
# 输出: ELF 64-bit LSB executable, ARM aarch64...

# 用 xxd 看 magic bytes
xxd suspicious_file.sh | head -1
# 7f454c46 = ELF magic
```

### 文件名不可信

**"DriverLoader" 不一定加载驱动，"Updater" 不一定更新。**

常见名字欺骗：

| 文件名暗示 | 实际行为 |
|-----------|---------|
| `DriverLoader` | 可能是 ptrace 注入器 / 进程 hook |
| `SystemService` | 可能是后门 / C2 agent |
| `Updater` / `Update` | 可能是 dropper / 下载器 |
| `Helper` / `Assistant` | 可能是提权工具 |
| `lib*.so` | 可能是注入 payload |

**分析时应该：**
- 忽略文件名暗示，按实际代码行为判断
- 关注 `mmap`、`ptrace`、`/proc/self/mem` 等系统调用
- 如果看到"加载驱动"但没有 `insmod`/`init_module` 调用，说明名不副实

### 静态分析不够时的动态补充

纯静态分析只能看到代码骨架。以下场景必须配合动态分析：

| 场景 | 推荐动态方法 |
|------|-------------|
| 代码有解密/解压逻辑 | 在解密后下断点，dump 明文 |
| 大量间接调用（函数指针表） | strace/ltrace 跟踪实际调用 |
| 疑似反调试 | 先 strace 看 ptrace 调用 |
| 内嵌 shellcode/payload | QEMU 用户态模拟执行 |
| 网络通信协议未知 | tcpdump/Wireshark 抓包 |

```bash
# strace 跟踪系统调用（重点关注）
strace -f -e trace=open,mmap,ptrace,execve,connect ./binary

# ltrace 跟踪库函数调用
ltrace -f ./binary

# QEMU 用户态模拟（不需要真实设备）
qemu-aarch64 -strace ./binary_arm64

# 检查反调试：看是否 ptrace 自追踪
strace ./binary 2>&1 | grep ptrace
# 如果看到 ptrace(PTRACE_TRACEME, ...) 说明有反调试
```

### 进程注入/保护壳类样本的常见模式

这类样本（如 `LinYuDriverLoader`）通常：

1. **不是真正加载内核驱动**（需要 root 权限，大多数场景没有）
2. **实际行为是进程注入**：
   - `ptrace` attach 到目标进程
   - 通过 `/proc/<pid>/mem` 读写目标内存
   - `mmap` 映射 shellcode 到目标进程空间
3. **内嵌加密 payload**：
   - 运行时解密一段 shellcode
   - 解密后的 payload 才是真正的 hook 代码
4. **反调试保护**：
   - `ptrace(PTRACE_TRACEME)` 自追踪
   - 时间检测（`clock_gettime` 前后对比）
   - `/proc/self/status` 检查 TracerPid

**分析策略**：
```text
1. file 命令确认真实类型
2. strings 看有没有明显的路径/库名/错误信息
3. rabin2 -I 看架构/编译器/保护
4. 静态找 mmap/ptrace/open 调用
5. 如果有解密逻辑 → 动态跑到解密后 dump
6. 如果有反调试 → 先 patch 掉或用 LD_PRELOAD 绕过
```

<!-- skill-trace:b394fba58bf36447ee892b6eaacbba31 -->
