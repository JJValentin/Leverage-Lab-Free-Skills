# Leverage Lab Free Skills

Three Claude Code skills from my personal setup. Install them and they work immediately.

These are the same skills I use daily to run my business. No fluff, no theory — production-tested tools that make Claude Code dramatically more useful.

## What's Inside

### 🧠 Structured Reasoning
**What it does:** Forces systematic thinking on complex decisions. Instead of getting surface-level "here are some options" responses, it runs through frameworks — first principles, tradeoff analysis, assumption testing, multi-perspective validation.

**When to use it:** Business strategy, offer positioning, pricing decisions, architecture choices — anything where the obvious answer might be wrong.

**Highlights:**
- Three modes: Light (quick decisions), Deep (irreversible decisions), Consensus (highest-stakes)
- Built on an 8-phase Engineering Flywheel framework
- Auto-routes by decision reversibility and complexity
- Optional "thinker" validation for Type 1 decisions

### 🔍 Deep Search
**What it does:** Multi-platform research across YouTube, Reddit, HackerNews, X/Twitter, and SearXNG — in parallel. Not just "Google it" — scored, deduplicated, cross-source linked results.

**When to use it:** Market research, competitive analysis, content topic discovery, trend analysis, answering "what are people actually saying about X?"

**Highlights:**
- 5 platforms searched simultaneously
- Auto-selects platforms based on query type (product, concept, opinion, how-to, comparison, news)
- Three-axis scoring: relevance (45%), recency (25%), engagement (30%)
- Cross-source convergence detection (same topic across multiple platforms = stronger signal)
- Each platform also usable standalone
- Zero pip dependencies — uses only standard library + system tools

### 🔨 Skill Forge
**What it does:** Creates new skills or optimizes existing ones. This is the skill that builds skills. Feed it what you want to automate, and it generates a structured SKILL.md with triggers, steps, context, and constraints.

**When to use it:** When you find yourself explaining the same process to Claude repeatedly. Turn any repeated workflow into a reliable, reusable skill.

**Highlights:**
- CREATE mode (new skills) and OPTIMIZE mode (improve existing)
- 11 thinking lenses for deep analysis
- Quality gates: timelessness scoring, size limits, trigger requirements
- 3-agent synthesis panel for validation
- Full reference docs included for the methodology

## Installation

### Claude Code (native)

Drop the skill folders into your project or a shared skills directory. Claude Code will pick them up when you reference them.

```
your-project/
├── skills/
│   ├── structured-reasoning/
│   │   └── SKILL.md
│   ├── deep-search/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── skill-forge/
│       ├── SKILL.md
│       └── references/
```

Or clone this entire repo into your project:

```bash
git clone https://github.com/JJValentin/Leverage-Lab-Free-Skills.git skills
```

### OpenClaw

Copy each skill folder to `~/.openclaw/skills/`:

```bash
cp -r skills/structured-reasoning ~/.openclaw/skills/
cp -r skills/deep-search ~/.openclaw/skills/
cp -r skills/skill-forge ~/.openclaw/skills/
```

### Any Other AI

The SKILL.md files are plain markdown. Copy the content into your system prompt, paste it as context, or reference it however your tool supports persistent instructions.

## Deep Search Prerequisites

Deep Search works out of the box for HackerNews and SearXNG. Other platforms need their respective tools:

- **YouTube:** [yt-dlp](https://github.com/yt-dlp/yt-dlp) installed
- **Reddit:** A Reddit OAuth token or the `reddit-research` CLI
- **X/Twitter:** [Bird CLI](https://github.com/nicholasgasior/bird) with session cookies, or an xAI API key
- **SearXNG:** A running instance (default: localhost:8888)

Missing a platform? The orchestrator skips unavailable platforms gracefully — you still get results from whatever's configured.

## The Workflow

These skills work best as part of a sequence, not in isolation:

1. **Brainstorm + Research** — Deep Search to explore the problem space
2. **Proposal** — Synthesize findings into a structured proposal
3. **Planning** — Structured Reasoning to make the key decisions
4. **Implementation** — Build with clarity, not guesswork

Most people go straight from brainstorm to implementation. The middle steps cost 15 minutes and save hours.

## Build Your Own

That's what Skill Forge is for. The best skills come from your own workflows — processes you already know work, packaged so AI can execute them reliably.

Start here:
1. Pick a task you explain to Claude repeatedly
2. Run Skill Forge: "skill-forge: create [what you want to automate]"
3. Test on a real task, iterate 2-3 times
4. You now have a reusable skill

## License

MIT — use these however you want.

## Questions?

DM me on social. I read all of them.

---

*From the [Leverage Lab](https://leveragelab.co) — building with AI, not just talking about it.*
