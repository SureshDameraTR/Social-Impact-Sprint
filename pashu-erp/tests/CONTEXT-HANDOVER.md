# Context Handover — PashuRaksha Test Suite Build

**Last updated**: 2026-04-20 (end of Phase 0 session)
**Use this file** when starting a new session so you do not re-discover what
the previous session already verified. Read this top-to-bottom before doing
anything else.

---

## 1. The user's standing rules (do not violate)

These came directly from the user across two messages and override any
default behaviour:

1. **No hallucinations.** Never claim a fact, count, or success without
   running a command that produces it. If you have to guess, **stop and
   ask**.

2. **No half-testing while reporting success.** A test is "passing" only
   after you have run it and read the output. "Should pass" is not
   passing.

3. **Everything must be in depth.** If a section says "every endpoint",
   every endpoint must actually be listed.

4. **Don't believe any doc and blindly follow.** Cross-verify every claim
   from CLAUDE.md, READMEs, AGENTS.md against the live code or live
   services. Use your own thinking.

5. **Always double-verify.** When you discover something with one command,
   re-confirm it with a second command from a different angle before
   relying on it.

6. **When context fills up, write a context handover file.** That is this
   file. Update it before any compaction.

---

## 2. Where we are in the workflow

The user kicked off a "build a complete production-grade test suite"
project structured in phases. The Phase 1 message was **truncated** at
`Create this directory structure:` — the user has not yet sent the
directory layout or the Phase 1 spec.

**Current phase: Phase 0 (Discovery) — DONE.**
**Next phase: WAIT FOR USER** to paste the rest of Phase 1.

Do **NOT** invent Phase 1 scope. Do **NOT** start writing tests. The user
will resend.

### Default decisions taken when the user did not answer clarifying questions

The previous session asked 4 clarifying questions and the user did not
answer them, so these defaults were applied:

1. **AUDIT THEN AUGMENT** the existing test suite (do not replace it).
2. **Phase 0 only** for now. Wait for explicit Phase 1 spec.
3. **Verify the environment first** before claiming anything is testable.
4. **Discovery report path**: `pashu-erp/tests/DISCOVERY-REPORT.md`.

If the user wants different defaults, they will say so when they resend.

---

## 3. What is on disk right now

```
pashu-erp/tests/
├── DISCOVERY-REPORT.md      # full Phase 0 report (~600 lines, all numbers verified)
└── CONTEXT-HANDOVER.md      # this file
```

The existing test suites are **inside the packages**, not in this top-level
`tests/` directory. Specifically:

```
pashu-erp/packages/api/tests/                # pytest, 529 cases, 494 passing
pashu-erp/packages/api/tests/integration/    # 13 cases, real Postgres :5433
pashu-erp/packages/admin/src/__tests__/      # Jest, 4 files
pashu-erp/packages/mobile/src/__tests__/     # Jest, 16 real test files + setup
pashu-erp/packages/collection/src/__tests__/ # vitest, 2 files / 7 tests passing
pashu-erp/packages/vet/src/__tests__/        # vitest, 2 files / 9 tests passing
pashu-erp/e2e/                               # Playwright + k6 (43 test() blocks)
```

---

## 4. Verified facts (do not re-verify these)

Every number below came from a command that was actually run. Sources are
in `tests/DISCOVERY-REPORT.md` Appendix.

| Thing                          | Number      |
| ------------------------------ | ----------- |
| API routers                    | 29          |
| API endpoints                  | 115         |
| DB tables                      | 27          |
| DB mapped columns              | 245         |
| Alembic migrations             | 12          |
| Mock-backend endpoints         | 12          |
| Pytest cases collected         | 529         |
| Pytest passing (unit)          | 494         |
| Pytest skipped                 | 24          |
| Pytest failing (unit)          | 0           |
| Integration pytest cases       | 13          |
| Vitest collection passing      | 7 of 7      |
| Vitest vet passing             | 9 of 9      |
| Playwright `test()` blocks     | 43          |
| Frontend Jest files (admin)    | 4           |
| Frontend Jest files (mobile)   | 18 (16 real + 2 setup) |

The `DISCOVERY-REPORT.md` has the per-router endpoint table, per-model
column counts, full endpoint inventory by method+path+handler, full UI
route map for all 4 frontends, and the auth contract per app.

---

## 5. Open questions / loose ends to address before/in Phase 1

These are NOT done yet. Do NOT skip them when Phase 1 starts.

1. **Why are 24 pytest tests skipped?** Run `cd packages/api && uv run
   pytest tests/ --ignore=tests/integration -rs -q | grep SKIP` and
   document the reasons. Could be a fixture-gated module (likely OK) or
   hidden failures (definitely not OK).

2. **Coverage gap by endpoint, not by file.** A test file exists for every
   router, but we have not measured whether every one of the 115 endpoints
   is actually exercised. Required Phase 1 task: walk each `test_<router>.py`
   and tag which endpoints it hits, produce a coverage matrix.

3. **k6 load test (`e2e/load/baseline.js`) uses hard-coded OTP `123456`.**
   Will 401 against real auth. Either (a) seed a fixed OTP in test mode,
   (b) wire a `MOCK_OTP_VALUE` env var, or (c) rewrite to scrape OTP from
   API logs like `e2e/fullstack-smoke.spec.ts` does.

4. **`milk_center.py` 6th endpoint** (`POST /v1/milk-center/farmers/enroll`)
   was found by raw count but not by the function-name extractor. Re-read
   `packages/api/app/routers/milk_center.py` lines ~340 to confirm the
   handler name before writing a test.

5. **Vaccination route order** — `/vaccinations/{animal_id}` and
   `/vaccinations/schedule` overlap. Pin the ordering with a test.

6. **Income summary route shadowing** — `/income/summary/{user_id}` vs
   `/income/summary`. Pin with a test.

7. **Two copies of `kannada-parser.test.ts`** in the mobile package
   (`src/__tests__/services/` and `src/services/__tests__/`). Investigate;
   either deduplicate or document why both exist.

8. **CDP scripts under `e2e/`** (13 `.py` files) are not part of any test
   runner. Decide: integrate or delete.

9. **Frontend services not in default docker profile.** Any e2e suite must
   either use `--profile frontend` on docker compose or rely on Playwright's
   `webServer` config to spin them up. Document explicitly which path the
   e2e plan takes.

10. **Demo seed users** (`+91990000000{1,2,5,6}`) are baked into the
    Playwright spec. Their existence must become a precondition test, not
    an assumption.

---

## 6. Verification snippets — run these to re-baseline at the start of any session

```bash
# From pashu-erp/

# Stack health
docker ps --format "table {{.Names}}\t{{.Status}}" | head
curl -s http://localhost:8000/health
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8001/health

# Endpoint count (must equal 115)
grep -rE "^@router\." packages/api/app/routers/ | wc -l

# Pytest baseline (must end "494 passed, 24 skipped")
cd packages/api && uv run pytest tests/ --ignore=tests/integration -q --tb=no | tail -1

# Vitest baselines (must show "7 passed" and "9 passed")
( cd packages/collection && npx vitest run 2>&1 | tail -2 )
( cd packages/vet && npx vitest run 2>&1 | tail -2 )
```

If any of these baselines change, **investigate before doing anything
else** — something has drifted since this handover was written.

---

## 7. Tooling notes for the next session

- **Always use** `nvm use 22` before running any node tooling. The
  default `node` on this WSL install may be older.
- **Always use** `uv run pytest` (never bare `pytest`) inside
  `packages/api/`. The project's deps are uv-managed.
- **Do not use** `npx vitest list --run` to count tests — it under-reports.
  Use `npx vitest run` and read the summary.
- **Avoid `cat`/`head`/`tail`/`sed`/`awk`** as primary file tooling — the
  agent has dedicated `Read`, `Grep`, `Glob`, `StrReplace`, `Write` tools
  that are more reliable. Shell is for git/docker/test runners.
- **Working directory** for shell commands defaults to the workspace root
  `Social-Impact-Sprint/`. Most commands need `working_directory:
  /home/sdamera/workbench/Social-Impact-Sprint/pashu-erp`.

---

## 8. The unfinished Phase 1 prompt (verbatim, as far as it went)

> "## PHASE 1: BACKEND API TESTING (pytest + httpx)
>
> ### 1A. Setup
> Create this directory structure:"

Everything after the colon was cut off. **Wait for the user to resend.**

---

## 9. How to use this file at session start

1. **Read this file in full** before responding to anything.
2. Run the verification snippets in section 6. If everything matches,
   proceed. If not, investigate before claiming anything else.
3. Update section 4 (verified facts) and section 5 (open questions) as you
   make progress. **Never delete entries** — only mark them resolved.
4. When this session is itself running low on context, update this file
   again before compaction so the chain of trust never breaks.
