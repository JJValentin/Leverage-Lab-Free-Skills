# Decision contracts and bounded judgment

Version 0.3.0. This is our operating convention, not an industry-standard schema. See [sources](DECISION-SOURCES.md), [provider details](providers/typesafe-jev.md) and [evaluation](decision-evaluation.md). None of the thresholds or fixtures in this package is validated for production.

## The design change

Add a decision function where a workflow repeatedly needs a narrow interpretation. Do not add an always-running “decision agent.” Keep three choices available: deterministic rules, bounded model judgment, and reasoning/human deliberation. They are alternatives and can be combined; they are not three compulsory serial calls.

For example, code establishes that a required asset is missing. A model might classify an ambiguous customer reply. A reasoning agent can propose how to resolve a conflict. The actual task owner or authorized workflow records the result. Permission enforcement remains outside the model.

The separation has an established management analogue: OMG DMN models decisions alongside process and case models. We borrow separate, inspectable decision logic and dependencies. This package does not implement DMN, BPMN, CMMN or FEEL. No new modeling tool is required. [D01]

## Which mechanism?

| Need | Start with | Do not substitute |
|---|---|---|
| Exact arithmetic, date comparison, duplicate ID, file/digest test | Code | Semantic model judgment |
| Authority, resource scope, action limit, current claim | Protected runtime and authoritative records | A model's opinion about permission |
| Repeated semantic classification with explicit options | Optional typed decision function | A permanent profile for every category |
| Unfamiliar problem, synthesis, prose, open-ended plan | Existing reasoning/generative agent | A chain of tiny classifications pretending to reason |
| Values, ambiguous consent or consequential tradeoff | Accountable human | A confidence threshold |
| Task already handled well by the current agent | Existing path | Mandatory extra infrastructure |

Decide based on measured benefit after including retrieval, provider latency, fallback, maintenance and user review effort. A cheaper individual call need not make the complete workflow cheaper. Keep the model count and context footprint small.

## Four distinct objects

**Contract:** a reusable, versioned question and its handling rules. **Observation:** a typed prediction about a specific input version. **Policy response:** deterministic selection of abstain, inspect, prepare or route. **Authority:** current permission to perform a particular action. A high prediction does not supply authority.

A human's recorded project decision is a fifth, separate thing. Do not rename approvals “model decisions” or overwrite human decisions with predictions.

## Contract checklist

Describe the outcome this decision supports and why a simpler rule is insufficient. Specify allowed scope, required/optional input fields, source references, revision and freshness limits. Define each output's semantics: a yes probability, a categorical distribution, or a position on an explicitly described ordinal scale. Include an unknown/no-match path for closed choices.

Record contract and policy versions, provider/model/adapter versions, input projection, cost/latency/retry bounds, fallback, privacy/egress, evaluation reference and owner. Keep examples and extensive evidence outside startup context. Use [the example contract](../assets/decision-contract.template.json) as a checklist, not as native harness configuration.

For a real deployment, give the prediction a receipt with the contract, input and rubric fingerprints, model identity, source revisions, creation/expiry, outcome and evaluation status. Use private scoped storage and a retention policy. Hashes can leak through dictionary guessing and are not anonymization. Authentication, immutable logs and encryption are not supplied by the example helper.

## Runtime sequence

1. Read authoritative state and check scope. Honor explicit user instructions and known deterministic outcomes before considering a model call.
2. Select the smallest approved input slice. Check prerequisites and freshness in code. Do not use a model to decide whether confidential data may leave its scope.
3. Call the approved provider only when enabled and useful. Batch questions only when each can be answered from the same authorized state. If question B needs A's answer, run a second stage or provide the required fact first.
4. Validate types, option coverage, finite ranges, probability sums and request/model binding. Retain unknown values as unknown. Structural validity does not prove semantic correctness.
5. Apply the versioned, locally evaluated gates and consistency checks. Low evidence, no-match, stale results or service failure select a fallback, not a forced answer. Separate questions are not independent evidence; do not multiply their probabilities as if they were.
6. Route to an existing handler or prepare a proposal. Recheck current permission, task claim, artifact version and approval immediately before any consequential action. Record actual results in the authoritative system.
7. Return a useful outcome, not an internal prediction trace. Store a compact private receipt where necessary and expire it with its source state.

These are implementation requirements for the host, not features created by reading this file. The bundled helper covers offline request projection, response validation and hypothetical gate checks only.

## Where each part lives

| Part | Location |
|---|---|
| General method for designing a decision | Architect or the domain skill |
| Decision question/options/rubric | Versioned contract near that workflow/skill |
| Local model choice, thresholds, privacy approval | Approved deployment configuration, outside shared examples |
| Current inputs and source revisions | Canonical project/task/source records |
| One prediction | Short-lived derived receipt, not durable personal memory |
| Provider API implementation | Narrow tool/module/adapter; not a new persona |
| Binding human approval | Existing authenticated approval system |
| Explanatory documentation | Selectively loaded references |

Keep multiple contracts in one directory only when useful; do not create an extra app or a contract for a one-time easy question. Register contract pointers in the existing system specification rather than duplicating all definitions.

## Memory and context safeguards

Classification can propose that a statement is a preference, task fact, procedure candidate or temporary context. It cannot confirm truth, resolve privacy, assign authority, or authorize a memory write. Split mixed statements first. The existing memory owner still applies source, effective-time, sensitivity, contradiction and supersession rules.

Required policy and access boundaries are not candidates for a relevance model to discard. Evidence ranking must preserve mandatory source reads and meaningful contradictions. Revalidate upstream state at resumption; a recorded “probably ready” is not evidence that a task is currently ready.

Where the host caches decisions, key by scope, contract/policy version, model/adapter version, selected inputs/source revisions and question/option content. Invalidate on changes and respect expiry. Do not reuse a decision across users or clients. No cache is implemented by the offline helper.

## Project Hub integration

Hub stays a projection of work. Do not change `state`, `task_snapshot`, `owner`, question answers or completion digests based solely on a model score. Put tentative interpretations in a clearly labeled proposal to the current task owner. After source verification, update the native record first and the hub second.

For known missing approvals, failed checks or artifact changes, use the existing deterministic checks. Do not ask Jev whether an approval is “probably sufficient.” Do not turn a project priority score into a claim that this person should work harder or that their productivity is inadequate.

## Usability and failure behavior

Use the normal interface and an optional suggestion, not a probability dashboard. Explain uncertainty in ordinary terms only when it matters. The user can correct routing and decline suggestions; don't rerun a classifier until it overrules the correction. Mandatory system/security constraints still apply.

Default service failure to the existing working path, when that path is permitted. If privacy forbids another provider, remain local or ask the human for the necessary decision. Do not silently send the same private input to a second company. A low-confidence internal choice is not automatically a user interruption.

Define a whole-interaction deadline, bounded model calls and a circuit breaker in the host. Avoid oscillating routes: once a handler is working, reroute only on new material evidence or user direction. Group nonblocking review questions; surface real blockers with one affected outcome and a useful recommendation. Evaluate underuse and unnecessary escalation as well as wrong autonomous routes. [D12]

## Default rollout

Off → offline fixtures → authorized shadow evaluation → advisory pilot → bounded routing only after acceptance. “Shadow” still costs money and transmits data if a real provider is called; it only means the prediction does not control the workflow. Separate egress approval from routing approval.

The shipped contracts are shadow-only with unset gates and unvalidated evaluation records. Installing Architect leaves providers off. No Jev key, network call, routing hook or authority expansion is performed.
