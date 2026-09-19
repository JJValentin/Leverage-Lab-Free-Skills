# Optional provider: TypeSafe Jev

Documentation reviewed September 19, 2026. Jev is optional. This adapter is guidance plus an offline wire-format implementation, not a live harness integration or an endorsement of vendor performance claims. Sources [D02–D10] are listed in [DECISION-SOURCES.md](../DECISION-SOURCES.md).

## Verified API shape

The current HTTP interface is `POST https://api.typesafe.ai/v1/systemone` with Bearer authentication and a JSON object containing `state`, `model`, and `questions`. Each question has `type`, `instructions`, and type-specific `criteria`. Question IDs associate responses but are not part of inference, so put the actual question in `instructions`. [D02]

| Architect concept | Jev request | Response semantics |
|---|---|---|
| Binary probability | `type: noul`; explicit yes/no instructions | `noul`: probability of yes; no separate confidence |
| Categorical distribution | `type: choice`; described option map | `choice`, `probabilities`, `confidence` |
| Ordinal judgment | `type: score`; ordered descriptive levels | `score`, `probabilities`, `legend`, `confidence` |

`confidence` describes distribution concentration, not an independently verified probability the answer is correct. A Noul near zero can be a strong no, not a failed answer. Keep probability, provider confidence and locally observed error separate. [D03, D04]

Score is the probability-weighted index of its descriptive levels, starting at zero, and can be fractional. It is not a 1–5 integer, completion percentage, measurement of money, or confidence of correctness. Different distributions can have the same mean. Inspect the distribution when the tail matters. [D05]

## Fit and limits

Use narrow semantic judgments with described boundary cases. Leave exact arithmetic, counts and date comparisons in code. Generate prose and novel plans with a generative agent. Treat state as potentially adversarial: closed-set output does not prevent a malicious input from steering the model to a harmful valid option. [D06]

The current models page identifies `jev-1.13.0` and describes text/JSON inputs. Confirm supported models and limits when installing. Prefer a pinned model for evaluated gates; an alias may change underneath the deployment. Do not infer account access, privacy terms or measured latency from this documentation check. [D07]

Questions sharing state can be evaluated in one call, but a question cannot see another answer from that call. Parallel evaluation is not statistical independence. Do not treat two variants of a question as two independent votes. [D08]

## Prepare and inspect without an account

Run from the installed/extracted Architect directory:

```sh
python3 scripts/decision_tools.py validate assets/examples/route-request.contract.json
python3 scripts/decision_tools.py request \
  assets/examples/route-request.contract.json \
  assets/examples/route-request.state.json \
  --now 2026-09-19T12:00:00Z
python3 scripts/decision_tools.py demo
```

The request command emits a preview wrapper: a fingerprint and a `request` property containing the wire body. It makes no network call. It sends only allowlisted fields into `request.state`; metadata/source bindings remain in the local fingerprint. Top-level allowlisting is not secret detection: inspect nested contents before authorizing transmission. Use fictional fixtures first.

The demo validates a synthetic receipt; its probabilities are hand-authored, not a Jev result. Its thresholds are unset, so the result remains shadow-only and uncalibrated. `--now` is solely for replaying the dated fixture; production code must use a trusted current clock and newly observed source state.

## An authorized live pilot

First review data egress, provider terms, API availability and measured need. Obtain credentials through the existing secret manager/environment, never memory or SKILL.md. Use TypeSafe's documented HTTP interface or maintained SDK; inspect and pin the SDK used. No package is installed by Architect. The vendor also publishes a `typesafe-ai` skill, which can supply detailed implementation help after review; do not treat it as policy authority or install duplicate versions. [D09]

Implement a narrow, read-only decision tool. The host should call `prepare_request`, transmit only its `request` body, capture the response under that same fingerprint, and use `assess_receipt` before interpreting it. Do not attach a fingerprint to an arbitrary result after the fact and call it verified. A fingerprint prevents accidental mismatching; it is not a signature or proof of service origin.

A receiver envelope has `provider`, `request_fingerprint`, `received_at`, and `response`. `response` is the unmodified JSON returned by Jev, including its resolved model. The helper validates this specific wire version. Other providers need an explicit adapter for their semantics; their confidence fields are not interchangeable. No fallback API calls are bundled.

The host owns transport timeouts, cancellation, rate limits, bounded retries, provider egress, billing and logging. The decision API reads are not permissions to execute later tools. Avoid logging full state, private documents, API keys or server error bodies. The offline helper has no circuit breaker or live API client because it never calls a service.

## Hermes pilot: skill suggestions, not task ownership

TypeSafe publishes a skill-suggestion cookbook using a pinned Hermes catalog. It proposes a shortlist followed by a closer fit check, with the option to suggest nothing. Its reported results are vendor experiments on its fixture and model versions, not a benchmark of this user's installation. [D10]

Our adaptation: keep explicit skill requests and mandatory skill-loading rules; shortlist only approved available skills; evaluate absolute fit as well as relative choice; allow `none`; load the chosen skill normally; let the agent reject a poor suggestion. Do not download unreviewed skills, modify system prompts from arbitrary result text, or bypass native discovery. Code maps an allowlisted ID to a known handler. Never use a model-produced ID as a shell fragment.

Start offline or shadow-only on repeated ambiguous skill choices. Compare against simply improving skill descriptions or using the existing model; keep Jev disabled if it adds no useful benefit.

## Promotion conditions

Follow [decision-evaluation.md](../decision-evaluation.md). Evaluate representative and adversarial inputs, no-match cases, wrong confident predictions, calibration, fallback and total interaction effort. Pin question/options/model changes and re-test them together. No universal cutoff, guaranteed correctness, speed multiplier or reduction in token cost is assumed by this package.
