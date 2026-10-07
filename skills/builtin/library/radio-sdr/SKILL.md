---
name: radio-sdr
description: "Use for RF/SDR security research including signal identification, replay feasibility study in shielded labs, and wireless protocol analysis outside classic Wi-Fi."
---

# RF / SDR Security Research

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: **spectrum and transmission are strictly regulated by law**; authorized bands / shielded rooms / lab targets only
2. `NOW`: scope must state the equipment, the bands, and whether transmission is allowed (receive-only by default)
3. `ACT`: receive-only identification → demodulation analysis → lab reproduction assessment

## Applicable scenarios

- Non-Wi-Fi RF such as wireless remotes/sensors (authorized)
- Protocol research such as ADS-B/remotes (lawful reception)
- Division of labor with wifi-wireless: this skill leans toward **general SDR RF**; Wi-Fi offense/defense goes to R29

## Workflow

```text
□ Confirm regulations and licensing
□ Receive-only: identify center frequency and modulation
□ GNU Radio / URH analysis
□ Replay only in a shielded room and with written permission
□ Conclusions focus on: is unauthorized control possible / hardening advice
```

## Toolchain

| Tool | Purpose |
|------|------|
| RTL-SDR / HackRF (compliant) | RX/TX hardware |
| URH / GNU Radio | Analysis |
| Inspectrum | Signals |

## References

- `references/sdr-lab-rules.md`
- `../wifi-wireless/` `../ot-ics/` `../hardware-security/`

## Routing context

**Upstream**: MASTER R38
**MUST NOT**: interfere with public communications, or transmit without authorization

## Task-completion self-check

- [ ] Did I default to receive-only and record the regulatory boundary?
- [ ] Checklist?

<!-- skill-trace:3c1db9f3964954e6d0219620cb7e0910 -->
