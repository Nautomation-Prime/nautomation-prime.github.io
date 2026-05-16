---
title: Script Library
description: Production-ready Python automation tools for Cisco infrastructure. Open-source scripts with comprehensive documentation and GitHub repositories.
tags:
  - Scripts
  - Tools
  - Open Source
  - GitHub
  - Production Ready
---

## Script Library

### Production-Ready Automation for Cisco Infrastructure

Welcome to the **Nautomation Prime Script Library**. Here you'll find open-source, hardened Python automation tools designed for enterprise Cisco deployments.

!!! warning "Python Prerequisite"
    This site focuses on applying Python to network automation. We assume familiarity with core Python concepts (variables, functions, loops, exceptions, and file I/O). If you're new to Python, complete a fundamentals course first, then return here.

---

## 📚 Available Scripts

### CDP Network Audit Tool

**Status:** ✅ Available  
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

[📖 View Deep Dive Documentation](../deep-dives/cdp-audit.md) | [:material-github: GitHub Repository](https://github.com/Nautomation-Prime/Cisco_CDP_Network_Audit)

---

### Access Switch Port Audit Tool

**Status:** ✅ Available
**Description:** A production-hardened collector designed to map interface health and utilisation across your access layer.

**Features:**

- Parallel device SSH connections for high-speed audits
- Conservative "Stale Port" detection logic using PoE, neighbours, and input timers
- Multi-source port classification (Access vs. Trunk vs. Routed)
- Professional Excel workbooks with automated conditional formatting
- Full Jump-Host (Bastion) integration for restricted environments

[📖 View Deep Dive Documentation](../deep-dives/access-switch-audit.md) | [:material-github: GitHub Repository](https://github.com/Nautomation-Prime/Access_Switch_Audit)

---

### Cisco IOS-XE Compliance Audit

**Status:** ✅ Available
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

[📖 View Deep Dive Documentation](../deep-dives/cisco-compliance-audit.md) | [🗒️ Runbook](https://github.com/Nautomation-Prime/Cisco-Compliance-Audit/blob/main/docs/RUNBOOK.md) | [:material-github: GitHub Repository](https://github.com/Nautomation-Prime/Cisco-Compliance-Audit)

---

## 🧭 Learning Paths

**Unsure where to start?** These learning paths connect scripts to tutorials and deep dives based on your experience level:

### 📖 Beginner Path

Start here if you're new to network automation:

1. Learn Python fundamentals (external resources)
2. Read [Multi-Device Show Command Collection](../tutorials/beginner/multi-device-show-command.md) — learn Netmiko basics
3. Try [Configuration Backup Tutorial](../tutorials/beginner/multi-device-config-backup.md) — understand backup patterns
4. Explore [CDP Network Audit Deep Dive](../deep-dives/cdp-audit.md) — see how threading and configuration work at scale

### 🛠️ Intermediate Path

Ready to understand production patterns:

1. Read [Nornir Fundamentals](../tutorials/intermediate/nornir-fundamentals.md) — multi-device automation framework
2. Read [Enterprise Config Backup with Nornir](../tutorials/intermediate/enterprise-config-backup-nornir.md) — scalable patterns
3. Study [Access Switch Audit Deep Dive](../deep-dives/access-switch-audit.md) — parallel collection and intelligent parsing
4. Study [CDP Network Audit Deep Dive](../deep-dives/cdp-audit.md) — threading, configuration, and jump hosts

### 🚀 Advanced Path

Ready to build custom solutions:

1. Review all [Deep Dives](../deep-dives/index.md) for architectural patterns
2. Study [Cisco Compliance Audit Deep Dive](../deep-dives/cisco-compliance-audit.md) — policy-driven compliance with remediation generation
3. Customize scripts for your environment (GitHub repositories include full source)
4. Integrate with [PRIME Framework](../prime-framework/index.md) methodology
5. Contact us for [consulting services](../services.md) on bespoke automation

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

### IOS-XE Software Upgrade Orchestrator

**Status:** 🚧 In Development  
**Description:** Automated, intelligent firmware management for Cisco IOS-XE switch stacks that eliminates manual upgrade errors and reduces downtime through comprehensive pre-flight validation.

**Planned Features:**

- Pre-flight validation (disk space, compatibility, current version checks)
- Binary integrity verification (MD5/SHA checksums)
- Automated file transfer to target devices (SCP/TFTP/HTTP)
- Stack-aware upgrade orchestration with rolling restarts
- Version compliance reporting across the estate
- Rollback capability for failed upgrades
- Parallel upgrade support for multiple stacks
- Email notifications and comprehensive logging
- Integration with maintenance windows and change control systems

**Current Status:** Architecture and design phase. Feature set being finalised based on enterprise deployment requirements.

---

## 🛠️ Getting Started with Scripts

### Prerequisites

- Python 3.8+
- Netmiko or equivalent SSH library
- Network access to target devices
- Appropriate credentials/permissions

### Installation & Setup

Each script repository includes detailed installation instructions in its README. Typical workflow:

```bash
# Clone the repository
git clone https://github.com/Nautomation-Prime/<script-name>
cd <script-name>

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

See each repository's README for platform-specific instructions.

### Configuration

All scripts follow the **Nautomation Prime** philosophy of transparency and security:

- Credentials are stored in OS credential managers (Windows Credential Manager, etc.)
- Configuration files are well-documented with inline comments.  
- Pre-flight validation checks prevent unsafe deployments.  

### Support & Questions

For issues, feature requests, or questions about any script:  

- Check the **Deep Dives** documentation for detailed explanations.  
- Open an issue on the respective GitHub repository.  
- Contact us via [email](mailto:enquiries@nautomationprime.io) or [LinkedIn](https://www.linkedin.com/company/nautomationprime) for consulting services.  

---

!!! success "Need one of these patterns tailored to your environment?"
  If you want these scripts adapted, extended, or rolled out across a live estate, review our [Enterprise Automation Services](../services.md), the [PRIME Framework](../prime-framework/index.md), or [request a Discovery Call](mailto:enquiries@nautomationprime.io).

---

## Resources by Topic

**Quick access to find what you need:**

| Topic | Resources |
| :--- | :--- |
| **Network Discovery** | [📖 CDP Network Audit Deep Dive](../deep-dives/cdp-audit.md) • [💾 Script](https://github.com/Nautomation-Prime/Cisco_CDP_Network_Audit) |
| **Port & Interface Health** | [📖 Access Switch Audit Deep Dive](../deep-dives/access-switch-audit.md) • [💾 Script](https://github.com/Nautomation-Prime/Access_Switch_Audit) |
| **Compliance & Governance** | [📖 Cisco Compliance Audit Deep Dive](../deep-dives/cisco-compliance-audit.md) • [🗒️ Runbook](https://github.com/Nautomation-Prime/Cisco-Compliance-Audit/blob/main/docs/RUNBOOK.md) • [💾 Script](https://github.com/Nautomation-Prime/Cisco-Compliance-Audit) |
| **Configuration Management** | [🎓 Configuration Backup (Beginner)](../tutorials/beginner/multi-device-config-backup.md) • [🎓 Enterprise Backup with Nornir (Intermediate)](../tutorials/intermediate/enterprise-config-backup-nornir.md) |
| **Data Collection & Reporting** | [🎓 Show Commands to Excel (Beginner)](../tutorials/beginner/netmiko-show-command-to-excel.md) • [🎓 Multi-Device Collection (Beginner)](../tutorials/beginner/multi-device-show-command.md) |
| **Automation Frameworks** | [🎓 Nornir Fundamentals](../tutorials/intermediate/nornir-fundamentals.md) • [📖 Advanced Patterns](../tutorials/intermediate/advanced-nornir-patterns.md) |
| **Automation Methodology** | [🚀 PRIME Framework](../prime-framework/index.md) • [ℹ️ Philosophy & Approach](../prime-framework/philosophy.md) |

---

## The "Prime" Philosophy

All scripts in this library adhere to three core principles:

1. **Line-by-Line Transparency** - Every function is documented, every decision explained  
2. **Hardened for Production** - Robust error handling, security best practices, pre-flight checks  
3. **Vendor-Neutral** - Built on industry-standard libraries like Netmiko, Nornir, and TextFSM  

> **Mission:** To empower network engineers through the **[PRIME Framework](../prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](../prime-framework/philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.
