---
title: Script Library
description: Free, open-source, production-grade Python automation tools for Cisco infrastructure, with paid tailoring and deployment available.
tags:
  - Scripts
  - Tools
  - Tools
  - Production Ready
---

## Script Library

### Production-Ready Automation for Cisco Infrastructure

This is the **Nautomation Prime Script Library**: the production-grade, hardened Python tools I have built for enterprise Cisco estates. Each one has a free deep dive that explains exactly how it works.

!!! abstract "Free and open source"
    Every tool here is released under the Apache License 2.0. [Get them on GitHub](https://github.com/Nautomation-Prime) and use, change and share them however you like. If you want a tool tailored, deployed or extended for your estate, I do that as paid work, on [contract](../work-with-me/index.md) or as a [fixed-scope project](../smb/index.md).

!!! warning "Python Prerequisite"
    This site focuses on applying Python to network automation. I assume familiarity with core Python concepts (variables, functions, loops, exceptions, and file I/O). If you're new to Python, complete a fundamentals course first, then return here.

---

## 📚 Available Scripts

### CDP Network Audit Tool

**Status:** ✅ Free and open source (Apache 2.0)
**Description:** A threaded discovery utility that starts from seed Cisco devices and crawls the network using Cisco Discovery Protocol (CDP), producing structured Excel reports with professional formatting.

**Features:**

- Parallel discovery with configurable worker pool (via config.py or environment variable overrides)
- Centralised configuration with comprehensive config.py (200+ documented settings)
- Two-tier authentication (primary user with customisable fallback username)
- Jump server / bastion support (Paramiko channel + Netmiko sock)
- DNS enrichment for discovered hostnames
- Excel reporting from pre-formatted templates with multiple sheets
- Hybrid logging with optional logging.conf
- Up to 3 automatic retries for transient connectivity issues
- Comprehensive error tracking (authentication failures, connection errors)
- Extensive customisation options (credentials, paths, Excel formatting, DNS, logging, and more)


[📖 View Deep Dive Documentation](../foundation/deep-dives/cdp-audit.md) | [💻 Get it on GitHub](https://github.com/Nautomation-Prime/Cisco-Discovery-Audit)

---

### Access Switch Port Audit Tool

**Status:** ✅ Free and open source (Apache 2.0)
**Description:** A production-hardened collector designed to map interface health and utilisation across your access layer.

**Features:**

- Parallel device SSH connections for high-speed audits
- Conservative "Stale Port" detection logic using PoE, neighbours, and input timers
- Multi-source port classification (Access vs. Trunk vs. Routed)
- Professional Excel workbooks with automated conditional formatting
- Full Jump-Host (Bastion) integration for restricted environments


[📖 View Deep Dive Documentation](../foundation/deep-dives/access-switch-audit.md) | [💻 Get it on GitHub](https://github.com/Nautomation-Prime/Access_Switch_Audit)

---

### Cisco IOS-XE Compliance Audit

**Status:** ✅ Free and open source (Apache 2.0)
**Description:** A policy-driven compliance auditor with 90+ role-aware checks, automated remediation generation, and multi-format reporting for enterprise Cisco switches.

**Features:**

- Split YAML config directories plus separate inventory for reusable policy
- Role-aware port classification (uplink, downlink, access, routed, unused)
- 90+ toggleable checks across management, control, and data planes
- Multi-format reporting (HTML dashboards, JSON, CSV, remediation scripts)
- Severity/tag filtering with a governed remediation lifecycle
- Interactive operator modes with approval-governed change execution
- Jump host / bastion support for restricted environments
- Concurrent device auditing for large-scale operations


[📖 View Deep Dive Documentation](../foundation/deep-dives/cisco-compliance-audit.md) | [💻 Get it on GitHub](https://github.com/Nautomation-Prime/Cisco-Compliance-Audit)

---

### Cisco Config Generator

**Status:** ✅ Free and open source (Apache 2.0)  
**Description:** Turns structured Excel intent into per-device Cisco IOS-XE configuration files using a reusable Python core and Jinja2 templates, with a validation-first workflow and a pack architecture that keeps customer rules in data and templates rather than hardcoded logic.

**Features:**

- Intent modelling via a structured Excel workbook
- Validation-first processing before any rendering
- Template-driven Jinja2 rendering with a reusable core engine
- Pack architecture that separates policy-as-data from logic
- Dual execution modes (interactive TUI and headless CLI)
- Deterministic per-device Cisco IOS-XE configuration output

[📖 View Deep Dive Documentation](../foundation/deep-dives/cisco-config-generator.md) | [💻 Get it on GitHub](https://github.com/Nautomation-Prime/Cisco-Config-Generator)

---

### Cisco IOS-XE Software Upgrade Orchestrator

**Status:** ✅ Free and open source (Apache 2.0)
**Description:** A production-grade Python CLI that coordinates multi-device IOS-XE software upgrades with persistent checkpoints, strict safety gates, and deterministic recovery for high-consequence maintenance windows.

**Features:**

- Durable state engine with resumable, checkpointed runs
- Canary and topology-aware batching
- Install-mode-only upgrade policy
- pyATS/Genie pre- and post-change comparison gates
- Explicit handling of partial success and restart recovery

[📖 View Deep Dive Documentation](../foundation/deep-dives/ios-xe-upgrade-orchestrator.md) | [💻 Get it on GitHub](https://github.com/Nautomation-Prime/Cisco-IOS-XE-Software-Upgrade-Orchestrator)

---

## 🧭 Learning Paths

**Unsure where to start?** These learning paths connect scripts to tutorials and deep dives based on your experience level:

### 📖 Beginner Path

Start here if you're new to network automation:

1. Learn Python fundamentals (external resources)
2. Read [Multi-Device Show Command Collection](../foundation/tutorials/beginner/multi-device-show-command.md) — learn Netmiko basics
3. Try [Configuration Backup Tutorial](../foundation/tutorials/beginner/multi-device-config-backup.md) — understand backup patterns
4. Explore the [CDP Network Audit Deep Dive](../foundation/deep-dives/cdp-audit.md) — see how threading and configuration work at scale

### 🛠️ Intermediate Path

Ready to understand production patterns:

1. Read [Nornir Fundamentals](../foundation/tutorials/intermediate/nornir-fundamentals.md) — multi-device automation framework
2. Read [Enterprise Config Backup with Nornir](../foundation/tutorials/intermediate/enterprise-config-backup-nornir.md) — scalable patterns
3. Study [Access Switch Audit Deep Dive](../foundation/deep-dives/access-switch-audit.md) — parallel collection and intelligent parsing
4. Study [CDP Network Audit Deep Dive](../foundation/deep-dives/cdp-audit.md) — threading, configuration, and jump hosts

### 🚀 Advanced Path

Ready to build custom solutions:

1. Review all [Deep Dives](../foundation/deep-dives/index.md) for architectural patterns
2. Study [Cisco Compliance Audit Deep Dive](../foundation/deep-dives/cisco-compliance-audit.md) — policy-driven compliance with remediation generation
3. Read the [PRIME Framework](../prime-framework/index.md) for how I take automation from idea to team ownership
4. Want a tool deployed in your estate? See [Work With Me](../work-with-me/index.md)

---

## 🔄 Coming Soon

### Zero Touch Provisioning (ZTP) Tool

**Status:** 🚧 In Development  
**Description:** Automated deployment solution for Cisco devices that streamlines initial configuration and reduces deployment time from hours to minutes.

**Planned Features:**

- Automated device configuration from templates
- DHCP option integration for network-based provisioning
- Email notifications for deployment status and errors
- HTTP server integration for configuration and log file management
- Pre-flight validation and rollback capabilities
- Multi-device orchestration with dependency management
- Comprehensive logging with remote log collection

**Current Status:** Core functionality tested and validated. Additional features (email notifications, HTTP log server integration) under active development.

---

## 🛠️ Getting Started with Scripts

### Prerequisites

- Python 3.10+
- Netmiko or equivalent SSH library
- Network access to target devices
- Appropriate credentials/permissions

### Installation & Setup

Each tool lives in its own GitHub repository with a README and setup instructions. The typical workflow:

```bash
# Clone the tool's repository
git clone https://github.com/Nautomation-Prime/<tool-repo>.git
cd <tool-repo>

# Install dependencies
pip install -r requirements.txt

# Run with --help to see options
python main.py --help
```

### Credential Management

Scripts use your operating system's native credential manager for secure authentication:

- **Windows:** CDP Network Audit prompts you to save credentials to Windows Credential Manager on first run. Enter your username and password when prompted, and the script will store them securely. Future runs use the stored credentials automatically.  
- **macOS:** Credentials are stored in Keychain - Upcoming  
- **Linux:** Credentials are stored in `pass` or similar managers - Upcoming  

Credentials are never stored in plaintext files or hardcoded in scripts.

Each repository's README covers platform-specific instructions.

### Configuration

All scripts follow the **Nautomation Prime** philosophy of transparency and security:

- Credentials are stored in OS credential managers (Windows Credential Manager, etc.)
- Configuration files are well-documented with inline comments.  
- Pre-flight validation checks prevent unsafe deployments.  

### Support & Questions

For issues, feature requests, or questions about any script:  

- Check the **Deep Dives** documentation for detailed explanations.  
- Raise an issue on the tool's GitHub repository.  
- For tailoring or deployment in your estate, see [Work With Me](../work-with-me/index.md).

---

!!! success "Need one of these tools working in your environment?"
    The tools are free. If you want one adapted, deployed, or rolled out across a live estate, I do that as paid work, on [contract](../work-with-me/index.md) or as a [fixed-scope project](../smb/index.md).

---

## Resources by Topic

**Quick access to find what you need:**

| Topic | Resources |
| :--- | :--- |
| **Network Discovery** | [📖 CDP Network Audit Deep Dive](../foundation/deep-dives/cdp-audit.md) • [💻 GitHub](https://github.com/Nautomation-Prime/Cisco-Discovery-Audit) |
| **Port & Interface Health** | [📖 Access Switch Audit Deep Dive](../foundation/deep-dives/access-switch-audit.md) • [💻 GitHub](https://github.com/Nautomation-Prime/Access_Switch_Audit) |
| **Compliance & Governance** | [📖 Cisco Compliance Audit Deep Dive](../foundation/deep-dives/cisco-compliance-audit.md) • [💻 GitHub](https://github.com/Nautomation-Prime/Cisco-Compliance-Audit) |
| **Configuration Management** | [🎓 Configuration Backup (Beginner)](../foundation/tutorials/beginner/multi-device-config-backup.md) • [🎓 Enterprise Backup with Nornir (Intermediate)](../foundation/tutorials/intermediate/enterprise-config-backup-nornir.md) |
| **Data Collection & Reporting** | [🎓 Show Commands to Excel (Beginner)](../foundation/tutorials/beginner/netmiko-show-command-to-excel.md) • [🎓 Multi-Device Collection (Beginner)](../foundation/tutorials/beginner/multi-device-show-command.md) |
| **Automation Frameworks** | [🎓 Nornir Fundamentals](../foundation/tutorials/intermediate/nornir-fundamentals.md) • [📖 Advanced Patterns](../foundation/tutorials/intermediate/advanced-nornir-patterns.md) |
| **Automation Methodology** | [🚀 PRIME Framework](../prime-framework/index.md) • [ℹ️ Philosophy & Approach](../prime-framework/philosophy.md) |

---

<div class="np-reflection" markdown>
<p class="np-reflection-label">Between the Lines</p>
<p>In martial practice a <em>kata</em> is a form rehearsed until it no longer needs deciding. The value was never the movement itself; it is the attention freed up once the movement has become reliable.</p>
<p>A script library is that idea written down. A tool is only worth having when it gives the same careful result on the hundredth run as on the first—and the reward for that is not speed. It is one less thing occupying you.</p>
</div>

## The "Prime" Philosophy

All scripts in this library adhere to three core principles:

1. **Line-by-Line Transparency** - Every function is documented, every decision explained  
2. **Hardened for Production** - Robust error handling, security best practices, pre-flight checks  
3. **Vendor-Neutral** - Built on industry-standard libraries like Netmiko, Nornir, and TextFSM  

> **Mission:** To empower network engineers through the **[PRIME Framework](../prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](../prime-framework/philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.
