# Resume Protocol

Use this reference when continuing a loop after a restart, session switch, or interruption. TRAE clears chat context on every new session, so resume must reconstruct state entirely from files.

## When To Resume

Send `resume loop <loop_id>` or "continue the previous loop" in a new session. The agent should resume when:

- a prior loop was interrupted (session closed, context compacted, crash, user switched tasks);
- the user explicitly asks to continue a loop;
- a new session starts and an active (non-completed) `loop-state.md` exists.

Do not start a new loop when an active one exists for the same work. Reuse the `loop_id` and `artifact_dir`.

## The 9 Steps

### Step 1 — Locate the artifact directory
- Preferred: the user message names the `loop_id` -> locate `docs/loop-engineering/<loop_id>/`.
- Fallback: scan `docs/loop-engineering/` subdirectories for one containing `loop-state.md` with `loop_status` not `completed`; pick the most recent by `last_updated`.
- Not found -> tell the user no active loop exists; ask whether to start fresh or specify a path.

### Step 2 — Read loop-state.md first
- This is the only first-read entry point. Do not read the brief or plan first.
- Extract: `loop_id`, `phase`, `phase_step`, `role`, `loop_status`, `next_action`, `next_role`, `next_phase`, `blockers`, `open_gaps`, `dual_mode`, `auto_iteration`, `latest_artifacts`, `worklog`, `repair_iteration`.
- Run `powershell -File scripts/validate-loop-state.ps1 -Path loop-state.md`. If it fails, treat as cannot-resume.

### Step 3 — Read the worklog
- Read `worklog.md` (the append-only event stream) to understand the history: prior phase transitions, subagent dispatches, user decisions, repair iterations.
- Purpose: reconstruct WHY the loop is at the current phase, not just WHERE it is.

### Step 4 — Read the latest artifacts per role context rules
- Use `lane-roles.md` Context Rules By Role to decide what to read:
  - execution reads merged plan + local code/tests;
  - arbitration reads both reviews + execution report + live evidence;
  - planning reads broadly;
  - review reads the bounded evidence bundle.
- Do not read future-phase artifacts (they should be null in latest_artifacts).

### Step 5 — Validate artifact completeness
- Check that non-null `latest_artifacts` entries exist, are non-empty, and have required headings (per `subagent-dispatch.md` Failure Handling).
- Missing/empty/malformed -> mark `resume-with-gap: <artifact> <problem>`.
- If `phase=execution`, compare `git status` / diff against the execution report. If the worktree has changes not reflected in the report (or vice versa), mark `resume-with-gap: incomplete execution state`.
- Run `powershell -File scripts/validate-loop-contract.ps1 -Path 12-plan-merged.md` if that artifact exists.

### Step 6 — Classify the resume
- **clean resume**: no blockers, no open_gaps, artifacts complete and consistent -> go to Step 8.
- **resume-with-gap**: open_gaps present (strategy-gap / plan-gap / loop-limit-reached), OR artifacts missing/malformed, OR execution worktree inconsistent -> go to Step 7 (stop for checkpoint).
- **cannot-resume**: `loop-state.md` itself missing/malformed, OR `loop_status=completed` -> tell the user; ask whether to start fresh or repair manually.

### Step 7 — Stop for checkpoint (only for resume-with-gap)
- Present the blocker/gap content and options:
  1. Retry / gather more evidence
  2. Proceed degraded with explicit marker
  3. Return to planning / revise brief
  4. Pause
- Do not auto-advance through a gap. Stop rules in `stop-rules.md` apply: a gap marker blocks execution.
- If a required subagent artifact was unavailable before the interruption, do not pretend it reviewed. Re-dispatch or stop for degraded-mode approval.

### Step 8 — Continue from next_action
- Resume the `next_role` and execute `next_action`.
- Reuse the SAME `loop_id` and `artifact_dir`. Do not create a new loop (forward-tests scenario 1).
- If `auto_iteration=enabled` and TRAE auto-run setting is ON -> advance automatically per `auto-iteration.md`, stopping only at halt points.
- If `auto_iteration=disabled` or auto-run is OFF -> execute `next_action` then pause for user confirmation of the next step.

### Step 9 — Update loop-state.md and worklog
- Immediately update `loop-state.md`: `resume_count+1`, `last_updated=now`, `last_event="resumed from <phase>"`.
- Append a resume event to `worklog.md` using the `state_event` structure from `state-feedback-schema.md`:
  ```yaml
  state_event:
    loop_id: <id>
    event_id: resume-<n>
    role: manager
    status: active
    next_role: <resumed role>
    next_action: <from loop-state.md>
    stop_or_continue: continue
    evidence: loop-state.md resume_count=<n>
  ```
- During continued execution, overwrite `loop-state.md` on every phase/role/blocker/artifact change per `loop-state-schema.md` update timing.

## Resume Output Template

After completing Steps 1-9 (or stopping at Step 7), the agent's first output should be:

```text
Resumed loop <loop_id>
- phase: <phase> (step <phase_step>/8)
- role: <role>
- status: <loop_status>
- blockers: <none | list>
- open_gaps: <none | list>
- next action: <next_action>
- resume count: <n>
<if clean resume: continuing with next_action>
<if resume-with-gap: stopped for checkpoint — present gap and options>
```

## What Resume Must Not Do

- Start a new loop with a new `loop_id` for the same work.
- Recover state from chat history instead of from `loop-state.md` + worklog.
- Auto-advance through a gap or blocker.
- Pretend a missing subagent artifact reviewed.
- Skip the worktree-consistency check when resuming mid-execution.
- Forget to update `loop-state.md` and append the resume event.
