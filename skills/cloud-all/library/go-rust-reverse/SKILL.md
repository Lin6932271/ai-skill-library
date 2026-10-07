---
name: go-rust-reverse
description: "Use for reverse engineering stripped Go and Rust binaries including runtime recognition, pclntab/moduel data recovery, panic strings, and idiomatic decompilation recovery."
---

# Go / Rust Binary Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md`
2. `NOW`: confirm the sample is a Go/Rust build (`file`/strings/runtime traits)
3. `NEXT`: whether GoReSym / relevant plugins are available
4. `ACT`: runtime recognition → symbol/metadata recovery → business logic

## Applicable scenarios

- Symbol-stripped Go malware/tools
- Rust release binaries, panic-string-driven analysis
- Language-specific methods that complement generic ida/ghidra

## Workflow

### Go

```text
□ Identify go.buildid, runtime symbol residue, pclntab
□ GoReSym / redress / IDA Go plugin to recover function names
□ Watch the shape of interface, slice, string structures in decompilation
□ Network/crypto library paths: crypto/* net/http
```

### Rust

```text
□ panic strings, rust_begin_unwind, crate-path hints
□ Code bloat from generic instantiation; locate string xrefs first
□ Async/tokio state machines need cross-reference analysis
```

### Dynamic

```text
□ Frida still usable; mind the Go stack and scheduler
□ Prefer log- and config-string-driven breakpoints
```

## Toolchain

| Tool | Purpose |
|------|------|
| GoReSym | Go metadata |
| IDA/Ghidra + Go/Rust plugins | Decompilation |
| radare2 | Quick strings |
| strings / rabin2 | Triage |

## References

- `references/go-rust-notes.md`
- `../reverse-engineering/go-reverse.md` `../ida-reverse/` `../ghidra-reverse/`
- seed: `field-journal/seed-002_go-malware-stripped.md`

## Routing context

**Upstream**: MASTER R33  
**Downstream**: malware-sample flow `malware-analysis`; generic RE `reverse-engineering`

## Task-completion self-check

- [ ] Did I recover key function names or an equivalent mapping?
- [ ] Did I annotate language-runtime evidence?
- [ ] Checklist?

<!-- skill-trace:aace74146e15131cf956e4ac58b1ffbf -->
