---
name: l-license
description: "MUST on 破解/绕过激活/去验证/授权/卡密/注册机/keygen with local exe/apk/file. Local router to detailed modules."
---

# l-license Local Entry

Scope: cracking / bypassing activation / removing verification / license keys / keygen (local exe/apk/file). Detailed modules are installed beside this entry.

## Selection Rules (avoid mis-picking)
1. First read the "Module List" below.
2. Scan the "Module List" below **top to bottom**; use the first one that matches the current task.
   When multiple capabilities are needed, stack at most 3, with entries higher up taking priority.
3. Read the selected local module from `../<MODULE_ID>/SKILL.md`, then apply its task guidance.
4. When none matches exactly, fall through to the "Fallback" at the bottom of this page.

## Local Module Reading

Read the selected module from the adjacent directory `<MODULE_ID>/SKILL.md`. Use the existing local file directly.

## Module List (ordered by priority)

- `reverse-engineering` — Reverse-engineering master guide: format identification, protection analysis, evidence-driven progress.
- `reverse_flow_skill` — Reversing workflow skill: the full sample-to-report reversing workflow.
- `dotnet-reverse` — .NET reversing: dnSpy/ILSpy decompilation and debugging.
- `apk-reverse` — Android APK reversing: jadx/apktool decompilation, smali edits, Frida dynamic hooking.
- `binary-diff` — Binary diffing: compare two versions to find patched changes.
- `patch-diff-exploit` — Patch diffing and exploitation: infer exploitable points from a patch.
- `protocol-reverse` — Protocol reversing: recover the format of a proprietary communication protocol.
- `js-reverse` — JS reversing: deobfuscation, locating encryption algorithms.
- `mobile-reverse` — Mobile reversing: shared iOS/Android reversing workflow.
- `thick-client` — Thick-client security: desktop app local storage, communication, and trust-boundary testing.
- `browser-extension-reverse` — Browser-extension reversing: analyze an extension's manifest, background scripts, and logic.
- `code-audit` — Code audit: source-level security vulnerability review.

## Fallback
When none of the above matches exactly: for reversing tasks read `reverse_flow_skill`, for pentest tasks read `pentest-tools`, then continue per its body; if still unsure read `skills` for a second routing pass.

<!-- skill-trace:7cdc12ec11ab510f66eaf66c3348584a -->
