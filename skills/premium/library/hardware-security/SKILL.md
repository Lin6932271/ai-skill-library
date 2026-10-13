---
name: hardware-security
description: "Hardware and Embedded Interface Security"
---

# Hardware and Embedded Interface Security

## Scope

Use this module only for a device the user owns or has explicit permission to inspect. Confirm physical access authorization, voltage limits, and whether opening the enclosure is allowed. Default to non-destructive and read-only methods.

## Workflow

1. Photograph and label the board, connectors, components, test pads, and power arrangement.
2. Establish ground and voltage levels with appropriate instruments before connecting an adapter.
3. Observe UART output passively and record baud rate, framing, boot stage, and timestamps.
4. Identify JTAG/SWD candidates and document whether debug access is disabled or authenticated without attempting a bypass.
5. Acquire firmware only through approved read-only methods and hash every image.
6. Assess secure-boot configuration, update verification, debug exposure, and secret storage from offline evidence.

## Safety Rules

- Do not over-voltage, short pads, glitch power, erase flash, unlock debug, or interrupt boot without explicit written authorization and an isolated sacrificial device.
- Do not alter production equipment or safety-critical systems.
- Treat extracted firmware, keys, identifiers, and customer data as sensitive evidence.

## Output

Return a pinout/evidence table, acquisition hashes, observed boot and debug posture, confidence, physical safety notes, and remediation. Clearly distinguish passive observation from any authorized active step.

## 使用前核对

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。正文不表示示例代码已经在本机执行或验证。
