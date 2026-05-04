---
title: Zero-Touch Provisioning Setup
description: Auto-configure new Cisco access switches the moment they're plugged in. This pack designs and implements a ZTP solution for your environment — so new switches come up fully provisioned without an engineer touching them.
tags:
  - SMB
  - Zero-Touch Provisioning
  - ZTP
  - Cisco
  - Network Provisioning
---

## Zero-Touch Provisioning Setup

### New Switches That Configure Themselves

Rolling out a new site or expanding an existing one means someone configuring every port, VLAN, and interface on each new access switch. It's slow, it's error-prone, and it scales poorly as your network grows.

Zero-Touch Provisioning (ZTP) changes that. When a new switch is racked, cabled, and powered on, it automatically downloads its configuration and comes up fully provisioned — without an engineer logging in manually.

This pack designs and implements a ZTP solution tailored to your environment.

---

## What You Get

**A complete, documented ZTP solution for your network:**

- **ZTP architecture design** — DHCP scope configuration, provisioning server options, device discovery mechanism
- **Python-based provisioning script** — hosted on a lightweight server or VM in your environment
- **Device template library** — configuration templates for your standard switch roles (access, distribution, or custom)
- **Basic inventory registration** — device logs itself in an inventory file on first boot
- **Lab test and validation** — tested on a physical or virtual device before you use it in production
- **Operations runbook** — step-by-step guide for your team to add new switch types and deploy to new sites
- **Full source code** — documented line-by-line; no black-box binaries
- **45-minute handover walkthrough**

---

## How ZTP Works (Cisco IOS-XE)

```
1. New switch powers on with factory-default configuration

2. Switch sends DHCP request on all interfaces

3. DHCP server responds with:
   ├── IP address
   ├── Default gateway
   └── DHCP Option 67 (bootfile name pointing to provisioning script URL)

4. Switch downloads and executes the Python provisioning script

5. Provisioning script:
   ├── Identifies the device (serial number, model, MAC)
   ├── Looks up the correct configuration template
   ├── Renders the template with site/device-specific values
   ├── Applies the configuration to the device
   └── Registers the device in the inventory file

6. Switch is fully configured and operational
   — no engineer login required
```

---

## Configuration Templates

Templates are written in Jinja2 and are fully customisable. A standard access switch template typically covers:

- Hostname
- Management VLAN and IP address
- Default gateway
- VLANs (data, voice, management)
- Interface profiles (access ports, uplink trunks, PoE settings)
- Spanning tree mode and portfast/BPDU guard
- NTP, syslog, SNMP, AAA
- SSH access and VTY line configuration
- Login banner

Multiple templates can be maintained for different switch roles (e.g. access, distribution, warehouse, PoE-heavy). The provisioning script selects the correct template based on device model, serial number, or a pre-registered lookup.

---

## Pricing

| Scope | Price |
| :---- | :---- |
| Single site, single switch role template | £1,500 |
| Multi-role templates (e.g. access + distribution) | £2,200 |
| Multi-site with inventory integration | £3,000 |

---

## Technical Prerequisites

- A management VLAN and DHCP server that can be configured to serve Option 67
- A lightweight server or VM (Linux preferred, Windows supported) reachable from the provisioning VLAN — this hosts the provisioning script and template files
- Cisco IOS-XE devices that support ZTP (Catalyst 9000 series, ISR 1000/4000 series)
- Network connectivity between the provisioning server and the DHCP/switching infrastructure

**No cloud services required.** The provisioning server runs entirely within your own environment.

---

## Turnaround

**2–3 weeks** from scope agreement.

Typical timeline:

1. **Architecture review (Day 1–3)** — confirm DHCP approach, template roles, server placement, and inventory requirements
2. **Development (Day 4–10)** — provisioning script and templates built
3. **Lab validation (Day 11–15)** — tested on a physical or virtual device in your environment before signing off
4. **Delivery and handover (Day 15–21)**

---

## Frequently Asked Questions

**What happens if the provisioning server is unreachable?**

The switch will keep retrying. Without a successful provisioning response, the device remains in a DHCP-loop state. It will not apply a partial configuration. Once the server is reachable, provisioning completes normally.

**Can we update templates after delivery?**

Yes. Templates are plain Jinja2 text files. Your team can edit them directly using a text editor. The documentation explains the template syntax and how to test changes before deploying to production.

**What if a switch has already been configured — will ZTP overwrite it?**

ZTP only runs on factory-default or fully zeroed devices. A switch with an existing startup configuration will not trigger ZTP on boot.

**Can it work with our existing DHCP server (Windows DHCP / Infoblox)?**

Yes. We advise on the exact DHCP scope options required. If your DHCP server supports Option 67, it will work. We provide tested configuration examples for common platforms during scoping.

**Does it require internet access?**

No. Everything runs within your network. The provisioning script and templates are hosted on your own server.

**What about Day-2 changes after initial provisioning?**

ZTP handles Day-0 (initial provisioning). For Day-2 changes (ongoing configuration management), consider our [Custom Script Build](./custom-script-build.md) or [Automation-as-a-Service](./automation-as-a-service.md) packages.

---

[**Enquire About This Pack →**](mailto:enquiries@nautomationprime.io?subject=Zero-Touch%20Provisioning%20Setup){.md-button .md-button--primary} [**View All Packages →**](../services.md){.md-button}
