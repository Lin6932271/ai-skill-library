---
name: digital-forensics
description: "Use for digital forensics including memory dumps, disk timelines, PCAP investigation, artifact triage, and IR evidence preservation."
---

# Digital Forensics & IR Artifacts

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` or the organization's IR authorization statement
2. `NOW`: confirm this is **forensics/attribution**, not offensive scanning
3. `NOW`: create a case; prefer read-only copies of evidence (write-protect the original media)
4. `NEXT`: tool-index; Volatility, etc. often run manually
5. `ACT`: preserve hashes → timeline → key artifacts

## Applicable scenarios

- Memory-dump analysis (Volatility 2/3)
- Disk / E01 / dropped-file timelines
- PCAP attribution and protocol reconstruction (can join `protocol-reverse/`)
- Host artifacts: Prefetch, Shimcache, Event Log, browser history
- Incident-response IOC extraction (joint with `malware-analysis/` / `threat-hunting/`)

## Workflow

### 1. Preservation

```text
□ Compute SHA256; record timezone and collection command
□ Work on the copy; keep the original read-only
□ Write chain-of-custody notes into the timeline
```

### 2. Memory

```bash
vol -f mem.dmp windows.info
vol -f mem.dmp windows.pslist
vol -f mem.dmp windows.netscan
vol -f mem.dmp windows.cmdline
```

### 3. Host artifacts

```text
□ Event logs: Security / PowerShell / Sysmon
□ Persistence: Run keys, services, scheduled tasks, WMI
□ Execution traces: Amcache, Prefetch, BAM
```

### 4. Network

```text
□ tshark to tally conversations and DNS
□ Export suspicious streams → protocol-reverse or malware C2 analysis
```

## Toolchain

| Tool | Purpose |
|------|------|
| Volatility 3 | Memory |
| Timeline Explorer / Plaso | Super timeline |
| tshark | PCAP |
| Eric Zimmerman tool set | Windows artifacts |
| Autopsy / FTK Imager | Disk |

## References

- `references/forensics-triage.md`
- `../malware-analysis/` `../threat-hunting/` `../protocol-reverse/`

## Routing context

**Upstream**: MASTER R25  
**Downstream**: deep-dive malicious sample → malware-analysis; rules → threat-hunting

## Task-completion self-check

- [ ] Did I preserve hashes and a copy strategy?
- [ ] Is the timeline reviewable?
- [ ] Are IOCs sanitized and graded?
- [ ] Checklist?

<!-- skill-trace:e2019196a45875fbb5498150f8ddc7f0 -->
