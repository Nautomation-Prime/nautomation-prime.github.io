---
title: Cisco Compliance Audit Runbook
description: One-page operational runbook for Cisco IOS-XE Compliance Audit change windows.
tags:
  - Deep Dive
  - Runbook
  - Compliance Audit
  - Operations
  - Change Management
---

## Cisco IOS-XE Compliance Audit: One-Page Runbook

This runbook is a compact operational checklist for change windows.

Primary deep dive:

- [Cisco IOS-XE Compliance Audit](./cisco-compliance-audit.md)

---

## Scope

Use this workflow when implementing or validating the following control areas:

1. Root guard direction correctness
2. Trunk native VLAN compliance
3. DHCP snooping trust placement
4. Unused-port hardening
5. Remediation script execution and verification

---

## Phase 1: Pre-Change Validation

1. Run baseline audit and save HTML, JSON, and CSV outputs.
2. Confirm trunk direction classification before applying STP guard changes.
3. Verify policy values for native VLAN, parking VLAN, and trust intent in YAML.
4. Flag unknown-direction and unknown-native-VLAN findings for manual review.
5. Generate remediation script and prune to approved change scope.

---

## Phase 2: Controlled Implementation

1. Apply root guard only on validated downlinks.
2. Remove root guard from validated uplinks.
3. Correct native VLAN mismatches on trunk interfaces using policy-defined values.
4. Apply DHCP snooping trust only on policy-approved interfaces.
5. Enforce unused-port hardening as a bundle:
   - shutdown
   - parking VLAN
   - BPDU guard
   - CDP/LLDP restrictions
6. Apply remediation commands in staged order:
   - global commands first
   - interface commands second

---

## Phase 3: Post-Change Verification

1. Re-run audit immediately after implementation.
2. Confirm targeted FAIL and WARN findings moved to PASS.
3. Verify no new failures were introduced in adjacent controls.
4. Review consolidated HTML dashboard for cross-device regressions.
5. Validate per-device score movement and delta summary.

---

## Phase 4: Evidence and Closure

1. Attach before/after reports to the change record.
2. Include generated remediation script and final executed command list.
3. Record approved exceptions directly in policy.
4. Schedule follow-up audit run after normal operations resume.
5. Capture lessons learned and update site policy defaults.

---

## Fast Pass Criteria

All criteria should pass before closing the change:

1. No critical FAIL findings in changed scope.
2. No unexpected score regressions on unaffected devices.
3. Delta report shows resolved findings greater than or equal to new failures.
4. Change evidence package is complete and attached.

---

## Quick Command Patterns

```bash
# Full run
python -m compliance_audit

# Scoped categories
python -m compliance_audit --categories management_plane control_plane data_plane

# Custom output path
python -m compliance_audit -o ./reports/change-window

# CI gate example
python -m compliance_audit --fail-threshold 80
```

---

## Notes

1. If trunk direction is unknown, pause guard changes until topology intent is confirmed.
2. Treat remediation scripts as change artifacts, not blind auto-fix payloads.
3. Prefer dry-run validation for policy changes before production enforcement.
