---
title: Credential Management in Network Automation
date: 2026-02-26T12:00:00
draft: false
author: "Nautomation Prime Team"
description: How to manage credentials securely in network automation, avoid common pitfalls, and align with the PRIME Framework for production safety.
tags:
  - Blog
  - Credential Management
  - Security
  - PRIME Framework
  - Best Practices
---

## Credential Management in Network Automation: Best Practices for Safety and Scale

---

> **This post is part of our ongoing series on network automation best practices, grounded in the [PRIME Framework](../../prime-framework/index.md) and [PRIME Philosophy](../../prime-framework/philosophy.md).**

## Why This Blog Exists

Credentials are the keys to your network—and the #1 target for attackers. This post explains why credential management is critical, how to do it safely, and how the PRIME Framework guides best practices for production automation.

<!-- more -->

---

## 🚦 PRIME Philosophy: Safety First

- **Safety:** Never hardcode credentials. Always use secure storage and retrieval.
- **Transparency:** Know where every credential is used and why.
- **Measurability:** Audit credential usage and access.
- **Ownership:** Your team controls the secrets, not a vendor.
- **Empowerment:** Make secure practices easy for engineers.

---

## Related Tutorials & Deep Dives

- [Secure Credential Vaulting (Expert)](../../tutorials/expert/secure-credential-vaulting.md) — Integrate enterprise-grade secrets management into your automation workflows.
- [Deep Dive: Access Switch Audit](../../deep-dives/access-switch-audit.md) — See credential management in a real-world modular automation tool.

- Hardcoded passwords are a breach waiting to happen
- Shared credentials make auditing impossible
- Manual rotation leads to outages and mistakes
- Compliance requires proof of secure handling

---

---

## Why Credential Management Matters

- **Security breach risk:** Exposed credentials lead to unauthorized access, data theft, and network compromise
- **Compliance violations:** PCI-DSS, SOX, HIPAA, and other standards require secure credential handling
- **Audit trail:** Every credential access must be logged for compliance and incident investigation
- **Hardcoded credentials are a common attack vector:** They appear in Git history, backups, logs everywhere
- **Shared credentials prevent accountability:** You can't track who made changes or when

**Real Cost of a Breach:**
    - Average breach cost: $4+ million (IBM 2021 study)
    - Security incident response: Months of effort
    - Reputation damage: Lost customer trust
    - Compliance fines: Potentially millions

---

## Secure Credential Management Patterns

### 1. Environment Variables (Simple, Local Development)

Store secrets outside code and config files. Use `.env` files with python-dotenv (for development only).

```python
import os
from dotenv import load_dotenv

# Load from .env file (NEVER COMMIT THIS!)
load_dotenv()

username = os.environ['DEVICE_USERNAME']
password = os.environ['DEVICE_PASSWORD']

# For production, set environment variables via CI/CD or deployment platform
```

**`.env` file example (development only):**
```
DEVICE_USERNAME=admin
DEVICE_PASSWORD=SecurePassword123!
DEVICE_IPS=10.0.0.1,10.0.0.2,10.0.0.3
```

**Security checklist:**
- [ ] `.env` file is in `.gitignore` (never commit!)
- [ ] Env vars are set by deployment system (Kubernetes, CI/CD, cloud provider)
- [ ] Different credentials for dev/staging/prod
- [ ] Credentials are rotated regularly

---

### 2. Vault Integration (Enterprise-Grade, Multi-Team)

HashiCorp Vault provides centralized credential management with comprehensive auditing.

```python
import hvac
import os

class VaultCredentialProvider:
    """Fetch credentials from HashiCorp Vault."""
    
    def __init__(self, vault_addr: str, vault_token: str):
        """
        Args:
            vault_addr: Vault server address (e.g., 'https://vault.example.com')
            vault_token: Token for Vault authentication (from env var)
        """
        self.client = hvac.Client(url=vault_addr, token=vault_token)
    
    def get_credentials(self, device_id: str) -> dict:
        """
        Fetch credentials from Vault.
        
        Vault path structure:
        secret/network/devices/{device_id} -> {username, password, enable_password}
        """
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=f'network/devices/{device_id}'
            )
            creds = secret['data']['data']
            return {
                'username': creds['username'],
                'password': creds['password'],
                'enable_password': creds.get('enable_password', ''),
            }
        except hvac.exceptions.InvalidPath as e:
            raise CredentialNotFound(f"Device credentials not found: {device_id}") from e
        except hvac.exceptions.Forbidden as e:
            raise CredentialAccessDenied(f"Access denied to device credentials: {device_id}") from e
    
    def list_credentials(self, path: str) -> list:
        """List available credentials (no secrets returned)."""
        return self.client.secrets.kv.v2.list_secrets(path)
    
    def rotate_credential(self, device_id: str, new_password: str) -> bool:
        """Rotate a device password in Vault."""
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=f'network/devices/{device_id}'
        )
        secret['data']['data']['password'] = new_password
        
        self.client.secrets.kv.v2.create_or_update_secret(
            path=f'network/devices/{device_id}',
            secret_data=secret['data']['data']
        )
        return True

# Usage
vault_provider = VaultCredentialProvider(
    vault_addr=os.environ['VAULT_ADDR'],
    vault_token=os.environ['VAULT_TOKEN']
)

creds = vault_provider.get_credentials('router-01')
print(creds)  # Only username, password, enable_password (no URLs or extra secrets)
```

**Vault Setup & Best Practices:**
- Create separate Vault paths for dev/staging/prod
- Use AppRole or JWT authentication (not long-lived tokens)
- Enable audit logging (log every secret access)
- Auto-rotate credentials using Vault workflows
- Limit token TTL (time-to-live)

---

### 3. AWS Secrets Manager (Cloud-Native)

For AWS users, Secrets Manager provides managed secret storage.

```python
import boto3
import json
import os

class AWSSecretProvider:
    """Fetch credentials from AWS Secrets Manager."""
    
    def __init__(self, region='us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region)
    
    def get_credentials(self, secret_name: str) -> dict:
        """Fetch secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            if 'SecretString' in response:
                secret = json.loads(response['SecretString'])
                return secret
            else:
                # Binary secret (rare for network credentials)
                return response['SecretBinary']
        except self.client.exceptions.ResourceNotFoundException:
            raise CredentialNotFound(f"Secret not found: {secret_name}")
        except Exception as e:
            raise CredentialAccessDenied(f"Failed to retrieve secret: {e}")
    
    def rotate_secret(self, secret_name: str, new_password: str) -> bool:
        """Update a secret in AWS."""
        try:
            response = self.client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps({'password': new_password})
            )
            return True
        except Exception as e:
            print(f"Rotation failed: {e}")
            return False

# Usage
aws_provider = AWSSecretProvider()
creds = aws_provider.get_credentials('network/router-01')
```

---

### 4. Encrypted Files (SOPS, Ansible Vault)

For team-based development, use encrypted files with version control.

**SOPS (Secrets Operations):**

```bash
# Install SOPS and initialize with AWS KMS or GPG
brew install sops

# Create encrypted secrets file
sops --kms 'arn:aws:kms:us-east-1:123456789:key/abc123' secrets.yaml
```

```yaml
# secrets.yaml (encrypted)
devices:
  router-01:
    username: admin
    password: ENC[AES256_GCM,data:xyz,iv:abc,...]
  router-02:
    username: admin
    password: ENC[AES256_GCM,data:xyz,iv:def,...]
```

**In code:**
```python
import yaml
import subprocess

def load_sops_secrets(file_path: str) -> dict:
    """Load SOPS-encrypted secrets file."""
    result = subprocess.run(
        ['sops', '--decrypt', file_path],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise CredentialAccessDenied(f"Failed to decrypt: {result.stderr}")
    
    return yaml.safe_load(result.stdout)

creds = load_sops_secrets('secrets.yaml')
```

---

## Refactoring a Script for Secure Credentials

**Before (INSECURE):**
```python
# BAD: Hardcoded credentials visible in code and Git history!
devices = [
    {'ip': '10.0.0.1', 'username': 'admin', 'password': 'cisco123'},
    {'ip': '10.0.0.2', 'username': 'admin', 'password': 'cisco123'},
]

for device in devices:
    conn = netmiko.ConnectHandler(**device, device_type='cisco_ios')
    print(conn.send_command('show version'))
```

**After (SECURE with Vault):**
```python
# GOOD: Credentials pulled from Vault at runtime
vault = VaultCredentialProvider(vault_addr=os.environ['VAULT_ADDR'],
                               vault_token=os.environ['VAULT_TOKEN'])

device_ips = ['10.0.0.1', '10.0.0.2']

for ip in device_ips:
    creds = vault.get_credentials(ip)
    conn = netmiko.ConnectHandler(
        host=ip,
        device_type='cisco_ios',
        username=creds['username'],
        password=creds['password'],
        enable_password=creds.get('enable_password', '')
    )
    print(conn.send_command('show version'))
```

---

## Advanced Patterns: Rotation, Auditing, and Compliance

### Automated Credential Rotation

```python
import asyncio
from datetime import datetime, timedelta

class CredentialRotationManager:
    """Automatically rotate device credentials."""
    
    def __init__(self, vault_provider, rotation_interval_days=90):
        self.vault = vault_provider
        self.rotation_interval = timedelta(days=rotation_interval_days)
    
    async def rotate_all_credentials(self):
        """Rotate all device credentials on schedule."""
        devices = self.vault.list_credentials('network/devices')
        
        for device_id in devices:
            try:
                # Check last rotation date
                last_rotated = await self.get_last_rotation_date(device_id)
                if datetime.now() - last_rotated > self.rotation_interval:
                    print(f"Rotating credentials for {device_id}")
                    await self.rotate_device_credential(device_id)
            except Exception as e:
                print(f"Rotation failed for {device_id}: {e}")
    
    async def rotate_device_credential(self, device_id: str):
        """Rotate a single device's credential."""
        # Generate new password
        new_password = self.generate_secure_password()
        
        # Connect to device and set new password
        creds = self.vault.get_credentials(device_id)
        device_ip = self.resolve_device_ip(device_id)
        
        await self.set_device_password(device_ip, creds, new_password)
        
        # Update Vault
        self.vault.rotate_credential(device_id, new_password)
        
        # Log rotation
        await self.log_rotation_event(device_id)
    
    def generate_secure_password(self) -> str:
        """Generate a strong random password."""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(16))
        return password
    
    async def log_rotation_event(self, device_id: str):
        """Log credential rotation for compliance."""
        event = {
            'event': 'credential_rotation',
            'device': device_id,
            'timestamp': datetime.now().isoformat(),
            'user': os.environ.get('USER', 'automation'),
        }
        # Send to logging system, e.g., Splunk, ELK
        print(f"[AUDIT] {event}")
```

### Audit Logging with Splunk/ELK

```python
import logging
from logging.handlers import SyslogHandler

# Configure structured logging to Splunk
class SplunkFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'event_type': getattr(record, 'event_type', 'unknown'),
            'device': getattr(record, 'device', ''),
            'user': getattr(record, 'user', ''),
        }
        return json.dumps(log_entry)

# Setup handler
logger = logging.getLogger('credential_audit')
handler = SyslogHandler(address=('splunk-collector', 514))
formatter = SplunkFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log credential access
def log_credential_access(device_id, action, user):
    """Log all credential access for audit."""
    logger.info(
        f"Credential {action}",
        extra={
            'event_type': f'credential_{action}',
            'device': device_id,
            'user': user,
        }
    )
```

---

## PRIME in Action: Credential Auditing, Rotation, and Ownership

- Use logging to track credential usage (never log secrets themselves)
- Automate rotation and test for expired credentials in CI/CD
- Document credential sources, update processes, and access policies
- Ensure only authorized users/systems can access production credentials
- Regular audits: Who accessed credentials? When? For what purpose?
- Compliance integration: Generate reports for compliance teams

---

## Security Checklist: Credential Management

- [ ] No hardcoded credentials in code or config files
- [ ] Credentials stored in dedicated vault/manager (Vault, AWS, Azure, etc.)
- [ ] Environment-specific credentials (dev/staging/prod)
- [ ] Credentials rotated every 30-90 days
- [ ] API keys and tokens have expiration dates
- [ ] All credential access is logged with timestamps and users
- [ ] Access to credentials requires authentication (MFA where possible)
- [ ] Credentials are never logged or printed
- [ ] CI/CD pipelines use vault agents or short-lived tokens
- [ ] Regular audit logs reviewed for unauthorized access
- [ ] Incident response plan for potential credential leaks
- [ ] Team training on secure handling (no screenshots, pastebin, etc.)

---

## Summary: Blog Takeaways

- Secure credential management is non-negotiable for production automation
- Use environment variables, secrets managers, RBAC, and dynamic secrets
- Automate rotation, auditing, and compliance
- PRIME principles make security sustainable, auditable, and empowering
- Test credential handling in CI/CD pipelines before production
- Educate team on secure practices—most breaches are human error

---

---

## 📣 Want More?

- [How to Choose the Right Network Automation Framework](choosing-network-automation-framework.md)
- [Why Most Network Automation Pipelines Fail (And How to Fix Them)](why-automation-fails.md)
- [PRIME Framework Overview](../../prime-framework/index.md)

---
