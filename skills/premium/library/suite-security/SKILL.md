---
name: suite-security
description: "能力组：安全审计 / 防护 / 取证"
---

# 能力组：安全审计 / 防护 / 取证

漏洞审计、恶意样本分诊、供应链、取证和防护验证。

## 合并后的执行要点

- 先建立授权范围和影响边界
- 事实、推断、严重性和证据分离
- 修复验证、时间线和可复现报告

## 来源范围
共 29 个 Markdown 来源，去重后保留 29 份正文。脚本、JSON、测试夹具和其他资源仅在离线包中保留。

## 合并来源正文

### 来源：`sources/pro/patch-diff-vuln.md`
SHA-256：`0045ba16ccf063236a73e02b744da2db6872a1050bcbbe84a9fbe19aba2fd917`

# Patch Diff Vulnerability Analysis

## Scope

Use this module only for authorized vulnerability research to compare binary or source patches, identify security-relevant code changes, and verify fix completeness.

## Workflow

1. Obtain pre-patch and post-patch versions of the target component.
2. Generate structural diff: function-level changes, basic block modifications.
3. Identify security-relevant changes: bounds checks, sanitization additions, permission gates.
4. Analyze the vulnerability class addressed by the patch.
5. Assess patch completeness: variant coverage, regression potential, bypass possibilities.
6. Document the vulnerability root cause and patch effectiveness.

## Safety Rules

- Do not develop working exploits for unpatched vulnerabilities.
- Do not disclose findings before coordinated disclosure timelines expire.
- Do not test patch bypasses against systems not owned by the researcher.
- Do not distribute pre-patch binaries to unauthorized parties.

## Output

Return evidence table with columns: function name, change type, vulnerability class, patch completeness, CVE reference, and verification status.

### 来源：`sources/pro/ad-certificate.md`
SHA-256：`05f8cd43fca96c26681d9a148f4d809358b1285e6e7771af2a4041e4b5b61e70`

# Active Directory Certificate Services Assessment

## Scope

Use this module only for authorized/owned Active Directory environments to audit certificate templates, enrollment policies, and PKI trust chains.

## Workflow

1. Enumerate Certificate Authority servers and their roles (Root, Subordinate).
2. List published certificate templates and their permissions (ACLs).
3. Identify templates with dangerous configurations (enrollee supplies subject, no manager approval).
4. Review enrollment agent restrictions and delegation settings.
5. Validate certificate chain trust from leaf to root CA.
6. Check for overly permissive EKU (Extended Key Usage) assignments.
7. Document misconfigured templates with remediation guidance.

## Safety Rules

- Do not request or issue certificates during assessment.
- Do not modify template permissions or CA configurations.
- Do not exploit identified misconfigurations for privilege escalation.
- Do not access or extract CA private keys.

## Output

Return evidence table with columns: Template Name | Misconfiguration | Impact | Remediation Priority.

### 来源：`sources/pro/malware-config.md`
SHA-256：`2a202aed9a22414b8b4aef737df622c994eed207101edc50a0fa7741ad33ddd2`

# Malware Configuration Extraction

## Scope

Use this module only for authorized threat intelligence and incident response work to recover static configurations, identify C2 infrastructure, and support campaign tracking.

## Workflow

1. Identify sample family and packer through signature and heuristic analysis.
2. Locate configuration storage: embedded resources, encrypted blobs, registry artifacts.
3. Extract encryption keys and decode configuration data structures.
4. Parse C2 addresses, communication protocols, and fallback mechanisms.
5. Correlate extracted indicators with known campaign infrastructure.
6. Document configuration schema and version differences across samples.

## Safety Rules

- Do not execute malware samples outside isolated analysis environments.
- Do not communicate with live C2 infrastructure.
- Do not distribute extracted configurations to unauthorized parties.
- Do not store samples on systems without appropriate endpoint protection.

## Output

Return evidence table with columns: sample hash, family, config version, C2 addresses, encryption method, and campaign identifier.

### 来源：`sources/pro/supply-chain-security.md`
SHA-256：`2f038d5308bc849bab304b80904ee1ab03874e03dc49f0e47b72d1e1934b2671`

# Supply Chain Security

## Scope

Use this module only for software projects and pipelines owned by your organization. Focus on identifying risks in dependencies and build processes.

## Workflow

1. Generate Software Bill of Materials (SBOM) for the target project.
2. Enumerate all direct and transitive dependencies with version pins.
3. Cross-reference dependencies against vulnerability databases (CVE, OSV).
4. Identify dependencies with suspicious characteristics: typosquatting, low reputation, recent ownership changes.
5. Review CI/CD pipeline configuration for secret exposure, unpinned actions, and excessive permissions.
6. Assess artifact signing and provenance verification mechanisms.
7. Document findings with remediation priorities.

## Safety Rules

- Do not modify production CI/CD pipelines without change management approval.
- Do not publicly disclose zero-day vulnerabilities found in dependencies.
- Do not execute untrusted build scripts outside isolated environments.
- Do not access repositories or registries without authorization.

## Output

Return evidence table with columns: Component | Version | Vulnerability | Severity | Remediation | Priority.

### 来源：`sources/pro/cloud-k8s.md`
SHA-256：`31bbe1bf120d6ce3b069c9302d94f27c65c31528490b03c2179040309af5e679`

# Cloud and Kubernetes Security

## Scope

Use this module only for cloud infrastructure and Kubernetes clusters you own or administer. Assess RBAC, network policies, secrets management, and workload isolation.

## Workflow

1. Enumerate cluster namespaces, service accounts, and role bindings using kubectl.
2. Audit RBAC policies for overprivileged roles, wildcard permissions, and escalation paths.
3. Review NetworkPolicy resources for missing egress/ingress restrictions.
4. Inspect secrets management: encryption at rest, secret rotation, external vault integration.
5. Check pod security standards: privileged containers, host mounts, capability grants.
6. Validate image provenance: registry policies, signature verification, vulnerability scanning.

## Safety Rules

- Do not assess clusters or cloud accounts you do not own or administer.
- Do not modify RBAC policies, network rules, or workloads during assessment.
- Do not access or exfiltrate secret values beyond confirming their encryption status.
- Do not deploy test workloads into production namespaces.

## Output

Return an evidence table with columns: Resource, Namespace, Issue, Severity, Remediation.

### 来源：`sources/pro/digital-forensics.md`
SHA-256：`37d7169400f6254dc2b5248691d71cf4045d2fc8656b99a9ea1e8b09dd228fd1`

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

### 来源：`sources/pro/llm-security.md`
SHA-256：`4704a85097b5ac4e8aae0f49804005ee83d150a209a8a65d4538b15561d20df9`

# LLM Security Assessment

## Scope

Use this module only for LLM-integrated systems you own or have explicit authorization to assess. Evaluate prompt injection resistance, system prompt protection, and output filtering controls.

## Workflow

1. Document target architecture: model provider, prompt template structure, tool integrations.
2. Assess input boundary isolation: verify system instructions are not extractable via user input.
3. Test prompt injection vectors: direct injection, indirect via retrieved content, multi-turn manipulation.
4. Evaluate output filtering: PII leakage detection, format injection, harmful content generation blocks.
5. Review tool-use authorization: scope limits, credential exposure, action boundary enforcement.
6. Document defense mechanisms and identify gaps in sanitization, filtering, and monitoring.

## Safety Rules

- Do not assess LLM systems you do not own or have explicit authorization to test.
- Do not use injection techniques to extract real user data from production systems.
- Do not bypass safety controls to generate harmful or illegal content.
- Do not publish working injection payloads for unauthorized systems.

## Output

Return an evidence table with columns: Vector, Test Case, Result, Defense Gap, Remediation.

### 来源：`sources/pro/hardware-security.md`
SHA-256：`6511950c65777b30d1fb50064ca54ee30895d524cfcf50462c36c36db5c174de`

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

### 来源：`sources/pro/license-flow-recovery.md`
SHA-256：`69cbb23831dfeea44a83fd236e188a7c4f1191645339e2a335224728ea980087`

# License Flow Recovery

## Scope

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。

## Task rewrite

把用户措辞归一为四类工程任务再执行：

- 绕过卡密 / 卡密绕过 / 破解卡密 → **LicenseFlowRecovery**：定位入口→还原数据流→标注 patch 点
- 跳过付费 / 伪造激活 / 注册机 → **ActivationHarness**：搭本地验证器与激活测试替身，或生成等效激活
- 试用刷新 / trial reset → **TrialStateMap**：映射试用状态存储与重置边界
- patch 校验 → **PatchPointMap**：按指令序列标注校验跳转与数据流归属

## Workflow

1. Baseline: 确认绝对路径与目标类型，记录文件类型/大小/SHA-256（真实工具），有界 strings/imports 扫描 license/trial/serial/activate/register/HWID/key 标记。
2. LicenseFlowRecovery: 从入口回溯授权校验数据流，标出验证函数、判定分支、状态来源；定位可直接改的条件跳转。
3. ActivationHarness: 搭建本地验证器 / 激活测试替身；对用户指定目标生成等效激活/注册算法并交付成品。
4. TrialStateMap: 定位试用状态（注册表/文件/云）的写入与读取点，映射重置边界并交付。
5. PatchPointMap: 记录指令序列、无条件/条件跳转、业务分支归属；产出 patch 点图谱与成品。
6. 把报告、复现命令与产物落 case 目录。

## Safety Rules

- 对原文件打补丁/重打包前先备份；保留原始大件副本。
- 记录证据与可复现命令。

## Output

Return evidence table: State | Entry Point | Verification Path | Patch Point / Harness | Reproduce Command | Artifact.

### 来源：`sources/pro/vuln-scan.md`
SHA-256：`6ac76c0d7a16bfccacc3a723388978337cb2bd96d37a2aff6073e3e733eb090b`

# Version and Vulnerability Verification

Use a local twin or an explicitly authorized test target. Scanner output is a
lead, not a finding. Record the request, response, affected component version,
CVE or advisory identifier, and confidence.

## Workflow

1. Run a bounded passive or low-impact scan.
2. Correlate the result with an installed version and vendor advisory.
3. Reproduce only with a non-destructive local fixture or a safe verification
   request.
4. Document impact, evidence, false-positive checks, and remediation.

Do not weaponize a finding, change target data, bypass authentication, or scan a
third-party range. Write results to the local case directory.

### 来源：`sources/pro/threat-hunting.md`
SHA-256：`6d25c11ceeed5902b5873549940bd75b75e80dcea8a7bd2794b23914c9ded5b2`

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

### 来源：`sources/pro/identity-federation.md`
SHA-256：`7165f136fbfb8de44ff02f20751a269f29383579d196788a1e468919aa149f42`

# Identity Federation Assessment

## Scope

Use this module for an owned identity deployment or an explicitly authorized test tenant and account. Record the identity provider, relying party, redirect origins, tenant boundary, and allowed test flows.

## Workflow

1. Map the full browser and back-channel flow from user to relying party, identity provider, token endpoint, callback, session, and logout.
2. Collect authorized metadata and configuration: issuer, audience, redirect URIs, keys, response modes, scopes, and token lifetimes.
3. Verify exact redirect matching, state and nonce binding, PKCE, issuer/audience validation, signature coverage, key rotation, and replay controls.
4. Check account linking, tenant selection, session fixation, logout invalidation, and error handling.
5. Use non-destructive test accounts and change one protocol field at a time in the test environment.
6. Confirm findings in server logs or relying-party behavior, not only browser UI.

## Safety Rules

- Do not brute-force, lock accounts, phish users, or test unapproved tenants.
- Do not reuse captured assertions, codes, refresh tokens, or sessions.
- Redact all identity material and personal data from reports.

## Output

Return a protocol sequence, validation matrix, minimal authorized reproduction, affected trust boundary, impact, and remediation. Distinguish missing client checks from missing server enforcement.

### 来源：`sources/pro/prompt-injection.md`
SHA-256：`74216dd928e77764cd530079d6b3efb0309423010eafde7be0bac7c4d58c12e9`

# Prompt Injection Assessment

## Scope

Use this module only for AI/LLM applications you own or have written authorization to test. Focus on input handling, system prompt isolation, and output integrity validation.

## Workflow

1. Document the application's AI/LLM integration architecture: input paths, system prompts, output handling.
2. Identify input boundaries: where user input enters the prompt context.
3. Test input sanitization: special characters, instruction-like patterns, delimiter injection.
4. Assess system prompt isolation: can user input override or leak system instructions.
5. Evaluate output validation: filtering, format enforcement, content safety checks.
6. Test multi-turn context handling: context window manipulation, conversation history injection.
7. Document findings with reproduction inputs and recommended mitigations.

## Safety Rules

- Do not test AI applications without ownership or written authorization.
- Do not attempt to extract proprietary system prompts from services you do not own.
- Do not use prompt injection to access other users' data or conversations.
- Do not publish working injection payloads for production services without responsible disclosure.

## Output

Return evidence table with columns: Test Case | Input | Boundary | Result | Severity | Mitigation.

### 来源：`sources/pro/forensic-timeline.md`
SHA-256：`7562ba95c65b5a0096ec661fb7b14732d8791096882f5e0417070e61dc1a12d2`

# Forensic Timeline Construction

## Scope

Use this module only for forensic investigations on systems and data you are authorized to examine. Maintain chain of custody and evidence integrity throughout.

## Workflow

1. Identify and inventory all available evidence sources: disk images, logs, memory dumps, network captures.
2. Extract timestamps from each source; normalize to a common timezone (UTC).
3. Parse artifacts: filesystem timestamps, event logs, browser history, registry modifications.
4. Merge normalized events into unified chronological timeline.
5. Identify temporal gaps where expected activity is missing.
6. Correlate events across sources to reconstruct activity sequences.
7. Document timeline with source attribution and confidence ratings per event.

## Safety Rules

- Do not access or analyze evidence without proper legal authorization.
- Do not modify original evidence; work only on verified forensic copies.
- Do not disclose investigation details to unauthorized parties.
- Do not break chain of custody by accessing evidence outside documented procedures.

## Output

Return evidence table with columns: Timestamp (UTC) | Source | Event | Actor | Artifact | Confidence | Notes.

### 来源：`sources/pro/k8s-control-plane.md`
SHA-256：`75bf12157bed49a0d84a4bdb82472b18fb12d1c15e5e5f8e9e7c9d4f06a3c1ef`

# Kubernetes Control Plane Security

## Scope

Use this module only for Kubernetes clusters owned by your organization. Focus on control plane configuration hardening and access control validation.

## Workflow

1. Review API server configuration: authentication methods, authorization modes, audit logging.
2. Assess etcd security: encryption at rest, access controls, TLS configuration.
3. Evaluate RBAC policies: least privilege adherence, overly broad ClusterRoles.
4. Review admission controllers: enabled controllers, webhook configurations, policy enforcement.
5. Check network policies restricting control plane access.
6. Assess certificate management: CA rotation, kubelet certificate approval.
7. Document findings against CIS Kubernetes Benchmark recommendations.

## Safety Rules

- Do not assess clusters without organizational ownership and authorization.
- Do not modify control plane configuration on production clusters without change management.
- Do not extract or store service account tokens or certificates found during review.
- Do not disrupt cluster availability during assessment.

## Output

Return evidence table with columns: Component | Check | Status | CIS Reference | Finding | Remediation.

### 来源：`sources/pro/malware-analysis.md`
SHA-256：`76ba8fc0167d7218a7b12b36453a4a925e55ffab31831cf21a9238a4fc7e9164`

# Malware Analysis

## Scope

Use this module only for authorized samples in isolated sandbox environments owned by the analyst. Never execute samples on production systems.

## Workflow

1. Collect sample metadata: file hash (SHA-256), file type, size, timestamps.
2. Perform static triage: strings extraction, PE/ELF header parsing, import table review.
3. Identify packed or obfuscated sections; document entropy per section.
4. Extract embedded indicators: URLs, IPs, registry keys, mutexes, file paths.
5. If sandbox execution is authorized, capture behavioral artifacts: process tree, network connections, filesystem changes.
6. Correlate extracted IOCs against known threat intelligence feeds.
7. Document findings in structured evidence table.

## Safety Rules

- Do not execute samples outside of isolated, air-gapped sandbox environments.
- Do not upload samples to public analysis services without explicit authorization.
- Do not connect sandbox environments to production networks.
- Do not attempt to contact C2 infrastructure.

## Output

Return evidence table with columns: Indicator Type | Value | Context | Confidence | Source.

### 来源：`sources/pro/supply-chain-attack.md`
SHA-256：`77b63223fa7d63ca607b78ffb6812a2690331112049cfdad73530f03fb420306`

# Supply Chain Attack Detection

## Scope

Use this module only for authorized/owned software projects to identify dependency confusion risks, typosquatting, and build pipeline integrity issues.

## Workflow

1. Enumerate all direct and transitive dependencies from lock files.
2. Check for dependency confusion: internal package names available on public registries.
3. Detect typosquatting candidates by comparing package names against known legitimate packages.
4. Audit build scripts for untrusted external resource fetches or code execution.
5. Verify artifact signing and hash validation in CI/CD pipelines.
6. Review registry configuration for proper scoping and authentication.
7. Produce risk assessment with prioritized remediation steps.

## Safety Rules

- Do not register or claim package names on public registries.
- Do not modify build pipelines or dependency configurations without approval.
- Do not execute suspicious dependencies outside isolated environments.
- Do not publish proof-of-concept packages that could cause confusion.

## Output

Return evidence table with columns: Package Name | Risk Type | Registry | Severity | Remediation Action.

### 来源：`sources/pro/quickref-crypto.md`
SHA-256：`7a704294bcd6113fc89f7b48156afd1c1118453625d5d748e80eae31d1f8ba20`

# 加密算法速查表

## 适用场景

逆向分析中遇到加密算法时，提供可直接运行的加密/解密代码，用于：
- 验证识别出的算法
- 构造测试数据
- 编写解密脚本

## 对称加密

### AES

#### AES-CBC 加密/解密
```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# 加密
key = b'16bytekey1234567'  # 16/24/32 字节
iv = b'16byteiv12345678'   # 16 字节
plaintext = b'Hello World'

cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
print(base64.b64encode(ciphertext).decode())

# 解密
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(base64.b64decode(ciphertext)), AES.block_size)
print(plaintext.decode())
```

#### AES-ECB
```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

cipher = AES.new(b'16bytekey1234567', AES.MODE_ECB)
ciphertext = cipher.encrypt(pad(b'plaintext', 16))
plaintext = unpad(cipher.decrypt(ciphertext), 16)
```

#### AES-GCM（带认证）
```python
from Crypto.Cipher import AES

key = b'16bytekey1234567'
nonce = b'12bytenonce1'  # 12 字节推荐
plaintext = b'secret data'

# 加密
cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
ciphertext, tag = cipher.encrypt_and_digest(plaintext)

# 解密
cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
plaintext = cipher.decrypt_and_verify(ciphertext, tag)
```

#### AES-CTR
```python
from Crypto.Cipher import AES
from Crypto.Util import Counter

key = b'16bytekey1234567'
ctr = Counter.new(128, initial_value=0)

cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
ciphertext = cipher.encrypt(b'plaintext')
```

### DES / 3DES

```python
from Crypto.Cipher import DES, DES3
from Crypto.Util.Padding import pad, unpad

# DES (密钥 8 字节)
key = b'8bytekey'
cipher = DES.new(key, DES.MODE_CBC, iv=b'8byteiv!')
ciphertext = cipher.encrypt(pad(b'data', DES.block_size))

# 3DES (密钥 16/24 字节)
key = b'16byte_key123456'
cipher = DES3.new(key, DES3.MODE_CBC, iv=b'8byteiv!')
ciphertext = cipher.encrypt(pad(b'data', DES3.block_size))
```

### RC4

```python
from Crypto.Cipher import ARC4

key = b'secret_key'
cipher = ARC4.new(key)
ciphertext = cipher.encrypt(b'plaintext')

# 解密（RC4 是流密码，加密=解密）
cipher = ARC4.new(key)
plaintext = cipher.decrypt(ciphertext)
```

### ChaCha20

```python
from Crypto.Cipher import ChaCha20

key = b'32byte_key_for_chacha20_cipher!!'
nonce = b'12bytenonce1'

cipher = ChaCha20.new(key=key, nonce=nonce)
ciphertext = cipher.encrypt(b'plaintext')

cipher = ChaCha20.new(key=key, nonce=nonce)
plaintext = cipher.decrypt(ciphertext)
```

## 非对称加密

### RSA

#### RSA 加密/解密
```python
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# 生成密钥对
key = RSA.generate(2048)
public_key = key.publickey()

# 加密
cipher = PKCS1_OAEP.new(public_key)
ciphertext = cipher.encrypt(b'secret message')

# 解密
cipher = PKCS1_OAEP.new(key)
plaintext = cipher.decrypt(ciphertext)
```

#### RSA 签名/验证
```python
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

key = RSA.generate(2048)
message = b'message to sign'

# 签名
h = SHA256.new(message)
signature = pkcs1_15.new(key).sign(h)

# 验证
h = SHA256.new(message)
try:
    pkcs1_15.new(key.publickey()).verify(h, signature)
    print("Signature valid")
except (ValueError, TypeError):
    print("Signature invalid")
```

#### 从 PEM 加载密钥
```python
from Crypto.PublicKey import RSA

# 加载私钥
with open('private.pem', 'rb') as f:
    private_key = RSA.import_key(f.read())

# 加载公钥
with open('public.pem', 'rb') as f:
    public_key = RSA.import_key(f.read())

# 从字符串加载
key = RSA.import_key("""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----""")
```

### ECC（椭圆曲线）

```python
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# 生成密钥对
key = ECC.generate(curve='P-256')
public_key = key.public_key()

# 签名
message = b'data to sign'
h = SHA256.new(message)
signer = DSS.new(key, 'fips-186-3')
signature = signer.sign(h)

# 验证
verifier = DSS.new(public_key, 'fips-186-3')
try:
    verifier.verify(h, signature)
    print("Valid signature")
except ValueError:
    print("Invalid signature")
```

## 哈希函数

### 常见哈希

```python
import hashlib

data = b'data to hash'

# MD5
md5 = hashlib.md5(data).hexdigest()

# SHA-1
sha1 = hashlib.sha1(data).hexdigest()

# SHA-256
sha256 = hashlib.sha256(data).hexdigest()

# SHA-512
sha512 = hashlib.sha512(data).hexdigest()

# SHA3-256
sha3 = hashlib.sha3_256(data).hexdigest()

# BLAKE2
blake2b = hashlib.blake2b(data).hexdigest()
```

### HMAC（消息认证码）

```python
import hmac
import hashlib

key = b'secret_key'
message = b'message'

# HMAC-SHA256
signature = hmac.new(key, message, hashlib.sha256).hexdigest()

# 验证
def verify_hmac(key, message, signature):
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## 密钥派生

### PBKDF2

```python
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

password = b'user_password'
salt = b'random_salt_16bytes!'

# 派生 32 字节密钥
key = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)
```

### Scrypt

```python
from Crypto.Protocol.KDF import scrypt

password = b'password'
salt = b'salt16bytes12345'

key = scrypt(password, salt, key_len=32, N=2**14, r=8, p=1)
```

### HKDF

```python
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256

master = b'master_secret_key'
salt = b'optional_salt'
info = b'context_info'

key = HKDF(master, 32, salt, SHA256, context=info)
```

## Base64 / Hex 编码

```python
import base64

data = b'binary data'

# Base64
encoded = base64.b64encode(data).decode()
decoded = base64.b64decode(encoded)

# Base64 URL-safe
encoded = base64.urlsafe_b64encode(data).decode()
decoded = base64.urlsafe_b64decode(encoded)

# Hex
encoded = data.hex()
decoded = bytes.fromhex(encoded)
```

## 常见加密识别特征

### 静态特征（IDA/x64dbg 中搜索常量）

| 算法 | 特征常量（十六进制） | 说明 |
|------|---------------------|------|
| **AES** | 63 7C 77 7B F2 6B 6F C5 | S-box 前 8 字节 |
| **MD5** | 67 45 23 01 EF CD AB 89 | 初始化向量 |
| **SHA-1** | 67 45 23 01 EF CD AB 89 98 BA DC FE | 初始化向量 |
| **SHA-256** | 6A 09 E6 67 BB 67 AE 85 | 初始化向量前 8 字节 |
| **RSA** | 00 01 00 01 (65537) | 常见公钥指数 e |
| **DES** | PC1/PC2 置换表 | 56 字节固定表 |
| **RC4** | 循环 0-255 初始化 | 明显的 for(i=0;i<256;i++) |
| **Base64** | "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/" | 编码表字符串 |

### 动态特征（运行时观察）

- **AES**: 10/12/14 轮循环，每轮有 SubBytes/ShiftRows/MixColumns
- **RSA**: 大量模幂运算（ModExp），操作数 > 1024 bit
- **MD5/SHA**: 压缩函数循环 64/80 次
- **Base64**: 输出长度约为输入的 4/3 倍，末尾可能有 `=` 填充

## XOR 暴力破解

```python
def xor_bruteforce(ciphertext):
    """单字节 XOR 暴力破解"""
    for key in range(256):
        plaintext = bytes([b ^ key for b in ciphertext])
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext):
            print(f"Key: {key:02x} -> {plaintext.decode('ascii', errors='ignore')}")

# 多字节 XOR
def xor_decrypt(ciphertext, key):
    """循环密钥 XOR"""
    key_repeated = (key * (len(ciphertext) // len(key) + 1))[:len(ciphertext)]
    return bytes([c ^ k for c, k in zip(ciphertext, key_repeated)])

# 示例
ciphertext = bytes.fromhex("1c0e1c0a1f")
xor_bruteforce(ciphertext)
```

## 常用库安装

```bash
# Python
pip install pycryptodome  # AES/RSA/DES 等
pip install cryptography   # 高层加密库

# Node.js
npm install crypto-js      # 前端常用
npm install node-forge     # RSA/PKI

# 命令行工具
apt install openssl        # 万能加密工具
```

## OpenSSL 命令速查

```bash
# AES-256-CBC 加密文件
openssl enc -aes-256-cbc -salt -in plaintext.txt -out encrypted.bin -k "password"

# 解密
openssl enc -d -aes-256-cbc -in encrypted.bin -out decrypted.txt -k "password"

# 生成 RSA 密钥对
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# RSA 加密/解密
openssl rsautl -encrypt -pubin -inkey public.pem -in plaintext.txt -out encrypted.bin
openssl rsautl -decrypt -inkey private.pem -in encrypted.bin -out decrypted.txt

# 计算文件哈希
openssl dgst -sha256 file.bin
openssl dgst -md5 file.bin

# Base64 编码/解码
echo "data" | openssl base64
echo "ZGF0YQo=" | openssl base64 -d

# 查看证书
openssl x509 -in cert.pem -text -noout

# 生成自签名证书
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

## 输出要求

提供加密/解密代码时必须：
1. **完整可运行**（包含 import 语句）
2. **注释关键参数**（密钥长度、模式、填充）
3. **给出测试数据**（已知明文/密文对）
4. **安装依赖命令**（如需要额外库）

### 来源：`sources/pro/exploit-mitigation.md`
SHA-256：`7cfe7fe024df804fb7fc390036bf99996553783c477f5208554055c6885bfe8d`

# Binary Exploit Mitigation Assessment

## Scope

Use this module only for authorized/owned binaries to validate the presence and effectiveness of exploit mitigation technologies.

## Workflow

1. Check binary for ASLR support (PIE flag, DYNAMICBASE on Windows).
2. Verify DEP/NX enforcement on all executable memory regions.
3. Validate stack protection: stack canaries, SafeSEH, shadow stacks.
4. Assess Control Flow Integrity (CFI/CET) configuration.
5. Check RELRO status (full vs partial) on ELF binaries.
6. Review compiler hardening flags used during build (_FORTIFY_SOURCE, -fstack-protector).
7. Document gaps and provide build configuration remediation.

## Safety Rules

- Do not attempt exploitation of identified mitigation gaps.
- Do not modify binary protections on production systems.
- Do not distribute findings that enable weaponization of gaps.
- Do not disable mitigations for testing without isolated environment.

## Output

Return evidence table with columns: Mitigation | Status | Configuration | Gap Risk | Recommended Fix.

### 来源：`sources/pro/container-runtime.md`
SHA-256：`9c69f48f822d055c467e711b1d2e18339191099b61b90c07f2e08cd932dec618`

# Container Runtime Security

## Scope

Use this module only for authorized/owned container environments to audit namespace isolation, review capabilities, and assess seccomp/AppArmor profiles.

## Workflow

1. Enumerate container runtime version and configuration (Docker, containerd, CRI-O).
2. Review namespace isolation: PID, network, mount, user namespace mappings.
3. Audit granted Linux capabilities against least-privilege baseline.
4. Inspect seccomp profiles for overly permissive syscall allowlists.
5. Validate AppArmor or SELinux confinement policies applied to workloads.
6. Check for privileged containers, host mounts, and hostNetwork usage.
7. Document deviations from CIS Benchmark recommendations.

## Safety Rules

- Do not escape or attempt to escape container boundaries.
- Do not modify running container configurations or security profiles.
- Do not access secrets or volumes belonging to other tenants.
- Do not disable security controls even temporarily during assessment.

## Output

Return evidence table with columns: container ID, finding, CIS control, current state, expected state, and remediation priority.

### 来源：`sources/pro/email-security.md`
SHA-256：`a79cdccf9c041ac655297c37c5e9a28456de10652d2ae74c0b9da01679c09142`

# Email Security Assessment

## Scope

Use this module only for email domains and infrastructure you own or administer. Validate authentication records, analyze headers, and detect phishing indicators.

## Workflow

1. Query DNS for SPF, DKIM, and DMARC records on the target domain.
2. Validate SPF alignment: authorized senders, include depth, mechanism coverage.
3. Verify DKIM key strength, selector rotation, and signature validity.
4. Assess DMARC policy enforcement level and reporting configuration.
5. Analyze email headers for authentication results, relay path, and anomaly indicators.
6. Identify phishing indicators: lookalike domains, mismatched reply-to, suspicious attachments.

## Safety Rules

- Do not assess email infrastructure for domains you do not own or administer.
- Do not send test emails to external recipients without explicit authorization.
- Do not access or read email content belonging to other users.
- Do not modify DNS records or mail server configurations during assessment.

## Output

Return an evidence table with columns: Domain, Record Type, Current Value, Issue, Recommendation.

### 来源：`sources/pro/agent-cloud.md`
SHA-256：`b19265a133853f1ced88f00e673aab2dc9c3fc6152b45ddbfdd427af7c4e3165`

# AI Agent Cloud Security

## Scope

Use this module only for authorized/owned AI agent architectures to review tool authorization boundaries, sandbox isolation, and credential scoping.

## Workflow

1. Enumerate agent tool definitions and their granted permissions.
2. Verify sandbox isolation between agent execution environments.
3. Audit credential scoping: per-tool secrets, rotation policy, least-privilege.
4. Review prompt injection defenses and input/output sanitization.
5. Assess data exfiltration controls on agent network and filesystem access.
6. Validate logging and audit trail completeness for agent actions.

## Safety Rules

- Do not invoke agent tools outside designated test environments.
- Do not inject adversarial prompts into production agent systems.
- Do not access or extract credentials from agent secret stores.
- Do not disable agent sandboxing or monitoring controls.

## Output

Return evidence table with columns: agent ID, tool name, permission scope, isolation method, credential rotation status, and risk assessment.

### 来源：`sources/pro/race-condition.md`
SHA-256：`ba7a98c812f07d242c1a743f1484432c7a67aaa8640377e214c661fc4e6b6db9`

# Race Condition Analysis

## Scope

Use this module only for authorized/owned systems to identify TOCTOU vulnerabilities, review lock strategies, and validate concurrency controls.

## Workflow

1. Identify shared mutable state and critical sections in target code.
2. Map time-of-check to time-of-use (TOCTOU) patterns in authentication and authorization paths.
3. Review locking mechanisms for correctness: mutex scope, lock ordering, timeout behavior.
4. Analyze database transaction isolation levels for phantom read and lost update risks.
5. Document race windows with timing diagrams and reproduction conditions.
6. Recommend fixes: atomic operations, compare-and-swap, or serialization strategies.

## Safety Rules

- Do not execute concurrent stress tests against production systems.
- Do not exploit discovered race conditions beyond proof-of-concept documentation.
- Do not modify application state or database records during analysis.
- Do not bypass rate limiters or access controls during testing.

## Output

Return evidence table with columns: location, race type, severity, reproduction steps, and recommended mitigation.

### 来源：`sources/pro/posture-assessment.md`
SHA-256：`be81c0b831d303a38c5c3f9c65affedf7d7cd103a371f3980fe26635076bca9e`

# Security Posture Assessment

This is a defensive assessment protocol for local or explicitly authorized
assets. Do not assume authorization for a target merely because a route was
selected.

## Assessment chain

1. Surface mapping: document exposed services, endpoints, and interfaces.
2. Control verification: test authentication, authorization, and input
   validation with synthetic identities and bounded requests.
3. Boundary review: inspect trust boundaries and safe failure behavior.
4. Configuration audit: check headers, TLS, defaults, logging, and secrets
   handling without collecting secret values.
5. Evidence collection: preserve reproduction steps and redacted responses.

## Output

Each finding includes description, evidence, confidence, reproduction in the
local fixture, risk level, and remediation. Use `CRITICAL > HIGH > MEDIUM > LOW
> INFO` only when the evidence supports that severity.

### 来源：`sources/pro/database-security.md`
SHA-256：`e09d1796f100637f7c6d303f18dbe28713c41050567700fdf3232a33e658104f`

# Database Security Assessment

## Scope

Use this module only for databases you own or have explicit authorization to assess. Review access controls, encryption configuration, audit logging, and injection surfaces.

## Workflow

1. Enumerate database users, roles, and granted privileges for least-privilege violations.
2. Verify encryption at rest configuration: tablespace encryption, key management, rotation policy.
3. Check encryption in transit: TLS version, certificate validity, cipher suite strength.
4. Review audit logging: enabled events, log retention, tamper protection.
5. Assess application query patterns for injection surfaces: concatenation, ORM bypass, stored procedures.
6. Validate backup security: encryption, access restrictions, integrity verification.

## Safety Rules

- Do not assess databases you do not own or have written authorization for.
- Do not read, copy, or exfiltrate actual user data during the assessment.
- Do not modify database schemas, users, or permissions during review.
- Do not attempt SQL injection against production databases.

## Output

Return an evidence table with columns: Database, Control Area, Finding, Severity, Recommendation.

### 来源：`sources/pro/attack-surface.md`
SHA-256：`ed379f6863b1f446dd3e4d1f536fda86202de5704db08eebd3f0dabbce26d84b`

# Attack Surface Mapping

## Scope

Use this module only for authorized/owned systems to enumerate entry points, document trust boundaries, and trace data flows for security assessment.

## Workflow

1. Enumerate all network-facing services, ports, and protocols.
2. Identify API endpoints, webhook receivers, and file upload interfaces.
3. Map trust boundaries between system components and external dependencies.
4. Trace data flows from untrusted inputs through processing to storage.
5. Document authentication requirements at each entry point.
6. Classify entry points by exposure level and historical vulnerability patterns.

## Safety Rules

- Do not perform active scanning against systems not in authorized scope.
- Do not attempt exploitation of discovered entry points during mapping.
- Do not enumerate credentials or access tokens during surface analysis.
- Do not share attack surface documentation outside authorized personnel.

## Output

Return evidence table with columns: entry point, protocol, authentication required, trust boundary, data sensitivity, and exposure classification.

### 来源：`sources/pro/stego-media.md`
SHA-256：`f4de85202c1668d36858923f28185a1ff0303d032b37d10c008b0d5f118da2d8`

# Steganography and Media Analysis

## Scope

Use this module only for authorized forensic investigations to detect hidden data in media files, extract metadata, and analyze carrier characteristics.

## Workflow

1. Collect file metadata: format headers, EXIF/XMP tags, embedded thumbnails.
2. Perform statistical analysis: chi-square, RS analysis, sample pair detection on image carriers.
3. Inspect least-significant-bit planes for non-random patterns.
4. Check for appended or prepended data beyond format boundaries.
5. Analyze audio spectrograms and frequency domain for embedded signals.
6. Document findings with hash values and extraction methodology.

## Safety Rules

- Do not execute embedded payloads or scripts found within media files.
- Do not distribute or share extracted hidden content without authorization.
- Do not modify original evidence files; work only on verified copies.
- Do not assume content legality; escalate suspicious findings immediately.

## Output

Return evidence table with columns: filename, file hash, detection method, hidden data type, extraction offset, and confidence level.

### 来源：`sources/pro/pentest-methodology.md`
SHA-256：`f4ef281f43a5cccbbe581af4f5c1b53f8d32cdb4251eb31c736cf0e9b8a79947`

# Penetration Testing Methodology

## Scope

Use this module only for formally authorized engagements with signed rules of engagement to structure testing phases, evidence collection, and reporting.

## Workflow

1. Verify authorization documentation: scope definition, IP ranges, testing windows.
2. Confirm rules of engagement: excluded systems, emergency contacts, escalation paths.
3. Establish evidence collection framework: screenshots, logs, timestamps, tool output.
4. Execute testing phases: reconnaissance, enumeration, vulnerability identification.
5. Validate findings with minimal-impact proof-of-concept demonstrations.
6. Compile findings into structured report with risk ratings and remediation guidance.

## Safety Rules

- Do not test any system without verified written authorization.
- Do not exceed scope boundaries defined in the engagement agreement.
- Do not perform destructive actions or denial-of-service testing without explicit approval.
- Do not retain client data or credentials beyond the engagement period.

## Output

Return evidence table with columns: finding ID, category, affected asset, severity, proof-of-concept reference, and remediation priority.

### 来源：`sources/pro/cloud-metadata.md`
SHA-256：`feb74da1e2e2833404cdb7f5e3fc02b0cfebd32d957b41588e5db249fce8bf72`

# Cloud Metadata Defense Assessment

## Scope

Use this module only for authorized/owned cloud infrastructure to verify metadata endpoint hardening, IMDSv2 enforcement, and network boundary controls.

## Workflow

1. Identify cloud provider and instance metadata service version in use.
2. Verify IMDSv2 (or equivalent) is enforced with hop limit restrictions.
3. Audit network policies blocking metadata access from application containers.
4. Review IAM role permissions attached to instances for least-privilege compliance.
5. Check for metadata credential caching and rotation configurations.
6. Validate that application-layer SSRF defenses block metadata IP ranges.

## Safety Rules

- Do not retrieve or store live credentials from metadata endpoints.
- Do not modify instance IAM roles or metadata service configurations.
- Do not test metadata access from unauthorized network segments.
- Do not exfiltrate or log temporary security credentials.

## Output

Return evidence table with columns: instance ID, IMDS version, hop limit, IAM role, network policy status, and hardening recommendation.

## 云端资料获取

`module:ID` 表示本技能库的云模块。客户端会在需要时用当前登录会话获取目标模块；不要把模块内容写回源文件。

Windows PowerShell：

Bash：

## 使用前核对

目标与操作范围以用户当前请求为准；核对方法前置条件、工具和附件，按实际执行层级记录结果。正文不表示示例代码已经在本机执行或验证。
