---
title: Coming Soon
description: Preview upcoming Python automation scripts and tools for Cisco network engineering, currently in design and development.
tags:
  - Coming Soon
  - Roadmap
---

# Coming Soon

Welcome to the **Coming Soon** section! This area showcases automation projects currently in the design and planning phase. These comprehensive solutions are being carefully architected to address real-world network engineering challenges.

---

## What to Expect

The scripts and tools featured here represent:

- **Detailed Design Documents** - Comprehensive planning blueprints covering architecture, workflows, and implementation strategies
- **Best Practices** - Industry-standard approaches to common network automation challenges
- **Platform-Specific Guidance** - Tailored solutions for Cisco IOS, IOS-XE, NX-OS, and other platforms
- **Production-Ready Planning** - Enterprise-grade considerations for fault tolerance, security, and scalability

---

## Projects in Development

### [Cisco IOS-XE Zero Touch Provisioning](Cisco%20IOS-XE%20Zero%20Touch%20Provisioning.md)

A production-ready Python script for automating Day 0 provisioning of Cisco Catalyst switches running IOS-XE. This comprehensive solution enables hands-free deployment at scale with enterprise-grade reliability.

- Serial-based configuration lookup with automatic device identification
- Retry logic with exponential backoff for network resilience
- Structured JSON logging to Graylog/Syslog for centralized monitoring
- Automatic SSH key generation and secure file cleanup
- Rotating flash logs and optional JSON device reports
- Platform-specific guidance for StackWise, dual SUP, and multi-platform deployments

**Unique Features:** Built-in retry mechanisms handle real-world network transients (Spanning Tree convergence, DHCP timing), structured logging enables searchable device tracking without knowing IP addresses, and secure credential handling with automatic cleanup.

**Status:** :test_tube: Testing & Validation Phase

---

### [IOS-XE Software Upgrade Orchestrator](IOS-XE%20Software%20Upgrade%20Orchestrator.md)

A comprehensive Python-based orchestration framework for automating Cisco IOS-XE software upgrades across diverse platforms. This design document covers:

- End-to-end upgrade workflows (discovery, validation, execution, rollback)
- Platform-specific considerations (ISSU, dual SUPs, StackWise Virtual)
- Fault tolerance and error handling strategies
- **Integration with Cisco Catalyst Center, Ansible, and Nornir** - Detailed analysis of when and why to use Python alongside these popular platforms
- Excel-based inventory management and existing automation tool integration
- Security, compliance, and audit trail requirements

**Unique Feature:** This design includes in-depth comparisons explaining why Python orchestration **complements** (not replaces) tools like Catalyst Center and Ansible, with decision matrices and real-world use cases.

**Status:** :fontawesome-solid-drafting-compass: Design & Planning Phase

---

## Stay Updated

These projects will be promoted to the [Script Library](../scripts/index.md) once implementation is complete and thoroughly tested. Check back regularly for updates!

---

!!! tip "Feedback Welcome"
    Have suggestions or specific requirements for these upcoming tools? Feel free to reach out via the [contact page](../about.md#contact).
