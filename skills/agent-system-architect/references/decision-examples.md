# Four bounded decision examples

All examples are templates and fixtures. They have no tuned gates, no live provider results and no automatic writes. Choose one useful example; do not install four new services. The JSON format belongs to this kit, not to Hermes or TypeSafe.

## 1. Request routing

[Contract](../assets/examples/route-request.contract.json): classify the requested work as direct answer, existing task, project work, recurring-process work or unknown. A recurring-process classification does not authorize a schedule. An existing explicit task ID can bypass this classification.

The outcome is a suggested handler, not a task created by the classifier. Keep a reasoning agent as fallback and ask the user only for an unresolved decision that matters. Use the [fictional state](../assets/examples/route-request.state.json) and run `python3 scripts/decision_tools.py demo` for an offline structural check.

## 2. Information placement

[Contract](../assets/examples/placement-candidate.contract.json): evaluate one already-split statement as a memory candidate, project fact, task-state candidate, reusable-procedure candidate, session-only material or unknown. Distinguish a temporary constraint from a durable preference.

The memory/task/project owner then checks sources, scope, effective dates, duplication and consent. Do not save inferred preferences, create a skill, or update a task simply because one category scored highly. A bundle containing multiple kinds of information must be split before classification; otherwise choose unknown.

## 3. Project Hub attention

[Contract](../assets/examples/hub-attention.contract.json): identify a possible need for human interpretation in an ambiguous status message. Ask a binary question about whether an unresolved choice is expressed, and an ordinal question about described impact.

This does not determine task state, urgency from dates, artifact integrity or approval validity. Those come from code and canonical records. Record a proposal through the task owner only after checking the source; preserve the existing hub schema and reading experience. The helper never calls `hub.py set`, `ask` or `answer`.

## 4. Skill fit

[Contract](../assets/examples/skill-fit.contract.json): compare a small, trusted shortlist that includes Architect and Project Hub, plus none/unknown. The full deployment should derive candidates from the actual permitted installed roster, not hard-code this example. Evaluate absolute fit as a separate binary question so “best of these” does not imply “any of these is appropriate.”

Respect explicit user skill selection, mandatory skill requirements and installed-skill permissions. Do not use predicted IDs as paths or commands. Resolve them through a code-owned allowlist and load the actual skill. This borrows a pattern from TypeSafe's Hermes-catalog cookbook; no improvement has been measured on the user's setup. [D10 in DECISION-SOURCES.md]

## Adapting to another provider

Keep the question and handling contract independent of the client implementation. Map each provider's types, absence values, probability semantics and version identities explicitly. A regular LLM can perform the same bounded task, but a confidence number it writes is not automatically calibrated. Compare it fairly with the existing agent and with ordinary rules before adding Jev.
