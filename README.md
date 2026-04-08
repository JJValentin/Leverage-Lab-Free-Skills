# Leverage Lab Free Skills

Production-tested AI skills and a custom project management schema. Install them and they work immediately.

> **AI Setup:** Point your AI assistant to this README. It contains everything needed to install these skills automatically and walk you through any manual setup steps.

---

## What's Inside

### AI Skills
- 🧠 **Structured Reasoning** — Systematic decision-making frameworks
- 🔍 **Deep Search** — Multi-platform parallel research engine
- 🔨 **Skill Forge** — The skill that builds skills

### Project Management
- 📋 **Agent-Ops Schema** — A custom [OpenSpec](https://github.com/Fission-AI/OpenSpec) schema for managing projects with AI agents. Structured workflow: proposal → specs → design → tasks → implementation.

---

## AI Installation Instructions

**If you are an AI assistant helping a user install these, follow these steps exactly.**

### Step 1: Detect the user's environment

Ask which platform they use, or detect it from context:

- **Claude Code** (native CLI) → skills go in the project directory or `~/.claude/skills/`
- **OpenClaw** → skills go in `~/.openclaw/skills/`
- **Cursor / Windsurf / other IDE** → skills go in the project's `.cursor/skills/` or equivalent config directory
- **Other AI tool** → the SKILL.md files are plain markdown; paste into system prompt or custom instructions

### Step 2: Clone and install skills

```bash
# Clone the repo
git clone https://github.com/JJValentin/Leverage-Lab-Free-Skills.git /tmp/leverage-lab-skills

# Copy skills to the appropriate directory based on platform:

# For Claude Code (project-level):
cp -r /tmp/leverage-lab-skills/skills/* ./skills/

# For Claude Code (global):
mkdir -p ~/.claude/skills
cp -r /tmp/leverage-lab-skills/skills/* ~/.claude/skills/

# For OpenClaw:
cp -r /tmp/leverage-lab-skills/skills/* ~/.openclaw/skills/

# Clean up
rm -rf /tmp/leverage-lab-skills
```

### Step 3: Install OpenSpec + Agent-Ops schema

The agent-ops schema requires [OpenSpec CLI](https://github.com/Fission-AI/OpenSpec). Install it first:

```bash
npm install -g @anthropic-ai/openspec@latest
```

Then set up the agent-ops schema in your project:

```bash
# Navigate to your project root
cd /path/to/your/project

# Initialize OpenSpec (if not already initialized)
openspec init

# Copy the agent-ops schema into your project's openspec directory
cp -r /tmp/leverage-lab-skills/openspec/schemas/agent-ops openspec/schemas/

# Copy the config that activates the schema
cp /tmp/leverage-lab-skills/openspec/config.yaml openspec/config.yaml
```

> **Note:** If you already have an `openspec/config.yaml`, merge the `schema: agent-ops` line and the context/rules sections instead of overwriting.

**Customize the config** — Edit `openspec/config.yaml` to match the user's setup:
- Update agent names under `context` (default: Z, Rex, Echo, Scout, Joshua)
- Update tools list to match their stack
- Adjust the rules if needed

### Step 4: Verify installation

After copying, confirm these exist:
- `structured-reasoning/SKILL.md`
- `deep-search/SKILL.md` (also contains `scripts/` directory)
- `skill-forge/SKILL.md` (also contains `references/` directory)
- `openspec/schemas/agent-ops/schema.yaml`
- `openspec/schemas/agent-ops/templates/` (4 template files)
- `openspec/config.yaml`

### Step 5: Deep Search setup (requires manual steps)

Deep Search works out of the box for **HackerNews** (no setup needed). Other platforms require tools the user must install:

**Tell the user which platforms need setup and ask which ones they want:**

| Platform | What's needed | Install command |
|----------|--------------|-----------------|
| YouTube | yt-dlp | `pip install yt-dlp` or `brew install yt-dlp` |
| Reddit | Reddit OAuth credentials | See [Reddit setup](#reddit-setup) below |
| X/Twitter | Bird CLI with session cookies, OR an xAI API key | See [X/Twitter setup](#xtwitter-setup) below |
| SearXNG | A running SearXNG instance | `docker run -d -p 8888:8080 searxng/searxng` |

**Missing platforms are fine.** The orchestrator skips unavailable platforms and returns results from whatever is configured.

### Step 6: Confirm to the user

Tell the user:
1. Which skills were installed and where
2. Which Deep Search platforms are ready vs need setup
3. Whether OpenSpec + agent-ops schema is set up
4. How to use each skill (see [Usage](#usage) below)

---

## Skills

### 🧠 Structured Reasoning

Forces systematic thinking on complex decisions. Instead of surface-level "here are some options" responses, it runs through frameworks: first principles, tradeoff analysis, assumption testing, multi-perspective validation.

**Use for:** Business strategy, offer positioning, pricing decisions, architecture choices — anything where the obvious answer might be wrong.

- Three modes: Light (quick decisions), Deep (irreversible decisions), Consensus (highest-stakes)
- Built on an 8-phase Engineering Flywheel framework
- Auto-routes by decision reversibility and complexity
- Optional "thinker" validation for Type 1 decisions

### 🔍 Deep Search

Multi-platform research across YouTube, Reddit, HackerNews, X/Twitter, and SearXNG — in parallel. Scored, deduplicated, cross-source linked results.

**Use for:** Market research, competitive analysis, content topic discovery, trend analysis, answering "what are people actually saying about X?"

- 5 platforms searched simultaneously
- Auto-selects platforms based on query type (product, concept, opinion, how-to, comparison, news)
- Three-axis scoring: relevance (45%), recency (25%), engagement (30%)
- Cross-source convergence detection (same topic across multiple platforms = stronger signal)
- Each platform also usable standalone
- Zero pip dependencies — uses only Python standard library + system tools

### 🔨 Skill Forge

Creates new skills or optimizes existing ones. The skill that builds skills. Feed it what you want to automate, and it generates a structured SKILL.md with triggers, steps, context, and constraints.

**Use for:** When you find yourself explaining the same process to your AI repeatedly. Turn any repeated workflow into a reliable, reusable skill.

- CREATE mode (new skills) and OPTIMIZE mode (improve existing)
- 11 thinking lenses for deep analysis
- Quality gates: timelessness scoring, size limits, trigger requirements
- 3-agent synthesis panel for validation
- Full reference docs included for the methodology

---

## Agent-Ops Schema (OpenSpec)

A custom OpenSpec schema designed for managing projects with AI agents. Instead of jumping straight from idea to implementation, it enforces a structured flow that prevents wasted work and scope creep.

### The Flow

```
Idea → Proposal → Specs → Design → Tasks → Implementation
         ↓          ↓        ↓         ↓
       (why)    (what done  (how)   (who does
                 looks like)         what)
```

### Artifacts

**Proposal** (`proposal.md`) — Establishes WHY this work is needed.
- What problem it solves, why now
- What changes (deliverables, workflows, systems)
- Workstreams (new and modified)
- Impact and ownership

**Specs** (`specs/<workstream>/spec.md`) — Defines WHAT done looks like.
- One spec per workstream from the proposal
- Acceptance criteria with GIVEN/WHEN/THEN scenarios
- Every criterion must be verifiable — clear pass/fail
- Supports delta operations: ADDED, MODIFIED, REMOVED criteria

**Design** (`design.md`) — Explains HOW the work gets done.
- Optional — only create when multiple agents/tools are involved, new integrations, or coordination is needed
- Context, goals/non-goals, approach, tools, risks, coordination, open questions

**Tasks** (`tasks.md`) — Breaks work into assignable units.
- Checkbox format for progress tracking: `- [ ] 1.1 @agent Task description`
- Each task completable in a single session (< 30 min)
- Grouped by phase with verification steps
- Includes approval gates where human sign-off is needed

### How to use it

Once OpenSpec and the agent-ops schema are installed:

```bash
# Start a new project/change
openspec new change "my-project-name"

# Check status
openspec status --change "my-project-name"

# Get instructions for creating an artifact
openspec instructions proposal --change "my-project-name"
```

Or just tell your AI:
```
"Create a new openspec change for [what you want to build]"
"Propose a change for redesigning the onboarding flow"
```

The AI reads the schema instructions, generates each artifact in dependency order, and produces a complete project plan ready for implementation.

### Customizing the schema

The `config.yaml` file defines your project context. Edit it to match your setup:

```yaml
schema: agent-ops

context: |
  # Describe your project/team here
  Agent team:
  - Agent1: role description
  - Agent2: role description
  - Human: final approver
  
  Tools: list your tools and platforms here

rules:
  proposal:
    - Include which agent(s) own execution
    - If external-facing, flag approval gates
  specs:
    - Every criterion must have a verifiable scenario
    - Use GIVEN/WHEN/THEN for scenarios
  design:
    - Name specific tools and skills
    - Flag any operations that need human approval
  tasks:
    - Tag every task with @agent or @human
    - Tasks must be completable in a single session
    - Include explicit verification steps per phase
```

### Schema structure

```
openspec/
├── config.yaml                          # Project context and rules
└── schemas/
    └── agent-ops/
        ├── schema.yaml                  # Artifact definitions and workflow
        └── templates/
            ├── proposal.md              # Proposal template
            ├── spec.md                  # Spec template  
            ├── design.md               # Design template
            └── tasks.md                # Tasks template
```

---

## Usage

### Structured Reasoning
```
"Use structured reasoning to evaluate whether I should raise prices or add a new tier"
"Structured reasoning: should we build this in-house or use a third-party API?"
```

### Deep Search
```
"Deep search: what are people saying about AI agents for small business?"
"Research this topic across all platforms: solopreneur automation tools"
```

Or run the script directly:
```bash
python3 skills/deep-search/scripts/search.py "your topic" --days 30 --depth default
```

Depth options: `quick` (fast scan), `default` (balanced), `deep` (thorough)

### Skill Forge
```
"Skill forge: create a skill for [what you want to automate]"
"Skill forge: optimize my existing [skill name] skill"
```

### Agent-Ops (OpenSpec)
```
"Create a new change for building a newsletter automation pipeline"
"Propose a change for redesigning the checkout flow"
"Show me the status of my current changes"
```

---

## Platform Setup Details

### Reddit Setup

You need Reddit API OAuth credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app" at the bottom
3. Choose "script" type
4. Set redirect URI to `http://localhost:8080`
5. Note your client ID (under the app name) and client secret
6. Set environment variables:
   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USERNAME="your_username"
   export REDDIT_PASSWORD="your_password"
   ```

### X/Twitter Setup

**Option A: Bird CLI** (scraping, no API key needed)
1. Install Bird CLI: https://github.com/nicholasgasior/bird
2. Authenticate with your X session cookies
3. Bird handles the rest

**Option B: xAI API key** (official API)
1. Get an API key from https://console.x.ai
2. Set: `export XAI_API_KEY="your_key"`

### SearXNG Setup

Run a local instance:
```bash
docker run -d --name searxng -p 8888:8080 searxng/searxng
```

Or point to an existing instance by setting: `export SEARXNG_URL="http://your-instance:8080"`

Default: `http://localhost:8888`

---

## The Workflow

These skills and the agent-ops schema work best as a sequence:

1. **Research** — Deep Search to explore the problem space
2. **Decide** — Structured Reasoning to evaluate options and make key decisions
3. **Plan** — Agent-Ops to create a proposal, specs, design, and tasks
4. **Build** — Work through the task list with clear acceptance criteria
5. **Capture** — Skill Forge to turn successful workflows into reusable skills

Most people skip straight from research to building. The planning steps cost 15 minutes and save hours.

## Build Your Own Skills

That's what Skill Forge is for. The best skills come from your own workflows — processes you already know work, packaged so AI can execute them reliably.

1. Pick a task you explain to your AI repeatedly
2. Run: `"skill forge: create [what you want to automate]"`
3. Test on a real task, iterate 2-3 times
4. You now have a reusable skill

## License

MIT — use these however you want.

## Questions?

DM me on social. I read all of them.

---

*From the [Leverage Lab](https://whop.com/leverage-lab-hq) — building with AI, not just talking about it.*
