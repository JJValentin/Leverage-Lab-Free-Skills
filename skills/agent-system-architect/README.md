# Agent System Architect 0.3

Design, audit, or improve single-agent and multi-agent systems without replacing what already works. Version 0.3 adds optional bounded decision contracts and a TypeSafe Jev adapter while keeping permissions, task state, memory, and human approvals authoritative outside the model.

Start with `SKILL.md`. `references/` contains the operating model, harness adapters, decision-layer design, evaluation guidance, Project Hub integration, and sources. `assets/` contains portable templates and shadow-mode examples. `scripts/decision_tools.py` is an offline request/receipt validator; it performs no network calls and grants no authority.

This repository copy contains the deployable skill, templates, references, and offline helper. See `VALIDATION.md` for what was tested in the development package and what remains unverified. No live Jev connection, credentials, routing hook, memory migration, Project Hub state migration, or permission change is performed by installing this skill.
