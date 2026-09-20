---
title: "Capstone Chapter 5: Deploying with Nornir"
description: Push configuration in batches with Nornir, using decorators for retry, rate limiting and audit logging, with a dry run that proves the path before it writes.
tags:
  - Capstone
  - Nornir
  - Decorators
  - Deployment
  - Tutorial
---

## Chapter 5: Deploying with Nornir

*Capstone chapter 5 of 7 — [project overview](./index.md)*

## "The Write Phase, and Everything That Stops It Going Too Far"

Four chapters of preparation, and now the one that changes something.

The work here isn't pushing config — Nornir does that in about six lines. The work is arranging for a failure to affect two devices instead of two hundred, for a transient SSH drop to retry rather than abort, and for every action to leave a trace.

---

## 🎯 What You'll Build

- A Nornir inventory generated from your validated intent — one source of truth, not two
- Decorators for retry, timing and audit logging
- `netpipe/deploy.py` — batched deployment with a backup taken first
- `netpipe deploy` — with `--dry-run` as the default habit

**Builds on:** [Nornir Fundamentals](../intermediate/nornir-fundamentals.md), [Decorators in Network Automation](../intermediate/decorators-network-automation.md)

---

## 📇 Generate the Inventory, Don't Maintain One

Nornir wants `hosts.yaml`, `groups.yaml` and `defaults.yaml`. You already have every fact those files need, in `intent/man1.yaml`, validated.

Maintaining both means maintaining a divergence. Generate the Nornir inventory instead.

**`netpipe/inventory.py`:**

```python
#!/usr/bin/env python3
"""
Build a Nornir inventory from validated intent.

The intent file is the source of truth. These files are build output and
are regenerated on every run — never edit them by hand.
"""

from pathlib import Path

import yaml
from nornir import InitNornir
from nornir.core import Nornir

from netpipe.models import SiteIntent
from netpipe.settings import Settings

PLATFORM_DRIVER = {"ios": "cisco_ios", "iosxe": "cisco_ios", "nxos": "cisco_nxos"}


def write_inventory(intent: SiteIntent, directory: str = "inventory") -> Path:
    """Write hosts/groups/defaults from intent. Returns the directory."""
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)

    hosts = {
        device.name: {
            "hostname": str(device.mgmt_ip),
            "platform": PLATFORM_DRIVER[device.platform],
            "groups": [device.role],
            "data": {
                "site": intent.site,
                "model": device.model,
                "change_reference": intent.change_reference,
            },
        }
        for device in intent.devices
    }

    groups = {
        role: {"data": {"role": role}}
        for role in sorted({device.role for device in intent.devices})
    }

    (out / "hosts.yaml").write_text(
        yaml.safe_dump(hosts, sort_keys=True), encoding="utf-8")
    (out / "groups.yaml").write_text(
        yaml.safe_dump(groups, sort_keys=True), encoding="utf-8")
    (out / "defaults.yaml").write_text(
        yaml.safe_dump({"data": {"site": intent.site}}), encoding="utf-8")

    return out


def build_nornir(intent: SiteIntent, settings: Settings) -> Nornir:
    """Initialise Nornir from generated inventory, with runtime credentials."""
    directory = write_inventory(intent)

    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {"num_workers": settings.max_workers},
        },
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": str(directory / "hosts.yaml"),
                "group_file": str(directory / "groups.yaml"),
                "defaults_file": str(directory / "defaults.yaml"),
            },
        },
        logging={"enabled": False},   # we do our own — see below
    )

    # Credentials are injected at runtime and never written to disk
    nr.inventory.defaults.username = settings.username
    nr.inventory.defaults.password = settings.password.get_secret_value()

    return nr
```

The critical line is near the bottom: **credentials are set on the in-memory inventory**, never written into `hosts.yaml`. A generated inventory file is a file somebody will eventually commit by accident; make sure there's nothing in it worth leaking.

Add `inventory/` to `.gitignore` for the same reason it's build output.

---

## 🎀 Decorators

Three concerns that apply to every device operation and belong in none of them. This is what [the decorators tutorial](../intermediate/decorators-network-automation.md) was preparing you for.

**`netpipe/decorators.py`:**

```python
#!/usr/bin/env python3
"""
Cross-cutting concerns for device operations.
"""

import functools
import json
import logging
import random
import time
from datetime import datetime, timezone

logger = logging.getLogger("netpipe")


def retry(attempts: int = 3, base_delay: float = 2.0,
          exceptions: tuple = (Exception,)):
    """
    Retry with exponential backoff and jitter.

    Only for transient failures. A rejected command is not transient —
    retrying it three times just means being wrong three times.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last: Exception | None = None

            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last = exc
                    if attempt == attempts:
                        break
                    delay = base_delay * (2 ** (attempt - 1))
                    delay += random.uniform(0, delay * 0.1)   # jitter
                    logger.warning(
                        "%s failed (attempt %d/%d): %s — retrying in %.1fs",
                        func.__name__, attempt, attempts, exc, delay,
                    )
                    time.sleep(delay)

            raise last

        return wrapper
    return decorator


def audited(action: str):
    """
    Emit a structured record of an operation, whatever its outcome.

    Every write the pipeline performs passes through here. Chapter 7
    collects these into the change's audit artefact.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(task, *args, **kwargs):
            started = datetime.now(timezone.utc)
            record = {
                "timestamp": started.isoformat(),
                "action": action,
                "device": task.host.name,
                "site": task.host.get("site"),
                "change_reference": task.host.get("change_reference"),
            }

            try:
                result = func(task, *args, **kwargs)
                record["outcome"] = "success"
                return result
            except Exception as exc:
                record["outcome"] = "failure"
                record["error"] = f"{type(exc).__name__}: {exc}"
                raise
            finally:
                record["duration_s"] = round(
                    (datetime.now(timezone.utc) - started).total_seconds(), 2)
                logger.info(json.dumps(record))

        return wrapper
    return decorator
```

!!! warning "Retry Is Not a Substitute for Correctness"
    `retry` is wrapped around *connection* failures only, never around the configuration push itself. A dropped SSH session is worth retrying. A command the device rejected is not — the second attempt fails identically, and the third leaves you with three identical errors in the log and no more information than you had after the first.

    Worse, retrying a partially-applied configuration can compound the damage. Retry transport, not intent.

---

## 🚀 The Deployment Task

**`netpipe/deploy.py`:**

```python
#!/usr/bin/env python3
"""
The write phase.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

from netpipe.decorators import audited, retry
from netpipe.models import SiteIntent
from netpipe.settings import Settings

logger = logging.getLogger("netpipe")


@dataclass
class DeployOutcome:
    succeeded: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)
    backups: dict[str, Path] = field(default_factory=dict)


# ── Nornir tasks ────────────────────────────────────────────────────────

@audited("backup")
@retry(attempts=3, base_delay=2.0)
def task_backup(task: Task) -> Result:
    """Save the running config before touching anything."""
    reply = task.run(
        task=netmiko_send_command,
        command_string="show running-config",
        read_timeout=120,
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = Path("artefacts/backup") / f"{task.host.name}-{stamp}.cfg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(reply.result, encoding="utf-8")

    return Result(host=task.host, result=str(path))


@audited("configure")
def task_configure(task: Task, candidate_dir: str) -> Result:
    """Apply the candidate configuration."""
    candidate = Path(candidate_dir) / f"{task.host.name}.cfg"
    lines = [
        line for line in candidate.read_text(encoding="utf-8").splitlines()
        if line.strip() and line.strip() not in ("!", "end")
    ]

    reply = task.run(
        task=netmiko_send_config,
        config_commands=lines,
        read_timeout=180,
    )

    return Result(host=task.host, result=reply.result, changed=True)


@audited("save")
@retry(attempts=2, base_delay=3.0)
def task_save(task: Task) -> Result:
    """Write the running config to startup."""
    reply = task.run(
        task=netmiko_send_command,
        command_string="write memory",
        read_timeout=120,
    )
    return Result(host=task.host, result=reply.result)


# ── Orchestration ───────────────────────────────────────────────────────

def deploy_batch(nr, candidate_dir: str, outcome: DeployOutcome) -> None:
    """Back up, configure and save one batch of devices."""
    backup = nr.run(task=task_backup)
    for name, result in backup.items():
        if result.failed:
            outcome.failed[name] = f"backup failed: {result.exception}"
        else:
            outcome.backups[name] = Path(result.result)

    # Never configure a device we could not back up
    safe = nr.filter(filter_func=lambda host: host.name in outcome.backups)
    if not safe.inventory.hosts:
        return

    configured = safe.run(task=task_configure, candidate_dir=candidate_dir)
    for name, result in configured.items():
        if result.failed:
            outcome.failed[name] = f"configure failed: {result.exception}"

    applied = safe.filter(
        filter_func=lambda host: host.name not in outcome.failed)
    if not applied.inventory.hosts:
        return

    saved = applied.run(task=task_save)
    for name, result in saved.items():
        if result.failed:
            outcome.failed[name] = f"save failed: {result.exception}"
        else:
            outcome.succeeded.append(name)


def deploy(nr, intent: SiteIntent, settings: Settings,
           cleared: list[str], candidate_dir: str = "artefacts/candidate",
           ) -> DeployOutcome:
    """
    Deploy to cleared devices, in batches, stopping if a batch fails.
    """
    outcome = DeployOutcome()

    all_hosts = list(nr.inventory.hosts)
    outcome.skipped = [name for name in all_hosts if name not in cleared]

    targets = [name for name in all_hosts if name in cleared]
    batches = [targets[i:i + settings.batch_size]
               for i in range(0, len(targets), settings.batch_size)]

    for number, batch in enumerate(batches, start=1):
        logger.info("batch %d/%d: %s", number, len(batches), ", ".join(batch))

        scoped = nr.filter(filter_func=lambda host, b=batch: host.name in b)
        deploy_batch(scoped, candidate_dir, outcome)

        if outcome.failed:
            logger.error(
                "batch %d had %d failure(s) — stopping before batch %d",
                number, len(outcome.failed), number + 1,
            )
            remaining = [name for later in batches[number:] for name in later]
            outcome.skipped.extend(remaining)
            break

    return outcome
```

### Three decisions to notice

**Back up first, and never configure a device you couldn't back up.** The `safe` filter enforces it. A device you can't read is a device you can't undo, and chapter 7's rollback depends on these files existing.

**Batches stop on failure.** If batch one fails, batch two never runs. The default `batch_size` of 5 means a template that's wrong in a way nothing caught reaches five devices, not fifty. This is [blast radius](../../production-grade-network-automation-principles/scoping-automation-to-reduce-blast-radius.md) in about six lines.

**`write memory` is its own step.** Configuration that's applied but not saved survives until the next reload — which is a genuinely useful safety property while you're still verifying, and a nasty surprise if you assumed it saved itself. Making it explicit means chapter 7 can choose *not* to save when verification fails.

!!! danger "The Default Here Is Deliberately Conservative"
    Five devices per batch, halt on any failure, no automatic continuation. For a 400-device estate that's eighty sequential batches and a slow afternoon.

    Raise it when you've earned the confidence — the same template, the same pipeline, run successfully across enough change windows that the risk is understood. Not on day one because the deploy felt slow. The [dependency ordering tutorial](../expert/dependency-ordering-task-orchestration.md) covers doing this properly when order between devices matters.

---

## 🖥️ The `deploy` Command

Add to **`netpipe/cli.py`**:

```python
import logging

from netpipe.deploy import deploy
from netpipe.inventory import build_nornir
from netpipe.preflight import preflight_device


def cmd_deploy(args: argparse.Namespace) -> int:
    try:
        intent = load_intent(args.intent)
    except IntentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    settings = load_settings()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # 1. Render
    try:
        render_site(intent)
    except RenderError as exc:
        print(f"✗ render failed: {exc}", file=sys.stderr)
        return 1

    # 2. Pre-flight
    print("Running pre-flight...")
    with ThreadPoolExecutor(max_workers=settings.max_workers) as pool:
        reports = list(pool.map(
            lambda device: preflight_device(device, settings), intent.devices))

    cleared = [r.device for r in reports if r.cleared]
    blocked = [r for r in reports if not r.cleared]

    for report in blocked:
        reasons = ", ".join(c.name for c in report.failures)
        print(f"  ✗ {report.device} blocked: {reasons}")

    if not cleared:
        print("\n✗ No devices cleared pre-flight. Nothing to do.", file=sys.stderr)
        return 1

    print(f"  ✓ {len(cleared)} device(s) cleared\n")

    # 3. Confirm
    print(f"About to configure {len(cleared)} device(s) "
          f"in batches of {settings.batch_size}:")
    for name in cleared:
        print(f"    {name}")
    print(f"\nChange reference: {intent.change_reference}")

    if args.dry_run:
        print("\n(dry run — nothing was sent)")
        return 0

    if settings.require_approval:
        answer = input("\nType the change reference to proceed: ").strip()
        if answer != intent.change_reference:
            print("✗ Not confirmed. Nothing was sent.", file=sys.stderr)
            return 1

    # 4. Deploy
    nr = build_nornir(intent, settings)
    outcome = deploy(nr, intent, settings, cleared)

    print(f"\n✓ {len(outcome.succeeded)} succeeded")
    if outcome.failed:
        print(f"✗ {len(outcome.failed)} failed")
        for name, reason in outcome.failed.items():
            print(f"    {name}: {reason}")
    if outcome.skipped:
        print(f"– {len(outcome.skipped)} skipped: {', '.join(outcome.skipped)}")

    return 1 if outcome.failed else 0
```

Register it:

```python
    deploy_cmd = sub.add_parser("deploy", parents=[common],
                                help="apply configuration to devices")
    deploy_cmd.add_argument("--dry-run", action="store_true",
                            help="do everything except send configuration")
    deploy_cmd.set_defaults(func=cmd_deploy)
```

### The approval prompt

Typing the change reference — not `y`, not `yes` — is a small piece of friction with a specific purpose. `y` is muscle memory; you can type it without reading the screen. `CHG0047821` has to be copied from the line above it, which means looking at the line above it, which means seeing how many devices are listed.

Set `NETAUTO_REQUIRE_APPROVAL=false` for CI. Keep it on for humans. See [Human-in-the-Loop Automation Design](../../production-grade-network-automation-principles/human-in-the-loop-automation-design.md).

---

## ▶️ Run It

Always this first:

```bash
python -m netpipe deploy --dry-run
```

```
Running pre-flight...
  ✓ 2 device(s) cleared

About to configure 2 device(s) in batches of 5:
    man1-acc-sw-01
    man1-acc-sw-02

Change reference: CHG0047821

(dry run — nothing was sent)
```

Then, when the diff has been reviewed and the window is open:

```bash
python -m netpipe deploy
```

```
Running pre-flight...
  ✓ 2 device(s) cleared

About to configure 2 device(s) in batches of 5:
    man1-acc-sw-01
    man1-acc-sw-02

Change reference: CHG0047821

Type the change reference to proceed: CHG0047821

2026-09-20 14:22:01 INFO batch 1/1: man1-acc-sw-01, man1-acc-sw-02
2026-09-20 14:22:04 INFO {"timestamp": "2026-09-20T14:22:01.882431+00:00",
  "action": "backup", "device": "man1-acc-sw-01", "site": "MAN1",
  "change_reference": "CHG0047821", "outcome": "success", "duration_s": 2.41}
2026-09-20 14:22:19 INFO {"timestamp": "2026-09-20T14:22:04.310220+00:00",
  "action": "configure", "device": "man1-acc-sw-01", "site": "MAN1",
  "change_reference": "CHG0047821", "outcome": "success", "duration_s": 15.02}
2026-09-20 14:22:23 INFO {"timestamp": "2026-09-20T14:22:19.331901+00:00",
  "action": "save", "device": "man1-acc-sw-01", "site": "MAN1",
  "change_reference": "CHG0047821", "outcome": "success", "duration_s": 3.88}
...

✓ 2 succeeded
```

Those JSON lines are not decoration. Chapter 7 collects them into the change record, and in the meantime they're already queryable:

```bash
python -m netpipe deploy 2>&1 | grep '^{' | jq 'select(.outcome=="failure")'
```

---

## 🧪 Tests

Deployment can't be fully tested without devices, but the parts that decide *what* happens can.

**`tests/test_deploy.py`:**

```python
import pytest
import yaml

from netpipe.decorators import retry
from netpipe.inventory import write_inventory
from netpipe.intent import load_intent


def test_inventory_matches_intent(tmp_path):
    intent = load_intent("intent/man1.yaml")
    directory = write_inventory(intent, str(tmp_path))

    hosts = yaml.safe_load((directory / "hosts.yaml").read_text())

    assert set(hosts) == {"man1-acc-sw-01", "man1-acc-sw-02"}
    assert hosts["man1-acc-sw-01"]["hostname"] == "10.1.1.11"
    assert hosts["man1-acc-sw-01"]["platform"] == "cisco_ios"
    assert hosts["man1-acc-sw-01"]["data"]["change_reference"] == "CHG0047821"


def test_generated_inventory_holds_no_secrets(tmp_path):
    intent = load_intent("intent/man1.yaml")
    directory = write_inventory(intent, str(tmp_path))

    for name in ("hosts.yaml", "groups.yaml", "defaults.yaml"):
        content = (directory / name).read_text().lower()
        assert "password" not in content
        assert "username" not in content


def test_retry_gives_up_and_reraises():
    calls = []

    @retry(attempts=3, base_delay=0.01)
    def always_fails():
        calls.append(1)
        raise ConnectionError("nope")

    with pytest.raises(ConnectionError):
        always_fails()
    assert len(calls) == 3


def test_retry_stops_once_it_succeeds():
    calls = []

    @retry(attempts=3, base_delay=0.01)
    def fails_once():
        calls.append(1)
        if len(calls) < 2:
            raise ConnectionError("transient")
        return "ok"

    assert fails_once() == "ok"
    assert len(calls) == 2


def test_batching_splits_correctly():
    targets = [f"sw{n:02d}" for n in range(1, 13)]
    size = 5
    batches = [targets[i:i + size] for i in range(0, len(targets), size)]

    assert len(batches) == 3
    assert [len(b) for b in batches] == [5, 5, 2]
    assert [name for batch in batches for name in batch] == targets
```

`test_generated_inventory_holds_no_secrets` is the important one. It's the automated version of the reason credentials are injected in memory, and it will fail loudly the day somebody "simplifies" `write_inventory` by putting the username in `defaults.yaml`.

---

## 📁 Where You Are

```
netpipe/
├── netpipe/
│   ├── cli.py            ← validate, plan, preflight, deploy
│   ├── decorators.py     ← retry, audited                      (new)
│   ├── deploy.py         ← the write phase                     (new)
│   ├── inventory.py      ← intent to Nornir inventory          (new)
│   └── ...
├── inventory/            ← generated, gitignored
├── artefacts/
│   ├── backup/           ← pre-change configs                  (new)
│   ├── candidate/
│   └── diff/
└── tests/
    └── test_deploy.py                                          (new)
```

---

## 🎯 Key Takeaways

- ✅ **Generate the Nornir inventory from intent** — Two inventories will diverge
- ✅ **Credentials in memory, never in generated files** — And test that it stays true
- ✅ **Retry transport, not intent** — A rejected command fails identically three times
- ✅ **Back up first, and don't configure what you couldn't back up** — Rollback depends on it
- ✅ **Batch, and halt on failure** — Five wrong devices instead of fifty
- ✅ **Make the operator type something meaningful** — `y` is muscle memory
- ✅ **`--dry-run` before every real run** — Including the ones you're sure about

---

## ➡️ Next

Nornir reported success. That means the device accepted the commands — not that the network works.

[Chapter 6 — Proving the Change with PyATS](./06-proving-the-change-with-pyats.md) goes and checks.

---

[← Chapter 4 — Credentials and Pre-Flight](./04-credentials-and-preflight.md) | [Chapter 6 — Proving the Change with PyATS →](./06-proving-the-change-with-pyats.md)
