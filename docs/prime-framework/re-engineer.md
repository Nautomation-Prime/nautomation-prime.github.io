---
title: Re-engineer
description: Stage 2 of the PRIME Framework - optimising processes and designing scalable architecture before automation begins.
tags:
  - PRIME Framework
  - Re-engineer
  - Process Design
  - Architecture
---

## Re-engineer Workflows

## Stage 2 of the PRIME Framework

> **"Don't automate broken processes. The Re-engineer stage ensures we're building the *right* automation, not just making bad workflows faster."**

!!! success "Stage Outcome"
    **Deliverable:** Technical architecture documents, workflow diagrams, and design decision records with safety mechanisms planned.

    **Typical Result:** Workflows redesigned to eliminate 30-50% of manual steps, built for parallel execution and scalability before coding begins.

        ```mermaid
        graph TD
        A[Current Workflow] -->|Analyse| B[Identify Issues]
        B -->|Redesign| C[Prime Workflows]
        C -->|Architect| D[Technical Design]
        D -->|Validate| E[Safety Mechanisms]
        
        style A fill:#999
        style B fill:#7B68EE
        style C fill:#8A7AEE
        style D fill:#998CEE
        style E fill:#A89EEE
        ```

**Prime Terminology Used:** Prime Workflows design, Prime Agents architecture planning

---

## 🎯 Objective

Design optimised, scalable workflows and architecture **before** writing code. This stage prevents the costly mistake of automating inefficient processes.

---

## 🚫 The Automation Trap

The most common (and expensive) mistake in automation:

        ```text
        Current Manual Workflow (inefficient)
                ↓ automate directly
        Automated Workflow (still inefficient, now faster!)
        ```

**Example:**  
Manually adding VLANs requires logging into 5 switches individually, copying configs, pasting with modifications, saving.

**Bad Automation:** Script that mimics these exact steps  
**Good Re-engineering:** Template-based bulk provisioning with validation

!!! info "Why Re-engineering Comes Before Implementation"
    If you skip this stage and jump straight to coding, you'll automate your current inefficiencies. You'll get a faster version of a bad process. Then you're locked into that design.

    This stage is where you solve the problem *permanently*—by redesigning the workflow *before* automating it. It costs more upfront, but saves infinitely more in the long run.

---

## ✅ What Happens During Re-engineer

### 1. Process Analysis

For each prioritised automation from the [Pinpoint](./pinpoint.md) stage, we map the current workflow:

#### Current State Mapping

### Example: VLAN Provisioning (Current Process)

        ```text
        1. Receive change ticket
        2. Identify target switches from site documentation
        3. SSH to each switch individually
        4. Copy running-config for backup (manual paste to notepad)
        5. Enter config mode
        6. Add VLAN commands (typing by hand)
        7. Save config
        8. Repeat steps 3-7 for remaining switches
        9. Update change ticket
        ```

**Identified Issues:**

- ❌ No validation before applying config
- ❌ No rollback mechanism if VLAN ID conflicts
- ❌ Manual typing introduces errors
- ❌ No verification VLAN was actually created
- ❌ Sequential execution (slow for many switches)
- ❌ No audit trail beyond ticket notes

---

### 2. Workflow Redesign

We design an optimised process that addresses identified issues:

#### Future State Design

### Example: VLAN Provisioning (Re-engineered)

        ```text
        1. Receive change ticket (parsed for VLAN details)
        2. Validate VLAN ID doesn't conflict
        3. Generate config from template (Jinja2)
        4. Identify target switches from inventory (CSV/Netbox)
        5. Pre-flight checks:
        - Verify device reachability
        - Check VLAN ID availability
        - Validate trunk port capacity
        6. Apply config to all switches (parallel execution)
        7. Post-flight validation:
        - Verify VLAN in show vlan
        - Check STP state
        8. Generate completion report (with before/after snapshots)
        9. Auto-update ticket with results
        ```

**Improvements:**

- ✅ Template-based (zero typing errors)
- ✅ Pre-flight validation (catch conflicts before change)
- ✅ Parallel execution (10x faster)
- ✅ Post-flight verification (proves success)
- ✅ Automatic rollback on failure
- ✅ Comprehensive audit trail

---

### 3. Safety Mechanism Design

Production networks require bulletproof safety:

#### Pre-Flight Checks

Before making any changes, automation should verify:

**Connectivity:**

- Device reachable via ICMP
- SSH port accessible
- Authentication successful
- Sufficient privilege level

**State Validation:**

- Device not in maintenance mode
- No active config sessions (prevent collision)
- Sufficient CPU/memory headroom
- Required feature sets enabled

**Change Validation:**

- Configuration doesn't conflict with existing state
- Required parameters present and valid
- Change scope matches authorisation
- Dry-run simulation successful

#### Rollback Capability

Every automation should include:

- **Checkpoint save before changes**
- **Atomic operations** (all-or-nothing for multi-device)
- **Automatic rollback on failure**
- **Manual rollback procedure documented**

---

### 4. Architecture Planning

For each automation, we design the technical architecture:

#### Data Flow

        ```text
        [User Input] → [Validation Layer] → [Inventory Source]
                        ↓
                [Template Engine]
                        ↓
        [Pre-Flight Checks] → [Device Connection Pool]
                        ↓
                [Parallel Execution]
                        ↓
        [Post-Flight Validation] → [Reporting Engine]
                        ↓
                [Audit Log] + [Ticket Update]
        ```

#### Component Selection

| Requirement | Technology Choice | Rationale |
| :--- | :--- | :--- |
| Device connection | Netmiko | Broad platform support, reliable |
| Templating | Jinja2 | Industry standard, powerful |
| Inventory | CSV → Netbox (future) | Start simple, path to scale |
| Parallel execution | Threading | Good enough for <100 devices |
| Validation | TextFSM | Structured data from show commands |
| Logging | Python logging module | Structured, rotatable logs |

#### Scalability Planning

**Current Scale:** 50 devices  
**12-Month Scale:** 150 devices  
**24-Month Scale:** 300+ devices

**Design Decisions:**

- Threading sufficient now, document async migration path
- CSV inventory works now, plan Netbox integration at 100+ devices
- Local execution acceptable now, consider container deployment at scale

---

### 5. Integration Design

Automation rarely exists in isolation. We design integrations with:

#### External Systems

**Network Management:**

- **DNS** — Validate hostnames, update records if automation creates interfaces
- **IPAM** — Reserve IPs, prevent conflicts
- **Monitoring** — Trigger config refresh after changes
- **Netbox/CMDB** — Source of truth for inventory

**Business Systems:**

- **Ticketing** — Auto-update status, attach reports
- **Workflow Systems** — Approval gates for high-risk changes
- **Notification** — Email, Slack, Teams alerts

**Security Systems:**

- **Credential Vaults** — HashiCorp Vault, CyberArk
- **Logging** — Syslog, SIEM integration
- **Audit Systems** — Compliance reporting

---

### 6. Error Handling Strategy

We design comprehensive error handling:

#### Failure Modes

| Failure Type | Detection | Response |
| :--- | :--- | :--- |
| Device unreachable | Pre-flight ICMP check | Skip device, log, continue |
| Authentication failure | SSH connection attempt | Alert, halt (credential issue) |
| Config syntax error | Commit check | Rollback, alert |
| Post-validation fail | Show command parsing | Rollback, detailed logging |
| Partial multi-device failure | Per-device validation | Complete successful, report failed |

#### Logging Strategy

- **INFO:** Normal operations, successful executions
- **WARNING:** Recoverable issues, devices skipped
- **ERROR:** Failures requiring attention
- **CRITICAL:** System-wide failures, safety mechanism triggers

---

## 📊 Deliverable: Technical Design Documents

At the end of the Re-engineer stage, you receive:

### 1. Process Flow Diagrams

Visual representation of optimised workflows with:

- Current state vs. future state comparison
- Decision points and conditional logic
- Error handling paths
- User interactions points

### 2. Technical Architecture Documents

**For each automation:**

- Component architecture diagram
- Data flow mapping
- Technology stack justification
- Integration touchpoints
- Scalability roadmap

### 3. Safety & Validation Plans

- Pre-flight check specifications
- Post-flight validation criteria
- Rollback procedures
- Testing strategy (lab/staging approach)

### 4. Implementation Blueprints

Detailed specifications for the Implement stage:

- Required Python libraries
- Configuration file structures
- Logging format standards
- Error message conventions
- CLI argument specifications

---

## 💡 Why Re-engineer Matters

### Returns Compound Over Time

A well-designed workflow becomes the template for future automations:

- **First automation:** 4 weeks to design + implement
- **Second automation:** 2 weeks (reuse patterns)
- **Fifth automation:** 1 week (mostly template customization)

### Prevents Expensive Rewrites

Skipping Re-engineer leads to:

- ❌ Hard-coded values throughout code
- ❌ No validation (issues discovered in production)
- ❌ Can't handle edge cases (brittle)
- ❌ Doesn't scale (rewrite needed at 50 → 200 devices)

With Re-engineer:

- ✅ Template-driven (easy to modify)
- ✅ Comprehensive validation (catches issues early)
- ✅ Handles edge cases gracefully
- ✅ Scales to 10x without major changes

---

## 🚀 What Happens Next

After Re-engineer, proceed to [Stage 3: Implement](./implement.md) where designs become production-ready code.

The implementation team (whether internal or Nautomation Prime) now has:

- Clear requirements
- Proven design patterns
- Safety guardrails defined
- Success criteria established

This dramatically accelerates development and ensures quality.

---

## 📋 Re-engineer Checklist

Before moving to Implement stage:

- [ ] Current workflow documented with pain points identified
- [ ] Future state workflow designed with safety mechanisms
- [ ] Architecture reviewed and technology choices justified
- [ ] Integration requirements identified and documented
- [ ] Error handling strategy defined
- [ ] Validation criteria established (what "success" looks like)
- [ ] Scalability plan documented (today + 12/24 months)
- [ ] Design review completed with stakeholders
- [ ] Lab/test environment requirements confirmed

---

## 💼 Engagement Options

### Re-engineer as Part of Full PRIME Engagement

Included as Stage 2 when you engage for the complete framework. Typically 1-2 weeks duration per automation project.

### Standalone Re-engineer Service

Sometimes clients have identified their automations but need design help:

**Fixed Fee:** £3,000 - £6,000 per automation (depending on complexity)

**Includes:**

- Current state workflow analysis
- Future state process design
- Technical architecture documents
- Safety & validation planning
- Implementation blueprints

**Perfect for:** Internal teams with Python skills but need architecture guidance

---

## 🎓 Learn More

- **[PRIME Framework Overview](./index.md)** — See how all five stages work together
- **[Previous Stage: Pinpoint](./pinpoint.md)** — How we identified this automation
- **[Next Stage: Implement](./implement.md)** — Building production-ready code
- **[Request Discovery Call](../contact.md)** — Discuss your automation needs

---

> **Mission:** To empower network engineers through the **[PRIME Framework](./index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](./philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.

---

[← Previous: Pinpoint](./pinpoint.md) | [Back to PRIME Framework](./index.md) | [Next: Implement →](./implement.md)
