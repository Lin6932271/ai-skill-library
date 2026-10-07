---
name: supply-chain-security
description: "Use for software supply-chain security assessment covering SBOM, SCA, CI/CD pipelines, container images, build integrity, dependency provenance, and vulnerability reachability."
---

# Supply Chain Security Testing

## ACTION REQUIRED (execute immediately after reading)

2. `NOW`: confirm whether the current task falls within this skill's applicable scope
3. `NEXT`: read `../tool-index.md`, verify tool availability and actual paths
4. `NEXT`: when a tool is missing, invoke bootstrap; do not guess paths
5. `ACT`: enter step 1 of the "Workflow" and execute; do not stop at a confirmation state

> SBOM / SCA / CI/CD pipeline / dependency provenance
> Regulation-driven: US Executive Order SBOM, China national standards, EU CRA

## Applicable scenarios

- Software supply-chain security assessment
- Open-source dependency vulnerability scanning and validation
- CI/CD pipeline security audit
- Container-image security analysis
- Third-party component compliance review
- Build-artifact provenance and integrity verification

## Six-layer supply-chain governance framework

```text
Layer 1: Source-code trust assessment → upstream repo / maintainer / release-history review
Layer 2: Build-pipeline integration → CI/CD security gates, signature verification
Layer 3: Artifact-distribution integrity → signatures, checksums, SBOM attachment
Layer 4: Runtime protection → container scanning, admission control
Layer 5: Continuous monitoring → real-time CVE tracking, vulnerability-reachability analysis
Layer 6: Incident response → supply-chain-attack response, rollback strategy
```

## Workflow

### 1. SBOM generation and audit

```text
Generate SBOM:
□ CycloneDX format: cdxgen → bom.json
□ SPDX format: sbom-tool generate
□ Syft: syft <image|dir> -o spdx-json

Audit focus:
□ Any unknown / unauthorized dependencies
□ Any deprecated / unmaintained packages
□ License-conflict detection
□ Direct-dependency vs transitive-dependency inventory
□ Release timeline and maintainer status of each component
```

### 2. Software Composition Analysis (SCA)

```bash
# OSV-Scanner (free, maintained by Google)
osv-scanner scan -r . --format json

# OWASP Dependency-Track (enterprise-grade continuous monitoring)
docker run -p 8080:8080 dependencytrack/apiserver
# → upload SBOM → auto-match NVD/OSV/GitHub Advisory

# Snyk (commercial)
snyk test --all-projects
snyk monitor  # 持续监控

# Trivy (container + dependency + IaC)
trivy fs .          # 文件系统扫描
trivy image nginx   # 容器镜像
trivy config .      # IaC 配置
```

### 3. Vulnerability-reachability validation

```text
An SCA alert ≠ actual risk! Most SCA tools have only ~15% of alerts actually reachable.

Validation steps:
1. Use Dependency-Track or Trivy to get the CVE list
2. Filter for CVSS ≥ 7.0 vulnerabilities
3. Do reachability analysis for CVEs that have a PoC
   - Code Property Graph slicing: trace the path from user input to the vulnerable function
   - DEPTEX method: EPD (Execution Path Dominance) + LLM semantic validation
4. Validate the PoC in an isolated environment
5. Rank fix priority for reachable vulnerabilities by actual impact
```

Tool references:
- CodeQL: GitHub code query → data-flow analysis
- Snyk Code: reachability tagging
- DEPTEX: LLM-assisted context-aware risk assessment

### 4. CI/CD pipeline security

```text
Security checkpoints:
□ Code commit → pre-commit hook: gitleaks (secret scanning)
□ PR stage → SCA scan (Trivy/OSV-Scanner)
□ Build stage → artifact signing (cosign)
□ Push stage → SBOM attachment (syft + attest)
□ Deploy stage → admission control (OPA/Kyverno + image scan)
□ Runtime → continuous vulnerability monitoring (Dependency-Track)

Pipeline's own security:
□ Pipeline as Code audit (GitHub Actions / GitLab CI config injection)
□ Runner isolation (prevent a malicious build from breaking out of the container)
□ Secret management (Actions Secrets / Vault, no hardcoding)
□ Third-party Action review (pin to a commit SHA, not a tag)
```

### 5. Container-image security

```bash
# Dockerfile audit
hadolint Dockerfile

# Image scan (multi-layer: OS + app dependencies + config)
trivy image --severity HIGH,CRITICAL nginx:latest

# Minimal base image
# Prefer: distroless → alpine → slim → avoid latest
docker scout quickview nginx:latest

# Image signing
cosign sign --key cosign.key myimage:tag
cosign verify --key cosign.pub myimage:tag
```

### 6. Third-party dependency review

```text
New-dependency checklist:
□ Maintenance status: commits in the last 6 months? maintainer activity?
□ Security history: any past malicious-code implants?
□ Dependency tree: how many transitive dependencies does adding it introduce?
□ License: compatible with the project license?
□ Alternatives: is there a safer alternative (Snyk Advisor / Socket.dev score)?

Risk-assessment matrix:
  high maintenance × low dependency count × compatible license → low risk
  low maintenance × high dependency count × license conflict → high risk
```

## Toolchain

| Tool | Purpose | Get it |
|------|------|------|
| OWASP Dependency-Track | Enterprise-grade continuous SCA | `docker pull dependencytrack/apiserver` |
| OSV-Scanner | Free SCA (OSV.dev ecosystem) | `go install github.com/google/osv-scanner` |
| Trivy | Image + dependency + IaC scanning | `apt install trivy` |
| Syft | SBOM generation | `curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh` |
| cdxgen | CycloneDX SBOM generation | `npm install -g @cyclonedx/cdxgen` |
| Cosign | Container signing | `go install github.com/sigstore/cosign/v2/cmd/cosign` |
| Gitleaks | Secret/credential scanning | `go install github.com/gitleaks/gitleaks/v8` |
| Snyk | Commercial SCA + reachability | `npm install -g snyk` |
| CodeQL | Code query + data flow | Built into GitHub Actions |

## References

- `references/sbom-sca-methodology.md` — SBOM + SCA methodology
- `references/cicd-pipeline-security.md` — CI/CD pipeline security audit


## Task-completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step in the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items required by RULES?

<!-- skill-trace:80ed436308ad2f8e2fec61e7695882bb -->
