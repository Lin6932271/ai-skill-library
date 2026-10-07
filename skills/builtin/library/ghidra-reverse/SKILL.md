---
name: ghidra-reverse
description: "Use for free/open reverse engineering with Ghidra (headless or GUI), including decompile, cross-refs, and optional Ghidra MCP workflows when IDA is unavailable."
---

# Ghidra Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md`
2. `NOW`: confirm you need **Ghidra** (no IDA / prefer open-source / bulk headless)
3. `NEXT`: read `../tool-index.md` for the ghidra / ghidra-mcp path
4. `NEXT`: missing tools → bootstrap `ghidra-mcp` (if the manifest supports it) or install Ghidra via manual steps
5. `ACT`: import the sample → auto-analyze → export the decompilation of key functions

## Applicable scenarios

- Primary reversing entry when there is no IDA license
- Bulk headless analysis / decompilation in CI
- Ghidra scripting (Java/Python Jython/PyGhidra) automation
- Integration with `binary-diff` / `patch-diff-exploit` via ghidriff

## Division of labor with IDA

| Requirement | Prefer |
|------|------|
| Deep-dive with existing IDA MCP | `ida-reverse/` |
| Open-source / bulk / teaching | **this skill** |
| CLI-only quick recon | `radare2/` |

## Workflow

### 1. Project and auto-analysis

```text
□ New Project → Import file → Analyze (default analyzers)
□ Record language/compiler recognition results and base address
□ Mark entry points, export table, string xrefs
```

### 2. Key functions

```text
□ Reverse-lookup from strings / imported APIs
□ Decompile window to recover the algorithm
□ Rename functions/variables; write Plate comments
□ Hand off to Frida/GDB when dynamic is needed (reverse-engineering dynamic chapter)
```

### 3. Headless (bulk)

```bash
# Example: the analyzeHeadless path varies by install, MUST take it from tool-index
analyzeHeadless /path/to/project Proj -import sample.bin -postScript ExportDecomp.py
```

### 4. MCP (if configured)

```text
□ Confirm the ghidra MCP port (commonly 8765, defer to tool-index)
□ Use MCP tools to pull decompilation / xrefs, do not guess the port
```

## Toolchain

| Tool | Purpose | Bootstrap |
|------|------|------|
| Ghidra | Main decompilation tool | manual release / package manager |
| ghidra-mcp | AI bridge | bootstrap capability name `ghidra-mcp` |
| ghidriff | Patch diffing | see `patch-diff-exploit` |

## References

- `references/ghidra-cheatsheet.md`
- `../ida-reverse/` `../radare2/` `../binary-diff/`

## Routing context

**Upstream**: MASTER R22  
**Downstream**: dynamic validation → Frida/GDB; exploitation → `pwn-chain`  
**Peer**: `ida-reverse` (commercial deep-dive)

## Task-completion self-check

- [ ] Is it based on the real Ghidra/tool-index path?
- [ ] Did I annotate function addresses and renames?
- [ ] Are there reproducible steps?
- [ ] Checklist / journal?

<!-- skill-trace:0f6758ddc3723e9ad1a71015bab01680 -->
