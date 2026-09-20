---
title: "Capstone Chapter 2: Validating Intent"
description: Turn raw YAML into typed Pydantic models with naming standards, VLAN rules and design constraints encoded, so invalid intent can never reach a device.
tags:
  - Capstone
  - Pydantic
  - Validation
  - Tutorial
---

## Chapter 2: Validating Intent

*Capstone chapter 2 of 7 — [project overview](./index.md)*

## "The Gate That Decides Whether Anything Else Runs"

Chapter 1 gave you a dictionary. A dictionary is a container, not a contract — it holds whatever was typed into the file, including the mistakes.

This chapter replaces it with a model. By the end, `intent/man1.yaml` either loads as a fully typed object with every rule satisfied, or it doesn't load at all and tells you exactly why.

This is the most important chapter in the capstone. Everything after it assumes its data is correct, and it can only assume that because this chapter refuses to let anything else through.

---

## 🎯 What You'll Build

- `netpipe/models.py` — the complete data contract
- Interface expansion: forty-four undocumented ports become explicit `unused` state
- Site-wide cross-checks that no single device can perform on its own
- `netpipe validate` — the command CI will run on every pull request

**Builds on:** [Pydantic Data Validation](../intermediate/pydantic-data-validation-network-automation.md), [JSON Data Handling](../intermediate/json-data-handling-network-automation.md)

---

## 🧱 The Models

**`netpipe/models.py`:**

```python
#!/usr/bin/env python3
"""
The netpipe data contract.

Every rule the pipeline enforces about intent lives in this module.
If it isn't expressed here, it isn't enforced anywhere.
"""

import re
from typing import Annotated, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    IPvAnyAddress,
    field_validator,
    model_validator,
)

# ── Shared constrained types ────────────────────────────────────────────

VlanId = Annotated[int, Field(ge=1, le=4094)]
SiteCode = Annotated[str, Field(pattern=r"^[A-Z]{3}\d$")]

DEVICE_NAME = re.compile(r"^[a-z]{3}\d-(core|dist|acc)-sw-\d{2}$")

# Port counts we know how to expand. Extend as your estate does.
HARDWARE = {
    "C9300-24P": {"access_prefix": "GigabitEthernet1/0/", "access_ports": 24,
                  "uplink_prefix": "TenGigabitEthernet1/1/", "uplink_ports": 4},
    "C9300-48P": {"access_prefix": "GigabitEthernet1/0/", "access_ports": 48,
                  "uplink_prefix": "TenGigabitEthernet1/1/", "uplink_ports": 4},
}


# ── Leaf models ─────────────────────────────────────────────────────────

class Vlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: VlanId
    name: Annotated[str, Field(min_length=1, max_length=32,
                               pattern=r"^[A-Z0-9_-]+$")]
    description: str = ""


class Interface(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=3)]
    description: str = ""
    mode: Literal["access", "trunk", "routed", "unused"]
    access_vlan: Optional[VlanId] = None
    voice_vlan: Optional[VlanId] = None
    trunk_vlans: list[VlanId] = []
    ip_address: Optional[IPvAnyAddress] = None
    enabled: bool = True

    @model_validator(mode="after")
    def mode_implies_its_own_settings(self):
        name = self.name

        if self.mode == "access":
            if self.access_vlan is None:
                raise ValueError(f"{name}: access ports require access_vlan")
            if self.trunk_vlans:
                raise ValueError(f"{name}: access ports cannot have trunk_vlans")

        if self.mode == "trunk":
            if not self.trunk_vlans:
                raise ValueError(f"{name}: trunk ports require trunk_vlans")
            if self.access_vlan is not None:
                raise ValueError(f"{name}: trunk ports cannot have access_vlan")
            if self.voice_vlan is not None:
                raise ValueError(f"{name}: trunk ports cannot have voice_vlan")

        if self.mode == "routed":
            if self.ip_address is None:
                raise ValueError(f"{name}: routed ports require ip_address")
            if self.access_vlan or self.trunk_vlans or self.voice_vlan:
                raise ValueError(f"{name}: routed ports cannot have switchport VLANs")

        if self.voice_vlan is not None and self.access_vlan == self.voice_vlan:
            raise ValueError(f"{name}: voice_vlan must differ from access_vlan")

        return self


class Defaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain_name: str
    ntp_servers: Annotated[list[IPvAnyAddress], Field(min_length=1)]
    syslog_server: IPvAnyAddress
    unused_vlan: VlanId
    mtu: Annotated[int, Field(ge=1500, le=9216)] = 1500


# ── Device ──────────────────────────────────────────────────────────────

class Device(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    mgmt_ip: IPvAnyAddress
    platform: Literal["ios", "iosxe", "nxos"]
    role: Literal["core", "distribution", "access", "edge"]
    model: str
    interfaces: list[Interface] = []

    @field_validator("name")
    @classmethod
    def follows_naming_standard(cls, value: str) -> str:
        value = value.strip().lower()
        if not DEVICE_NAME.match(value):
            raise ValueError(
                f"'{value}' does not match the naming standard "
                "<site><n>-<role>-sw-<nn>, e.g. man1-acc-sw-01"
            )
        return value

    @field_validator("model")
    @classmethod
    def model_is_known(cls, value: str) -> str:
        if value not in HARDWARE:
            raise ValueError(
                f"unknown model '{value}'; known models: {sorted(HARDWARE)}"
            )
        return value

    @model_validator(mode="after")
    def interface_names_are_unique(self):
        seen: set[str] = set()
        for interface in self.interfaces:
            if interface.name in seen:
                raise ValueError(f"{self.name}: {interface.name} listed twice")
            seen.add(interface.name)
        return self


# ── Site ────────────────────────────────────────────────────────────────

class SiteIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[1]
    site: SiteCode
    description: str = ""
    change_reference: Annotated[str, Field(pattern=r"^CHG\d{7}$")]
    defaults: Defaults
    vlans: Annotated[list[Vlan], Field(min_length=1)]
    devices: Annotated[list[Device], Field(min_length=1)]

    # ── Site-wide rules ─────────────────────────────────────────────

    @model_validator(mode="after")
    def vlan_ids_are_unique(self):
        seen: set[int] = set()
        for vlan in self.vlans:
            if vlan.id in seen:
                raise ValueError(f"VLAN {vlan.id} declared more than once")
            seen.add(vlan.id)
        return self

    @model_validator(mode="after")
    def unused_vlan_is_declared(self):
        declared = {vlan.id for vlan in self.vlans}
        if self.defaults.unused_vlan not in declared:
            raise ValueError(
                f"defaults.unused_vlan is {self.defaults.unused_vlan}, "
                f"which is not in the site VLAN list {sorted(declared)}"
            )
        return self

    @model_validator(mode="after")
    def interfaces_only_use_declared_vlans(self):
        declared = {vlan.id for vlan in self.vlans}

        for device in self.devices:
            for interface in device.interfaces:
                used = set(interface.trunk_vlans)
                if interface.access_vlan:
                    used.add(interface.access_vlan)
                if interface.voice_vlan:
                    used.add(interface.voice_vlan)

                undeclared = used - declared
                if undeclared:
                    raise ValueError(
                        f"{device.name}/{interface.name} uses VLAN(s) "
                        f"{sorted(undeclared)} not declared at site "
                        f"{self.site} (declared: {sorted(declared)})"
                    )
        return self

    @model_validator(mode="after")
    def device_names_match_site(self):
        prefix = self.site.lower()
        for device in self.devices:
            if not device.name.startswith(prefix):
                raise ValueError(
                    f"{device.name} does not belong to site {self.site} "
                    f"(expected the name to start with '{prefix}')"
                )
        return self

    @model_validator(mode="after")
    def management_ips_are_unique(self):
        seen: dict[str, str] = {}
        for device in self.devices:
            key = str(device.mgmt_ip)
            if key in seen:
                raise ValueError(
                    f"{device.name} and {seen[key]} share management IP {key}"
                )
            seen[key] = device.name
        return self
```

### What the site-level validators earn you

Everything under "site-wide rules" is a check **no individual device can make**. A `Device` model can't know which VLANs the site declared or whether another switch has the same management address. That's why they live on the parent.

They're also the checks that catch the expensive mistakes. An interface in an undeclared VLAN is a port that comes up dead. Two devices sharing a management IP means your pipeline configures one box twice and reports success for both.

!!! tip "Where to Put a New Rule"
    Ask what the rule needs to see. One field? `@field_validator`. Several fields on one object? `@model_validator` on that model. Something about the whole site? `@model_validator` on `SiteIntent`. Putting it at the lowest level that can see everything it needs keeps the error messages specific.

---

## 🔌 Expanding the Unused Ports

Chapter 1 promised that the forty-four undescribed ports on a 48-port switch would become explicit state. This is where that happens.

Add to **`netpipe/models.py`**:

```python
def expand_interfaces(device: Device, unused_vlan: int) -> list[Interface]:
    """
    Return the device's full port inventory.

    Described interfaces are preserved exactly. Every other port the
    hardware has becomes an explicit 'unused' interface. Interfaces named
    in intent but absent from the hardware profile are kept and flagged
    by the caller, never silently dropped.
    """
    profile = HARDWARE[device.model]
    described = {interface.name: interface for interface in device.interfaces}

    expected: list[str] = [
        f"{profile['access_prefix']}{n}"
        for n in range(1, profile["access_ports"] + 1)
    ] + [
        f"{profile['uplink_prefix']}{n}"
        for n in range(1, profile["uplink_ports"] + 1)
    ]

    full: list[Interface] = []
    for name in expected:
        if name in described:
            full.append(described.pop(name))
        else:
            full.append(Interface(
                name=name,
                description="UNUSED",
                mode="unused",
                access_vlan=unused_vlan,
                enabled=False,
            ))

    # Anything left in `described` wasn't in the hardware profile.
    # Keep it — the operator meant something by it — but it's visible.
    full.extend(described.values())
    return full


def off_profile_interfaces(device: Device) -> list[str]:
    """Interface names in intent that the hardware profile doesn't contain."""
    profile = HARDWARE[device.model]
    expected = {
        f"{profile['access_prefix']}{n}"
        for n in range(1, profile["access_ports"] + 1)
    } | {
        f"{profile['uplink_prefix']}{n}"
        for n in range(1, profile["uplink_ports"] + 1)
    }
    return [i.name for i in device.interfaces if i.name not in expected]
```

Note that `unused` interfaces get `access_vlan=unused_vlan` and `enabled=False`. Chapter 3's template turns that into `switchport access vlan 999` and `shutdown`.

The design decision underneath: **an undocumented port is not an unknown port.** It has a defined state, and that state is "shut, in the parking VLAN". Leaving it out of the generated config means whatever was on it last stays on it, which is how a decommissioned server's port stays live in a user VLAN for three years.

!!! warning "This Is a Blast Radius Decision, Not a Cosmetic One"
    Expansion means your generated config touches every port on the switch, not just the ones in the intent file. That's deliberate — it's the difference between a config that *describes* the device and one that merely *adds to* it — but understand what you've chosen. Chapter 3's diff, and the human review it exists to enable, is the control that makes it safe. Don't skip it. See [Scoping Automation to Reduce Blast Radius](../../production-grade-network-automation-principles/scoping-automation-to-reduce-blast-radius.md).

---

## 📥 The Real Loader

Replace **`netpipe/intent.py`**:

```python
#!/usr/bin/env python3
"""
Load and validate site intent.
"""

from pathlib import Path

import yaml
from pydantic import ValidationError

from netpipe.models import SiteIntent, expand_interfaces


class IntentError(Exception):
    """Intent could not be loaded or did not satisfy the contract."""


def load_intent(path: str | Path, expand: bool = True) -> SiteIntent:
    """
    Read, parse and validate an intent file.

    Raises IntentError with a human-readable report on any failure.
    """
    path = Path(path)

    if not path.exists():
        raise IntentError(f"Intent file not found: {path}")

    try:
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise IntentError(f"{path} is not valid YAML:\n  {exc}") from exc

    if not isinstance(raw, dict):
        raise IntentError(f"{path} did not contain a YAML mapping")

    try:
        intent = SiteIntent.model_validate(raw)
    except ValidationError as exc:
        raise IntentError(format_validation_error(path, exc)) from exc

    if expand:
        for device in intent.devices:
            device.interfaces = expand_interfaces(
                device, intent.defaults.unused_vlan
            )

    return intent


def format_validation_error(path: Path, exc: ValidationError) -> str:
    """Render a ValidationError as something an operator can act on."""
    lines = [f"{path} failed validation ({exc.error_count()} problem(s)):", ""]

    for err in exc.errors():
        location = " -> ".join(str(part) for part in err["loc"])
        message = err["msg"].removeprefix("Value error, ")

        lines.append(f"  {location or 'site-wide'}")
        lines.append(f"      {message}")

        # A site-wide rule failed against the whole document; echoing it
        # back is noise. Only show the input for a specific field.
        if location:
            supplied = repr(err.get("input"))
            if len(supplied) > 80:
                supplied = supplied[:77] + "..."
            lines.append(f"      you supplied: {supplied}")

        lines.append("")

    return "\n".join(lines)
```

Three details worth calling out.

`removeprefix("Value error, ")` strips the wrapper Pydantic adds to messages raised from your own validators. Your carefully written "access ports require access_vlan" arrives as "Value error, access ports require access_vlan"; the operator doesn't need the noise.

Errors from a `@model_validator` on `SiteIntent` have an **empty** location — the rule failed against the whole document, not one field. Labelling those `site-wide` reads better than an empty line, and suppressing the "you supplied" for them matters a great deal: the input in that case *is* the entire intent file.

Truncating at 80 characters covers the remaining case, where a missing field makes Pydantic echo the whole device dictionary back at you.

---

## 🖥️ The `validate` Command

Add to **`netpipe/cli.py`**:

```python
from netpipe.intent import IntentError, load_intent
from netpipe.models import off_profile_interfaces


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate an intent file and report what it describes."""
    try:
        intent = load_intent(args.intent)
    except IntentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    print(f"✓ {args.intent} is valid\n")
    print(f"  Site:    {intent.site} — {intent.description}")
    print(f"  Change:  {intent.change_reference}")
    print(f"  VLANs:   {', '.join(str(v.id) for v in intent.vlans)}\n")

    warnings: list[str] = []

    for device in intent.devices:
        modes: dict[str, int] = {}
        for interface in device.interfaces:
            modes[interface.mode] = modes.get(interface.mode, 0) + 1

        summary = "  ".join(f"{count} {mode}"
                            for mode, count in sorted(modes.items()))
        print(f"  {device.name:<20} {device.model:<12} "
              f"{len(device.interfaces):>3} ports   {summary}")

        for name in off_profile_interfaces(device):
            warnings.append(
                f"{device.name}/{name} is not part of a {device.model} "
                "hardware profile — it will be configured, but check the name"
            )

    if warnings:
        print()
        for warning in warnings:
            print(f"  ⚠ {warning}")

    return 0
```

And register it in `build_parser()`, alongside `show`:

```python
    validate = sub.add_parser("validate", parents=[common],
                              help="validate an intent file")
    validate.set_defaults(func=cmd_validate)
```

`cmd_show` from chapter 1 imported `load_raw_intent`, which no longer exists. Either delete `cmd_show` — `validate` does everything it did and more — or point it at `load_intent`. This tutorial drops it.

For the same reason, update `tests/test_intent.py`: `load_raw_intent` is now `load_intent`, and a missing file raises `IntentError` rather than `FileNotFoundError`. The credentials tripwire test is unchanged and still earns its place.

---

## ▶️ Run It

```bash
python -m netpipe validate
```

**Output:**

```
✓ intent/man1.yaml is valid

  Site:    MAN1 — Manchester campus, building 1, access layer
  Change:  CHG0047821
  VLANs:   10, 20, 30, 999

  man1-acc-sw-01       C9300-48P     52 ports   3 access  1 trunk  48 unused
  man1-acc-sw-02       C9300-24P     28 ports   2 access  1 trunk  25 unused
```

Fifty-two ports from a file that described four. Every one of them now has a defined state.

### Now break it

Change `access_vlan: 10` to `access_vlan: 50` on the first interface and run again:

```
✗ intent/man1.yaml failed validation (1 problem(s)):

  site-wide
      man1-acc-sw-01/GigabitEthernet1/0/1 uses VLAN(s) [50] not declared
      at site MAN1 (declared: [10, 20, 30, 999])
```

Try a few more. Each one should stop the pipeline dead:

| Change | What you should see |
|---|---|
| `name: man1-access-sw-01` | Doesn't match the naming standard |
| `mgmt_ip: 10.1.1.300` | Not a valid IPv4 or IPv6 address |
| `model: C9200-48P` | Unknown model; known models: [...] |
| `change_reference: CHG123` | String should match pattern `^CHG\d{7}$` |
| Delete `mode:` from an interface | Field required |
| `platfrom: iosxe` | Extra inputs are not permitted |
| Give both switches `10.1.1.11` | Share management IP 10.1.1.11 |
| Set `unused_vlan: 900` | Not in the site VLAN list |

Eight classes of defect, none of which can now reach a device.

---

## 🧪 Tests

**`tests/test_models.py`:**

```python
import pytest
from pydantic import ValidationError

from netpipe.intent import load_intent
from netpipe.models import Device, Interface, expand_interfaces


def test_real_intent_validates():
    intent = load_intent("intent/man1.yaml")
    assert intent.site == "MAN1"
    assert len(intent.devices) == 2


def test_expansion_covers_every_port():
    intent = load_intent("intent/man1.yaml")
    by_name = {d.name: d for d in intent.devices}
    assert len(by_name["man1-acc-sw-01"].interfaces) == 52   # 48 + 4 uplinks
    assert len(by_name["man1-acc-sw-02"].interfaces) == 28   # 24 + 4 uplinks


def test_described_interfaces_survive_expansion():
    intent = load_intent("intent/man1.yaml")
    device = intent.devices[0]
    gi1 = next(i for i in device.interfaces
               if i.name == "GigabitEthernet1/0/1")
    assert gi1.description == "Desk 101"
    assert gi1.access_vlan == 10
    assert gi1.enabled is True


def test_undescribed_ports_are_shut_and_parked():
    intent = load_intent("intent/man1.yaml")
    device = intent.devices[0]
    gi9 = next(i for i in device.interfaces
               if i.name == "GigabitEthernet1/0/9")
    assert gi9.mode == "unused"
    assert gi9.enabled is False
    assert gi9.access_vlan == intent.defaults.unused_vlan


def test_access_port_without_vlan_rejected():
    with pytest.raises(ValidationError, match="require access_vlan"):
        Interface(name="Gi1/0/1", mode="access")


def test_trunk_with_access_vlan_rejected():
    with pytest.raises(ValidationError, match="cannot have access_vlan"):
        Interface(name="Gi1/0/1", mode="trunk",
                  trunk_vlans=[10], access_vlan=10)


def test_voice_vlan_must_differ():
    with pytest.raises(ValidationError, match="must differ from access_vlan"):
        Interface(name="Gi1/0/1", mode="access",
                  access_vlan=10, voice_vlan=10)


def test_naming_standard_enforced():
    with pytest.raises(ValidationError, match="naming standard"):
        Device(name="switch1", mgmt_ip="10.1.1.1", platform="iosxe",
               role="access", model="C9300-24P")


def test_duplicate_interface_rejected():
    with pytest.raises(ValidationError, match="listed twice"):
        Device(
            name="man1-acc-sw-01", mgmt_ip="10.1.1.1", platform="iosxe",
            role="access", model="C9300-24P",
            interfaces=[
                {"name": "Gi1/0/1", "mode": "access", "access_vlan": 10},
                {"name": "Gi1/0/1", "mode": "access", "access_vlan": 20},
            ],
        )
```

```bash
pytest tests/ -q
```

Every rule you encoded is now a rule you can prove still holds when someone edits the model in eight months.

---

## 🔁 Put It in CI

`validate` is designed to be the first thing your pipeline runs on a pull request. It needs no devices, no credentials and no network.

**`.github/workflows/validate.yml`:**

```yaml
name: Validate intent

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt pytest
      - run: pytest tests/ -q
      - run: python -m netpipe validate --intent intent/man1.yaml
```

An engineer proposing a VLAN change now finds out it's wrong in the pull request, not in the change window.

---

## 📁 Where You Are

```
netpipe/
├── intent/man1.yaml
├── netpipe/
│   ├── cli.py             ← show, validate
│   ├── intent.py          ← validating loader
│   └── models.py          ← the data contract  (new)
└── tests/
    ├── test_intent.py
    └── test_models.py     (new)
```

---

## 🎯 Key Takeaways

- ✅ **The model is the gate** — Nothing downstream re-checks, because nothing downstream has to
- ✅ **Rules live at the level that can see them** — Field, model, or site
- ✅ **Site-wide checks catch the expensive mistakes** — Undeclared VLANs, duplicate addresses
- ✅ **Expansion makes omission explicit** — An undocumented port has a defined state
- ✅ **Format errors for the person reading them** — Strip the wrappers, truncate the dumps
- ✅ **Validation belongs in CI** — No devices needed, so there's no excuse

---

## ➡️ Next

You have a validated, fully expanded description of what the site should be. Nothing has generated a single line of configuration yet.

[Chapter 3 — Rendering Configuration](./03-rendering-configuration.md) turns the models into candidate configs and shows you exactly what would change.

---

[← Chapter 1 — Intent and Repository Layout](./01-intent-and-repository-layout.md) | [Chapter 3 — Rendering Configuration →](./03-rendering-configuration.md)
