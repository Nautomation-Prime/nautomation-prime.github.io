---
title: "Secure Credential Vaulting for Network Automation: HashiCorp Vault, AWS Secrets Manager, and Beyond"
description: How to integrate enterprise-grade secrets management into your automation workflows for safety and compliance.
tags:
  - Expert
  - Security
  - Credential Vaulting
  - HashiCorp Vault
  - AWS Secrets Manager
  - Network Automation
  - Tutorial
---

## Secure Credential Vaulting for Network Automation: HashiCorp Vault, AWS Secrets Manager, and Beyond

## Why This Tutorial Exists

Hardcoded credentials are a top security risk. This tutorial shows how to use enterprise secrets managers with Python automation, aligned with the PRIME Framework.

---

## Prerequisites

- Advanced Python
- Familiarity with environment variables and API authentication

---

## Why Use a Secrets Manager?

- Centralized, auditable, and automatable
- Supports rotation, RBAC, and compliance
- Enables dynamic secrets and just-in-time access
- Integrates with CI/CD, GitOps, and automation frameworks

---

## Advanced Example: Using HashiCorp Vault with Python (with Error Handling)

```python
import hvac
import os

def get_vault_secret(path, key):
    client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])
    try:
        secret = client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data'][key]
    except Exception as e:
        raise RuntimeError(f"Vault error: {e}")

password = get_vault_secret('network/creds', 'password')
```

---

## Advanced Example: Using AWS Secrets Manager (with Rotation and JSON Parsing)

```python
import boto3
import json

def get_aws_secret(secret_id, key):
    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId=secret_id)
    secret_dict = json.loads(secret['SecretString'])
    return secret_dict[key]

password = get_aws_secret('network/creds', 'password')
```

---

## Dynamic Secrets and Just-in-Time Access

- Use Vault's dynamic secrets (e.g., SSH, database) for ephemeral credentials
- Example: Retrieve a dynamic SSH credential for a network device

```python
ssh_secret = client.secrets.ssh.generate_credentials(role_name='netops', ip='10.0.0.1')
username = ssh_secret['data']['username']
password = ssh_secret['data']['password']
```

---

## Integrating with Automation Frameworks (Nornir, Netmiko, Ansible, etc.)

- Inject secrets at runtime using environment variables or secure API calls
- Example: Pass credentials to Nornir dynamically

```python
from nornir import InitNornir
from nornir.core.inventory import Host

def set_host_credentials(host: Host):
    host.username = get_vault_secret('network/creds', 'username')
    host.password = get_vault_secret('network/creds', 'password')

nr = InitNornir(config_file='config.yaml')
nr.inventory.hosts['router1'].username = get_vault_secret('network/creds', 'username')
nr.inventory.hosts['router1'].password = get_vault_secret('network/creds', 'password')
```

---

## CI/CD and GitOps Integration

- Use secrets managers with GitHub Actions, GitLab CI, or Jenkins
- Inject secrets as environment variables at runtime
- Never commit secrets to code or config files

Example: GitHub Actions with HashiCorp Vault

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Fetch secrets from Vault
        uses: hashicorp/vault-action@v2
        with:
          url: ${{ secrets.VAULT_ADDR }}
          method: token
          token: ${{ secrets.VAULT_TOKEN }}
          secrets: |
            network/creds username | VAULT_USERNAME
            network/creds password | VAULT_PASSWORD
      - name: Run automation
        run: python scripts/automate.py
        env:
          USERNAME: ${{ env.VAULT_USERNAME }}
          PASSWORD: ${{ env.VAULT_PASSWORD }}
```

---

## Compliance, Auditing, and Best Practices

- Enable audit logging for all secret access
- Enforce RBAC and least-privilege access
- Automate credential rotation and expiration checks
- Document credential sources, access policies, and rotation schedules

---

## PRIME in Action: Safety, Ownership, and Compliance

- Audit credential usage and access
- Automate rotation and expiration checks
- Document credential sources, access, and policies
- Integrate with compliance and security monitoring tools

---

## Summary: Tutorial Takeaways

- Use enterprise secrets managers for production automation
- Integrate secrets with automation, CI/CD, and GitOps workflows
- PRIME principles ensure safety, ownership, and compliance

---

## 📣 Want More?

- [Nornir + PyATS Integration](nornir-pyats-integration.md)
- [Asyncio for Network Automation](asyncio-network-automation.md)
- [DevOps & Observability](devops-observability-network-automation.md)
- [Tool Ecosystem Integration](tool-ecosystem-integration.md)
- [Credential Management in Network Automation](../../blog/posts/credential-management-network-automation.md)
- [PRIME Framework Overview](../../prime-framework/index.md)

---
