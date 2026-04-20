---
title: Cisco Compliance Audit Runbook
description: One-page operational runbook for Cisco IOS-XE Compliance Auditor covering audit, approval, apply, and operator workflows.
tags:
  - Deep Dive
  - Runbook
  - Compliance Audit
  - Operations
  - Change Management
---

## Cisco IOS-XE Compliance Audit: One-Page Runbook

This runbook is a compact operational guide for change windows, routine audits, and the current remediation lifecycle workflow.

!!! info "Version Alignment"
  This runbook reflects the **current main branch state (April 2026)** of Cisco IOS-XE Compliance Auditor.

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
6. Run guided operator workflows without memorising flags

---

## Pre-Checks (Start Here)

1. Confirm config and inventory paths are correct.
2. Confirm credentials are available (keyring, environment variables, or prompt).
3. Confirm remediation execution policy in YAML if you plan to apply changes.
4. If required, enable ROI settings in `audit_settings.roi`.

Example config path:

- `compliance_audit/compliance_config/`

## Optional ROI Setup

If you want reports to show estimated time saved and value saved, enable ROI in config:

```yaml
audit_settings:
  roi:
    enabled: true
    manual_minutes_per_device: 20.0
    manual_minutes_per_check: 0.25
    automation_overhead_minutes_per_device: 2.0
    hourly_rate: 85.0
    currency: "GBP"
```

Interpretation:

- Minutes saved = estimated manual effort minus automated effort
- Value saved = hours saved multiplied by `hourly_rate`

ROI appears in:

- Console summary
- Per-device JSON under `roi`
- Per-device HTML stat cards
- Consolidated HTML summary cards

---

## Common Command Templates

```bash
# Run full audit from the default config directory
python -m compliance_audit

# Run audit with a specific config directory
python -m compliance_audit -c configs/site_alpha

# Run audit for a single device
python -m compliance_audit --device ZZ-LAB1-001ASW001:192.0.2.61

# Surface only high-severity findings
python -m compliance_audit --min-severity high

# Surface only CIS or PCI-tagged findings
python -m compliance_audit --tags cis pci

# Combine severity and tag filters
python -m compliance_audit --min-severity high --tags cis pci

# Launch guided interactive wizard
python -m compliance_audit --interactive

# Launch full-screen TUI
python -m compliance_audit --tui

# Show all CLI options in a table
python -m compliance_audit --list-options

# List remediation packs
python -m compliance_audit --remediation-list

# List only pending remediation packs
python -m compliance_audit --remediation-list pending

# List remediation packs as JSON
python -m compliance_audit --remediation-list all --remediation-output json

# List remediation packs as CSV, sorted by risk, with a limit
python -m compliance_audit --remediation-list all --remediation-output csv --remediation-sort risk --remediation-limit 50

# Approve one pack
python -m compliance_audit --remediation-approve <PACK_ID> --approver "john.doe" --ticket-id "CHG0012345"

# Reject one pack
python -m compliance_audit --remediation-reject <PACK_ID> --approver "john.doe" --reason "Reason text"

# Apply one approved pack
python -m compliance_audit --remediation-apply <PACK_ID>

# Apply all approved packs
python -m compliance_audit --remediation-apply-all
```

---

## Standard Operating Procedure

### 0) Choose Operator Experience

Guided wizard mode:

```bash
python -m compliance_audit --interactive
```

Full-screen terminal UI:

```bash
python -m compliance_audit --tui
```

CLI discovery table:

```bash
python -m compliance_audit --list-options
```

Notes:

- Use `--interactive` when you want prompts and command previews.
- Use `--tui` when you want a full-screen workflow with keyboard navigation.
- Use standard flags for CI, automation, and scripted operations.

### 1) Run Baseline Audit

```bash
# Full audit using the default config directory
python -m compliance_audit

# Audit with optional filters
python -m compliance_audit --min-severity high
python -m compliance_audit --tags cis pci
python -m compliance_audit --categories management_plane
```

Expected outcome:

1. Reports are generated in `output_dir`.
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
python -m compliance_audit --remediation-approve <PACK_ID> \
  --approver "john.doe" \
  --ticket-id "CHG0012345"
```

Approve all pending:

```bash
python -m compliance_audit --remediation-approve-all \
  --approver "john.doe" \
  --ticket-id "CHG0012345"
```

Reject one:

```bash
python -m compliance_audit --remediation-reject <PACK_ID> \
  --approver "john.doe" \
  --reason "Out of approved change scope"
```

Notes:

- Ticket ID is required by default and controlled by `audit_settings.remediation.approval.require_ticket_id`.
- Use `--expires-hours` to override the default approval lifetime.

### 4) Final Review Before Apply

```bash
python -m compliance_audit --remediation-list approved
```

Final checks:

- Confirm the approved pack is still in scope for the current change window.
- Confirm ticket mapping and expiry are still valid.
- Confirm any high-risk exceptions have explicit approval before using `--allow-high-risk`.

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
python -m compliance_audit
```

---

## Safety Rules

1. Do not apply remediation outside authorised change windows.
2. Always review approved pack scope, expiry, and risk before production apply.
3. Do not approve packs without ticket and risk validation.
4. Treat `--allow-high-risk` as exception-only.
5. Prefer `--remediation-apply-all` only after queue review.

---

## Troubleshooting Quick Table

| Symptom | Likely Cause | Action |
| --- | --- | --- |
| Remediation workflow disabled | `remediation.enabled: false` | Enable `audit_settings.remediation.enabled` |
| Execution disabled | `execution.enabled: false` | Enable `audit_settings.remediation.execution.enabled` |
| Approval expired | TTL elapsed | Re-run audit, generate a new pack, and approve again |
| Checksum mismatch | Script changed after approval | Re-run audit and approve fresh pack |
| High-risk blocked | Policy enforcement active | Use `--allow-high-risk` only with approval |
| Hostname mismatch | Device identity mismatch | Validate inventory and target prompt before apply |

---

## Escalation and Rollback

If apply fails or behaviour is unexpected:

1. Stop additional apply actions.
2. Capture pack ID, device, and error output.
3. Check remediation execution logs in `output_dir`.
4. Escalate to network engineering or the change manager.
5. Use your standard network rollback procedure for the affected device or site.

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
4. Review approved pack scope and risk.
5. Apply approved pack(s).
6. Verify applied/failed status.
7. Re-run audit for closure evidence.
