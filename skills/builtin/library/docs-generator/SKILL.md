---
name: docs-generator
description: "Creates task-oriented technical documentation with progressive disclosure. Use when writing READMEs, API docs, architecture docs, or markdown documentation.\nAlso use this skill at the END of any completed reverse engineering, penetration testing, CTF, or security analysis task to generate a formal report in the user's project directory.\nTrigger keywords: 写报告, 写文档, 出报告, writeup, 技术文档, report, documentation."
---

# Technical Documentation

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: confirm whether the current task falls within this skill's applicable scope
2. `NOW`: read `../tool-index.md`, verify tool availability and actual paths
3. `NEXT`: when a tool is missing, invoke bootstrap; do not guess paths
4. `ACT`: enter step 1 of the "Workflow" and execute; do not stop at a confirmation state

For writing style, tone, and voice guidance, use `Skill(ce:writer)` with **The Engineer** persona.

## Security/reverse-task documentation output

When a reverse/pentest/CTF/security-analysis task is complete, this skill is responsible for generating a formal technical document in the **user's project directory**.

### When it triggers

1. A reverse task is complete and the core conclusions have been produced (algorithm recovery, signature crack, bypass scheme, etc.)
2. A penetration test is complete and vulnerabilities have been found and validated
3. A CTF challenge is solved and the flag has been obtained
4. The user explicitly asks to "write a report / document / writeup"

### Template selection

| Task type | Template to use |
|---------|---------|
| APK/binary/so reversing | `references/security-report-templates.md` → reverse-engineering report |
| Penetration test / vuln hunting | `references/security-report-templates.md` → penetration-test report |
| CTF solve | `references/security-report-templates.md` → CTF Writeup |
| JS/Web signature reversing | `references/security-report-templates.md` → signature-reversing report |
| Generic technical docs | `references/templates.md` → README / API docs |

### Output specification

- **Output location**: the user's current project directory (not the skill-package directory)
- **Filename format**: `YYYY-MM-DD_[type]-[target-short-name]-report.md`
- **If the project has a `docs/` directory**: prefer placing it under `docs/`
- **Encoding**: UTF-8
- **Language**: follow the user's conversation language (Chinese conversation → Chinese report, English conversation → English report)

### Quality requirements

- All code blocks must be directly runnable or have clear context
- No placeholders/TODOs
- Key findings must be backed by evidence
- Reproduction steps must let a third party reproduce independently
- Sensitive information (real tokens, passwords, internal URLs) replaced with placeholders
- **MUST** include the Evidence → Finding → Path chain (see `../ops/evidence-finding-path.md` and template §0)
- **SHOULD** reference the case `scope.md` / `timeline.md` (`../scripts/case-init.ps1`)

### Diagram integration

When generating a report, call the `diagram-generator` skill at appropriate points to generate visual diagrams:

| Report type | Suggested diagram | Diagram type |
|---------|---------|---------|
| Reverse-engineering report | function call graph, data-flow diagram | Mermaid flowchart / sequenceDiagram |
| Penetration-test report | attack-path diagram, network-topology diagram | Mermaid flowchart / Graphviz |
| CTF Writeup | solution-reasoning flowchart | Mermaid flowchart |
| JS signature-reversing report | request-chain sequence diagram, algorithm flowchart | Mermaid sequenceDiagram / flowchart |

Diagrams are embedded into the report markdown as Mermaid code blocks, ensuring they render directly on GitHub/GitLab.

---

## Core Principles

### 1. Progressive Disclosure

Reveal information in layers:

| Layer | Content | User Question |
|-------|---------|---------------|
| 1 | One-sentence description | What is it? |
| 2 | Quick start code block | How do I use it? |
| 3 | Full API reference | What are my options? |
| 4 | Architecture deep dive | How does it work? |

**Warnings, breaking changes, and prerequisites go at the TOP.**

### 2. Task-Oriented Writing

```markdown
<!-- Bad: Feature-oriented -->
## AuthService Class
The AuthService class provides authentication methods...

<!-- Good: Task-oriented -->
## Authenticating Users
To authenticate a user, call login() with credentials:
```

### 3. Show, Don't Tell

Every concept needs a concrete example.

## Formatting Standards

- **Sentence case headings**: "Getting started" not "Getting Started"
- **Max 3 heading levels**: Deeper means split the doc
- **Always specify language** in code blocks
- **Relative paths** for internal links
- **Tables** for structured data with 3+ attributes

## Quality Checklist

- [ ] Code examples tested and runnable
- [ ] No placeholder text or TODOs
- [ ] Matches actual code behavior
- [ ] Scannable without reading everything
- [ ] Reader knows what to do next

## Anti-Patterns

| Problem | Fix |
|---------|-----|
| Wall of text | Break up with headings, bullets, code, tables |
| Buried critical info | Warnings/breaking changes at TOP |
| Missing error docs | Always document what can go wrong |

## Templates

For README, API endpoint, and file organization templates, see [references/templates.md](references/templates.md).

## Related Skills

- `Skill(ce:writer)` - Writing style, tone, and voice (load The Engineer persona)
- `Skill(ce:visualizing-with-mermaid)` - Architecture and flow diagrams


---

## On-Demand Bootstrap

This skill depends on no external tools; it is pure text generation. No bootstrap needed.

If diagrams need to be rendered into the report, it calls the `diagram-generator/` skill.

---

## Routing context

**Upstream entry**: all security/reverse skills call this skill automatically after task completion
**Trigger method**:
- Automatic: executed as step 9 of the behavior chain after task completion
- Manual: the user says "写报告", "出文档", "writeup"

**Peer-related modules**:
- `apk-reverse/` — generate a reverse report after APK reversing is complete
- `ida-reverse/` — generate a reverse report after binary analysis is complete
- `radare2/` — generate a reverse report after CLI analysis is complete
- `js-reverse/` — generate a signature report after JS signature reversing is complete
- `reverse-engineering/` — generate a reverse report after generic reversing is complete
- `field-journal/` — report content also serves as a data source for the evolution journal

**Security report templates**: `references/security-report-templates.md`
**Generic doc templates**: `references/templates.md`


## Task-completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step in the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Does the report contain Evidence / Finding / Path (the ops contract)?
- [ ] Did I complete and write back the Checklist items required by RULES?

<!-- skill-trace:c323001409ffb10385fe13caadee3fd0 -->
