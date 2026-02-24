---
title: Model-Driven APIs in Network Automation: gNMI, RESTCONF, and the Future of Device Management
description: How model-driven APIs are changing network automation, with practical examples and PRIME-aligned best practices.
tags:
  - Blog
  - Model-Driven APIs
  - gNMI
  - RESTCONF
  - YANG
  - PRIME Framework
  - Best Practices
---

# Model-Driven APIs in Network Automation: gNMI, RESTCONF, and the Future of Device Management

> *Published: February 24, 2026  \
Author: Nautomation Prime Team*

---
> **This post is part of our ongoing series on network automation best practices, grounded in the [PRIME Framework](../prime-framework/index.md) and [PRIME Philosophy](../prime-framework/philosophy.md).**

## Why This Blog Exists

Legacy CLI and SNMP are giving way to model-driven APIs like gNMI and RESTCONF. This post explains what they are, why they matter, and how to use them for scalable, vendor-neutral automation.

---

## What are Model-Driven APIs?

- APIs based on YANG data models
- gNMI (gRPC Network Management Interface)
- RESTCONF (RESTful API for YANG models)
- Enable structured, programmatic device management

---


---

## Related Tutorials & Deep Dives

- [Streaming Telemetry in Network Automation](emerging-tech-streaming-telemetry.md) — Real-time data for modern automation workflows.
- [AI and Machine Learning in Network Automation](emerging-tech-ai-ml-network-automation.md) — Explore practical AI/ML use cases for automation.
- [Event-Driven Automation in the Network](emerging-tech-event-driven-automation.md) — Build real-time, event-driven workflows.

- Consistent, vendor-neutral automation
- Faster, safer, and more reliable than CLI scraping
- Enable intent-based and closed-loop automation

---

## Getting Started

- Identify devices that support gNMI/RESTCONF
- Use open-source libraries (pygnmi, requests)
- Build scripts for config, state, and telemetry

---

## Example: Using pygnmi for gNMI

```python
from pygnmi.client import gNMIclient
with gNMIclient(target=('router', 57400), username='admin', password='pass') as gc:
    result = gc.get(path=['/interfaces/interface[name=Ethernet1]'])
    print(result)
```

---

## PRIME in Action: Transparency and Ownership

- Document API usage and dependencies
- Build abstraction layers for portability
- Track API changes and vendor support

---

## Summary: Blog Takeaways

- Model-driven APIs are the future of network automation
- Use gNMI and RESTCONF for scalable, vendor-neutral management
- PRIME principles ensure safe, transparent adoption

---

## 📣 Want More?

- [Vendor-Neutral Automation: Avoiding Lock-In and Building for Portability](vendor-neutral-automation.md)
- [PRIME Framework Overview](../prime-framework/index.md)

---
