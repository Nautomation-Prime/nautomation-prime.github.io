---
title: Model-Driven APIs in Network Automation
date: 2026-02-26T12:00:00
author: "Nautomation Prime Team"
draft: false
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

## Model-Driven APIs in Network Automation: gNMI, RESTCONF, and the Future of Device Management

---
> **This post is part of our ongoing series on network automation best practices, grounded in the [PRIME Framework](../../prime-framework/index.md) and [PRIME Philosophy](../../prime-framework/philosophy.md).**

## Why This Blog Exists

Legacy CLI and SNMP are giving way to model-driven APIs like gNMI and RESTCONF. This post explains what they are, why they matter, and how to use them for scalable, vendor-neutral automation.

<!-- more -->

---

## What are Model-Driven APIs?

- APIs based on YANG data models (standardized, vendor-neutral)
- gNMI (gRPC Network Management Interface): high-performance, streaming, and config/state access
- RESTCONF: RESTful API for YANG models, easy to use with HTTP/JSON
- Enable structured, programmatic device management and automation
- Replace legacy CLI scraping and SNMP with reliable, scalable interfaces

---

## Why Model-Driven APIs? (Benefits & Use Cases)

- **Consistency:** Same data model and API across vendors (multi-vendor automation)
- **Reliability:** Fewer parsing errors, less breakage on upgrades
- **Speed:** Bulk config/state retrieval, streaming telemetry
- **Intent-based automation:** Express desired state, not just CLI commands

**Common Use Cases:**

- Automated config deployment and validation
- Real-time state monitoring and alerting
- Closed-loop remediation (auto-fix drift)
- Compliance and audit reporting

---

## YANG Data Models: The Foundation

- YANG defines the structure of config/state data (interfaces, BGP, QoS, etc.)
- Vendors and standards bodies publish YANG models (OpenConfig, IETF, Cisco)
- Tools: pyang, yang-explorer for browsing and validating models

---

## Example 1: Using pygnmi for gNMI (Config/State)

```python
from pygnmi.client import gNMIclient
with gNMIclient(target=('router', 57400), username='admin', password='pass', insecure=True) as gc:
  # Get interface state
  result = gc.get(path=['/interfaces/interface[name=Ethernet1]'])
  print(result)
  # Set config example
  set_result = gc.set(update=[('/interfaces/interface[name=Ethernet1]/config/enabled', False)])
  print(set_result)
```

---

## Example 2: Using RESTCONF with Python (requests)

```python
import requests
import json

url = 'https://router/restconf/data/ietf-interfaces:interfaces/interface=Ethernet1'
headers = {
  'Accept': 'application/yang-data+json',
  'Content-Type': 'application/yang-data+json',
}
auth = ('admin', 'pass')
response = requests.get(url, headers=headers, auth=auth, verify=False)
print(json.dumps(response.json(), indent=2))
```

---

## Advanced Patterns: Abstraction, Error Handling, and Portability

- Build Python classes/functions to abstract API calls (hide protocol details)
- Handle errors and API version changes gracefully
- Use environment variables or vaults for credentials
- Track vendor support and API changes over time

---

## PRIME in Action: Transparency, Ownership, and Measurability

- Document API usage, dependencies, and data models
- Build abstraction layers for portability and future-proofing
- Track API changes, vendor support, and automation outcomes
- Use model-driven APIs for compliance, audit, and reporting

---

## Summary: Blog Takeaways

- Model-driven APIs are the future of scalable, reliable, and vendor-neutral network automation
- Use gNMI and RESTCONF for structured config, state, and telemetry
- Build abstractions and track changes for long-term success
- PRIME principles ensure safe, transparent, and measurable adoption

---

## Related Tutorials & Deep Dives

- [Streaming Telemetry in Network Automation](emerging-tech-streaming-telemetry.md) — Real-time data for modern automation workflows.
- [AI and Machine Learning in Network Automation](emerging-tech-ai-ml-network-automation.md) — Explore practical AI/ML use cases for automation.
- [Event-Driven Automation in the Network](emerging-tech-event-driven-automation.md) — Build real-time, event-driven workflows.

---

## 📣 Want More?

- [Vendor-Neutral Automation: Avoiding Lock-In and Building for Portability](vendor-neutral-automation.md)
- [PRIME Framework Overview](../../prime-framework/index.md)

---
