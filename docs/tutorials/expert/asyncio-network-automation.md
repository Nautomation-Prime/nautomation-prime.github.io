---
title: "Asyncio for Network Automation: High-Performance, Non-Blocking Operations"
description: Master Python's asyncio for scalable, event-driven network automation workflows.
tags:
  - Expert
  - Asyncio
  - Python
  - Network Automation
  - Tutorial
---

## Asyncio for Network Automation: High-Performance, Non-Blocking Operations

## Why This Tutorial Exists

Traditional threading and multiprocessing have limits. Asyncio enables high-performance, non-blocking automation for telemetry, APIs, and large-scale device operations.

---

## Prerequisites

- Advanced Python
- Familiarity with coroutines, event loops, and async/await

---

## When to Use Asyncio

- High-volume telemetry collection
- API polling and event-driven workflows
- Lightweight, non-blocking device operations

---

## Asyncio Basics Refresher

```python
import asyncio
async def main():
    await asyncio.sleep(1)
asyncio.run(main())
```

---

## Advanced Asyncio Patterns for Network Automation

### 1. Connection Pooling and Rate Limiting

Efficiently manage hundreds or thousands of device connections using semaphores and connection pools:

```python
import asyncio
from scrapli.async_driver import AsyncScrapli

semaphore = asyncio.Semaphore(20)  # Limit concurrent connections

async def collect(device):
    async with semaphore:
        async with AsyncScrapli(**device) as conn:
            result = await conn.send_command('show version')
            return result.result
```

### 2. Robust Error Handling and Timeouts

Use `asyncio.wait_for` and granular exception handling to ensure reliability:

```python
async def safe_collect(device, timeout=10):
    try:
        return await asyncio.wait_for(collect(device), timeout=timeout)
    except asyncio.TimeoutError:
        return f"Timeout on {device['host']}"
    except Exception as e:
        return f"Error on {device['host']}: {e}"
```

### 3. Gathering Results with Progress Tracking

Track progress and handle partial failures gracefully:

```python
from tqdm.asyncio import tqdm_asyncio

async def main(devices):
    results = []
    for coro in tqdm_asyncio.gather(*(safe_collect(d) for d in devices)):
        results.append(await coro)
    return results
```

---

## Real-World Use Case: Async Telemetry Collection

Collect streaming telemetry from multiple devices using async HTTP or gRPC clients (e.g., `httpx`, `grpclib`).

```python
import httpx

async def fetch_telemetry(device):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://{device['host']}/telemetry", timeout=5)
        return resp.json()
```

---

## Integrating with Other Async Libraries

- **httpx** for async HTTP APIs
- **aiomultiprocess** for hybrid CPU-bound + IO-bound tasks
- **aiosqlite** for async database logging

Example: Logging results asynchronously

```python
import aiosqlite

async def log_result(device, result):
    async with aiosqlite.connect('results.db') as db:
        await db.execute(
            "INSERT INTO results (device, output) VALUES (?, ?)",
            (device['host'], result)
        )
        await db.commit()
```

---

## Debugging, Testing, and Observability

- Use `asyncio.run(debug_main())` with logging and breakpoints
- Leverage `pytest-asyncio` for async test cases
- Integrate with observability tools (e.g., OpenTelemetry, Prometheus exporters)

---

## Performance Tuning and Benchmarking

- Profile event loop with `asyncio.get_running_loop().time()`
- Use `uvloop` for faster event loops (Linux)
- Benchmark with large device lists and tune semaphore limits

---

## Security and Best Practices

- Never store credentials in code; use async vault clients (e.g., `hvac` for HashiCorp Vault)
- Validate SSL/TLS for all async HTTP/gRPC calls
- Sanitize device outputs before logging

---

## PRIME in Action: Safety and Transparency

- Document async patterns, error handling, and fallback strategies
- Monitor performance, failures, and resource usage
- Ensure transparency in automation outcomes for audits

---

## Summary: Tutorial Takeaways

- Asyncio enables scalable, high-performance, and safe network automation
- Integrate with async libraries for full-stack automation
- PRIME principles ensure robust, transparent, and secure adoption

---

## 📣 Want More?

- [Nornir + PyATS Integration](nornir-pyats-integration.md)
- [Secure Credential Vaulting](secure-credential-vaulting.md)
- [DevOps & Observability](devops-observability-network-automation.md)
- [Tool Ecosystem Integration](tool-ecosystem-integration.md)
- [Async vs. Threading vs. Multiprocessing in Network Automation](../../blog/posts/async-vs-threading-vs-multiprocessing.md)
- [PRIME Framework Overview](../../prime-framework/index.md)

---
