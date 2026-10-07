---
name: ot-ics
description: "Use for OT/ICS security assessment covering Purdue model zoning, PLC/SCADA exposure, industrial protocol discovery, and safe passive-first evaluation."
---

# OT / ICS Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` — **misoperation in an industrial-control environment can cause physical harm**
2. `NOW`: written authorization must clearly state: site, network segment, whether active scanning / register writes are allowed
3. `NOW`: case-init; default **passive-first**; PLC write operations forbidden before `ready_for_act`
4. `NEXT`: tool-index; most ICS tools need manual setup and an isolated lab network
5. `ACT`: asset and zone identification → exposure surface → read-only validation

## Applicable scenarios

- Industrial-control/SCADA/DCS security assessment (authorized)
- Purdue-model zoning and cross-zone channels
- Modbus/DNP3/S7/EtherNet/IP and other protocol exposure
- Engineering workstations, HMI, historians, jump hosts
- IT/OT convergence boundary (firewall rules, data diodes)

## Safety iron rules (MUST)

```text
MUST NOT, unless explicitly permitted:
- Write coils/registers to a PLC
- High-rate internet-wide scan of production OT
- Interrupt safety-instrumented-system (SIS) related paths
Prefer: read-only identification, traffic mirroring, offline firmware/config analysis
```

## Workflow

### Phase 1 — zoning and assets

```text
□ Purdue L0–L5 sketch: field devices → control → supervision → site DMZ → enterprise
□ Asset inventory: PLC/RTU/HMI/engineering workstation/historian/Jump host
□ Protocol and port baseline (authorized segments only)
```

### Phase 2 — passive and read-only

```text
□ SPAN/mirror PCAP → protocol-reverse / Wireshark ICS dissectors
□ Offline audit of config and engineering files (TIA/RSLogix exports, etc.)
□ Record default passwords and plaintext protocols (Modbus no-auth) as Findings, do not write to disk or change values
```

### Phase 3 — restricted active

```text
□ Low-rate identification, maintenance window
□ Read-only function codes first
□ Evidence at each step; stop and report immediately on anomaly
```

### Phase 4 — firmware/patch surface

```text
□ Controller firmware version → CVE mapping (do not blindly flash firmware)
□ Joint with firmware-pentest for offline image analysis
```

## Toolchain

| Tool | Purpose | Note |
|------|------|------|
| Wireshark ICS dissectors | Passive parsing | Mirrored traffic |
| Nmap NSE (restricted) | Identification | Rate and time window |
| Claroty/Nozomi, etc. | Asset discovery | Commercial/on-site |
| PLC vendor engineering software | Config audit | Offline first |
| binwalk / Ghidra | Firmware | Offline |

## References

- `references/ot-safe-assessment.md`
- `../firmware-pentest/` `../protocol-reverse/` `../network` via pentest-tools

## Routing context

**Upstream**: MASTER R28  
**Downstream**: firmware deep-dive `firmware-pentest`; protocol `protocol-reverse`; IT lateral movement `windows-ad`/`attack-chain`  
**Peer**: do not hit OT with an ordinary Web scanner's default parameters

## Task-completion self-check

- [ ] Did I default to passive/read-only and record the authorization boundary?
- [ ] Did I avoid write operations on control loops (unless explicitly permitted)?
- [ ] Do findings include physical/process-impact notes?
- [ ] Checklist / journal?

<!-- skill-trace:dd5e3362f7e4abb97cc42006c5d1e01e -->
