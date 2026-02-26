---
title: "Nornir + PyATS Integration: Enterprise-Grade Automation and Validation"
description: Combine Nornir's parallel execution with PyATS validation for production-ready, scalable network automation.
tags:
  - Expert
  - Nornir
  - PyATS
  - Validation
  - Enterprise
  - Tutorial
---

# Nornir + PyATS Integration: Enterprise-Grade Automation and Validation

## Why This Tutorial Exists

Most automation frameworks excel at either execution (Nornir) or validation (PyATS)—but not both. This tutorial shows how to combine them for safe, scalable, and measurable automation, aligned with the PRIME Framework.

---

## Prerequisites

- Intermediate Python
- Familiarity with Nornir and PyATS basics
- Working Nornir and PyATS environments

---

## Architecture Overview

- Nornir handles inventory, parallel execution, and task orchestration
- PyATS provides structured validation and parsing
- Integration points: run Nornir tasks, then validate with PyATS

---


## Step 1: Define Inventory and Testbed (Source of Truth)

- Use NetBox, Nautobot, or YAML for Nornir inventory (dynamic inventory recommended for large-scale)
- Use PyATS testbed YAML for device definitions, or generate dynamically from inventory

Example: Dynamic inventory from NetBox
```python
from nornir_netbox.plugins.tasks import netbox_inventory
nr = InitNornir(
  inventory={
    'plugin': 'NetBoxInventory2',
    'options': {'nb_url': 'https://netbox.local', 'nb_token': 'TOKEN'}
  }
)
```

---

## Step 2: Build Nornir Tasks for Config Push with Error Handling

```python
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config
from nornir_utils.plugins.functions import print_result

def push_config(task, commands):
  try:
    task.run(task=netmiko_send_config, config_commands=commands)
  except Exception as e:
    task.host['error'] = str(e)

nr = InitNornir(config_file='config.yaml')
result = nr.run(task=push_config, commands=[...])
print_result(result)
```

---

## Step 3: Validate with PyATS After Each Change (Automated Parsing)

```python
from pyats.topology import loader
from genie.libs.parser.utils import get_parser
import logging

def validate_with_pyats(device, testbed_file, command, parser_name):
  testbed = loader.load(testbed_file)
  dev = testbed.devices[device]
  dev.connect()
  output = dev.execute(command)
  parser = get_parser(command, dev.os, dev.platform, dev.context)
  parsed = parser(device=dev, output=output)
  logging.info(f"Validation for {device}: {parsed}")
  return parsed
```

---

## Step 4: Orchestrate Workflow with Rollback and Reporting

```python
def orchestrate(devices, commands, testbed_file, validation_cmd, parser_name):
  for device in devices:
    push_result = push_config(device, commands)
    validation = validate_with_pyats(device, testbed_file, validation_cmd, parser_name)
    if not validation['expected_state']:
      rollback_config(device)
      log_failure(device, push_result, validation)
    else:
      log_success(device, push_result, validation)
```

---

## Advanced Patterns: Parallelism, Pre/Post Checks, and Compliance

- Use Nornir's parallelism for scale, but throttle for safety (e.g., `num_workers`)
- Automate pre-flight and post-flight validation with PyATS jobs
- Integrate compliance checks (e.g., pyATS Genie, Batfish)

---

## Error Handling, Logging, and Reporting

- Capture and log all exceptions per device
- Use structured logging (e.g., JSON logs) for auditability
- Generate HTML/Markdown reports for stakeholders

Example: Structured logging
```python
import structlog
logger = structlog.get_logger()
logger.info("nornir_pyats_run", device=device, result=validation)
```

---

## Security, Compliance, and Auditability

- Store credentials in vaults (e.g., HashiCorp Vault, Ansible Vault)
- Enforce RBAC for automation execution
- Log every change and validation for compliance

---

## PRIME in Action: Safety, Measurability, and Empowerment

- Pre-flight and post-flight validation for every change
- Automated rollback and structured reporting
- Empower teams with safe, measurable, and auditable automation

---

## Summary: Tutorial Takeaways

- Combining Nornir and PyATS delivers safe, scalable, and compliant automation
- Advanced orchestration, validation, and reporting are key for production
- PRIME principles ensure validation, transparency, and empowerment

---

## 📣 Want More?

- [Asyncio for Network Automation](asyncio-network-automation.md)
- [Secure Credential Vaulting](secure-credential-vaulting.md)
- [DevOps & Observability](devops-observability-network-automation.md)
- [Tool Ecosystem Integration](tool-ecosystem-integration.md)
- [Testing Strategies for Network Automation](../../blog/posts/testing-strategies-network-automation.md)
- [PRIME Framework Overview](../../prime-framework/index.md)

---
