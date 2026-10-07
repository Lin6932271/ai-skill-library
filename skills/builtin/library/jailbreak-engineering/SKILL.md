---
name: jailbreak-engineering
description: "jailbreak-engineering"
---

# Jailbreak Engineering / Jailbreak Engineering

> This domain is fully covered by `llm-security/`. This file is a routing alias; the Agent should load `llm-security/SKILL.md` directly to obtain the full SOP.
> Path: `_bundled_skills/llm-security/SKILL.md`

## Trigger routing
Keywords: 越狱、jailbreak、bypass、绕过、沙箱逃逸、权限提升、root、分析、注入、inject、提示词、prompt

## Routing map
`jailbreak-engineering` → `llm-security` (actual skill domain)

## Quick SOP (minimal)

### Phase 1: target analysis
1. Identify the target Agent's constraint system (system prompt / rules / content policy)
2. Confirm injection surfaces: user input, external documents, tool-call return values, memory writes
3. Grade it: simple rule check vs. multi-layer nested constraints

### Phase 2: injection strategy (executed by llm-security)
- **Direct injection**: use instruction priority to override rules
- **Context overflow**: flood the constraint section with overly long tokens
- **Role-play**: construct a "legitimate scenario" that defeats the constraints
- **Tool abuse**: use execute_command/write_file to bypass filters
- **Memory poisoning**: persist an injection into the Agent's memory

### Phase 3: validation
1. Assert: after injection, did the target perform an action the original constraints forbid?
2. Persistence: does the injection still take effect after a conversation refresh?
3. Penetration radius: can the AI-constraint break be bridged to system privileges?

### Phase 4: reporting
- Attack path (conditions required at each step + success/failure)
- Constraint weak points (exactly which rule was broken)
- Remediation advice (hotfix + architecture-level improvements)

## Forbidden actions
- ❌ Do not run jailbreak testing directly against production systems (unless a scope-contract authorization already exists)
- ❌ Do not perform unauthorized privilege-escalation operations
- ❌ Do not use jailbreak techniques for purposes that violate the target application's ToS
- ❌ After a successful jailbreak, do not escalate beyond the AI sandbox to system boundaries (unless the scope explicitly defines it)
- ❌ Do not publicly disclose discovered constraint vulnerabilities (report to the vendor first / follow the bug-bounty process)

Full SOP + detailed strategy → `llm-security/SKILL.md`

<!-- skill-trace:f3cde4186daf79dafdc31618715c02fa -->
