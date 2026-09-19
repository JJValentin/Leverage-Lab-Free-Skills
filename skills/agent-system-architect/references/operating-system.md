# Portable operating model

This is a research-informed synthesis, not a certified standard or universal optimum. Source references are in SOURCES.md. Separate what the organization needs from what a particular harness implements.

## Foundations translated into mechanisms

Organizational design is broader than reporting lines: align strategy, responsibilities, work processes, capabilities and evaluation. Coordination theory addresses dependencies, shared resources, timing and compatible outputs. Systems engineering distinguishes verification against requirements from validation of the person's actual need. Flow management makes capacity and work in progress explicit. Systems thinking adds information flows, feedback delays and whole-system outcomes. Human-centered design adds understandable state, correction and user control.

The proposed implementation has four parts: an operating specification; a harness adapter; actual execution/control mechanisms; and a human interface. A skill guides their design but cannot substitute for a task store, scheduler or permission service.

Maintain three maps. **Authority:** who may decide or act? **Dependencies:** what must happen first, and what resources conflict? **Information:** which record is authoritative, who owns it and who may change it? Do not force all three into one manager-to-worker org chart.

Cover five management functions: purpose/policy, sensing/adaptation, operational control, coordination and execution. A person, a database constraint, a routine, deterministic code or an agent may cover a function. A small deployment need not have five agents or five services.

## Outcome and work structure

Overall intent defines what matters and what must be protected. Areas are ongoing responsibilities. Projects are finite changes with completion conditions. Processes are repeatable flows. Tasks are commitments with an owner and acceptance condition. Actions are individual execution steps. These are logical distinctions, not six required applications.

Prefer existing records: a CRM can own customer data; a calendar owns events; a native task board owns commitments; a project record owns scope and decisions. Project Hub can display the current work without becoming another master. A small finite project can be one existing record with a checklist.

A work packet needs: identity; accountable human; execution owner; desired outcome/non-goals; inputs and authoritative sources; dependencies; permitted actions; acceptance evidence; effort and spending limits; exception conditions; next action; and relevant artifact/receipt pointers. Do not demand a giant form for a trivial task.

Use native statuses where possible. The conceptual lifecycle is captured, ready, running, waiting/needs-review, done, with explicit failed/cancelled outcomes. A retry is another attempt under the same work identity. Completion requires acceptance evidence, not an agent's closing message. Native claims, leases and stale-worker checks belong to the coordinator.

## Agent, skill, profile, tool or workflow?

A decision contract describes a reusable bounded judgment; a decision receipt is one dated, derived prediction; a human decision record preserves an actual choice or approval. These are different objects. A role is durable responsibility; a skill is a reusable method; a worker is a temporary executor; a model is a replaceable capability; a workflow coordinates transitions; a profile is a persistent runtime/application boundary with harness-specific semantics.

Predictable rules belong in automation. Narrow semantic judgments can use a typed decision function. Open-ended synthesis, planning or variable execution can use one agent. Jev is one optional implementation of the judgment function, not a required layer or new agent. A single existing agent remains appropriate when decomposition adds more overhead than benefit. A separable question or artifact can justify a temporary worker. A persistent customer-facing service, private domain or independent queue can justify another profile. Expertise or a different writing voice alone does not.

Before delegating, specify input, scope, output, acceptance evidence, tool rights, write ownership, maximum effort and escalation. Use specialist context isolation or parallelism only when it improves measured quality, latency or cost. Do not create an executive hierarchy to make the system look organized.

## Bounded decisions inside the workflow

Separate the question, the model's prediction, the deterministic response to that prediction, and the authority to execute. Logical path: authorized current inputs → optional bounded judgment → validation/abstention → an existing handler → independent action checks → verified outcome. The path can bypass judgment entirely; a human may resolve a case directly.

This extends the original organizational approach rather than replacing it. OMG's Decision Model and Notation explicitly separates business decisions from complementary process/case models. Our contracts borrow that separation but are not DMN files, FEEL programs or a conformance implementation. See [decision-layer.md](decision-layer.md) and [decision sources](DECISION-SOURCES.md).

## Placement and scope

Decision contracts belong with the versioned workflow or reusable method; deployment scope and thresholds belong in the local approved configuration; predictions belong in time-bounded operational receipts. Do not put private inputs or receipts in a published skill. Instructions contain short rules that apply at their scope. Skills contain reusable methods and selective references. Stable facts/preferences belong in scoped memory. Project purpose and decisions belong in the project record. Work state, approvals, attempts and action receipts belong in the operational store. Large evidence belongs in retrieval/archive. Schedules and controls belong in real runtime mechanisms.

Mixed example: 'Use a friendly voice; send the report Friday; this client wants one page; this week is waiting for figures; follow this procedure.' Split voice into the appropriate preference, Friday into a schedule, client format into scoped memory, waiting status into the task record, and the method into a skill. None of these alone creates authorization to send.

Promote a repeatable, evaluated method into a skill after removing private case data. Promote a durable sourced fact into memory with scope and correction rules. Promote only truly cross-cutting constraints into startup instructions. Demote long manuals to references and completed history to archives. Retirement needs an owner and a retention policy, not endless accumulation.

## Context and memory

Treat scope (user, organization/client, area, project, task, session), loading (hot, warm, cold), and authority (canonical, derivative, tentative) independently. A durable project decision can be retrieved only when relevant. A current task state is volatile but important now. Global storage does not mean every agent should read everything.

Assemble applicable policy, relevant constraints, current task contract, project brief, method and necessary evidence. Known IDs and authoritative pointers come before broad semantic retrieval when available. Inspect relevant sources rather than assuming a short search snippet is complete. Reserve room for tool results and output; narrow the assignment instead of dropping mandatory constraints.

A context budget is measured, not a universal percentage. Monitor loaded tokens, truncation, retrieval usefulness, latency and actual task results. Do not mistake the number of files on disk for the effective prompt. Keep large artifacts outside `hub.json`; `status` is a routing brief and `show` is a targeted record, not proof of current external state.

Memory writes should check source, scope, sensitivity, duplication and contradiction before committing. Important records benefit from subject, source, observation/effective dates, owner, verification and supersession/expiry. Simple low-risk preferences can stay concise. A newer timestamp does not necessarily override a stronger source or a fact about a different period.

For correction, distinguish this response, this project and an enduring preference. Preserve an explicit user's correction and retire stale derivatives. Keep unresolved conflicts visible; do not act on an arbitrary choice between contradictory sources. Enforce privacy before retrieval rather than relying only on a model to omit private details afterward.

For decision-assisted work, persist only the relevant contract/model/version and receipt pointer; a fresh source revision invalidates the old prediction. Do not load all contracts or model distributions into future sessions. A fingerprint binds data but is not encryption, a signature or proof of truth.

At handoff persist identity, current state, completed actions, artifact locations, decisions, source revisions, outstanding uncertainty and next action. Preserve evidence and outcomes, not hidden reasoning. Revalidate the canonical record before resuming. Conversation compaction alone does not establish durable operational continuity.

## Authority and reliability

Describe authority in the specification and enforce it downstream. Limit tools and data to the task; make consequential approvals bind to actual resource, recipient, amount, purpose, artifact/version, duration and usage limits. Test alternative routes such as shell access. A child cannot obtain authority its parent was not permitted to delegate.

Profiles may separate application state while sharing the OS account, filesystem or credentials. Verify the real boundary. An instruction, owner label, remembered preference or displayed answer is not authentication or authorization.

A timeout does not prove an external action failed. Use provider idempotency where supported, otherwise reconcile actual source records or escalate. Do not repeat a send, payment or calendar change based solely on an absent response. Avoid universal exactly-once claims.

Local atomic writes, work claiming, lease expiry, budget enforcement, action idempotency and approval checks solve different problems. Choose the actual mechanism required. Project Hub's cooperative file lock only covers compliant local state writers; multi-host coordination requires a verified service or a designated single writer.

## Experience and improvement

Provide one coherent front door. Default to current situation, a useful result/next action and any decision needed. Make evidence inspectable without dumping operational logs into every answer. Show what was prepared versus executed, and what is blocked versus unknown. Batch nonblocking questions while promptly surfacing consequential blockers.

Use progressive disclosure. Project Hub's overview is for orientation and decisions; reading view is for consuming the actual work. Do not layer old plans above completed drafts. Do not equate word count, messages, token output or filled calendars with value. Review queues and the person's attention are constrained capacity.

Offer correction, pause, cancellation, resumption and reduced proactivity only where implemented. Keep autonomy and notification preferences controllable. Reward through visible useful completion, less repeated explanation and easy recovery rather than obligatory streaks, inflated praise or artificial urgency.

Check execution promptly, but reconsider strategy on a cadence that matches feedback delays. One missed reply is not reason to rewrite the plan. Improvement is observed failure, diagnosis, candidate change, evaluation, approved rollout and monitored result. Agents may propose changes; they cannot expand goals or permissions through a retrospective.
