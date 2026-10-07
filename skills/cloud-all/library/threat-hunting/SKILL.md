---
name: threat-hunting
description: "Use for blue-team threat hunting, detection engineering with Sigma/YARA, SIEM query design, and incident detection validation."
---

# Threat Hunting & Detection Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: confirm blue-team/hunting authorization and the data-source scope (SIEM, EDR exports)
2. `NOW`: state the hypothesis before querying data; don't mindlessly churn through alerts
3. `NEXT`: tools and data-ingestion method
4. `ACT`: hypothesis → query → validate → turn into rules

## Applicable scenarios

- Threat hunting (hypothesis-driven)
- Sigma / YARA detection engineering
- Alert tuning, false-positive analysis
- With `malware-analysis/`: sample-side IOCs → land detections in this skill
- With `digital-forensics/`: case artifacts → lateral hunting

## Workflow

### 1. Build a hypothesis

```text
e.g.: attacker uses living-off-the-land for lateral movement
→ data sources: Sysmon 1/3/10, Windows Security 4624/4648
→ success criterion: find anomalous parent processes or rare account log sources
```

### 2. Query and stacking

```text
□ Baseline: normal admin activity windows and hosts
□ Anomalies: new services, encoded PowerShell, unusual outbound
□ Correlate: same account, multiple hosts, short-window logins
```

### 3. Turn into rules

```yaml
# Sigma skeleton is in malware-analysis; this skill emphasizes:
# - false-positive surface
# - data-source field mapping
# - response playbook links
```

### 4. Validation

```text
□ Atomic tests (Atomic Red Team) only in an authorized lab
□ Replay historical logs to validate recall
```

## Toolchain

| Tool | Purpose |
|------|------|
| Sigma CLI / sigmac | Rule conversion |
| YARA | File/memory |
| SIEM (ELK/Splunk, etc.) | Queries |
| osquery | Endpoint hunting |
| Atomic Red Team | Detection validation (lab) |

## References

- `references/hunting-loop.md`
- `../malware-analysis/references/yara-sigma-rules.md`
- `../digital-forensics/`

## Routing context

**Upstream**: MASTER R27  
**Downstream**: confirmed intrusion → forensics; malicious sample → malware-analysis  
**MUST NOT**: run attack simulations in an unauthorized production environment

## Task-completion self-check

- [ ] Is there a clear hypothesis and conclusion?
- [ ] Do the rules note false positives and data sources?
- [ ] Checklist?

<!-- skill-trace:521e0614560da1d949cc8fa318b76752 -->
