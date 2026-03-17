---
title: Streaming Telemetry in Network Automation
date: 2026-02-26T12:00:00
draft: false
author: "Nautomation Prime Team"
description: An introduction to streaming telemetry, why it matters, and how to use it in your automation workflows.
tags:
  - Blog
  - Streaming Telemetry
  - Emerging Tech
  - PRIME Framework
  - Best Practices
---

## Streaming Telemetry in Network Automation: Real-Time Data for Modern Operations

---

> **This post is part of our ongoing series on network automation best practices, grounded in the [PRIME Framework](../../prime-framework/index.md) and [PRIME Philosophy](../../prime-framework/philosophy.md).**

!!! info "Transparency Note"
    Examples, scenarios, and any outcome figures in this article are provided for education and are based on enterprise delivery experience or anonymised composite scenarios unless explicitly identified as direct Nautomation Prime client outcomes.

## Why This Blog Exists

SNMP and CLI scraping are no longer enough. Streaming telemetry provides real-time, structured data for modern network automation. This post introduces the concept, benefits, and practical steps to get started.

<!-- more -->

---

## What is Streaming Telemetry?

- Push-based, real-time data from network devices
- Uses protocols like gRPC, gNMI, and model-driven YANG
- Delivers structured, high-frequency updates (JSON, GPB, or XML)
- Enables proactive monitoring, anomaly detection, and closed-loop automation

---

## Why Streaming Telemetry? (Benefits & Use Cases)

- **Real-time visibility:** Instantly detect outages, congestion, or config drift
- **Reduced overhead:** No more slow, resource-intensive polling
- **Rich data:** Access to interface stats, BGP state, QoS, and more
- **Automation triggers:** Use telemetry events to drive config changes, ticketing, or remediation

**Common Use Cases:**

- SLA monitoring and alerting
- Automated compliance checks
- Dynamic traffic engineering
- Security anomaly detection

---

## Streaming Telemetry Architecture

- **Device:** Publishes telemetry data (Cisco IOS-XR, NX-OS, Junos, EOS)
- **Collector:** Receives and parses telemetry (Telegraf, Pipeline, custom Python)
- **Processor:** Analyzes, stores, and triggers automation (InfluxDB, Prometheus, custom apps)

---

## Example 2: Processing Telemetry for Automation (Advanced)

```python
import asyncio
import json
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TelemetryEvent:
    timestamp: float
    device: str
    interface: str
    metric: str
    value: int

async def process_telemetry_stream(telemetry_queue):
    """Process incoming telemetry and trigger automation."""
    threshold_config = {
        'in_errors': 100,
        'out_errors': 100,
        'input_queue_drops': 50,
        'queue_depth': 200,
    }
    
    while True:
        event = await telemetry_queue.get()
        
        # Parse telemetry
        try:
            metric_name = event.metric
            value = event.value
            device = event.device
            interface = event.interface
        except AttributeError:
            logger.error(f"Invalid telemetry event: {event}")
            continue
        
        # Check against thresholds
        threshold = threshold_config.get(metric_name)
        if threshold and value > threshold:
            logger.warning(f"ALERT: {device} {interface} {metric_name}={value} (threshold={threshold})")
            
            # Trigger remediation
            await remediate_interface(device, interface, metric_name, value)
        
        telemetry_queue.task_done()

async def remediate_interface(device, interface, metric_name, value):
    """Attempt automated remediation."""
    remediation_actions = {
        'in_errors': lambda d, i: bounce_interface(d, i),
        'input_queue_drops': lambda d, i: increase_queue_buffer(d, i),
        'queue_depth': lambda d, i: apply_qos(d, i),
    }
    
    action = remediation_actions.get(metric_name)
    if action:
        try:
            result = await action(device, interface)
            logger.info(f"Remediation successful: {device} {interface}")
            await verify_remediation(device, interface, metric_name)
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            await alert_human_ops(device, interface, metric_name, value)

async def verify_remediation(device, interface, metric_name, max_retries=3):
    """Verify that remediation actually fixed the issue."""
    for attempt in range(max_retries):
        await asyncio.sleep(5)  # Wait 5 seconds before checking
        current_value = await get_current_metric(device, interface, metric_name)
        
        if current_value < 50:  # Back to normal
            logger.info(f"Remediation verified on {device} {interface}")
            return True
    
    logger.error(f"Remediation could not be verified on {device} {interface}")
    return False
```

---

## Collecting Telemetry: Practical Setup Guide

### Using Telegraf to Collect from gNMI/SNMP

```toml
# /etc/telegraf/telegraf.conf
[[inputs.gnmi]]
  addresses = ["10.0.0.1:57400", "10.0.0.2:57400"]
  username = "admin"
  password = "password"
  
  [[inputs.gnmi.subscription]]
    name = "interface_counters"
    origin = "openconfig"
    path = "/interfaces/interface/state/counters"
    mode = "sample"
    sample_interval = "10s"

[[outputs.influxdb]]
  urls = ["http://localhost:8086"]
  database = "network_telemetry"
```

### Using Python Async gNMI for Real-Time Processing

```python
import asyncio
from pygnmi.client import gNMIclient
import json

async def collect_telemetry_async(device_ip, username, password):
    """Collect telemetry from gNMI-enabled device asynchronously."""
    
    async with gNMIclient(
        target=(device_ip, 57400),
        username=username,
        password=password,
        insecure=True,
        # Enable SSL if needed: insecure=False, cert_file='cert.pem', key_file='key.pem'
    ) as gc:
        # Subscribe to interface counters
        subscription = {
            'path': '/interfaces/interface/state/counters',
            'mode': 'sample',
            'sample_interval': 10000000000  # 10 seconds in nanoseconds
        }
        
        try:
            async for telemetry in gc.subscribe(
                subscriptions=[subscription],
                mode='stream',
                encoding='json_ietf'
            ):
                # Process each telemetry update
                await process_telemetry(telemetry)
        except Exception as e:
            print(f"Error: {e}")

async def process_telemetry(telemetry_msg):
    """Parse and store telemetry data."""
    try:
        # Extract data from gNMI message
        if 'update' in telemetry_msg:
            for update in telemetry_msg['update']['update']:
                path = update['path']
                value = update['val']['json_val']
                
                # Store in time-series database
                await store_in_influx(path, value)
                
                # Check for alerts
                await check_thresholds(path,value)
    except Exception as e:
        print(f"Failed to process telemetry: {e}")

# Main event loop
async def main():
    devices = [
        {'ip': '10.0.0.1', 'username': 'admin', 'password': 'pass'},
        {'ip': '10.0.0.2', 'username': 'admin', 'password': 'pass'},
    ]
    
    tasks = [collect_telemetry_async(d['ip'], d['username'], d['password']) for d in devices]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

---

## Telemetry Storage & Analysis

### Time-Series Database Options

| Database | Pros | Cons | Best For |
| :--- | :--- | :--- | :--- |
| **InfluxDB** | Fast, simple, built-in compression | Single node scalability | Small to medium networks |
| **Prometheus** | Pull-based, excellent for metrics | Limited retention/high cardinality | Kubernetes, multi-vendor |
| **TimescaleDB** | PostgreSQL-compatible, SQL queries | Steeper setup | Complex queries, large scale |
| **Elasticsearch** | Flexible, full-text search | Complex, resource-intensive | Logs + metrics, compliance |

### Example: Querying Telemetry with InfluxQL

```sql
SELECT IF(mean("in_errors") > 100, 'ALERT', 'OK') as status
FROM "interface_counters"
WHERE device = 'router-01' AND time > now() - 1h
GROUP BY time(5m), interface
```

---

## Alerting & Automation with Telemetry

### Grafana Alert Rules

```yaml
alert: HighInterfaceErrors
expr: rate(interface_in_errors_total[5m]) > 10
for: 5m
labels:
  severity: critical
annotations:
  summary: "High errors on {{ $labels.device }} {{ $labels.interface }}"
  runbook_url: "https://runbooks.example.com/interface_errors"
```

### Dynamic Thresholds (ML-Based)

```python
async def check_thresholds_dynamic(device, metric_value):
    """Use recent baseline to detect anomalies (not just static thresholds)."""
    
    # Get baseline from last 1 hour
    baseline = await get_metric_baseline(device, hours=1)
    mean = baseline['mean']
    stddev = baseline['stddev']
    
    # Detect if current value is 3+ standard deviations from mean
    z_score = abs((metric_value - mean) / stddev)
    if z_score > 3:
        await alert_ops(f"Anomaly detected on {device}: z-score={z_score:.2f}")
```

---

## Advanced Patterns: Scaling, Security, and Observability

### High-Volume Telemetry: Kafka Buffer

```python
# Produce telemetry to Kafka for distributed processing
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def stream_telemetry_to_kafka(telemetry_queue):
    """Buffer telemetry in Kafka for processing."""
    while True:
        event = await telemetry_queue.get()
        producer.send('network_telemetry', value=event)

# Consume from Kafka for processing
from kafka import KafkaConsumer

def process_telemetry_from_kafka():
    consumer = KafkaConsumer(
        'network_telemetry',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    for message in consumer:
        event = message.value
        process_event(event)
```

### Secure Telemetry Streams

- Use **TLS/mTLS** for gNMI connections
- Implement **role-based access control** for telemetry consumers
- Encrypt telemetry data **at rest** (database encryption)
- Sanitize sensitive fields (mask device IPs, credentials)
- Use **API keys/tokens** for collector authentication

```python
# Secure gNMI example with certificates
gc = gNMIclient(
    target=('10.0.0.1', 57400),
    username='admin',
    password='pass',
    insecure=False,  # Enable TLS
    cert_file='/path/to/client.crt',
    key_file='/path/to/client.key',
    ca_certs='/path/to/ca.crt'
)
```

---

## Additional PRIME Practices: Measurability, Safety, and Transparency

- **Establish baselines** — Collect 1-2 weeks of normal telemetry before alerting
- **Track alert accuracy** — Monitor false positive and false negative rates monthly
- **Use run IDs** — Correlate telemetry with automation actions for end-to-end tracing
- **Document thresholds** — Every alert should have a runbook explaining why it fired
- **Monitor collection health** — Alert if a device stops sending telemetry
- **Archive telemetry** — Retain data for compliance, trend analysis, and incident forensics

---

## PRIME in Action: Measurability, Safety, and Transparency

- Use telemetry for automated validation and compliance
- Alert on anomalies and performance issues
- Document telemetry sources, data models, and usage
- Build dashboards for key metrics and automation triggers

---

## Summary: Blog Takeaways

- Streaming telemetry is the future of network data collection and automation
- Start with supported devices and open-source collectors
- Use telemetry to drive real-time monitoring, alerting, and automation
- PRIME principles ensure safe, measurable, and transparent adoption

---

## Related Tutorials & Deep Dives

- [Model-Driven APIs in Network Automation](emerging-tech-model-driven-apis.md) — Learn about gNMI, RESTCONF, and YANG for structured device management.
- [Event-Driven Automation in the Network](emerging-tech-event-driven-automation.md) — Build real-time, event-driven workflows with webhooks and message queues.
- [DevOps & Observability (Expert)](../../tutorials/expert/devops-observability-network-automation.md) — Integrate telemetry into CI/CD and monitoring pipelines.

## 📣 Want More?

- [Observability for Network Automation](observability-network-automation.md)
- [PRIME Framework Overview](../../prime-framework/index.md)

---
