# Minimal Refactor — T3 Walk-through

This is a walk-through of a single T3 loop (dual plan + dual review) using `00-brief.md` as the task. Use it to see the artifact flow and the exact Task subagent prompt shapes. File/symbol names are illustrative.

## Expected Artifacts

```
docs/loop-engineering/YYYY-MM-DD-auth-async-await/
  loop-state.md
  00-brief.md
  10-plan-A.md
  11-plan-B.md
  12-plan-merged.md
  20-execution-report.md
  30-review-A.md
  31-review-B.md
  40-arbitration.md
  50-final-report.md
```

## Step-by-step

### Step 0 — Initialize loop-state.md
Main agent creates `loop-state.md` at the artifact directory root before writing any other artifact:

```yaml
loop_id: YYYY-MM-DD-auth-async-await
artifact_dir: docs/loop-engineering/YYYY-MM-DD-auth-async-await
phase: brief
phase_step: 0
role: planning
loop_status: active
next_action: "write 00-brief.md"
next_role: planning
next_phase: dual_plan
blockers: []
open_gaps: []
route_tier: T3
subagent_policy: required
dual_mode: same_model_auto
auto_iteration: enabled
repair_iteration: 0
resume_count: 0
```

This file is the first thing a new session reads on `resume loop <loop_id>`.

### Step 1 — Brief
Main agent writes `00-brief.md` (see the file in this folder). Includes a strategic `good_enough` target. Route tier T3.

Update loop-state.md: `phase: dual_plan`, `next_action: "write 10-plan-A.md"`.

### Step 2 — plan-A
Main agent writes `10-plan-A.md` from the brief. Required headings: Goal / Scope / Tasks / Tests / Verification / Risks / Not Doing. It calls out the 401-retry preservation as a risk.

### Step 3 — Dispatch plan-B subagent
Main agent dispatches a Task subagent of type `general_purpose_task`. The prompt contains ONLY the brief + context pack + required headings + independence declaration. It must NOT contain plan-A.

Prompt skeleton:

```markdown
# Task: Independent Plan B

You are an independent planning agent. A separate planner has been working on the
same brief, but you must NOT assume any prior plan exists. Produce your own
independent plan from the brief below.

## Brief (00-brief.md)
<paste 00-brief.md full text>

## Context Pack
<paste full text of src/auth/login.ts, src/auth/types.ts, the existing login test>
<list constraints: strict TS, no new deps, public signatures unchanged>

## Required Output
## Goal
## Scope
## Tasks
## Tests / Verification
## Risks
## Not Doing

## Constraints
- Do not modify any code files. You are planning only.
- Do not ask follow-up questions.
- If the brief is missing a strategic "good enough" target, note it as
  `strategy-gap: <missing decision>` and still produce your best plan.

## Independence Declaration
No other plan has been shared with you. Your output will be compared against an
independent Plan A only after both are complete.
```

### Step 4 — Write plan-B verbatim
Main agent writes the subagent's returned output verbatim into `11-plan-B.md`, adding only:

```
<!-- source: subagent plan-B / subagent_id: <id> / dispatched: <iso time> -->
```

It does not edit, summarize, or compress the output.

Update loop-state.md: `subagent_dispatches` += `{role: plan-B, subagent_id: <id>, artifact: 11-plan-B.md, status: completed}`.

### Step 5 — Merge
Main agent (as merger) reads both plans and writes `12-plan-merged.md`:

```
## Source Plans
- 10-plan-A.md (main agent)
- 11-plan-B.md (subagent plan-B, subagent_id <id>)

## Accepted From A
- ...

## Accepted From B
- ...

## Rejected
- (from A) <idea> — reason: ...

## Third Path Decisions
- (neither plan) <idea> — reason: ...

## Final Tasks
- ...

## Verification
- npm run lint
- npm test -- src/auth

## Completion Criteria
- public signatures unchanged; 401-retry preserved and tested; auth tests green
```

Run the validator:

```powershell
powershell -File scripts/validate-loop-contract.ps1 -Path 12-plan-merged.md
```

Update loop-state.md: `phase: execution`, `next_action: "execute 12-plan-merged.md"`.

### Step 6 — Execute
Main agent follows `12-plan-merged.md`, edits `src/auth/login.ts` and the tests, writes `20-execution-report.md` (Changed Files / Task Status with Evidence / Verification output / Git State / Known Gaps).

Update loop-state.md: `phase: dual_review`, `next_action: "dispatch review-A subagent"`.

### Step 7 — Dispatch review-A subagent
Main agent builds the evidence bundle and dispatches a Task subagent of type `Explore` (read-only). The prompt contains ONLY the bundle + read-only constraint + required headings + independence declaration. It must NOT contain any other review.

Prompt skeleton:

```markdown
# Task: Independent Read-Only Review

You are an independent review agent. Perform a read-only review of the execution
below. Do not modify any code. Do not assume any other review exists.

## Evidence Bundle

### Merged Plan (12-plan-merged.md)
<paste>

### Execution Report (20-execution-report.md)
<paste>

### Changed Diff
<paste precise diff hunks + surrounding lines for src/auth/login.ts>

### Relevant Complete Functions
<paste the full rewritten login function and the refresh helper — no ellipses>

### Test Output
<paste full `npm test -- src/auth` command + pass/fail count>

### Acceptance Criteria
- public signatures unchanged
- 401-retry preserved and covered by a test
- strict TS green

## Required Output
## Source
## Findings
- P0/P1/P2/P3: <title>
  Claim: <what is wrong>
  Evidence: <path:line / command output / artifact path>
  Why it matters: <impact>
  Suggested action: <fix>
## Criteria Check

## Constraints
- Read-only. Do not modify any files.
- Do not ask follow-up questions.
- Every factual claim must carry path:line, command output, or `not verified`.

## Independence Declaration
No other review has been shared with you. Your output will be compared against an
independent Review B only after both are complete.
```

### Step 8 — Write review-A verbatim
Main agent writes the output verbatim into `30-review-A.md` with a provenance header.

### Step 9 — Dispatch review-B subagent
Main agent dispatches a SECOND review subagent with the SAME evidence bundle and constraints. The prompt must NOT contain review-A. Write its output verbatim into `31-review-B.md`.

### Step 10 — Arbitrate and repair
Main agent (as arbitrator) writes `40-arbitration.md`, enumerating every P0/P1 from both reviews with a decision label and evidence citation (not subagent identity). Repairs accepted issues as coherent patches, reruns verification.

Update loop-state.md: `phase: arbitration`; if repairs were made, `repair_iteration` += 1.

### Step 11 — Stop-rule check and final report
- repair iteration within cap (≤ 2)?
- no unresolved P0?
- no `loop-limit-reached` / `strategy-gap` / `plan-gap`?

If all pass, write `50-final-report.md`: final status / changed files / review findings and dispositions / verification output / artifact paths / git state / residual risks.

Update loop-state.md: `phase: final`, `loop_status: completed`.

## What this walk-through proves

- the main agent never injects its own conclusions into a subagent prompt;
- plan-B and review-B prompts never contain their A counterparts;
- subagent outputs are written verbatim;
- arbitration cites evidence, not identity;
- the validator runs on the merged plan before execution;
- `loop-state.md` is updated after every phase transition, enabling cross-session resume via `resume loop <loop_id>`.
