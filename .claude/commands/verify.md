# Quick Verify

Fast verification of current code changes. Runs only the relevant pipeline stages for uncommitted changes — no full release sweep.

## Usage

`/verify` — Detect changed files and run fast checks + build + functional tests

## Instructions

This is a lightweight shortcut for `/pipeline change`. Execute these steps:

### 1. Detect Changes

```bash
git diff --name-only HEAD
git diff --cached --name-only
```

If no changes detected, report "No changes to verify" and exit.

### 2. Route Agents

Read the impact map from `.claude/agents/pipeline-orchestrator.md` (Step 2: Route via Impact Map section).
Match changed file paths against patterns to determine which agents activate.

### 3. Execute Fast Pipeline (stages 3-5 only)

**Stage 3 — Fast Checks** (parallel):
- code-reviewer: pattern/style review of the diff
- security-analyst: OWASP quick scan on changed files
- contract-tester: schema consistency check (if API files changed)

**Stage 4 — Build & Lint** (parallel):
- `ruff check` on Python files (if changed)
- `next build` on admin (if changed)
- `vite build` on collection/vet (if changed)

**Stage 5 — Functional Tests** (parallel):
- Run relevant test suites based on what changed

### 4. Report

Output a compact scorecard with pass/fail per stage and any findings.
Skip stages 6-8 (quality, security, release gate) — those are for `/pipeline change` or `/pipeline release`.
