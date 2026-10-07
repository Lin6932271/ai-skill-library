---
name: code-audit
description: "Use for source-code security review and SAST workflows including Semgrep, CodeQL patterns, dangerous API hunting, and fix verification."
---

# Source Code Security Audit

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` or the code-audit authorization
2. `NOW`: confirm you have **source/repository access** (no source, binary only → switch to an RE skill)
3. `NOW`: state the language stack and scope (directory/service/PR diff)
4. `NEXT`: tool-index; semgrep, etc.
5. `ACT`: threat-model sketch → automated scan → manual verification

## Applicable scenarios

- White-box audit, PR/diff security review
- Semgrep / CodeQL / Bandit / gosec and other SAST
- Dangerous APIs, injection points, missing authorization, crypto misuse
- Division of labor with `supply-chain-security/`: this skill leans toward **your own code logic**, supply-chain leans toward dependencies and pipelines

## Workflow

### 1. Scope and threat model

```text
□ Trust boundaries: user input, files, deserialization, SSRF, auth middleware
□ High-value assets: auth, payments, admin panel, key handling
```

### 2. Automated scan

```bash
semgrep --config auto .
# or a project rule pack
semgrep --config p/owasp-top-ten .
```

### 3. Manual verification (MUST)

```text
□ Each SAST hit: reachable? exploitable? false positive?
□ Authz: IDOR/privilege escalation, missing checks, wrong multi-tenant isolation
□ Injection: SQL/command/template/LDAP
□ Crypto: hard-coded keys, ECB, custom crypto
```

### 4. Output

```text
Finding: location + data flow + PoC + fix recommendation
Optional ATT&CK / CWE number
```

## Toolchain

| Tool | Language/scenario |
|------|-----------|
| Semgrep | Multi-language quick rules |
| CodeQL | Deep data flow (GitHub) |
| Bandit | Python |
| gosec / staticcheck | Go |
| SpotBugs / FindSecBugs | Java |

## References

- `references/sast-review-checklist.md`
- `../supply-chain-security/` `../api-security/` `../llm-security/` (Agent code)

## Routing context

**Upstream**: MASTER R26  
**Role**: `ops/role-map.md` cae  
**Downstream**: dependency vulns → supply-chain; runtime validation → pentest-tools

## Task-completion self-check

- [ ] Did I manually verify rather than just paste scanner output?
- [ ] Does it include fix recommendations?
- [ ] Is it scoped to the authorized repository?
- [ ] Checklist?

<!-- skill-trace:a9b9916f328fc62f78be5beb4dce7eb9 -->
