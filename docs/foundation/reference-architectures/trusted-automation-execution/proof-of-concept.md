---
title: Proof of Concept v1
description: The first Trusted Automation Execution proof of concept — deliberately small, built on a trusted runner, a manifest and digest, and a default-deny local policy — with its requirements, a thirteen-case test matrix, and an honest account of what it does not prove.
image: assets/social/trusted-automation-execution.png
image_alt: "Trusted Automation Execution: a reference architecture from the Nautomation Prime Academy"
tags:
  - Reference Architecture
  - Zero Trust
  - Security
  - Python
  - Testing
---

## Proof of Concept v1

!!! info "A design, not a download"
    This page specifies the proof of concept: what it implements, and what it has to demonstrate before it counts as working. No code or repository is published. The architecture and this specification are the published work, and nothing here should be read as a claim that these tests already pass.

The first proof of concept deliberately does not try to implement the enterprise stack. Its job is narrower and more useful: prove that the [ten invariants](./index.md#ten-invariants) hold, and make the upgrade path to the [full architecture](./architecture.md) visible.

It targets the [Foundation profile](./adoption-profiles.md#profile-a-foundation), and any build of it should say so every time it is demonstrated. The proof of concept shows how to prove the idea. The reference architecture describes where the idea can ultimately go.

The repository layout below assumes Python, because this site does. Nothing in the model depends on that. The same decision belongs in front of a PowerShell script, an Ansible playbook, or a Terraform apply.

!!! warning "A hash and a YAML file are not High-Assurance"
    The PoC uses a SHA-256 digest to demonstrate integrity checking. A digest proves that a file matches an expected value. It does not prove who published the file or how it was built; that needs signing and verified provenance. The PoC demonstrates the *shape* of the decision, not the strength of the target state.

---

## Repository Layout

```text
trusted-automation-execution/
├── runner/
│   └── trusted_runner.py
├── policy/
│   └── policy.yaml
├── trust/
│   ├── workload-manifest.json
│   └── approved-digests.json
├── workloads/
│   ├── approved_read_only.py
│   └── lab_change.py
├── validation/
│   └── validate_outcome.py
├── evidence/
│   └── execution_records/
├── config/
│   └── targets.yaml
├── tests/
│   ├── test_integrity.py
│   ├── test_policy.py
│   ├── test_scope.py
│   └── test_runner.py
└── README.md
```

The layout is the architecture in miniature. `runner/` is the enforcement point. `policy/` and `trust/` are the decision inputs, and they sit outside `workloads/` because nothing a workload can write should be something the runner trusts. Separate directories are where that starts; file permissions on the runner host are where it is enforced. `validation/` is separate from `workloads/` for the reason the architecture gives in [Validate the resulting state independently](./architecture.md#8-validate-the-resulting-state-independently): the code that makes a change does not grade it.

---

## Requirements

1. **The runner is the only entry point.** A workload cannot invoke itself through the privileged path.
2. **Each workload has a manifest** stating its name, version, risk class, allowed capabilities, and intended platform.
3. **SHA-256 verifies the artefact** against protected expected state. The documentation says plainly that this is an integrity demonstration, not publisher or provenance assurance.
4. **Policy is declarative,** version-controlled, protected from the workload, and default-deny.
5. **Targets are allow-listed** and classified, at minimum, as lab or non-lab.
6. **The runner's network access is restricted** to the allow-listed targets and the services it needs, so a policy error cannot reach anything else.
7. **Secrets are unavailable to the workload** until the runner has an allow decision.
8. **Lab targets or a simulation mode by default.** Nothing in the PoC can reach production without a deliberate change.
9. **Execution evidence** records a Job ID for the run, requester and context, workload, version and digest, policy result and reason, operation, targets, and outcome, and contains no secrets.
10. **Independent post-run validation** produces a result distinct from the workload's exit status, and every run ends in an explicit terminal state.
11. **Automated tests exercise both permitted and prohibited paths.**

The last is the one that turns the PoC from a demo into evidence. A boundary that has only ever been shown allowing things has not been shown to be a boundary.

### v1, module by module

In terms of the [module catalogue](./architecture.md#the-module-catalogue), v1 implements every core module at Foundation strength: the runner's single entry point (1), the manifest as the canonical request (3), the digest (6), the runner and its local policy as the trust gateway (7), the runner host (9), the host firewall (12), the workload's own connection code as its adapter (14), lab targets (15), the validator (16), an explicit terminal state for every run (17), and the evidence record (18).

Of the conditional modules, it attributes the requester through the operating-system account that invoked the runner (2), checks for approval on high-risk requests (5), and retrieves its secret only after an allow (11). It has no dedicated workload identity (10); that is one of the gaps listed below. It omits all three optional modules — a separate source of truth (an allow-list stands in), orchestration, and device AAA — and says so.

---

## Illustrative Manifest

```json
{
  "name": "iosxe-compliance-audit",
  "version": "1.0.0",
  "risk_class": "R1",
  "runtime": "python",
  "publisher": "nautomation-prime-poc",
  "platforms": ["cisco-iosxe"],
  "capabilities": ["read-operational-state"],
  "validation_profile": "audit-read-only"
}
```

`risk_class` uses the site's [automation risk classes](../../production-grade-network-automation-principles/enterprise-control-matrix.md#automation-risk-classification). A compliance audit analyses state and reports findings without changing anything, which makes it R1 — Advisory.

`capabilities` is what the workload declares it needs. A valid, verified workload asking for a capability outside that list is denied. That is the *identity is not capability* invariant, made testable.

---

## Illustrative Policy

```yaml
workload: iosxe-compliance-audit
allowed:
  environments: [lab]
  operations: [read-operational-state]
  platforms: [cisco-iosxe]
require:
  integrity_verified: true
  known_workload: true
  audit_logging: true
  target_allowlisted: true
on_missing_evidence: deny
```

`on_missing_evidence: deny` carries the design. Every `require` entry is a fact the runner has to establish. When it cannot — the digest file is unreadable, the audit sink does not answer — this line decides what happens. It decides in advance, in a reviewed file, rather than leaving it to whatever the code happens to do with an exception.

---

## Demonstration and Test Matrix

Thirteen cases. The first proves the controls do not simply block everything. The other twelve prove they block the right things.

| Test | Expected decision | What it proves |
|---|---|---|
| Approved read-only workload against a lab target | **ALLOW** | The controls do not merely block everything |
| One byte or line changed in the workload | **DENY**, before privilege | The integrity gate works |
| Workload replaced with an unknown file of the same name | **DENY** | A filename or path is not identity |
| Valid workload requests a configuration capability | **DENY** | Identity is not capability |
| Valid workload targets an unauthorised device | **DENY** | Scope is evaluated |
| Workload connects directly to an address outside the allow-list | **BLOCKED** by the network boundary | Policy is not the only scope control |
| Required evidence missing | **DENY** | The design fails closed |
| Policy file malformed or unavailable | **DENY** | A policy failure does not become an allow |
| Credential backend unavailable | **FAIL SAFE**, no execution | There is no fallback to embedded standing secrets |
| Execution succeeds but the validator finds the wrong state | **EXECUTED / VALIDATION FAIL** | Authorisation, process exit, and operational outcome are separate results |
| Audit sink unavailable | Policy-defined; **DENY** in the PoC, where audit is mandatory | Evidence requirements can be enforced, not just requested |
| Revoked workload or version | **DENY** | Trust can be withdrawn |
| High-risk request without approval | **DENY** | The risk-class control path works |

Write each case as an automated test in `tests/`, not as a step in a manual demo script.

The validation-fail case is the one most worth showing a sceptical audience: a run the process reports as a success, and the evidence record reports as a failure. That is the gap between *it ran* and *it worked*, made visible. The capstone's [Proving the Change with PyATS](../../tutorials/capstone/06-proving-the-change-with-pyats.md) chapter builds the same moment from the other direction.

---

## What the PoC Does Not Prove

Being specific about this is what makes the PoC credible.

- **Publisher trust.** A digest matches content against a stored value, so anyone who can write to the stored value can approve their own code. Signing closes that gap. The PoC does not.
- **Provenance.** Nothing verifies how the artefact was built.
- **Workload identity.** The manifest *names* the workload. It does not cryptographically identify it.
- **Runner integrity.** The runner is trusted because it is the runner. A compromised runner host defeats every check it performs.
- **Just-in-time privilege.** Retrieving a stored secret after the allow decision is the right order of operations, but the secret still exists before the run and after it.
- **Tamper resistance.** A local record with a protected copy is far better than nothing. It is not evidence the workload cannot reach.

Each of these is a named step in the [adoption roadmap](./adoption-profiles.md#adoption-roadmap). The value of the PoC is that its gaps are visible, and that the trust model does not change as they close. The [Foundation Quick-Start](./foundation-quick-start.md#what-comes-next) names the three upgrades that close the most of them first.

---

## When It Has Succeeded

The PoC will have succeeded when it demonstrates, under automated test and at Foundation-profile strength, the first nine of the [ten things that must be true](./architecture.md#ten-things-that-must-be-true). The tenth — that the architecture can be implemented at lower maturity without redefining its principles — is what the PoC exists to show.

---

## Continue

- Previous: [Worked Example: Azure and Cisco](./worked-example-azure-cisco.md)
- Section index: [Trusted Automation Execution](./index.md)
- Related: [Capstone: Build a Config Deployment Pipeline](../../tutorials/capstone/index.md) — a working pipeline that already implements several of these gates
