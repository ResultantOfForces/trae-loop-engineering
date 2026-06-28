# Resume Walk-through — Interrupt and Continue

This is a positive example of resuming a loop after an interruption. It complements `forward-tests.md` (which asserts edge cases) by showing the happy path step by step. File/symbol names are illustrative.

## Scenario

A T3 loop is refactoring `src/auth/login.ts` from callbacks to async/await. The main agent completed Phases 1-3 (brief, dual plan, merge) and started Phase 4 (execution). Mid-execution the session was closed. A new session resumes the loop.

## State At Interruption

`docs/loop-engineering/2026-06-28-auth-async-await/loop-state.md` at interruption:

```yaml
loop_id: 2026-06-28-auth-async-await
artifact_dir: docs/loop-engineering/2026-06-28-auth-async-await
phase: execution
phase_step: 4
role: execution
loop_status: active
next_action: "Rewrite the refresh helper in src/auth/login.ts; then write 20-execution-report.md"
next_role: execution
next_phase: execution_report
blockers: []
open_gaps: []
route_tier: T3
subagent_policy: required
dual_mode: same_model_auto
auto_iteration: enabled
latest_artifacts:
  brief: 00-brief.md
  plan_a: 10-plan-A.md
  plan_b: 11-plan-B.md
  plan_merged: 12-plan-merged.md
  execution_report: null
  review_a: null
  review_b: null
  arbitration: null
  final_report: null
worklog: worklog.md
repair_iteration: 0
open_p0_count: 0
resume_count: 0
created_at: 2026-06-28T10:00:00+08:00
last_updated: 2026-06-28T12:30:00+08:00
last_event: "started rewriting login() to async/await"
```

## Resume Steps

### New session first message
```
resume loop 2026-06-28-auth-async-await
```

### Step 1 — Locate
The agent finds `docs/loop-engineering/2026-06-28-auth-async-await/` (named by loop_id).

### Step 2 — Read loop-state.md first
The agent reads `loop-state.md`. It runs:
```powershell
powershell -File scripts/validate-loop-state.ps1 -Path loop-state.md
```
Output: `OK`. The agent now knows: phase=execution, step 4/8, role=execution, no blockers, no gaps, dual_mode=same_model_auto, auto_iteration=enabled.

### Step 3 — Read worklog
The agent reads `worklog.md` and learns: brief written, plan-A written, plan-B dispatched and returned, merged plan written and validated, execution started on `login()`. This explains WHY the loop is at execution.

### Step 4 — Read latest artifacts per role context
Execution role context (per `lane-roles.md`): merged plan + local code/tests. The agent reads `12-plan-merged.md` and `src/auth/login.ts` (current state). It does NOT read review/arbitration artifacts (they are null).

### Step 5 — Validate completeness
- `12-plan-merged.md` exists, non-empty, has required headings -> OK.
- Phase=execution, so the agent checks `git status` and compares against any partial execution report. The worktree shows `login.ts` modified but no `20-execution-report.md` yet -> consistent with "execution in progress, not yet reported". No `resume-with-gap`.

### Step 6 — Classify
No blockers, no open_gaps, artifacts consistent -> **clean resume**. Skip Step 7.

### Step 8 — Continue from next_action
`auto_iteration=enabled` and TRAE auto-run is ON -> the agent continues automatically. It resumes `next_action`: finishes rewriting the refresh helper, then writes `20-execution-report.md`, advancing to Phase 5 (execution_report). It then dispatches review-A and review-B subagents (Phase 6), arbitrates (Phase 7), repairs if needed within the cap, and writes `50-final-report.md` (Phase 8) — stopping only if a halt point triggers.

### Step 9 — Update loop-state.md and worklog
Immediately on resume:
```yaml
# updated fields
resume_count: 1
last_updated: 2026-06-28T15:00:00+08:00
last_event: "resumed from execution"
```
And appended to `worklog.md`:
```yaml
state_event:
  loop_id: 2026-06-28-auth-async-await
  event_id: resume-1
  role: manager
  status: active
  next_role: execution
  next_action: "Rewrite the refresh helper; write 20-execution-report.md"
  stop_or_continue: continue
  evidence: loop-state.md resume_count=1
```

As the loop advances through subsequent phases, the agent overwrites `loop-state.md` (phase, phase_step, latest_artifacts, etc.) and appends worklog events per `loop-state-schema.md`.

## Resume With Gap (Contrast)

If instead `loop-state.md` had `open_gaps: [plan-gap]` at interruption, Step 6 would classify **resume-with-gap**, Step 7 would stop for a checkpoint presenting the gap and options (retry / proceed degraded / return to planning / pause), and the loop would NOT auto-advance.

## What This Walk-through Proves

- resume reads `loop-state.md` first, not chat history;
- the same `loop_id` is reused, no new loop created;
- a clean resume auto-continues through the remaining phases;
- a gap stops the resume for a checkpoint;
- `loop-state.md` and worklog are updated on resume and on every subsequent phase change.
