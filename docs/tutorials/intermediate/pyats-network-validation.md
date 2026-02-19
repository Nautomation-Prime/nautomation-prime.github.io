---
title: PyATS for Network Validation - Device Testing Patterns
description: Master PyATS device parsing, testbed configuration, and validation patterns. Learn how to capture network state and validate automation changes in production.
tags:
  - PyATS
  - Network Validation
  - Device Parsing
  - Testing
  - Cisco
---

## From Basics to Production Patterns

In the [PyATS Fundamentals](./pyats-fundamentals.md) guide, you learned the core concepts. Now let's build practical patterns you'll use in production.

This guide focuses on:

- Real device parsing (what does the data actually look like?)
- Designing validation checkpoints (what should you validate?)
- Handling common pitfalls (dealing with failures, timeouts, credential issues)
- Scaling across multiple devices

---

## Deep Dive: Device Parsing

### What PyATS Parsing Actually Returns

When you call `device.parse('show vlan')`, you don't get text. You get structured data:

```python
from pyats.topology import loader

testbed = loader.load('testbed.yaml')
device = testbed.devices['switch-01']
device.connect()

# Parse VLAN output
vlan_output = device.parse('show vlan')

# What does it look like?
import json
print(json.dumps(vlan_output, indent=2))
```

**Output:**

```json
{
  "vlans": {
    "1": {
      "name": "default",
      "status": "active",
      "interfaces": {
        "Ethernet1/1": {
          "interface_mode": "routed"
        },
        "Ethernet1/2": {
          "interface_mode": "static_access"
        }
      }
    },
    "10": {
      "name": "DATA",
      "status": "active",
      "interfaces": {
        "Ethernet1/3": {
          "interface_mode": "static_access"
        },
        "Ethernet1/4": {
          "interface_mode": "static_access"
        }
      }
    }
  }
}
```

**Key Point:** Structured, not text. Easy to validate.

### Common Commands & Their Output Structure

#### Show VLAN

```python
vlans = device.parse('show vlan')
# Access specific VLAN
vlan_10 = vlans['vlans']['10']
print(vlan_10['name'])  # "DATA"
print(vlan_10['status'])  # "active"
print(list(vlan_10['interfaces'].keys()))  # ['Ethernet1/3', 'Ethernet1/4']
```

#### Show IP Route

```python
routes = device.parse('show ip route')
# Structure varies by OS, but generally:
# routes['route'] contains the routing table
for prefix, route_data in routes['route'].items():
    print(f"{prefix}: {route_data}")
# Output:
# 10.0.0.0/24: {'': [{'metric': '0', 'next_hop': {...}}]}
```

#### Show Interfaces

```python
interfaces = device.parse('show interfaces')
# interfaces contains all interface data
interfaces_up = [
    name for name, data in interfaces.items() 
    if data.get('oper_status') == 'up'
]
print(f"Interfaces up: {len(interfaces_up)}")
```

#### Show IP BGP Summary

```python
bgp = device.parse('show ip bgp summary')
# BGP neighbor data
neighbors = bgp['device']['bgp_id']['65000']['neighbors']
for neighbor_ip, neighbor_data in neighbors.items():
    state = neighbor_data['state']
    print(f"Neighbor {neighbor_ip}: {state}")
    # Output: "Neighbor 10.0.0.1: Established"
```

### Finding Available Parsers

Not all commands are available. Check which ones Cisco supports:

```bash
# List all available parsers
from genie.libs.parser.utils.common import ParserLookup
from pyats.topology import loader

testbed = loader.load('testbed.yaml')
device = testbed.devices['switch-01']

# Get available commands for this device
lookup = ParserLookup(device.os)
for command in sorted(lookup.keys()):
    if 'vlan' in command.lower():
        print(command)

# Output examples:
# show vlan
# show vlan access-log
# show vlan id
```

Or visit [Cisco's Parser Index](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers) for the full list.

---

## Real-World Validation Patterns

### Pattern 1: Configuration Compliance Check

**Scenario:** Ensure all access ports are in the correct VLAN

```python
def test_access_port_compliance(device):
    """
    Validate: All access ports must be in VLAN 10 (DATA)
    Except: Port Et1/48 which should be in VLAN 20 (MGMT)
    """
    
    vlan_data = device.parse('show vlan')
    
    required_config = {
        '10': ['Ethernet1/1', 'Ethernet1/2', 'Ethernet1/3', 'Ethernet1/4'],
        '20': ['Ethernet1/48'],
    }
    
    for vlan_id, required_ports in required_config.items():
        actual_ports = list(vlan_data['vlans'][vlan_id]['interfaces'].keys())
        
        for port in required_ports:
            assert port in actual_ports, f"{port} missing from VLAN {vlan_id}!"
        
        # Also warn about unexpected ports
        unexpected = set(actual_ports) - set(required_ports)
        if unexpected:
            print(f"⚠️  Warning: Unexpected ports in VLAN {vlan_id}: {unexpected}")
    
    print("✅ VLAN compliance check passed")
```

### Pattern 2: Interface Health Check

**Scenario:** After deploying new infrastructure, validate all interfaces are up and operational

```python
def test_interface_health(device, expected_up_count=48):
    """
    Validate: Expected number of interfaces are operational
    Check: No disabled ports, no down ports, no errors
    """
    
    interfaces = device.parse('show interfaces')
    
    interfaces_up = 0
    interfaces_errors = 0
    interfaces_down = []
    
    for iface_name, iface_data in interfaces.items():
        # Skip loopbacks and management interfaces for this check
        if 'Loopback' in iface_name or 'Management' in iface_name:
            continue
        
        # Count up interfaces
        if iface_data.get('oper_status') == 'up':
            interfaces_up += 1
        else:
            interfaces_down.append(iface_name)
        
        # Check for errors
        input_errors = iface_data.get('counters', {}).get('in_errors', 0)
        output_errors = iface_data.get('counters', {}).get('out_errors', 0)
        
        if input_errors > 0 or output_errors > 0:
            interfaces_errors += 1
            print(f"⚠️  {iface_name}: errors detected (in:{input_errors}, out:{output_errors})")
    
    # Assertions
    assert interfaces_up >= expected_up_count, \
        f"Expected {expected_up_count} interfaces up, got {interfaces_up}"
    
    assert interfaces_errors == 0, \
        f"Found {interfaces_errors} interfaces with errors"
    
    assert len(interfaces_down) == 0, \
        f"Expected all interfaces up, but these are down: {interfaces_down}"
    
    print(f"✅ Interface health check passed ({interfaces_up} interfaces up)")
```

### Pattern 3: Routing Validation

**Scenario:** Ensure critical routes exist after a network change

```python
def test_critical_routes(device):
    """
    Validate: Critical routes exist and are reachable
    """
    
    routes = device.parse('show ip route')
    
    required_routes = [
        '10.0.0.0/8',      # Corporate network
        '192.168.0.0/16',  # Management network
        '172.16.0.0/12',   # WAN network
    ]
    
    available_routes = list(routes['route'].keys())
    
    for required in required_routes:
        assert required in available_routes, \
            f"Critical route {required} not found in routing table!"
        
        route_info = routes['route'][required]
        print(f"✅ Route {required} exists")
    
    print("✅ Routing validation passed")
```

### Pattern 4: BGP Neighbor Validation

**Scenario:** Ensure all expected BGP neighbors are established

```python
def test_bgp_neighbors(device):
    """
    Validate: All BGP neighbors are in 'Established' state
    """
    
    bgp = device.parse('show ip bgp summary')
    
    # Get neighbors
    neighbors = bgp['device']['bgp_id']['65000']['neighbors']
    
    required_states = {
        '10.0.1.1': 'Established',     # Primary ISP peer
        '10.0.2.1': 'Established',     # Secondary ISP peer
        '192.168.1.2': 'Established',  # Internal peer
    }
    
    for neighbor_ip, expected_state in required_states.items():
        actual_neighbor = neighbors.get(neighbor_ip, {})
        actual_state = actual_neighbor.get('state', 'Down')
        
        assert actual_state == expected_state, \
            f"BGP neighbor {neighbor_ip}: expected {expected_state}, got {actual_state}"
        
        # Check message counts
        messages_received = actual_neighbor.get('msg_rcvd', 0)
        assert messages_received > 0, \
            f"BGP neighbor {neighbor_ip}: no messages received!"
        
        print(f"✅ BGP neighbor {neighbor_ip}: {actual_state} ({messages_received} messages)")
    
    print("✅ BGP validation passed")
```

---

## Handling Real-World Challenges

### Challenge 1: Device Connection Timeouts

Some devices are slow or unreliable. Handle gracefully:

```python
import pytest
from pyats.topology import loader

@pytest.fixture
def device_with_timeout(testbed):
    """Connect with timeout handling"""
    device = testbed.devices['slow_switch']
    
    try:
        device.connect(timeout=30)  # 30-second timeout
        yield device
    except Exception as e:
        pytest.fail(f"Failed to connect to device: {e}")
    finally:
        try:
            device.disconnect()
        except:
            pass  # Connection already closed or never opened

def test_with_retry(device_with_timeout):
    """Retry parsing if device is slow"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            vlan_data = device_with_timeout.parse('show vlan')
            break  # Success
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                pytest.fail(f"Failed after {max_retries} retries: {e}")
            print(f"⚠️  Retry {retry_count}/{max_retries}")
```

### Challenge 2: Incomplete Device Data

Some commands might fail on some devices:

```python
def test_with_graceful_fallback(device):
    """
    Validate routing even if BGP isn't configured
    """
    
    # Try to get BGP data, but don't fail if not available
    bgp_data = None
    try:
        bgp_data = device.parse('show ip bgp summary')
    except Exception:
        print("⚠️  BGP not configured on this device")
    
    # Validate routing (always available)
    routes = device.parse('show ip route')
    assert routes is not None, "No routing table?"
    
    # Optional: validate BGP only if available
    if bgp_data:
        neighbors = bgp_data['device']['bgp_id']['65000']['neighbors']
        assert len(neighbors) > 0, "BGP neighbors not established"
    
    print("✅ Validation passed")
```

### Challenge 3: Credential Management

Always use vault encryption:

```python
# testbed.yaml
testbed:
  name: "Production"

devices:
  switch-01:
    type: switch
    os: ios
    connections:
      cli:
        protocol: ssh
        ip: 10.1.1.1
        port: 22
        credentials:
          default:
            username: admin
            password: !vault |
              $ANSIBLE_VAULT;1.1;AES256;secrets
              # Encrypted password
```

In your test, credentials are automatically decrypted:

```python
def test_with_vault_credentials(device):
    """Credentials are automatically decrypted from vault"""
    # No need to pass password - PyATS handles it
    device.connect()
    # ... run your tests
    device.disconnect()
```

---

## Scaling: Testing Multiple Devices

### Pattern: Multi-Device Validation

```python
import pytest
from pyats.topology import loader

@pytest.fixture(scope='session')
def testbed():
    return loader.load('testbed.yaml')

@pytest.mark.parametrize('device_name', ['switch-01', 'switch-02', 'switch-03'])
def test_vlan_on_all_switches(testbed, device_name):
    """
    Run the same test on all switches
    PyTest will run this 3 times (once per device)
    """
    device = testbed.devices[device_name]
    device.connect()
    
    # Validate VLAN 10 exists
    vlans = device.parse('show vlan')
    assert '10' in vlans['vlans'], f"VLAN 10 missing on {device_name}!"
    
    device.disconnect()
```

Run it:

```bash
pytest test_multi_device.py -v

# Output:
# test_vlan_on_all_switches[switch-01] PASSED
# test_vlan_on_all_switches[switch-02] PASSED
# test_vlan_on_all_switches[switch-03] PASSED
```

### Pattern: Validate Configuration Consistency Across Devices

```python
def test_consistent_vlan_config(testbed):
    """
    Ensure all switches have the same VLAN configuration
    """
    
    all_devices_vlans = {}
    
    # Collect VLAN data from all switches
    for device_name in ['switch-01', 'switch-02', 'switch-03']:
        device = testbed.devices[device_name]
        device.connect()
        
        vlans = device.parse('show vlan')
        all_devices_vlans[device_name] = set(vlans['vlans'].keys())
        
        device.disconnect()
    
    # Compare
    reference_vlans = all_devices_vlans['switch-01']
    
    for device_name, vlans in all_devices_vlans.items():
        assert vlans == reference_vlans, \
            f"{device_name} VLAN config differs from switch-01!"
    
    print("✅ All switches have consistent VLAN configuration")
```

---

## Integration with Automation

### Before/After Pattern (Complete Example)

```python
from pyats.topology import loader
from netmiko import ConnectHandler
import pytest

@pytest.fixture
def testbed():
    return loader.load('testbed.yaml')

@pytest.fixture
def device(testbed):
    dev = testbed.devices['switch-01']
    dev.connect()
    yield dev
    dev.disconnect()

def capture_baseline(device):
    """Capture state BEFORE automation"""
    return {
        'vlans': set(device.parse('show vlan')['vlans'].keys()),
        'interfaces_up': sum(
            1 for iface_data in device.parse('show interfaces').values()
            if iface_data.get('oper_status') == 'up'
        ),
    }

def run_automation(device):
    """Execute your actual automation"""
    from netmiko import ConnectHandler
    
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        host=device.connections.cli.ip,
        username='admin',
        password='...',
    )
    
    # Configure new VLAN
    net_connect.send_config_set([
        'vlan 100',
        'name AUTOMATION-TEST',
    ])
    net_connect.disconnect()

def validate_automation(device, baseline):
    """Validate state AFTER automation"""
    after = {
        'vlans': set(device.parse('show vlan')['vlans'].keys()),
        'interfaces_up': sum(
            1 for iface_data in device.parse('show interfaces').values()
            if iface_data.get('oper_status') == 'up'
        ),
    }
    
    # Validate changes
    new_vlans = after['vlans'] - baseline['vlans']
    assert '100' in new_vlans, "VLAN 100 not created!"
    assert after['interfaces_up'] == baseline['interfaces_up'], \
        "Interfaces changed state!"
    
    return after

def test_vlan_automation_with_validation(device):
    """Complete automation with before/after validation"""
    
    baseline = capture_baseline(device)
    print(f"Before: {len(baseline['vlans'])} VLANs, {baseline['interfaces_up']} interfaces up")
    
    run_automation(device)
    
    after = validate_automation(device, baseline)
    print(f"After: {len(after['vlans'])} VLANs, {after['interfaces_up']} interfaces up")
    print("✅ Automation validated successfully")
```

---

## Testing Tips & Best Practices

### ✅ Do's

- ✅ **Capture baseline before automation** — You can't validate change without knowing the starting state
- ✅ **Test in non-critical environments first** — Lab or staging before production
- ✅ **Use fixtures for device connections** — PyTest fixtures handle setup/teardown automatically
- ✅ **Parameterize multi-device tests** — Run the same test on different devices
- ✅ **Document what you're validating** — Clear test names explain intent
- ✅ **Log results verbosely** — Future you will appreciate the detail

### ❌ Don'ts

- ❌ **Hardcode IP addresses** — Use testbed files
- ❌ **Store credentials in test files** — Use vault encryption
- ❌ **Assume device behavior** — Parse and validate actual state
- ❌ **Skip error handling** — Devices fail. Handle it gracefully.
- ❌ **Test only happy paths** — What happens when a device is unreachable?

---

## Next Step

Ready to integrate PyATS into your actual automation workflow?

**[Building Reliable Automation with PyATS](./building-reliable-automation-with-pyats.md)** — Learn how PyATS integrates with Netmiko, Nornir, and your PRIME Framework engagements.

---

> **Structured parsing + validation = confidence.** When you can test network state programmatically, you can automate with certainty, not hope.

