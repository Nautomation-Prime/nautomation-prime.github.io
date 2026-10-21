---
title: Incident Response Automation
description: Detect, remediate, and recover from network incidents automatically. Pattern matching, self-healing networks, and incident tracking. Enterprise-grade automation.
tags:
  - Incident Response
  - Automation
  - Self-Healing Networks
  - Remediation
  - Expert
  - Resilience
---

## Why Automated Response Matters

**Scenario:** BGP session flaps at 2 AM.

**Manual response:**

- Alert fires at 2 AM
- Engineer gets paged
- Waits 15-30 minutes for engineer to respond
- Engineer investigates (15 minutes)
- Engineer identifies cause (10 minutes)
- Engineer applies fix (10 minutes)
- **Total: 60-90 minutes of outage**

**With automated response:**

- Alert fires at 2 AM
- Automated system identifies flapping pattern
- Runs diagnostics in parallel
- Identifies isolated peer with bad BGP config
- Withdraws peer routes, updates peer config, re-enables
- **Total: 90 seconds of outage**
- Engineer reviews incident history next morning

**Automated response reduces MTTR (Mean Time To Repair) by 98%.**

---

## Pattern 1: Event Detection Engine

### The Implementation

```python
# src/incident_detector.py
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Callable
from datetime import datetime
from enum import Enum
import json

class SeverityLevel(Enum):
    """Incident severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "info"

class RemediationType(Enum):
    """Type of remediation available."""
    AUTOMATIC = "automatic"  # Can be fixed without approval
    MANUAL = "manual"        # Requires engineer approval
    ESCALATE = "escalate"    # Escalate to NOC

@dataclass
class Incident:
    """Detected incident."""
    id: str
    name: str
    severity: SeverityLevel
    device: str
    symptoms: Dict[str, Any]
    detected_at: datetime
    remediation_type: RemediationType
    likely_causes: List[str]
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity.value,
            "device": self.device,
            "symptoms": self.symptoms,
            "detected_at": self.detected_at.isoformat(),
            "remediation_type": self.remediation_type.value,
            "likely_causes": self.likely_causes
        }

class PatternMatcher:
    """Detect incidents from device metrics and events."""
    
    def __init__(self):
        self.patterns = {}
        self.incident_counter = 0
    
    def register_pattern(
        self,
        name: str,
        check_func: Callable,
        severity: SeverityLevel,
        remediation_type: RemediationType,
        likely_causes: List[str] = None
    ):
        """
        Register pattern to detect.
        
        Args:
            name: Pattern name
            check_func: Function to detect pattern (returns True if found)
            severity: Incident severity
            remediation_type: Type of remediation available
            likely_causes: List of possible root causes
        """
        self.patterns[name] = {
            "check_func": check_func,
            "severity": severity,
            "remediation_type": remediation_type,
            "likely_causes": likely_causes or []
        }
    
    def detect(self, device: str, metrics: Dict) -> List[Incident]:
        """
        Check all patterns against device metrics.
        
        Args:
            device: Device name
            metrics: Device metrics/state
        
        Returns:
            List of detected incidents
        """
        incidents = []
        
        for pattern_name, pattern in self.patterns.items():
            try:
                if pattern["check_func"](metrics):
                    incident = Incident(
                        id=f"INC-{self.incident_counter:05d}",
                        name=pattern_name,
                        severity=pattern["severity"],
                        device=device,
                        symptoms=metrics,
                        detected_at=datetime.now(),
                        remediation_type=pattern["remediation_type"],
                        likely_causes=pattern["likely_causes"]
                    )
                    incidents.append(incident)
                    self.incident_counter += 1
            
            except Exception as e:
                # Log pattern check failure, continue
                print(f"⚠ Pattern '{pattern_name}' check failed: {e}")
        
        return incidents
```

### Pattern Registration Examples

```python
# src/patterns.py
from incident_detector import PatternMatcher, SeverityLevel, RemediationType

detector = PatternMatcher()

# Pattern: BGP session flapping
detector.register_pattern(
    name="BGP Session Flapping",
    check_func=lambda m: (
        m.get("bgp_session_changes_last_hour", 0) > 10 and
        m.get("bgp_session_state") != "Established"
    ),
    severity=SeverityLevel.HIGH,
    remediation_type=RemediationType.AUTOMATIC,
    likely_causes=[
        "BGP configuration mismatch",
        "Network connectivity issue",
        "Peer interface bouncing",
        "CPU overload"
    ]
)

# Pattern: High interface error rate
detector.register_pattern(
    name="High Interface Error Rate",
    check_func=lambda m: (
        m.get("interface_crc_errors", 0) > 100 or
        m.get("interface_errors_percent", 0) > 5
    ),
    severity=SeverityLevel.CRITICAL,
    remediation_type=RemediationType.MANUAL,
    likely_causes=[
        "Duplex mismatch",
        "Defective cable",
        "Port flapping",
        "Controller issue"
    ]
)

# Pattern: Low memory
detector.register_pattern(
    name="Low Available Memory",
    check_func=lambda m: m.get("available_memory_percent", 100) < 10,
    severity=SeverityLevel.HIGH,
    remediation_type=RemediationType.MANUAL,
    likely_causes=[
        "Memory leak in process",
        "Process consuming too much memory",
        "Device needs restart"
    ]
)

# Pattern: Reachability loss
detector.register_pattern(
    name="Device Unreachable",
    check_func=lambda m: not m.get("reachable", True),
    severity=SeverityLevel.CRITICAL,
    remediation_type=RemediationType.ESCALATE,
    likely_causes=[
        "Network connectivity issue",
        "Device down",
        "Routing issues",
        "Management interface failure"
    ]
)
```

---

## Pattern 2: Automatic Remediation Engine

```python
# src/remediation.py
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from incident_detector import Incident

@dataclass
class RemediationAction:
    """Single remediation step."""
    name: str
    func: Callable
    validate_func: Optional[Callable] = None  # Verify remediation worked
    undo_func: Optional[Callable] = None      # Reverse this step (None = can't)
    
    async def execute(self) -> bool:
        """Execute remediation and validate."""
        try:
            print(f"  Executing: {self.name}")
            await self.func()
            
            if self.validate_func:
                if await self.validate_func():
                    print(f"  ✓ {self.name} successful")
                    return True
                else:
                    print(f"  ✗ {self.name} validation failed")
                    return False
            
            return True
        
        except Exception as e:
            print(f"  ✗ {self.name} failed: {e}")
            return False

class RemediationRunbook:
    """Define remediation steps for an incident type."""
    
    def __init__(self, incident_name: str):
        self.incident_name = incident_name
        self.actions: List[RemediationAction] = []

    def add_action(
        self,
        name: str,
        func: Callable,
        validate_func: Optional[Callable] = None,
        undo_func: Optional[Callable] = None
    ):
        """Add remediation action. Give an undo_func if the step can be reversed."""
        self.actions.append(RemediationAction(name, func, validate_func, undo_func))
    
    async def execute(self, incident: Incident) -> Dict[str, Any]:
        """
        Execute all remediation actions.
        
        Args:
            incident: Incident to remediate
        
        Returns:
            dict with execution results and success status
        """
        print(f"\n🔧 Remediating: {self.incident_name}")
        print(f"   Device: {incident.device}")
        print(f"   Likely causes: {', '.join(incident.likely_causes)}\n")
        
        results = {
            "incident_id": incident.id,
            "actions_taken": [],
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        attempted = []

        for action in self.actions:
            attempted.append(action)
            success = await action.execute()
            results["actions_taken"].append({
                "name": action.name,
                "success": success
            })

            if not success:
                results["success"] = False
                print(f"\n⚠ Remediation failed at: {action.name}")
                print(f"  Rolling back to previous state...")
                await self._roll_back(attempted)
                break

        return results

    async def _roll_back(self, attempted: List[RemediationAction]):
        """
        Undo the steps that ran, newest first.

        Steps after the failure never ran, so there's nothing to undo for
        them. The failed step is included: it may have half-applied.
        """
        for action in reversed(attempted):
            if action.undo_func is None:
                print(f"  Can't undo: {action.name} (no undo step)")
                continue
            print(f"  Undoing: {action.name}")
            try:
                await action.undo_func()
            except Exception as e:
                # Keep undoing the rest, but never hide a failed undo
                print(f"  ✗ Undo of {action.name} failed: {e}")
```

### Remediation Runbook Examples

```python
# src/remediation_runbooks.py
import asyncio
from netmiko import ConnectHandler
from remediation import RemediationRunbook

# Netmiko is blocking, so every step runs its session in a worker thread
# with asyncio.to_thread() rather than stalling the event loop

def _session(device: dict, work):
    """Open a Netmiko session, run work(conn), and close it again."""
    with ConnectHandler(**device) as conn:
        return work(conn)

def all_bgp_neighbors_established(bgp_summary: str) -> bool:
    """
    True if every neighbour row of 'show ip bgp summary' ends in a number.

    IOS never prints the word "Established" here: an established peer
    shows its received-prefix count in the last column, and a down peer
    shows its state (Idle, Active, Connect...).
    """
    _, found, table = bgp_summary.partition("Neighbor")
    if not found:
        return False
    states = [line.split()[-1] for line in table.splitlines()[1:] if line.strip()]
    return bool(states) and all(state.isdigit() for state in states)

# --- BGP Flapping Remediation -------------------------------------------

async def clear_bgp_session(device):
    """Soft-reset BGP (re-sends routes without dropping the sessions)."""
    await asyncio.to_thread(_session, device, lambda conn: conn.send_command("clear ip bgp * soft"))

async def verify_bgp_stable(device):
    """Verify every BGP neighbour is established."""
    output = await asyncio.to_thread(
        _session, device, lambda conn: conn.send_command("show ip bgp summary")
    )
    return all_bgp_neighbors_established(output)

def build_bgp_flapping_runbook(device: dict) -> RemediationRunbook:
    """BGP runbook for one device (a Netmiko connection dict)."""
    runbook = RemediationRunbook("BGP Session Flapping")
    runbook.add_action(
        name="Clear BGP session",
        func=lambda: clear_bgp_session(device),
        validate_func=lambda: verify_bgp_stable(device),
        # A soft clear changes no configuration, so there's no undo_func
    )
    return runbook

# --- Interface Error Remediation ----------------------------------------

async def restart_interface(device, interface):
    """Bounce the interface (shutdown / no shutdown)."""
    await asyncio.to_thread(_session, device, lambda conn: conn.send_config_set([
        f"interface {interface}",
        "shutdown",
        "no shutdown"
    ]))

async def enable_interface(device, interface):
    """Undo step: make sure a failed bounce doesn't leave the port shut down."""
    await asyncio.to_thread(_session, device, lambda conn: conn.send_config_set([
        f"interface {interface}",
        "no shutdown"
    ]))

async def verify_interface_healthy(device, interface):
    """
    Verify the interface came back up/up.

    Error counters don't reset when an interface bounces, so the error
    *rate* is judged by the monitor's next measurement, not here.
    """
    output = await asyncio.to_thread(
        _session, device, lambda conn: conn.send_command(f"show interfaces {interface}")
    )
    return "is up, line protocol is up" in output

def build_interface_error_runbook(device: dict, interface: str) -> RemediationRunbook:
    """Interface runbook for one port on one device."""
    runbook = RemediationRunbook("High Interface Error Rate")
    runbook.add_action(
        name=f"Restart interface {interface}",
        func=lambda: restart_interface(device, interface),
        validate_func=lambda: verify_interface_healthy(device, interface),
        undo_func=lambda: enable_interface(device, interface),
    )
    return runbook
```

Runbooks are built per device, when an incident needs one, because each step must know which device (and port) to act on:

```python
runbook = build_interface_error_runbook(device, "GigabitEthernet1/0/24")
result = await runbook.execute(incident)
```

---

## Pattern 3: Incident Tracking & History

```python
# src/incident_tracker.py
import json
from datetime import datetime
from pathlib import Path
from typing import List
from incident_detector import Incident

class IncidentTracker:
    """Track incidents and remediation history."""
    
    def __init__(self, history_file: str = "incidents.jsonl"):
        self.history_file = Path(history_file)
    
    def record_incident(self, incident: Incident):
        """Log detected incident."""
        with open(self.history_file, "a") as f:
            record = {
                "type": "incident_detected",
                "timestamp": datetime.now().isoformat(),
                "incident": incident.to_dict()
            }
            f.write(json.dumps(record) + "\n")
    
    def record_remediation(self, incident_id: str, result: dict):
        """Log remediation attempt."""
        with open(self.history_file, "a") as f:
            record = {
                "type": "remediation_executed",
                "timestamp": datetime.now().isoformat(),
                "incident_id": incident_id,
                "result": result
            }
            f.write(json.dumps(record) + "\n")
    
    def get_incident_history(self, device: str = None) -> List[dict]:
        """Get incident history for device."""
        if not self.history_file.exists():
            return []
        
        incidents = []
        with open(self.history_file, "r") as f:
            for line in f:
                record = json.loads(line)
                
                # Filter by device if specified
                if device and record["type"] == "incident_detected":
                    if record["incident"]["device"] != device:
                        continue
                
                incidents.append(record)
        
        return incidents
    
    def get_mttr(self, days: int = 7) -> float:
        """
        Calculate Mean Time To Repair.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Average repair time in minutes
        """
        incidents = self.get_incident_history()
        
        incident_times = {}
        for record in incidents:
            if record["type"] == "incident_detected":
                incident_id = record["incident"]["id"]
                incident_times[incident_id] = {
                    "detected": record["timestamp"]
                }
            
            elif record["type"] == "remediation_executed":
                incident_id = record["incident_id"]
                if incident_id in incident_times:
                    incident_times[incident_id]["remediated"] = record["timestamp"]
        
        # Calculate repair time for incidents with remediation
        repair_times = []
        for inc_id, times in incident_times.items():
            if "remediated" in times:
                detected = datetime.fromisoformat(times["detected"])
                remediated = datetime.fromisoformat(times["remediated"])
                repair_time = (remediated - detected).total_seconds() / 60
                repair_times.append(repair_time)
        
        if repair_times:
            return sum(repair_times) / len(repair_times)
        return 0
```

---

## Pattern 4: Adaptive Response Based on History

```python
# src/adaptive_remediation.py
from typing import List
from incident_tracker import IncidentTracker
from remediation import RemediationRunbook

class AdaptiveRemediationEngine:
    """Learn from incident history and adjust remediation."""
    
    def __init__(self, tracker: IncidentTracker):
        self.tracker = tracker
        self.success_rates = {}
    
    def calculate_success_rate(self, remediation_name: str) -> float:
        """Calculate success rate of remediation type."""
        incidents = self.tracker.get_incident_history()
        
        total = 0
        successful = 0
        
        for record in incidents:
            if record["type"] == "remediation_executed":
                for action in record["result"].get("actions_taken", []):
                    if action["name"] == remediation_name:
                        total += 1
                        if action["success"]:
                            successful += 1
        
        if total == 0:
            return 0.0
        
        return (successful / total) * 100
    
    def select_remediation_strategy(
        self,
        incident_name: str,
        available_strategies: List[RemediationRunbook]
    ) -> RemediationRunbook:
        """
        Select best remediation based on historical success.
        
        Args:
            incident_name: Type of incident
            available_strategies: Possible remediation approaches
        
        Returns:
            Best remediation strategy based on history
        """
        strategy_scores = {}
        
        for strategy in available_strategies:
            success_rate = self.calculate_success_rate(strategy.incident_name)
            strategy_scores[strategy.incident_name] = success_rate
        
        # Return strategy with highest success rate
        best_strategy = max(
            available_strategies,
            key=lambda s: strategy_scores.get(s.incident_name, 0)
        )
        
        print(f"Selected strategy: {best_strategy.incident_name} "
              f"(success rate: {strategy_scores[best_strategy.incident_name]:.1f}%)")
        
        return best_strategy
```

---

<div class="np-reflection" markdown>
<p class="np-reflection-label">Between the Lines</p>
<p>"If you can keep your head when all about you / Are losing theirs and blaming it on you" is usually read as advice for the crisis itself. It is really advice for the ordinary hours beforehand.</p>
<p>Nobody becomes calm at 3am by deciding to be. They are calm because the detection, the runbook and the rollback were written on an unremarkable Tuesday by somebody who was not panicking — which is the strongest argument for doing this work while nothing is on fire.</p>
</div>

## Best Practices

### 1. Separate Automatic vs Manual Remediation

```python
# ✅ GOOD - Clear separation
async def handle_incident(incident):
    match incident.severity:
        case SeverityLevel.LOW:
            await automatic_remediation.execute(incident)

        case SeverityLevel.CRITICAL:
            await escalate_to_noc(incident)

# ❌ BAD - Auto-fix critical issues
async def auto_fix_critical(incident):
    if incident.severity == SeverityLevel.CRITICAL:
        await automatic_fix(incident)  # Too risky!
```

### 2. Always Validate Before and After

```python
# ✅ GOOD - Comprehensive validation
async def remediate():
    # Validate current state
    if not await validate_incident():
        return False
    
    # Apply fix
    await fix_issue()
    
    # Validate fix worked
    if not await validate_fix():
        await rollback()
        return False
    
    return True

# ❌ BAD - No validation
async def remediate():
    await fix_issue()  # Hope it works
```

### 3. Design for Rollback

```python
# ✅ GOOD - Keep rollback capability
actions = [
    RemediationAction(
        "update_config",
        func=update_config,
        undo_func=restore_previous_config  # How to put it back
    )
]

# ❌ BAD - No way to undo
async def fix_issue():
    delete_old_config()  # Can't rollback
    apply_new_config()
    restart_service()
```

### 4. Track and Learn

```python
# ✅ GOOD - Record all activity
async def track_and_learn(incident):
    tracker.record_incident(incident)
    result = await remediation.execute(incident)
    tracker.record_remediation(incident.id, result)

    # Analyze and improve
    mttr = tracker.get_mttr()
    print(f"MTTR: {mttr:.1f} minutes")

# ❌ BAD - Silent failures
async def silent_remediation(incident):
    await remediation.execute(incident)  # No record of what happened
```

---

## Production Deployment Example

```python
# src/automation_engine.py
import asyncio
import re
from datetime import datetime
from typing import List
from netmiko import ConnectHandler
from incident_detector import Incident, PatternMatcher, RemediationType, SeverityLevel
from remediation_runbooks import build_bgp_flapping_runbook
from incident_tracker import IncidentTracker

class AutomationEngine:
    """Main orchestration for incident detection and response."""
    
    def __init__(self, devices: List[dict]):
        self.devices = devices
        self.detector = PatternMatcher()
        self.tracker = IncidentTracker()
        self.runbook_builders = {}
        
        # Register patterns
        self._register_patterns()
        
        # Register runbooks
        self._register_runbooks()
    
    def _register_patterns(self):
        """Register all incident detection patterns."""
        # BGP flapping: a session changed state within the hour, and at
        # least one neighbour is down right now
        self.detector.register_pattern(
            name="BGP Session Flapping",
            check_func=lambda m: (
                m.get("bgp_changes_hour", 0) > 0 and
                not m.get("bgp_established", True)
            ),
            severity=SeverityLevel.HIGH,
            remediation_type=RemediationType.AUTOMATIC
        )
        # ... more patterns
    
    def _register_runbooks(self):
        """Register runbook builders: runbooks are built per device on demand."""
        self.runbook_builders["BGP Session Flapping"] = build_bgp_flapping_runbook

    # --- Metric parsers: plain functions of CLI text, easy to unit test ---

    @staticmethod
    def _bgp_neighbor_rows(bgp_summary: str) -> List[List[str]]:
        """Split the neighbour table of 'show ip bgp summary' into columns."""
        _, found, table = bgp_summary.partition("Neighbor")
        if not found:
            return []
        return [line.split() for line in table.splitlines()[1:] if line.strip()]

    def _count_bgp_changes(self, bgp_summary: str) -> int:
        """
        Neighbours whose session went up or down within the last hour.

        Up/Down shows hh:mm:ss for times under a day (longer ones look like
        2d03h), so 00:mm:ss means the state changed less than an hour ago.
        """
        return sum(
            1 for row in self._bgp_neighbor_rows(bgp_summary)
            if re.fullmatch(r"00:\d\d:\d\d", row[-2])
        )

    def _check_bgp_established(self, bgp_summary: str) -> bool:
        """True if every neighbour shows a prefix count (not Idle/Active...)."""
        return all(row[-1].isdigit() for row in self._bgp_neighbor_rows(bgp_summary))

    def _get_interface_errors(self, input_error_lines: str) -> int:
        """Total input errors across all interfaces."""
        return sum(int(n) for n in re.findall(r"(\d+) input errors", input_error_lines))

    def _collect_metrics(self, device: dict) -> dict:
        """Blocking Netmiko work; check_device() runs it in a worker thread."""
        with ConnectHandler(**device) as conn:
            bgp_summary = conn.send_command("show ip bgp summary")
            input_errors = conn.send_command("show interfaces | include input errors")

        return {
            "reachable": True,
            "bgp_changes_hour": self._count_bgp_changes(bgp_summary),
            "bgp_established": self._check_bgp_established(bgp_summary),
            "interface_errors": self._get_interface_errors(input_errors)
        }

    async def check_device(self, device: dict) -> List[Incident]:
        """Collect metrics and detect incidents."""
        try:
            metrics = await asyncio.to_thread(self._collect_metrics, device)
            return self.detector.detect(device["host"], metrics)

        except Exception as e:
            return [Incident(
                id="INC-UNREACHABLE",
                name="Device Unreachable",
                severity=SeverityLevel.CRITICAL,
                device=device["host"],
                symptoms={"error": str(e)},
                detected_at=datetime.now(),
                remediation_type=RemediationType.ESCALATE,
                likely_causes=["Network down", "Device down"]
            )]
    
    async def run(self, check_interval: int = 60):
        """Main event loop."""
        print("Starting incident response engine...")
        
        while True:
            print(f"\n[{datetime.now()}] Checking devices...")
            
            # Check all devices, keeping each incident with its device
            found = []
            for device in self.devices:
                for incident in await self.check_device(device):
                    found.append((device, incident))

            # Process incidents
            for device, incident in found:
                print(f"\n{incident.severity.value.upper()}: {incident.name} on {incident.device}")

                self.tracker.record_incident(incident)

                # Only auto-remediate lower severity
                if incident.remediation_type == RemediationType.AUTOMATIC:
                    if incident.name in self.runbook_builders:
                        runbook = self.runbook_builders[incident.name](device)
                        result = await runbook.execute(incident)
                        self.tracker.record_remediation(incident.id, result)

                else:
                    print(f"  ⚠ Escalating to NOC: {incident.likely_causes}")
            
            # Wait for next check
            await asyncio.sleep(check_interval)
```

---

## Summary

Incident automation provides:

- **Detection** → Pattern matching identifies problems
- **Response** → Automatic remediation for known issues
- **History** → Track what happened and why
- **Learning** → Improve over time based on results
- **Visibility** → Know MTTR and system health

---

## Related Patterns

- **[Testing Patterns](../intermediate/testing-network-automation.md)** — Test remediation behaviours
- **[Health Checks](../intermediate/health-checks-pre-flight-validation.md)** — Detect issues early
- **[Circuit Breakers](./circuit-breakers-backpressure-network-automation.md)** — Prevent cascade failures
