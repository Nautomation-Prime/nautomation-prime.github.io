---
title: Designing the Tool Catalogue
description: The eight classes of tool a governed agent needs, the four execution patterns behind them, and how a tool moves from draft to retired without anyone losing track of what is enabled.
tags:
  - Governed AI
  - Tool Design
  - MCP
  - Architecture
  - Enterprise
---

## Designing the Tool Catalogue

One tool is a refactor. Twenty tools is an architecture, and it is the point at which most governed-agent projects quietly lose control of their own surface area.

The failure is gradual and it looks reasonable at every step. Someone needs interface counters, so a tool is added. Someone needs them filtered, so a parameter is added. Someone needs a different platform, so an optional field appears. Six months later there is a tool with eleven optional parameters that can reach most of the estate, and nobody can say what it is permitted to do without reading the implementation.

A catalogue prevents that, and it does it by deciding **what kinds of tool exist** before deciding which ones you need.

---

## The Eight Classes

Every tool worth building falls into one of eight classes. The class determines what controls the tool carries, which means classification is a design decision, not documentation written afterwards.

| Class | What it does | Example names | The control that defines it |
|---|---|---|---|
| **Discovery** | Finds things in the source of truth | `find_devices`, `find_sites` | Results come from an authoritative source, filtered to the caller's scope |
| **State** | Reads current operational state | `get_device_health`, `get_interface_status` | Read-only, scoped, source and timestamp returned |
| **Diagnostics** | Runs a bounded, non-configuring operation | `run_diagnostic` | Takes a **diagnostic identifier**, never command text |
| **Compliance** | Evaluates state against a baseline | `check_compliance`, `compare_configuration` | Deterministic policy evaluation, structured findings |
| **Proposal** | Builds a change artifact without applying it | `create_remediation_pack` | Immutable output, no execution path |
| **Approval** | Validates and submits a proposal for authorisation | `validate_remediation_pack`, `submit_for_approval` | Checks syntax, scope, ticket, approver, expiry |
| **Execution** | Applies an approved artifact | `apply_approved_remediation` | Requires unmodified approval, checksum, scope, and window |
| **Verification** | Confirms the result, or reverses it | `verify_change`, `rollback_change` | Verification mandatory; rollback limited to predefined recovery |

Two things fall out of this table that are easy to miss.

**The classes are ordered.** Discovery through verification is the sequence a change actually follows. A catalogue with proposal tools but no approval or verification tools has built the interesting half of a change pipeline and skipped the half that makes it safe.

**Each class has exactly one job.** The reason `create_remediation_pack` and `apply_approved_remediation` are separate tools — rather than one tool with an `apply: bool` parameter — is that separating them makes proposal and execution separately authorisable. A boolean flag is not an authorisation boundary. Two tools are.

!!! danger "The parameter that becomes a privilege escalation"
    Any optional parameter that widens what a tool can do is a control boundary hiding in a schema. `dry_run: false`, `force: true`, `scope: "all"`, `platform_override` — each of these turns one tool into two, without the second one ever being approved. If a parameter changes the class of the tool, it should have been a different tool.

---

## The Four Execution Patterns

Underneath the eight classes there are only four sequences. Every tool implements one of them, and a tool that does not fit one is worth a second look.

### Read

> Validate input → authenticate → resolve target → verify identity → authorise → read → normalise → redact → audit → return

Used by discovery, state, diagnostics, and compliance tools. Note how much happens before the read: five steps of validation for an operation that changes nothing. That is not excessive. A read tool that returns the wrong device's configuration to the wrong person is a data incident, and it is the most likely incident a governed agent will actually have.

### Proposal

> Resolve → read current state → evaluate policy → build immutable artifact → return **without executing**

The output is an artifact, not advice. That distinction is the whole point of the class: a proposal you can approve is one you can also checksum, expire, and compare against what actually ran.

### Change

> Revalidate identity, scope, current state, approval, window, and checksum → execute once → verify → audit

Every one of those revalidations happened already, at proposal or approval time. They happen again because time has passed. The device may have changed, the approval may have expired, the scope may have been narrowed, and the artifact may have been edited. Revalidation at execution is what makes the earlier approval meaningful.

**Execute once** is doing work in that sentence too. A change tool that retries on an ambiguous failure may apply the change twice. Retry belongs to the caller, after verification has established what actually happened.

### Rollback

> Invoke only a predefined recovery associated with this change context

Rollback is not a free-form capability and it is not "run the opposite change". It is a specific, pre-authored recovery path attached to a specific change. An agent that can compose a rollback is an agent with a change tool, whatever it is called.

---

## Sizing a Tool

The recurring design question is how much a single tool should do. Three tests, in order:

1. **Can you name it `verb_noun` without a conjunction?** `get_interface_status` is one tool. `get_or_reset_interface` is two, and the name is telling you so.
2. **Does every parameter change *what it is asked about*, rather than *what it does*?** Target, scope, and filter parameters are fine. Mode, action, and behaviour parameters are a second tool.
3. **Would you authorise all of it to the same population?** If some callers should have part of this tool and not the rest, it is already two tools; the only question is whether you split it now or after the access review.

Erring towards more, narrower tools costs a little duplication in the catalogue and buys authorisation granularity you cannot retrofit. Erring the other way produces the eleven-optional-parameter tool.

---

## Tool Lifecycle

A catalogue is only trustworthy if enablement is a state, not a memory. Six states, and the transitions between them are where the governance actually lives.

| State | Meaning | What must exist to enter it |
|---|---|---|
| **Draft** | Being designed | Purpose, class, provisional schema, named owner, provisional risk class |
| **Review** | Under assessment | Architecture, security, operational, and test review scheduled or complete |
| **Approved** | Cleared, not yet live | Roles and scopes recorded, dependencies documented, evidence retained |
| **Enabled** | Callable | Published to a specific, approved client and audience — not to everyone with access |
| **Deprecated** | Replaced, still callable | Replacement named, migration guidance published, removal date set |
| **Retired** | Not callable | Invocation disabled, access revoked, evidence archived |

Three rules make this work in practice:

- **Approved and enabled are different states.** A tool can be approved for one audience and not another. Collapsing these two is how a tool approved for a lab pilot ends up in the production agent.
- **Deprecation is announced before removal, with a date.** Silent removal breaks callers; silent retention leaves an unowned capability enabled.
- **Retirement revokes access, it does not just hide the tool.** A tool removed from a catalogue but still reachable by its endpoint has been hidden, not retired.

This is [NP-TOOL-08](../standards/control-catalogue.md#np-tool-tool-boundary).

---

## Reviewing the Catalogue as a Whole

Individual tool reviews miss catalogue-level problems. Periodically, ask:

- **What is the widest thing an agent can do?** Take the enabled set for one role and describe the most impactful sequence it permits. That is your real risk class, not the highest class of any single tool.
- **Which tools have never been called?** Unused tools are surface area with no benefit. Retire them.
- **Which tools have grown parameters since approval?** Schema widening is the most common undocumented escalation, and it never looks like one at the time.
- **Do proposal, approval, and execution map to different roles?** If one identity holds all three, the segregation of duties exists in the diagram and not in the system.
- **Is anything enabled that no longer has a named owner?** That is an orphan, and it gets disabled until someone claims it.

---

## Where This Leaves You

The catalogue defines *what capabilities exist* and *who may call them*. It does not yet define what a call looks like going in, what comes back, or what happens when it fails — and those are where a well-designed catalogue can still produce an agent that misleads its users.

That is the next page.

---

## Continue the Series

- Series Index: [Governed AI for Network Operations](./index.md)
- Previous: [From Script to Tool](./from-script-to-tool.md)
- Next: [Tool Contracts and Failure Modes](./tool-contracts-and-failure-modes.md)
- Controls: [NP-TOOL-01, NP-TOOL-02, NP-TOOL-08](../standards/control-catalogue.md#np-tool-tool-boundary)
