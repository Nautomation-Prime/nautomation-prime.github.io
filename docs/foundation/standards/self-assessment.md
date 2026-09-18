---
title: Assessing Yourself Against These Controls
description: A repeatable method for assessing network automation against the control catalogue — evidence quality tests, outcome definitions, finding severity, and what closure actually requires.
tags:
  - Standards
  - Governance
  - Assessment
  - Audit
  - Enterprise
---

## Assessing Yourself Against These Controls

Publishing a [control catalogue](./control-catalogue.md) raises an obvious question: how do you find out where you actually stand against it?

Most teams answer that with a spreadsheet, a row per control, and a column of red, amber, and green. It takes an afternoon and produces something that looks like an assessment. Six months later nobody can reconstruct why any given cell was amber, the person who filled it in has moved teams, and the whole thing gets redone from scratch.

The difference between that and a real assessment is not rigour or effort. It is **evidence**. A control is not green because somebody believed it was. It is green because something exists that demonstrates it, and that something can be found again by a different person.

---

## The Method

Eight steps. For a single service this is half a day; for a portfolio, budget per service and do them in batches.

1. **Fix the scope.** Which service, which version, which environment, which sites and device roles. An assessment without a scope statement cannot be repeated or compared.
2. **Confirm ownership and risk class.** If the [three owners](../production-grade-network-automation-principles/automation-service-lifecycle.md#three-owners-not-one) are not named, that is your first finding — record it and continue.
3. **Select applicable controls.** Use the [applicability map](./control-catalogue.md#applicability-by-risk-class) as a starting point, then decide each control deliberately.
4. **Record applicability rationale** for anything you mark not applicable. This is the step teams skip, and it is the one an auditor goes to first.
5. **Collect and test evidence** against the six criteria below.
6. **Assign an outcome** to each applicable control.
7. **Raise findings with severity**, an owner, and a target date.
8. **Get an accountable approval** of the result, including the residual risk being accepted.

!!! tip "Assess the service, not the team"
    An assessment that reads as a verdict on people produces defensive evidence and hidden gaps. The subject is the service. The useful question is *what would someone need to see to believe this control is working*, not *did you do your job*.

---

## Evidence Quality

Before an outcome can be assigned, the evidence has to survive six tests. Most disputed assessments come down to evidence that passes four of these and fails two.

| Criterion | The test |
|---|---|
| **Relevant** | Does it demonstrate *this* control for *this* scope? A pipeline that runs tests proves NP-PLAT-06 for the pipeline, not for a service deployed by hand around it |
| **Current** | Is it recent enough for the decision, and does it match the version in production now? Evidence from a release two versions ago is history, not evidence |
| **Traceable** | Can you tell what system produced it, when, and under whose identity? A screenshot with no context is an assertion with a picture attached |
| **Complete** | Does it show the control *operating*, not just existing? A documented rollback procedure is design intent. A rollback test result is evidence |
| **Protected** | Could it have been altered without anyone noticing? Evidence a team can edit freely is weaker than evidence a system emitted |
| **Repeatable** | Could someone else obtain the same evidence independently, without the original author's help? |

The single most common failure is **Complete**. Design documents, policies, and runbooks describe what is supposed to happen. They are necessary and they are not sufficient. For every control, ask what artifact a *run* produces.

---

## Outcomes

Five outcomes, not three. Red-amber-green collapses two genuinely different situations — a control you have chosen not to apply, and a control you are knowingly running without — into the same colour.

| Outcome | Meaning | What it requires |
|---|---|---|
| **Compliant** | The requirement is met and the evidence survives all six tests | Evidence reference |
| **Partially compliant** | The control is implemented in part, and the gap is understood | Evidence reference, description of the gap, agreed remediation with owner and date |
| **Non-compliant** | The requirement is not met and the risk is unresolved | Finding with severity, remediation plan or an explicit risk decision |
| **Not applicable** | The control genuinely does not apply to this scope | Recorded rationale. "We don't do that" is not a rationale; "the service has no write path, so NP-CHG does not apply" is |
| **Exception** | The control cannot be met and a time-bound waiver is in force | A valid [exception record](../production-grade-network-automation-principles/exception-and-waiver-process.md) with compensating controls and an expiry |

**Exception is not a synonym for non-compliant.** Non-compliant means the risk is sitting there unowned. Exception means someone with authority has looked at it, accepted it, put compensating controls in place, and set a date to revisit. The whole point of separating them is that the first is a problem and the second is a decision.

---

## Finding Severity

Severity describes the risk the gap creates, not how hard it will be to fix. Those get conflated constantly, and it always biases the register towards whatever is cheapest to close.

| Severity | Definition | Required response |
|---|---|---|
| **Critical** | Immediate or material uncontrolled risk — an unbounded write path, exposed credentials, no audit trail on a change service | Escalate now. Block release, or suspend the unsafe capability until resolved |
| **High** | Significant control failure with credible impact | Prioritised remediation with an accountable risk decision while it is open |
| **Medium** | A genuine weakness with limited current exposure | Planned remediation, tracked to closure |
| **Low** | Minor evidence or process weakness | Correct through normal improvement work |
| **Observation** | No failure, but an improvement is available | Optional, tracked if worth doing |

Two rules that keep this honest:

- **Severity is set by the assessor, not negotiated by the service owner.** Disagreement is recorded as a risk decision, not resolved by downgrading the finding.
- **A Critical finding on an R0 service is still Critical.** Risk class decides which controls apply; it does not soften the severity of a control that applies and has failed.

---

## The Assessment Record

One record per assessment. What it must capture, in whatever tool you already use:

- **Scope** — service ID, version, environment, sites and roles, assessment date
- **Context** — owners, risk class, AI risk class where an agent is involved
- **Per control** — identifier, applicability, outcome, evidence reference
- **Findings** — description, severity, affected control, impact
- **Actions** — remediation, named owner, target date
- **Exceptions** — reference, compensating controls, expiry
- **Approval** — assessor, accountable approver, decision, residual risk accepted

The test of the record is not that it is complete. It is whether someone who was not present can pick it up in a year and understand both what was found and what was decided.

---

## Closure

An assessment is complete only when all of the following are true:

- Every applicable control has an outcome
- Every Critical and High finding has an approved disposition — remediated, in progress with a date, or formally accepted
- Every exception cited is valid, in force, and not expired
- Every action has a named owner and a target date
- The accountable approver has recorded the decision and the residual risk being accepted

Anything short of that is a draft. This matters more than it sounds: an assessment left at 90% is routinely cited afterwards as though it were finished, and the 10% that was never closed is exactly where the risk was.

---

## Assessment Cadence

Tie the cadence to risk class, and to events rather than only to the calendar.

| Trigger | Scope of assessment |
|---|---|
| Before production acceptance | Full, all applicable controls |
| Material change — new write capability, wider scope, changed identity model, new AI behaviour | Full reassessment of affected families |
| R3 and R4 services | Full, annually at minimum |
| R0 to R2 services | Full, every two years, or on material change |
| After a serious incident or near miss | Targeted at the controls implicated, plus anything the incident showed to be weaker than believed |
| Exception expiry | Targeted at the waived control |

---

<div class="np-reflection" markdown>
<p class="np-reflection-label">Between the Lines</p>
<p>Seneca ended each day by going back over it — not to punish himself, he was careful to say, but because a fault you can name is one you have already half-addressed. The practice only works if you are willing to look at the bad days rather than the flattering ones.</p>
<p>An assessment that starts with your best-engineered service is the same exercise performed on the wrong evidence. So, usually, is the story we tell ourselves about how the week went.</p>
</div>

## Starting Small

If a full assessment is more than your team can absorb right now, the useful subset is short. In order:

1. **Pick your highest-risk service, not your best one.** The assessment is diagnostic, and a clean result from your best-engineered service tells you nothing you did not know.
2. **Assess NP-CORE and NP-EVD only.** Fourteen controls. If targeting and evidence are sound, most of the rest is recoverable; if they are not, nothing else matters yet.
3. **Record evidence references, not judgements.** A link to a test result is worth more than a green cell, and it is what makes the second assessment cheaper than the first.
4. **Do the second service.** The comparison between two is where the portfolio-level pattern shows up.

Everything else can wait until you have done it twice.

---

## Getting Help With This

The method above is free and complete — you do not need us to run it. If you would rather have the assessment done with you, and the findings written up in a form your security and change governance teams will accept, that is the [Automation Opportunity Assessment](../../smb/packages/automation-assessment.md) for smaller estates, or the individual assessment services on the [Services](../../services.md) page.

---

## Continue

- Previous: [Automation Control Catalogue](./control-catalogue.md)
- Next: [Python Engineering Standard](./python-engineering-standard.md)
- Standards Index: [Automation Standards](./index.md)
- Related: [Exception and Waiver Process](../production-grade-network-automation-principles/exception-and-waiver-process.md) · [Operator Review Worksheet](../production-grade-network-automation-principles/operator-review-worksheet.md)
