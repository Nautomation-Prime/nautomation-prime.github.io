---
title: Start Here
description: New to Nautomation Prime? Five pages, in order, that take you from your first Netmiko script to a production-grade deployment pipeline.
tags:
  - Start Here
  - Learning Path
  - Academy
---

<div class="np-hero" markdown>

<p class="np-eyebrow">Your first visit? Read these five pages, in this order.</p>

## Start here

This site has a lot of pages. You don't need most of them yet. If you are a network engineer who knows a little Python and wants to automate Cisco devices properly, work through these five in order. Each one assumes you've done the one before it.

</div>

!!! info "Before you start"
    These pages teach you to apply Python to network automation, not Python itself. You should already be comfortable with variables, functions, loops, conditionals, exceptions and basic file I/O. If you're new to Python, complete a fundamentals course first (Real Python, Codecademy or similar), then come back.

    You'll also need **Python 3.10 or later**, SSH access to some Cisco devices (physical or virtual, such as CML, EVE-NG or GNS3), and credentials to log in to them.

---

### 1. [Your first script: show command to Excel](foundation/tutorials/beginner/netmiko-show-command-to-excel.md)

Connect to a single Cisco device with Netmiko, run a show command, and turn the output into something you can hand to someone else. Every line is explained.

### 2. [Back up every device's config](foundation/tutorials/beginner/multi-device-config-backup.md)

The same idea, across many devices at once: the first script most teams actually need, and the first one where things go wrong at scale.

### 3. [Intermediate tutorials](foundation/tutorials/intermediate/index.md)

YAML intent, validation, Jinja2 templates, Nornir, PyATS, logging and rollback, one technique per page. Work through the data and Nornir sections before moving on.

### 4. [Build netpipe: the Capstone](foundation/tutorials/capstone/index.md)

Seven chapters, one repository. You combine everything from step 3 into a deployment pipeline that validates, renders, deploys, proves and rolls back a real change. This is where it stops being a set of techniques and becomes a system.

### 5. [Production-Grade Principles](foundation/production-grade-network-automation-principles/index.md)

Why the pipeline you just built is shaped the way it is: pre-flight checks, blast radius, idempotency, rollback, audit. It reads differently once you've built the thing it describes.

---

That's it. When you've finished, the rest of the site is organised into three tracks: [Learn](academy/learn/index.md), [Govern](academy/govern/index.md) and [See it done](academy/see-it-done/index.md).
