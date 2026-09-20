---
title: "Capstone Chapter 1: Intent and Repository Layout"
description: Set up the netpipe project skeleton and write the YAML intent file that describes a site — the data every later chapter consumes.
tags:
  - Capstone
  - YAML
  - Project Structure
  - Tutorial
---

## Chapter 1: Intent and Repository Layout

*Capstone chapter 1 of 7 — [project overview](./index.md)*

## "Decide What Is Data Before You Write Any Code"

Every automation project makes one decision early that it lives with for years: **what is data and what is code?**

Get it right and adding a new site is editing a YAML file. Get it wrong and adding a new site means editing Python, which means testing Python, which means a code review and a release for something that should have been a pull request against a text file.

This chapter makes that decision explicitly, then builds the skeleton around it.

---

## 🎯 What You'll Build

- The `netpipe` package layout every later chapter fills in
- `intent/man1.yaml` — a complete description of a small access-layer site
- A loader that reads it and prints it back

**Builds on:** [YAML Data Modelling](../intermediate/yaml-data-modeling-network-automation.md)

---

## 🧭 The Data/Code Boundary

Here's the rule this project uses. It's not the only defensible one, but it is consistent, which matters more:

| Belongs in **data** (YAML) | Belongs in **code** (Python/Jinja2) |
|---|---|
| Which devices exist | How to connect to a device |
| What VLANs a site has | What a VLAN configuration block looks like |
| Which interface is in which VLAN | The rule that access ports need a VLAN |
| Site codes, naming, addressing | The naming standard's regular expression |
| Anything that differs per site | Anything that's the same everywhere |

The test to apply when you're unsure: **would a network engineer who doesn't write Python need to change this?** If yes, it's data.

!!! warning "The Failure Mode This Prevents"
    The most common shape of a doomed automation project is a Python file with a dictionary at the top containing site-specific values, "just for now". Six months later there are fourteen of them, three have drifted out of sync, and nobody can deploy a site without a developer. Draw the line now while the project is one file.

---

## 🏗️ Create the Skeleton

```bash
mkdir -p netpipe/{intent,netpipe,templates,inventory,tests,artefacts}
cd netpipe
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1

pip install "pydantic>=2.0" pydantic-settings pyyaml jinja2 \
            nornir nornir-netmiko nornir-utils netmiko rich
pip freeze > requirements.txt
```

Create the package marker and a `.gitignore` that keeps your secrets and generated files out of version control:

```bash
touch netpipe/__init__.py
cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.pyc
.env
artefacts/
EOF
git init && git add -A && git commit -m "netpipe: project skeleton"
```

!!! danger "artefacts/ Is Ignored on Purpose — For Now"
    Generated configs and diffs don't belong in git while you're developing; they'd churn on every run. Audit records are different, and chapter 7 discusses where those should actually go. Local-only is fine until then.

---

## 📝 Write the Intent File

This is the heart of the project. Everything downstream is a transformation of this file.

**`intent/man1.yaml`:**

```yaml
---
# Site intent for MAN1 — access layer
# This file describes what the site SHOULD look like.
# It does not describe how to achieve it.

version: 1
site: MAN1
description: Manchester campus, building 1, access layer
change_reference: CHG0047821

defaults:
  domain_name: example.internal
  ntp_servers:
    - 10.0.0.10
    - 10.0.0.11
  syslog_server: 10.0.0.20
  unused_vlan: 999
  mtu: 1500

vlans:
  - id: 10
    name: USERS
    description: General user access
  - id: 20
    name: VOICE
    description: IP telephony
  - id: 30
    name: PRINTERS
    description: Managed print devices
  - id: 999
    name: PARKING
    description: Shutdown holding VLAN for unused ports

devices:
  - name: man1-acc-sw-01
    mgmt_ip: 10.1.1.11
    platform: iosxe
    role: access
    model: C9300-48P
    interfaces:
      - name: GigabitEthernet1/0/1
        description: Desk 101
        mode: access
        access_vlan: 10
        voice_vlan: 20
      - name: GigabitEthernet1/0/2
        description: Desk 102
        mode: access
        access_vlan: 10
        voice_vlan: 20
      - name: GigabitEthernet1/0/3
        description: Print room
        mode: access
        access_vlan: 30
      - name: TenGigabitEthernet1/1/1
        description: Uplink to man1-dist-sw-01
        mode: trunk
        trunk_vlans: [10, 20, 30]

  - name: man1-acc-sw-02
    mgmt_ip: 10.1.1.12
    platform: iosxe
    role: access
    model: C9300-24P
    interfaces:
      - name: GigabitEthernet1/0/1
        description: Desk 201
        mode: access
        access_vlan: 10
        voice_vlan: 20
      - name: GigabitEthernet1/0/2
        description: Meeting room AV
        mode: access
        access_vlan: 10
      - name: TenGigabitEthernet1/1/1
        description: Uplink to man1-dist-sw-01
        mode: trunk
        trunk_vlans: [10, 20, 30]
```

### Five decisions worth noticing

**`version: 1` at the top.** When the schema changes — and it will — you need a way to tell an old file from a new one. It costs one line now and saves a guessing game later.

**`change_reference` is in the data.** The pipeline's audit record (chapter 7) needs to tie back to your change management system. Putting it in the intent file means the change number travels with the change, rather than being typed on a command line and mistyped at 02:00.

**Only exceptions are listed.** `man1-acc-sw-01` is a 48-port switch with four interfaces described. The other forty-four aren't an oversight — chapter 2 expands them into explicit `unused` state. Operators document what's special; the tool accounts for everything else. This is the same decision the [Cisco Config Generator](../../deep-dives/cisco-config-generator.md) makes, and for the same reason: a port omitted by accident and a port omitted deliberately must not produce different outcomes.

**`defaults` is a block, not repetition.** NTP servers are the same on every device at the site. Repeating them per device would guarantee they eventually differ.

**No credentials.** Not commented out, not placeholders — absent. Chapter 4 handles them properly. Anything you put in this file is going in git.

---

## 🐍 The Loader

A deliberately minimal one for now. Chapter 2 replaces its guts with Pydantic; this version exists so you can see the raw shape of what you've written.

**`netpipe/intent.py`:**

```python
#!/usr/bin/env python3
"""
Load raw site intent from YAML.

This is the chapter 1 version: it parses, and that's all. Chapter 2
replaces the return type with validated models.
"""

from pathlib import Path

import yaml


def load_raw_intent(path: str | Path) -> dict:
    """Read a YAML intent file and return it as a plain dictionary."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Intent file not found: {path}")

    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")

    return data
```

Note `yaml.safe_load`, not `yaml.load`. An intent file is input, and `yaml.load` can instantiate arbitrary Python objects. There is never a reason to use it here.

---

## 🖥️ A Front Door

Every chapter adds a subcommand. Set the pattern up now so there's somewhere to put them.

**`netpipe/cli.py`:**

```python
#!/usr/bin/env python3
"""
netpipe command line interface.
"""

import argparse
import sys

from netpipe.intent import load_raw_intent


def cmd_show(args: argparse.Namespace) -> int:
    """Print a summary of an intent file."""
    try:
        intent = load_raw_intent(args.intent)
    except (FileNotFoundError, ValueError) as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    print(f"Site:    {intent.get('site')}")
    print(f"Change:  {intent.get('change_reference')}")
    print(f"VLANs:   {len(intent.get('vlans', []))}")
    print(f"Devices: {len(intent.get('devices', []))}\n")

    for device in intent.get("devices", []):
        described = len(device.get("interfaces", []))
        print(f"  {device['name']:<20} {device['mgmt_ip']:<12} "
              f"{device.get('model', '?'):<12} {described} interfaces described")

    return 0


def build_parser() -> argparse.ArgumentParser:
    # Options every subcommand shares. Defining them on a parent parser
    # means `netpipe show --intent X` works — which is the order people
    # actually type. An argument on the top-level parser would only be
    # accepted *before* the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--intent",
        default="intent/man1.yaml",
        help="path to the site intent file (default: %(default)s)",
    )

    parser = argparse.ArgumentParser(
        prog="netpipe",
        description="Intent-driven configuration pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show", parents=[common],
                          help="summarise an intent file")
    show.set_defaults(func=cmd_show)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
```

Make it runnable as a module:

**`netpipe/__main__.py`:**

```python
import sys

from netpipe.cli import main

sys.exit(main())
```

---

## ▶️ Run It

```bash
python -m netpipe show
```

**Output:**

```
Site:    MAN1
Change:  CHG0047821
VLANs:   4
Devices: 2

  man1-acc-sw-01       10.1.1.11    C9300-48P    4 interfaces described
  man1-acc-sw-02       10.1.1.12    C9300-24P    3 interfaces described
```

No devices touched, nothing installed beyond PyYAML. That's chapter 1 working.

!!! warning "Windows: `UnicodeEncodeError` on the Tick Characters"
    If you're on Windows and the first `✓` throws `UnicodeEncodeError: 'charmap' codec can't encode character '✓'`, your console is running the legacy cp1252 code page. The code is fine; the terminal can't render it.

    Fix it for the session:

    ```powershell
    $env:PYTHONUTF8 = "1"
    ```

    Or permanently, by adding this to the top of `netpipe/__main__.py`:

    ```python
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ```

    Worth doing now — every remaining chapter prints status symbols.

---

## 🧪 Prove the Boundary Holds

One test, to lock in the decision this chapter made:

**`tests/test_intent.py`:**

```python
import pytest

from netpipe.intent import load_raw_intent


def test_loads_real_intent_file():
    intent = load_raw_intent("intent/man1.yaml")
    assert intent["site"] == "MAN1"
    assert len(intent["devices"]) == 2


def test_missing_file_is_a_clear_error():
    with pytest.raises(FileNotFoundError, match="Intent file not found"):
        load_raw_intent("intent/nope.yaml")


def test_no_credentials_in_intent():
    """Intent is committed to git. Secrets must never appear in it."""
    with open("intent/man1.yaml", encoding="utf-8") as handle:
        content = handle.read().lower()

    for forbidden in ("password", "secret", "enable_pass", "api_key", "token"):
        assert forbidden not in content, f"'{forbidden}' found in intent file"
```

```bash
pip install pytest
pytest tests/ -q
```

That third test is not a joke test. It's a tripwire, it costs nothing to run in CI, and it will catch the day somebody adds a `password:` key because it was the fastest way to get their change out.

---

## 📁 Where You Are

```
netpipe/
├── .gitignore
├── requirements.txt
├── intent/
│   └── man1.yaml          ← the site, described
├── netpipe/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py             ← show
│   └── intent.py          ← raw loader
├── templates/             (empty — chapter 3)
├── inventory/             (empty — chapter 5)
├── tests/
│   └── test_intent.py
└── artefacts/             (empty — chapter 3 onwards)
```

---

## 🎯 Key Takeaways

- ✅ **Decide data vs code once, early** — The boundary is expensive to move later
- ✅ **Intent describes the destination**, never the route to it
- ✅ **Version your intent format** — One line now, no archaeology later
- ✅ **Document exceptions, derive the rest** — Omission must be deliberate, not accidental
- ✅ **Never put secrets in intent** — It's committed; test that it stays clean
- ✅ **`yaml.safe_load`, always** — `yaml.load` executes what it reads

---

## ➡️ Next

Right now nothing checks any of this. `mgmt_ip` could be `banana`, `access_vlan` could be 5000, and `show` would print it happily.

[Chapter 2 — Validating Intent](./02-validating-intent.md) turns the file into typed models that refuse to load when they're wrong.

---

[← Capstone Overview](./index.md) | [Chapter 2 — Validating Intent →](./02-validating-intent.md)
