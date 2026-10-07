---
name: identity-federation
description: "Use for assessment of federated identity systems including SAML, OIDC, OAuth2 flows, SSO misconfiguration, and token confusion issues."
---

# Identity Federation (SAML / OIDC / OAuth)

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read precedent-pentest; SSO test accounts and the IdP/SP scope go into scope
2. `NOW`: brute-force attempts that lock out real user accounts are forbidden
3. `NEXT`: capture tools and documentation (metadata URL)
4. `ACT`: protocol-flow mapping → common misconfigurations → validation

## Applicable scenarios

- SAML Response signature/assertion tampering surface (classic flaw patterns)
- OIDC implicit / authorization-code + missing PKCE
- redirect_uri / state / nonce issues
- IdP and SP metadata, multi-tenant issuer confusion
- Complements `api-security` JWT attacks (this skill leans toward federation and SSO flows)

## Workflow

```text
□ Draw it out: User → SP → IdP → Token → SP
□ Collect: /.well-known/openid-configuration, SAML metadata
□ Check: redirect_uri exact match, state binding, PKCE
□ Check: SAML signature coverage, algorithm downgrade
□ Session fixation and logout invalidation
```

## Toolchain

| Tool | Purpose |
|------|------|
| Burp + SAML Raider, etc. | Assertion editing (authorized) |
| jwt_tool | JWT segments |
| Browser DevTools | Redirect chain |
| IdP admin logs | Audit |

## References

- `references/sso-flow-checklist.md`
- `../api-security/` `../windows-ad/` (enterprise IdP)

## Routing context

**Upstream**: MASTER R37  
**Downstream**: pure API JWT → api-security; cloud IdP → cloud-k8s

## Task-completion self-check

- [ ] Did I map the full SSO flow?
- [ ] Does each finding have a reproduction and impact?
- [ ] Checklist?

<!-- skill-trace:8e40f077fa8daaebfc3b388971fa3809 -->
