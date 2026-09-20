---
title: "Capstone Chapter 7: Rollback and the Audit Record"
description: Wire verification failure to automatic rollback, emit a structured audit record of the whole change, and join every stage into one orchestrated command.
tags:
  - Capstone
  - Rollback
  - Audit
  - Structured Logging
  - Tutorial
---

## Chapter 7: Rollback and the Audit Record

*Capstone chapter 7 of 7 — [project overview](./index.md)*

## "What Happens When It Goes Wrong, and What You Can Prove Afterwards"

Six chapters in, the pipeline can detect a broken change. It just can't do anything about it, and it can't tell you afterwards what happened.

This chapter fixes both, and then joins every stage into one command.

---

## 🎯 What You'll Build

- `netpipe/rollback.py` — restore from the backups chapter 5 took
- `netpipe/audit.py` — a structured record of intent, action, proof and approval
- `netpipe run` — validate → snapshot → preflight → deploy → verify → rollback if needed
- A finished pipeline

**Builds on:** [Error Recovery and Rollback](../intermediate/error-recovery-rollback-network-automation.md), [Structured Logging](../intermediate/structured-logging-network-automation.md), [State Management and Idempotency](../intermediate/state-management-idempotency-network-automation.md)

---

## ↩️ Rollback Is Harder Than It Sounds

Before the code, the caveats — because rollback is the feature most likely to be trusted more than it deserves.

**Restoring a config file is not restoring a state.** `configure replace` gets the text back. It does not un-bounce an interface, un-flush a MAC table, un-reconverge spanning tree, or bring back the BGP session that dropped while the config was wrong. The device returns to the old configuration; the network takes its own time, and sometimes doesn't.

**Rollback can fail too.** It runs over the same management path the change may have just broken. If your change took out the uplink, the rollback cannot reach the device. This is not hypothetical — it's the single most common way an automated rollback doesn't happen.

**Some changes have no rollback.** A deleted VLAN takes its MAC table with it. A regenerated crypto key is gone. Restoring the config that referenced them doesn't bring them back.

So: implement rollback, use it, and never let it become the reason you skipped the review. See [Rollback Strategies — What Works and What Doesn't](../../production-grade-network-automation-principles/rollback-strategies-what-works-and-what-doesnt.md).

---

## 🔧 The Rollback Module

**`netpipe/rollback.py`:**

```python
#!/usr/bin/env python3
"""
Restore devices from the backups taken before the change.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

from netpipe.decorators import audited, retry

logger = logging.getLogger("netpipe")


class NoBackupError(Exception):
    """There is nothing to roll back to."""


@dataclass
class RollbackOutcome:
    restored: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    no_backup: list[str] = field(default_factory=list)


def latest_backup(device_name: str,
                  directory: str = "artefacts/backup") -> Path:
    """Most recent backup for a device. Timestamps sort lexically."""
    candidates = sorted(Path(directory).glob(f"{device_name}-*.cfg"))
    if not candidates:
        raise NoBackupError(f"no backup found for {device_name}")
    return candidates[-1]


@audited("rollback")
@retry(attempts=3, base_delay=5.0)
def task_rollback(task: Task) -> Result:
    """
    Restore the pre-change configuration by merging the backup back in.

    This is the simple case and it handles changed values correctly. It
    cannot remove a command the change *added* — see the note below on
    `configure replace` for that.
    """
    backup = latest_backup(task.host.name)
    config = backup.read_text(encoding="utf-8")

    lines = [line for line in config.splitlines()
             if line.strip() and line.strip() not in ("!", "end")]

    task.run(
        task=netmiko_send_config,
        config_commands=lines,
        read_timeout=180,
    )

    task.run(
        task=netmiko_send_command,
        command_string="write memory",
        read_timeout=120,
    )

    return Result(host=task.host,
                  result=f"restored from {backup.name}",
                  changed=True)


def rollback(nr, targets: list[str]) -> RollbackOutcome:
    """Roll back the named devices."""
    outcome = RollbackOutcome()

    havable = []
    for name in targets:
        try:
            latest_backup(name)
            havable.append(name)
        except NoBackupError:
            outcome.no_backup.append(name)
            logger.error("cannot roll back %s: no backup", name)

    if not havable:
        return outcome

    scoped = nr.filter(filter_func=lambda host: host.name in havable)
    results = scoped.run(task=task_rollback)

    for name, result in results.items():
        if result.failed:
            outcome.failed[name] = str(result.exception)
            logger.error("rollback FAILED for %s: %s", name, result.exception)
        else:
            outcome.restored.append(name)

    return outcome
```

!!! danger "A Failed Rollback Is an Incident, Not a Log Line"
    `outcome.failed` means a device is sitting in a state nobody intended and automation could not fix. That is a human problem from the moment it happens.

    `netpipe` prints it loudly and exits non-zero. In production, this is where you page someone — the [incident response tutorial](../expert/incident-response-automation.md) covers wiring that up. What you must not do is let it scroll past in a log.

!!! tip "`configure replace` Deserves a Look"
    The code above merges the backup's lines back in, which works for additive changes and is what Netmiko does most naturally. It cannot remove a command the change *added* — merging `switchport access vlan 10` over `switchport access vlan 20` works, but merging a config that simply lacks a line won't delete that line.

    On IOS-XE, `configure replace flash:backup.cfg force` computes a true difference and applies it. It's the right tool, it needs the file copied to the device first (SCP), and it's worth the extra step for any change that removes configuration. Treat the merge version here as the simple case.

---

## 📋 The Audit Record

The audit record answers, months later, four questions: **what was intended, what was done, what was proven, and who said yes.**

**`netpipe/audit.py`:**

```python
#!/usr/bin/env python3
"""
The change record.
"""

import getpass
import hashlib
import json
import platform
import socket
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from netpipe.models import SiteIntent


def _git_revision() -> str:
    """The commit the pipeline ran from, so the code is identifiable."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _digest(path: Path) -> str:
    """SHA-256 of a file, so the artefact can be shown to be unmodified."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class AuditRecord:
    # Identity
    change_reference: str
    site: str
    started_at: str
    finished_at: str = ""

    # Provenance
    operator: str = field(default_factory=getpass.getuser)
    host: str = field(default_factory=socket.gethostname)
    python_version: str = field(default_factory=platform.python_version)
    git_revision: str = field(default_factory=_git_revision)
    intent_digest: str = ""

    # What happened
    approved: bool = False
    dry_run: bool = False
    devices_targeted: list[str] = field(default_factory=list)
    devices_blocked: dict[str, str] = field(default_factory=dict)
    devices_configured: list[str] = field(default_factory=list)
    devices_failed: dict[str, str] = field(default_factory=dict)
    devices_verified: list[str] = field(default_factory=list)
    devices_rolled_back: list[str] = field(default_factory=list)
    rollback_failures: dict[str, str] = field(default_factory=dict)

    # Evidence
    findings: list[dict] = field(default_factory=list)
    artefacts: dict[str, str] = field(default_factory=dict)

    outcome: str = "incomplete"

    def conclude(self) -> str:
        """Decide the overall verdict."""
        self.finished_at = datetime.now(timezone.utc).isoformat()

        if self.dry_run:
            self.outcome = "dry-run"
        elif self.rollback_failures:
            self.outcome = "rollback-failed"
        elif self.devices_rolled_back:
            self.outcome = "rolled-back"
        elif self.devices_failed:
            self.outcome = "partial-failure"
        elif self.devices_configured and not self.devices_verified:
            self.outcome = "unverified"
        elif self.devices_configured:
            self.outcome = "success"
        else:
            self.outcome = "no-change"

        return self.outcome

    def write(self, directory: str = "artefacts/audit") -> Path:
        out = Path(directory)
        out.mkdir(parents=True, exist_ok=True)

        stamp = self.started_at.replace(":", "").replace("-", "")[:15]
        path = out / f"{self.change_reference}-{stamp}.json"
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

        return path


def start_record(intent: SiteIntent, intent_path: str,
                 dry_run: bool = False) -> AuditRecord:
    return AuditRecord(
        change_reference=intent.change_reference,
        site=intent.site,
        started_at=datetime.now(timezone.utc).isoformat(),
        intent_digest=_digest(Path(intent_path)),
        devices_targeted=[device.name for device in intent.devices],
        dry_run=dry_run,
    )
```

### The fields that get left out, and shouldn't be

Most homegrown audit logs record which devices changed. The ones that turn out to matter later are the other three.

**`intent_digest`.** The SHA-256 of the intent file at the moment it ran. Six months on, `intent/man1.yaml` has been edited eleven times, and this is the only way to establish what the change actually asked for. Without it, "here's the file" is an assertion, not evidence.

**`git_revision`.** The intent says what was wanted; the revision says what code interpreted it. A template bug introduced in March and fixed in May makes an April change unexplainable without this line.

**`devices_blocked`.** Devices you *didn't* touch, and why. When someone asks why switch 14 was missed, the answer is in the record rather than in somebody's memory.

And `outcome` is deliberately not a boolean. `rolled-back` and `partial-failure` and `unverified` are genuinely different situations, and flattening them into `false` throws away the distinction you'll most want.

See [Building Audit-Ready Automation](../../production-grade-network-automation-principles/building-audit-ready-automation.md).

!!! warning "`artefacts/` Is Gitignored — Audit Records Shouldn't Live There Forever"
    Chapter 1 gitignored `artefacts/` because generated configs churn. Audit records are the exception: they're the evidence, and a laptop is not a retention policy.

    Ship them somewhere durable — object storage with versioning, your logging platform, or your change system as an attachment against the change reference. The `write()` method is where you add that. Also think about retention and personal data: `operator` and `host` are identifying, and your organisation may have rules about how long that's kept.

---

## 🔗 The `run` Command

Every stage, in order, with the failure paths wired up.

Add to **`netpipe/cli.py`**:

```python
from netpipe.audit import start_record
from netpipe.rollback import rollback


def cmd_run(args: argparse.Namespace) -> int:
    """The full pipeline: validate, snapshot, preflight, deploy, verify."""
    # ── Validate ────────────────────────────────────────────────────
    try:
        intent = load_intent(args.intent)
    except IntentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    settings = load_settings()
    logging.basicConfig(level=settings.log_level,
                        format="%(asctime)s %(levelname)s %(message)s")

    record = start_record(intent, args.intent, dry_run=args.dry_run)
    print(f"═══ {intent.change_reference} — {intent.site} ═══\n")
    print(f"[1/6] validate     ✓ {len(intent.devices)} devices")

    # ── Render ──────────────────────────────────────────────────────
    try:
        written = render_site(intent)
    except RenderError as exc:
        print(f"[2/6] render       ✗ {exc}", file=sys.stderr)
        record.conclude()
        record.write()
        return 1

    record.artefacts["candidate"] = "artefacts/candidate"
    print(f"[2/6] render       ✓ {len(written)} configs")

    # ── Pre-flight ──────────────────────────────────────────────────
    with ThreadPoolExecutor(max_workers=settings.max_workers) as pool:
        reports = list(pool.map(
            lambda device: preflight_device(device, settings), intent.devices))

    cleared = [r.device for r in reports if r.cleared]
    for report in reports:
        if not report.cleared:
            record.devices_blocked[report.device] = ", ".join(
                check.name for check in report.failures)

    print(f"[3/6] preflight    {'✓' if cleared else '✗'} "
          f"{len(cleared)} cleared, {len(record.devices_blocked)} blocked")

    for name, reason in record.devices_blocked.items():
        print(f"                     ✗ {name}: {reason}")

    if not cleared:
        record.conclude()
        path = record.write()
        print(f"\n✗ Nothing cleared pre-flight. Record: {path}")
        return 1

    # ── Snapshot ────────────────────────────────────────────────────
    testbed = build_testbed(intent, settings)
    before: dict[str, dict] = {}

    for device in intent.devices:
        if device.name not in cleared:
            continue
        try:
            before[device.name] = snapshot(testbed, device.name, "before")
        except Exception as exc:
            print(f"                     ⚠ {device.name}: "
                  f"no before-snapshot ({exc})")
            before[device.name] = {}

    record.artefacts["state_before"] = "artefacts/state"
    print(f"[4/6] snapshot     ✓ {len(before)} captured")

    # ── Approve and deploy ──────────────────────────────────────────
    if args.dry_run:
        print("[5/6] deploy       – dry run, nothing sent")
        record.conclude()
        path = record.write()
        print(f"\nRecord: {path}")
        return 0

    if settings.require_approval:
        print(f"\nAbout to configure {len(cleared)} device(s).")
        answer = input(f"Type {intent.change_reference} to proceed: ").strip()
        if answer != intent.change_reference:
            print("✗ Not confirmed.", file=sys.stderr)
            record.conclude()
            record.write()
            return 1

    record.approved = True

    nr = build_nornir(intent, settings)
    outcome = deploy(nr, intent, settings, cleared)

    record.devices_configured = outcome.succeeded
    record.devices_failed = outcome.failed
    record.artefacts["backups"] = "artefacts/backup"

    print(f"[5/6] deploy       {'✓' if not outcome.failed else '✗'} "
          f"{len(outcome.succeeded)} configured, {len(outcome.failed)} failed")

    # ── Verify ──────────────────────────────────────────────────────
    to_verify = [d for d in intent.devices if d.name in outcome.succeeded]
    bad: list[str] = []

    for device in to_verify:
        report = verify_device(testbed, device, intent,
                               before.get(device.name, {}))
        record.findings.extend(
            {"device": f.device, "severity": f.severity,
             "subject": f.subject, "detail": f.detail}
            for f in report.findings)

        if report.passed:
            record.devices_verified.append(device.name)
        else:
            bad.append(device.name)

    record.artefacts["state_after"] = "artefacts/state"
    print(f"[6/6] verify       {'✓' if not bad else '✗'} "
          f"{len(record.devices_verified)} verified, {len(bad)} failed")

    for finding in record.findings:
        if finding["severity"] == "error":
            print(f"                     ✗ {finding['device']}/"
                  f"{finding['subject']}: {finding['detail']}")

    # ── Roll back what failed verification ──────────────────────────
    if bad and not args.no_rollback:
        print(f"\n⟲ Rolling back {len(bad)} device(s)...")
        result = rollback(nr, bad)

        record.devices_rolled_back = result.restored
        record.rollback_failures = result.failed

        for name in result.restored:
            print(f"    ✓ {name} restored")
        for name, reason in result.failed.items():
            print(f"    ✗ {name} ROLLBACK FAILED: {reason}")
        for name in result.no_backup:
            print(f"    ✗ {name} no backup available")

    elif bad:
        print(f"\n⚠ {len(bad)} device(s) failed verification. "
              "Rollback suppressed by --no-rollback.")

    # ── Conclude ────────────────────────────────────────────────────
    verdict = record.conclude()
    path = record.write()

    print(f"\n═══ {verdict.upper()} ═══")
    print(f"Record: {path}")

    if record.rollback_failures:
        print("\n‼ DEVICES LEFT IN AN UNINTENDED STATE — ESCALATE",
              file=sys.stderr)
        return 2

    return 0 if verdict in ("success", "dry-run", "no-change") else 1
```

Register it:

```python
    run = sub.add_parser("run", parents=[common],
                         help="the full pipeline, end to end")
    run.add_argument("--dry-run", action="store_true",
                     help="stop before deploying")
    run.add_argument("--no-rollback", action="store_true",
                     help="leave failed devices alone (investigate manually)")
    run.set_defaults(func=cmd_run)
```

### Three exit codes, not two

`0` success, `1` something failed and was handled, `2` a device is in an unintended state and automation gave up. A scheduler can treat `2` differently from `1`, and it should — one is a change that didn't happen, the other is a change that half happened and can't be undone.

### `--no-rollback` exists on purpose

Automatic rollback is the right default and the wrong choice during an investigation. When you're trying to understand *why* a change broke something, restoring the previous config destroys the evidence. `--no-rollback` is for the second run, once you already know the first one failed.

---

## ▶️ Run It

**Dry run — the habit:**

```bash
python -m netpipe run --dry-run
```

```
═══ CHG0047821 — MAN1 ═══

[1/6] validate     ✓ 2 devices
[2/6] render       ✓ 2 configs
[3/6] preflight    ✓ 2 cleared, 0 blocked
[4/6] snapshot     ✓ 2 captured
[5/6] deploy       – dry run, nothing sent

Record: artefacts/audit/CHG0047821-20260920T143107.json
```

**A change that works:**

```
═══ CHG0047821 — MAN1 ═══

[1/6] validate     ✓ 2 devices
[2/6] render       ✓ 2 configs
[3/6] preflight    ✓ 2 cleared, 0 blocked
[4/6] snapshot     ✓ 2 captured

About to configure 2 device(s).
Type CHG0047821 to proceed: CHG0047821

[5/6] deploy       ✓ 2 configured, 0 failed
[6/6] verify       ✓ 2 verified, 0 failed

═══ SUCCESS ═══
Record: artefacts/audit/CHG0047821-20260920T143107.json
```

**A change that doesn't — the pipeline doing its job:**

```
═══ CHG0047821 — MAN1 ═══

[1/6] validate     ✓ 2 devices
[2/6] render       ✓ 2 configs
[3/6] preflight    ✗ 1 cleared, 1 blocked
                     ✗ man1-acc-sw-02: identity
[4/6] snapshot     ✓ 1 captured

About to configure 1 device(s).
Type CHG0047821 to proceed: CHG0047821

[5/6] deploy       ✓ 1 configured, 0 failed
[6/6] verify       ✗ 0 verified, 1 failed
                     ✗ man1-acc-sw-01/TenGigabitEthernet1/1/1: was up
                       before the change, now down

⟲ Rolling back 1 device(s)...
    ✓ man1-acc-sw-01 restored

═══ ROLLED-BACK ═══
Record: artefacts/audit/CHG0047821-20260920T143107.json
```

One device was never touched because it wasn't the device it claimed to be. The other was configured, broke its own uplink, was caught, and was put back. Nobody was watching.

**The record it wrote:**

```json
{
  "change_reference": "CHG0047821",
  "site": "MAN1",
  "started_at": "2026-09-20T14:31:07.221084+00:00",
  "finished_at": "2026-09-20T14:34:52.664219+00:00",
  "operator": "cdavies",
  "host": "AUTO-RUNNER-01",
  "python_version": "3.12.4",
  "git_revision": "9f3c1ab7e4d2...",
  "intent_digest": "7d4a1f0b8c33...",
  "approved": true,
  "dry_run": false,
  "devices_targeted": ["man1-acc-sw-01", "man1-acc-sw-02"],
  "devices_blocked": {"man1-acc-sw-02": "identity"},
  "devices_configured": ["man1-acc-sw-01"],
  "devices_failed": {},
  "devices_verified": [],
  "devices_rolled_back": ["man1-acc-sw-01"],
  "rollback_failures": {},
  "findings": [
    {
      "device": "man1-acc-sw-01",
      "severity": "error",
      "subject": "TenGigabitEthernet1/1/1",
      "detail": "was up before the change, now down"
    }
  ],
  "artefacts": {
    "candidate": "artefacts/candidate",
    "backups": "artefacts/backup",
    "state_before": "artefacts/state",
    "state_after": "artefacts/state"
  },
  "outcome": "rolled-back"
}
```

Everything the post-incident conversation needs, written without anybody remembering to write it.

---

## 🧪 Tests

**`tests/test_audit.py`:**

```python
import json

import pytest

from netpipe.audit import AuditRecord, start_record
from netpipe.intent import load_intent
from netpipe.rollback import NoBackupError, latest_backup


@pytest.fixture
def record():
    return start_record(load_intent("intent/man1.yaml"), "intent/man1.yaml")


def test_record_captures_provenance(record):
    assert record.change_reference == "CHG0047821"
    assert record.site == "MAN1"
    assert len(record.intent_digest) == 64      # sha-256 hex
    assert record.operator
    assert record.devices_targeted == ["man1-acc-sw-01", "man1-acc-sw-02"]


def test_digest_changes_with_the_file(tmp_path):
    intent_file = tmp_path / "a.yaml"
    source = load_intent("intent/man1.yaml")

    intent_file.write_text("x", encoding="utf-8")
    first = start_record(source, str(intent_file)).intent_digest

    intent_file.write_text("y", encoding="utf-8")
    second = start_record(source, str(intent_file)).intent_digest

    assert first != second


@pytest.mark.parametrize("setup,expected", [
    (lambda r: setattr(r, "dry_run", True), "dry-run"),
    (lambda r: None, "no-change"),
    (lambda r: r.devices_configured.append("sw1"), "unverified"),
    (lambda r: (r.devices_configured.append("sw1"),
                r.devices_verified.append("sw1")), "success"),
    (lambda r: r.devices_failed.update({"sw1": "boom"}), "partial-failure"),
    (lambda r: r.devices_rolled_back.append("sw1"), "rolled-back"),
    (lambda r: r.rollback_failures.update({"sw1": "unreachable"}),
     "rollback-failed"),
])
def test_outcome_verdicts(record, setup, expected):
    setup(record)
    assert record.conclude() == expected


def test_rollback_failure_outranks_everything(record):
    record.devices_configured.append("sw1")
    record.devices_verified.append("sw1")
    record.devices_rolled_back.append("sw2")
    record.rollback_failures["sw3"] = "unreachable"
    assert record.conclude() == "rollback-failed"


def test_record_writes_valid_json(record, tmp_path):
    record.conclude()
    path = record.write(str(tmp_path))

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["change_reference"] == "CHG0047821"
    assert written["outcome"] == "no-change"


def test_latest_backup_picks_the_newest(tmp_path):
    for stamp in ("20260101T090000Z", "20260920T143107Z", "20260615T120000Z"):
        (tmp_path / f"sw1-{stamp}.cfg").write_text("!", encoding="utf-8")

    assert latest_backup("sw1", str(tmp_path)).name == "sw1-20260920T143107Z.cfg"


def test_no_backup_is_an_explicit_error(tmp_path):
    with pytest.raises(NoBackupError, match="no backup found for sw9"):
        latest_backup("sw9", str(tmp_path))
```

`test_rollback_failure_outranks_everything` is the one worth keeping. Verdict precedence is easy to get subtly wrong when someone adds an eighth outcome, and a change recorded as `success` while a device sits unrecoverable is the worst possible bug in an audit system.

---

## 📁 The Finished Project

```
netpipe/
├── .env.example
├── .github/workflows/validate.yml
├── requirements.txt
├── intent/
│   └── man1.yaml
├── netpipe/
│   ├── audit.py          ← the change record
│   ├── cli.py            ← validate, plan, preflight, deploy,
│   │                       snapshot, verify, run
│   ├── collect.py
│   ├── decorators.py
│   ├── deploy.py
│   ├── diff.py
│   ├── intent.py
│   ├── inventory.py
│   ├── models.py
│   ├── preflight.py
│   ├── render.py
│   ├── rollback.py       ← restore from backup
│   ├── settings.py
│   ├── testbed.py
│   └── verify.py
├── templates/
│   └── access_switch.j2
├── tests/                ← 57 tests, none needing a device
└── artefacts/
    ├── audit/  backup/  candidate/  diff/  state/
```

Around 800 lines. You can read all of it in an afternoon.

---

## 🎓 What You Actually Built

Look back at the arrows from [the overview](./index.md). Six of the seven stages exist to refuse something:

| Stage | Refuses |
|---|---|
| validate | Intent that can't be correct |
| plan | Changes nobody has looked at |
| preflight | Devices that aren't ready, or aren't the right device |
| deploy | More than one batch, once a batch has failed |
| verify | Success, when only the commands succeeded |
| rollback | Leaving a broken change in place |

The one stage that does the work — `netmiko_send_config` — is a single line.

That ratio is the lesson. Sending configuration to a device has never been the difficult part of network automation; you could do it after the first beginner tutorial on this site. The difficulty, and the entire difference between a script and something you'd let run against production on a Friday, is everything arranged around that line to make it safe.

---

## ➡️ Where to Go Next

**Make it yours.** Point it at your own intent, naming standard, VLANs and templates. The pipeline's shape doesn't change; everything inside it will.

**Then extend it:**

- **[Secure Credential Vaulting](../expert/secure-credential-vaulting.md)** — Replace `.env` with Vault or AWS Secrets Manager. Only `load_settings()` changes.
- **[Asyncio for Network Automation](../expert/asyncio-network-automation.md)** — When batched threading stops scaling.
- **[Circuit Breakers and Backpressure](../expert/circuit-breakers-backpressure-network-automation.md)** — Stop hammering a device that's already failing.
- **[Dependency Ordering and Task Orchestration](../expert/dependency-ordering-task-orchestration.md)** — When device order matters, not just batch size.
- **[DevOps and Observability](../expert/devops-observability-network-automation.md)** — Ship those audit records and JSON logs somewhere that can query them.
- **[Incident Response Automation](../expert/incident-response-automation.md)** — Page someone on `rollback-failed` instead of printing it.
- **[Tool Ecosystem Integration](../expert/tool-ecosystem-integration.md)** — Source intent from NetBox; close the change in ServiceNow from the audit record.
- **[Governed AI for Network Operations](../../governed-ai-network-operations/index.md)** — `netpipe`'s subcommands are already narrow typed tools with a validation gate. That's most of what a safe AI tool boundary requires.

And read the [Production-Grade Principles](../../production-grade-network-automation-principles/index.md) track properly now. Every page in it will read differently, because you've built the thing it's describing.

---

## 🎯 Key Takeaways

- ✅ **Rollback restores config, not state** — And it can fail; plan for that
- ✅ **A failed rollback is an incident** — Distinct exit code, escalation, not a log line
- ✅ **Record the intent digest and git revision** — Otherwise there's no evidence, only assertions
- ✅ **Record what you skipped, and why** — It's the question people actually ask later
- ✅ **`outcome` is not a boolean** — `rolled-back` and `partial-failure` are different problems
- ✅ **`--no-rollback` for investigations** — Restoring the config destroys the evidence
- ✅ **Six stages refuse, one acts** — That ratio is the whole discipline

---

[← Chapter 6 — Proving the Change with PyATS](./06-proving-the-change-with-pyats.md) | [Capstone Overview](./index.md) | [Expert Tutorials →](../expert/index.md)
