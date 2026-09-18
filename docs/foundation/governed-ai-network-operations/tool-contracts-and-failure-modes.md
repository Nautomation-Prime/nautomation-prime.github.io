---
title: Tool Contracts and Failure Modes
description: What goes into a governed tool, what comes back, and what happens when it fails — input schemas, the output contract, a nine-category error taxonomy, and the negative tests that prove the boundary holds.
tags:
  - Governed AI
  - Tool Design
  - Testing
  - Error Handling
  - Enterprise
---

## Tool Contracts and Failure Modes

A catalogue of narrow, well-classified tools can still produce an agent that confidently tells an engineer something untrue.

It happens at the edges. The tool returns a partial result and the model presents it as complete. The tool times out and the model reports the device as healthy because nothing said otherwise. The tool rejects an out-of-scope target and the model helpfully tries a neighbouring one. None of these is a failure of the tool boundary as such — the boundary held. They are failures of the **contract**: what the tool promised to return, and what it said when it could not.

This page is about that contract, and about proving it holds.

---

## Input Schemas

The schema is not documentation. It is the enforcement point, and it is the part of the system a model interacts with most directly.

**Requirements:**

- **Strict types.** Every field typed, every type narrow. `str` is not a type for a device identifier.
- **Enumerations rather than free text** for anything that selects behaviour. The set of valid diagnostics, check categories, and platforms is knowable at build time.
- **Length and range limits** on everything that has them, including strings you believe are short.
- **Required fields explicit**, with no defaults that silently widen scope. A `scope` field defaulting to "all" is a trap.
- **Unknown parameters rejected, not ignored.** Ignoring an unrecognised field means a caller can believe it constrained an operation that ran unconstrained.
- **Versioned schemas** with documented compatibility, so a widened schema is a visible event.

The rule that separates a tool schema from an API schema is the last one about free text:

!!! quote "The free-text rule"
    Free text survives only where it **cannot affect behaviour** — a ticket reference, a comment, a change description. The moment a string influences what runs or what it runs against, it becomes an enumeration or a resolved identifier.

Two categories of input deserve separate treatment:

| Input kind | Handling |
|---|---|
| **User-supplied search values** | Accepted as free text, used only to *search*. Never passed downstream as a target |
| **Resolved target identifiers** | Produced by a discovery tool from the source of truth. The only thing an operational tool accepts as a target |

Keeping these distinct in the schema — different field names, different types — is what stops a hostname a model read in a device banner from becoming a connection target.

---

## The Output Contract

Every tool returns the same envelope. Consistency here does more for agent safety than any single field, because it means the model never has to infer the shape of what it got back.

| Field | Why it is mandatory |
|---|---|
| **Status** | Success, partial, or failure — stated, never inferred from the presence of data |
| **Correlation ID** | Ties this invocation to the conversation, the user, and the audit record |
| **Tool name and version** | The same question asked of two versions can legitimately give different answers |
| **Resolved target** | What was *actually* acted on, which may not be what was asked for |
| **Source and timestamp** | Where each fact came from and when it was true |
| **Observed facts** | Structured data, separated from interpretation |
| **Warnings** | Anything degraded, partial, stale, or assumed |
| **Recommendations** | Separate field, clearly not facts |
| **Change indicator** | Explicitly whether anything was altered. On a read tool this is always false, and it is still present |
| **Evidence references** | Pointers to fuller evidence the agent did not need to carry |

Three of these carry more weight than their size suggests.

**Resolved target** is what lets the agent show the engineer which device it actually used. Most wrong-device incidents are visible in the transcript if this field is surfaced, and invisible if it is not.

**The change indicator** sounds redundant on read tools. It is not — it means "did anything change" is answered by the service on every single call, rather than by the model reasoning about which tools it used. That reasoning is exactly the kind you do not want the model doing.

**Warnings** is where partial results go. A tool that collected eight of ten devices must say so explicitly, because a model presented with eight results and no warning will summarise eight as if it were ten.

Redaction happens before the envelope is built. Secrets and unnecessary sensitive configuration should never reach the model in the first place — not because the model will leak them, but because the transcript is now a place they exist.

This is [NP-TOOL-05](../standards/control-catalogue.md#np-tool-tool-boundary).

---

## The Error Taxonomy

"It failed" is not something a caller can reason about. Nine categories, each of which implies a different next action.

| Category | Meaning | Required behaviour |
|---|---|---|
| **`INVALID_INPUT`** | Schema violation or unknown parameter | Reject before any downstream action. Say which field |
| **`UNAUTHENTICATED`** | Identity not established | Return no operational detail at all |
| **`UNAUTHORISED`** | Identity valid, action not permitted | Fail closed, audit the denial, do not hint at what would be permitted |
| **`TARGET_NOT_FOUND`** | Target does not resolve | Do not substitute a near match. Ever |
| **`IDENTITY_MISMATCH`** | Expected, controller, and live identity disagree | Reject any controlled action. Report the discrepancy |
| **`OUT_OF_SCOPE`** | Target resolves but is outside the caller's permitted scope | Reject and audit |
| **`APPROVAL_INVALID`** | Approval missing, expired, modified, or out of window | Reject. Do not offer to proceed without it |
| **`DEPENDENCY_TIMEOUT`** | A downstream system did not answer in time | Bounded failure with structured partial information |
| **`VERIFICATION_FAILED`** | The change ran but the result is not what was intended | Stop further changes. Expose only the approved recovery path |

The two that most change agent behaviour are `TARGET_NOT_FOUND` and `VERIFICATION_FAILED`.

**`TARGET_NOT_FOUND` must not be helpful.** The instinct to return "did you mean `MAN-DC1-SW02`?" is the instinct that puts the model back in the targeting decision. Return the failure; let the engineer disambiguate.

**`VERIFICATION_FAILED` is not a retry condition.** It means the system is in a state nobody designed. The correct response is to stop, not to try again — and the tool contract should make that structurally obvious, by returning recovery options rather than an error the caller might reasonably retry.

`UNAUTHORISED` deserves one note: the denial is audited, which means an agent probing for capability leaves a trail. That is a feature, and it only works if denials are logged as completely as successes ([NP-TOOL-07](../standards/control-catalogue.md#np-tool-tool-boundary)).

---

## The Negative Test Matrix

Positive tests prove a tool works. Negative tests prove the boundary exists. These are the ones that belong in the pipeline, run on every change to a tool or its schema.

| Test | What it proves |
|---|---|
| Valid schema accepted | The contract is usable |
| Invalid schema rejected | Validation runs before anything else |
| Unknown parameter rejected | Extra fields cannot smuggle behaviour |
| Ambiguous target rejected | No silent disambiguation |
| Unknown target rejected | No substitution of a near match |
| Out-of-scope target rejected | Scope is enforced in the service |
| Authentication denial | No operational detail leaks to an unauthenticated caller |
| Role denial | Authorisation is not a role-name check in application code |
| Injection and command-text rejection | Free text cannot reach a device |
| Dependency timeout | Bounded failure, structured partial result |
| Partial failure across targets | Warnings present, count accurate |
| Secret redaction | Credentials do not appear in output, warnings, or errors |
| Audit completeness | Every field present, including on the denial paths |
| Approval expiry | An expired approval is refused |
| Checksum mismatch | A modified artifact is refused |
| Idempotency | A second identical call changes nothing |
| No-change-required | Reported explicitly, not as silence |
| Post-change verification | Cannot be skipped |
| Rollback path | Invokes only the predefined recovery |

Nineteen tests. For a read-only tool roughly half apply, and that half is still the half that matters.

!!! tip "The adversarial pass"
    Run the boundary tests with a model, not just with a test harness. Ask it, in ordinary conversation, to do the things the tools forbid — widen scope, skip an approval, run a command, act on an ambiguous device. You are not testing whether the model complies; you are testing whether your *refusals* are clear enough that it stops rather than finding a creative route. Where it finds one, the finding is about the catalogue, not the model.

---

## What Good Looks Like in a Transcript

The contract only pays off if the agent surfaces it. Four things should be visible to an engineer reading the conversation:

- **Which device was actually used**, by resolved identifier, not by the name they typed
- **When the data was true**, because a five-minute-old reading and a live one lead to different decisions
- **What was not collected**, with the reason
- **Whether anything changed**, stated on every response

An agent that gets all four right is one an engineer can check. That is a lower bar than trustworthy, and it is the correct bar — the goal was never an agent you have to trust.

---

## Continue the Series

- Series Index: [Governed AI for Network Operations](./index.md)
- Previous: [Designing the Tool Catalogue](./tool-catalogue-design.md)
- Next: [Agent Review Checklist](./agent-review-checklist.md)
- Controls: [NP-TOOL-03, NP-TOOL-05, NP-TOOL-06, NP-TOOL-07](../standards/control-catalogue.md#np-tool-tool-boundary)
