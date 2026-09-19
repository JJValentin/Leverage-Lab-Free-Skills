# Rollout and evaluation

Separate package correctness from helpful autonomous behavior. These procedures are proposed operating practices; the thresholds must be selected for the deployment.

## Read-only audit output

Report one observed problem, its evidence and impact; the current source-of-truth map; capabilities marked verified/documented/unsupported/unknown; what should remain unchanged; the smallest proposed change; and tests/rollback. Do not produce a ten-agent architecture when the actual problem is a stale task brief.

Resolve important context from available records rather than forcing the user through a questionnaire. Ask for a decision only when it changes safety or scope. Do not read unrelated personal information or secret contents to make an inventory look complete.

## Change plan

Identify exact source and destination, existing versions/revisions, authorized writes, preserved customizations, expected benefit, required controls, staging location, backup handling, test cases, acceptance criteria and rollback. Call out any irreversible external effect separately. A JSON template is a checklist, not native harness configuration.

Stage first; validate syntax; verify effective loaded behavior; run fixtures; pilot one process; then expand deliberately. Use supported native APIs. Never edit a task database directly. A missing permission/scheduler/memory capability is a gap to handle, not a feature to assert in prose.

For a Project Hub migration, preserve canonical files and native commitments, preview schema conversion, retain a private state backup, revalidate legacy completion evidence, inspect the rendered artifacts and test resumption. Do not treat reading mode as privacy redaction. Roll back code and matching state together after reconciling intervening changes.

## Evaluation levels

1. **Static:** links, frontmatter, syntax, declared dependencies, no private state in the package.
2. **Deterministic helper:** state validation, concurrency, safe failure, rendering, migration, source snapshots, installation refusal paths.
3. **Live harness:** actual skill loading, effective context, tools/permissions, native coordinator interaction, real resumption and scope isolation.
4. **External integration:** source permissions, stale/retry behavior, unknown outcomes, provenance and approval version binding.
5. **User experience:** can the intended person understand, steer, correct and resume without unnecessary burden?

Passing level 1 or 2 does not prove levels 3-5. List what ran, environment, outcome and what did not run. Do not turn a vendor research claim into a local acceptance result.

## Required behavioral scenarios

| Scenario | Expected result |
|---|---|
| Small ordinary request | Answer directly; no project/profile ceremony |
| Existing system works | Preserve it; no parallel task/memory system |
| Fresh session resumes work | Find current task/source, artifact and next action without a transcript dump |
| User corrects a preference | Correct the right scope; supersede stale derivatives |
| Source conflicts with a summary | Reconcile at the source; do not overwrite authority with a nicer summary |
| Source unavailable or stale | Show dated/unknown state; avoid consequential action based on it |
| Missing or changed artifact | Fail visibly; do not report a successful empty/obsolete deliverable |
| Uncertain send outcome | Reconcile receipt before any retry |
| Revoked/stale approval | Reject external execution; a hub answer is not permission |
| Another worker owns the task | Respect native claim/lease; do not use owner text as a claim |
| Two local hub writers | Preserve both nonconflicting updates or reject a stale proposal |
| Cross-host writers | Require verified coordination or one designated writer |
| User pauses or cancels | Use the real mechanism; state what is already irreversible |
| Nonblocking questions accumulate | Batch; do not interrupt repeatedly |
| A meaningful blocker appears | Escalate through the agreed channel with the affected work and recommendation |
| Reading mode | Actual work is readable; plans and operational chatter do not lead |
| Shared/public destination | Review audience and permissions; no private notes/state leaked |
| Live upgrade fails | Preserve the previous useful output and follow the documented rollback/reconciliation path |

## Measures

Track accepted outcomes, error/rework rate, time to useful result, human review effort, interruptions, repeated explanation, recovery success, latency and operating cost. Include perceived clarity/control when evaluating actual users. Avoid rewarding word count, number of agent messages, checked boxes or a fully booked calendar.

Choose capacity limits based on actual work and human review bottlenecks. There is no universal best number of active projects, agents or prompt tokens. Start small and adjust from evidence. Never self-expand permissions or scope because a retrospective claims success.

## Handover

State what changed, what stayed, what was verified, remaining limits, exact use/resume/correction instructions, how to pause/revert and one recommended next step. Verify a commit/PR or installed version before claiming publication or installation. A generated report is not a live configured system.

## Optional decision layer

Apply [decision-evaluation.md](decision-evaluation.md) only where a bounded model judgment is proposed. Audit existing logic first; register a versioned contract; remain off or shadow-only until egress, semantic performance and routing behavior are verified. Keep native task/memory/approval owners.

The offline helper and synthetic fixtures test parsing, probability semantics, freshness, source/version fingerprints and hypothetical gates. They cannot establish Jev accuracy, calibration, effective permissions, lower cost, live availability or a better experience. Retain the existing route as rollback.
