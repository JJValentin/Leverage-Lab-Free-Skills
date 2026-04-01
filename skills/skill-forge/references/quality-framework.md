# Quality Framework

Unified quality criteria from Agent Skills spec, SkillCreator, and practical guidance.

---

## Frontmatter Requirements

Required fields:
```yaml
---
name: skill-name       # REQUIRED: lowercase, hyphens, 1-64 chars, matches folder
description: |         # REQUIRED: WHAT + WHEN + keywords, ≤1024 chars, no angle brackets
  What it does.
  When to use it.
  Trigger keywords.
---
```

Optional: `license`, `compatibility`, `metadata` (author, version, category)

Name regex: `^[a-z0-9]+(-[a-z0-9]+)*$`

---

## Description Quality

1-3: vague, missing WHAT or WHEN
4-6: has WHAT and WHEN, missing keywords
7-8: WHAT + WHEN + keywords, specific
9-10: action verb + context + keywords + examples

Template: `[ACTION VERB] [WHAT]. [WHEN to use / trigger context]. [Keywords for activation].`

Good example: `Generate commit messages following conventional commit format. Use when user asks for help with git commits, commit messages, or conventional commits.`

---

## Size Requirements

SKILL.md: ≤500 lines, ~5000 tokens — keep it lean
Reference depth: 1 level only — nested chains cause partial reads

Why one level? AI may use `head -100` on nested files. One level is reliable across all implementations.

---

## Trigger Requirements

Count: 3-5 distinct phrases
Style: natural language, varied phrasings
Format: compact (no tables) — one trigger per line

Good triggers: `skill-forge: create {goal}`, `forge new skill`, `improve this skill`, `make skill better`
Bad triggers: `sf` (cryptic), `create` (too generic), `skill management system v2` (too technical)

---

## Timelessness Scoring

1-3: ephemeral (weeks-months) → Reject
4-6: moderate (1-2yr) → Revise
7-8: solid (2-4yr) → Approve
9-10: timeless (5+ yr) → Exemplary

Anti-obsolescence: design around principles not implementations, document WHY not just WHAT, include extension points, abstract volatile dependencies, version-agnostic patterns.

---

## Extension Points

Every skill needs ≥2 documented extension points.

Types: feature plugins, capability additions, output format templates, validation rules

Document as:
```markdown
## Extension Points
1. **[Name]** - [Purpose] — Location: [path], Mechanism: [how to extend]
2. **[Name]** - [Purpose] — Location: [path], Mechanism: [how to extend]
```

---

## Anti-Patterns

Nested references (`reference/x/y.md`) → flatten to one level
Over-explaining (>500 lines) → cut to essentials
Vague description → rewrite with WHAT+WHEN+keywords template
Windows paths (backslashes) → use forward slashes
Magic numbers (unexplained constants) → document WHY
Too many options → pick default, mention alternatives sparingly
Single trigger → add 3-5 triggers
Missing WHY → document reasoning
Version pinning (hardcoded versions) → abstract dependencies
No extension points → add ≥2
Markdown tables in agent docs → use compact inline formats instead

---

## Synthesis Panel Thresholds

Design agent: min avg 7.0, 0 critical issues allowed
Audience agent: min avg 7.0, 0 critical issues allowed
Evolution agent: min avg 7.0 (timelessness ≥7), 0 critical issues allowed
