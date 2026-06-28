# Stop Rules

Use this reference when a T2+ loop needs done checks, repair iteration caps, and hard-stop conditions. Stop rules prevent a loop from spinning forever.

## Pre-Execution Definition

For every T2+ route, define before execution starts:

- done check: what evidence proves the task is complete;
- max rounds: the repair iteration cap;
- budget cap: token/time budget if known;
- hard-stop risks: production/destructive risk, route-tier mismatch, no new evidence.

## Repair Iteration Cap

- Maximum 2 repair iterations per brief.
- On the third new P0, write `loop-limit-reached` and stop for user input.
- Any unresolved P0 blocks the final report.

## Severity Disposition

- P0: must be fixed. Blocks final report.
- P1: must be fixed, deferred with a named reason, or disputed with resolution notes.
- P2: may ship only if fixed or explicitly deferred.
- P3: may be recorded without blocking.

If two independent reviews both mark the same issue P0 and the main agent cannot disprove it with strong (`path:line`) evidence, stop for a user decision.

## Stop Or Checkpoint Triggers

Stop or checkpoint when:

- the strategic direction changes;
- no new evidence appears after repeated repair;
- production or destructive risk appears;
- the route tier no longer matches the task;
- a required subagent artifact is unavailable and the user has not approved degraded continuation;
- the user correction changes the strategic target, execution boundary, or "good enough" definition (then update the Strategic Loop Contract and rerun its validator before the next execution).

## Final Report Gate

Write `50-final-report.md` only when stop rules pass:

- no unresolved P0;
- P1 items fixed, deferred with reason, or disputed with notes;
- repair iterations within the cap;
- no active `loop-limit-reached`, `strategy-gap`, or `plan-gap` marker.

The final report includes: final status, changed files, review findings and dispositions, verification output, artifact paths, git state, residual risks.

## Auto-Iteration Halt Points

Every stop trigger and checkpoint trigger in this file is a halt point for auto-iteration (see `references/auto-iteration.md`). When the loop is auto-advancing, encountering any of these MUST stop the loop — auto-run does not bypass them.

Additionally, on resume (`references/resume-protocol.md`), if `loop-state.md` still carries a `loop-limit-reached` / `strategy-gap` / `plan-gap` marker in `open_gaps`, do not auto-advance; stop for a checkpoint.
