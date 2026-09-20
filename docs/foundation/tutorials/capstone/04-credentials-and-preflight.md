---
title: "Capstone Chapter 4: Credentials and Pre-Flight"
description: Move secrets out of the codebase with pydantic-settings, then add the pre-flight gates that must pass before any configuration is written to a device.
tags:
  - Capstone
  - Credentials
  - Pre-Flight
  - Safety
  - Tutorial
---

## Chapter 4: Credentials and Pre-Flight

*Capstone chapter 4 of 7 — [project overview](./index.md)*

## "Everything That Must Be True Before You Write Anything"

Two problems, one chapter, because they're the same problem wearing different clothes: **things your automation assumed were true and never checked.**

It assumed credentials would be in the environment. It assumed the device would be reachable, would be the device you meant, would have room for a config file, and wouldn't be halfway through somebody else's change. Every one of those assumptions is a way for a change window to go wrong quietly.

---

## 🎯 What You'll Build

- `netpipe/settings.py` — validated configuration and secrets, out of the codebase
- `netpipe/preflight.py` — five gates that run before any write
- `netpipe preflight` — a pass/fail table an operator can read at a glance

**Builds on:** [Credential Management](../intermediate/credential-management-network-automation.md), [Health Checks and Pre-Flight Validation](../intermediate/health-checks-pre-flight-validation.md)

---

## 🔐 Settings and Secrets

Chapter 3 read `os.environ.get("NETAUTO_PASSWORD", "")` and carried on with an empty string if it wasn't there. That's how you get an authentication failure on device one and spend ten minutes suspecting the device.

**`netpipe/settings.py`:**

```python
#!/usr/bin/env python3
"""
Runtime configuration and credentials.

Values come from the environment or a .env file. Nothing here is ever
committed; .env is in .gitignore.
"""

from typing import Annotated, Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NETAUTO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Credentials — no defaults, deliberately
    username: Annotated[str, Field(min_length=1)]
    password: SecretStr
    enable_secret: SecretStr | None = None

    # Execution controls
    max_workers: Annotated[int, Field(ge=1, le=50)] = 10
    batch_size: Annotated[int, Field(ge=1, le=100)] = 5
    connect_timeout: Annotated[int, Field(ge=5, le=120)] = 20

    # Safety controls
    require_approval: bool = True
    min_free_flash_mb: Annotated[int, Field(ge=0)] = 20
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


def load_settings() -> Settings:
    """
    Load settings, failing immediately and clearly if anything is missing.
    """
    from pydantic import ValidationError

    try:
        return Settings()
    except ValidationError as exc:
        missing = [str(err["loc"][0]).upper() for err in exc.errors()
                   if err["type"] == "missing"]
        if missing:
            names = ", ".join(f"NETAUTO_{name}" for name in missing)
            raise SystemExit(
                f"✗ Missing required configuration: {names}\n"
                f"  Set them in your environment or in a .env file."
            ) from exc
        raise SystemExit(f"✗ Invalid configuration:\n{exc}") from exc
```

**`.env.example`** — commit this one, so the next person knows what's needed:

```bash
# Copy to .env and fill in. .env is gitignored.
NETAUTO_USERNAME=admin
NETAUTO_PASSWORD=
NETAUTO_ENABLE_SECRET=

# Optional overrides
NETAUTO_BATCH_SIZE=5
NETAUTO_MAX_WORKERS=10
NETAUTO_REQUIRE_APPROVAL=true
```

### Why `SecretStr`

```python
settings = load_settings()

print(settings)
# username='admin' password=SecretStr('**********') ...

print(settings.password)
# **********

connection_password = settings.password.get_secret_value()
# the actual value — only where it's needed
```

The value only appears when you explicitly ask for it. An accidental `print(settings)`, a logged exception, a debugger repr, a crash report posted in a support ticket — all of them show asterisks. You have to *mean it* to leak the password, and the `get_secret_value()` call is greppable in review.

!!! danger "This Is a Floor, Not a Ceiling"
    Environment variables and a `.env` file are the right starting point: they keep secrets out of git, which is the failure that actually happens. But they're still plaintext on disk, readable by anything running as you, and they don't rotate or audit.

    For production, `load_settings()` is where you swap in a real secret store. The [Secure Credential Vaulting](../expert/secure-credential-vaulting.md) tutorial covers HashiCorp Vault and AWS Secrets Manager, and the shape of this function doesn't change — only where the values come from. See also [Secrets and Credentials in Enterprise Automation](../../production-grade-network-automation-principles/secrets-and-credentials-in-enterprise-automation.md).

---

## 🚦 The Five Gates

A pre-flight check earns its place by answering one question: **would failing this have caused a bad change?** If the answer is no, it's noise, and noise in a pre-flight report trains people to skim it.

These five earn their place.

| Gate | Catches |
|---|---|
| **Reachable** | Device down, wrong IP, firewall, SSH disabled |
| **Identity** | Right IP, wrong device — the most dangerous failure here |
| **Config register** | A device that will boot to ROMMON or ignore its config |
| **Free flash** | `%Error opening flash:` halfway through saving |
| **No active session** | Someone else already changing this device |

**`netpipe/preflight.py`:**

```python
#!/usr/bin/env python3
"""
Pre-flight gates. Every one of these runs read-only, before any write.
"""

import re
import socket
from dataclasses import dataclass

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from netpipe.models import Device
from netpipe.settings import Settings

PLATFORM_DRIVER = {"ios": "cisco_ios", "iosxe": "cisco_ios", "nxos": "cisco_nxos"}


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass
class DeviceReport:
    device: str
    checks: list[CheckResult]

    @property
    def cleared(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failures(self) -> list[CheckResult]:
        return [check for check in self.checks if not check.passed]


# ── Individual gates ────────────────────────────────────────────────────

def check_reachable(device: Device, timeout: int = 5) -> CheckResult:
    """Is TCP/22 open?"""
    try:
        with socket.create_connection((str(device.mgmt_ip), 22), timeout):
            return CheckResult("reachable", True, f"{device.mgmt_ip}:22 open")
    except OSError as exc:
        return CheckResult("reachable", False, f"{device.mgmt_ip}:22 — {exc}")


def check_identity(device: Device, connection) -> CheckResult:
    """
    Is this the device we think it is?

    The single most important gate. An IP address that has been reassigned,
    a typo in intent, or a DHCP-reused management address all put you on a
    device you did not mean to configure — and every other check will pass
    happily while you do it.
    """
    prompt = connection.find_prompt().rstrip("#>").strip()

    if prompt.lower() != device.name.lower():
        return CheckResult(
            "identity", False,
            f"expected '{device.name}', device says '{prompt}'"
        )
    return CheckResult("identity", True, f"confirmed {prompt}")


def check_config_register(connection) -> CheckResult:
    """Will this device actually load its configuration on boot?"""
    output = connection.send_command("show version | include Configuration register")
    match = re.search(r"0x[0-9A-Fa-f]{4}", output)

    if not match:
        return CheckResult("config-register", True, "not reported (non-IOS?)")

    value = match.group(0).lower()
    if value not in ("0x2102", "0x0102"):
        return CheckResult(
            "config-register", False,
            f"{value} — device may ignore its startup config"
        )
    return CheckResult("config-register", True, value)


def check_free_flash(connection, minimum_mb: int) -> CheckResult:
    """Is there room to save?"""
    output = connection.send_command("show version | include bytes of memory|free")
    match = re.search(r"(\d+)\s+bytes\s+(?:total\s+)?\(\s*(\d+)\s+bytes free", output)

    if not match:
        output = connection.send_command("dir flash: | include bytes free")
        match = re.search(r"\((\d+)\s+bytes free", output)
        free_mb = int(match.group(1)) // (1024 * 1024) if match else None
    else:
        free_mb = int(match.group(2)) // (1024 * 1024)

    if free_mb is None:
        return CheckResult("free-flash", True, "could not determine (skipped)")

    if free_mb < minimum_mb:
        return CheckResult("free-flash", False,
                           f"{free_mb} MB free, need {minimum_mb} MB")
    return CheckResult("free-flash", True, f"{free_mb} MB free")


def check_no_active_session(connection, our_username: str) -> CheckResult:
    """Is anybody else logged in and configuring?"""
    output = connection.send_command("show users")
    lines = output.splitlines()

    # `show users` is fixed-width, and the Line column is itself several
    # tokens ("2 vty 0"), so splitting on whitespace picks the wrong field.
    # Locate the User column from the header instead.
    header = next((line for line in lines
                   if "User" in line and "Line" in line), None)
    if header is None:
        return CheckResult("no-active-session", True, "could not parse (skipped)")

    start = header.index("User")
    end = header.index("Host(s)") if "Host(s)" in header else start + 20

    others: set[str] = set()
    for line in lines[lines.index(header) + 1:]:
        if not line.strip():
            continue
        user = line[start:end].strip()
        if user and user != our_username:
            others.add(user)

    if others:
        return CheckResult("no-active-session", False,
                           f"also logged in: {', '.join(sorted(others))}")
    return CheckResult("no-active-session", True, "sole session")


# ── Orchestration ───────────────────────────────────────────────────────

def preflight_device(device: Device, settings: Settings) -> DeviceReport:
    """Run every gate against one device. Read-only throughout."""
    checks: list[CheckResult] = []

    reachable = check_reachable(device)
    checks.append(reachable)

    if not reachable.passed:
        # No point attempting the rest
        return DeviceReport(device.name, checks)

    try:
        connection = ConnectHandler(
            device_type=PLATFORM_DRIVER[device.platform],
            host=str(device.mgmt_ip),
            username=settings.username,
            password=settings.password.get_secret_value(),
            secret=(settings.enable_secret.get_secret_value()
                    if settings.enable_secret else ""),
            conn_timeout=settings.connect_timeout,
            fast_cli=False,
        )
    except NetmikoAuthenticationException:
        checks.append(CheckResult("authenticate", False, "credentials rejected"))
        return DeviceReport(device.name, checks)
    except NetmikoTimeoutException as exc:
        checks.append(CheckResult("authenticate", False, f"timed out: {exc}"))
        return DeviceReport(device.name, checks)

    checks.append(CheckResult("authenticate", True, f"as {settings.username}"))

    try:
        checks.append(check_identity(device, connection))
        checks.append(check_config_register(connection))
        checks.append(check_free_flash(connection, settings.min_free_flash_mb))
        checks.append(check_no_active_session(connection, settings.username))
    finally:
        connection.disconnect()

    return DeviceReport(device.name, checks)
```

### The identity gate deserves the attention

Every other check tells you whether a device is *healthy*. The identity check tells you whether it's the *right* device, and it's the only one where passing every other gate makes things worse rather than better.

Consider: a management IP gets reassigned during a data centre move, and nobody updates the intent file. Your pipeline connects successfully, authenticates successfully, finds plenty of flash, sees no other users — and then applies an access-layer template to whatever is now living at that address.

Comparing the device's own prompt to the name in intent costs one command. See [Validating Device Identity Before Automation Runs](../../production-grade-network-automation-principles/validating-device-identity-before-automation-runs.md).

!!! warning "Match the Gate to Your Environment"
    These five are examples of the *kind* of check worth running, not a universal list. `show users` parsing varies by platform and version. Config register doesn't exist on NX-OS. Your estate may care about something these ignore entirely — an unsaved running config, a pending reload, a specific software version, a maintenance window flag in your CMDB.

    The transferable part is the shape: **read-only, cheap, and each one answers "would failing this have caused a bad change?"**

!!! tip "Parse Fixed-Width Output by Column, Not by `split()`"
    `check_no_active_session` finds the `User` column from the header rather than taking `line.split()[2]`. That isn't fussiness — the Line field in `show users` is itself three tokens (`2 vty 0`), so the naive version returns `0` for every row and silently never detects anybody.

    It's the general hazard with screen-scraped CLI output: the code appears to work, the tests pass if you write them from the same wrong assumption, and the check quietly does nothing. Where a parser exists (TextFSM, or Genie in chapter 6), prefer it. Where you must scrape, anchor to the header.

---

## 🖥️ The `preflight` Command

Add to **`netpipe/cli.py`**:

```python
from concurrent.futures import ThreadPoolExecutor

from netpipe.preflight import DeviceReport, preflight_device
from netpipe.settings import load_settings


def cmd_preflight(args: argparse.Namespace) -> int:
    """Run pre-flight gates against every device in the intent."""
    try:
        intent = load_intent(args.intent)
    except IntentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    settings = load_settings()

    print(f"Pre-flight for {intent.site} ({len(intent.devices)} devices)\n")

    with ThreadPoolExecutor(max_workers=settings.max_workers) as pool:
        reports: list[DeviceReport] = list(pool.map(
            lambda device: preflight_device(device, settings),
            intent.devices,
        ))

    for report in reports:
        mark = "✓" if report.cleared else "✗"
        print(f"{mark} {report.device}")
        for check in report.checks:
            symbol = "✓" if check.passed else "✗"
            print(f"    {symbol} {check.name:<20} {check.detail}")
        print()

    cleared = [r for r in reports if r.cleared]
    blocked = [r for r in reports if not r.cleared]

    print(f"{len(cleared)} cleared, {len(blocked)} blocked")

    if blocked:
        print("\nBlocked devices will be skipped by deploy:")
        for report in blocked:
            reasons = ", ".join(check.name for check in report.failures)
            print(f"  {report.device}: {reasons}")

    return 1 if blocked else 0
```

Register it:

```python
    preflight = sub.add_parser("preflight", parents=[common],
                               help="run pre-flight gates (read-only)")
    preflight.set_defaults(func=cmd_preflight)
```

---

## ▶️ Run It

```bash
cp .env.example .env
# edit .env with your lab credentials
python -m netpipe preflight
```

**Everything healthy:**

```
Pre-flight for MAN1 (2 devices)

✓ man1-acc-sw-01
    ✓ reachable            10.1.1.11:22 open
    ✓ authenticate         as admin
    ✓ identity             confirmed man1-acc-sw-01
    ✓ config-register      0x2102
    ✓ free-flash           1421 MB free
    ✓ no-active-session    sole session

✓ man1-acc-sw-02
    ✓ reachable            10.1.1.12:22 open
    ✓ authenticate         as admin
    ✓ identity             confirmed man1-acc-sw-02
    ✓ config-register      0x2102
    ✓ free-flash           1380 MB free
    ✓ no-active-session    sole session

2 cleared, 0 blocked
```

**Something wrong:**

```
Pre-flight for MAN1 (2 devices)

✓ man1-acc-sw-01
    ✓ reachable            10.1.1.11:22 open
    ✓ authenticate         as admin
    ✓ identity             confirmed man1-acc-sw-01
    ✓ config-register      0x2102
    ✓ free-flash           1421 MB free
    ✓ no-active-session    sole session

✗ man1-acc-sw-02
    ✓ reachable            10.1.1.12:22 open
    ✓ authenticate         as admin
    ✗ identity             expected 'man1-acc-sw-02', device says 'man1-acc-sw-03'
    ✓ config-register      0x2102
    ✓ free-flash           1380 MB free
    ✗ no-active-session    also logged in: jsmith

1 cleared, 1 blocked

Blocked devices will be skipped by deploy:
  man1-acc-sw-02: identity, no-active-session
```

That second report is the chapter working. A change that would have reconfigured the wrong switch, while a colleague was logged into it, stopped before anything was written — and the operator can see precisely why in two lines.

**No credentials set:**

```
✗ Missing required configuration: NETAUTO_USERNAME, NETAUTO_PASSWORD
  Set them in your environment or in a .env file.
```

Compare that to chapter 3's behaviour: an empty string passed to Netmiko, and an authentication failure that looks like a device problem.

---

## 🧪 Tests

The gates take a connection object, so they can be tested against a fake one — no lab required.

**`tests/test_preflight.py`:**

```python
from dataclasses import dataclass

import pytest

from netpipe.models import Device
from netpipe.preflight import (
    check_config_register,
    check_free_flash,
    check_identity,
    check_no_active_session,
)


@dataclass
class FakeConnection:
    """Minimal stand-in for a Netmiko connection."""
    prompt: str = "man1-acc-sw-01#"
    responses: dict | None = None

    def find_prompt(self):
        return self.prompt

    def send_command(self, command):
        for fragment, reply in (self.responses or {}).items():
            if fragment in command:
                return reply
        return ""


@pytest.fixture
def device():
    return Device(name="man1-acc-sw-01", mgmt_ip="10.1.1.11",
                  platform="iosxe", role="access", model="C9300-48P")


def test_identity_passes_on_match(device):
    result = check_identity(device, FakeConnection())
    assert result.passed


def test_identity_fails_on_wrong_device(device):
    result = check_identity(device, FakeConnection(prompt="man1-acc-sw-99#"))
    assert not result.passed
    assert "man1-acc-sw-99" in result.detail


def test_identity_ignores_prompt_decoration(device):
    assert check_identity(device, FakeConnection(prompt="man1-acc-sw-01>")).passed
    assert check_identity(device, FakeConnection(prompt="MAN1-ACC-SW-01#")).passed


def test_config_register_flags_bad_value():
    conn = FakeConnection(responses={
        "Configuration register": "Configuration register is 0x2142"})
    result = check_config_register(conn)
    assert not result.passed
    assert "0x2142" in result.detail


def test_config_register_accepts_normal_value():
    conn = FakeConnection(responses={
        "Configuration register": "Configuration register is 0x2102"})
    assert check_config_register(conn).passed


def test_config_register_absent_is_not_a_failure():
    assert check_config_register(FakeConnection()).passed


def test_free_flash_blocks_when_low():
    conn = FakeConnection(responses={
        "dir flash:": "1935477760 bytes total (10485760 bytes free)"})
    result = check_free_flash(conn, minimum_mb=20)
    assert not result.passed
    assert "10 MB free" in result.detail


def test_free_flash_passes_when_ample():
    conn = FakeConnection(responses={
        "dir flash:": "1935477760 bytes total (1490587648 bytes free)"})
    assert check_free_flash(conn, minimum_mb=20).passed


def test_other_user_blocks():
    conn = FakeConnection(responses={"show users": (
        "    Line       User       Host(s)              Idle\n"
        "   1 vty 0     jsmith     idle                 00:00:12\n"
        "*  2 vty 1     admin      idle                 00:00:00\n"
    )})
    result = check_no_active_session(conn, our_username="admin")
    assert not result.passed
    assert "jsmith" in result.detail


def test_only_us_is_fine():
    conn = FakeConnection(responses={"show users": (
        "    Line       User       Host(s)              Idle\n"
        "*  2 vty 1     admin      idle                 00:00:00\n"
    )})
    assert check_no_active_session(conn, our_username="admin").passed
```

That fake connection is worth more than it looks. Every gate you add from here can be tested the same way, which means your pre-flight logic stays correct without a lab and without waiting for a real device to be in a bad state.

!!! tip "Test the Failure Path, Not Just the Happy One"
    `test_config_register_flags_bad_value` uses `0x2142` — the value set during password recovery. It's exactly the state a device gets left in after someone recovers it and forgets to set the register back, and it's exactly the device you don't want to push config to. That's what a pre-flight test should encode: the specific bad state you're guarding against, not a generic "returns False".

---

## 📁 Where You Are

```
netpipe/
├── .env                ← gitignored, real values
├── .env.example        ← committed, documents what's needed   (new)
├── netpipe/
│   ├── cli.py          ← validate, plan, preflight
│   ├── preflight.py    ← the gates                            (new)
│   ├── settings.py     ← validated config and secrets         (new)
│   └── ...
└── tests/
    └── test_preflight.py                                      (new)
```

You can also now delete the `os.environ.get` block from `cmd_plan` and use `load_settings()` there too.

---

## 🎯 Key Takeaways

- ✅ **Missing config fails at startup** — Not as a confusing device error later
- ✅ **`SecretStr` makes leaking deliberate** — Logs and tracebacks show asterisks
- ✅ **Identity is the gate that matters most** — Right IP, wrong device is the dangerous one
- ✅ **Every gate is read-only** — Pre-flight must be safe to run any time
- ✅ **A gate must justify itself** — "Would failing this have caused a bad change?"
- ✅ **Fake the connection, test the gates** — Pre-flight logic doesn't need a lab

---

## ➡️ Next

Validated intent. Rendered configs. A reviewed diff. Devices that have cleared every gate.

[Chapter 5 — Deploying with Nornir](./05-deploying-with-nornir.md) finally writes something.

---

[← Chapter 3 — Rendering Configuration](./03-rendering-configuration.md) | [Chapter 5 — Deploying with Nornir →](./05-deploying-with-nornir.md)
