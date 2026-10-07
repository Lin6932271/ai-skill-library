---
name: email-security
description: "Use for email security review including phishing analysis, header authentication (SPF/DKIM/DMARC), BEC patterns, and mailbox token abuse research."
---

# Email Security & Phishing Analysis

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: confirm authorization (analyzing sample emails / tenant configuration review)
2. `NOW`: do not re-deliver malicious samples to real users
3. `ACT`: header authentication → content/URL → attachment sandbox → tenant control-plane recommendations

## Applicable scenarios

- Phishing-email dissection and IOCs
- SPF/DKIM/DMARC configuration assessment
- BEC (business email compromise) fraud patterns
- OAuth application phishing / mailbox token abuse (joint with llm/cloud identity)
- Security-awareness exercise design (authorized)

## Workflow

```text
□ Full raw headers: Received chain, From/Return-Path consistency
□ SPF/DKIM/DMARC alignment results
□ URL sandbox and attachment static analysis (joint with malware-analysis)
□ Spoofed brand and reply-address discrepancies
□ Tenant: anti-phishing policy, external tagging, MFA, OAuth app consent
```

## Toolchain

| Tool | Purpose |
|------|------|
| Email client "view source" | Headers |
| dig/nslookup | SPF/DMARC records |
| urlscan / sandbox | Links and attachments |
| Tenant admin center | Policy |

## References

- `references/email-auth-checklist.md`
- `../malware-analysis/` `../attack-chain/` (phishing phase) `../windows-ad/` (tokens)

## Routing context

**Upstream**: MASTER R36  
**MUST NOT**: unauthorized bulk test-phishing against third-party domains

## Task-completion self-check

- [ ] Are the header-authentication conclusions complete?
- [ ] Are IOCs made detectable (joint with threat-hunting)?
- [ ] Checklist?

<!-- skill-trace:37ca30ba8540807473e6ae471ab5b778 -->
