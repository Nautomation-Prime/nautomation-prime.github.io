---
title: Scoping Automation to Reduce Blast Radius
description: Constrain automation by site, role, domain, and batch to reduce failure impact and improve change safety.
tags:
  - Production Principles
  - Blast Radius
  - Deployment Strategy
  - Canary
  - Network Automation
---

## Why Scope Is a Safety Feature

Even high-quality automation can fail in surprising ways. Scope controls determine whether failure is contained or widespread.

A robust scoping model turns one potential enterprise outage into a manageable localised issue.

---

## Scoping Dimensions

Apply multiple dimensions together:

- Site scope: specific campuses, DCs, or regions
- Role scope: access, distribution, core, WAN edge
- Topology scope: failure domain boundaries
- Population scope: percentage or fixed batch count
- Time scope: maintenance windows and freeze periods

---

## Staged Rollout Pattern

Recommended rollout sequence:

1. Lab and replay test
2. Canary set (1-3 representative devices)
3. Small batch (5-10 percent)
4. Incremental expansion with hold points
5. Full rollout after success criteria are met

Define objective promotion criteria between stages.

---

## Batch Safety Controls

Every batch should include:

- Maximum device count cap
- Abort threshold (for example 2 critical failures)
- Manual confirmation between phases
- Cooldown period for signal observation

This limits cascading failures under uncertain conditions.

---

## Production Checklist

- Rollout starts with canary targets
- Scope is explicit and immutable during execution
- Batch limits are enforced by code, not operator memory
- Abort thresholds are predefined and tested
- Post-batch health signals are reviewed before expansion

---

## Anti-Patterns

- One-click fleet-wide rollout for first execution
- Dynamic target expansion during a live run
- No distinction between roles or topology domains
- Ignoring asymmetric risk across device classes

---

## Key Takeaway

Scoping is not just operational convenience. It is a primary control that decides the size of your worst-case outcome.

<div class="np-reflection" markdown>
<p class="np-reflection-label">Between the Lines</p>
<p>Kipling admired the nerve to "make one heap of all your winnings / And risk it on one turn of pitch-and-toss" — and then, pointedly, to start again at the beginning and never breathe a word about the loss.</p>
<p>It is a fine thing to read and a poor way to run a change window. Scope exists so that a bad night costs one site rather than the estate, and so that whoever ran it still gets their weekend.</p>
</div>

---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 5 - Real-World Idempotency in Network Automation](./real-world-idempotency-in-network-automation.md)
- Next: [Part 7 - Designing Automation That Can Safely Fail](./designing-automation-that-can-safely-fail.md)
