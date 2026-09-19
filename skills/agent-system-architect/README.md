# Agent System Architect 0.4

Design or improve a single-agent or multi-agent system that performs useful work and is understandable, steerable and recoverable. This version adds explicit human-agent collaboration and response behavior to the existing operating model, context/memory design, harness adapters, optional Jev decisions and Project Hub integration.

## Start here

Read [SKILL.md](SKILL.md). During setup, apply the [collaboration rules](references/human-agent-collaboration.md) and select only relevant [response patterns](references/response-patterns.md). The [experience evaluation](references/experience-evaluation.md) and [source register](references/UX-SOURCES.md) separate proposed practices from demonstrated results.

Ask your agent:

> Read Agent System Architect. Audit my current system read-only, including how it communicates and executes. Preserve my identity, memory provider, task coordinator, Project Hub and permissions. Identify one interaction that causes avoidable effort. Propose the smallest reversible change, map the compact collaboration policy to the actual instruction scope, and test a routine success, correction, interruption and failure. Do not install new agents, providers, schedules or permissions as a side effect.

## From design to everyday behavior

The architecture skill is invoked for setup and audit. It is not the everyday assistant personality. After approval, merge the relevant [compact collaboration policy](assets/COLLABORATION.template.md) into the harness's existing effective instruction scope, preserving local rules and user preferences. Verify the active version and loading in a fresh/reloaded session. Keep detailed research and tests on demand, not in every prompt.

The [experience contract](assets/experience-contract.template.json) is an optional design record. Use existing system fields where possible. The [40 scenarios](assets/experience-scenarios.json) are executable test specifications once adapted to an actual harness, not evidence that any model passed them. Record observed results with the [run template](assets/experience-run.template.json).

## Check the package locally

Python 3.10+; standard library only. From this skill directory:

```sh
python3 -B -m unittest discover -s tests -p 'test_experience.py' -v
python3 scripts/decision_tools.py demo
```

These check package contracts and fictional fixtures. They do not call Jev, exercise native tools, test live conversation quality or establish accessibility conformance. See [VALIDATION.md](VALIDATION.md).

## Install or upgrade

Resolve the actual active skill root. Compare the existing copy, preserve local customizations, back up appropriately and stage replacement of only this skill. Do not leave duplicate discoverable versions. No Project Hub schema migration is required. Verify effective skill loading and separately validate any approved instruction-policy change.

No live API transport, task coordinator, permission engine, scheduler, interface controls or memory service is created by this package. Decisions remain optional and advisory; the existing authorized runtime owns execution. No credentials or private project data belong in the shared skill.
