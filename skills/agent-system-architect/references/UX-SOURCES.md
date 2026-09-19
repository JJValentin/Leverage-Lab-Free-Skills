# Human-agent experience: sources and design traceability

Reviewed September 19, 2026. The exact interaction rules, templates, examples, scenario suite and release gates are our synthesis. No source validates this entire architecture. No full book or paywalled standard was read for this update; the consulted material is identified below. Existing organizational foundations remain in [SOURCES.md](SOURCES.md) and [operating-system.md](operating-system.md).

| ID | Primary source and material consulted | Contribution and limitation |
|---|---|---|
| U01 | Don Norman, *The Design of Everyday Things*, revised 2013: [author's synopsis and contents](https://jnd.org/books/the-design-of-everyday-things-revised-and-expanded-edition/) | Conceptual models, discoverability, feedback, constraints and recovery are explicit book themes. This is not a claim to have reviewed the full text or tested its application to agents. |
| U02 | Jakob Nielsen, [10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), author-maintained article; principles originated in 1994 | Visible state, user control, recognition, consistency and error recovery. Heuristics guide inspection; they do not establish measured usability. |
| U03 | Ben Shneiderman, [Eight Golden Rules](https://www.cs.umd.edu/users/ben/goldenrules.html), author summary associated with *Designing the User Interface* | Feedback, closure, reversal, control and manageable memory demands. Summary consulted, not the complete textbook. |
| U04 | Amershi and colleagues, [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/), CHI 2019 project overview; [Microsoft HAX library](https://www.microsoft.com/en-us/haxtoolkit/library/) | Guidance across initial use, regular use, failures and adaptation. We adopt relevant concerns without treating the guidelines as proof of this deployment's quality. |
| U05 | Eric Horvitz, [Principles of Mixed-Initiative User Interfaces](https://www.microsoft.com/en-us/research/publication/principles-mixed-initiative-user-interfaces/), CHI 1999 abstract; [Mixed-Initiative Interaction](https://www.microsoft.com/en-us/research/publication/mixed-initiative-interaction/), 1999 abstract | Coupling automation with user direction, rather than choosing total automation or total manual operation. Abstracts consulted; our ask/act policy is an adaptation. |
| U06 | Microsoft Research, [Magentic-UI: Towards Human-in-the-loop Agentic Systems](https://www.microsoft.com/en-us/research/publication/magentic-ui-report/), July 2025 technical-report overview | A research prototype explores co-planning, co-tasking, action guards and multiple evaluation methods. It motivates inspectable, steerable execution; it does not prove these patterns work in every harness. |
| U07 | Houde and colleagues, [Controlling AI Agent Participation in Group Conversations](https://research.ibm.com/publications/controlling-ai-agent-participation-in-group-conversations-a-human-centered-approach), IUI 2025, author-institution abstract | Two group-ideation studies motivate control of participation and avoidance of agent domination. Do not generalize to all business or personal conversations without testing. |
| U08 | W3C, [WCAG 2.2](https://www.w3.org/TR/WCAG22/), recommendation text | Keyboard access, focus, non-color cues, reflow, status messages and avoiding redundant entry inform interface checks. A chat policy alone is not WCAG conformance or an accessibility audit. |
| U09 | NASA, [Systems Engineering Handbook, fundamentals](https://www.nasa.gov/reference/2-0-fundamentals-of-systems-engineering/), public handbook chapter | Verification against requirements and validation of intended use are distinct. We keep technical completion separate from human acceptance and benefit. |
| U10 | [The Kanban Guide, May 2025](https://kanbanguides.org/the-kanban-guide/2025.5/), guide text | Explicit flow and work-in-progress management motivate treating human review as constrained capacity. No universal project-count limit is prescribed. |
| U11 | Donella Meadows, [Leverage Points](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/), author essay | Information flows, rules and feedback delays inform coordination and review cadence. Notification policies here are an adaptation, not an experimentally optimal schedule. |
| U12 | Center for Self-Determination Theory, [theory overview](https://selfdeterminationtheory.org/theory/) | Autonomy, competence and relatedness provide a motivational lens. Applying it to an agent experience is a hypothesis; it does not justify simulated attachment or engagement manipulation. |
| U13 | Becker and colleagues, [early-2025 developer-productivity study](https://arxiv.org/abs/2507.09089), paper abstract | In the studied experienced-developer setting, perceived benefit differed from measured completion time. This is historical, setting-specific evidence, not a claim about all current tools. |
| U14 | METR, [experiment-design update](https://metr.org/blog/2026-02-24-uplift-update/), February 24, 2026 report | Selection effects and concurrent-agent work complicate current productivity estimates. Measure local outcomes and user effort instead of recycling an old universal speed claim. |
| U15 | Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), January 9, 2026 engineering article | Evaluate end states and interaction quality, balance do/do-not cases, and calibrate model grading with people. Vendor engineering experience is not independent validation of our suite. |

## Connection to the original organizational model

Galbraith's alignment of strategy, structure, processes, rewards and people remains the reason to design experience together with responsibilities and evaluation, rather than adding a friendly persona afterward. Malone and Crowston's coordination framework remains the reason to define handoffs and dependencies instead of making the user coordinate agent messages. These are retained foundations, not newly replicated studies. NASA, Kanban and Meadows were revisited above to connect delivery quality, human capacity and feedback.

The human is part of the operating system, not a fallback endpoint with unlimited attention. Our translation is: a clear working agreement, bounded initiative, reviewable decisions, verified increments, recoverable state and an interface that makes the next useful action apparent.

## Coverage map

| Design concerns | Rules | Evidence anchors |
|---|---|---|
| First use, familiar terms, recognition and progressive detail | H01-H02, H11 | U01-U04 |
| Clarification, consent and appropriate initiative | H03-H04 | U04-U06 |
| Real execution, evidence and graceful recovery | H05-H06, H10 | U02-U03, U09, U15 |
| Attention, group participation and review capacity | H07-H08 | U04, U07, U10-U11 |
| Corrections, stop/resume and cautious adaptation | H09 | U04-U06 |
| Accessibility and agency-preserving motivation | H12-H13 | U08, U12 |
| Measured usefulness versus perceived helpfulness | H13-H14 | U09, U13-U15 |

Source dates above identify the material, not an assertion that each is the newest publication in its field. Public web pages can change. Old and new sources serve different purposes; recent publication alone does not make a practice better.
