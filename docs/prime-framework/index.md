---
title: The PRIME Framework
description: The five-stage method Christopher Davies uses to take Cisco automation from identifying inefficiencies to a team that owns the result, on contract or project work.
tags:
  - PRIME Framework
  - Methodology
  - Network Automation
  - Consulting
---

<div class="np-hero" markdown>

<p class="np-eyebrow">How I approach automation work, on contract or on a project</p>

## The PRIME Framework

The PRIME Framework is the five-stage method I use for turning operational pain points into production-grade automation, measurable ROI, and real team ownership. It exists to stop organisations automating the wrong things, shipping brittle scripts, and ending up dependent on the original author.

<div class="np-action-row" markdown>

[Read the Philosophy](./philosophy.md){.md-button .md-button--primary}
[Work With Me](../work-with-me/index.md){.md-button}
[How a Project Runs](../how-we-work.md){.md-button}

</div>

<ul class="np-signal-list">
  <li>Five-stage delivery model</li>
  <li>Business case before build</li>
  <li>Safety and handover built in</li>
  <li>Designed for team ownership</li>
</ul>

</div>

## Who the framework is for

<div class="grid cards" markdown>

-   ### Leaders who need proof before they invest

    Use the framework when leadership needs a clear business case, measured value, and visibility into what automation is actually achieving.

-   ### Teams inheriting fragile scripts

    Use the framework when existing automation works just enough to be risky, but nobody wants to own, change, or troubleshoot it.

-   ### Engineers moving from one-off scripts to a programme

    Use the framework when the goal is not just faster tasks, but a repeatable automation operating model that can scale.

-   ### Organisations that cannot afford unsafe change

    Use the framework when validation, rollback, governance, and gradual rollout matter as much as delivery speed.

</div>

---

## 🎯 Why a Framework?

Network automation isn't just about writing scripts—it's about **transforming operations**. Too many automation projects fail because they:

- ❌ Automate the wrong things (busy work instead of bottlenecks)
- ❌ Lack production safety (untested code hits critical infrastructure)
- ❌ Create new technical debt (unmaintainable "black box" scripts)
- ❌ Don't measure impact (no ROI visibility)
- ❌ Fail to transfer knowledge (dependency on one person)

The PRIME Framework addresses all of these challenges with a structured approach.

---

## 📐 The Five Stages

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontSize':'18px'}}}%%
graph LR
    P[Pinpoint]
    R[Re-engineer]
    I[Implement]
    M[Measure]
    E[Empower]
    P --> R
    R --> I
    I --> M
    M --> E
    style P fill:#4A90E2
    style R fill:#7B68EE
    style I fill:#50C878
    style M fill:#FFB347
    style E fill:#FF6B9D
```

### [**P** — Pinpoint](./pinpoint.md) Inefficiencies

**Objective:** Identify high-impact automation opportunities

**What Happens:**

- Workflow analysis and time-motion studies
- Identification of repetitive manual tasks
- Risk assessment of error-prone processes
- ROI estimation for potential automations

**Deliverable:** Prioritised automation roadmap with estimated savings

---

### [**R** — Re-engineer](./re-engineer.md) Workflows

**Objective:** Design optimised processes before automating

**What Happens:**

- Process redesign (don't automate bad workflows!)
- Architecture planning for scalability
- Safety mechanism design (pre-flight checks, rollback capability)
- Integration planning with existing tools

**Deliverable:** Technical design documents and workflow diagrams

---

### [**I** — Implement](./implement.md) Solutions

**Objective:** Build production-ready automation following the [PRIME Philosophy](./philosophy.md)

**What Happens:**

- Development of hardened Python scripts
- Line-by-line documentation for transparency
- Comprehensive error handling and validation
- Testing in lab/staging environment

**Deliverable:** Production-ready code with full documentation

---

### [**M** — Measure](./measure.md) Performance

**Objective:** Prove value and continuously improve

**What Happens:**

- Metrics collection (time saved, errors eliminated)
- Performance monitoring and optimisation
- User feedback gathering
- Iterative refinement based on real-world usage

**Deliverable:** ROI reports and optimised automation

---

### [**E** — Empower](./empower.md) Your Team

**Objective:** Ensure long-term success and self-sufficiency

**What Happens:**

- Knowledge transfer and training
- Documentation and runbooks
- Ongoing support window
- Capability building for internal teams

**Deliverable:** Self-sufficient teams with transferable skills

---

## 🔄 Why This Framework Works

### 1. **Starts with Value, Not Technology**

The "Pinpoint" stage ensures we're solving real problems, not automating for automation's sake. Every project begins with a business case.

### 2. **Emphasises Design Over Quick Fixes**

The "Re-engineer" stage prevents the common mistake of automating broken workflows. We optimise first, then automate.

### 3. **Prioritises Production Safety**

The "Implement" stage isn't just coding—it's building with enterprise-grade error handling, validation, and transparency.

### 4. **Proves Return on Investment**

The "Measure" stage provides concrete evidence of value, justifying continued investment in automation.

### 5. **Builds Capability, Not Dependency**

The "Empower" stage ensures clients aren't dependent on external consultants—they gain skills and confidence.

---

## 🎓 Framework + Philosophy

The PRIME Framework is how we **deliver** automation projects. The **[PRIME Philosophy](./philosophy.md)** defines **how we think and build**:

**Core Principles:**

- **Transparency Over Obscurity** — Every line of code explained, no black boxes
- **Measurability Over Assumptions** — Data-driven decisions, proven ROI
- **Ownership Over Dependency** — Your team owns the automation, not us
- **Safety Over Speed** — Production-grade reliability, not quick hacks
- **Empowerment Over Magic Buttons** — Understanding, not mysterious automation

**[Read the full Philosophy →](./philosophy.md)**

| PRIME Stage | Philosophy Application |
| :--- | :--- |
| **Pinpoint** | Vendor-neutral analysis (no tool lock-in) |
| **Re-engineer** | Production-hardened design from the start |
| **Implement** | Line-by-line transparency in all code |
| **Measure** | Honest, documented results |
| **Empower** | Knowledge transfer, not gatekeeping |

Together, they ensure **value, quality, and sustainability**.

---

<div class="np-reflection" markdown>
<p class="np-reflection-label">Between the Lines</p>
<p>Aristotle opens the <em>Nicomachean Ethics</em> by observing that every craft aims at some good, and that if the chain of means never arrives anywhere, wanting anything at all would be empty. It is a fair question to put to any method: what is it finally for?</p>
<p>None of the five stages exist to make work feel busier. They exist so a task that used to occupy someone&rsquo;s evening can be handled in thirty seconds instead &mdash; which only matters if that evening then belongs to something other than the next ticket.</p>
</div>

---

## 💼 Framework in Practice

### Typical Timeline (Medium Complexity Project)

| Stage | Duration | Key Milestone |
| :--- | :---: | :--- |
| Pinpoint | 1 week | Automation roadmap approved |
| Re-engineer | 1-2 weeks | Technical design signed off |
| Implement | 2-4 weeks | Code delivered & tested |
| Measure | 2-4 weeks | ROI demonstrated |
| Empower | 1-2 weeks | Team trained & autonomous |

**Total:** 7-13 weeks for most projects

### Investment by Stage

Projects are priced as fixed-fee engagements based on scope and complexity. You can engage for:

- **Full Framework** (all five stages) — Recommended for maximum value and sustainable ROI
- **Selected Stages** (e.g., Implement + Empower) — When design documentation already exists
- **Pinpoint Assessment Only** — Understand opportunities before committing to full engagement

**For project pricing, see [Consultancy (by enquiry)](../services/index.md). On a contract, the same stages shape how I plan and deliver the work.**

!!! info "Flexible structure"
    The stages flex to your timeline and budget. Most projects would take 7-13 weeks, and payment for projects can be structured around milestones.

---

## 📊 What the framework aims for

!!! success "Target outcomes"
    - **Large time savings** on repetitive tasks such as VLAN provisioning and config audits
    - **Far fewer configuration errors**, because changes are templated, validated and checked before and after
    - **A clear payback case**, estimated in Pinpoint before any build starts
    - **Knowledge transfer** — the team can run, change and extend the automation without the original author

    These are the goals the stages are designed around, not measured client results.

---

## 🚀 Getting Started with PRIME

<div class="np-cta-strip" markdown>

### Want this method on your team?

I apply the PRIME Framework whether I'm working on contract inside your team or on a fixed-scope project. Start with [Work With Me](../work-with-me/index.md), or read how a [project runs stage by stage](../how-we-work.md).

<div class="np-action-row" markdown>

[Work With Me](../work-with-me/index.md){.md-button .md-button--primary}
[How a Project Runs](../how-we-work.md){.md-button}
[Small Projects by Enquiry](../smb/index.md){.md-button}

</div>

</div>

### Typical entry path for a project

1. A short conversation to understand operational problems and constraints.
2. Optional [Pinpoint](./pinpoint.md) assessment to identify the highest-value opportunities.
3. The full framework or selected stages, depending on your needs.

---

## 🔍 Deep Dive: Individual Stages

Explore each stage in detail:

1. **[Pinpoint Inefficiencies](./pinpoint.md)** — How we identify the right automation targets
2. **[Re-engineer Workflows](./re-engineer.md)** — Optimising processes before coding
3. **[Implement Solutions](./implement.md)** — Building production-ready solutions
4. **[Measure Performance](./measure.md)** — Proving value and continuous improvement
5. **[Empower Your Team](./empower.md)** — Knowledge transfer and long-term success

---

## 🆚 PRIME Framework vs. Traditional Automation

How does the PRIME Framework compare to typical automation approaches?

| Aspect | Traditional Approach | PRIME Framework |
| :--- | :--- | :--- |
| **Discovery** | "What do you want automated?" | **Pinpoint:** Data-driven ROI analysis, prioritisation matrix |
| **Planning** | Jump straight to coding | **Re-engineer:** Workflow optimisation, architecture design, safety planning |
| **Development** | Quick scripts, minimal testing | **Implement:** Production-hardened with PRIME Philosophy principles |
| **Validation** | "It works on my laptop" | **Measure:** Metrics collection, ROI proof, continuous improvement |
| **Sustainability** | Vendor lock-in, no documentation | **Empower:** Knowledge transfer, team capability building |
| **Typical Outcome** | Script that works once, breaks later | **Prime Automation™** — sustainable, measurable, team-owned |
| **Business Value** | Unknown/untracked | Proven ROI (typically 6-12 month payback) |

**The difference:** Traditional automation delivers code. PRIME Framework delivers **capability**.

---

## 🎨 Prime Terminology

Throughout our framework and services, you'll encounter these unique terms:

| Term | Definition |
| :--- | :--- |
| **Prime Automation™** | Automation built following the PRIME Framework—characterised by measurable ROI, production safety, and team empowerment |
| **Prime Workflows** | Re-engineered operational processes optimised for automation (not just automated existing workflows) |
| **Prime Agents** | Python scripts developed with autonomous decision-making capability (pre-flight checks, validation, rollback) |
| **Prime Efficiency Stack** | The technology foundation (Netmiko, Nornir, TextFSM, Jinja2) used across all implementations |
| **Prime Overwatch™** | Continuous monitoring and metrics collection (Measure stage) for automation performance |
| **Prime Capability** | The end goal of the Empower stage—teams that can maintain, modify, and extend automation independently |

These aren't just buzzwords: each names a specific approach in the method.

---

## 📊 Illustrative Scenarios

!!! note "Hypothetical examples"
    These scenarios are hypothetical, written to show how the five stages fit together. They are not client case studies, and the figures are illustrative estimates.

### Scenario 1: Access Layer VLAN Provisioning → Prime Automation™

**Scenario:** A UK financial services firm, 300+ access switches  
**Challenge:** Manual VLAN adds taking 15 mins/switch, high error rate  
**PRIME Stages:**

- **Pinpoint:** Identified 200+ VLAN changes/year = 50 hours wasted
- **Re-engineer:** Designed **Prime Workflows** with templated provisioning + approval gates
- **Implement:** **Prime Agent** using Jinja2 templates with pre/post-flight validation
- **Measure:** **Prime Overwatch™** tracked 2 mins/change average, error-free operations over 6 months
- **Empower:** Team achieved **Prime Capability**—now extends scripts for SVI creation

**Illustrative ROI:** £12,500/year savings, 6-month payback

---

### Scenario 2: Compliance Audit Automation → Prime Efficiency Stack

**Scenario:** A healthcare provider, 150 Cisco devices, quarterly PCI-DSS audits  
**Challenge:** Manual config review taking 40 hours per quarter  
**PRIME Stages:**

- **Pinpoint:** Compliance checking identified as most time-intensive task
- **Re-engineer:** Defined "golden config" standards in YAML, created **Prime Workflows**
- **Implement:** **Prime Agent** built on **Prime Efficiency Stack** (Netmiko + TextFSM + pandas)
- **Measure:** **Prime Overwatch™** showed 97% reduction in audit time (40h → 1h)
- **Empower:** Security team gained **Prime Capability** to maintain golden configs

**Illustrative ROI:** £8,000/year savings, increased compliance confidence, 3x coverage

---

## 🎬 Experience the PRIME Framework

### Visual Overview

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontSize':'20px'}}}%%
graph TD
    A[Your Network Operations] -->|Inefficient Manual Work| B{PRIME Framework}
    B -->|Stage 1| C[Pinpoint: Discover ROI Opportunities]
    B -->|Stage 2| D[Re-engineer: Optimise Workflows]
    B -->|Stage 3| E[Implement: Build Prime Agents]
    B -->|Stage 4| F[Measure: Prime Overwatch™]
    B -->|Stage 5| G[Empower: Prime Capability]
    
    C --> H[Prime Automation™]
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I[Measurable ROI]
    H --> J[Team Independence]
    H --> K[Sustainable Growth]
    
    style B fill:#4A90E2
    style H fill:#50C878
    style I fill:#FFB347
    style J fill:#FFB347
    style K fill:#FFB347
```

---

## 📖 Additional Scenario

### Scenario 3: IOS-XE Upgrade Orchestration → Prime Agents Intelligence

**Scenario:** A retail chain, 200+ branch routers requiring IOS-XE 17.x upgrade  
**Challenge:** Manual upgrades took 1 hour/device, required site visits, unpredictable failures  
**PRIME Stages:**

- **Pinpoint:** 200 devices × 1 hour = 200 hours effort, travel costs £15k, compliance deadline
- **Re-engineer:** Designed **Prime Workflows** with staged rollouts (10% → 25% → 50% → 100%)
- **Implement:** **Prime Agent** with autonomous pre-flight checks (CPU, memory, disk space, MD5 verification)
- **Measure:** **Prime Overwatch™** tracked success rate (192/200 successful, 8 skipped due to hardware constraints)
- **Empower:** Network team achieved **Prime Capability**—now handles firmware updates independently

**Illustrative ROI:** £22,000 saved (160 hours + travel elimination), 96% success rate, no network downtime incidents

---

## 💡 Frequently Asked Questions

??? question "Do I need all five stages?"

    **For best results, yes.** The stages are sequential and build on each other. However, if you have existing design documentation, we can start at the "Implement" stage.
    
    If you're unsure about ROI, start with just the "Pinpoint" stage as a standalone assessment.

??? question "How is this different from other consultancies?"

    Most consultancies jump straight to implementation without understanding workflows ("Implement-first"). Others provide strategy without execution ("PowerPoint automation").
    
    The PRIME Framework combines **both strategy and execution** in one structure.

??? question "Can I implement the framework myself?"

    Absolutely! The framework isn't proprietary—it's a best-practice methodology. Our [Tutorials](../foundation/tutorials/index.md) and [Deep Dives](../foundation/deep-dives/index.md) give you the technical skills to follow the PRIME Framework internally.

??? question "What if my team is new to Python?"

    **You can still use the PRIME Framework.** We offer different engagement tracks:
    
    **Track 1: Operational Ownership (No Python Required)**
    
    - We deliver production-ready automation with comprehensive user documentation
    - Focus: Your team learns to **operate** the automation effectively
    - Empowerment: Understanding what automation does, when to run it, how to interpret results
    - Outcome: Reliable automation that reduces manual work, owned operationally by your team
    
    **Track 2: Code-Level Ownership (Python Knowledge Helpful)**
    
    - We deliver code with line-by-line technical documentation
    - Focus: Your team learns to **modify and extend** automation
    - Empowerment: Training includes Python fundamentals, code walkthroughs, modification workshops
    - Outcome: Full autonomy—your team writes new automation independently
    
    **Track 3: Hybrid (Recommended for Growing Teams)**
    
    - Operational ownership initially, with gradual code-level capability building
    - Focus: Start using automation immediately, build Python skills over time
    - Empowerment: Phased training—operations first, code literacy second, modification third
    - Outcome: Progressive independence as team skills develop
    
    See [Services: Engagement Tracks](../services/index.md#engagement-tracks-by-technical-capability) for detailed breakdowns.
    
    We also offer [beginner tutorials](../foundation/tutorials/beginner/index.md) to help your team build Python foundational skills.

??? question "How do you handle failed automations?"

    The "Measure" stage includes failure analysis and remediation. If automation doesn't deliver expected value, we refine iteratively. The fixed-fee model means we're incentivised to deliver working solutions.

---

## 🌟 Where to go next

The PRIME Framework takes the guesswork out of network automation, whether you're just starting or scaling existing efforts.

**Next Steps:**

- **[Understand the principles](./philosophy.md)** — Read the PRIME Philosophy
- **[Work with me](../work-with-me/index.md)** on contract, or ask about a [small fixed-scope project](../smb/index.md)
- **[Learn the foundations](../foundation/tutorials/index.md)** with free tutorials
- **[Study production tools](../foundation/deep-dives/index.md)** to see the framework in action

---

> **Mission:** To empower network engineers through the **[PRIME Framework](./index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](./philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.
