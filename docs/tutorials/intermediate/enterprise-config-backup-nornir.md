---
title: Enterprise Config Backup Deep Dive - Building a Real System
description: Build a production-grade config backup system with Nornir including database integration, change detection, compliance checking, and reporting.
tags:
  - Intermediate
  - Nornir
  - Advanced Tasks
  - Database
  - Compliance
  - Tutorial
---

# Enterprise Config Backup Deep Dive: Building a Real System

## "From Simple Backup to Automated Compliance — Real Enterprise Architecture"

In [Tutorial #2](./nornir-fundamentals.md), you built a parallel config backup system. It's functional, but it's missing critical enterprise features:

- **Where are historical backups stored?** (Text files alone don't scale)
- **Can you detect when configs change?** (Compliance auditing)
- **Can you see which devices are non-compliant?** (Reporting)
- **How do you retrieve a specific backup from 6 months ago?** (Archival)

In this tutorial, we'll build a **production-grade backup system** with database integration, change detection, and compliance reporting.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ Multi-step task composition (tasks calling other tasks)
- ✅ Database integration with SQLite
- ✅ Config comparison and change detection
- ✅ Compliance checking and scoring
- ✅ Professional result processing and reporting
- ✅ Production patterns for Nornir systems
- ✅ Building reusable task libraries
- ✅ Troubleshooting complex workflows

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [Tutorial #2: Nornir Fundamentals](./nornir-fundamentals.md)** — Understand tasks, inventory, and parallel execution
- ✅ Basic SQL (SELECT, CREATE TABLE)
- ✅ Understanding of Python dictionaries and JSON
- ✅ File I/O and comparison concepts

### Required Software
```bash
# Add to your existing Tutorial #2 environment
pip install sqlite3  # Usually built-in
```

SQLite3 is included in Python by default, so you should be good!

---

## 🏗️ Architecture Overview

Before writing code, let's understand the system:

```
Nornir Task Flow:

1. backup_config (task)
   └─ Retrieve running config from device

2. save_config (task)
   └─ Write to database & filesystem

3. compare_configs (task)
   └─ Compare with previous backup
   └─ Detect changes

4. compliance_check (task)
   └─ Compare against standards
   └─ Generate compliance score

5. generate_report (task)
   └─ Create summary report
   └─ Database logging
```

**Key difference from Tutorial #2:** Each device's data flows through a 5-step pipeline.

---

## 🗄️ Database Schema

First, we need a database to store backup metadata. Create `init_db.py`:

```python
"""
Initialize the backup database schema
Run once: python init_db.py
"""

import sqlite3
import os

def init_database(db_file='backup.db'):
    """Create database tables for backup tracking"""
    
    # Create connection
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Table 1: Backup metadata
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT NOT NULL,
        backup_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        config_size INTEGER,
        config_hash TEXT,
        changed BOOLEAN DEFAULT 0,
        status TEXT,
        filepath TEXT
    )
    ''')
    
    # Table 2: Compliance history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compliance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT NOT NULL,
        check_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        compliance_score REAL,
        issues TEXT,
        status TEXT
    )
    ''')
    
    # Table 3: Changes detected
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT NOT NULL,
        change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        previous_backup_id INTEGER,
        new_backup_id INTEGER,
        lines_added INTEGER,
        lines_removed INTEGER,
        summary TEXT,
        FOREIGN KEY(previous_backup_id) REFERENCES backups(id),
        FOREIGN KEY(new_backup_id) REFERENCES backups(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized: {db_file}")

if __name__ == "__main__":
    init_database()
```

**Run this once:**
```bash
python init_db.py
```

---

## 🚀 The Complete Production Script

Create `tasks/enterprise_backup.py` with advanced task composition:

```python
"""
Enterprise Configuration Backup with Nornir
Includes: Database logging, change detection, compliance checking
"""

import sqlite3
import hashlib
import difflib
import os
from datetime import datetime
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# TASK 1: Retrieve Configuration
# ============================================================================

@task
def backup_config(task: Task) -> Result:
    """
    Retrieve running configuration from device
    
    Returns config data without saving (that's Task 2)
    """
    device_name = task.host.name
    device_ip = task.host.hostname
    
    logger.info(f"[{device_name}] Retrieving configuration...")
    
    try:
        result = task.run(
            netmiko_send_command,
            command_string="show running-config",
            use_textfsm=False,
            name="Get running config"
        )
        
        config = result[0].result
        
        if isinstance(config, str) and len(config) > 100:
            # Calculate config hash for change detection
            config_hash = hashlib.sha256(config.encode()).hexdigest()
            logger.info(f"[{device_name}] ✓ Retrieved {len(config):,} bytes")
            
            return Result(
                host=task.host,
                result={
                    'success': True,
                    'config': config,
                    'size': len(config),
                    'hash': config_hash,
                    'timestamp': datetime.now()
                }
            )
        else:
            logger.warning(f"[{device_name}] Config data invalid")
            return Result(
                host=task.host,
                result={'success': False, 'error': 'Invalid config data'},
                failed=True
            )
            
    except Exception as e:
        logger.error(f"[{device_name}] ✗ Connection failed: {str(e)}")
        return Result(
            host=task.host,
            result={'success': False, 'error': str(e)},
            failed=True
        )

# ============================================================================
# TASK 2: Save Configuration and Log to Database
# ============================================================================

@task
def save_config(task: Task, config_data: dict, backup_dir: str = "configs", db_file: str = "backup.db") -> Result:
    """
    Save configuration to file and database
    Tracks: size, hash, timestamp, change status
    """
    device_name = task.host.name
    
    if not config_data.get('success'):
        logger.warning(f"[{device_name}] Skipping save (config retrieval failed)")
        return Result(
            host=task.host,
            result={'success': False, 'reason': 'config_retrieval_failed'},
            failed=True
        )
    
    try:
        # Save to filesystem
        os.makedirs(backup_dir, exist_ok=True)
        safe_name = device_name.replace('.', '-')
        filename = f"{safe_name}_running-config.txt"
        filepath = os.path.join(backup_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(config_data['config'])
        
        file_size = os.path.getsize(filepath)
        
        # Log to database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get previous backup to detect change
        cursor.execute('''
            SELECT id, config_hash FROM backups 
            WHERE device_name = ? 
            ORDER BY backup_timestamp DESC LIMIT 1
        ''', (device_name,))
        
        previous = cursor.fetchone()
        changed = False
        
        if previous:
            # Compare with previous
            previous_hash = previous[1]
            changed = (previous_hash != config_data['hash'])
        
        # Insert new backup record
        cursor.execute('''
            INSERT INTO backups (device_name, config_size, config_hash, changed, status, filepath)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_name, file_size, config_data['hash'], changed, 'success', filepath))
        
        backup_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        status_msg = "CHANGED" if changed else "unchanged"
        logger.info(f"[{device_name}] ✓ Saved ({status_msg}): {file_size:,} bytes")
        
        return Result(
            host=task.host,
            result={
                'success': True,
                'filepath': filepath,
                'size': file_size,
                'backup_id': backup_id,
                'changed': changed
            }
        )
        
    except Exception as e:
        logger.error(f"[{device_name}] Save failed: {str(e)}")
        return Result(
            host=task.host,
            result={'success': False, 'error': str(e)},
            failed=True
        )

# ============================================================================
# TASK 3: Detect Changes
# ============================================================================

@task
def detect_changes(task: Task, current_config: str, db_file: str = "backup.db") -> Result:
    """
    Compare current config with previous backup
    Calculate added/removed lines
    """
    device_name = task.host.name
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get previous config
        cursor.execute('''
            SELECT b.id, b.filepath FROM backups b
            WHERE b.device_name = ? AND b.id < (
                SELECT MAX(id) FROM backups WHERE device_name = ?
            )
            ORDER BY b.id DESC LIMIT 1
        ''', (device_name, device_name))
        
        previous = cursor.fetchone()
        conn.close()
        
        if not previous:
            logger.info(f"[{device_name}] No previous backup (this is first)")
            return Result(
                host=task.host,
                result={
                    'success': True,
                    'changed': False,
                    'lines_added': 0,
                    'lines_removed': 0,
                    'summary': 'First backup'
                }
            )
        
        # Load previous config
        previous_id, previous_filepath = previous
        with open(previous_filepath, 'r') as f:
            previous_config = f.read()
        
        # Compare configs
        previous_lines = previous_config.splitlines()
        current_lines = current_config.splitlines()
        
        # Calculate difference
        differ = difflib.unified_diff(previous_lines, current_lines, lineterm='')
        diff_lines = list(differ)
        
        added = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        # Summarize changes
        if added == 0 and removed == 0:
            summary = "No changes"
            changed = False
        else:
            summary = f"+{added} lines, -{removed} lines"
            changed = True
        
        logger.info(f"[{device_name}] Changes detected: {summary}")
        
        return Result(
            host=task.host,
            result={
                'success': True,
                'changed': changed,
                'lines_added': added,
                'lines_removed': removed,
                'summary': summary,
                'previous_backup_id': previous_id
            }
        )
        
    except Exception as e:
        logger.error(f"[{device_name}] Change detection failed: {str(e)}")
        return Result(
            host=task.host,
            result={'success': False, 'error': str(e)},
            failed=True
        )

# ============================================================================
# TASK 4: Compliance Checking
# ============================================================================

@task
def compliance_check(task: Task, config: str, db_file: str = "backup.db") -> Result:
    """
    Check for common compliance issues:
    - Missing banner
    - Weak logging
    - Missing ACLs
    etc.
    """
    device_name = task.host.name
    config_lower = config.lower()
    
    issues = []
    score = 100
    
    # Check for security configurations
    security_checks = {
        'banner motd': ('Missing MOTD banner', 10),
        'logging': ('Missing syslog configuration', 15),
        'enable secret': ('Weak enable password (not using secret)', 20),
        'access-list': ('No ACLs configured', 10),
        'ntp': ('Missing NTP configuration', 5),
        'snmp-server host': ('SNMP not configured', 5),
    }
    
    for check_key, (issue_desc, penalty) in security_checks.items():
        if check_key not in config_lower:
            issues.append(issue_desc)
            score -= penalty
    
    score = max(0, score)  # Don't go below 0
    
    try:
        # Store compliance check in database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        issues_str = "; ".join(issues) if issues else "All checks passed"
        
        cursor.execute('''
            INSERT INTO compliance (device_name, compliance_score, issues, status)
            VALUES (?, ?, ?, ?)
        ''', (device_name, score, issues_str, 'completed'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"[{device_name}] Compliance score: {score}/100")
        
        return Result(
            host=task.host,
            result={
                'success': True,
                'score': score,
                'issues': issues,
                'passed_checks': len(security_checks) - len(issues)
            }
        )
        
    except Exception as e:
        logger.error(f"[{device_name}] Compliance check failed: {str(e)}")
        return Result(
            host=task.host,
            result={'success': False, 'error': str(e)},
            failed=True
        )

# ============================================================================
# TASK 5: Generate Summary Report
# ============================================================================

@task
def generate_report(task: Task, all_results: dict) -> Result:
    """
    Generate text report of backup operation
    """
    device_name = task.host.name
    
    try:
        device_results = all_results.get(device_name, {})
        
        report_lines = [
            f"\n{'=' * 70}",
            f"Device: {device_name}",
            f"{'=' * 70}",
        ]
        
        # Config info
        if 'save_config' in device_results:
            save_info = device_results['save_config']
            if save_info.get('success'):
                report_lines.append(f"✓ Config saved: {save_info.get('size', 0):,} bytes")
            else:
                report_lines.append(f"✗ Config save failed: {save_info.get('error')}")
        
        # Change detection
        if 'detect_changes' in device_results:
            change_info = device_results['detect_changes']
            if change_info.get('success'):
                status = "CHANGED" if change_info.get('changed') else "unchanged"
                report_lines.append(f"Changes: {change_info.get('summary')}")
        
        # Compliance
        if 'compliance_check' in device_results:
            compliance_info = device_results['compliance_check']
            if compliance_info.get('success'):
                score = compliance_info.get('score', 0)
                report_lines.append(f"Compliance Score: {score}/100")
                if compliance_info.get('issues'):
                    report_lines.append(f"Issues: {len(compliance_info['issues'])}")
        
        report = "\n".join(report_lines)
        
        return Result(
            host=task.host,
            result={
                'success': True,
                'report': report
            }
        )
        
    except Exception as e:
        return Result(
            host=task.host,
            result={'success': False, 'error': str(e)},
            failed=True
        )
```

**Save as:** `tasks/enterprise_backup.py`

---

## 🔧 Orchestration Script

Create `enterprise_main.py` to run the complete workflow:

```python
"""
Enterprise Configuration Backup System
Parallel execution with change detection and compliance checking
"""

import os
import sys
import getpass
from datetime import datetime
from nornir import InitNornir
import sqlite3
import tabulate
from tasks.enterprise_backup import (
    backup_config,
    save_config,
    detect_changes,
    compliance_check,
    generate_report
)

def main():
    """Main orchestration function"""
    
    print("=" * 70)
    print("Enterprise Configuration Backup System")
    print("=" * 70)
    
    # Get password
    device_password = getpass.getpass('Enter device password: ')
    
    try:
        # Initialize Nornir
        nornir = InitNornir(config_file="nornir_config.yaml")
        
        # Update passwords
        for host in nornir.inventory.hosts.values():
            host.password = device_password
        
        print(f"✓ Loaded {len(nornir.inventory.hosts)} devices\n")
        
        # ================================================================
        # STAGE 1: Backup Configurations (Parallel)
        # ================================================================
        print(f"{'=' * 70}")
        print("STAGE 1: Retrieving Configurations")
        print(f"{'=' * 70}\n")
        
        backup_results = nornir.run(
            task=backup_config,
            name="Backup Configurations"
        )
        
        # Extract config data for next stages
        config_data = {}
        for device_name, result in backup_results.items():
            if result[0].result.get('success'):
                config_data[device_name] = result[0].result
            else:
                config_data[device_name] = None
        
        # ================================================================
        # STAGE 2: Save Configurations (Parallel)
        # ================================================================
        print(f"\n{'=' * 70}")
        print("STAGE 2: Saving Configurations & Creating Database Records")
        print(f"{'=' * 70}\n")
        
        save_results = nornir.run(
            task=save_config,
            config_data=config_data,
            backup_dir="enterprise_configs",
            db_file="backup.db"
        )
        
        # ================================================================
        # STAGE 3: Detect Changes (Parallel)
        # ================================================================
        print(f"\n{'=' * 70}")
        print("STAGE 3: Detecting Configuration Changes")
        print(f"{'=' * 70}\n")
        
        changes_results = nornir.run(
            task=detect_changes,
            current_config={
                device_name: config_data[device_name]['config']
                if config_data[device_name] else None
                for device_name in config_data.keys()
            },
            db_file="backup.db"
        )
        
        # ================================================================
        # STAGE 4: Compliance Checking (Parallel)
        # ================================================================
        print(f"\n{'=' * 70}")
        print("STAGE 4: Running Compliance Checks")
        print(f"{'=' * 70}\n")
        
        compliance_results = nornir.run(
            task=compliance_check,
            config={
                device_name: config_data[device_name]['config']
                if config_data[device_name] else ""
                for device_name in config_data.keys()
            },
            db_file="backup.db"
        )
        
        # ================================================================
        # STAGE 5: Generate Summary Report
        # ================================================================
        print(f"\n{'=' * 70}")
        print("STAGE 5: Generating Summary Report")
        print(f"{'=' * 70}\n")
        
        # Aggregate all results for reporting
        all_aggregated = {}
        for device_name in nornir.inventory.hosts.keys():
            all_aggregated[device_name] = {
                'backup_config': backup_results[device_name][0].result,
                'save_config': save_results[device_name][0].result,
                'detect_changes': changes_results[device_name][0].result,
                'compliance_check': compliance_results[device_name][0].result,
            }
        
        report_results = nornir.run(
            task=generate_report,
            all_results={
                device_name: all_aggregated[device_name]
                for device_name in nornir.inventory.hosts.keys()
            }
        )
        
        # ================================================================
        # PRINT FINAL SUMMARY
        # ================================================================
        print(f"\n{'=' * 70}")
        print("FINAL SUMMARY")
        print(f"{'=' * 70}\n")
        
        # Database analysis
        conn = sqlite3.connect("backup.db")
        cursor = conn.cursor()
        
        # Summary table
        summary_data = []
        for device_name in nornir.inventory.hosts.keys():
            config_success = backup_results[device_name][0].result.get('success', False)
            save_success = save_results[device_name][0].result.get('success', False)
            
            if compliance_results[device_name][0].result.get('success'):
                score = compliance_results[device_name][0].result.get('score', 0)
            else:
                score = 0
            
            changed = changes_results[device_name][0].result.get('changed', False)
            
            summary_data.append([
                device_name,
                "✓" if config_success else "✗",
                "✓" if save_success else "✗",
                "Changed" if changed else "Same",
                f"{score}/100"
            ])
        
        headers = ["Device", "Config Retrieved", "Saved", "Status", "Compliance"]
        print(tabulate.tabulate(summary_data, headers=headers, tablefmt="grid"))
        
        # Statistics
        successful = sum(1 for d in summary_data if d[1] == "✓")
        changed_count = sum(1 for d in summary_data if "Changed" in d[3])
        avg_compliance = sum(int(d[4].split('/')[0]) for d in summary_data) / len(summary_data)
        
        print(f"\nSuccessful Backups: {successful}/{len(nornir.inventory.hosts)}")
        print(f"Changed Configs: {changed_count}/{len(nornir.inventory.hosts)}")
        print(f"Average Compliance: {avg_compliance:.1f}/100")
        
        print(f"\n✓ Backup database: backup.db")
        print(f"✓ Config files: enterprise_configs/")
        
        conn.close()

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Save as:** `enterprise_main.py`

---

## 🚀 Running the Enterprise System

### Setup

```bash
# Initialize database (one-time)
python init_db.py

# Run the backup system
python enterprise_main.py
```

### Expected Output

```
======================================================================
Enterprise Configuration Backup System
======================================================================
✓ Loaded 5 devices

======================================================================
STAGE 1: Retrieving Configurations
======================================================================

[router1] Retrieving configuration...
[router2] Retrieving configuration...
[switch1] Retrieving configuration...
[router3] Retrieving configuration...
[switch2] Retrieving configuration...

[router1] ✓ Retrieved 45,234 bytes
[router2] ✓ Retrieved 38,912 bytes
[switch1] ✓ Retrieved 62,148 bytes
[router3] ✓ Retrieved 41,205 bytes
[switch2] ✓ Retrieved 55,678 bytes

======================================================================
STAGE 2: Saving Configurations & Creating Database Records
======================================================================

[router1] ✓ Saved (unchanged): 45,234 bytes
[router2] ✓ Saved (CHANGED): 38,912 bytes
[switch1] ✓ Saved (unchanged): 62,148 bytes
[router3] ✓ Saved (unchanged): 41,205 bytes
[switch2] ✓ Saved (CHANGED): 55,678 bytes

======================================================================
STAGE 3: Detecting Configuration Changes
======================================================================

[router1] Changes detected: No changes
[router2] Changes detected: +12 lines, -8 lines
[switch1] Changes detected: No changes
[router3] Changes detected: No changes
[switch2] Changes detected: +5 lines, -2 lines

======================================================================
STAGE 4: Running Compliance Checks
======================================================================

[router1] Compliance score: 85/100
[router2] Compliance score: 80/100
[switch1] Compliance score: 90/100
[router3] Compliance score: 75/100
[switch2] Compliance score: 88/100

======================================================================
STAGE 5: Generating Summary Report
======================================================================

======================================================================
FINAL SUMMARY
======================================================================

╒════════════╤═════════════════╤═════════╤═════════╤═════════════╕
│ Device     │ Config Retrieved │ Saved   │ Status  │ Compliance  │
╞════════════╪═════════════════╪═════════╪═════════╪═════════════╡
│ router1    │ ✓                │ ✓       │ Same    │ 85/100      │
│ router2    │ ✓                │ ✓       │ Changed │ 80/100      │
│ switch1    │ ✓                │ ✓       │ Same    │ 90/100      │
│ router3    │ ✓                │ ✓       │ Same    │ 75/100      │
│ switch2    │ ✓                │ ✓       │ Changed │ 88/100      │
╘════════════╧═════════════════╧═════════╧═════════╧═════════════╛

Successful Backups: 5/5
Changed Configs: 2/5
Average Compliance: 83.6/100

✓ Backup database: backup.db
✓ Config files: enterprise_configs/
```

---

## 📊 Querying the Database

You now have a full backup history. Query it:

```python
# query_backups.py
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("backup.db")
cursor = conn.cursor()

print("Recent Backups:")
cursor.execute('''
    SELECT device_name, backup_timestamp, config_size, changed
    FROM backups
    WHERE backup_timestamp > datetime('now', '-7 days')
    ORDER BY backup_timestamp DESC
    LIMIT 20
''')

for row in cursor.fetchall():
    device, timestamp, size, changed = row
    status = "📝 Changed" if changed else "✓ Unchanged"
    print(f"{device:<15} {timestamp:<20} {size:>10,} bytes  {status}")

print("\n\nCompliance Scores:")
cursor.execute('''
    SELECT device_name, compliance_score, MAX(check_timestamp)
    FROM compliance
    GROUP BY device_name
    ORDER BY compliance_score DESC
''')

for row in cursor.fetchall():
    device, score, timestamp = row
    print(f"{device:<15} {score:>6.1f}/100  ({timestamp})")

conn.close()
```

---

## 🎓 Key Concepts Mastered

### Task Composition

```python
# You can chain tasks or run them in series
result1 = task.run(backup_config,      ...  )
result2 = task.run(save_config,        data=result1.result)
result3 = task.run(detect_changes,     config=result1.result['config'])
```

### Database Integration

```python
# Store metadata for historical analysis
conn = sqlite3.connect("backup.db")
cursor.execute("INSERT INTO backups (device_name, ...) VALUES (...)")
conn.commit()
```

### Data Aggregation

```python
# Collect results from all parallel executions
for device_name, result in backup_results.items():
    data = result[0].result  # Extract result from device
```

---

## 🚀 Advanced Variations

### Email Reports on Changes

```python
import smtplib
from email.mime.text import MIMEText

def send_change_report(changed_devices):
    body = f"Changed configs: {', '.join(changed_devices)}"
    msg = MIMEText(body)
    msg['Subject'] = "Config Changes Detected"
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@gmail.com', 'password')
    server.send_message(msg)
    server.quit()

# In main.py, after compliance checks:
if changed_count > 0:
    changed = [d[0] for d in summary_data if "Changed" in d[3]]
    send_change_report(changed)
```

### Push Alerts to Slack

```python
import requests

def send_slack_alert(device_name, message):
    webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    data = {'text': f"🚨 {device_name}: {message}"}
    requests.post(webhook_url, json=data)

# Use in compliance_check:
if score < 70:
    send_slack_alert(device_name, f"Low compliance: {score}/100")
```

### Backup Retention Policy

```python
import datetime

def cleanup_old_backups(days_to_keep=30):
    conn = sqlite3.connect("backup.db")
    cursor = conn.cursor()
    
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
    
    cursor.execute('''
        SELECT filepath FROM backups 
        WHERE backup_timestamp < ?
    ''', (cutoff.isoformat(),))
    
    for (filepath,) in cursor.fetchall():
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted old backup: {filepath}")
    
    # Also delete old records
    cursor.execute('''
        DELETE FROM backups WHERE backup_timestamp < ?
    ''', (cutoff.isoformat(),))
    
    conn.commit()
    conn.close()

# Call before backup: cleanup_old_backups(days_to_keep=30)
```

---

## 🧪 Testing Your System

### Test with Limited Devices

```python
# Filter to specific group in main.py
filtered = nornir.filter(group="ios_devices")
filtered.run(backup_config, ...)
```

### Mock Database for Testing

```python
# Use in-memory SQLite for testing
conn = sqlite3.connect(":memory:")  # ← In-memory database
```

---

## 🎯 Connection to PRIME Framework

This tutorial demonstrates the **Implement** stage:

- **Pragmatic:** Database stores what matters; compliance automates auditing
- **Transparent:** Detailed logging at every stage; clear reports
- **Reliable:** Multi-stage validation; graceful error handling

---

## 🎓 Next Steps

You've built an enterprise-grade automation system! Here's what's next:

**Continue with Advanced Patterns:**

1. **[Advanced Nornir Patterns](./advanced-nornir-patterns.md)** (Strongly Recommended)
   - Custom inventory plugins (Netbox integration)
   - Middleware for cross-task logic
   - Advanced error handling and logging
   - Memory optimization for 10,000+ devices
   - Multi-vendor support
   - Testing and debugging workflows

2. **[Why Nornir?](./why-nornir.md)** — Understand architectural decisions and alternatives

**Study Production Code:**

3. **[Deep Dives](../../deep-dives/index.md)** — See how production tools implement similar patterns
   - [CDP Network Audit](../../deep-dives/cdp-audit.md) — Enterprise discovery at scale
   - [Access Switch Audit](../../deep-dives/access-switch-audit.md) — Parallel collection and intelligent handling

**Scale & Deploy:**

4. **[PRIME Framework](../../prime-framework/index.md)** — Structure your automation for sustainable ROI
5. **[Services](../../services.md)** — Consulting for enterprise automation systems
6. **[Contact Us](../../about.md#contact)** — Let's discuss your automation challenges

---

[← Back to Intermediate Tutorials](./index.md)
