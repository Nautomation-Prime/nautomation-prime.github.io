---
title: "Capstone Chapter 6: Proving the Change with PyATS"
description: Verify a deployment independently by learning operational state with PyATS Genie and diffing it against a snapshot taken before the change.
tags:
  - Capstone
  - PyATS
  - Genie
  - Verification
  - Tutorial
---

## Chapter 6: Proving the Change with PyATS

*Capstone chapter 6 of 7 — [project overview](./index.md)*

## "Nornir Said Success. That Isn't the Same as Working."

When Nornir reports success, it means the device accepted the commands without an error string. That is a genuinely low bar.

A switch will accept `switchport access vlan 10` on a port whose physical link is down. It will accept a trunk configuration that immediately drops adjacency because the other end doesn't match. It will accept VLAN definitions that spanning tree then blocks. Every one of those is "success" to the thing that sent the commands.

This chapter goes and looks.

---

## 🎯 What You'll Build

- A PyATS testbed generated from intent — same pattern as chapter 5's inventory
- State snapshots before and after, using Genie's operational models
- `netpipe/verify.py` — a state diff and a verdict
- `netpipe verify` — the command that decides whether chapter 7 rolls back

**Builds on:** [PyATS Fundamentals](../intermediate/pyats-fundamentals.md), [PyATS Network Validation](../intermediate/pyats-network-validation.md)

---

## 🔬 Why Not Just Re-Read the Config?

You could run `show running-config` again and check your lines are present. It's tempting, it's fast, and it proves almost nothing.

Re-reading the config asks the device: *"do you have the text I sent you?"* Of course it does — you just sent it, and it said yes. The question that matters is different: *"is the network in the state that text was supposed to produce?"*

| Config says | Operational state says |
|---|---|
| `switchport access vlan 10` | The port is in VLAN 10 **and the link is up** |
| `switchport mode trunk` | The trunk is up **and forwarding the expected VLANs** |
| `vlan 20 / name VOICE` | VLAN 20 exists **and isn't blocked by spanning tree** |
| Interface has no `shutdown` | The interface is `up/up`, not `up/down` or `err-disabled` |

The right-hand column is what Genie reads. This is [the whole argument for PyATS](../intermediate/pyats-fundamentals.md), and it's why the [config diff in chapter 3 was labelled advisory](./03-rendering-configuration.md).

---

## 📇 Generate the Testbed

Same principle as the Nornir inventory: derive it, don't maintain it.

**`netpipe/testbed.py`:**

```python
#!/usr/bin/env python3
"""
Build a PyATS testbed from validated intent.
"""

from pathlib import Path

import yaml
from genie.testbed import load as load_testbed

from netpipe.models import SiteIntent
from netpipe.settings import Settings

PYATS_OS = {"ios": "iosxe", "iosxe": "iosxe", "nxos": "nxos"}


def build_testbed(intent: SiteIntent, settings: Settings,
                  directory: str = "artefacts"):
    """
    Write a testbed file and return a loaded Genie testbed object.

    Credentials go into the in-memory object only; the file on disk has
    placeholders, exactly as with the Nornir inventory in chapter 5.
    """
    devices = {
        device.name: {
            "os": PYATS_OS[device.platform],
            "type": "switch",
            "credentials": {
                "default": {"username": "%ENV{NETAUTO_USERNAME}",
                            "password": "%ENV{NETAUTO_PASSWORD}"},
            },
            "connections": {
                "cli": {
                    "protocol": "ssh",
                    "ip": str(device.mgmt_ip),
                    "arguments": {"connection_timeout": settings.connect_timeout},
                },
            },
        }
        for device in intent.devices
    }

    document = {
        "testbed": {"name": f"{intent.site}-generated"},
        "devices": devices,
    }

    path = Path(directory) / "testbed.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    return load_testbed(str(path))
```

`%ENV{...}` is PyATS's own environment substitution — the file references the variable, the value is resolved at load time and never written down.

---

## 📸 Snapshots

Genie's `learn()` builds a structured model of a feature by running whatever commands that feature needs and parsing them into a normalised dictionary. The same code works across IOS-XE and NX-OS, which is most of the point.

**`netpipe/verify.py`:**

```python
#!/usr/bin/env python3
"""
Independent verification of applied changes.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from netpipe.models import Device, SiteIntent

logger = logging.getLogger("netpipe")

# Genie features we care about for an access-layer change
FEATURES = ("interface", "vlan")


@dataclass
class Finding:
    device: str
    severity: str        # "error" | "warning" | "info"
    subject: str
    detail: str


@dataclass
class VerifyReport:
    device: str
    reachable: bool = True
    findings: list[Finding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.reachable and not any(
            f.severity == "error" for f in self.findings)


def snapshot(testbed, device_name: str, label: str,
             directory: str = "artefacts/state") -> dict:
    """
    Learn operational state and write it to disk.

    `label` is typically 'before' or 'after'.
    """
    device = testbed.devices[device_name]
    device.connect(log_stdout=False, learn_hostname=True)

    state: dict = {}
    try:
        for feature in FEATURES:
            try:
                state[feature] = device.learn(feature).info
            except Exception as exc:      # a feature may be unsupported
                logger.warning("%s: could not learn %s: %s",
                               device_name, feature, exc)
                state[feature] = {}
    finally:
        device.disconnect()

    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{device_name}-{label}.json"
    path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")

    return state
```

!!! warning "Learning State Is Not Instant"
    `device.learn("interface")` on a 48-port switch runs several commands and parses all of them. Budget 10–30 seconds per feature per device, and learn only the features your change could plausibly affect. Learning `everything` on a large estate is how a five-minute verification becomes a forty-minute one and stops being run.

---

## ✅ The Checks

A snapshot is only useful when something compares it to an expectation. Three checks, in increasing order of how much they tell you.

Add to **`netpipe/verify.py`**:

```python
def check_intent_satisfied(device: Device, after: dict) -> list[Finding]:
    """Does operational state match what intent asked for?"""
    findings: list[Finding] = []
    interfaces = after.get("interface", {})

    for wanted in device.interfaces:
        actual = interfaces.get(wanted.name)

        if actual is None:
            findings.append(Finding(
                device.name, "warning", wanted.name,
                "not present in learned state"))
            continue

        # Administrative state
        enabled = actual.get("enabled", False)
        if wanted.enabled and not enabled:
            findings.append(Finding(
                device.name, "error", wanted.name,
                "intent says enabled, device reports shutdown"))
        elif not wanted.enabled and enabled:
            findings.append(Finding(
                device.name, "error", wanted.name,
                "intent says shutdown, device reports enabled"))

        # Access VLAN membership
        if wanted.mode == "access":
            actual_vlan = (actual.get("switchport_access_vlan")
                           or actual.get("access_vlan"))
            if actual_vlan and int(actual_vlan) != wanted.access_vlan:
                findings.append(Finding(
                    device.name, "error", wanted.name,
                    f"intent VLAN {wanted.access_vlan}, "
                    f"device reports VLAN {actual_vlan}"))

    return findings


def check_vlans_exist(device: Device, intent: SiteIntent,
                      after: dict) -> list[Finding]:
    """Every VLAN the site declares should exist on the switch."""
    findings: list[Finding] = []
    learned = after.get("vlan", {}).get("vlans", {})

    for vlan in intent.vlans:
        key = str(vlan.id)
        if key not in learned:
            findings.append(Finding(
                device.name, "error", f"vlan {vlan.id}",
                "declared in intent but not present on the device"))
            continue

        state = learned[key].get("state", "").lower()
        if state and state != "active":
            findings.append(Finding(
                device.name, "warning", f"vlan {vlan.id}",
                f"state is '{state}', expected 'active'"))

    return findings


def check_nothing_else_broke(device_name: str, before: dict,
                             after: dict) -> list[Finding]:
    """
    Did anything that was working before stop working?

    This is the check that catches collateral damage — the interface you
    weren't touching that went down because of a VLAN you removed.
    """
    findings: list[Finding] = []
    was = before.get("interface", {})
    now = after.get("interface", {})

    for name, previous in was.items():
        current = now.get(name)
        if current is None:
            findings.append(Finding(
                device_name, "warning", name,
                "present before the change, absent afterwards"))
            continue

        before_up = previous.get("oper_status") == "up"
        after_up = current.get("oper_status") == "up"

        if before_up and not after_up:
            findings.append(Finding(
                device_name, "error", name,
                f"was up before the change, now "
                f"{current.get('oper_status', 'unknown')}"))

    return findings


def verify_device(testbed, device: Device, intent: SiteIntent,
                  before: dict) -> VerifyReport:
    """Snapshot after the change and run every check."""
    report = VerifyReport(device.name)

    try:
        after = snapshot(testbed, device.name, "after")
    except Exception as exc:
        report.reachable = False
        report.findings.append(Finding(
            device.name, "error", "connection",
            f"could not verify: {exc}"))
        return report

    report.findings.extend(check_intent_satisfied(device, after))
    report.findings.extend(check_vlans_exist(device, intent, after))
    report.findings.extend(check_nothing_else_broke(device.name, before, after))

    return report
```

### `check_nothing_else_broke` is the one that earns the chapter

The first two checks confirm you got what you asked for. The third asks the question nobody asks until it's too late: **did anything else change?**

That's where real outages come from. You reconfigure four access ports, and the uplink goes down because the trunk's allowed-VLAN list no longer includes the native VLAN. Every check that only looks at the four ports you touched will report complete success while the switch is isolated.

It only works because you have a `before` snapshot. Which means taking one is not optional, and it has to happen before the deploy — not after you notice something is wrong.

!!! danger "Verification That Only Checks What You Changed Isn't Verification"
    A surprising number of automation suites assert exactly the lines they just pushed. That's a tautology with a test runner around it — it passes whenever the device is reachable, including when the change has broken the network.

    The minimum honest bar is: *what was working before is still working, and what I asked for is now true.* Both halves.

---

## 🖥️ The `verify` Command

`verify` needs a `before` snapshot, so it fits into the flow as two steps. Add to **`netpipe/cli.py`**:

```python
import json   # cli.py doesn't have this yet

from netpipe.testbed import build_testbed
from netpipe.verify import snapshot, verify_device


def cmd_snapshot(args: argparse.Namespace) -> int:
    """Capture operational state. Run this before deploying."""
    try:
        intent = load_intent(args.intent)
    except IntentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    settings = load_settings()
    testbed = build_testbed(intent, settings)

    print(f"Capturing '{args.label}' state for {intent.site}...\n")

    failures = 0
    for device in intent.devices:
        try:
            state = snapshot(testbed, device.name, args.label)
            counts = ", ".join(
                f"{len(value)} {key}" for key, value in state.items())
            print(f"  ✓ {device.name:<20} {counts}")
        except Exception as exc:
            print(f"  ✗ {device.name:<20} {exc}")
            failures += 1

    print(f"\nWritten to artefacts/state/*-{args.label}.json")
    return 1 if failures else 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify applied state against intent and the pre-change snapshot."""
    try:
        intent = load_intent(args.intent)
    except IntentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    settings = load_settings()
    testbed = build_testbed(intent, settings)

    print(f"Verifying {intent.site}...\n")

    reports = []
    for device in intent.devices:
        before_path = Path("artefacts/state") / f"{device.name}-before.json"
        if not before_path.exists():
            print(f"  ⚠ {device.name}: no 'before' snapshot — "
                  "collateral checks skipped")
            before = {}
        else:
            before = json.loads(before_path.read_text(encoding="utf-8"))

        reports.append(verify_device(testbed, device, intent, before))

    errors = 0
    for report in reports:
        mark = "✓" if report.passed else "✗"
        print(f"{mark} {report.device}")

        for finding in report.findings:
            symbol = {"error": "✗", "warning": "⚠", "info": "·"}[finding.severity]
            print(f"    {symbol} {finding.subject:<28} {finding.detail}")
            if finding.severity == "error":
                errors += 1

        if not report.findings:
            print("    · no findings")
        print()

    passed = [r for r in reports if r.passed]
    print(f"{len(passed)}/{len(reports)} device(s) verified, {errors} error(s)")

    return 1 if errors else 0
```

Register both:

```python
    snap = sub.add_parser("snapshot", parents=[common],
                          help="capture operational state")
    snap.add_argument("--label", default="before",
                      choices=["before", "after"],
                      help="which snapshot this is (default: %(default)s)")
    snap.set_defaults(func=cmd_snapshot)

    verify_cmd = sub.add_parser("verify", parents=[common],
                                help="verify state against intent")
    verify_cmd.set_defaults(func=cmd_verify)
```

---

## ▶️ Run It

The full sequence, with verification in its proper place:

```bash
python -m netpipe validate
python -m netpipe plan --show          # review the diff
python -m netpipe snapshot --label before
python -m netpipe deploy
python -m netpipe verify
```

**Snapshot:**

```
Capturing 'before' state for MAN1...

  ✓ man1-acc-sw-01      52 interface, 1 vlan
  ✓ man1-acc-sw-02      28 interface, 1 vlan

Written to artefacts/state/*-before.json
```

**A clean verification:**

```
Verifying MAN1...

✓ man1-acc-sw-01
    · no findings

✓ man1-acc-sw-02
    · no findings

2/2 device(s) verified, 0 error(s)
```

**A verification that earns its keep:**

```
Verifying MAN1...

✓ man1-acc-sw-01
    · no findings

✗ man1-acc-sw-02
    ✗ GigabitEthernet1/0/1        intent VLAN 10, device reports VLAN 1
    ✗ TenGigabitEthernet1/1/1     was up before the change, now down
    ⚠ vlan 30                     state is 'suspended', expected 'active'

1/2 device(s) verified, 2 error(s)
```

Read that second report carefully, because it's the case the whole chapter exists for. **The deploy succeeded.** Nornir was satisfied, every command was accepted, `write memory` returned cleanly. And the uplink is down.

Nothing before this chapter would have told you. `plan` showed a sensible diff, `preflight` passed every gate, `deploy` reported success. Only a comparison against operational state taken before the change reveals that the switch is now isolated.

---

## 🧪 Tests

The checks take plain dictionaries, so they test against saved state with no lab at all.

**`tests/test_verify.py`:**

```python
import pytest

from netpipe.intent import load_intent
from netpipe.verify import (
    check_intent_satisfied,
    check_nothing_else_broke,
    check_vlans_exist,
)


@pytest.fixture(scope="module")
def intent():
    return load_intent("intent/man1.yaml")


@pytest.fixture
def device(intent):
    return intent.devices[0]


def state_with(**interfaces):
    return {"interface": interfaces}


def test_matching_state_produces_no_findings(device):
    after = state_with(**{
        i.name: {
            "enabled": i.enabled,
            "oper_status": "up" if i.enabled else "down",
            "switchport_access_vlan": str(i.access_vlan or ""),
        }
        for i in device.interfaces
    })
    assert check_intent_satisfied(device, after) == []


def test_wrong_vlan_is_an_error(device):
    after = state_with(**{"GigabitEthernet1/0/1": {
        "enabled": True, "switchport_access_vlan": "1"}})
    findings = check_intent_satisfied(device, after)
    errors = [f for f in findings if f.severity == "error"]
    assert any("VLAN 1" in f.detail for f in errors)


def test_unexpected_shutdown_is_an_error(device):
    after = state_with(**{"GigabitEthernet1/0/1": {
        "enabled": False, "switchport_access_vlan": "10"}})
    findings = check_intent_satisfied(device, after)
    assert any("device reports shutdown" in f.detail for f in findings)


def test_port_that_should_be_shut_but_is_up(device):
    after = state_with(**{"GigabitEthernet1/0/9": {
        "enabled": True, "switchport_access_vlan": "999"}})
    findings = check_intent_satisfied(device, after)
    assert any("device reports enabled" in f.detail for f in findings)


def test_missing_vlan_is_an_error(device, intent):
    after = {"vlan": {"vlans": {"10": {"state": "active"},
                                "20": {"state": "active"}}}}
    findings = check_vlans_exist(device, intent, after)
    subjects = {f.subject for f in findings if f.severity == "error"}
    assert subjects == {"vlan 30", "vlan 999"}


def test_suspended_vlan_is_a_warning(device, intent):
    after = {"vlan": {"vlans": {
        str(v.id): {"state": "active"} for v in intent.vlans}}}
    after["vlan"]["vlans"]["30"]["state"] = "suspended"

    findings = check_vlans_exist(device, intent, after)
    assert [f.severity for f in findings] == ["warning"]


def test_interface_going_down_is_caught():
    before = state_with(**{"TenGigabitEthernet1/1/1": {"oper_status": "up"}})
    after = state_with(**{"TenGigabitEthernet1/1/1": {"oper_status": "down"}})

    findings = check_nothing_else_broke("sw1", before, after)
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert "was up before" in findings[0].detail


def test_interface_already_down_is_not_flagged():
    before = state_with(**{"GigabitEthernet1/0/9": {"oper_status": "down"}})
    after = state_with(**{"GigabitEthernet1/0/9": {"oper_status": "down"}})
    assert check_nothing_else_broke("sw1", before, after) == []


def test_interface_coming_up_is_not_flagged():
    before = state_with(**{"GigabitEthernet1/0/1": {"oper_status": "down"}})
    after = state_with(**{"GigabitEthernet1/0/1": {"oper_status": "up"}})
    assert check_nothing_else_broke("sw1", before, after) == []
```

The last two matter as much as the failures. A check that flags ports which were already down, or ports that came *up* as a result of your change, produces a report full of noise — and a report full of noise is a report nobody reads.

!!! tip "Keep Real Snapshots as Fixtures"
    Once you've run a snapshot against real hardware, commit a trimmed copy into `tests/fixtures/`. Genie's output shape varies between platforms and releases, and a captured real response is worth more than a hand-written dictionary you invented to make your own code pass.

---

## 📁 Where You Are

```
netpipe/
├── netpipe/
│   ├── cli.py            ← validate, plan, preflight, deploy, snapshot, verify
│   ├── testbed.py        ← intent to PyATS testbed          (new)
│   ├── verify.py         ← snapshots and checks             (new)
│   └── ...
├── artefacts/
│   ├── state/            ← before/after JSON                (new)
│   ├── testbed.yaml      ← generated                        (new)
│   └── ...
└── tests/
    └── test_verify.py                                       (new)
```

---

## 🎯 Key Takeaways

- ✅ **Accepted is not working** — Nornir's success means the commands parsed
- ✅ **Verify operational state, not configuration text** — `up/up`, not "the line is there"
- ✅ **Snapshot before you change** — There's no comparison without one
- ✅ **Check what you didn't touch** — Collateral damage is where outages come from
- ✅ **Don't flag improvements** — A noisy report is an unread report
- ✅ **Generate the testbed** — Same reason as the Nornir inventory
- ✅ **Keep real Genie output as fixtures** — Its shape is not something to guess at

---

## ➡️ Next

`verify` returned a non-zero exit code. Right now that's all it does — the broken change is still on the device, and nothing has recorded what happened.

[Chapter 7 — Rollback and the Audit Record](./07-rollback-and-audit.md) closes the loop.

---

[← Chapter 5 — Deploying with Nornir](./05-deploying-with-nornir.md) | [Chapter 7 — Rollback and the Audit Record →](./07-rollback-and-audit.md)
