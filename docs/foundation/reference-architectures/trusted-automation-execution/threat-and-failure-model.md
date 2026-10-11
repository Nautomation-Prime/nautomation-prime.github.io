---
title: Threat and Failure Model
description: What Trusted Automation Execution defends against, the residual risk it leaves behind, how it behaves when its own components fail, and what it explicitly does not claim to solve.
tags:
  - Reference Architecture
  - Zero Trust
  - Security
  - Risk Management
  - Enterprise
---

## Threat and Failure Model

An architecture that lists only what it defends against is a sales document. This page lists three things: what the model is designed to reduce, what it leaves behind when it works, and how it behaves when its own parts fail.

The third list matters most in practice. A trust boundary is only as good as its behaviour on the day the policy service is down.

---

## Threats and Residual Risk

| Threat or failure | Primary controls | What remains |
|---|---|---|
| **Accidental script modification** | Digest and signature verification | If the trust metadata is as easy to modify as the script, protected signing and provenance are needed |
| **Unapproved workload substitution** | Immutable artefact identity, signing, provenance | Compromise of the publisher or the build root of trust remains critical |
| **Credential theft from source** | External secrets, just-in-time authority | Runtime or host compromise can still expose authority while it is in use |
| **Over-privileged workload** | Capability policy, target scope, target-side RBAC | Policy design errors can still grant too much |
| **Compromised long-lived runner** | Ephemeral isolation, minimal standing privilege, attestation | Host, hypervisor, or control-plane compromise is a higher-order risk |
| **Operator targets the wrong device** | Source-of-truth resolution, approvals, pre-flight | Bad authoritative data can still misclassify a target |
| **Automation defect** | Tests, staged rollout, circuit breakers, independent validation, rollback | Some defects only appear in real environments |
| **Build or pipeline compromise** | Controlled build, provenance, protected signing, an enforced verifier | Root-of-trust compromise remains high impact |
| **Log deletion or falsification** | Protected evidence outside the workload's control | Compromise of the evidence platform itself remains possible |
| **AI or agent overreach** | No route around the gateway, capability policy, human approval for risky actions | Agent safety still depends on upstream model and tool governance |
| **Policy service unavailable** | Fail closed for privileged operations, and a designed break-glass route | The availability trade-off has to be engineered deliberately |
| **Malicious but properly approved code** | Review, separation of duties, testing, behaviour limits, validation | Approval cannot prove the absence of malicious intent or a latent vulnerability |

The last row is the honest one. Every control in this architecture verifies that what runs is what was approved. None of them can verify that what was approved was a good idea. Code review, separation of duties, and [independent validation](./architecture.md#7-validate-independently) are there for that, and even together they reduce the risk rather than remove it.

---

## Failure Behaviour

How the boundary behaves when part of it is unavailable, or returns something unexpected.

| Failure | Preferred behaviour |
|---|---|
| **Unknown workload or publisher** | Deny |
| **Integrity or provenance mismatch** | Deny, and alert |
| **Mandatory context unavailable** | Deny |
| **Policy service unavailable** | Deny the privileged operation. Use break-glass only where organisational policy explicitly permits it |
| **Privilege broker unavailable** | Do not fall back to embedded or broad credentials |
| **Pre-flight failed** | Do not begin the write phase |
| **Circuit breaker trips mid-run** | Stop new work, contain scope, preserve evidence, then evaluate rollback or repair |
| **Post-validation fails** | Mark the run unsuccessful and attention-required, even though the process exited zero |
| **Evidence sink unavailable** | For high-risk operations, deny or stop according to policy. Never silently discard required evidence |

Two of these deserve comment.

**The privilege broker fallback** is where good designs quietly fail. Someone adds a fallback "for resilience": if the vault is unreachable, use the credential in the environment file. From that day the vault is optional and the architecture is a suggestion. The fallback is the vulnerability.

**The evidence sink** forces a real decision. Refusing to run because logging is down feels excessive until you consider the alternative, which is a high-risk change with no record of it. For read-only work, buffering locally and forwarding later may be acceptable. For change it usually is not. Decide in advance, write the decision into policy, and test it.

---

## Fail Closed, and What It Costs

Failing closed has a price. Pretending otherwise produces a design that gets bypassed the first time it blocks an emergency.

If the policy service, the identity provider, or the privilege broker is unavailable, privileged automation stops. That is correct for routine work and potentially dangerous during an incident, because the moment you most need automation may be the moment its dependencies are degraded. Two responses, used together:

- **Engineer the dependencies for the availability you need.** If privileged automation is part of incident response, its policy and privilege path are as critical as the systems it repairs.
- **Design the break-glass route before you need it.** A separate protected identity, a stated reason, narrow scope, full logging, and mandatory review afterwards. Exercise it, so that the first time it is used is not the first time it is tried.

What you must not do is resolve the tension by letting failures become allows. [Designing Automation That Can Safely Fail](../../production-grade-network-automation-principles/designing-automation-that-can-safely-fail.md) applies to the boundary as much as to the automation behind it.

---

## Explicit Non-Goals

What this architecture does not claim to do. Each of these is somebody else's control, and a design that assumes otherwise has a gap it cannot see.

- Guarantee that authorised code is free of vulnerabilities or malicious logic
- Replace host, network, application, or secrets-platform security
- Remove the need for software supply-chain security, code review, or dependency controls
- Prove formal compliance with NIST, CISA, or any regulatory framework
- Make arbitrary AI-generated code safe to execute
- Replace change management, operational ownership, or incident response
- Provide a universal rollback mechanism. Rollback is workload- and platform-specific — see [Rollback Strategies](../../production-grade-network-automation-principles/rollback-strategies-what-works-and-what-doesnt.md)
- Guarantee availability when critical policy, identity, or privilege systems fail

The fifth is worth underlining. The architecture verifies that what runs was approved. It does not make unapproved code safe by inspecting it at the gate. AI-generated automation reaches production the way any other code does — reviewed, built, signed, and published — or it does not reach production.

---

## Continue

- Previous: [The Full Reference Architecture](./architecture.md)
- Next: [Adoption Profiles](./adoption-profiles.md)
- Section index: [Trusted Automation Execution](./index.md)
