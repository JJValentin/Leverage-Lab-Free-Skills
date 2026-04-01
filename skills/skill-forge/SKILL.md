---
name: skill-forge
description: |
  Create new agent skills or optimize existing ones with deep analysis, quality gates, and synthesis panel approval. Use when creating skills, improving skills, optimizing skills, auditing skill quality, or when user says "forge skill", "create skill", "improve skill", "make skill better".
license: MIT
metadata:
  version: 1.1.0
  author: skill-forge
  sources: SkillCreator v3.1, Structured Reasoning v2.0, Agent Skills Spec
---

# Skill Forge - Create & Optimize Agent Skills

Unified skill for creating new skills AND optimizing existing ones. Auto-routes based on skill existence.

---

## Triggers

- "skill-forge: create {goal}" or "forge new skill" - CREATE mode
- "skill-forge: optimize {skill-name}" or "improve this skill" - OPTIMIZE mode
- "create skill for {purpose}" - CREATE mode
- "audit this skill" or "score this skill" - OPTIMIZE assess-only
- "make this skill better" - OPTIMIZE mode

---

## How It Works

Your request - skill exists? YES = OPTIMIZE, NO = CREATE. Both share the quality framework: 11 thinking lenses, regression questioning, evolution scoring (>=7), synthesis panel (3/3 unanimous).

---

## Quality Standards (Must Pass)

- Name: lowercase, hyphens, 1-64 chars, matches folder
- Description: WHAT + WHEN + trigger keywords, <=1024 chars, no angle brackets
- Size: <=500 lines / <=5000 tokens
- References: one level deep only (no nested chains)
- Triggers: 3-5 natural language phrases (compact, one per line)
- Extension Points: >=2 documented
- Timelessness: score >=7/10
- No pipe tables anywhere - use compact formats

---

## CREATE Mode

Phase 1 - Deep Analysis: expand requirements (explicit, implicit, unknown unknowns), apply 11 thinking lenses, regression questioning until 3 empty rounds
Phase 2 - Specification: XML spec with all decisions + WHY, validate timelessness >=7
Phase 3 - Generation: fresh context, zero errors, SKILL.md <=500 lines, references one level deep
Phase 4 - Synthesis Panel: 3 agents (Design, Audience, Evolution), unanimous 3/3 required, loop with feedback if rejected

See: references/create-mode.md

---

## OPTIMIZE Mode

Phase 1 - Assessment: load skill, score each quality dimension 1-10, identify strengths/weaknesses
Phase 2 - Gap Analysis: apply relevant lenses to weaknesses, prioritize with ICE score
Phase 3 - Preservation: map what works (DON'T BREAK), plan surgical changes, backward compat check
Phase 4 - Targeted Generation: incremental changes only, preserve working patterns, generate changelog
Phase 5 - Synthesis Panel: same 3 agents + "Did we break anything?" check, unanimous required

See: references/optimize-mode.md

---

## Commands

- `--assess-only` - assessment without changes
- `--plan-only` - specification only
- `/status` - show progress

---

## Anti-Patterns (Must Avoid)

- Nested references - use one level deep only
- Over-explaining - be concise, AI is smart
- Vague descriptions - WHAT + WHEN + keywords
- Magic numbers - document the WHY
- Single trigger - use 3-5 varied phrases
- Missing WHY - document rationale
- Pipe tables - use compact key: value format

---

## Output Structure

```
~/.openclaw/skills/{skill-name}/
  SKILL.md          # Main (<=500 lines)
  references/       # Deep docs (one level)
  scripts/          # Tools (optional)
```

---

## 11 Thinking Lenses (Quick Reference)

First Principles - What is fundamentally needed?
Inversion - What guarantees failure?
Second-Order - What happens after the obvious?
Pre-Mortem - Why did this fail (future)?
Systems - How do parts interact?
Devil's Advocate - Strongest counter-argument?
Constraints - What's truly fixed?
Pareto - Which 20% delivers 80%?
Root Cause - Why is this needed? (5 Whys)
Comparative - How do options stack up?
Opportunity Cost - What are we giving up?

Minimum: all 11 scanned, >=5 applied in depth. See: references/11-lenses.md

---

## Synthesis Panel

- Design agent: structure, patterns, correctness
- Audience agent: clarity, triggers, usability
- Evolution agent: timelessness >=7, extension points

Requirement: unanimous 3/3, max 5 iterations. See: references/synthesis-panel.md

---

## Timelessness Scoring

1-3 - Reject (ephemeral), 4-6 - Revise (moderate), 7-8 - Approve (solid), 9-10 - Exemplary (timeless)

See: references/quality-framework.md

---

## Extension Points

1. Additional Lenses - add to references/11-lenses.md for domain-specific analysis
2. Quality Criteria - extend references/quality-framework.md with new scoring dimensions
3. New Panel Agents - add specialized evaluators for domain expertise
4. Domain Templates - skill templates for common patterns (API integration, workflow automation)

---

## References

- references/create-mode.md - full creation workflow
- references/optimize-mode.md - full optimization workflow
- references/quality-framework.md - scoring rubrics
- references/11-lenses.md - thinking model details
- references/synthesis-panel.md - panel protocol
