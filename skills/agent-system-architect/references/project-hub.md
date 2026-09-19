# Optional Project Hub adapter

Project Hub is a reader-facing projection of project work, not the commitment ledger. Agent System Architect designs/audits the sources, authority, context, topology, and experience; the native task coordinator owns commitments, claims, dependencies, and execution state; Project Hub presents artifacts, review metadata, sourced decisions, and a compact resumption view.

When a Hub exists, inspect its version/schema, canonical task source, artifact pointers, writer topology, and actual reader experience before changing it. Preserve the existing hub when it works. Do not create another dashboard.

On resumption: read compact hub status, identify the relevant item, re-read the canonical task/source and necessary artifact, execute under current permissions, update the authoritative task/source first, then update the Hub presentation. A hub owner label is not a task claim; a hub answer is not execution permission; generated HTML is not source truth.

Keep large work artifacts outside hub state. For multiple writers, use the Hub's supported local revision/locking behavior only within its tested scope; cross-host coordination needs one designated writer or a verified transactional coordinator.

For v0.3 decision assistance, model predictions may suggest attention or routing but must not mutate Hub artifact status, task snapshots, owner, approvals, or completion evidence directly. Known blockers, dates, claims, digests, and approvals remain deterministic/canonical checks.
