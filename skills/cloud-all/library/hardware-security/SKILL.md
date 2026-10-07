---
name: hardware-security
description: "Use for hardware and embedded interface security research including UART/JTAG discovery, debug pad triage, secure boot overview, and offline firmware extraction support."
---

# Hardware / Embedded Interface Security

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: confirm **physical-access authorization** and device ownership
2. `NOW`: ESD/power safety; read-only probing by default
3. `NEXT`: pair with firmware-pentest for image analysis
4. `ACT`: enclosure and debug-interface identification → consoles → extraction

## Applicable scenarios

- UART / JTAG / SWD debug-port discovery
- Boot logs, root shell, boot interruption
- Flash extraction via teardown
- Feasibility assessment of secure boot / encrypted Flash (non-destructive first)

## Workflow

```text
□ Tear down the authorized device; photograph and label test points
□ Use a multimeter to find GND/VCC/TX/RX; logic levels 1.8/3.3/5V
□ USB-TTL read-only logging; record the baud rate
□ JTAG: enumerate IDCODE; assess whether it is locked
□ Extract the image → hand off to firmware-pentest / ghidra
```

## Toolchain

| Tool | Purpose |
|------|------|
| USB-TTL / logic analyzer | UART |
| J-Link / CMSIS-DAP | Debug |
| bus pirate / flipper (lab) | Multi-protocol |
| binwalk / flashrom | Extraction |

## References

- `references/debug-interface-triage.md`
- `../firmware-pentest/` `../ot-ics/`

## Routing context

**Upstream**: MASTER R34
**MUST NOT**: tear down or damage others' devices without authorization

## Task-completion self-check

- [ ] Did I record the interface levels and pinout?
- [ ] Was the image hash-preserved?
- [ ] Checklist?

<!-- skill-trace:2583ffd922e663264d6da5cc3bb8a21d -->
