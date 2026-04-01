# OPTIMIZE Mode - Full Workflow

Complete protocol for improving existing skills without breaking them.

---

## Phase 1: Assessment

Load and score existing skill across 8 dimensions (1-10 each):
- Frontmatter Validity — required fields present, correct format
- Description Quality — WHAT + WHEN + keywords, specific
- Size Compliance — ≤500 lines, appropriate depth
- Reference Structure — one level deep, properly linked
- Trigger Coverage — 3-5 natural language phrases
- Extension Points — ≥2 documented
- Timelessness — principle-based, score ≥7
- Anti-pattern Avoidance — clean, no major anti-patterns

Scoring:
- 1-3: broken/missing
- 4-6: present but weak
- 7-8: meets standard
- 9-10: exemplary

### Assessment Output Format

```markdown
## Assessment: {skill-name}
Overall: X.X/10

Frontmatter: X/10 — [notes]
Description: X/10 — [notes]
Size: X/10 — [notes]
References: X/10 — [notes]
Triggers: X/10 — [notes]
Extension Points: X/10 — [notes]
Timelessness: X/10 — [notes]
Anti-patterns: X/10 — [notes]

Strengths (preserve): [list]
Weaknesses (fix): [list]
Critical Issues: [list]
```

---

## Phase 2: Gap Analysis

For each weakness, apply the relevant lens (see 11-lenses.md):

Vague description → First Principles → rewrite with WHAT+WHEN+keywords
No extension points → Systems Thinking → add ≥2 extension points
Nested references → Constraint Analysis → flatten to one level
Poor triggers → Audience Simulation → add natural language alternatives
Over-explaining → Pareto → cut to essential 20%

Prioritize with ICE score (Impact × Confidence × Ease). Fix highest ICE first.

---

## Phase 3: Preservation Analysis

Document what MUST be preserved before making changes:

```markdown
## Preservation List

Core Functionality:
- [feature] — used by [workflows]

Established Triggers:
- "{trigger}" — KEEP (users rely on this)

Working Integrations:
- Integrates with: {other skill}
```

Surgical Change Plan:
- Improve (not replace): weak descriptions, add triggers without removing old
- Add: extension points, new triggers for discoverability
- Remove: anti-patterns, redundancy, nested references
- Keep unchanged: core workflow, existing triggers (backward compat)

---

## Phase 4: Targeted Generation

Apply changes surgically:
1. Copy all preserved elements unchanged
2. Improve weak areas per change plan
3. Add new triggers, extension points
4. Remove anti-patterns, redundancy
5. Update links if structure changed

Generate change log:
```markdown
## Changes: v{new} from v{old}
Improved: [list]
Added: [list]
Removed: [list]
Preserved: [list]
Migration Notes: [any breaking changes]
```

---

## Phase 5: Synthesis Panel

Same 3 agents as CREATE mode + optimization-specific checks:
- Design: "Did structure changes break flow?"
- Audience: "Did we break established triggers?"
- Evolution: "Did we improve without regression?"

Optimization rejection triggers:
- Broke existing trigger → REJECT
- Removed working feature (without approval) → REJECT
- Introduced new anti-pattern → REJECT
- Net score decrease → REJECT

---

## Quick Checklist

Before: skill exists and readable, user confirmed scope, original backed up
Assessment: all 8 dimensions scored, strengths identified, weaknesses prioritized (ICE)
Preservation: core functionality mapped, triggers documented, backward compat planned
Generation: changes incremental, change log complete, nothing broken
Panel: all 3 approved, no backward compat issues, net improvement confirmed
