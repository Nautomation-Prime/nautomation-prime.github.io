---
title: PyATS Fundamentals - Network Test Automation
description: Learn PyATS (Python API for Test Automation System), Cisco's enterprise-grade framework used for millions of automated tests monthly. Build reliable network validation.
tags:
  - PyATS
  - Testing
  - Network Automation
  - Cisco
  - Validation
---

## Why PyATS Matters

Cisco uses **PyATS to execute millions of automated tests every month** across their infrastructure and products.

That's not millions per year. **Millions per month.**

If you're building production network automation—whether deploying configurations, upgrading devices, or making bulk changes—you need **validation**. PyATS is how enterprise teams prove their automation actually worked.

---

## What is PyATS?

**PyATS** (Python API for Test Automation System) is Cisco's open-source, enterprise-grade test automation framework.

Built by Cisco engineers to test Cisco equipment at massive scale, it's now available for anyone to use.

### Key Capabilities

- **Device State Validation** — "Does the device have this configuration? Are these routes in the routing table?"
- **Before/After Testing** — Capture network state before automation runs, validate state after, prove the change worked
- **Multi-Vendor Support** — Works with Cisco, Juniper, Arista, F5, and others
- **Testbed-Driven** — Define your network topology once, write tests that apply across all devices
- **Production-Grade** — Robust error handling, detailed reporting, designed for enterprise operations

### Why It's Different from Other Testing Frameworks

| Aspect | PyATS | Generic Unit Testing |
| :--- | :--- | :--- |
| **Focus** | Network devices & infrastructure | Code logic |
| **Connection Model** | SSH/NETCONF to actual devices | Mocks and stubs |
| **Real Device State** | Validates actual network state | Validates code behavior |
| **Enterprise Scale** | Built for millions of tests/month | Built for thousands/day |
| **Network-Specific** | Parsers for Cisco output, device APIs | Generic assertions |

**Example:** PyATS doesn't test "is my VLAN provisioning code correct?" It tests "did the VLAN actually get created on the device?"

---

## The Business Case: Why Your Team Needs This

### The Problem

You've written automation to:

- Provision 50 VLANs across 10 switches
- Upgrade IOS on 200 devices
- Configure new BGP peers on your WAN edge

The automation runs. No errors. You assume it worked.

**But did it actually?**

- Did all 50 VLANs actually get created on all 10 switches?
- Did any devices fail mid-upgrade?
- Did the BGP peering actually establish?

Without validation, you're guessing. And "guesswork" doesn't scale in production environments.

### The Solution: PyATS Validation

```python
# BEFORE automation: Capture current state
before_state = get_vlan_count(switch_ip)
print(f"Before: {before_state} VLANs exist")

# RUN YOUR AUTOMATION (provision 50 new VLANs)
provision_vlans(switch_ip, vlan_list)

# AFTER automation: Validate state changed
after_state = get_vlan_count(switch_ip)
assert after_state == before_state + 50, "VLAN provisioning failed!"
print(f"✅ Validation passed: {after_state} VLANs now exist")
```

**Result:** You have proof. Not "we think it worked." Actual proof.

---

## How PyATS Fits Into the PRIME Framework

| PRIME Stage | PyATS Role |
| :--- | :--- |
| **Pinpoint** | Establish baselines (pre-automation device state) |
| **Re-engineer** | Design validation checkpoints (what to verify) |
| **Implement** | Write PyATS tests alongside automation code |
| **Measure** | Compare before/after states—prove ROI |
| **Empower** | Automated tests become operational runbooks |

---

## PyATS Fundamentals: Key Concepts

### 1. Testbed File

A YAML file defining your network topology:

```yaml
testbed:
  name: "Production Network"

devices:
  switch-01:
    type: switch
    os: ios
    connections:
      cli:
        protocol: ssh
        ip: "10.1.1.1"
        port: 22
        credentials:
          default:
            username: admin
            password: !vault |
              # Encrypted password
    
  switch-02:
    type: switch
    os: ios
    connections:
      cli:
        protocol: ssh
        ip: "10.1.1.2"
        port: 22
        credentials:
          default:
            username: admin
            password: !vault |
              # Encrypted password
```

**Key Point:** Define your devices once. Reuse across all tests.

### 2. Device Parsing

PyATS parses device CLI output into structured data:

```python
from pyats.topology import loader

# Load testbed
testbed = loader.load('testbed.yaml')

# Connect to a device
device = testbed.devices['switch-01']
device.connect()

# Parse CLI output automatically
output = device.parse('show vlan')
# Returns structured dictionary:
# {
#   'vlans': {
#     '1': {'name': 'default', 'interfaces': [...]},
#     '10': {'name': 'DATA', 'interfaces': [...]},
#     ...
#   }
# }

# Easy to validate
assert '10' in output['vlans'], "VLAN 10 missing!"
```

**Why This Matters:** No regex parsing. No fragile text processing. Cisco's parsers do the heavy lifting.

### 3. Test Structure

PyATS tests follow a simple pattern:

```python
import pytest
from pyats.topology import loader

@pytest.fixture(scope='session')
def testbed():
    """Load testbed once per test session"""
    return loader.load('testbed.yaml')

@pytest.fixture
def device(testbed):
    """Connect to a device"""
    dev = testbed.devices['switch-01']
    dev.connect()
    yield dev
    dev.disconnect()

def test_vlan_exists(device):
    """Test: VLAN 10 exists on the device"""
    output = device.parse('show vlan')
    assert '10' in output['vlans'], "VLAN 10 not found!"

def test_vlan_has_name(device):
    """Test: VLAN 10 has correct name"""
    output = device.parse('show vlan')
    assert output['vlans']['10']['name'] == 'DATA', "VLAN 10 name mismatch!"

def test_vlan_has_interfaces(device):
    """Test: VLAN 10 has expected interfaces"""
    output = device.parse('show vlan')
    vlan_10 = output['vlans']['10']['interfaces']
    assert 'Ethernet0/1' in vlan_10, "Ethernet0/1 missing from VLAN 10!"
```

Run all tests with: `pytest test_vlan_validation.py -v`

---

## Before/After Pattern: The Game Changer

This is the pattern that makes PyATS powerful for automation validation:

### Step 1: Baseline (Before Automation)

```python
def capture_baseline(device):
    """Capture network state BEFORE automation"""
    baseline = {
        'vlan_count': len(device.parse('show vlan')['vlans']),
        'routes': device.parse('show ip route')['route'],
        'interfaces_up': count_up_interfaces(device),
        'bgp_neighbors': device.parse('show ip bgp summary')['device']['bgp_id'],
    }
    return baseline
```

### Step 2: Run Automation

```python
def run_automation(device):
    """Your actual automation (provision VLANs, configure BGP, etc.)"""
    from netmiko import ConnectHandler
    
    conn = ConnectHandler(
        device_type='cisco_ios',
        host=device.connections.cli.ip,
        username='admin',
        password='...',
    )
    
    # Your automation commands
    conn.send_config_set([
        'vlan 100',
        'name PROD-VLAN',
        'vlan 101',
        'name PROD-VLAN-2',
    ])
    conn.disconnect()
```

### Step 3: Validate (After Automation)

```python
def validate_automation(device, baseline):
    """Validate network state AFTER automation"""
    after = {
        'vlan_count': len(device.parse('show vlan')['vlans']),
        'routes': device.parse('show ip route')['route'],
        'interfaces_up': count_up_interfaces(device),
    }
    
    # Assert expectations
    assert after['vlan_count'] == baseline['vlan_count'] + 2, "VLAN count mismatch!"
    assert '100' in after['vlan_count'], "VLAN 100 not found!"
    assert '101' in after['vlan_count'], "VLAN 101 not found!"
    assert after['interfaces_up'] == baseline['interfaces_up'], "Interfaces went down!"
    
    return after
```

### Step 4: Complete Test

```python
def test_vlan_provisioning_with_validation(testbed):
    """Complete before/after automation validation"""
    
    device = testbed.devices['switch-01']
    device.connect()
    
    # BEFORE
    baseline = capture_baseline(device)
    print(f"Baseline: {baseline['vlan_count']} VLANs exist")
    
    # DURING (run your automation)
    run_automation(device)
    
    # AFTER
    after = validate_automation(device, baseline)
    print(f"✅ Validation passed! VLANs: {baseline['vlan_count']} → {after['vlan_count']}")
    
    device.disconnect()
```

**Result:** Proof that your automation worked. Not assumption. Proof.

---

## Installation & Setup

### Step 1: Install PyATS

```bash
pip install pyats
```

### Step 2: Create Testbed File

Create `testbed.yaml`:

```yaml
testbed:
  name: "Lab Network"

devices:
  csr1000v:
    type: router
    os: iosxe
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.10
        port: 22
        credentials:
          default:
            username: admin
            password: !vault |
              $ANSIBLE_VAULT;1.1;AES256
              # Your encrypted password here
```

### Step 3: Store Credentials Securely

PyATS integrates with Ansible Vault for credential encryption:

```bash
# Encrypt a password
ansible-vault encrypt_string 'your_password' --name 'password'

# Copy the output into testbed.yaml
```

**Never store plaintext passwords.** PyATS supports vault encryption out of the box.

### Step 4: Test Connection

```python
from pyats.topology import loader

testbed = loader.load('testbed.yaml')
device = testbed.devices['csr1000v']
device.connect()
print(f"✅ Connected to {device.name}")
device.disconnect()
```

---

## Real-World Example: Validate a Configuration Change

### Scenario

You've written Netmiko automation to configure a new interface. You want proof it worked.

### The Test

```python
import pytest
from pyats.topology import loader
from netmiko import ConnectHandler

@pytest.fixture
def testbed():
    return loader.load('testbed.yaml')

@pytest.fixture
def device(testbed):
    dev = testbed.devices['csr1000v']
    dev.connect()
    yield dev
    dev.disconnect()

def test_interface_configuration(device):
    """
    Scenario: Configure Ethernet0/1 with IP 10.0.1.1/24
    Validate: Interface exists, has correct IP, is up
    """
    
    # Connect via Netmiko to configure
    from netmiko import ConnectHandler
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        host=device.connections.cli.ip,
        username='admin',
        password=device.credentials['default'].password,
    )
    
    # Run configuration commands
    commands = [
        'interface Ethernet0/1',
        'ip address 10.0.1.1 255.255.255.0',
        'no shutdown',
    ]
    net_connect.send_config_set(commands)
    net_connect.disconnect()
    
    # NOW VALIDATE WITH PYATS
    # Parse interface configuration
    interfaces = device.parse('show interfaces')
    eth01 = interfaces.get('Ethernet0/1', {})
    
    # Validate interface exists
    assert eth01, "Ethernet0/1 not found!"
    
    # Validate interface is up
    assert eth01.get('enabled') == True, "Interface not enabled!"
    assert eth01.get('oper_status') == 'up', "Interface not up!"
    
    # Parse IP address
    ip_config = device.parse('show ip interface Ethernet0/1')
    ip_addr = ip_config['Ethernet0/1']['ipv4']['10.0.1.1']['ip']
    
    # Validate IP address
    assert ip_addr == '10.0.1.1', f"IP mismatch! Got {ip_addr}"
    
    print("✅ Validation passed: Interface configured correctly")
```

Run this test:

```bash
pytest test_interface_config.py -v

# Output:
# test_interface_configuration PASSED
# ✅ Validation passed: Interface configured correctly
```

---

## Key Takeaways

- ✅ **PyATS is Cisco-native** — Built by engineers who understand network devices
- ✅ **Millions of tests/month** — If Cisco trusts it at that scale, so should you
- ✅ **Before/After validation** — Prove your automation actually worked
- ✅ **No more guessing** — Replace "I think it worked" with "The automation passed 47 validation tests"
- ✅ **Integrates with PRIME Framework** — Perfect fit for Implement and Measure stages
- ✅ **Teams understand it** — Your operations team can write tests too (with knowledge transfer)

---

## Next Steps

1. **[PyATS for Network Validation](./pyats-network-validation.md)** — Deep dive into device parsing and validation patterns
2. **[Building Reliable Automation with PyATS](./building-reliable-automation-with-pyats.md)** — Integration into your automation workflow
3. **[PyATS Documentation](https://pubhub.devnetcloud.com/media/pyats/docs/)** — Official Cisco docs

Or jump straight to:

- **[Nornir Fundamentals](./nornir-fundamentals.md)** — Framework for parallel automation execution
- **[Why Automation Fails](../why-automation-fails.md)** — Understand how PyATS prevents failures

---

> **Production automation without validation is guesswork.** PyATS transforms validation from manual checklist to automated proof. Enterprise teams use it millions of times per month for good reason.

