---
title: Cisco Compliance Audit Runbook
description: One-page operational runbook for Cisco IOS-XE Compliance Auditor v4.0 including remediation lifecycle workflow.
tags:
  - Deep Dive
  - Runbook
  - Compliance Audit
  - Operations
  - Change Management
---

## Cisco IOS-XE Compliance Audit: One-Page Runbook

This runbook is a compact operational guide for change windows and the v4.0 remediation lifecycle workflow.

!!! info "Version Alignment"
   This runbook reflects **Cisco IOS-XE Compliance Auditor v4.0** (March 2026).

Primary deep dive:

- [Cisco IOS-XE Compliance Audit](./cisco-compliance-audit.md)

---

## Scope

Use this workflow to:

1. Run audits and generate reports
2. Review remediation packs
3. Approve or reject remediation packs with change control metadata
4. Apply one approved pack or all approved packs
5. Re-verify compliance posture after implementation

---

## Pre-Checks (Start Here)

1. Confirm Linux/macOS/WSL execution environment (no native Windows PyATS runtime).
2. Confirm config and inventory paths are correct.
3. Confirm credentials are available (keyring, environment variables, or prompt).
4. Confirm remediation execution policy in YAML if you plan to apply changes.
5. If required, enable ROI settings in `audit_settings.roi`.

---

## Standard Operating Procedure

### 1) Run Baseline Audit

```bash
python -m compliance_audit -c compliance_audit/compliance_config.yaml
```

Expected outcome:

1. HTML/JSON/CSV reports are generated in output directory.
2. Remediation scripts and review packs are generated for failing findings.

### 2) Review Pack Queue

```bash
python -m compliance_audit --remediation-list pending
```

Decision logic:

1. Approve if in scope and operationally safe.
2. Reject if out of policy, risky, or outside change window.

### 3) Approve or Reject Packs

Approve one:

```bash
python -m compliance_audit --remediation-approve <PACK_ID> --approver "john.doe" --ticket-id "CHG0012345"
```

Approve all pending:

```bash
python -m compliance_audit --remediation-approve-all --approver "john.doe" --ticket-id "CHG0012345"
```

Reject one:

```bash
python -m compliance_audit --remediation-reject <PACK_ID> --approver "john.doe" --reason "Out of approved change scope"
```

### 4) Preflight Before Apply (Recommended)

Single pack preflight:

```bash
python -m compliance_audit --remediation-apply <PACK_ID> --apply-dry-run
```

Bulk preflight:

```bash
python -m compliance_audit --remediation-apply-all --apply-dry-run
```

### 5) Apply Approved Packs

Apply one pack:

```bash
python -m compliance_audit --remediation-apply <PACK_ID>
```

Apply all approved packs:

```bash
python -m compliance_audit --remediation-apply-all
```

If high-risk packs are blocked and exception approval exists:

```bash
python -m compliance_audit --remediation-apply <PACK_ID> --allow-high-risk
python -m compliance_audit --remediation-apply-all --allow-high-risk
```

### 6) Post-Apply Verification

```bash
python -m compliance_audit --remediation-list applied
python -m compliance_audit --remediation-list failed
python -m compliance_audit -c compliance_audit/compliance_config.yaml
```

---

## Safety Rules

1. Do not apply remediation outside authorized change windows.
2. Always run `--apply-dry-run` before production apply.
3. Do not approve packs without ticket and risk validation.
4. Treat `--allow-high-risk` as exception-only.
5. Prefer `--remediation-apply-all` only after queue review.

---

## Troubleshooting Quick Table

| Symptom | Likely Cause | Action |
| --- | --- | --- |
| Remediation workflow disabled | `remediation.enabled: false` | Enable `audit_settings.remediation.enabled` |
| Execution disabled | `execution.enabled: false` | Enable `audit_settings.remediation.execution.enabled` |
| Approval expired | TTL elapsed | Re-run audit and approve new pack |
| Checksum mismatch | Script changed after approval | Re-run audit and approve fresh pack |
| High-risk blocked | Policy enforcement active | Use `--allow-high-risk` only with approval |
| Hostname mismatch | Device identity mismatch | Validate inventory and target prompt before apply |

---

## Fast Pass Criteria

All criteria should pass before closure:

1. No critical FAIL findings remain in changed scope.
2. No unexpected score regressions on unaffected devices.
3. Applied packs show successful status (or documented exception).
4. Change evidence package includes baseline and post-change reports.

---

## Daily Operator Checklist

1. Run audit.
2. Review pending queue.
3. Approve or reject with ticket mapping.
4. Run apply preflight dry-run.
5. Apply approved pack(s).
6. Verify applied/failed status.
7. Re-run audit for closure evidence.
