# Code Review

Run an agent-powered code review on current changes using the SDLC agent suite.

## Usage

- `/review` — Review all uncommitted changes
- `/review <file>` — Review a specific file

## Instructions

### 1. Gather Changes

If `$ARGUMENTS` specifies a file, focus on that file. Otherwise:

```bash
git diff --name-only HEAD
git diff --cached --name-only
```

Read the full diff for each changed file.

### 2. Dispatch Reviewers (parallel)

Launch these agents simultaneously using the Agent tool, each reviewing the diff from their perspective:

1. **code-reviewer** — Coding standards, patterns, anti-patterns, DRY, SOLID
2. **security-analyst** — OWASP Top 10, auth checks, injection, data exposure
3. **accessibility-tester** — If UI files changed: WCAG 2.1 AA, contrast, ARIA

For API changes, also launch:
4. **contract-tester** — Response envelope, schema consistency, breaking changes
5. **api-tester** — Edge cases, error handling, pagination

For mobile changes, also launch:
6. **i18n-tester** — Translation coverage, RTL, number formatting
7. **network-resilience-tester** — Offline handling, retry logic

For any UI/frontend changes, also launch:
8. **rural-ux-reviewer** — Farmer literacy, sunlight readability, touch targets, offline-first UX

For Python backend changes involving PII/auth/user data, also launch:
9. **compliance-auditor** — DPDP Act 2023, Aadhaar handling, consent flows, data retention

### 3. Synthesize

Collect all agent findings and present a unified review:

```
FILE: <path>
  [CRITICAL] <agent>: <finding>
  [HIGH]     <agent>: <finding>
  [MEDIUM]   <agent>: <finding>
  [LOW]      <agent>: <finding>
```

Group by file, sort by severity within each file.

### 4. Summary

End with:
- Total findings by severity
- Top 3 items to fix before committing
- Whether the changes are safe to commit as-is
