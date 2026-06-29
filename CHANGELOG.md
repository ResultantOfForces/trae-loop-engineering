# Changelog

All notable changes to the `trae-loop-engineering` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows the bespoke versioning policy described below.

## Version Strategy

Version bumps follow the impact of a change, not a calendar:

- **MAJOR** — breaking changes to artifact names, contract fields, or loop phases (e.g. renaming `11-plan-B.md`, adding/removing a contract field, or inserting/removing a loop phase). Resets consumers' artifact pipelines.
- **MINOR** — a new reference document, route tier (T0-T5), or `subagent_policy` value; additive and backward-compatible.
- **PATCH** — clarifications, typo/format fixes, doc corrections, or other non-breaking fixes.

## [Unreleased]

### [1.1.0] - Unreleased — Deep Optimization

#### Added
- `assets/` directory with fillable templates: `loop-state-template.md`, `brief-template.md`, `contract-template.md`, `task-packet-template.md`.
- `evals/evals.json` — machine-readable forward-test scenarios (14 ported from `references/forward-tests.md` + 2 new scenarios for the T4 and T5 route tiers), each with verifiable assertions and a `leak_hygiene` flag.
- Frontmatter compliance checks for skill metadata.
- Cross-platform validation scripts (PowerShell + Python 3.8+): `scripts/validate-loop-contract.{ps1,py}`, `scripts/validate-loop-state.{ps1,py}`.
- Method completeness coverage for all eight loop phases and the full six-interface contract.
- Deeper TRAE integration notes (Task subagent model constraint, auto-run prerequisite, cross-session resume).

#### Changed
- Forward-test scenarios converted from prose into structured, machine-readable JSON with `leak_hygiene` flags and explicit assertions.
- Reduced redundancy across references (deduplicated evidence, dispatch, and dual rules).

## [1.0.0] - 2026-06-28

### Added
- Initial port from `codex-loop-engineering` to TRAE.
- Six-interface contract (goal/state/context/act/capture/stop) and T0-T5 route tiers.
- Artifact protocol (`00-brief.md` through `50-final-report.md`).
- Dual plan/review via one-shot Task subagents; `subagent_policy` replacing `claude_policy`.
- File-based memory (`loop-state.md`) and cross-session resume protocol.
- Stop rules, evidence standards, and user checkpoints.
- Hybrid dual: same-model auto (default) and cross-model manual (upgrade).
- References, validation scripts, and example walk-throughs (`examples/minimal-refactor/`, `examples/resume-walkthrough/`).
