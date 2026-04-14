# Pipeline Orchestrator

Invoke the SDLC pipeline to verify code changes, implement requirements, or perform a full release sweep.

## Usage

- `/pipeline` — Auto-detect mode from git state (CHANGE if uncommitted diffs exist, otherwise prompt for requirement)
- `/pipeline requirement <text>` — REQUIREMENT mode: design + implement + verify a new feature
- `/pipeline change` — CHANGE mode: verify current uncommitted changes
- `/pipeline release` — RELEASE mode: full pre-release sweep of all 34 agents

## Instructions

You are invoking the pipeline orchestrator. Follow these steps:

### 1. Determine Mode

Parse the argument `$ARGUMENTS`:

- If argument starts with "requirement" or "req": **REQUIREMENT mode** — extract the requirement text after the keyword
- If argument is "change": **CHANGE mode**
- If argument is "release": **RELEASE mode**
- If no argument: **Auto-detect** — run `git diff --name-only` and `git diff --cached --name-only`. If files changed, use CHANGE mode. Otherwise, ask the user what they'd like to do.

### 2. Read the Orchestrator

Read `.claude/agents/pipeline-orchestrator.md` for the full orchestration protocol including:
- Stage definitions and gating rules
- Impact map (file pattern to agent routing)
- Agent communication protocol (JSON findings format)
- Scorecard format
- Conflict resolution rules

### 3. Execute

Follow the orchestrator's instructions for the selected mode:

**REQUIREMENT mode:**
1. Understand (business-analyst + agritech-domain-expert)
2. Design (software-architect + ux-designer in parallel)
3. Get user approval on design
4. Implement (dispatch to relevant developers)
5. Auto-trigger CHANGE pipeline on the new code

**CHANGE mode:**
1. `git diff --name-only` to detect changed files
2. Match against impact map to select agents
3. Execute stages 3-8 (agents within each stage run in parallel via Agent tool)
4. Gate after each stage — stop on BLOCK, continue on WARN
5. Produce scorecard

**RELEASE mode:**
1. Activate ALL 34 agents
2. Include load, chaos, NFR validation
3. Full scorecard + release report

### 4. Report

Always end with the ASCII scorecard showing per-stage results and a VERDICT.

### 5. Beads Integration

- If findings require follow-up work, create beads issues: `bd create --title="<finding>" --type=bug --priority=<0-4>`
- If running for a specific bead, close it after successful pipeline: `bd close <id>`
