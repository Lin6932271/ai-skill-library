---
name: threat-hunting
description: "Threat Hunting"
---

# Threat Hunting

## Scope

Use this module only for networks and systems owned by your organization. Focus on detecting adversary presence through proactive hypothesis-driven investigation.

## Workflow

1. Formulate hunting hypothesis based on threat intelligence or anomaly observation.
2. Identify relevant data sources: endpoint logs, network flows, authentication events.
3. Develop search queries targeting hypothesis indicators across log platforms.
4. Correlate events across multiple sources to identify attack chains.
5. Develop Sigma or YARA rules to codify detection logic for validated findings.
6. Document true positives with timeline and affected assets.
7. Produce actionable report with detection rules and response recommendations.

## Safety Rules

- Do not access logs or systems outside your organizational authorization.
- Do not share IOCs that could reveal sensitive organizational details externally.
- Do not execute malware samples found during hunting outside isolated sandboxes.
- Do not disrupt production systems during investigation.

## Output

Return evidence table with columns: Hypothesis | Data Source | Finding | IOC | Detection Rule | Confidence.

## 使用前核对

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。正文不表示示例代码已经在本机执行或验证。
