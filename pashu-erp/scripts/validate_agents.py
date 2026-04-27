#!/usr/bin/env python3
"""
Validates that all SDLC agent definitions are structurally correct.

Run:  python scripts/validate_agents.py
JSON: python scripts/validate_agents.py --json

Exit 0 = all good, Exit 1 = failures found.
Writes JSON report to reports/latest/agent-validation.json when --json is passed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

AGENT_DIR = Path(".claude/agents")
AGENTS_INDEX = Path("AGENTS.md")
REPORT_DIR = Path("reports/latest")
HISTORY_DIR = Path("reports/history")

REQUIRED_FRONTMATTER = {"name", "description"}
MIN_LINES = 10
# Common hyphenated words in prose that aren't agent names
FALSE_POSITIVE_REFS = {
    "on-first-retry", "only-on-failure", "test-dir", "network-idle",
    "full-page", "non-blocking", "pre-release", "auto-load",
    "name-only", "package-level", "release-readiness",
    "docker-compose", "axe-core", "pashu-erp",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML frontmatter fields from markdown content."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def validate_agent(path: Path) -> dict:
    """Validate a single agent file. Returns a result dict."""
    name = path.stem
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    line_count = len(lines)
    errors: list[str] = []
    warnings: list[str] = []

    # Frontmatter
    fm = parse_frontmatter(text)
    if not fm:
        errors.append("missing YAML frontmatter")
    else:
        for field in REQUIRED_FRONTMATTER:
            if field not in fm:
                errors.append(f"missing '{field}' in frontmatter")

    # Minimum substance
    if line_count < MIN_LINES:
        errors.append(f"only {line_count} lines (expected {MIN_LINES}+)")

    # Should reference the workspace manifest
    if "WORKSPACE.md" not in text:
        warnings.append("does not reference WORKSPACE.md")

    return {
        "agent": name,
        "file": str(path),
        "lines": line_count,
        "frontmatter": fm,
        "errors": errors,
        "warnings": warnings,
        "status": "FAIL" if errors else "OK",
    }


def check_test_coverage(agents: list[dict]) -> list[str]:
    """Check whether each agent that has a corresponding test file in the test suite."""
    warnings: list[str] = []
    # Map agent roles to expected test file patterns
    test_dir = Path("pashu-erp/packages/api/tests")
    if not test_dir.is_dir():
        # Try from repo root
        test_dir = Path("packages/api/tests")
    if not test_dir.is_dir():
        warnings.append("API test directory not found -- skipping test coverage check")
        return warnings

    existing_tests = {f.stem for f in test_dir.glob("test_*.py")}
    # Agents that map to testable API modules
    testable_agents = {
        "backend-developer": "test_auth",
        "api-tester": "test_auth",
        "unit-tester": "test_disease_rules",
        "database-admin": "test_animals",
    }
    for agent_name, expected_test in testable_agents.items():
        agent_exists = any(a["agent"] == agent_name for a in agents)
        if agent_exists and expected_test not in existing_tests:
            warnings.append(f"agent '{agent_name}' has no corresponding test file '{expected_test}.py'")

    return warnings


def cross_reference_index(agents: list[dict]) -> list[str]:
    """Compare agent files against AGENTS.md index."""
    warnings: list[str] = []
    if not AGENTS_INDEX.exists():
        warnings.append("AGENTS.md not found — cannot cross-reference")
        return warnings

    index_text = AGENTS_INDEX.read_text(encoding="utf-8")
    index_refs = set(re.findall(r"([a-z][\w-]+)\.md", index_text))
    file_names = {a["agent"] for a in agents}

    missing_from_index = file_names - index_refs
    missing_from_disk = index_refs - file_names

    for name in sorted(missing_from_index):
        warnings.append(f"agent '{name}' exists on disk but not in AGENTS.md")
    for name in sorted(missing_from_disk):
        warnings.append(f"AGENTS.md references '{name}' but no file found")

    return warnings


def validate_impact_map(agents: list[dict]) -> list[str]:
    """Check that the pipeline-orchestrator's impact map references valid agents."""
    warnings: list[str] = []
    orchestrator = AGENT_DIR / "pipeline-orchestrator.md"
    if not orchestrator.exists():
        warnings.append("pipeline-orchestrator.md not found")
        return warnings

    text = orchestrator.read_text(encoding="utf-8")
    agent_names = {a["agent"] for a in agents}

    # Extract hyphenated references that look like agent names
    refs = set(re.findall(r"\b([a-z]+-[a-z]+(?:-[a-z]+)*)\b", text))
    refs -= FALSE_POSITIVE_REFS

    for ref in sorted(refs):
        if ref not in agent_names:
            # Check if it's a prefix of an actual agent (e.g. "browser-ui" → "browser-ui-tester")
            if any(a.startswith(ref) for a in agent_names):
                continue
            warnings.append(f"impact map references '{ref}' — no matching agent file")

    return warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SDLC agent definitions")
    parser.add_argument("--json", action="store_true", help="write JSON report")
    args = parser.parse_args()

    if not AGENT_DIR.is_dir():
        print(f"FAIL: Agent directory {AGENT_DIR} not found")
        sys.exit(1)

    agent_files = sorted(AGENT_DIR.glob("*.md"))
    results = [validate_agent(f) for f in agent_files]

    # Print results
    print("=== Agent Definition Validator ===\n")
    for r in results:
        tag = r["status"]
        suffix = f" — {', '.join(r['errors'])}" if r["errors"] else ""
        warn = f" [{', '.join(r['warnings'])}]" if r["warnings"] else ""
        print(f"{tag:4}  {r['agent']} ({r['lines']} lines){suffix}{warn}")

    total = len(results)
    errors = sum(1 for r in results if r["status"] == "FAIL")

    print(f"\n=== Results ===")
    print(f"Total agents: {total}")
    print(f"Errors: {errors}")

    # Cross-reference checks
    index_warnings = cross_reference_index(results)
    if index_warnings:
        print(f"\n=== AGENTS.md Cross-Reference ===")
        for w in index_warnings:
            print(f"WARN  {w}")

    impact_warnings = validate_impact_map(results)
    if impact_warnings:
        print(f"\n=== Impact Map Validation ===")
        for w in impact_warnings:
            print(f"WARN  {w}")

    test_warnings = check_test_coverage(results)
    if test_warnings:
        print(f"\n=== Test Coverage ===")
        for w in test_warnings:
            print(f"WARN  {w}")

    # Verdict
    verdict = "FAIL" if errors > 0 else "PASS"
    print(f"\nVERDICT: {verdict} ({total} agents, {errors} errors)")

    # JSON report
    if args.json:
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total": total,
            "passed": total - errors,
            "failed": errors,
            "verdict": verdict,
            "agents": results,
            "index_warnings": index_warnings,
            "impact_map_warnings": impact_warnings,
            "test_coverage_warnings": test_warnings,
        }
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        out = REPORT_DIR / "agent-validation.json"
        out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\nReport written to {out}")

        # Also archive
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive = HISTORY_DIR / f"agent-validation-{ts}.json"
        archive.write_text(json.dumps(report, indent=2) + "\n")

    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
