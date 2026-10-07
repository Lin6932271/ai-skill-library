---
name: l-webrecon
description: "MUST on 搞一下/渗透/测安全/注入/加管理员 with URL. Local router to detailed modules."
---

# l-webrecon Local Entry

Scope: authorized pentesting / web security testing / injection / privilege escalation / cloud and domain security (with a URL/target). Detailed modules are installed beside this entry.

## Selection Rules (avoid mis-picking)
1. First read the "Module List" below.
2. Scan the "Module List" below **top to bottom**; use the first one that matches the current task.
   When multiple capabilities are needed, stack at most 3, with entries higher up taking priority.
3. Read the selected local module from `../<MODULE_ID>/SKILL.md`, then apply its task guidance.
4. When none matches exactly, fall through to the "Fallback" at the bottom of this page.

## Local Module Reading

Read the selected module from the adjacent directory `<MODULE_ID>/SKILL.md`. Use the existing local file directly.

## Module List (ordered by priority)

- `pentest-tools` — Pentest tools quick reference: common tools and command cheat sheet.
- `pentest-tools__src-hunter` — Source/sensitive-info hunting: gather source code and credential leads in the target.
- `attack-chain` — Attack-chain orchestration: multi-stage planning of recon → initial access → privilege escalation → lateral movement.
- `api-security` — API security testing: assessment of interface auth, broken access control, rate limiting, CI/CD, etc.
- `network-analysis` — Network analysis: packet capture, protocols, traffic forensics.
- `database-security` — Database security: injection, permissions, and configuration-hardening assessment.
- `windows-ad` — Windows domain security: Kerberos, AD CS, domain privilege-escalation research.
- `identity-federation` — Identity federation: analysis of identity systems such as SSO/OAuth/SAML.
- `cloud-k8s` — Cloud and K8s security: assessment of containers, clusters, and cloud credentials.
- `supply-chain-security` — Supply-chain security: assessment of SBOM, dependencies, and build integrity.
- `email-security` — Email security: phishing, SPF/DKIM, and mail-gateway assessment.
- `wifi-wireless` — Wireless security: Wi-Fi capture, handshake analysis, lab deauth.
- `ot-ics` — OT/ICS security: assessment of PLC, SCADA, and industrial protocols.
- `llm-security` — LLM security: assessment of prompt injection, jailbreak, and data leakage.
- `threat-hunting` — Threat hunting: detection rules, SIEM, alert validation (blue team).
- `code-audit` — Code audit: source-level security vulnerability review.
- `api-design` — API design: design guidance for REST/GraphQL interface structure, versioning, and error conventions.
- `deploy-infra` — Deployment and infrastructure: environment setup and ops deployment.
- `jailbreak-engineering` — Jailbreak engineering: prompt-bypass and safety-boundary research (controlled experiments).

## Fallback
When none of the above matches exactly: for reversing tasks read `reverse_flow_skill`, for pentest tasks read `pentest-tools`, then continue per its body; if still unsure read `skills` for a second routing pass.

<!-- skill-trace:e5a479b7a3376f960789feb62a268372 -->
