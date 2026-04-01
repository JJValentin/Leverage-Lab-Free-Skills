# CREATE Mode - Full Workflow

Complete protocol for creating new skills from scratch.

---

## Phase 1: Deep Analysis

### 1.1 Input Expansion

Transform user goal into comprehensive requirements:

```
USER INPUT: "Create a skill for X"
  → EXPLICIT REQUIREMENTS: what user literally asked for, direct functionality stated
  → IMPLICIT REQUIREMENTS: what they expect but didn't say, standard quality expectations, integration with existing patterns
  → UNKNOWN UNKNOWNS: what they don't know they need, expert-level considerations, future needs not anticipated
  → DOMAIN CONTEXT: related skills that exist, patterns from similar skills, lessons from skill failures
```

### 1.2 Overlap Check

Before proceeding, check for existing skills:

```bash
ls ~/.openclaw/skills/
grep -r "description:" ~/.openclaw/skills/*/SKILL.md | grep -i "{keyword}"
```

Match score actions:
- >7/10 → use existing skill instead
- 5-7/10 → clarify distinction before proceeding
- <5/10 → proceed with new skill

### 1.3 Apply 11 Thinking Lenses

See 11-lenses.md for full details. Minimum requirements:
- All 11 lenses scanned for relevance
- At least 5 lenses applied in depth
- At least 3 actionable insights documented
- Conflicts between lenses resolved

### 1.4 Regression Questioning

Iterative questioning until exhausted:

**Question Categories:**

1. Missing Elements — "What am I missing?" / "What assumptions am I making?" / "What edge cases haven't I addressed?"
2. Expert Simulation — "What would a UX expert add?" / "What would a security expert flag?" / "What would a maintenance engineer change?"
3. Failure Analysis — "What would make this skill fail completely?" / "What would make users abandon this skill?" / "What would make this skill obsolete?"
4. Temporal Projection — "Will this still work in 6 months?" / "What ecosystem changes are likely in 1 year?" / "Is the core problem still relevant in 2 years?"

**Termination Criteria:**
- Three consecutive rounds produce no new insights
- All 11 thinking models applied
- ≥3 simulated expert perspectives considered
- Evolution/timelessness evaluated with score ≥7

---

## Phase 2: Specification

Generate XML spec capturing all analysis insights:

```xml
<skill_specification>
  <metadata>
    <name>skill-name</name>
    <analysis_iterations>N</analysis_iterations>
    <timelessness_score>X/10</timelessness_score>
  </metadata>
  <context>
    <problem_statement>What + Why + Who</problem_statement>
    <existing_landscape>Related skills, distinctiveness</existing_landscape>
  </context>
  <requirements>
    <explicit>What user asked for</explicit>
    <implicit>Expected but unstated</implicit>
    <discovered>Found through analysis</discovered>
  </requirements>
  <architecture>
    <pattern>Selected pattern with WHY</pattern>
    <phases>Ordered phases with verification</phases>
    <decision_points>Branches and defaults</decision_points>
  </architecture>
  <evolution_analysis>
    <timelessness_score>X/10</timelessness_score>
    <extension_points>Where skill can grow</extension_points>
    <obsolescence_triggers>What would break it</obsolescence_triggers>
  </evolution_analysis>
  <anti_patterns>
    <pattern>What to avoid + WHY + alternative</pattern>
  </anti_patterns>
  <success_criteria>
    <criterion>Measurable + verification method</criterion>
  </success_criteria>
</skill_specification>
```

### Specification Validation

Before proceeding:
- [ ] All sections present with no placeholders
- [ ] Every decision includes WHY
- [ ] Timelessness score ≥7 with justification
- [ ] At least 2 extension points documented
- [ ] All requirements traceable to source

---

## Phase 3: Generation

**Context:** Fresh, clean (no analysis artifacts polluting)
**Standard:** Zero errors — every section verified before proceeding

### 3.1 Create Directory Structure

```bash
mkdir -p ~/.openclaw/skills/{skill-name}/references
mkdir -p ~/.openclaw/skills/{skill-name}/scripts  # if needed
```

### 3.2 Write SKILL.md

Follow this structure (≤500 lines total):

```markdown
# Skill Name - Brief Description
One-line summary.
---
## Quick Start
[Minimal example]
---
## Triggers
[3-5 trigger phrases — compact format, no tables]
---
## How It Works
[Flowchart or brief explanation]
---
## Quick Reference
[Key lookups — compact format, no tables]
---
## Commands
[Available commands/flags]
---
## Anti-Patterns
[What to avoid]
---
## Validation Checklist
[Verification steps]
---
## References
[Links to reference files]
---
## Changelog
[Version history]
```

### 3.3 Quality Checks During Generation

Frontmatter: only allowed properties (name, description, license, metadata)
Name: hyphen-case, ≤64 chars, matches folder
Description: ≤1024 chars, no angle brackets, WHAT+WHEN+keywords
Triggers: 3-5 distinct, natural language, compact format (no tables)
Size: ≤500 lines
References: one level deep only
Extension Points: ≥2 documented

### 3.4 Generate Reference Documents

For complex topics, create reference files:
- Keep main SKILL.md concise
- Move deep dives to references/
- One level deep only (no nested chains)

---

## Phase 4: Synthesis Panel

3 agents must unanimously approve. See synthesis-panel.md for full protocol.

Panel composition:
- Design agent: structure, patterns, correctness
- Audience agent: clarity, triggers, usability
- Evolution agent: timelessness ≥7, extension points, ecosystem fit

Consensus:
- All 3 APPROVED → finalize skill
- Any CHANGES_REQUIRED → return to Phase 1 with issues as input, re-apply questioning, regenerate, re-submit
- 5 iterations without consensus → flag for human review

---

## Architecture Pattern Selection

Simple linear tasks → Single-Phase (steps 1-2-3)
Quality/compliance audits → Checklist (item verification)
Creating artifacts → Generator (input → transform → output)
Complex ordered workflows → Multi-Phase (phase 1 → phase 2 → phase 3)
Coordinating multiple skills → Orchestrator (meta-skill chains)

### Selection Decision Tree

```
Is it a simple procedure?
  YES → Single-Phase
  NO → Does it produce artifacts?
    YES → Generator
    NO → Does it verify/audit?
      YES → Checklist
      NO → Multi-Phase or Orchestrator
```
