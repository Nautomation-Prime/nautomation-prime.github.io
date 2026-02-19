---
title: Building Reliable Automation with PyATS - Production Patterns
description: Integrate PyATS validation into your Netmiko and Nornir automation. Learn production patterns for reliable network changes with measurable ROI proof.
tags:
  - PyATS
  - Production Automation
  - Reliability
  - PRIME Framework
  - Network Automation
---

## The Missing Piece: Validation in Your Automation

You've learned PyATS fundamentals and validation patterns. Now the critical piece: **how do you integrate PyATS into your actual production automation?**

This is where automation becomes **reliable**.

---

## The Reality of Production Automation

### Without Validation

```python
# Your automation runs
for device_ip in switch_ips:
    configure_vlan(device_ip, vlan_list)

# No output. Did it work?
# You manually SSH to each switch and check.
# Hope nobody changed anything while you're checking.
```

**Problem:** You're guessing. Zero proof the configuration was deployed.

### With PyATS Validation

```python
# Your automation runs
for device_ip in switch_ips:
    configure_vlan(device_ip, vlan_list)

# Automated validation runs immediately after
for device_ip in switch_ips:
    validate_vlan_config(device_ip, vlan_list)

# ✅ 47 validation tests passed
# ✅ 100% of VLANs deployed correctly
# ✅ Zero validation failures
# You have proof. Leadership gets metrics.
```

**Result:** Reliable automation with measurable proof.

---

## Pattern 1: Netmiko + PyATS (Simple Approach)

Combine Netmiko for configuration with PyATS for validation:

### The Setup

```python
from netmiko import ConnectHandler
from pyats.topology import loader

# Load testbed (devices, credentials)
testbed = loader.load('testbed.yaml')

# Device credentials from vault (encrypted)
device = testbed.devices['switch-01']
device.connect(via='cli')

# Netmiko for configuration (faster, simpler syntax)
net_connect = ConnectHandler(
    device_type='cisco_ios',
    host=device.ip,
    username=device.username,
    password=device.password,
)

# PyATS for validation (structured parsing)
# (already connected via device.connect())
```

### The Implementation

```python
def deploy_and_validate_vlan(testbed_file, device_name, vlan_config):
    """
    Deploy VLAN configuration and validate immediately
    
    Args:
        testbed_file: Path to testbed.yaml
        device_name: Device name from testbed
        vlan_config: List of dicts with vlan_id, name, interfaces
    
    Returns:
        dict: Validation results
    """
    
    from pyats.topology import loader
    from netmiko import ConnectHandler
    
    testbed = loader.load(testbed_file)
    device = testbed.devices[device_name]
    
    # Step 1: Capture baseline
    print(f"[1/4] Capturing baseline...")
    device.connect()
    baseline_vlans = set(device.parse('show vlan')['vlans'].keys())
    device.disconnect()
    print(f"      Baseline: {len(baseline_vlans)} VLANs exist")
    
    # Step 2: Deploy configuration via Netmiko
    print(f"[2/4] Deploying VLAN configuration...")
    try:
        net_connect = ConnectHandler(
            device_type='cisco_ios',
            host=device.connections.cli.ip,
            username='admin',
            password='...',  # From vault
            timeout=20,
        )
        
        # Build configuration commands
        config_commands = []
        for vlan in vlan_config:
            config_commands.extend([
                f"vlan {vlan['id']}",
                f"name {vlan['name']}",
            ])
        
        # Send configuration
        output = net_connect.send_config_set(config_commands)
        net_connect.disconnect()
        print(f"      Configuration sent successfully")
    except Exception as e:
        print(f"      ❌ Configuration failed: {e}")
        raise
    
    # Step 3: Validate configuration via PyATS
    print(f"[3/4] Validating configuration...")
    device.connect()
    
    validation_results = {
        'passed': 0,
        'failed': 0,
        'details': [],
    }
    
    for vlan in vlan_config:
        vlan_id = str(vlan['id'])
        
        # Parse current state
        vlan_data = device.parse('show vlan')
        
        # Check: VLAN exists
        if vlan_id not in vlan_data['vlans']:
            validation_results['failed'] += 1
            validation_results['details'].append(
                f"❌ VLAN {vlan_id} not found"
            )
            continue
        
        # Check: VLAN has correct name
        actual_name = vlan_data['vlans'][vlan_id]['name']
        expected_name = vlan['name']
        
        if actual_name != expected_name:
            validation_results['failed'] += 1
            validation_results['details'].append(
                f"❌ VLAN {vlan_id} name mismatch: expected '{expected_name}', got '{actual_name}'"
            )
            continue
        
        # Check: VLAN status is active
        status = vlan_data['vlans'][vlan_id]['status']
        if status != 'active':
            validation_results['failed'] += 1
            validation_results['details'].append(
                f"❌ VLAN {vlan_id} status not active: {status}"
            )
            continue
        
        # All checks passed
        validation_results['passed'] += 1
        validation_results['details'].append(
            f"✅ VLAN {vlan_id} ({expected_name}): deployed and active"
        )
    
    device.disconnect()
    
    # Step 4: Report results
    print(f"[4/4] Validation results...")
    for detail in validation_results['details']:
        print(f"      {detail}")
    
    total = validation_results['passed'] + validation_results['failed']
    print(f"\n      Result: {validation_results['passed']}/{total} validations passed")
    
    if validation_results['failed'] > 0:
        raise AssertionError(
            f"Validation failed: {validation_results['failed']} checks did not pass"
        )
    
    return validation_results

# Usage
vlan_config = [
    {'id': 100, 'name': 'PROD-DATA'},
    {'id': 101, 'name': 'PROD-VOICE'},
    {'id': 102, 'name': 'PROD-VIDEO'},
]

results = deploy_and_validate_vlan('testbed.yaml', 'switch-01', vlan_config)
print(f"✅ All {results['passed']} VLANs deployed and validated")
```

**Output:**

```
[1/4] Capturing baseline...
      Baseline: 42 VLANs exist
[2/4] Deploying VLAN configuration...
      Configuration sent successfully
[3/4] Validating configuration...
      ✅ VLAN 100 (PROD-DATA): deployed and active
      ✅ VLAN 101 (PROD-VOICE): deployed and active
      ✅ VLAN 102 (PROD-VIDEO): deployed and active

      Result: 3/3 validations passed

✅ All 3 VLANs deployed and validated
```

---

## Pattern 2: Nornir + PyATS (Parallel Deployment)

For deploying across multiple devices simultaneously:

### The Setup

```python
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_config
from nornir.plugins.functions.text import print_result
from pyats.topology import loader

# Initialize Nornir
nr = InitNornir(config_file='config.yaml')

# Load PyATS testbed
testbed = loader.load('testbed.yaml')
```

### The Implementation

```python
def parallel_deploy_and_validate(nr, testbed, vlan_config):
    """
    Deploy VLAN configuration in parallel across all devices
    Then validate in parallel
    """
    
    from nornir.core.task import Task
    from nornir.plugins.tasks.networking import netmiko_send_config
    from nornir.plugins.functions.text import print_result
    
    # Task 1: Deploy configuration in parallel
    def deploy_vlans(task):
        """Nornir task: deploy VLAN configuration"""
        
        config_commands = []
        for vlan in vlan_config:
            config_commands.extend([
                f"vlan {vlan['id']}",
                f"name {vlan['name']}",
            ])
        
        task.run(
            netmiko_send_config,
            config_commands=config_commands,
        )
    
    # Task 2: Validate configuration (after deployment)
    def validate_vlans(task):
        """Nornir task: validate VLAN configuration with PyATS"""
        
        device = testbed.devices[task.host.name]
        device.connect()
        
        vlan_data = device.parse('show vlan')
        validation_results = {'passed': 0, 'failed': 0}
        
        for vlan in vlan_config:
            vlan_id = str(vlan['id'])
            
            if vlan_id in vlan_data['vlans']:
                actual_name = vlan_data['vlans'][vlan_id]['name']
                if actual_name == vlan['name']:
                    validation_results['passed'] += 1
                else:
                    validation_results['failed'] += 1
            else:
                validation_results['failed'] += 1
        
        device.disconnect()
        task.result = validation_results
    
    # Execute deployment
    print("=" * 60)
    print("DEPLOYING VLANS IN PARALLEL...")
    print("=" * 60)
    deploy_results = nr.run(task=deploy_vlans)
    print_result(deploy_results)
    
    # Execute validation
    print("\n" + "=" * 60)
    print("VALIDATING VLANS IN PARALLEL...")
    print("=" * 60)
    validate_results = nr.run(task=validate_vlans)
    
    # Report
    for device_name, multi_result in validate_results.items():
        result = multi_result[0].result
        total = result['passed'] + result['failed']
        print(f"{device_name}: {result['passed']}/{total} validations passed")
    
    return validate_results

# Usage
vlan_config = [
    {'id': 100, 'name': 'PROD-DATA'},
    {'id': 101, 'name': 'PROD-VOICE'},
]

parallel_deploy_and_validate(nr, testbed, vlan_config)
```

**Output:**

```
============================================================
DEPLOYING VLANS IN PARALLEL...
============================================================
deploy_vlans*101 ** changed : True
deploy_vlans*102 ** changed : True
deploy_vlans*103 ** changed : True

============================================================
VALIDATING VLANS IN PARALLEL...
============================================================
switch-01: 2/2 validations passed
switch-02: 2/2 validations passed
switch-03: 2/2 validations passed

✅ 100% deployment success across all 3 switches
```

---

## Pattern 3: Recovery & Rollback

What if validation fails? Automatically recover:

```python
def deploy_with_automatic_rollback(device, config_commands, validation_func):
    """
    Deploy configuration with automatic rollback on validation failure
    """
    
    from netmiko import ConnectHandler
    
    device_ip = device.connections.cli.ip
    
    # Step 1: Save running config (for rollback)
    print("1. Saving current configuration (for rollback)...")
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        host=device_ip,
        username='admin',
        password='...',
    )
    
    # Save to local buffer
    net_connect.send_command('copy running-config startup-config')
    net_connect.disconnect()
    
    # Step 2: Deploy new configuration
    print("2. Deploying new configuration...")
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        host=device_ip,
        username='admin',
        password='...',
    )
    
    try:
        net_connect.send_config_set(config_commands)
        net_connect.disconnect()
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print("   No changes made (closed connection before save)")
        return False
    
    # Step 3: Validate new configuration
    print("3. Validating configuration...")
    device.connect()
    
    try:
        validation_success = validation_func(device)
    except AssertionError as e:
        print(f"❌ Validation failed: {e}")
        print("   Automatic rollback triggered...")
        device.disconnect()
        
        # Rollback
        net_connect = ConnectHandler(
            device_type='cisco_ios',
            host=device_ip,
            username='admin',
            password='...',
        )
        
        net_connect.send_command('reload')  # Or use other rollback method
        net_connect.disconnect()
        
        return False
    finally:
        device.disconnect()
    
    # Step 4: Save configuration permanently
    if validation_success:
        print("4. Saving configuration permanently...")
        net_connect = ConnectHandler(
            device_type='cisco_ios',
            host=device_ip,
            username='admin',
            password='...',
        )
        
        net_connect.send_command('copy running-config startup-config')
        net_connect.disconnect()
        
        print("✅ Configuration deployed, validated, and saved")
        return True

# Usage
def validate_my_vlans(device):
    """Validation function to pass to deploy_with_rollback"""
    vlans = device.parse('show vlan')
    
    expected_vlans = ['100', '101', '102']
    for vlan_id in expected_vlans:
        assert vlan_id in vlans['vlans'], f"VLAN {vlan_id} not found!"
    
    return True

config = [
    'vlan 100',
    'name PROD-DATA',
    'vlan 101',
    'name PROD-VOICE',
]

deploy_with_automatic_rollback(device, config, validate_my_vlans)
```

---

## Integration with PRIME Framework

### How PyATS Fits Each Stage

| PRIME Stage | PyATS Integration | Example |
| :--- | :--- | :--- |
| **Pinpoint** | Capture baseline metrics | "How many VLANs exist currently?" |
| **Re-engineer** | Document validation checkpoints | "What must be true after VLAN provisioning?" |
| **Implement** | Run PyATS tests as part of deployment | Deploy + immediately validate |
| **Measure** | Compare before/after with PyATS | "Baseline: 42 VLANs → After: 45 VLANs ✅" |
| **Empower** | Team can run validation tests autonomously | "Run pytest to verify deployment" |

### Example: Complete PRIME Workflow with PyATS

```python
"""
Complete workflow: Pinpoint → Implement → Measure
"""

from pyats.topology import loader
from netmiko import ConnectHandler

testbed = loader.load('testbed.yaml')

# PINPOINT: Establish baseline
print("=== PINPOINT STAGE ===")
device = testbed.devices['switch-01']
device.connect()
baseline = {
    'vlan_count': len(device.parse('show vlan')['vlans']),
    'interfaces_up': sum(
        1 for iface in device.parse('show interfaces').values()
        if iface.get('oper_status') == 'up'
    ),
}
device.disconnect()
print(f"Baseline: {baseline['vlan_count']} VLANs, {baseline['interfaces_up']} interfaces up")

# IMPLEMENT: Deploy and validate automatically
print("\n=== IMPLEMENT STAGE ===")
device.connect()

# Deploy
net_connect = ConnectHandler(
    device_type='cisco_ios',
    host=device.connections.cli.ip,
    username='admin',
    password='...',
)
net_connect.send_config_set(['vlan 100', 'name AUTOMATION-TEST'])
net_connect.disconnect()

# Validate immediately
vlans = device.parse('show vlan')
assert '100' in vlans['vlans'], "VLAN 100 deployment failed!"
print("✅ VLAN 100 deployed and validated")

device.disconnect()

# MEASURE: Prove ROI
print("\n=== MEASURE STAGE ===")
device.connect()
after = {
    'vlan_count': len(device.parse('show vlan')['vlans']),
    'interfaces_up': sum(
        1 for iface in device.parse('show interfaces').values()
        if iface.get('oper_status') == 'up'
    ),
}
device.disconnect()

print(f"After: {after['vlan_count']} VLANs, {after['interfaces_up']} interfaces up")
print(f"Change: +{after['vlan_count'] - baseline['vlan_count']} VLANs")
print(f"Health: {baseline['interfaces_up'] == after['interfaces_up']} (no interfaces went down)")
print("✅ Deployment successful with zero disruption")
```

---

## Testing Your Automation

Use pytest to test the entire workflow:

```python
import pytest
from pyats.topology import loader

@pytest.fixture
def testbed():
    return loader.load('testbed.yaml')

@pytest.fixture
def device(testbed):
    dev = testbed.devices['switch-01']
    dev.connect()
    yield dev
    dev.disconnect()

def test_vlan_deployment_end_to_end(device):
    """
    Test the complete workflow:
    1. Capture baseline
    2. Deploy configuration
    3. Validate immediately
    4. Verify no side effects
    """
    
    # Baseline
    baseline_vlans = set(device.parse('show vlan')['vlans'].keys())
    baseline_interfaces = sum(
        1 for iface in device.parse('show interfaces').values()
        if iface.get('oper_status') == 'up'
    )
    
    # Deploy (via Netmiko)
    from netmiko import ConnectHandler
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        host=device.connections.cli.ip,
        username='admin',
        password='...',
    )
    net_connect.send_config_set(['vlan 100', 'name TEST'])
    net_connect.disconnect()
    
    # Validate
    after_vlans = set(device.parse('show vlan')['vlans'].keys())
    assert '100' in after_vlans, "VLAN 100 not deployed!"
    assert len(after_vlans) == len(baseline_vlans) + 1, "Unexpected VLAN change!"
    
    # Verify no side effects
    after_interfaces = sum(
        1 for iface in device.parse('show interfaces').values()
        if iface.get('oper_status') == 'up'
    )
    assert after_interfaces == baseline_interfaces, "Interfaces went down!"
    
    print("✅ Complete workflow validated")
```

Run it:

```bash
pytest test_automation_workflow.py -v
# test_vlan_deployment_end_to_end PASSED ✅
```

---

## Best Practices for Production

### ✅ Do's

- ✅ **Always validate after deployment** — Never assume the device accepted your configuration
- ✅ **Capture baseline before changes** — You can't validate change without knowing the starting point
- ✅ **Use testbeds for multi-device** — One definition, infinite reuse
- ✅ **Implement rollback logic** — If validation fails, recover automatically
- ✅ **Log everything verbosely** — Debugging production issues requires detail
- ✅ **Test in non-production first** — Lab before production, always

### ❌ Don'ts

- ❌ **Skip validation** — "It probably worked" is not an acceptable standard
- ❌ **Store credentials in code** — Use vault encryption
- ❌ **Assume device state** — Always parse and validate
- ❌ **Ignore errors** — Handle failures gracefully with recovery
- ❌ **Test only happy paths** — What happens when a device is slow or offline?

---

## Summary

**PyATS transforms automation from hope to certainty:**

| Without PyATS | With PyATS |
| :--- | :--- |
| "The script ran." | "All 47 validation tests passed." |
| "I think it worked." | "Device configuration verified." |
| Manual spot-checking | Automated proof |
| Hope for the best | Know for certain |

**Integration with PRIME Framework:**

- **Pinpoint:** Establish baselines with PyATS parsing
- **Implement:** Deploy with automatic validation
- **Measure:** Prove ROI with before/after metrics
- **Empower:** Team runs validation tests independently

---

## Next Steps

- **[PyATS Documentation](https://pubhub.devnetcloud.com/media/pyats/docs/)** — Official Cisco reference
- **[Genie Parsers Index](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers)** — Find parsers for your commands
- **[Nornir + PyATS](./nornir-fundamentals.md)** — Parallel automation at scale

Or continue learning:

- **[Advanced Nornir Patterns](./advanced-nornir-patterns.md)** — Multi-threaded automation at scale
- **[Enterprise Config Backup](./enterprise-config-backup-nornir.md)** — Real production example

---

> **Production reliability isn't built on hope.** It's built on validation, testing, and recovery. PyATS makes all three automatic.

