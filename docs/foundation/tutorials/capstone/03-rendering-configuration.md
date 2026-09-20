---
title: "Capstone Chapter 3: Rendering Configuration"
description: Generate candidate device configurations with Jinja2 from validated models, diff them against the running config, and produce a change plan a human can review.
tags:
  - Capstone
  - Jinja2
  - Templates
  - Change Planning
  - Tutorial
---

## Chapter 3: Rendering Configuration

*Capstone chapter 3 of 7 — [project overview](./index.md)*

## "Generate It, Then Show Someone What Would Change"

You have validated intent. Now turn it into configuration — and stop, before you send it anywhere.

This chapter produces two artefacts: a **candidate config** for each device, and a **diff** against what's currently running. The diff is the point. It's the last place a human can look at a change while it's still free to cancel it.

---

## 🎯 What You'll Build

- `templates/access_switch.j2` — the site's configuration standard, as a template
- `netpipe/render.py` — models in, candidate configs out
- `netpipe/diff.py` — candidate versus running, normalised
- `netpipe plan` — the read-only command an operator runs before every change

**Builds on:** [Jinja2 Configuration Templates](../intermediate/jinja2-configuration-templates.md)

---

## ✂️ Read and Write Are Different Commands

`plan` reads. `deploy` (chapter 5) writes. They're separate subcommands, and that separation is deliberate.

A single command that renders, diffs and pushes means the operator's only options are "all of it" or "none of it". Splitting them means the normal workflow is: run `plan`, read the diff, think, *then* run `deploy`. The pause is the control.

It also means `plan` is safe to run at any time, by anyone, including in CI on a pull request. A command nobody's afraid of is a command that gets used. See [Separating Read and Write Phases](../../production-grade-network-automation-principles/separating-read-and-write-phases.md).

---

## 📄 The Template

**`templates/access_switch.j2`:**

```jinja2
{#
Template: access_switch.j2
Purpose:  Full access-layer switch configuration for {{ site }}
Context:  device (Device), site (str), defaults (Defaults), vlans (list[Vlan])
Note:     This renders a COMPLETE interface configuration. Every physical
          port appears, including unused ones. See chapter 2 on expansion.
#}
hostname {{ device.name }}
!
ip domain name {{ defaults.domain_name }}
!
{% for server in defaults.ntp_servers %}
ntp server {{ server }}
{% endfor %}
!
logging host {{ defaults.syslog_server }}
!
{% for vlan in vlans %}
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
{% if interface.voice_vlan %}
 switchport voice vlan {{ interface.voice_vlan }}
{% endif %}
 spanning-tree portfast
 spanning-tree bpduguard enable
{% elif interface.mode == 'trunk' %}
 switchport mode trunk
 switchport trunk allowed vlan {{ interface.trunk_vlans | join(',') }}
{% elif interface.mode == 'unused' %}
 switchport mode access
 switchport access vlan {{ interface.access_vlan }}
 spanning-tree portfast
 spanning-tree bpduguard enable
{% elif interface.mode == 'routed' %}
 no switchport
 ip address {{ interface.ip_address }} {{ interface.ip_address | netmask }}
{% endif %}
{% if interface.enabled %}
 no shutdown
{% else %}
 shutdown
{% endif %}
!
{% endfor %}
end
```

### Template rules this project follows

**Templates have no logic beyond presentation.** Notice there's no `{% if interface.mode == 'access' and interface.access_vlan is none %}` guard — chapter 2 already made that state impossible. A template that re-checks its data is a template that has stopped trusting the model, and you end up with the rules in two places, disagreeing.

**Every branch is explicit.** `unused` gets its own block rather than falling through to a default. When you read a generated config for a shut port, you can point at the lines that produced it.

**Filters do the formatting.** `trunk_vlans | join(',')` turns `[10, 20, 30]` into `10,20,30`. Keep transformations in filters, not in the data.

---

## 🐍 The Renderer

**`netpipe/render.py`:**

```python
#!/usr/bin/env python3
"""
Render candidate configurations from validated intent.
"""

import ipaddress
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError

from netpipe.models import Device, SiteIntent


class RenderError(Exception):
    """A template failed to render."""


def netmask(address) -> str:
    """Jinja2 filter: the dotted-decimal mask for an interface address."""
    return str(ipaddress.ip_interface(f"{address}/24").netmask)


def build_environment(template_dir: str = "templates") -> Environment:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.filters["netmask"] = netmask
    return env


def render_device(intent: SiteIntent, device: Device,
                  env: Environment | None = None) -> str:
    """Render one device's candidate configuration."""
    env = env or build_environment()

    try:
        template = env.get_template("access_switch.j2")
        return template.render(
            device=device,
            site=intent.site,
            defaults=intent.defaults,
            vlans=intent.vlans,
        )
    except TemplateError as exc:
        raise RenderError(f"{device.name}: {exc}") from exc


def render_site(intent: SiteIntent,
                output_dir: str = "artefacts/candidate") -> dict[str, Path]:
    """
    Render every device at the site.

    Returns a mapping of device name to the file the config was written to.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    env = build_environment()
    written: dict[str, Path] = {}

    for device in intent.devices:
        config = render_device(intent, device, env)
        path = out / f"{device.name}.cfg"
        path.write_text(config, encoding="utf-8")
        written[device.name] = path

    return written
```

### The two settings that matter most

**`undefined=StrictUndefined`.** Without it, a typo like `{{ interface.acces_vlan }}` renders an empty string. You get `switchport access vlan` with no number — a line that is silently wrong and will be rejected by the device, or worse, accepted with a default. With it, you get a loud `UndefinedError` at render time and nothing is generated at all.

**`keep_trailing_newline=True`.** Jinja2 strips the final newline by default. A config file that doesn't end in one produces a spurious last-line difference in every diff you ever run.

!!! tip "One Template, or One Per Role?"
    This project uses one template because every device in the intent file is an access switch. When you add distribution switches, resist the urge to add `{% if device.role == 'distribution' %}` to this file — split it into `access_switch.j2` and `distribution_switch.j2` and pick by role in `render_device`. Templates grow branches faster than anything else in a codebase, and a template with six roles in it is unreadable and untestable.

---

## 🔍 The Diff

Comparing a generated config to a running config is harder than it looks, and it's worth being straight about why.

A device does not echo back what you sent it. It reorders, expands abbreviations, omits defaults, adds its own, and prepends a block of timestamps and version banners that changes every time you look. A naive `difflib` between candidate and running output produces hundreds of lines of noise on a device where nothing has actually changed.

So: normalise both sides first, and treat the result as **advisory**.

**`netpipe/diff.py`:**

```python
#!/usr/bin/env python3
"""
Compare candidate configuration against what's running on the device.

This diff is for HUMAN REVIEW. It is deliberately not used to make
automated decisions — see the note in the chapter text.
"""

import difflib
import re

# Lines that change on their own and say nothing about configuration
NOISE = (
    re.compile(r"^Building configuration"),
    re.compile(r"^Current configuration\s*:"),
    re.compile(r"^! Last configuration change"),
    re.compile(r"^! NVRAM config last updated"),
    re.compile(r"^ntp clock-period"),
    re.compile(r"^version \d"),
    re.compile(r"^\s*$"),
)


def normalise(config: str) -> list[str]:
    """Reduce a config to comparable lines."""
    lines: list[str] = []

    for raw in config.splitlines():
        line = raw.rstrip()

        if any(pattern.match(line) for pattern in NOISE):
            continue
        if line.strip() == "!":
            continue

        lines.append(line)

    return lines


def config_diff(candidate: str, running: str, device_name: str) -> list[str]:
    """Return a unified diff of running -> candidate, as a list of lines."""
    return list(difflib.unified_diff(
        normalise(running),
        normalise(candidate),
        fromfile=f"{device_name} (running)",
        tofile=f"{device_name} (candidate)",
        lineterm="",
        n=2,
    ))


def summarise(diff: list[str]) -> tuple[int, int]:
    """Count added and removed lines, ignoring the diff's own headers."""
    added = sum(1 for line in diff
                if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff
                  if line.startswith("-") and not line.startswith("---"))
    return added, removed
```

!!! danger "Never Gate a Deployment on This Diff"
    It's tempting to write `if not diff: skip_device()` and call it idempotency. Don't.

    A clean diff here means *the text matched after normalisation*. It does not mean the device is in the intended state — your normaliser might be hiding a real difference, or the device might be reporting a config it hasn't successfully applied.

    Config text comparison is a review aid. **Proof of state comes from chapter 6**, where PyATS reads what the device is actually doing rather than what it says it was told. The distinction between "the config says VLAN 10" and "the port is in VLAN 10 and forwarding" is the distinction between finished and working. See [Real-World Idempotency](../../production-grade-network-automation-principles/real-world-idempotency-in-network-automation.md).

---

## 📡 Fetching the Running Config

`plan` needs the current state to diff against. One small Netmiko helper — chapter 5 replaces it with the Nornir version.

**`netpipe/collect.py`:**

```python
#!/usr/bin/env python3
"""
Read-only collection from devices.
"""

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

from netpipe.models import Device

PLATFORM_DRIVER = {
    "ios": "cisco_ios",
    "iosxe": "cisco_ios",
    "nxos": "cisco_nxos",
}


class CollectionError(Exception):
    """Could not read from a device."""


def fetch_running_config(device: Device, username: str, password: str) -> str:
    """Retrieve the running configuration. Read-only."""
    try:
        with ConnectHandler(
            device_type=PLATFORM_DRIVER[device.platform],
            host=str(device.mgmt_ip),
            username=username,
            password=password,
            conn_timeout=20,
            fast_cli=False,
        ) as connection:
            return connection.send_command("show running-config")

    except NetmikoAuthenticationException as exc:
        raise CollectionError(f"{device.name}: authentication failed") from exc
    except NetmikoTimeoutException as exc:
        raise CollectionError(f"{device.name}: unreachable at {device.mgmt_ip}") from exc
```

Credentials are passed in as arguments here, and chapter 4 supplies them properly. Note that both Netmiko exceptions are caught and re-raised as one domain error with a message an operator can read — "authentication failed" rather than a stack trace ending in a socket module.

---

## 🖥️ The `plan` Command

Add to **`netpipe/cli.py`**:

```python
import os
from pathlib import Path

from netpipe.collect import CollectionError, fetch_running_config
from netpipe.diff import config_diff, summarise
from netpipe.render import RenderError, render_site


def cmd_plan(args: argparse.Namespace) -> int:
    """Render candidate configs and diff them against the devices."""
    try:
        intent = load_intent(args.intent)
    except IntentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    try:
        written = render_site(intent)
    except RenderError as exc:
        print(f"✗ render failed: {exc}", file=sys.stderr)
        return 1

    print(f"Rendered {len(written)} candidate configs to artefacts/candidate/\n")

    if args.offline:
        for name, path in written.items():
            lines = len(path.read_text(encoding="utf-8").splitlines())
            print(f"  {name:<20} {lines:>4} lines")
        print("\n(offline — no devices contacted, no diff produced)")
        return 0

    username = os.environ.get("NETAUTO_USERNAME", "")
    password = os.environ.get("NETAUTO_PASSWORD", "")
    if not username or not password:
        print("✗ set NETAUTO_USERNAME and NETAUTO_PASSWORD "
              "(chapter 4 does this properly)", file=sys.stderr)
        return 1

    diff_dir = Path("artefacts/diff")
    diff_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    changes = 0

    for device in intent.devices:
        candidate = written[device.name].read_text(encoding="utf-8")

        try:
            running = fetch_running_config(device, username, password)
        except CollectionError as exc:
            print(f"  ✗ {device.name:<20} {exc}")
            failures += 1
            continue

        diff = config_diff(candidate, running, device.name)

        if not diff:
            print(f"  = {device.name:<20} no textual difference")
            continue

        added, removed = summarise(diff)
        changes += 1
        (diff_dir / f"{device.name}.diff").write_text(
            "\n".join(diff) + "\n", encoding="utf-8")

        print(f"  ~ {device.name:<20} +{added} -{removed} lines")

        if args.show:
            print()
            for line in diff:
                print(f"    {line}")
            print()

    print(f"\n{changes} device(s) would change, {failures} unreachable")
    print("Diffs written to artefacts/diff/ — review before deploying")

    return 1 if failures else 0
```

Register it:

```python
    plan = sub.add_parser("plan", parents=[common],
                          help="render configs and diff against devices")
    plan.add_argument("--offline", action="store_true",
                      help="render only; do not contact devices")
    plan.add_argument("--show", action="store_true",
                      help="print the full diff, not just a summary")
    plan.set_defaults(func=cmd_plan)
```

---

## ▶️ Run It

No lab needed for the first one:

```bash
python -m netpipe plan --offline
```

**Output:**

```
Rendered 2 candidate configs to artefacts/candidate/

  man1-acc-sw-01        435 lines
  man1-acc-sw-02        242 lines

(offline — no devices contacted, no diff produced)
```

Look at what it generated:

```bash
head -30 artefacts/candidate/man1-acc-sw-01.cfg
```

```
hostname man1-acc-sw-01
!
ip domain name example.internal
!
ntp server 10.0.0.10
ntp server 10.0.0.11
!
logging host 10.0.0.20
!
vlan 10
 name USERS
vlan 20
 name VOICE
vlan 30
 name PRINTERS
vlan 999
 name PARKING
!
interface GigabitEthernet1/0/1
 description Desk 101
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
```

And further down, port 9 — which nobody described:

```bash
grep -A 8 "interface GigabitEthernet1/0/9$" artefacts/candidate/man1-acc-sw-01.cfg
```

```
interface GigabitEthernet1/0/9
 description UNUSED
 switchport mode access
 switchport access vlan 999
 spanning-tree portfast
 spanning-tree bpduguard enable
 shutdown
!
```

Chapter 2's expansion, arriving as configuration. Forty-four ports that were absent from the intent file now have a defined, deliberate, reviewable state.

### With a lab

```bash
export NETAUTO_USERNAME=admin
export NETAUTO_PASSWORD='...'
python -m netpipe plan --show
```

```
Rendered 2 candidate configs to artefacts/candidate/

  ~ man1-acc-sw-01       +61 -4 lines
  ~ man1-acc-sw-02       +38 -2 lines

2 device(s) would change, 0 unreachable
Diffs written to artefacts/diff/ — review before deploying
```

---

## 🧪 Tests

Rendering is testable without a device, which means it belongs in CI.

**`tests/test_render.py`:**

```python
import pytest
from jinja2 import UndefinedError

from netpipe.intent import load_intent
from netpipe.render import build_environment, render_device
from netpipe.diff import normalise, config_diff, summarise


@pytest.fixture(scope="module")
def intent():
    return load_intent("intent/man1.yaml")


def test_renders_without_error(intent):
    config = render_device(intent, intent.devices[0])
    assert config.startswith("hostname man1-acc-sw-01")
    assert config.rstrip().endswith("end")


def test_described_port_gets_its_vlan(intent):
    config = render_device(intent, intent.devices[0])
    assert "interface GigabitEthernet1/0/1" in config
    assert " switchport access vlan 10" in config
    assert " switchport voice vlan 20" in config


def test_unused_port_is_parked_and_shut(intent):
    config = render_device(intent, intent.devices[0])
    block = config.split("interface GigabitEthernet1/0/9\n")[1].split("!")[0]
    assert "switchport access vlan 999" in block
    assert "shutdown" in block
    assert "no shutdown" not in block


def test_trunk_vlans_are_comma_joined(intent):
    config = render_device(intent, intent.devices[0])
    assert " switchport trunk allowed vlan 10,20,30" in config


def test_every_physical_port_appears(intent):
    config = render_device(intent, intent.devices[0])
    assert config.count("\ninterface ") == 52


def test_strict_undefined_catches_template_typos(intent, tmp_path):
    (tmp_path / "access_switch.j2").write_text(
        "hostname {{ device.nmae }}\n", encoding="utf-8")
    env = build_environment(str(tmp_path))

    with pytest.raises(Exception) as caught:
        render_device(intent, intent.devices[0], env)
    assert "nmae" in str(caught.value)


def test_normalise_strips_noise():
    raw = (
        "Building configuration...\n"
        "Current configuration : 4231 bytes\n"
        "!\n"
        "! Last configuration change at 09:14:02 UTC Mon Sep 14 2026\n"
        "version 17.9\n"
        "hostname man1-acc-sw-01\n"
    )
    assert normalise(raw) == ["hostname man1-acc-sw-01"]


def test_identical_configs_produce_no_diff():
    config = "hostname sw1\n!\ninterface Gi1/0/1\n shutdown\n"
    assert config_diff(config, config, "sw1") == []


def test_summarise_ignores_headers():
    diff = config_diff("hostname sw2\n", "hostname sw1\n", "sw1")
    added, removed = summarise(diff)
    assert (added, removed) == (1, 1)
```

`test_every_physical_port_appears` is the one to keep. It's the regression test for chapter 2's expansion surviving a template change — if somebody adds a filter that accidentally skips unused ports, forty-four switch ports quietly revert to whatever they were before, and this test is what catches it.

---

## 📁 Where You Are

```
netpipe/
├── netpipe/
│   ├── cli.py          ← validate, plan
│   ├── collect.py      ← read-only device access   (new)
│   ├── diff.py         ← normalise and compare     (new)
│   ├── intent.py
│   ├── models.py
│   └── render.py       ← models to config          (new)
├── templates/
│   └── access_switch.j2                            (new)
├── artefacts/
│   ├── candidate/      ← generated configs
│   └── diff/           ← what would change
└── tests/
    └── test_render.py                              (new)
```

---

## 🎯 Key Takeaways

- ✅ **Render and deploy are separate commands** — The pause between them is the control
- ✅ **`StrictUndefined` always** — A template typo must be an error, never a blank
- ✅ **Templates don't re-validate** — The model already did; two copies of a rule will disagree
- ✅ **Normalise before diffing** — Devices don't echo back what you sent
- ✅ **The diff is advisory** — For humans to read, never for code to branch on
- ✅ **Rendering is testable offline** — So there's no reason it isn't in CI

---

## ➡️ Next

You've been exporting credentials into your shell, which is not a plan. And `plan` will happily try to configure a device that's about to fail for reasons nothing has checked.

[Chapter 4 — Credentials and Pre-Flight](./04-credentials-and-preflight.md) fixes both.

---

[← Chapter 2 — Validating Intent](./02-validating-intent.md) | [Chapter 4 — Credentials and Pre-Flight →](./04-credentials-and-preflight.md)
