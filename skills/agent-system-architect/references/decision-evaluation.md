# Evaluating bounded decisions

This is a deployment plan, not evidence that the included classifier works. The local helper tests only mechanics. See [DECISION-SOURCES.md](DECISION-SOURCES.md) for calibration, selective prediction, model and usability sources.

## Begin with the current baseline

Record the actual repetitive decision, its input, downstream consequence and failure cost. Compare existing rules/current-agent behavior with the candidate. Include retrieval, context size, provider requests, fallbacks, wall-clock delay, maintenance and human review effort. No deployment is required when the existing approach is sufficient.

Create a representative, consented dataset with accountable labels or adjudicated acceptable outcomes. Include ordinary successes, no-match requests, mixed intents, missing information, corrections, stale records, unsupported languages and adversarial text. Split by user/project/time as appropriate to avoid near-duplicate leakage. Do not use the same examples to tune and claim final accuracy. Synthetic fixtures check plumbing; they are not a production calibration set.

## Distinguish three quantities

**Predicted probability:** the model's estimate for a proposition/category. **Provider confidence:** a provider-specific statistic, which may just measure distribution shape. **Measured performance:** correctness/cost on labeled deployment-relevant cases. None grants permission.

Calibration research distinguishes probability estimates from empirical correctness; selective prediction studies trading coverage for error by rejecting uncertain cases. Those results motivate measurement and abstention, not an imported guarantee for Jev or this system. [D11, D13]

## Pick gates from consequences, not attractive round numbers

Use separate costs for false positives and false negatives. Select candidate cutoffs on development data, then estimate results on held-out cases and important slices. Report the number accepted and rejected, error among accepted cases, total error, coverage, and review workload. Include uncertainty intervals and sample counts; zero observed errors in a small sample is not proof of zero risk.

For a binary question use both a yes threshold and a no threshold with an abstention band. For a categorical question consider selected probability, separation from alternatives, unknown/no-match and any validated provider statistic. For an ordinal score test the distribution and rubric, not just a rounded mean. Gates tuned on one question, model, primitive or label set do not transfer automatically.

A simple cost calculation, where class probabilities are trustworthy and costs are explicit, compares expected loss of each available response against the cost of review. Human values and rights are not collapsed into that calculation. For protected actions the permission/approval check applies regardless of expected utility.

For probabilistic classifiers report calibration plots and Brier score or log loss, with class-appropriate interpretation. Inspect class/scope-specific errors and drift; an aggregate metric can hide dangerous cases. For ordinal outputs evaluate the actual rubric and tail cases as well as mean error. Evaluate the workflow outcome, not only agreement between two models.

The example contracts deliberately leave all gates `null` and evaluation `not_run`. A field saying `validated` plus a reference is a record, not proof that anyone validated it. The helper never authenticates that claim and never authorizes an action.

## Required failure cases

| Case | Required behavior |
|---|---|
| Small/direct request | Bypass extra routing where unnecessary |
| Explicit user-selected skill/route | Honor it if permitted; model suggestion does not veto |
| No suitable option | Unknown/none or existing-agent fallback, not forced assignment |
| Missing input or stale source | Refresh or abstain before model-dependent routing |
| Input exceeds selected budget | Narrow explicitly; do not truncate away mandatory context |
| Wrong answer with high confidence | Recorded as an error; not excused by confidence |
| Noul near zero | Interpret as probability of no, not missing confidence |
| Diffuse or tied distribution | Abstain according to evaluated policy |
| Score with two distant peaks | Do not treat a middle mean as certain middle severity |
| Incomplete keys, NaN, wrong sum/type/model | Reject, no silent normalization |
| Result from old contract/source revision | Reject or recompute, even if label appears plausible |
| Malicious text requests privileged handling | No authority or write capability gained |
| Task/source disagrees with a prediction | Canonical source wins; reconcile before changes |
| Provider timeout/outage | Bounded fallback, no repeated user interruptions |
| Another provider is not approved for this scope | Do not transmit data to it as a convenience fallback |
| Low confidence across many cases | Bound review workload; revise/reroute or disable, not notification floods |
| User corrects an interpretation | Correct the relevant scope; do not silently promote to permanent memory |
| Model, rubric or skill roster changes | Re-evaluate and invalidate affected receipts/caches |

Offline helper tests cover structural cases only. Provider susceptibility, semantic accuracy, human experience, timeouts and native authorization require separate live or controlled integration tests.

## Staged rollout and rollback

**Off:** unchanged workflow, no provider calls. **Offline:** fictional/replayed fixtures. **Shadow:** authorized candidate calls recorded separately, existing path still decides. **Advisory:** optional suggestion with easy correction. **Bounded routing:** only approved handlers after held-out acceptance and verified runtime controls.

Use a scoped feature flag, owner, whole-interaction deadline and safe fallback. Keep budgets for calls and user review. Monitor errors, false escalations, missing escalations, p50/p95 latency, rework and spend. Test disabling the provider mid-work without losing the task. Roll back to the existing route and retain necessary private receipts; do not replay external actions.

Have the actual user test orientation, predictability and recovery. Raw confidence displays are optional inspection details, not the main interface. “No interruption” is not success if an important blocker was hidden; “asked the user” is not success if the system asks them to classify everything. [D12]
