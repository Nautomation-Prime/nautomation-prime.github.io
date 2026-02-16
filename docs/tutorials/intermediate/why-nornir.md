---
title: Why Nornir? Understanding the Problem and Solution
description: Discover why parallel execution matters, the limitations of sequential scripts, and how Nornir solves enterprise-scale automation challenges.
tags:
  - Intermediate
  - Nornir
  - Architecture
  - Performance
  - Parallelization
  - Tutorial
---

# Why Nornir? Understanding the Problem and Solution

## "From 30 Minutes to 3 Minutes — Why Enterprise Networks Need Parallel Automation"

You've completed the [Beginner Tutorials](../beginner/index.md) and successfully built a multi-device config backup script. It works great for 10 devices, even 50 devices. But what if your organization has 500 devices? Or 5,000?

In this tutorial, we'll uncover the critical scalability problem with your current approach, demonstrate how it manifests in real networks, and introduce **Nornir**—the solution designed for enterprise automation.

**Important:** This tutorial is conceptual. We're NOT writing production code yet. We're understanding the problem so that Nornir's solution makes sense.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ Why loops are fundamentally limited for device operations
- ✅ The mathematical principle of parallelization (Amdahl's Law)
- ✅ Real-world performance impact: sequential vs. parallel
- ✅ Nornir's architecture and why it's designed differently
- ✅ The cost/benefit tradeoff of adding framework complexity
- ✅ When Nornir is the right choice (and when it isn't)

---

## 🔴 The Problem: Sequential Bottleneck

Let's revisit your [Beginner Tutorial #3](../../beginner/multi-device-config-backup.md):

```python
# From Tutorial #3 — The Serial Approach
for device in devices:
    hostname, filename, size, status = backup_device_config(device, backup_dir)
```

**What this does:**
1. Connect to Device #1
2. Retrieve config (5 seconds of network I/O)
3. Save to file (1 second)
4. Disconnect
5. **THEN** move to Device #2
6. Repeat...

**The fundamental issue:** While the script waits for Device #1's network response, your CPU is completely idle. It can't fetch Device #2's config—it's stuck waiting.

---

### Real-World Impact

Let's do some math:

**Scenario: Enterprise network with 300 devices**

**Per-device timing:**

- SSH connection: 2 seconds
- `show running-config` execution: 3 seconds (network latency)
- File write: 1 second
- **Total per device: ~6 seconds**

**Sequential approach (Tutorial #3):**
```
300 devices × 6 seconds = 1,800 seconds = 30 MINUTES
```

**Parallel approach (Nornir):**
```
6 seconds × 10 concurrent connections = 0.6 seconds per "round"
300 ÷ 10 = 30 rounds
30 × 0.6 = 18 seconds (worst case, can be faster with optimization)
```

**Real-world result:** The same job takes 30 minutes with your current script but only 2-3 minutes with Nornir.

**That's a 10-15x speedup.**

---

## 📊 Visualizing Sequential vs. Parallel

### Sequential Execution (Tutorial #3 Approach)

```
Device 1: [=====...wait for network.....=====] ✓
Device 2:                                      [=====...wait for network.....=====] ✓
Device 3:                                                                           [=====...wait for network.....=====] ✓
Device 4:                                                                                                                  [=====...wait for network.....=====] ✓

Time: ████████████████████████████ (10 minutes for 4 devices)
CPU:  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ (CPU idle ~90% of the time)
```

**Notice:** While Device 1 waits for the network, Devices 2, 3, 4 aren't even started. The CPU is idle.

### Parallel Execution (Nornir Approach)

```
Device 1: [=====network=====]
Device 2:  [  ↑ overlapping  =====network=====]
Device 3:   [  ↑ overlapping  =====network=====]
Device 4:    [  ↑ overlapping  =====network=====]

Time: ████████████ (3 minutes for 4 devices)
CPU:  ████████████ (CPU efficiently scheduling I/O)
```

**Notice:** While Device 1 waits for the network, Devices 2, 3, 4 are fetching simultaneously. The network is fully utilized.

---

## 🧮 The Math: Amdahl's Law

Why doesn't this scale infinitely? There's a mathematical ceiling:

**Amdahl's Law:**
```
Speedup = 1 / [(1 - P) + (P / N)]

Where:
  P = percentage of task that can be parallelized (e.g., 0.95 for network ops)
  N = number of parallel processors/threads
```

**For network operations** (which are ~95% parallel):
- 10 parallel connections: 8.3x speedup
- 20 parallel connections: 13.3x speedup
- 50 parallel connections: 26x speedup
- 100 parallel connections: 47x speedup (diminishing returns visible here)

**Practical takeaway:** You get massive gains up to ~10-20 concurrent connections, then diminishing returns. But even diminishing returns beat sequential by a mile.

---

## 🚀 Why Your Tutorial #3 Script Doesn't Scale

Your current `multi-device-config-backup.py` uses this pattern:

```python
for device in devices:
    # Connect
    # Collect config
    # Save file
    # Move to next device (don't start next until this is done)
```

This is **sequential iteration**. It's simple, it's clear, it's great for learning—but it's a dead-end for enterprise scale.

### The Limitations

| Aspect | Tutorial #3 | Enterprise Need |
|:---|:---|:---|
| **Max devices** | 50-100 (before slowness) | 500-5000+ |
| **Expected runtime** | 10+ minutes | 2-3 minutes |
| **Code complexity** | Simple loops | Framework (Nornir) |
| **Failure isolation** | Per-device try/catch | Unified result aggregation |
| **Extensibility** | Hard (one-off changes) | Easy (reusable tasks) |
| **Team reusability** | One script per job | Shared task library |

---

## ✏️ Interlude: Why Not Just Use Threading in Python?

You might think: *"Why learn Nornir? Can't I just add `threading` to Tutorial #3?"*

You **could**, but here's why that's a bad idea:

```python
import threading

# This creates threads—but threads in Python don't truly parallelize due to GIL
def backup_with_threading(devices):
    threads = []
    for device in devices:
        t = threading.Thread(target=backup_device_config, args=(device,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
```

**Problems:**

1. **Python's GIL (Global Interpreter Lock)** — Threads don't actually run in parallel; they take turns
2. **Result aggregation** — Where does output go? How do you collect all results?
3. **Result aggregation** — No unified error handling
4. **Credentials** — Thread-safe password management gets complex
5. **Scalability** — Creating 500 threads crashes Python

**Nornir doesn't use threading**. It uses **async I/O** (via `asyncio`), which allows true concurrent operations *without* the GIL limitations.

---

## 🏗️ Nornir's Architecture

Nornir solves this problem by building a **task-based framework** instead of a script-based one.

### Core Concepts

#### 1. **Tasks** (not loops)
Instead of:
```python
for device in devices:
    do_something(device)
```

You write:
```python
@task
def backup_config(task):
    # This function runs once per device, in parallel
    config = task.run(netmiko_task, ...)
    return result
```

#### 2. **Inventory** (not hardcoded or CSV)
Nornir abstracts device information:
```yaml
# inventory/hosts.yaml
device1:
  hostname: 192.168.1.1
  groups:
    - ios_devices
  vars:
    privileged: true

device2:
  hostname: 192.168.1.2
  groups:
    - ios_devices
```

#### 3. **Runner** (not manual iteration)

Nornir's runner automatically:
- Loads all devices from inventory
- Executes tasks in parallel
- Collects results
- Handles failures

#### 4. **Result Aggregation** (not scattered output)
```python
result = nornir.run(backup_task)

# Built-in result object:
result[device_id].result  # The return value
result[device_id].failed  # Did it fail?
result[device_id].exception  # What went wrong?
```

**The benefit:** Nornir handles all the parallel complexity for you. You focus on the business logic.

---

## 📈 Architecture Comparison

### Tutorial #3 (Sequential Script Architecture)

```
main()
  ├── read_inventory()  [CSV]
  ├── for each device:
  │   ├── backup_device_config()
  │   │   ├── SSH connect
  │   │   ├── send_command()
  │   │   ├── Write file
  │   │   └── Return (hostname, filename, size, status)
  │   └── Collect results in list
  └── create_backup_manifest()
```

**Characteristics:**

- Linear control flow
- One device at a time
- Results scattered (some in variables, some in files)
- Hard to reuse (tied to specific task logic)

### Nornir (Task-Based Parallel Architecture)

```
Nornir Instance
  ├── Inventory Manager
  │   └── Loads devices from YAML/Netbox/API
  ├── Task Registry
  │   └── backup_config @task
  │   └── validate_config @task
  │   └── compare_configs @task
  └── Runner
      ├── Parallel task execution (connection pool)
      ├── Middleware pipeline
      ├── Result aggregation
      └── Plugin system
```

**Characteristics:**

- Task-based (functional programming)
- Parallel by default
- Unified result object
- Highly reusable (tasks are libraries)

---

## 💡 When to Use Nornir

### Use Nornir When:

✅ **Scale matters** (50+ devices)  
✅ **Performance matters** (tight backup windows)  
✅ **Complexity exists** (multi-step workflows, compliance checks)  
✅ **Teams collaborate** (shared task libraries)  
✅ **Enterprise requirements** (audit trails, integration, reliability)  
✅ **Future growth** (will your network grow?)  

### Use Tutorial #3 When:

✅ **Quick one-off script**  
✅ **Very small network** (<10 devices)  
✅ **Learning automation basics** (Tutorial #3 is perfect for this)  
✅ **No performance requirements**  

---

## 🎯 The Production Reality

In real organizations, here's what happens:

**Month 1:** *"Let's automate config backups!"*  
→ Build Tutorial #3 script  
→ Works great!

**Month 3:** *"We added offices in Asia and Europe. Backups now take 90 minutes."*  
→ "Hmm, let me add threading..."  
→ Threads cause issues...  

**Month 6:** *"Can we also do compliance checking? And integrate with our ticketing system?"*  
→ "The script is spiraling... This needs a redesign..."  
→ **This is where you wish you'd started with Nornir**

---

## 🔍 Under the Hood: Why Nornir Works

Nornir uses **asyncio** (Python's asynchronous I/O library) under the hood:

```python
# Parallel execution with asyncio (simplified)
import asyncio

async def backup_device(device):
    # While this device waits for SSH, other devices run
    await asyncio.sleep(3)  # Simulates network I/O
    return f"Backed up {device}"

async def backup_all(devices):
    # Create tasks for all devices (don't wait yet)
    tasks = [backup_device(d) for d in devices]
    # Now run ALL tasks concurrently
    results = await asyncio.gather(*tasks)
    return results

# All 4 devices run in ~3 seconds (parallel)
# Not 12 seconds (sequential)
```

**Nornir abstracts this complexity**, so you write simple task functions and Nornir handles the async execution automatically.

---

## 📊 Real Enterprise Example

**Telecom company with 2,500 Cisco devices**

**Old approach (Tutorial #3):**
```
Backup job scheduled: 2:00 AM
Expected completion: 4:30 AM (150 minutes)
Maintenance window: 2:00-6:00 AM ✓ Fits
```

**With Nornir:**
```
Backup job scheduled: 2:00 AM
Expected completion: 2:12 AM (12 minutes)
Maintenance window: 2:00-6:00 AM ✓ Fits comfortably
Plus: Can now run more audits/checks in same window!
```

**The business value:** 20 minutes used by automation instead of 2+ hours = real cost savings.

---

## 🧠 The Learning Curve

**Truth:** Nornir IS more complex than Tutorial #3.

But complexity serves a purpose:

```
Difficulty vs. Power

Tutorial Difficulty:  ▄ (low)
Tutorial Power:       ▄ (limited by scale)

Nornir Difficulty:    ████ (moderate)
Nornir Power:         ████████████████ (enterprise scale)
```

**The cost/benefit:** Adding moderate complexity early saves *enormous* complexity later (no threading hacks, no refactoring).

---

## 🔮 What's Coming Next

In [Tutorial #2: Nornir Fundamentals](./nornir-fundamentals.md), we'll:

1. Install Nornir and dependencies
2. Create your first inventory file
3. Write your first `@task` function
4. Run it against 5+ devices in parallel
5. See the performance benefit firsthand

**Spoiler:** You'll write basically the same logic as Tutorial #3, but Nornir will parallelize it automatically.

---

## 🎯 Key Takeaway

If you're automating networks at any significant scale:

**Sequential scripts = Training wheels**  
**Nornir = Real enterprise tool**

You don't need to choose immediately. But if you're building anything more than a quick proof-of-concept, learning Nornir is an investment that pays dividends.

---

## 💬 Your Perspective

As someone building this for the first time, here's my honest take:

- **Nornir feels more complex** when you first see it (it is)
- **BUT** it's designed specifically for your problem (parallel network ops)
- **AND** the payoff is huge (10-20x faster)
- **AND** once you understand it, it becomes your default tool

---

## 📚 Before You Continue

Make sure you have:

- ✅ Completed all [Beginner Tutorials](../beginner/index.md)
- ✅ Successfully run Tutorial #3 on at least 5 devices
- ✅ Observed how long it takes (30+ min for many devices)
- ✅ Understood the sequential bottleneck

When you're ready, [Tutorial #2 →](./nornir-fundamentals.md) will teach you to solve this problem with Nornir.

---

## 🆘 Questions Before Moving On?

**"Do I really need Nornir?"**  

- If you have <20 devices and never will: Probably not
- If you have >50 devices or think you will: Absolutely yes
- If you're in between: Learn it anyway; it's not that hard and you'll be prepared

**"Will I still use the Tutorial #3 approach?"**  

- Yes, for quick/one-off scripts
- But for anything you'll run more than once or scale: Nornir

**"Is Nornir hard to learn?"**  

- Moderate difficulty (Tutorial #2 makes it accessible)
- But the concepts are universal (async I/O, task-based automation)
- Worth the investment

---

[Continue to Tutorial #2: Nornir Fundamentals →](./nornir-fundamentals.md)

---

[← Back to Intermediate Tutorials](./index.md)
