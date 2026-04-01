---
name: structured-reasoning
description: |
  Apply structured multi-mode reasoning for complex decisions using the Engineering Flywheel framework. Use when making Type 1 irreversible decisions, comparing options with tradeoffs, debugging non-obvious failures, planning strategy, or resolving disagreements. Supports light, deep, and consensus modes with optional thinker validation.
metadata:
  timelessness_score: 8
---

# Structured Reasoning

Multi-mode structured reasoning for complex decisions, especially Type 1 (irreversible) decisions.

---

## Triggers

- "help me decide" or "what should I choose" - decision support
- Type 1 decisions: contracts, partnerships, major purchases, architecture choices
- "compare these options" or "weigh the tradeoffs" - multi-factor analysis
- "something broke and I don't know why" - debugging with structured approach
- "think through this carefully" - explicit reasoning request

---

## The Engineering Flywheel (8 Phases)

All decisions flow through these phases. Depth varies by mode.

**Phase 1 - Problem Framing:** What is success? What are hard constraints? What does failure look like?
**Phase 2 - Context Gathering:** Read relevant files, data, prior decisions (memory_recall). Map current state.
**Phase 3 - First Principles:** Challenge assumptions. Find bedrock truths. Expose the real problem. Build up from basics, not analogy.
**Phase 4 - Creative Synthesis:** Generate 2-4 options from fundamentals. Design simplest path for each.
**Phase 5 - Validation & Delete:** Test options against requirements. Prune complexity. Spawn thinker for Type 1 decisions.
**Phase 6 - Execute:** DECISION + CONFIDENCE (High/Medium/Low) + RATIONALE
**Phase 7 - Review:** NEXT ACTION + REVIEW TRIGGER + SUCCESS METRICS
**Phase 8 - Update Memory:** Log to MEMORY.md and daily notes. Document pattern for future decisions.

---

## Decision Routing

Reversibility test:
- YES (Type 2, reversible) - Light Mode: compressed flywheel, no thinker, decide today
- NO (Type 1, irreversible) - Deep Mode: full flywheel + thinker validation
- NO + highest stakes - Consensus Mode: thinker runs independent flywheel

Complexity test:
- Simple/obvious - skip structured reasoning entirely
- Medium complexity - Light Mode
- Complex with tradeoffs - Deep Mode
- Irreversible + high stakes - Consensus Mode

---

## Light Mode (Type 2 decisions, 2-3 min)

Compressed flywheel: 1-2 sentence problem statement, quick context check, challenge 1-2 assumptions, generate 2-3 options, pick simplest that works, state decision, set next action, quick note to daily log. Skip thinker.

---

## Deep Mode (Type 1 decisions, 5-10 min)

Full 8-phase flywheel with no shortcuts. At Phase 5, spawn thinker for validation:

```javascript
sessions_spawn({
  task: "Validate this Type 1 decision. SITUATION: [summary]. MY RECOMMENDATION: [choice and rationale]. Challenge: 1. What am I missing? 2. Strongest counter-argument? 3. Agree or disagree and why? 4. Blind spots?",
  model: "thinker",
  thinking: "high",
  label: "thinker-validation"
})
```

Synthesize thinker feedback before Phase 6.

---

## Consensus Mode (Highest-stakes Type 1)

For architecture lock-in, pricing/positioning, contracts, partnerships.

Phases 1-4 standard. Phase 5: spawn thinker with FULL context from all phases, request independent flywheel. Compare results, resolve conflicts, then proceed to Phase 6-8 with consensus decision.

```javascript
sessions_spawn({
  task: "Run your own independent Engineering Flywheel on this decision: [full context from phases 1-4]. Provide: 1. Your Problem Framing 2. Your First Principles analysis 3. Your options 4. Your recommendation 5. Where you disagree",
  model: "thinker",
  thinking: "high",
  label: "thinker-consensus"
})
```

---

## Output Format

Always end with:
- DECISION: [Clear statement]
- CONFIDENCE: High/Medium/Low
- RATIONALE: [Why - reference flywheel phases]
- NEXT ACTION: [Specific first step]
- REVIEW TRIGGER: [When to revisit]
- SUCCESS METRICS: [How we know it worked]

---

## Auto-Skip Conditions

Do NOT use for: simple factual questions, quick tasks, low-stakes Type 2 decisions, casual conversation.

---

## Extension Points

1. Custom flywheel phases - add domain-specific phases for specialized decision types
2. Thinker model alternatives - swap in different validation models as they become available
3. Decision templates - pre-configured flywheel shortcuts for recurring decision types (hiring, architecture, pricing)
