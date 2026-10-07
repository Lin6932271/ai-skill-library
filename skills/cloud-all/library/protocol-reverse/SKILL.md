---
name: protocol-reverse
description: "Use for reverse engineering of custom binary protocols, Protobuf/gRPC, WebSocket frames, and PCAP-driven protocol recovery."
---

# Protocol Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` — confirm authorization and routine operation boundaries
2. `NOW`: confirm whether the task is **protocol/traffic/serialization-format** reversing (pure Web parameter signing → switch to `js-reverse/`)
3. `NOW`: if there is target network interaction → complete scope via `../scripts/case-init.ps1`; ACT against the target is forbidden while `auth` is not granted
4. `NEXT`: read `../tool-index.md`; bootstrap missing tools (tshark/wireshark, etc. may need manual setup)
5. `ACT`: enter workflow Phase 1, produce a draft frame layout or message dictionary

## Applicable scenarios

- Custom TCP/UDP binary protocols
- Protobuf / gRPC / FlatBuffers / MessagePack
- WebSocket / MQTT / private RPC
- PCAP / PCAPNG field and state-machine recovery
- Client-server validation, sequence numbers, encrypted frame headers

## Not this skill

| Case | Where to go |
|------|------|
| HTTP parameter signing / JS encryption only | `js-reverse/` |
| TLS certificate issues only | `pentest-tools/` or browser proxy |
| Deep-dive of an in-firmware protocol stack + emulation | `firmware-pentest/` then back to this skill |

## Workflow

### Phase 1 — collection and triage

```text
□ Get samples: PCAP / proxy export / client logs / binary
□ Mark direction: C→S / S→C; is there a handshake, heartbeat, reconnect?
□ Fixed header? magic number? length field? TLV? fixed-length?
□ Is it compressed (zlib/gzip/lz4) or encrypted (AES/ChaCha inside frames)?
□ tshark -r cap.pcap -T fields -e frame.number -e ip.src -e tcp.payload
```

### Phase 2 — frame-layout recovery

```text
□ Align multiple messages of the same kind, find invariant bytes / incrementing sequence numbers
□ Length field: big/little endian, includes/excludes header
□ Checksum: CRC16/32, checksum, HMAC position
□ Draw the state machine: Connect → Auth → Ready → Request/Response → Close
□ Tools: Wireshark custom dissector draft / ImHex / 010 Editor template / Kaitai Struct
```

### Phase 3 — serialization and encryption

```text
□ Protobuf: .proto recovery (blackboxprotobuf / pbtk / protoc --decode_raw)
□ gRPC: HTTP/2 headers + protobuf body
□ Encryption: find key derivation (client so/dll/JS) → joint with ida-reverse / js-reverse / apk-reverse
□ Replay: only within authorized scope; harmless fields first, then sensitive operations
```

### Phase 4 — deliverables

```text
MUST produce:
- Message-type table (name / opcode / fields)
- At least 1 reproducible decode command or script
- Evidence: raw hex excerpt + decode result (sanitized)
```

## Toolchain

| Tool | Required | Purpose | Bootstrap |
|------|------|------|------|
| tshark / Wireshark | Strongly recommended | PCAP parsing | manual / winget |
| Python3 | Yes | Decode scripts | system |
| blackboxprotobuf | Optional | Unknown protobuf | pip |
| ImHex / 010 | Optional | Structure templates | manual |
| IDA / r2 / Ghidra | As needed | Client serialization functions | see the corresponding skill |

## References

- `references/protocol-workflow.md` — frame layout and Protobuf quick reference
- Related: `../ida-reverse/` `../js-reverse/` `../firmware-pentest/` `../pentest-tools/`

## Routing context

**Upstream**: `MASTER-ROUTING` R21 · `routing.md`  
**Downstream**: needs client algorithm → `ida-reverse`/`js-reverse`; needs exploit replay → `pentest-tools`/`api-security`  
**Peer**: `malware-analysis` (C2 protocols), `digital-forensics` (traffic forensics)

## Task-completion self-check

- [ ] Did I recover the message layout or state machine (not just paste hex)?
- [ ] Is there a reproducible decode command?
- [ ] Did I obey scope / sanitization?
- [ ] Did I write back to field-journal / report Checklist?

<!-- skill-trace:d7941ba73cfa27cd755af33212e523e1 -->
