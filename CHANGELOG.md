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

## [1.1.0] - 2026-06-29 — Deep Optimization

### Added
- `assets/` directory with fillable templates: `loop-state-template.md`, `brief-template.md`, `contract-template.md`, `task-packet-template.md`.
- `evals/evals.json` — machine-readable forward-test scenarios (14 ported from `references/forward-tests.md` + 2 new scenarios for the T4 and T5 route tiers), each with verifiable assertions and a `leak_hygiene` flag.
- Frontmatter compliance: `license`, `compatibility`, `metadata` (version, min-trae-version, tags), `allowed-tools` fields per agentskills.io spec.
- Cross-platform validation scripts (PowerShell + Python 3.8+): `scripts/validate-loop-contract.{ps1,py}`, `scripts/validate-loop-state.{ps1,py}`.
- SKILL.md Table of Contents (25 entries).
- Method chapters: Admission Gates, Execution Batch Sizing, Skill Promotion (expanded), Quick Arbitration Output.
- TRAE Memory, Rules, and MCP Integration chapter.
- Table of Contents added to 6 reference files (>100 lines): `lane-roles.md`, `subagent-dispatch.md`, `user-checkpoints.md`, `loop-state-schema.md`, `state-feedback-schema.md`, `resume-protocol.md`.
- Automation Guidance section in `references/forward-tests.md`.
- `CHANGELOG.md` following Keep a Changelog format.
- `README.md` Option D (.agents/skills/ path), Versioning section.

### Changed
- SKILL.md description simplified from 1019 to ~785 characters (removed redundant "Appropriate for..." paragraph).
- 7 SKILL.md sections compressed to summary + trigger format (Subagent Dual, Hybrid Dual, Stop Rules, Evidence Standards, Auto-Iteration, User Checkpoints, Roles).
- All PowerShell references updated to dual-platform format (PowerShell + Python 3.8+) across 10 files.
- README.md TRAE Work UI path fixed: "Settings > Skills & Commands" → "left sidebar → Skills (技能) → Installed tab".
- README.md Layout updated to include `assets/`, `evals/`, `CHANGELOG.md`, and dual-platform scripts.
- Forward-test scenario 2 aligned to 8-phase model (Brief → Dual Plan → Plan Merge → Execution → Execution Report → Dual Review → Arbitration → Final Report).
- Forward-test scenarios converted from prose into structured, machine-readable JSON with `leak_hygiene` flags and explicit assertions.
- Reduced redundancy across references (deduplicated evidence, dispatch, and dual rules).

### Fixed
- P2-2: `validate-loop-state.ps1` now validates `subagent_policy` (not_needed/conditional/required) and `route_tier` (T0-T5) enum values.
- P3-1: `validate-loop-state.ps1` redundant blockers condition (duplicate `[]` check) replaced with checks for `none` and empty string.
- P3-4: `Has-Key` / `has` token matcher regex fixed in all four validators (`validate-loop-contract.{ps1,py}`, `validate-loop-state.{ps1,py}`) — keys at start/end of normalized text now match.

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
