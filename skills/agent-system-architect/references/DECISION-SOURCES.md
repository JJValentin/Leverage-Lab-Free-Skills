# Decision-layer source register

Reviewed September 19, 2026 for version 0.3.0. Only public primary sources were used. This adds to the retained [baseline register](SOURCES.md); the entire historical research/harness set was not re-reviewed. No live Jev account, paid standards text, model weights, user dataset or deployment was tested.

| ID | Source | Use and limit |
|---|---|---|
| D01 | [OMG: Decision Model and Notation overview](https://www.omg.org/dmn/) | Separating explicit business decisions from process/case models; not a DMN implementation or compliance claim. |
| D02 | [TypeSafe HTTP API](https://docs.typesafe.ai/api) | Request/response fields, endpoint, primitive shapes and error categories; documentation, not a live request. |
| D03 | [TypeSafe confidence](https://docs.typesafe.ai/confidence) | Distribution-derived confidence; distinct from actual correctness and absent for Noul. |
| D04 | [TypeSafe Noul](https://docs.typesafe.ai/primitives/noul) | Probability of a yes answer; domain calibration still required. |
| D05 | [TypeSafe Score](https://docs.typesafe.ai/primitives/score) | Descriptive zero-based levels, weighted index and full distributions; not exact measurements. |
| D06 | [Jev 1.13 known limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13) | Numeric/date limits, irrelevant state, adversarial content and non-guaranteed identities; applies to that model version. |
| D07 | [TypeSafe models](https://docs.typesafe.ai/models) | Versioned IDs, aliases and supported input; volatile, verify before live deployment. |
| D08 | [TypeSafe introduction](https://docs.typesafe.ai/introduction) and [state](https://docs.typesafe.ai/concepts/state) | Narrow questions and selected state; parallel evaluation does not imply independent evidence. |
| D09 | [TypeSafe quick start](https://docs.typesafe.ai/introduction/quickstart) | SDK/HTTP and vendor skill entrypoints; no installer executed, vendor skill not bundled. |
| D10 | [TypeSafe skill-suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion) | Pattern tested by vendor with pinned Hermes catalog/model/fixtures; not a current-install benchmark or guaranteed gain. |
| D11 | [Guo et al., On Calibration of Modern Neural Networks, ICML 2017](https://proceedings.mlr.press/v70/guo17a.html) | Public abstract reviewed; probability calibration is empirical, not implied by output shape. Does not test Jev. |
| D12 | [Microsoft HAX Design Library](https://www.microsoft.com/en-us/haxtoolkit/library/) | Understandable state, correction and user control; local interface still needs usability validation. |
| D13 | [Geifman and El-Yaniv, Selective Classification for Deep Neural Networks, 2017](https://arxiv.org/abs/1705.08500) | Public abstract reviewed; reject-option/risk–coverage rationale, not a guarantee for this workflow. |
| D14 | [OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | Downstream authority, least privilege, bounded actions. A decision model is not access control. |
| D15 | [Agent Skills specification](https://agentskills.io/specification) | Selective supporting references/scripts, not new runtime behavior from a folder. |
| D16 | [TypeSafe Jev introduction](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | Vendor positioning/performance claims distinguished from measured local benefit. No speed/cost claim used as an acceptance criterion. |

All file conventions, contracts, example gates, routing policies, rollout steps and code in this update are our proposed implementation. Typed output can be valid yet wrong. A metadata flag does not prove calibration, authentic approval or source truth.
