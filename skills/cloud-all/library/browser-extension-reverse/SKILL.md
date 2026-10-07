---
name: browser-extension-reverse
description: "Use for reverse engineering of browser extensions (Chrome/Firefox) including manifest analysis, background workers, and extension-based credential or traffic logic recovery."
---

# Browser Extension Reverse Engineering

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md`
2. `NOW`: confirm the target is a **browser extension** (crx/xpi/unpacked directory), not ordinary web-page JS (ordinary → `js-reverse/`)
3. `NEXT`: unpack the extension; read the manifest
4. `ACT`: permission surface → background scripts → network/storage hooks

## Applicable scenarios

- Chrome/Edge MV2/MV3 extension analysis
- Firefox extensions
- Malicious-extension IOCs, supply-chain extension poisoning investigation
- Recovering signing/encryption/proxy logic implemented by an extension

## Workflow

### 1. Package

```text
□ Unpack crx / grab the extension directory from the profile
□ manifest.json: permissions, host_permissions, background, content_scripts
□ Assess excessive permissions (<all_urls>, webRequest, debugger)
```

### 2. Logic

```text
□ service_worker / background entry point
□ content_script injection points and world (isolated)
□ chrome.storage / IndexedDB keys
□ Same as `js-reverse`: observe network and message passing (runtime.sendMessage)
```

### 3. Dynamic

```text
□ Load the unpacked directory in developer mode
□ chrome://extensions to check for errors
□ Attach DevTools to the service worker
□ Frida / browser CDP (jshookmcp) when needed
```

## Toolchain

| Tool | Purpose |
|------|------|
| unpack/jq | manifest |
| Chrome DevTools | worker debugging |
| js-reverse toolchain | deep JS |
| YARA | malicious-extension rules |

## References

- `references/extension-analysis.md`
- field-journal entries related to extension recovery
- `../js-reverse/` `../malware-analysis/`

## Routing context

**Upstream**: MASTER R30  
**Downstream**: complex obfuscated JS → `js-reverse`; poisoning investigation → supply-chain / malware

## Task-completion self-check

- [ ] Did I list the permission surface and entry scripts?
- [ ] Did I recover the key data flows?
- [ ] Checklist?

<!-- skill-trace:b0e6242b3a1a47d5bef9cc1ba30a424e -->
