# Synthesis Panel Protocol

3 agents must unanimously approve. Unanimous = production-ready. Less = iterate.

---

## Agent Roles

Design agent — structure, patterns, correctness
- Key questions: Is the pattern right for this task? Are phases ordered correctly? Can each step be verified? Any logical inconsistencies? Would examples actually work?
- Red flags: wrong pattern, circular dependencies, vague verification, contradictory instructions, invalid syntax

Audience agent — clarity, triggers, usability
- Key questions: Would target audience naturally say these triggers? Can user follow each step without guessing? Are terms explained? Are examples provided? Would users find this skill?
- Red flags: triggers too technical, steps require unstated knowledge, jargon undefined, hard to discover

Evolution agent — timelessness, extensibility, ecosystem
- Key questions: Still valuable in 2 years? Extendable without rewriting? Volatile deps abstracted? Composes with other skills? WHY documented?
- Red flags: timelessness <7, no extension points, hardcoded deps, conflicts with existing skills, what without why

---

## Execution Protocol

Step 1: All 3 agents receive complete SKILL.md + reference docs
Step 2: Each produces structured review (scores, strengths, issues, recommendations, verdict: APPROVED or CHANGES_REQUIRED)
Step 3: Consensus check
  - All 3 APPROVED → finalize
  - Any CHANGES_REQUIRED → collect all issues, return to Phase 1, re-question, regenerate, re-submit
  - 5 iterations without consensus → escalate to human review

---

## Thresholds

Each agent needs: avg score ≥7.0, zero critical issues
Issue severity:
- Critical → blocks core function or violates key principle → auto CHANGES_REQUIRED
- Major → significant issue, workaround exists → ≥2 majors = CHANGES_REQUIRED
- Minor → improvement opportunity, non-blocking

---

## Optimization-Specific Extras

Additional questions for optimized skills:
- Design: "Did structure changes break flow?"
- Audience: "Did we break established triggers?"
- Evolution: "Did we improve without regression?"

Optimization rejection triggers: broke existing trigger, removed working feature without approval, introduced new anti-pattern, net score decrease

---

## Human Escalation Format (Round 5)

```markdown
## Human Review Required

Panel hasn't reached consensus after 5 iterations.

Remaining Disagreements:
- Design: [position] — [why]
- Audience: [position] — [why]
- Evolution: [position] — [why]

Options:
1. Accept with Design agent's recommendations
2. Accept with Audience agent's recommendations
3. Accept current state with documented limitations
4. Abandon and redesign from scratch
```
