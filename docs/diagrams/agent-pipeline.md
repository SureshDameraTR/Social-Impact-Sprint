# SDLC Agent Pipeline — Flow Diagrams

## Pipeline Orchestrator — 3 Modes

```mermaid
flowchart TD
    START(["/pipeline"]) --> DETECT{Auto-detect mode}

    DETECT -->|git diff has files| CHANGE["CHANGE mode"]
    DETECT -->|no changes| REQ["REQUIREMENT mode"]
    DETECT -->|explicit arg| RELEASE["RELEASE mode"]

    REQ --> R1["Stage 1: Understand<br/>business-analyst + agritech-domain-expert"]
    R1 --> R2["Stage 2: Design<br/>software-architect + ux-designer"]
    R2 --> APPROVE{User approves?}
    APPROVE -->|yes| R3["Stage 3-8: Implement + Verify"]
    APPROVE -->|no| R2

    CHANGE --> C1["Detect changed files"]
    C1 --> C2["Impact map → select agents"]
    C2 --> C3["Stages 3-8 in parallel"]

    RELEASE --> L1["Activate ALL 34 agents"]
    L1 --> L2["Full 8-stage sweep"]

    R3 --> SCORE
    C3 --> SCORE
    L2 --> SCORE
    SCORE(["Scorecard + VERDICT"])
```

## Stage Execution — Parallel with Gates

```mermaid
flowchart LR
    subgraph S3["Stage 3: Fast Checks"]
        direction TB
        LINT["ruff check"]
        TYPE["tsc --noEmit"]
        FMT["prettier"]
    end

    subgraph S4["Stage 4: Build"]
        direction TB
        API_B["uvicorn import check"]
        ADMIN_B["next build"]
        COLL_B["vite build"]
        VET_B["vite build"]
    end

    subgraph S5["Stage 5: Functional Tests"]
        direction TB
        UNIT["unit-tester"]
        INTG["integration-tester"]
        API_T["api-tester"]
        CTR["contract-tester"]
    end

    subgraph S6["Stage 6: UI Tests"]
        direction TB
        BRW["browser-ui-tester"]
        A11Y["accessibility-tester"]
        RUX["rural-ux-reviewer"]
        VIS["visual-regression-tester"]
    end

    subgraph S7["Stage 7: Non-Functional"]
        direction TB
        PERF["performance-tester"]
        LOAD["load-tester"]
        NET["network-resilience"]
        CHAOS["chaos-tester"]
    end

    subgraph S8["Stage 8: Security"]
        direction TB
        SEC_A["security-analyst"]
        SEC_T["security-tester"]
        COMP["compliance-auditor"]
    end

    S3 -->|GATE: 0 errors| S4
    S4 -->|GATE: all build| S5
    S5 -->|GATE: tests pass| S6
    S6 -->|GATE: no CRITICAL| S7
    S7 -->|GATE: no BLOCK| S8
    S8 --> DONE(["VERDICT"])
```

## /review Command — Multi-Perspective Dispatch

```mermaid
flowchart TB
    START(["/review"]) --> DIFF["git diff + git diff --cached"]
    DIFF --> CLASSIFY{"Classify changes"}

    CLASSIFY -->|always| CR["code-reviewer"]
    CLASSIFY -->|always| SA["security-analyst"]
    CLASSIFY -->|UI files| A11Y["accessibility-tester"]
    CLASSIFY -->|UI files| RUX["rural-ux-reviewer"]
    CLASSIFY -->|API changes| CTR["contract-tester"]
    CLASSIFY -->|API changes| APT["api-tester"]
    CLASSIFY -->|mobile| I18N["i18n-tester"]
    CLASSIFY -->|mobile| NET["network-resilience"]
    CLASSIFY -->|PII/auth| COMP["compliance-auditor"]

    CR --> SYNTH
    SA --> SYNTH
    A11Y --> SYNTH
    RUX --> SYNTH
    CTR --> SYNTH
    APT --> SYNTH
    I18N --> SYNTH
    NET --> SYNTH
    COMP --> SYNTH

    SYNTH(["Synthesized Review<br/>grouped by file, sorted by severity"])
```

## Impact Map — File Pattern to Agent Routing

```mermaid
flowchart LR
    subgraph Patterns["Changed File Patterns"]
        P1["packages/api/app/models/*"]
        P2["packages/api/app/routers/*"]
        P3["packages/api/app/services/*"]
        P4["packages/admin/src/**"]
        P5["packages/mobile/app/**"]
        P6["packages/collection/src/**"]
        P7["packages/vet/src/**"]
        P8["alembic/versions/*"]
        P9["docker-compose.yml"]
    end

    subgraph Agents["Activated Agents"]
        A1["backend-developer"]
        A2["database-admin"]
        A3["frontend-developer"]
        A4["mobile-developer"]
        A5["devops-engineer"]
        A6["agritech-domain-expert"]
    end

    P1 --> A1
    P1 --> A2
    P2 --> A1
    P3 --> A1
    P3 --> A6
    P4 --> A3
    P5 --> A4
    P6 --> A3
    P7 --> A3
    P8 --> A2
    P9 --> A5
```
