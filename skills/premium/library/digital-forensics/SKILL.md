---
name: digital-forensics
description: "Digital Forensics and Incident Response"
---

# Digital Forensics and Incident Response

## Scope

Use this module for evidence the user owns or is authorized to investigate. Preserve originals, minimize collection, and follow the organization's retention and privacy requirements.

## Workflow

1. Record case identifier, collector, source, acquisition time, timezone, tool version, and authorization boundary.
2. Hash original artifacts and work from verified read-only copies.
3. Build a normalized timeline before drawing conclusions.
4. Triage memory, event logs, execution artifacts, persistence locations, browser history, disk images, and packet captures as relevant.
5. Correlate claims across at least two independent evidence sources when possible.
6. Record alternative explanations, missing visibility, and confidence.

## Safety Rules

- Do not alter the original medium or boot an acquired image directly.
- Do not execute recovered binaries, scripts, macros, or documents.
- Minimize exposure of personal data, credentials, tokens, and unrelated content.
- Preserve chain-of-custody notes and clearly mark derived artifacts.

## Output

Return a timestamped evidence table, hashes, collection method, interpretation, confidence, and recommended containment or follow-up. Keep indicators redacted where disclosure would expose credentials or personal data.

## 使用前核对

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。正文不表示示例代码已经在本机执行或验证。
