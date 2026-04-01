# 11 Thinking Lenses

Systematic analysis framework ensuring comprehensive problem coverage. Apply all 11 (scan), apply ≥5 in depth, document ≥3 actionable insights.

---

1. **First Principles** — What is fundamentally needed? Strip conventions, find core utility, build from atomic requirements.
2. **Inversion** — What guarantees failure? List all failure modes → create explicit anti-patterns from each.
3. **Second-Order** — What happens after the obvious? Map consequence chains 3-4 levels deep. Example: skill generates docs → docs go stale → misleading docs worse than none → need sync mechanism.
4. **Pre-Mortem** — Assume complete failure 6 months out. Why did it fail? Prioritize by likelihood × impact. Mitigate top risks proactively.
5. **Systems Thinking** — How do parts interact? Map inputs/processes/outputs, identify feedback loops, find leverage points.
6. **Devil's Advocate** — Strongest counter-argument? For each major decision: write the best case against it. If it wins → change the decision. If original wins → document why.
7. **Constraint Analysis** — What's truly fixed vs assumed? Hard (platform limits, token constraints) vs Soft (conventions). Challenge soft constraints.
8. **Pareto (80/20)** — Which 20% of features deliver 80% of value? Focus on vital few. Defer the trivial many.
9. **Root Cause (5 Whys)** — Ask "why?" 5 times. Ensure skill addresses root cause, not symptoms.
10. **Comparative Analysis** — Score options across weighted criteria. Document justified selection.
11. **Opportunity Cost** — What are we giving up? Explicit trade-offs. Gain vs sacrifice. Why the trade-off is worth it.

---

## Application Protocol

Phase 1 — Rapid Scan (2-3 min each): note relevance (H/M/L) + one key insight per lens
Phase 2 — Deep Dive (10-15 min each): apply full protocol to High-relevance lenses, document insights, integrate into design
Phase 3 — Conflict Resolution: when lenses conflict, state each perspective, determine which dominates, document resolution and rationale
