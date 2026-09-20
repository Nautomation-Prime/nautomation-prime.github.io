---
title: Pydantic Data Validation for Network Automation
description: Use Pydantic v2 BaseModel to turn untrusted YAML, JSON and API data into typed, validated Python objects before your automation touches a device.
tags:
  - Intermediate
  - Pydantic
  - Validation
  - Data Modelling
  - Automation
  - Tutorial
---

## Pydantic Data Validation for Network Automation

## "From Hoping Your Data Is Right to Proving It — Typed Models at the Boundary"

You've modelled your intent in YAML and learned to exchange it as JSON. Both tutorials ended the same way: you loaded a file, got a Python dictionary back, and carried on. **Pydantic** is the step you're missing between "I loaded the data" and "I trust the data".

A dictionary will hold anything. It will happily hold VLAN 5000, an IP address with a typo, a `platfrom` key you misspelled at 23:40 during a change window, and an `mtu` of `"1500 "` with a trailing space from a copy-paste. None of that fails when you load it. It fails later — usually on the device, usually halfway through a loop, usually after you've already configured eleven switches.

**Why Pydantic belongs in your automation:**

- ✅ **Fail at the boundary, not on the device** — Bad data is rejected before a single SSH session opens
- ✅ **Types you can rely on** — `device.mgmt_ip` is an IP address object, not a string that looks like one
- ✅ **Errors an operator can act on** — Pydantic names the file, the host, the field and the reason
- ✅ **Self-documenting intent** — The model *is* the specification of what your data must look like
- ✅ **One tool, both formats** — The same model validates a YAML inventory and a JSON API response
- ✅ **Catches typos in keys** — The single highest-value check you can add to an inventory

**Real-world impact:** The difference between a change that fails safely in 0.2 seconds on your laptop and one that fails unsafely in 40 seconds across half a site.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ Why raw dictionaries are the wrong shape to build automation on
- ✅ Defining models with `BaseModel` and reading `ValidationError`
- ✅ Network-native field types (IP addresses, networks, constrained integers, literals)
- ✅ Nested models for devices, interfaces and VLANs
- ✅ Validating a complete YAML inventory file
- ✅ Custom rules with `@field_validator` and `@model_validator`
- ✅ Rejecting unknown keys with `extra="forbid"`
- ✅ Validating JSON API responses from a controller
- ✅ Handing a validated model to Jinja2
- ✅ When to reach for Pydantic and when to reach for JSON Schema

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [YAML Data Modelling](./yaml-data-modeling-network-automation.md)** — Structuring device intent
- ✅ **Completed [JSON Data Handling](./json-data-handling-network-automation.md)** — APIs and schema validation
- ✅ Comfortable with Python classes and type hints

### Required Software

```bash
# Create a virtual environment
python -m venv pydantic_venv
source pydantic_venv/bin/activate
# Windows PowerShell: .\pydantic_venv\Scripts\Activate.ps1
# Windows CMD: pydantic_venv\Scripts\activate.bat

# Install required packages
pip install "pydantic>=2.0" pyyaml requests jinja2
```

!!! warning "This Tutorial Is Pydantic v2"
    Pydantic v2 was a substantial rewrite, and a great deal of network automation content online still shows v1 syntax. If you copy an example from elsewhere and it uses `@validator`, `.dict()` or a nested `class Config:`, it is v1 and will not work here. There's a [migration table](#pydantic-v2-vs-v1-what-changed) at the end of this tutorial.

    Confirm your version before you start:

    ```bash
    python -c "import pydantic; print(pydantic.VERSION)"
    ```

### Required Access

- No device access required — every example in this tutorial runs offline

---

## 🔍 The Problem: What a Dictionary Costs You

In the YAML tutorial you wrote a validator that looked something like this:

```python
for host_name, host_data in hosts.items():
    if 'hostname' not in host_data:
        print(f"✗ Host '{host_name}' missing 'hostname' field")
        return False
```

That's honest code and it catches a real error. But look at what it *doesn't* catch. Here's an inventory that passes it completely:

```yaml
# inventory.yaml — every one of these is wrong, none of them are caught
core-sw-01:
  hostname: 10.1.1.300          # not a valid IP — .300 doesn't exist
  platform: ios
  mtu: "1500 "                  # string with trailing whitespace, not an int
  site: MAN1

dist-sw-01:
  hostname: 10.1.1.2
  platfrom: ios                 # typo — the real platform key is missing
  mtu: 9216
  site: MAN1

access-sw-01:
  hostname: 10.1.1.3
  platform: iso                 # transposed — no such platform
  mtu: 1500
  vlan: 5000                    # outside the valid 1–4094 range
  site: MAN1
```

Four defects. Your check returns `True`. The script proceeds.

The failures then surface in four different places at four different times: the IP fails when Netmiko tries to connect, the MTU string fails when Jinja2 renders `mtu 1500 ` into the config, the missing platform fails when Netmiko looks up a device driver, and VLAN 5000 fails *on the switch* — after you've already pushed to the first two devices.

Every one of those is knowable before you connect to anything. That's the entire argument for Pydantic.

---

## 🧱 Your First Model

A Pydantic model is a class. The annotations are the specification.

```python
#!/usr/bin/env python3
"""
A minimal device model.
"""

from pydantic import BaseModel, ValidationError


class Device(BaseModel):
    name: str
    hostname: str
    platform: str
    mtu: int


# Valid data — this works
device = Device(
    name="core-sw-01",
    hostname="10.1.1.1",
    platform="ios",
    mtu=1500,
)

print(device)
print(device.name)     # attribute access, not device['name']
print(device.mtu + 1)  # a real int — arithmetic just works
```

**Output:**

```
name='core-sw-01' hostname='10.1.1.1' platform='ios' mtu=1500
core-sw-01
1501
```

Now feed it something broken:

```python
try:
    Device(name="core-sw-01", hostname="10.1.1.1", platform="ios", mtu="not-a-number")
except ValidationError as e:
    print(e)
```

**Output:**

```
1 validation error for Device
mtu
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not-a-number', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/int_parsing
```

Three things to notice, because they're the whole value proposition:

1. **It failed immediately** — at construction, not at use.
2. **It named the field** — `mtu`, not "something went wrong".
3. **It showed the offending value** — `'not-a-number'`.

!!! tip "Coercion Is On by Default"
    `Device(..., mtu="1500")` succeeds and gives you `mtu=1500` as an integer. Pydantic coerces where the conversion is unambiguous and lossless. This is usually what you want with YAML, where a quoted number is a common accident. If you need to reject the string form outright, see [strict mode](#strictness-and-unknown-keys) later on.

---

## 🌐 Network-Native Field Types

`str` and `int` are a start, but `hostname: str` still accepts `10.1.1.300`. Pydantic ships types that understand the things networks are made of.

```python
#!/usr/bin/env python3
"""
A device model using network-aware types.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, IPvAnyAddress, IPvAnyNetwork

# A VLAN ID is an integer between 1 and 4094 — say so once, reuse everywhere
VlanId = Annotated[int, Field(ge=1, le=4094)]


class Device(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=63)]
    mgmt_ip: IPvAnyAddress
    mgmt_net: IPvAnyNetwork
    platform: Literal["ios", "iosxe", "nxos", "iosxr"]
    mtu: Annotated[int, Field(ge=1500, le=9216)]
    native_vlan: VlanId


device = Device(
    name="core-sw-01",
    mgmt_ip="10.1.1.1",
    mgmt_net="10.1.1.0/24",
    platform="iosxe",
    mtu=9216,
    native_vlan=999,
)

print(type(device.mgmt_ip))          # <class 'ipaddress.IPv4Address'>
print(device.mgmt_ip in device.mgmt_net)   # True — real network maths
```

**What each type buys you:**

| Type | Rejects | Gives you |
|---|---|---|
| `IPvAnyAddress` | `10.1.1.300`, `not-an-ip` | An `ipaddress.IPv4Address`/`IPv6Address` object |
| `IPvAnyNetwork` | `10.1.1.0/33`, host bits set | An `IPv4Network` you can iterate and compare |
| `Literal[...]` | `iso`, `IOS-XE`, `junos` | Guaranteed one of your supported platforms |
| `Field(ge=, le=)` | VLAN 5000, MTU 68 | An integer inside a range you decided |
| `Field(min_length=)` | Empty hostname | A string with actual content |

Now try each defect from the broken inventory:

```python
from pydantic import ValidationError

for bad in [
    {"mgmt_ip": "10.1.1.300"},   # invalid octet
    {"platform": "iso"},          # transposed platform
    {"native_vlan": 5000},        # out of range
    {"mtu": 68},                  # below the floor
]:
    payload = {
        "name": "test-sw", "mgmt_ip": "10.1.1.1", "mgmt_net": "10.1.1.0/24",
        "platform": "iosxe", "mtu": 1500, "native_vlan": 10,
    }
    payload.update(bad)
    try:
        Device(**payload)
    except ValidationError as e:
        print(f"{list(bad)[0]}: {e.errors()[0]['msg']}")
```

**Output:**

```
mgmt_ip: value is not a valid IPv4 or IPv6 address
platform: Input should be 'ios', 'iosxe', 'nxos' or 'iosxr'
native_vlan: Input should be less than or equal to 4094
mtu: Input should be greater than or equal to 1500
```

All four caught, offline, in milliseconds.

---

## 🏗️ Nested Models

Real inventory isn't flat. A device has interfaces; interfaces have VLANs. Models nest by using one model as another's type.

```python
#!/usr/bin/env python3
"""
Nested models: a device with interfaces and VLANs.
"""

from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, IPvAnyAddress

VlanId = Annotated[int, Field(ge=1, le=4094)]


class Vlan(BaseModel):
    id: VlanId
    name: Annotated[str, Field(min_length=1, max_length=32)]


class Interface(BaseModel):
    name: str
    description: str = ""                      # default — optional in the data
    mode: Literal["access", "trunk", "routed", "unused"]
    access_vlan: Optional[VlanId] = None
    ip_address: Optional[IPvAnyAddress] = None
    enabled: bool = True


class Device(BaseModel):
    name: str
    mgmt_ip: IPvAnyAddress
    platform: Literal["ios", "iosxe", "nxos", "iosxr"]
    vlans: list[Vlan] = []
    interfaces: list[Interface] = []


device = Device(
    name="access-sw-01",
    mgmt_ip="10.1.1.3",
    platform="iosxe",
    vlans=[
        {"id": 10, "name": "USERS"},
        {"id": 20, "name": "VOICE"},
    ],
    interfaces=[
        {"name": "GigabitEthernet1/0/1", "mode": "access", "access_vlan": 10},
        {"name": "GigabitEthernet1/0/2", "mode": "unused", "enabled": False},
    ],
)

print(device.vlans[0].name)              # USERS — typed all the way down
print(len(device.interfaces))            # 2
```

Note that you passed plain dictionaries for the nested items and got back `Vlan` and `Interface` objects. Pydantic validates recursively — a bad VLAN ID three levels deep is still caught, and the error tells you exactly where it was:

```python
from pydantic import ValidationError

try:
    Device(
        name="access-sw-01", mgmt_ip="10.1.1.3", platform="iosxe",
        vlans=[{"id": 10, "name": "USERS"}, {"id": 5000, "name": "BAD"}],
    )
except ValidationError as e:
    for err in e.errors():
        print(f"  at {' -> '.join(str(p) for p in err['loc'])}: {err['msg']}")
```

**Output:**

```
  at vlans -> 1 -> id: Input should be less than or equal to 4094
```

`vlans -> 1 -> id` is a path. That's what you print to an operator.

---

## 📂 Validating a YAML Inventory

Now put it together on a real file. This is the pattern you'll use most.

**`inventory.yaml`:**

```yaml
site: MAN1
devices:
  - name: core-sw-01
    mgmt_ip: 10.1.1.1
    platform: iosxe
    role: core
    vlans:
      - {id: 10, name: USERS}
      - {id: 20, name: VOICE}

  - name: access-sw-01
    mgmt_ip: 10.1.1.3
    platform: iosxe
    role: access
    interfaces:
      - {name: GigabitEthernet1/0/1, mode: access, access_vlan: 10}
      - {name: GigabitEthernet1/0/2, mode: unused, enabled: false}
```

**`models.py`:**

```python
#!/usr/bin/env python3
"""
Inventory models and a loader that fails fast with readable errors.
"""

import sys
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, ValidationError

VlanId = Annotated[int, Field(ge=1, le=4094)]


class Vlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: VlanId
    name: Annotated[str, Field(min_length=1, max_length=32)]


class Interface(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    mode: Literal["access", "trunk", "routed", "unused"]
    access_vlan: Optional[VlanId] = None
    ip_address: Optional[IPvAnyAddress] = None
    enabled: bool = True


class Device(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    mgmt_ip: IPvAnyAddress
    platform: Literal["ios", "iosxe", "nxos", "iosxr"]
    role: Literal["core", "distribution", "access", "edge"]
    vlans: list[Vlan] = []
    interfaces: list[Interface] = []


class Inventory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site: Annotated[str, Field(pattern=r"^[A-Z]{3}\d$")]
    devices: Annotated[list[Device], Field(min_length=1)]


def load_inventory(path: str) -> Inventory:
    """
    Load and validate an inventory file.

    Exits with a non-zero status and an operator-readable report if the
    file is malformed. Returns a fully typed Inventory on success.
    """
    try:
        with open(path) as handle:
            raw = yaml.safe_load(handle)
    except FileNotFoundError:
        sys.exit(f"✗ Inventory not found: {path}")
    except yaml.YAMLError as exc:
        sys.exit(f"✗ {path} is not valid YAML:\n  {exc}")

    try:
        return Inventory.model_validate(raw)
    except ValidationError as exc:
        print(f"✗ {path} failed validation ({exc.error_count()} problems):\n")
        for err in exc.errors():
            location = " -> ".join(str(part) for part in err["loc"])
            print(f"  {location}")
            print(f"      {err['msg']}")
            print(f"      you supplied: {err['input']!r}\n")
        sys.exit(1)


if __name__ == "__main__":
    inventory = load_inventory("inventory.yaml")
    print(f"✓ {inventory.site}: {len(inventory.devices)} devices validated")
    for device in inventory.devices:
        print(f"  {device.name:<16} {device.mgmt_ip}  {device.platform}")
```

**Output on a good file:**

```
✓ MAN1: 2 devices validated
  core-sw-01       10.1.1.1  iosxe
  access-sw-01     10.1.1.3  iosxe
```

**Output on the broken inventory from earlier:**

```
✗ inventory.yaml failed validation (4 problems):

  devices -> 0 -> mgmt_ip
      value is not a valid IPv4 or IPv6 address
      you supplied: '10.1.1.300'

  devices -> 1 -> platform
      Field required
      you supplied: {'name': 'dist-sw-01', 'mgmt_ip': '10.1.1.2', 'platfrom': 'ios', ...}

  devices -> 1 -> platfrom
      Extra inputs are not permitted
      you supplied: 'ios'

  devices -> 2 -> platform
      Input should be 'ios', 'iosxe', 'nxos' or 'iosxr'
      you supplied: 'iso'
```

Every defect, in one report, before anything connected to anything.

---

## ✍️ Custom Rules with Validators

Field types cover the general cases. Your naming standard and your design rules are yours, and they go in validators.

### Field validators — one field at a time

```python
import re

from pydantic import BaseModel, field_validator

HOSTNAME_PATTERN = re.compile(r"^[a-z]{3}\d-(core|dist|acc)-sw-\d{2}$")


class Device(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def enforce_naming_standard(cls, value: str) -> str:
        if not HOSTNAME_PATTERN.match(value):
            raise ValueError(
                f"'{value}' does not match the naming standard "
                "<site><n>-<role>-sw-<nn>, e.g. man1-core-sw-01"
            )
        return value
```

Two rules worth internalising: the method is a `@classmethod`, and you raise a plain `ValueError` — Pydantic catches it and folds it into the `ValidationError` report with the field location attached.

Validators can also normalise. Returning a changed value replaces the input:

```python
    @field_validator("name")
    @classmethod
    def normalise_case(cls, value: str) -> str:
        return value.strip().lower()   # "  MAN1-Core-SW-01 " -> "man1-core-sw-01"
```

!!! warning "Order Matters"
    Multiple validators on one field run in definition order. Put normalisation before enforcement, or you'll reject data you were about to fix.

### Model validators — rules that span fields

Some rules can't be checked one field at a time. An access port needs an access VLAN; a routed port must not have one.

```python
from typing import Literal, Optional

from pydantic import BaseModel, model_validator


class Interface(BaseModel):
    name: str
    mode: Literal["access", "trunk", "routed", "unused"]
    access_vlan: Optional[int] = None
    ip_address: Optional[str] = None

    @model_validator(mode="after")
    def check_mode_consistency(self):
        if self.mode == "access" and self.access_vlan is None:
            raise ValueError(f"{self.name}: access ports require an access_vlan")
        if self.mode == "routed" and self.ip_address is None:
            raise ValueError(f"{self.name}: routed ports require an ip_address")
        if self.mode == "routed" and self.access_vlan is not None:
            raise ValueError(f"{self.name}: routed ports cannot have an access_vlan")
        return self
```

`mode="after"` runs once every field has already been validated and converted, so you're comparing real values. Return `self`.

This is where a Pydantic model starts doing something a schema can't: it encodes *design rules*, not just shapes.

### Cross-referencing within the inventory

A model validator on the parent can check that children agree with each other — the check that catches the most real-world mistakes:

```python
class Device(BaseModel):
    name: str
    vlans: list[Vlan] = []
    interfaces: list[Interface] = []

    @model_validator(mode="after")
    def interfaces_reference_declared_vlans(self):
        declared = {vlan.id for vlan in self.vlans}
        for interface in self.interfaces:
            if interface.access_vlan and interface.access_vlan not in declared:
                raise ValueError(
                    f"{self.name}/{interface.name} uses VLAN {interface.access_vlan}, "
                    f"which is not declared on this device (declared: {sorted(declared)})"
                )
        return self
```

An interface assigned to a VLAN that was never created is a genuinely common outage. It costs you nine lines to make it impossible.

---

## 🔒 Strictness and Unknown Keys

`extra="forbid"` deserves its own section, because for inventory files it is the single highest-value setting in this tutorial.

By default Pydantic **ignores** keys it doesn't recognise. Your `platfrom` typo silently vanishes, the real `platform` field is reported missing, and — if `platform` happened to have a default — nothing is reported at all. You'd deploy with the wrong driver and no warning.

```python
from pydantic import BaseModel, ConfigDict


class Device(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # ...
```

| Setting | Behaviour | Use for |
|---|---|---|
| `extra="ignore"` (default) | Unknown keys silently dropped | API responses you don't control |
| `extra="forbid"` | Unknown keys raise an error | **Your own inventory and intent files** |
| `extra="allow"` | Unknown keys kept as attributes | Pass-through data you must preserve |

The rule of thumb: **forbid on data you author, ignore on data you receive.** You want to be told about your own typos. You don't want your automation to break because a vendor added a field to an API response.

For the inverse problem — a value that's the right shape but the wrong type, like `mtu: "1500"` — use strict mode where lossless coercion isn't acceptable:

```python
from typing import Annotated
from pydantic import Field

# Reject the string "1500"; require a real YAML integer
mtu: Annotated[int, Field(strict=True)]
```

Use this sparingly. With YAML in particular, coercion is usually a feature.

---

## 🌍 Validating API Responses

The same model validates JSON from a controller. This is the part that pays off the JSON tutorial.

```python
#!/usr/bin/env python3
"""
Validate a controller's device inventory response.
"""

from typing import Literal

import requests
from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, ValidationError


class ControllerDevice(BaseModel):
    # Controllers add fields between releases — ignore what we don't model
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    hostname: str
    management_ip: IPvAnyAddress = Field(alias="managementIpAddress")
    platform: str = Field(alias="platformId")
    reachability: Literal["Reachable", "Unreachable", "Ping Reachable"]
    uptime_seconds: int = Field(alias="upTime", default=0)


class ControllerResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    response: list[ControllerDevice]


def fetch_devices(base_url: str, token: str) -> list[ControllerDevice]:
    reply = requests.get(
        f"{base_url}/dna/intent/api/v1/network-device",
        headers={"X-Auth-Token": token},
        timeout=30,
    )
    reply.raise_for_status()

    try:
        parsed = ControllerResponse.model_validate_json(reply.text)
    except ValidationError as exc:
        raise RuntimeError(
            f"Controller returned data we don't understand:\n{exc}"
        ) from exc

    return parsed.response
```

Two details doing real work here:

**`Field(alias=...)`** lets the API keep its `managementIpAddress` camelCase while your code uses a sane `management_ip`. The ugly naming stops at the boundary instead of spreading through your codebase. (`populate_by_name=True` means you can still construct the model with `management_ip=...` in your own tests.)

**`model_validate_json()`** parses and validates in one step, which is faster than `json.loads()` followed by `model_validate()` because Pydantic v2's parser is implemented in Rust.

The wider point: an API response is untrusted input. A controller that returns `null` for a management IP will otherwise hand you a `None` that travels four function calls before failing somewhere unhelpful. Validate it where it arrives.

---

## 🎨 Handing a Validated Model to Jinja2

This is the join between this tutorial and the next one. Jinja2 renders from a validated model, not a raw dictionary.

```python
#!/usr/bin/env python3
"""
Render device configuration from a validated model.
"""

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from models import load_inventory

env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=StrictUndefined,   # unknown variable = error, not blank
)

inventory = load_inventory("inventory.yaml")
template = env.get_template("switch.j2")

for device in inventory.devices:
    config = template.render(device=device, site=inventory.site)
    with open(f"output/{device.name}.cfg", "w") as handle:
        handle.write(config)
    print(f"✓ rendered output/{device.name}.cfg")
```

**`templates/switch.j2`:**

```jinja2
hostname {{ device.name }}
!
{% for vlan in device.vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
!
{% for interface in device.interfaces %}
interface {{ interface.name }}
{% if interface.description %}
 description {{ interface.description }}
{% endif %}
{% if interface.mode == 'access' %}
 switchport mode access
 switchport access vlan {{ interface.access_vlan }}
{% elif interface.mode == 'unused' %}
 description UNUSED
 switchport mode access
 switchport access vlan 999
{% endif %}
{% if not interface.enabled %}
 shutdown
{% else %}
 no shutdown
{% endif %}
!
{% endfor %}
end
```

Note that the template uses **attribute access** — `device.name`, `interface.access_vlan` — because it's being handed objects. It reads better than `device['name']`, and combined with `StrictUndefined` a mistyped attribute in the template becomes a loud error rather than a blank line in a config file.

!!! danger "The `model_dump()` Gotcha"
    If you need a plain dictionary — to pass to a library, or to write out as JSON — `model_dump()` returns Python objects, not JSON-safe values. An `IPvAnyAddress` field comes back as an `ipaddress.IPv4Address`, which `json.dumps()` cannot serialise.

    ```python
    device.model_dump()                 # {'mgmt_ip': IPv4Address('10.1.1.1'), ...}
    device.model_dump(mode="json")      # {'mgmt_ip': '10.1.1.1', ...}  ← for JSON
    device.model_dump_json()            # '{"mgmt_ip": "10.1.1.1", ...}' ← a string
    ```

    Rendering with Jinja2 works either way because Jinja2 calls `str()` on values. Writing JSON does not. Reach for `mode="json"`.

---

## ⚖️ Pydantic or JSON Schema?

You learned JSON Schema in the [JSON tutorial](./json-data-handling-network-automation.md). Both validate data, and it's fair to ask which to use. They solve adjacent problems.

| | JSON Schema | Pydantic |
|---|---|---|
| Written in | JSON/YAML (language-neutral) | Python |
| Shareable with non-Python tools | ✅ Yes | ❌ No |
| Gives you typed objects | ❌ No — validates a dict, returns nothing | ✅ Yes |
| Custom logic | ⚠️ Limited to what the spec expresses | ✅ Arbitrary Python |
| Editor autocomplete | ❌ No | ✅ Yes |
| Publishable as a contract | ✅ That's its purpose | ✅ Via `model_json_schema()` |

**Use JSON Schema when** the schema is a contract that has to be read by something other than your Python code — a CI linter, a vendor's API documentation, another team's Go service, a VS Code YAML plugin giving your operators inline hints.

**Use Pydantic when** the data is entering your application and you want to work with it afterwards. Which, in an automation script, is nearly always.

You don't have to choose. A Pydantic model will generate the schema for you:

```python
import json
from models import Inventory

with open("inventory.schema.json", "w") as handle:
    json.dump(Inventory.model_json_schema(), handle, indent=2)
```

Commit that file, point your editor's YAML plugin at it, and your operators get autocomplete and inline errors while they're editing the inventory — from the same model that enforces the rules at runtime. One definition, two places it pays off.

---

## 🔑 Bonus: Settings and Credentials

`pydantic-settings` applies the same validation to configuration and environment variables, which pairs directly with the [credential management tutorial](./credential-management-network-automation.md):

```bash
pip install pydantic-settings
```

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AutomationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NETAUTO_", env_file=".env")

    username: str
    password: SecretStr
    vault_url: str = "https://vault.example.internal"
    max_workers: int = 10


settings = AutomationSettings()   # reads NETAUTO_USERNAME, NETAUTO_PASSWORD, ...

print(settings.password)                    # **********  — safe to log
print(settings.password.get_secret_value()) # the real value, only where needed
```

A missing `NETAUTO_PASSWORD` now fails at startup with a clear message rather than producing a confusing authentication failure on device seven. And `SecretStr` means an accidental `print(settings)` or a logged traceback shows `**********` instead of your enable password.

---

## 🔄 Pydantic v2 vs v1: What Changed

If you find an example online that doesn't work, check it against this table.

| v1 | v2 | Notes |
|---|---|---|
| `@validator("field")` | `@field_validator("field")` | Also needs `@classmethod` |
| `@root_validator` | `@model_validator(mode="after")` | Return `self`, not a dict |
| `class Config:` | `model_config = ConfigDict(...)` | Now an attribute |
| `.dict()` | `.model_dump()` | |
| `.json()` | `.model_dump_json()` | |
| `Model.parse_obj(d)` | `Model.model_validate(d)` | |
| `Model.parse_raw(s)` | `Model.model_validate_json(s)` | |
| `.schema()` | `.model_json_schema()` | |
| `conint(ge=1, le=4094)` | `Annotated[int, Field(ge=1, le=4094)]` | `conint` still works, `Annotated` preferred |
| `Optional[X]` implied optional | `Optional[X] = None` required | v2 no longer infers a `None` default |

That last row catches people out most often. In v2, `Optional[int]` means "may be `None`", not "may be omitted". If the field can be left out of the data, give it a default.

---

## 🏭 Production Patterns

### 1. One models module, imported everywhere

Define models in `models.py` and import them. The model is your data contract; having two definitions of a device is how they drift apart.

### 2. Validate once, at the edge

Validate immediately after loading a file or receiving a response. Everything downstream receives typed objects and should never re-check. If you find yourself writing `if device.mtu is None` deep in the code, the model was too loose.

### 3. Collect all errors, then exit

Pydantic reports every problem in one pass. Print the lot. An operator fixing four things in one edit is faster than four rounds of run-fix-run.

### 4. Version your models alongside your data

When the model gains a required field, existing inventory files become invalid. Either give the field a default or bump a `version` field in the data and handle both. Silent breakage at change time is worse than a schema you have to maintain.

### 5. Test your models

Models are logic and deserve the treatment the [testing tutorial](./testing-network-automation.md) describes:

```python
import pytest
from pydantic import ValidationError
from models import Interface


def test_access_port_requires_vlan():
    with pytest.raises(ValidationError, match="require an access_vlan"):
        Interface(name="Gi1/0/1", mode="access")


def test_routed_port_rejects_access_vlan():
    with pytest.raises(ValidationError, match="cannot have an access_vlan"):
        Interface(name="Gi1/0/1", mode="routed", ip_address="10.1.1.1", access_vlan=10)
```

Every rule you encode is a rule you can prove still holds.

### 6. Don't model what you don't use

It's tempting to model all sixty fields a controller returns. Model the ones you actually read, set `extra="ignore"`, and let the rest pass by. A smaller model is a smaller maintenance surface.

---

## 📚 Additional Resources

- **[Pydantic Documentation](https://docs.pydantic.dev/latest/)** — Official v2 documentation
- **[Pydantic Migration Guide](https://docs.pydantic.dev/latest/migration/)** — Full v1 to v2 changes
- **[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** — Configuration and environment variables
- **[Python typing Documentation](https://docs.python.org/3/library/typing.html)** — `Annotated`, `Literal`, `Optional`
- **[ipaddress Module](https://docs.python.org/3/library/ipaddress.html)** — What the IP field types return

---

## 🎯 Key Takeaways

- ✅ **Validate at the boundary** — Bad data should fail on your laptop, not on a device
- ✅ **The model is the specification** — Annotations document what your data must be
- ✅ **Network types catch network errors** — `IPvAnyAddress` and `Literal` reject what `str` accepts
- ✅ **`extra="forbid"` on your own files** — Typos in keys are the defect you'll actually hit
- ✅ **Validators encode design rules** — Not just shapes, but the rules your network runs on
- ✅ **One model, two formats** — The same class validates YAML intent and JSON responses
- ✅ **Errors name a path** — `devices -> 1 -> platform` is something an operator can fix
- ✅ **Pydantic v2 syntax only** — v1 examples will not run

---

## 🎓 Next Steps

You can now prove your data is correct before using it. Turn it into configuration:

1. **[Jinja2 Configuration Templates](./jinja2-configuration-templates.md)** (Recommended Next)
   - Render configs from the validated models you just built
   - Attribute access and `StrictUndefined` for safe templates

2. **[Health Checks and Pre-Flight Validation](./health-checks-pre-flight-validation.md)**
   - Data validation is the first pre-flight gate; add the device-state ones

3. **[Credential Management](./credential-management-network-automation.md)**
   - Apply `pydantic-settings` and `SecretStr` to your secrets handling

4. **[Testing Network Automation](./testing-network-automation.md)**
   - Prove your validation rules hold as the model evolves

---

> **Remember:** A dictionary tells you what someone typed. A model tells you what's true. Automation should only ever act on the second.

[← Back to JSON Tutorial](./json-data-handling-network-automation.md) | [Continue to Jinja2 Tutorial →](./jinja2-configuration-templates.md)
