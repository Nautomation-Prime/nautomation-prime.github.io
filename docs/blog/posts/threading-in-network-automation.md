---
date: 2026-02-26T12:00:00
draft: false
author: "Nautomation Prime Team"
description: Why threading is almost never the right tool for network automation, and how the PRIME Framework guides safer, scalable concurrency.
tags:
  - Blog
  - Concurrency
  - Network Automation
  - PRIME Framework
  - Best Practices
  - Lessons Learned
---

# Threading in Network Automation: When to Use It and When to Avoid It

---

> **This post is part of our ongoing series on network automation best practices, grounded in the [PRIME Framework](../../prime-framework/index.md) and [PRIME Philosophy](../../prime-framework/philosophy.md).**

## Why This Blog Exists

If you've ever been tempted to sprinkle a bit of Python `threading` into your network scripts for "speed"—stop! This post is for you. We'll show you why threading is almost always the wrong tool for network automation, and how the PRIME Framework's principles lead to safer, more scalable solutions.

<!-- more -->

---

## 🚦 PRIME Philosophy: The Foundation for Safe Automation

Before we dive into the technicals, let's set the stage. At Nautomation Prime, every automation decision is guided by five core principles:

- **Transparency** — No black boxes. Every script is documented and explainable.
- **Measurability** — Every outcome is tracked and proven. No assumptions.
- **Ownership** — You own your automation. No vendor lock-in.
- **Safety** — Production-grade reliability comes before speed.
- **Empowerment** — Your team understands and controls the automation.

> Learn more: [The PRIME Philosophy](../../prime-framework/philosophy.md)

---


## Why Threading Is Problematic for Network Device Automation

Network devices are not typical web services. They:

- Expose stateful, line‑oriented CLIs
- Require strict request/response ordering
- Often have fragile session handling
- May rate‑limit or lock sessions under load
- Expect deterministic sequencing of commands

Threading introduces concurrency without guaranteeing ordering, timing, or resource isolation. This leads to:

- Race conditions in CLI interactions
- Interleaved output when multiple threads share libraries not designed for concurrency
- Unpredictable failures when devices cannot handle parallel sessions
- Debugging complexity due to nondeterministic behaviour

### Deep Dive: Python Threading Internals & the GIL

Python's Global Interpreter Lock (GIL) means only one thread executes Python bytecode at a time. While threads can help with I/O-bound tasks, they do **not** provide true parallelism for CPU-bound work. Worse, many network libraries (e.g., Netmiko, Paramiko, pyATS) are not thread-safe, and their internal state can be corrupted by concurrent access.

#### Thread Safety: What Can Go Wrong?

- **Shared State:** Libraries that cache sessions, credentials, or buffers can have their state corrupted by multiple threads.
- **Non-atomic Operations:** Sending a command and reading output is not atomic—threads can interleave, causing output to be mixed or lost.
- **Resource Contention:** Devices may lock out sessions or rate-limit under concurrent access, leading to unpredictable failures.

#### Advanced Failure Scenarios

- **Deadlocks:** Two threads waiting on each other for resources (e.g., session locks) can cause the script to hang indefinitely.
- **Heisenbugs:** Bugs that only appear under certain timing conditions, making them nearly impossible to reproduce or debug.
- **Silent Data Corruption:** Output from one device appears in another thread’s buffer, leading to incorrect automation results without obvious errors.

> **For these reasons, threading is generally unsuitable for direct device configuration or state‑changing operations.**

---

## Advanced Checklist: Is Threading Safe for This Task?

- [ ] Is the task read-only and stateless?
- [ ] Does each thread have its own connection and state?
- [ ] Is the library explicitly documented as thread-safe?
- [ ] Can all failures be retried safely?
- [ ] Is deterministic ordering unnecessary?
- [ ] Have you tested at scale (10x+ devices)?

If you answered "no" to any of these, **avoid threading**.

---


## When Threading Is (and Isn't) Appropriate

Threading is useful when tasks are:

- I/O‑bound rather than CPU‑bound
- Stateless and do not modify device configuration
- Read‑only and tolerant of occasional retries
- Isolated so each thread has its own connection and state

### Example: CDP Neighbour Discovery (with Code)

A CDP neighbour collection script is:

- Read‑only
- Stateless
- Independent per device
- Tolerant of occasional connection failures

Threading works well here because each thread:

1. Opens its own session
2. Runs a single command
3. Parses output
4. Closes the session

There is no shared state, no configuration changes, and no risk of interleaving commands.

#### Example Code: Safe Threaded Data Collection

```python
import threading
import queue
import netmiko

def collect_cdp(host, creds, results):
  try:
    conn = netmiko.ConnectHandler(**creds, host=host)
    output = conn.send_command('show cdp neighbors detail')
    results.put((host, output))
    conn.disconnect()
  except Exception as e:
    results.put((host, f'ERROR: {e}'))

hosts = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
creds = {"device_type": "cisco_ios", "username": "user", "password": "pass"}
results = queue.Queue()
threads = []
for host in hosts:
  t = threading.Thread(target=collect_cdp, args=(host, creds, results))
  t.start()
  threads.append(t)
for t in threads:
  t.join()
while not results.empty():
  host, output = results.get()
  print(f"{host}: {output[:60]}...")
```

### When Threading Should Be Avoided

Threading should **not** be used for:

- Configuration changes of any kind
- Multi‑step workflows requiring strict sequencing
- Libraries that are not thread‑safe (Netmiko, Paramiko, pyATS, etc.)
- Long‑lived sessions where state persists across commands
- Operations requiring transaction‑like behaviour

#### Typical Failure Scenarios

- Two threads send commands faster than the device can process them
- Output from one thread appears in another thread’s buffer
- Session locks or rate limits cause unpredictable failures
- Devices with slow CPUs or control planes become overloaded

#### Advanced Example: What *Not* to Do

```python
# DANGEROUS: Shared connection object across threads
import threading
import netmiko

conn = netmiko.ConnectHandler(host='10.0.0.1', device_type='cisco_ios', username='user', password='pass')
def change_config():
  conn.send_config_set(['interface Loopback123', 'description BAD'])
threads = [threading.Thread(target=change_config) for _ in range(5)]
for t in threads:
  t.start()
for t in threads:
  t.join()
# This can corrupt device state, interleave commands, and cause outages!
```

---


## PRIME Framework: The Right Way to Scale

The [PRIME Framework](../../prime-framework/index.md) is designed to prevent exactly the kinds of failures threading introduces. Here’s how each stage helps:

| PRIME Stage   | How It Prevents Threading Pitfalls |
|-------------- |------------------------------------|
| **Pinpoint**  | Identifies where concurrency is safe and where it’s not. No guessing. |
| **Re-engineer** | Redesigns workflows for safety and scalability before automating. |
| **Implement** | Uses frameworks (like Nornir, AsyncIO) that provide safe, transparent parallelism. |
| **Measure**   | Tracks outcomes—so you know if concurrency is helping or hurting. |
| **Empower**   | Ensures your team understands the risks and best practices. |

### PRIME in Practice: Robust Alternatives

- **Nornir:** Provides controlled, per-host parallelism with error handling and inventory management.
- **AsyncIO:** Enables scalable, non-blocking I/O for high-volume telemetry and data collection (see our [asyncio expert tutorial](../../tutorials/expert/asyncio-network-automation.md)).
- **Process Pools:** For CPU-bound tasks, use `concurrent.futures.ProcessPoolExecutor` to bypass the GIL and isolate state.

#### Example: Nornir for Safe Parallelism

```python
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command

nr = InitNornir(config_file="config.yaml")
def show_cdp(task):
  result = task.run(task=netmiko_send_command, command_string="show cdp neighbors detail")
  task.host["cdp"] = result.result
results = nr.run(task=show_cdp)
for host, multi_result in results.items():
  print(f"{host}: {multi_result[0].result[:60]}...")
```

---

---

## Recommended Alternatives to Threading

Different automation tasks require different concurrency models. Here’s a quick reference:

| Task Type                      | Recommended Approach                        | Why It Works                                   | Notes                                  |
|--------------------------------|---------------------------------------------|------------------------------------------------|----------------------------------------|
| Configuration changes          | Nornir (serial or controlled parallelism)   | Ensures deterministic ordering and per‑host isolation | Use `num_workers` conservatively       |
| State‑changing workflows       | Nornir + per‑task error handling            | Predictable, structured execution              | Avoid high parallelism                  |
| Bulk read‑only data collection | ThreadPoolExecutor or Nornir parallel mode  | I/O‑bound, stateless, safe to parallelise      | Ensure each thread has its own connection |
| High‑volume telemetry          | AsyncIO + scrapli‑community async drivers   | Designed for concurrency, non‑blocking I/O     | Requires async‑capable libraries        |
| Long‑running workflows         | Process pools or distributed workers        | Avoids GIL limitations and isolates state      | Use for CPU‑heavy parsing or analytics  |
| Device inventory or discovery  | Threading or async                          | Stateless and tolerant of retries              | Ideal use case for threading            |

---
---


## Practical Guidance: Expert Best Practices

### Use Threading When:

- Each task is independent
- No configuration is being changed
- The library used is safe to call concurrently
- Failures can be retried without impact
- You need fast, parallel data collection

### Avoid Threading When:

- You are modifying device state
- You rely on multi‑step CLI interactions
- You need deterministic behaviour
- You are using libraries with shared global state
- You cannot tolerate nondeterministic failures

### Advanced Tips for Safe Concurrency

- **Always** use a thread-safe queue (e.g., `queue.Queue`) for results aggregation.
- Never share connection objects between threads.
- Limit the number of threads to avoid overwhelming devices (test with 2-3, scale up cautiously).
- For CPU-bound tasks, prefer `ProcessPoolExecutor`.
- For high-scale I/O, consider `asyncio` and async network libraries.
- Document concurrency assumptions and test at scale before production.

---


## Real-World Example: PRIME Philosophy in Action

> "We once rescued a client whose previous consultant used threading for config changes. The result? Interleaved commands, random failures, and a week of outages. We rebuilt their automation using the PRIME Framework—measurable, safe, and fully documented. No more outages, and the client's team could finally own their scripts."

#### Additional Case Study: Threading Gone Wrong

At another enterprise, a well-meaning engineer used threading to push VLAN changes to 100+ switches. Halfway through, devices started locking out sessions, and some switches received only partial configs. The result: a multi-day outage and a costly manual recovery. The root cause? Threading was used for a stateful, multi-step workflow—violating every PRIME principle. The fix: move to Nornir with serial execution and robust error handling.

---


## Summary: Blog Takeaways

- Threading is not inherently bad—but it’s the wrong tool for most network automation tasks.
- The PRIME Framework and Philosophy provide a safer, more sustainable path.
- If you want automation that’s transparent, measurable, and safe, avoid threading for anything stateful or critical.
- Use Nornir, AsyncIO, or process pools for robust, scalable concurrency.
- Always test concurrency at scale and document your design.
- Want to see the technical deep dive? [Read the full PRIME Philosophy](../../prime-framework/philosophy.md)

---

## 📣 Want More?

- See how the PRIME Framework prevents automation failures: [Why Most Network Automation Pipelines Fail (And How to Fix Them)](why-automation-fails.md)
- Learn about the five stages: [PRIME Framework Overview](../../prime-framework/index.md)
- Curious about the philosophy? [The PRIME Philosophy](../../prime-framework/philosophy.md)

---

*Have you seen advice elsewhere on this site to avoid threading? Now you know why!*

---
