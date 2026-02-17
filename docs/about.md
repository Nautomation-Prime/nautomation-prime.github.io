---
title: About Nautomation Prime
description: Learn about Nautomation Prime's mission to provide transparent, production-ready Cisco automation. Education, open-source tools, and professional services.
tags:
  - About
  - Company
  - Contact
---

## Our Story

Nautomation Prime was founded to bridge the gap between complex Cisco infrastructure and accessible Python-driven automation. We believe network engineers deserve transparency in their automation tools—no black boxes, no mystery code, just clear, production-ready solutions explained line-by-line.

### The Birth of the PRIME Framework

In the early days, we built custom automation for clients the traditional way: they'd describe a pain point, we'd write a Python script, deliver the code, invoice, and move on. Projects succeeded technically—the code worked—but we noticed a pattern:

**6 months later, the automation had stalled.**

Not because the code broke, but because:

- 🔻 **Nobody could modify it** when requirements changed (vendor lock-in)
- 🔻 **Leadership questioned the value** (no ROI metrics)
- 🔻 **The "easy" automations had been built** (leaving hard, high-value work undone)
- 🔻 **Teams didn't know what to automate next** (no roadmap)

We realized: **Delivering scripts isn't enough. Sustainable automation requires a structured methodology.**

That's why we created the **PRIME Framework**—a 5-stage approach that ensures every automation project delivers:

✅ **Measurable value** (Pinpoint opportunities based on data, not guesswork)  
✅ **Optimized workflows** (Re-engineer processes before automating)  
✅ **Production-grade quality** (Implement with safety, testing, documentation)  
✅ **Proven ROI** (Measure performance with concrete metrics)  
✅ **Team capability** (Empower internal staff to maintain and extend)

The name "PRIME" reflects our commitment to **excellence** over mediocrity:

- **P**inpoint Inefficiencies
- **R**e-engineer Workflows
- **I**mplement Solutions
- **M**easure Performance
- **E**mpower Your Team

The framework is built on the **Prime Philosophy** (our three core engineering principles), ensuring every line of code is transparent, reliable, and pragmatic.

**[Learn about the PRIME Framework →](./prime-framework/index.md)**

---

## What We Do

We provide education, open-source tools, and professional services—all guided by the **[PRIME Framework](./prime-framework/index.md)** and **Prime Philosophy**.

### 🎓 Education & Tutorials

Free, comprehensive guides that teach network automation through real-world Cisco use cases:

- **[Tutorials](./tutorials/index.md):** Step-by-step practical scripts for beginners, intermediate, and expert levels
- **[Deep Dives](./deep-dives/index.md):** Production-grade code walkthroughs with line-by-line explanations
- **Learning Path:** From first Netmiko script to advanced Nornir parallelization

Every script is explained line-by-line, every design decision documented.

### 🛠️ Open-Source Tools

Production-hardened Python scripts for common network automation tasks:

- [CDP Network Audit](./deep-dives/cdp-audit.md)
- [Access Switch Port Audit](./deep-dives/access-switch-audit.md)
- [Zero Touch Provisioning (ZTP)](./coming-soon/cisco-ios-xe-ztp.md) — Coming Soon
- [IOS-XE Upgrade Orchestrator](./coming-soon/ios-xe-upgrade-orchestrator.md) — Coming Soon

All tools are available on GitHub under GPL-3.0 license.

### 💼 Professional Services via PRIME Framework

Structured automation delivery through a proven 5-stage methodology:

**[Pinpoint](./prime-framework/pinpoint.md)** → **[Re-engineer](./prime-framework/re-engineer.md)** → **[Implement](./prime-framework/implement.md)** → **[Measure](./prime-framework/measure.md)** → **[Empower](./prime-framework/empower.md)**

## The Prime Philosophy {:#prime-philosophy}

Every tool, guide, and service adheres to three core engineering principles:

### 🎯 1. Pragmatic Over Perfect

**Ship solutions that work today, not theoretical perfection that never ships.**

We favor:

- ✅ Simple, direct solutions over abstract architectures
- ✅ Working code with clear TODOs over delayed perfection
- ✅ Solving today's problem efficiently over future-proofing speculatively

Complexity must earn its place by delivering measurable value.

**In Practice:** A 150-line script that solves the problem beats a 2,000-line "framework" that handles hypothetical edge cases.

### 🔍 2. Transparency Over Obscurity

**Verbose logging, human-readable outputs, zero "black box" magic.**

We explain:

- ✅ **The "why"** behind every design decision, not just the "what"
- ✅ **Every line of code** with detailed inline comments
- ✅ **Execution progress** with comprehensive logging (INFO, WARNING, ERROR)
- ✅ **Results** with Excel reports and executive summaries

**In Practice:** When automation fails at 2 AM, logs show exactly what happened and where. No mystery debugging.

### 🛡️ 3. Reliability Over Speed

**Pre-flight validation, post-flight verification, automatic rollback.**

Production networks deserve bulletproof automation:

- ✅ **Pre-flight checks:** Validate devices are reachable, configs won't conflict
- ✅ **Post-flight validation:** Verify changes were actually applied as intended
- ✅ **Automatic rollback:** Undo changes if validation fails
- ✅ **Comprehensive error handling:** Graceful degradation, never crash-and-burn

**In Practice:** Automation that works 98% of the time causes 2% catastrophic failures. Reliability means handling the 2% without human intervention.

---

### How Philosophy Informs Framework

The **Prime Philosophy** (values) guides the **PRIME Framework** (methodology):

| Philosophy Principle | Framework Application |
| :--- | :--- |
| **🎯 Pragmatic** | Pinpoint ROI-positive automations (not every task deserves automation) |
| **🔍 Transparent** | Measure with concrete metrics; Empower teams with detailed documentation |
| **🛡️ Reliable** | Re-engineer workflows with safety mechanisms; Implement with validation |

**[Learn about the PRIME Framework →](./prime-framework/index.md)**

### 1. Line-by-Line Transparency

We explain the *why* behind the code, not just the *what*. Every design decision is documented so you understand your automation completely.

### 2. Hardened for Production

Robust error handling, pre-flight safety checks, enterprise credential management, and thread-safe operations. These aren't "nice to have"—they're essential for critical infrastructure.

### 3. Vendor-Neutral

Built on industry-standard libraries (Netmiko, Nornir, PyATS). Your skills remain portable across vendors and platforms.

---

## The Team

**Christopher Davies** - Founder & Principal Automation Engineer

Christopher specialises in enterprise Cisco automation, with deep expertise in Python, ISE, and Zero Trust architectures. His mission is to democratise network automation through transparency and education.

**Trading Status:** Christopher Davies trading as (T/A) Nautomation Prime

[Connect on LinkedIn](https://www.linkedin.com/company/nautomationprime){ .md-button }

---

## Technology Stack

Our tools and guides leverage industry-standard Python libraries:

- **Netmiko** - Multi-vendor SSH automation
- **Paramiko** - Low-level SSH protocol implementation
- **Nornir** - Multi-threaded automation framework
- **TextFSM** - Structured parsing of CLI output
- **Pandas & OpenPyXL** - Professional Excel reporting
- **PyATS** - Cisco test automation framework

---

## Open Source Commitment

All public repositories are licenced under **GNU GPL-3.0**, ensuring:

- Source code transparency
- Community contributions welcome
- Free for educational and commercial use
- Copyleft protection

Bespoke client code is licenced under **MIT** or **Apache 2.0** as agreed during engagement.

[View Licensing Details](legal/licensing.md)

---

## Get Involved

### Use Our Tools

Browse the [Script Librarynetwork engineers through the **[PRIME Framework](./prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **Prime Philosophy** of transparency, reliability, and pragmatism

### Learn Network Automation

Explore our [Technical Deep Dives](deep-dives/index.md) for comprehensive guides.

### Request Custom Solutions

Need bespoke automation? [Contact us](services.md) to discuss your requirements.

### Contribute

Found a bug or have a feature request? Open an issue on our [GitHub organisation](https://github.com/Nautomation-Prime).

---

## Contact

**Geographic Address (UK):**  
Christopher Davies T/A Nautomation Prime  
9 The Sleeve  
Leek, ST138 HR  
Staffordshire  
England  
United Kingdom

- **Email:** [nautomationprime.f3wfe@simplelogin.com](mailto:nautomationprime.f3wfe@simplelogin.com)
- **LinkedIn:** [Nautomation Prime Company Page](https://www.linkedin.com/company/nautomationprime)
- **GitHub:** [Nautomation-Prime Organisation](https://github.com/Nautomation-Prime)

---

## Legal

- [Privacy Policy](legal/privacy-policy.md)
- [Terms of Use](legal/terms-of-use.md)
- [Disclaimer](legal/disclaimer.md)
- [Licensing](legal/licensing.md)
- [Brand & Logo Usage](legal/brand.md)

---

> **Mission:** To empower network engineers through the **[PRIME Framework](./prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[Prime Philosophy](#prime-philosophy)** of transparency, reliability, and pragmatism.
