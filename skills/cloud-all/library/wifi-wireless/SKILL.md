---
name: wifi-wireless
description: "Use for wireless security assessment including Wi-Fi capture, WPA handshake analysis, rogue AP detection research, and lab-only deauth testing."
---

# Wi-Fi / Wireless Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read precedent-pentest; **wireless attacks carry high legal risk** — written authorization and a physical scope are mandatory
2. `NOW`: scope must state the target SSID/BSSID/site; scanning neighbor networks is forbidden
3. `NEXT`: confirm the adapter's monitor-mode capability
4. `ACT`: recon → capture → analysis (lab first)

## Applicable scenarios

- Authorized Wi-Fi security assessment
- WPA/WPA2 handshake capture and offline evaluation
- Rogue AP / phishing-hotspot detection research
- Enterprise wireless isolation and portal security

## Workflow

```text
□ iwconfig / airmon-ng to enter monitor mode (legal environment)
□ airodump-ng to lock onto the target BSSID channel
□ Handshake or PMKID capture (target only)
□ hashcat/aircrack offline evaluation of password policy
□ Report: encryption type, isolation, portal bypass, recommendations
```

## Toolchain

| Tool | Purpose |
|------|------|
| aircrack-ng suite | Capture/evaluation |
| hcxdumptool / hcxtools | PMKID |
| hashcat | Password evaluation |
| Wireshark | Management-frame analysis |

## References

- `references/wireless-lab-rules.md`
- `../pentest-tools/` `../attack-chain/` (proximity-access sections)

## Routing context

**Upstream**: MASTER R29
**MUST NOT**: unauthorized deauth, or operating against non-target client networks

## Task-completion self-check

- [ ] Did I strictly lock onto the target BSSID?
- [ ] Did I provide hardening recommendations in the report?
- [ ] Checklist?

<!-- skill-trace:78282b1f26298a3235fc75fb7a4e8573 -->
