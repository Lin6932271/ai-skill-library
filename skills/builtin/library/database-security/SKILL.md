---
name: database-security
description: "Use for database security assessment covering PostgreSQL/MySQL/MSSQL/Mongo/Redis exposure, authz, UDF/command paths, and misconfiguration review."
---

# Database Security Assessment

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read precedent-pentest; **destructive statements are forbidden on production databases** unless explicitly permitted
2. `NOW`: scope must state the instance, account privileges, and whether write/delete is allowed
3. `NEXT`: client-tool paths
4. `ACT`: exposure surface → authentication → authorization → configuration → exploit-chain validation (safe)

## Applicable scenarios

- Database unauthorized access / weak passwords / wrong bind on 0.0.0.0
- Excessive privileges, dangerous features (xp_cmdshell, COPY PROGRAM, UDF)
- Lateral movement: from application account to DBA
- NoSQL injection and Redis file-write, etc. (authorized environment)

## Workflow

```text
□ Network exposure and TLS
□ Account roles and grantees
□ Access control on sensitive tables
□ Dangerous configuration: file_priv, xp_cmdshell, load_file
□ Whether audit logging is enabled
□ Backup and snapshot permissions
```

## Toolchain

| Tool | Purpose |
|------|------|
| Official CLI | Connect and enumerate |
| sqlmap | Injection validation (authorized) |
| nuclei | Known-exposure templates |
| Cloud RDS console audit | Configuration |

## References

- `references/db-misconfig-checklist.md`
- `../pentest-tools/` `../cloud-k8s/`

## Routing context

**Upstream**: MASTER R35  
**Downstream**: OS command obtained → attack-chain; cloud-managed → cloud-k8s

## Task-completion self-check

- [ ] Did I avoid unauthorized writes/deletes?
- [ ] Did I distinguish configuration issues from exploitable chains?
- [ ] Checklist?

<!-- skill-trace:1ec30a0ab116eb402a4ae8f6e745c404 -->
