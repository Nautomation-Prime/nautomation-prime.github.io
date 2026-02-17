---
title: Resources
description: Comprehensive guide to all Nautomation Prime learning materials, scripts, and automation tools organized by skill level and use case.
---

# Resources

Your complete guide to network automation tools, tutorials, and deep dives. Whether you're building your first Python script or orchestrating enterprise automation, find exactly what you need.

## Learning Paths by Skill Level

=== "Beginner"

    **Perfect for:** First-time automation users, foundation builders
    
    Start with Python fundamentals and basic device automation. No networking automation experience needed.
    
    1. **[Your First Python Network Automation Script](tutorials/beginner/netmiko-show-command-to-excel.md)** — Execute commands and export to Excel
    2. **[Multi-Device Show Commands](tutorials/beginner/multi-device-show-command.md)** — Query multiple devices at once  
    3. **[Multi-Device Configuration Backup](tutorials/beginner/multi-device-config-backup.md)** — Automate backup workflows
    
    **Time to completion:** 2-3 hours | **Prerequisites:** Python basics, SSH access to network devices

=== "Intermediate"

    **Perfect for:** Automation builders, framework explorers
    
    Master parallel execution, advanced inventory management, and enterprise patterns. Assumes Python familiarity and networking knowledge.
    
    1. **[Why Nornir?](tutorials/intermediate/why-nornir.md)** — Understand the shift from sequential to parallel
    2. **[Nornir Fundamentals](tutorials/intermediate/nornir-fundamentals.md)** — Build your first production task
    3. **[Enterprise Config Backup with Nornir](tutorials/intermediate/enterprise-config-backup-nornir.md)** — Scale to thousands of devices
    4. **[Advanced Nornir Patterns](tutorials/intermediate/advanced-nornir-patterns.md)** — Error handling, custom plugins, state management
    
    **Time to completion:** 4-6 hours | **Prerequisites:** Complete all Beginner tutorials or equivalent experience

=== "Expert"

    **Perfect for:** Framework architects, infrastructure engineers
    
    Build production-grade automation systems. Design custom workflows, integrate with enterprise tools, optimize performance.
    
    **Content coming soon.** In the meantime:
    - Explore the [Enterprise Config Backup](tutorials/intermediate/enterprise-config-backup-nornir.md) deep implementation
    - Study [Advanced Nornir Patterns](tutorials/intermediate/advanced-nornir-patterns.md) for scaling strategies
    
    **Expected content:** Custom Nornir plugins, API integration, state persistence, monitoring hooks

---

## Deep Dives: Production Scripts Explained

Line-by-line walkthroughs of real production automation code.

### [CDP Network Audit](deep-dives/cdp-audit.md)

**What it does:** Audit your network's CDP discovery, find orphaned devices, detect infrastructure issues

**Why it matters:** CDP data is often overlooked but reveals critical network health information

**Learn:** CDP parsing, data aggregation, anomaly detection patterns

**Skill level:** Intermediate | **Time:** 45 minutes

---

### [Access Switch Audit](deep-dives/access-switch-audit.md)

**What it does:** Validate access switch configuration consistency across your network

**Why it matters:** Config drift causes outages and security issues

**Learn:** Configuration comparison, multi-device auditing, remediation workflows

**Skill level:** Intermediate+ | **Time:** 1 hour

---

## Scripts Library

Ready-to-use automation tools for common network tasks.

### By Category

**Device Information & Auditing**

- [CDP Network Audit](deep-dives/cdp-audit.md) — Find and validate CDP discoveries
- [Access Switch Audit](deep-dives/access-switch-audit.md) — Detect configuration drift

**Configuration Management**

- [Multi-Device Config Backup](tutorials/beginner/multi-device-config-backup.md) — Backup enterprise configurations  
- [Enterprise Config Backup with Nornir](tutorials/intermediate/enterprise-config-backup-nornir.md) — Scale to thousands of devices

**Reporting & Data Export**

- [Show Command to Excel](tutorials/beginner/netmiko-show-command-to-excel.md) — Execute commands and generate reports
- [Multi-Device Show Commands](tutorials/beginner/multi-device-show-command.md) — Query and compare device data

**[Full Scripts Library](scripts/index.md)** — Browse all available tools

---

## PRIME Framework

Understand the philosophy and methodology behind Nautomation Prime.

- **[PRIME Framework Overview](prime-framework/index.md)** — 5-phase enterprise automation approach
- **[Pinpoint](prime-framework/pinpoint.md)** — Identify automation opportunities
- **[Empower](prime-framework/empower.md)** — Build your team's capabilities
- **[Implement](prime-framework/implement.md)** — Deploy production solutions
- **[Measure](prime-framework/measure.md)** — Track results and ROI
- **[Re-Engineer](prime-framework/re-engineer.md)** — Continuous improvement cycles

---

## Quick Search by Use Case

**I need to...**

**Backup configurations** → [Multi-Device Config Backup](tutorials/beginner/multi-device-config-backup.md) (Beginner) or [Enterprise Backup with Nornir](tutorials/intermediate/enterprise-config-backup-nornir.md) (Intermediate)

**Query device information** → [Show Command to Excel](tutorials/beginner/netmiko-show-command-to-excel.md) or [Multi-Device Show Commands](tutorials/beginner/multi-device-show-command.md)

**Audit network health** → [CDP Network Audit](deep-dives/cdp-audit.md) or [Access Switch Audit](deep-dives/access-switch-audit.md)

**Learn Nornir** → [Why Nornir?](tutorials/intermediate/why-nornir.md) → [Nornir Fundamentals](tutorials/intermediate/nornir-fundamentals.md) → [Advanced Patterns](tutorials/intermediate/advanced-nornir-patterns.md)

**Understand the PRIME approach** → [PRIME Framework](prime-framework/index.md)

**Start from scratch** → [Start Here](getting-started.md)

---

## Choosing Your Starting Point

!!! question "Unsure where to begin?"

    - **New to Python?** → [Start Here](getting-started.md) for environment setup
    - **Know Python, new to networking automation?** → Beginner tutorials
    - **Why Nornir won't work for me?** → It will—see [Why Nornir?](tutorials/intermediate/why-nornir.md)
    - **Building enterprise solutions?** → [Advanced Nornir Patterns](tutorials/intermediate/advanced-nornir-patterns.md)
    - **Want philosophical context?** → [PRIME Framework](prime-framework/index.md)

---

## Suggested Learning Sequences

### Path 1: Foundation Builder (3 hours)
Perfect if you've never automated a network device before.

1. [Your First Python Automation Script](tutorials/beginner/netmiko-show-command-to-excel.md) — Understand the basics
2. [Multi-Device Show Commands](tutorials/beginner/multi-device-show-command.md) — Add scale
3. [Multi-Device Config Backup](tutorials/beginner/multi-device-config-backup.md) — Practical real-world use case

**Next:** Jump to [Why Nornir?](tutorials/intermediate/why-nornir.md)

### Path 2: Production Scaler (5 hours)
You know Python and basic network automation. Need to handle 100+ devices.

1. [Why Nornir?](tutorials/intermediate/why-nornir.md) — Understand parallel execution
2. [Nornir Fundamentals](tutorials/intermediate/nornir-fundamentals.md) — Write production tasks
3. [Enterprise Config Backup with Nornir](tutorials/intermediate/enterprise-config-backup-nornir.md) — Real enterprise pattern
4. [Advanced Nornir Patterns](tutorials/intermediate/advanced-nornir-patterns.md) — Handle edge cases

**Next:** Explore Deep Dives for implementation patterns

### Path 3: Methodology Deep Dive (2 hours)
Understand the strategic framework behind automation decisions.

1. [PRIME Framework Overview](prime-framework/index.md) — The 5-phase model
2. Review each phase: [Pinpoint](prime-framework/pinpoint.md) → [Empower](prime-framework/empower.md) → [Implement](prime-framework/implement.md) → [Measure](prime-framework/measure.md) → [Re-Engineer](prime-framework/re-engineer.md)

**Next:** Apply PRIME thinking to your automation initiatives

### Path 4: Deep Dive Study (2 hours)
Learn by examining production-grade implementations.

1. [CDP Network Audit Deep Dive](deep-dives/cdp-audit.md) — Real network intelligence  
2. [Access Switch Audit Deep Dive](deep-dives/access-switch-audit.md) — Detect infrastructure drift

**Why:** Understand how professionals structure network automation code

---

## Resource Types

Each resource is tagged to help you find content that matches your style:

- **Tutorial** — Step-by-step guided learning with complete code
- **Deep Dive** — Line-by-line explanation of production automation code
- **Framework** — Strategic and methodology content
- **Script** — Ready-to-use automation tools

---

## Frequently Accessed Resources

**Most Popular**

- [Why Nornir?](tutorials/intermediate/why-nornir.md) — The clearest explanation of parallel automation
- [Nornir Fundamentals](tutorials/intermediate/nornir-fundamentals.md) — Your first production task  
- [Multi-Device Config Backup](tutorials/beginner/multi-device-config-backup.md) — The most practical beginner tutorial

**Highest ROI**

- [Enterprise Config Backup with Nornir](tutorials/intermediate/enterprise-config-backup-nornir.md) — Applies immediately to time-consuming manual work
- [Advanced Nornir Patterns](tutorials/intermediate/advanced-nornir-patterns.md) — Turns working code into production-ready code

**Best for Executives**
- [PRIME Framework](prime-framework/index.md) — Strategic, ROI-focused automation methodology
- [Measure](prime-framework/measure.md) — Track and communicate automation impact

---

## Still Need Help?

- **Getting started?** → [Start Here](getting-started.md)
- **Have a specific problem?** → Try [Quick Search by Use Case](#quick-search-by-use-case) above
- **Want to understand our philosophy?** → [About Nautomation Prime](about.md)
