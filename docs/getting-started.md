---
title: Getting Started
description: Learn what Nautomation Prime offers and find the right path for your network automation journey. Quick start guide for deep dives, scripts, and services.
tags:
  - Getting Started
  - Guide
  - Tutorial
  - Onboarding
---

Welcome! This guide will help you understand what Nautomation Prime offers and how to get started.

---

## What is Nautomation Prime?

**Nautomation Prime** bridges the gap between complex Cisco infrastructure and streamlined Python-driven automation. We provide:

- **[Tutorials](tutorials/index.md)** — Step-by-step practical guides for learning automation skills
- **[Deep Dives](deep-dives/index.md)** — Production-ready scripts explained line-by-line
- **[Script Library](scripts/index.md)** — Open-source automation tools for common tasks
- **[PRIME Framework Services](prime-framework/index.md)** — Proven 5-stage methodology for automation projects
- **[Professional Services](services.md)** — Custom automation tailored to your topology

**Important:** This site is **not a Python tutorial.** We assume you already know Python basics (variables, functions, loops, exceptions, file I/O). Our goal is to teach you how to apply Python to network automation and provide a foundation you can transfer into your own scripts or learning journey.

---

## 🚀 Quick Start Paths

### I want to learn network automation

Start with our **[Tutorials](tutorials/index.md)**. We provide hands-on, step-by-step guides for beginner, intermediate, and expert levels.

**Recommended Learning Path:**

1. **[Beginner Tutorials](tutorials/beginner/index.md)** — Your first Netmiko scripts
   - [Show Command to Excel](tutorials/beginner/netmiko-show-command-to-excel.md) — Start here
   - [Multi-Device Automation](tutorials/beginner/multi-device-show-command.md) — Scale to multiple devices

2. **[Intermediate Topics](tutorials/intermediate/index.md)** — Configuration management, validation, templating

3. **[Expert Topics](tutorials/expert/index.md)** — Nornir, AsyncIO, advanced patterns

4. **[Deep Dives](deep-dives/index.md)** — Production-grade code walkthroughs
   - [CDP Network Audit](deep-dives/cdp-audit.md) — Threading, security, enterprise design

### I want to use pre-built scripts

Check out our **[Script Library](scripts/index.md)**. Each script comes with documentation and GitHub repositories for easy deployment.

**Popular Scripts:**

- [CDP Network Audit Tool](scripts/index.md) — Discover your Cisco topology with line-by-line transparency
- [Access Switch Audit](deep-dives/access-switch-audit.md) — Port health and compliance checking

### I need custom automation for my environment (Services)

We deliver automation projects through the **[PRIME Framework](prime-framework/index.md)**—a proven 5-stage methodology:

**[Pinpoint](prime-framework/pinpoint.md)** → **[Re-engineer](prime-framework/re-engineer.md)** → **[Implement](prime-framework/implement.md)** → **[Measure](prime-framework/measure.md)** → **[Empower](prime-framework/empower.md)**

**Services include:**

- Full PRIME Framework engagements (discovery to team capability)
- Individual stages (à la carte services)
- Custom Python automation (VLAN provisioning, fleet upgrades, ISE integration)
- Deployment options (standard scripts, portable bundles, Docker containers)

**[View Services](services.md)** | **[Request Discovery Call](mailto:nautomationprime.f3wfe@simplelogin.com)**

---

## 📋 Prerequisites

**Python Knowledge (Important!):**

- **This site assumes you already know Python.** We teach you how to apply Python to network automation, not how to learn Python itself.
- If you're new to Python, we recommend completing a Python fundamentals course first (Codecademy, Real Python, W3Schools, or similar).
- You should understand: variables, functions, loops, conditionals, exceptions, and basic file I/O.
- Our code is written for clarity (not brevity), so intermediate Python developers will follow along easily.

**Technical Requirements:**

- **Python 3.8+** (or use our [portable bundles](services.md#zero-install-portable-bundles) if Python isn't available)
- **Network access** to your Cisco devices
- **Credentials** for device authentication
- **SSH enabled** on target Cisco devices

---

## Prime Philosophy {:#prime-philosophy}

Every tool, script, and guide adheres to three core engineering principles:

1. **🎯 Pragmatic Over Perfect**
    - Ship solutions that work today, not theoretical perfection that never ships
    - Complexity must earn its place by delivering measurable value
    - Simple, direct solutions over abstract architectures

2. **🔍 Transparency Over Obscurity**
    - We explain the *why* behind every line of code, not just the *what*
    - Verbose logging, human-readable outputs, zero "black box" magic
    - Every design decision is documented

3. **🛡️ Reliability Over Speed**
    - Pre-flight validation, post-flight verification, automatic rollback
    - Production-grade error handling—graceful degradation, never crash-and-burn
    - Thread-safe concurrent operations

**These values guide the [PRIME Framework](prime-framework/index.md)** — our structured methodology for automation projects.

**[Learn more about Prime Philosophy](about.md#prime-philosophy)**

---

## 🛠️ Common Tasks

### Deploy the CDP Network Audit Tool

1. Visit the [CDP Audit GitHub repository](https://github.com/Nautomation-Prime/Cisco_CDP_Network_Audit)
2. Read the [Deep Dive guide](deep-dives/cdp-audit.md) for understanding the architecture
3. Follow the README for installation and usage

### Request Custom Automation (PRIME Framework)

For structured automation projects with proven ROI:

1. **[Request Discovery Call](mailto:nautomationprime.f3wfe@simplelogin.com)**—free 30-60 minute discussion
2. Receive [Pinpoint stage](prime-framework/pinpoint.md) roadmap with ROI calculations
3. Choose full [PRIME Framework](prime-framework/index.md) or individual stages (à la carte)
4. Deliverables: Production code, documentation, ROI metrics, team capability

**[Learn about PRIME Framework](prime-framework/index.md)** | **[View Services](services.md)**

### Request Bespoke Automation

For custom automation tailored to your specific topology:

1. Review available [services and deployment options](services.md)
2. Contact us via [email](mailto:nautomationprime.f3wfe@simplelogin.com) or [LinkedIn](https://www.linkedin.com/company/nautomationprime)
3. Describe your requirements and any constraints (e.g., restricted environments, specific platforms)
4. Receive a detailed proposal and timeline

### Use Portable Bundles (No Python Installation)

1. Request a custom bundle through our [services page](services.md#zero-install-portable-bundles)
2. Download the bundle to your workstation or USB drive
3. Extract and run directly—no installation needed
4. Full source code is included for auditing

---

## ❓ Frequently Asked Questions

**Q: Do I need Python installed to use Nautomation Prime tools?**  
A: Not necessarily! We offer [portable bundles](services.md#zero-install-portable-bundles) that run without Python installation. These are ideal for restricted enterprise environments where Python may not be permitted. However, if you want to modify or extend our scripts, you'll need Python 3.8 or higher.

**Q: What's the difference between tutorials, deep dives, and services?**  
A: **[Tutorials](tutorials/index.md)** teach you to build automation yourself with step-by-step guides. **[Deep Dives](deep-dives/index.md)** explain production-grade scripts line-by-line so you understand how they work. **[Services](services.md)** deliver complete automation projects through the **[PRIME Framework](prime-framework/index.md)** with ROI proof and team empowerment.

**Q: Can you automate my specific network topology?**  
A: Absolutely! Our bespoke services cover custom scripting for any topology. Contact us via [email](mailto:nautomationprime.f3wfe@simplelogin.com) or [LinkedIn](https://www.linkedin.com/company/nautomationprime) to discuss your specific requirements.

**Q: Are these tools vendor-locked to Cisco?**  
A: Our tools are built on vendor-neutral libraries like **Netmiko**, **Nornir**, and **NAPALM**. While designed for Cisco, the patterns and concepts apply across other vendors (Juniper, Arista, Palo Alto, etc.). Your skills remain portable across platforms.

**Q: How do I secure my credentials?**  
A: We leverage native OS credential managers (Windows Credential Manager, Keychain on macOS, pass on Linux). Passwords are never stored in plaintext files or hardcoded in scripts. When you run a script like CDP Network Audit for the first time, it will prompt you to save your credentials to Windows Credential Manager—just enter your username and password, and the script will store them securely. Future runs will use the stored credentials automatically.

**Q: What if I don't have Python experience?**  
A: This site assumes you already know Python basics (variables, functions, loops, exceptions). If you're new to Python, we recommend completing a Python fundamentals course first (Codecademy, Real Python, or similar), then return to apply those skills to network automation. Our code is written for clarity, so even beginners with solid fundamentals will be able to follow along.

**Q: Do your scripts work in production environments?**  
A: Yes! All our scripts are production-grade with robust error handling, pre-flight safety checks, thread-safe concurrent operations, and comprehensive logging. We follow the Prime Philosophy principles to ensure reliability over speed. Many organizations use our scripts in live production environments.

**Q: What network devices do your scripts support?**  
A: Our scripts primarily target Cisco devices (IOS, IOS-XE, NX-OS, IOS-XR) but the underlying libraries (Netmiko, Nornir, NAPALM) support many vendors including Juniper, Arista, Palo Alto Networks, F5, and more. The patterns and techniques we teach are transferable across vendors.

**Q: Can I use your code in my own projects?**  
A: Yes! Our open-source scripts are available under permissive licenses. Check each repository for specific licensing terms. We encourage you to learn from, modify, and build upon our code for your own automation projects.

**Q: What's included in the PRIME Framework?**  
A: The [PRIME Framework](prime-framework/index.md) is our proven 5-stage methodology: **Pinpoint** (identify opportunities), **Re-engineer** (design solutions), **Implement** (build automation), **Measure** (prove ROI), and **Empower** (transfer knowledge). Each stage delivers specific outcomes with measurable value. You can engage for the full framework or individual stages à la carte.

---

## � Ready to Get Started?

Whether you're learning automation, deploying tools, or need bespoke services—we're here to help.

### For Custom Automation & Services

**[Book a Discovery Call](mailto:nautomationprime.f3wfe@simplelogin.com)** (Free, 30-60 minutes)

No obligation. We'll discuss your goals, timeline, and answer any questions about the PRIME Framework.

### For Questions or Discussions

- **Email:** [nautomationprime.f3wfe@simplelogin.com](mailto:nautomationprime.f3wfe@simplelogin.com)
- **LinkedIn:** [Nautomation Prime](https://www.linkedin.com/company/nautomationprime)

---

- **Learn Network Automation:** Start with [Tutorials](tutorials/index.md) or study [Deep Dives](deep-dives/index.md)
- **Deploy Tools:** Browse the [Script Library](scripts/index.md)
- **Professional Services:** Explore [PRIME Framework](prime-framework/index.md) for structured automation delivery
- **Custom Solutions:** View [Services](services.md) for bespoke automation options
- **Connect:** Contact us via [email](mailto:nautomationprime.f3wfe@simplelogin.com) or [LinkedIn](https://www.linkedin.com/company/nautomationprime)

---

> **Mission:** To empower network engineers through the **[PRIME Framework](prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[Prime Philosophy](about.md#prime-philosophy)** of transparency, reliability, and pragmatism.
