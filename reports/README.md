# Agent Reports & Baselines

Structured artifact storage for SDLC agent outputs. Agents write here; pipeline reads here for comparison.

## Directory Structure

```
reports/
  baselines/           Frozen reference points for comparison
    performance.json   Response times, bundle sizes, Lighthouse scores
    security.json      OWASP Top 10 checklist state + vulnerability counts
    accessibility.json WCAG 2.1 AA compliance scores per package
    coverage.json      Test coverage by package and category
    load.json          k6 baseline metrics (p95, throughput, error rate)
    i18n.json          Translation completeness per locale
    nfr-scorecard.json 10-category NFR scores (0-100 each)
    compliance.json    DPDP Act + Aadhaar Act compliance status

  latest/              Most recent run (overwritten each run)
    scorecard.md       Pipeline orchestrator verdict
    <agent-name>.md    Per-agent findings from last run

  history/             Timestamped archive (append-only)
    YYYY-MM-DD-<agent>.md
```

## How Agents Use This

### Writing Results
Every agent that produces a report writes TWO files:
1. `reports/latest/<agent-name>.md` — overwritten each run
2. `reports/history/YYYY-MM-DD-<agent-name>.md` — archived copy

### Comparing to Baseline
Agents that track metrics read from `reports/baselines/<category>.json` and compare:
- **Green**: metric improved or within tolerance
- **Yellow**: metric degraded < 10%
- **Red**: metric degraded >= 10% or new violation

### Updating Baselines
Baselines are updated manually after a successful release:
```bash
# After pipeline release with PASS verdict:
cp reports/latest/performance.json reports/baselines/performance.json
cp reports/latest/security.json reports/baselines/security.json
# etc.
```

## Agent-to-Artifact Map

| Agent | Writes | Reads Baseline |
|-------|--------|----------------|
| pipeline-orchestrator | `latest/scorecard.md` | all baselines |
| performance-tester | `latest/performance-tester.md` + `baselines/performance.json` | `baselines/performance.json` |
| load-tester | `latest/load-tester.md` + `baselines/load.json` | `baselines/load.json` |
| security-analyst | `latest/security-analyst.md` + `baselines/security.json` | `baselines/security.json` |
| security-tester | `latest/security-tester.md` | `baselines/security.json` |
| accessibility-tester | `latest/accessibility-tester.md` + `baselines/accessibility.json` | `baselines/accessibility.json` |
| rural-ux-reviewer | `latest/rural-ux-reviewer.md` | none |
| compliance-auditor | `latest/compliance-auditor.md` + `baselines/compliance.json` | `baselines/compliance.json` |
| nfr-validator | `latest/nfr-validator.md` + `baselines/nfr-scorecard.json` | `baselines/nfr-scorecard.json` |
| i18n-tester | `latest/i18n-tester.md` + `baselines/i18n.json` | `baselines/i18n.json` |
| qa-lead | `latest/qa-lead.md` + `baselines/coverage.json` | `baselines/coverage.json` |
| visual-regression-tester | `latest/visual-regression-tester.md` | `e2e/snapshots/` |
| code-reviewer | `latest/code-reviewer.md` | none |
| contract-tester | `latest/contract-tester.md` | none |
| api-tester | `latest/api-tester.md` | none |
| unit-tester | `latest/unit-tester.md` | `baselines/coverage.json` |
| integration-tester | `latest/integration-tester.md` | none |
| e2e-tester | `latest/e2e-tester.md` | none |
| browser-ui-tester | `latest/browser-ui-tester.md` | none |
| chaos-tester | `latest/chaos-tester.md` | none |
| network-resilience-tester | `latest/network-resilience-tester.md` | none |
| data-integrity-tester | `latest/data-integrity-tester.md` | none |
| release-manager | `latest/release-manager.md` | all baselines |
| business-analyst | `latest/business-analyst.md` | none |
| observability-engineer | `latest/observability-engineer.md` | none |
